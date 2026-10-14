"""Optional OAuth application, isolated from legacy MCP authentication."""

import json
import re
import time
from urllib.parse import parse_qs, urlencode, urlsplit

from mcp.server.auth.routes import build_metadata
from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions, RevocationOptions
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import AnyHttpUrl
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from tickdb_mcp.oauth.authorization import IssuerAuthorizationHandler
from tickdb_mcp.oauth.consent import SECURE_HEADERS, Consent
from tickdb_mcp.oauth.provider import SCOPE, Provider, validate_public_url
from tickdb_mcp.oauth.store import Store, digest
from tickdb_mcp.server import create_mcp

OAUTH_MCP_PATH = "/oauth"


class OAuthBoundary:
    """Bound HTTP inputs and fill resource/PKCE checks absent in the SDK token handler."""

    def __init__(self, app, provider):
        self.app = app
        self.provider = provider

    async def __call__(self, scope, receive, send):
        request = Request(scope, receive)
        path = scope["path"]
        error = None
        status = 400
        if len(scope.get("query_string", b"")) > 16384:
            await JSONResponse({"error": "invalid_request"}, status_code=414)(scope, receive, send)
            return
        if path == OAUTH_MCP_PATH:
            if "x-tickdb-key" in request.headers:
                error = "X-TickDB-Key is not accepted on the OAuth endpoint"
            else:
                await self.app(scope, receive, send)
                return
        elif request.method in {"GET", "POST"} and path in {
            "/authorize", "/token", "/register", "/revoke", "/oauth/consent",
        }:
            # Per source address, plus a global bound. Proxy trust is configured at deployment.
            limit = 10 if path == "/register" else 120
            ip = request.client.host if request.client else "unknown"
            with self.provider.store.transaction() as db:
                self.provider.store.prune(db)
                for key, maximum in ((f"{path}:{ip}", limit), (f"{path}:global", limit * 100)):
                    identifier = digest(key)
                    count = self.provider.store.read(db, "rate", identifier) or {
                        "count": 0, "expires": time.time() + 60,
                    }
                    if count["count"] >= maximum:
                        error, status = "Too many requests; retry later", 429
                        break
                    count["count"] += 1
                    self.provider.store.put(db, "rate", identifier, count, count["expires"])
            if error is None:
                if request.method == "POST":
                    body = bytearray()
                    async for chunk in request.stream():
                        body.extend(chunk)
                        if len(body) > 16384:
                            error, status = "Request body too large", 413
                            break
                    if error is None:
                        sent = False
                        original_receive = receive

                        async def replay():
                            nonlocal sent
                            if not sent:
                                sent = True
                                return {"type": "http.request", "body": bytes(body), "more_body": False}
                            return await original_receive()

                        receive = replay
                        if path == "/register":
                            try:
                                if not isinstance(json.loads(body), dict):
                                    error = "Invalid client metadata"
                            except (ValueError, UnicodeDecodeError, RecursionError):
                                error = "Invalid JSON"
                        else:
                            if request.headers.get("content-type", "").split(";")[0] != "application/x-www-form-urlencoded":
                                error = "Expected application/x-www-form-urlencoded"
                            try:
                                values = parse_qs(body.decode("utf-8"), keep_blank_values=True)
                            except UnicodeDecodeError:
                                values, error = {}, "Invalid form encoding"
                else:
                    values = parse_qs(scope.get("query_string", b"").decode("ascii", errors="replace"),
                                      keep_blank_values=True)
                if path != "/register" and error is None:
                    if any(len(v) != 1 for v in values.values()):
                        error = "Duplicate parameters are not accepted"
                    # SDK 1.26's revoke schema requires this optional OAuth field.
                    if path == "/revoke" and "client_secret" not in values:
                        values["client_secret"] = [""]
                        body = bytearray(urlencode(values, doseq=True).encode())
                    if path == "/token":
                        if values.get("resource") != [self.provider.resource]:
                            error = "Incorrect or missing resource"
                        if values.get("grant_type") == ["authorization_code"]:
                            verifier = values.get("code_verifier", [""])[0]
                            if not re.fullmatch(r"[A-Za-z0-9._~-]{43,128}", verifier):
                                error = "Invalid PKCE verifier"
        if error:
            headers = {**SECURE_HEADERS}
            if status == 429:
                headers["Retry-After"] = "60"
            await JSONResponse({"error": "invalid_request", "error_description": error},
                               status_code=status, headers=headers)(scope, receive, send)
            return
        await self.app(scope, receive, send)


def create_oauth_app(settings):
    public_url = validate_public_url(settings.oauth_public_url)
    if not settings.oauth_redirect_uris:
        raise ValueError("OAUTH_REDIRECT_URIS must contain exact allowed callback URLs")
    for uri in settings.oauth_redirect_uris:
        parsed = urlsplit(uri)
        if (parsed.scheme != "https" or not parsed.hostname or parsed.fragment
                or parsed.username or parsed.password):
            raise ValueError("OAuth callback URLs must use HTTPS without credentials or fragments")
    issuer = str(AnyHttpUrl(public_url))
    resource = public_url + OAUTH_MCP_PATH
    store = Store(settings.oauth_database_path, settings.oauth_encryption_key, resource)
    provider = Provider(store, issuer, resource, settings.oauth_redirect_uris)
    registration = ClientRegistrationOptions(enabled=True, default_scopes=[SCOPE], valid_scopes=[SCOPE])
    revocation = RevocationOptions(enabled=True)
    server = create_mcp(
        streamable_http_path=OAUTH_MCP_PATH, stateless_http=True,
        auth_server_provider=provider,
        auth=AuthSettings(issuer_url=AnyHttpUrl(issuer), resource_server_url=AnyHttpUrl(resource),
                          required_scopes=[SCOPE], client_registration_options=registration,
                          revocation_options=revocation, validate_token_resource=True),
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=[urlsplit(public_url).netloc], allowed_origins=[public_url],
        ),
    )
    app = server.streamable_http_app()
    # SDK 1.26 metadata advertises methods its client authenticator does not fully
    # support. Publish only the two methods we accept and test end to end.
    metadata = build_metadata(AnyHttpUrl(issuer), None, registration, revocation)
    metadata.token_endpoint_auth_methods_supported = ["none", "client_secret_post"]
    metadata.revocation_endpoint_auth_methods_supported = ["none", "client_secret_post"]

    async def discovery(request):
        # SDK 1.26's metadata model has no RFC 9207 field; publish the extension
        # explicitly while keeping issuer serialization identical to resource discovery.
        return JSONResponse({**metadata.model_dump(mode="json", exclude_none=True),
                             "authorization_response_iss_parameter_supported": True},
                            headers={"Access-Control-Allow-Origin": "*", "Cache-Control": "no-store"})

    app.router.routes = [r for r in app.routes
                         if r.path not in {"/.well-known/oauth-authorization-server", "/authorize"}]
    app.router.routes.extend([
        Route("/.well-known/oauth-authorization-server", discovery, methods=["GET", "OPTIONS"]),
        Route("/authorize", IssuerAuthorizationHandler(provider).handle, methods=["GET", "POST"]),
        Route("/oauth/consent", Consent(provider).handle, methods=["GET", "POST"]),
    ])
    return OAuthBoundary(app, provider), app
