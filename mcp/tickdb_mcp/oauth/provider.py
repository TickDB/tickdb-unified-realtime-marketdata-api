"""OAuth provider using SDK protocol handlers and opaque, resource-bound credentials."""

import re
import secrets
import time
from urllib.parse import urlsplit

from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    AuthorizeError,
    RefreshToken,
    RegistrationError,
    TokenError,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken
from pydantic import Field

from tickdb_mcp.oauth.store import Store, digest

SCOPE = "tickdb:read"
ACCESS_TTL = 900
GRANT_TTL = 30 * 86400
PENDING_TTL = 600
CODE_TTL = 300


class BoundAccessToken(AccessToken):
    api_key: str = Field(exclude=True, repr=False)


class Provider:
    def __init__(self, store: Store, issuer: str, resource: str, redirect_uris: list[str]):
        self.store = store
        self.issuer = issuer
        self.resource = resource
        self.redirect_uris = redirect_uris

    async def get_client(self, client_id):
        with self.store.transaction() as db:
            data = self.store.read(db, "client", client_id)
        return OAuthClientInformationFull.model_validate(data) if data else None

    async def register_client(self, client_info):
        redirects = [str(uri) for uri in client_info.redirect_uris or []]
        if not redirects or any(uri not in self.redirect_uris for uri in redirects):
            raise RegistrationError("invalid_redirect_uri", "Redirect URI is not allowed")
        if client_info.token_endpoint_auth_method not in {"none", "client_secret_post"}:
            raise RegistrationError("invalid_client_metadata", "Use none or client_secret_post")
        if set(client_info.grant_types) != {"authorization_code", "refresh_token"}:
            raise RegistrationError("invalid_client_metadata", "Unsupported grant types")
        if client_info.response_types != ["code"] or client_info.scope != SCOPE:
            raise RegistrationError("invalid_client_metadata", "Unsupported response type or scope")
        with self.store.transaction() as db:
            self.store.prune(db)
            if db.execute("SELECT count(*) FROM records WHERE kind='client'").fetchone()[0] >= 1000:
                raise RegistrationError("invalid_client_metadata", "Client registration capacity reached")
            self.store.put(db, "client", client_info.client_id,
                           client_info.model_dump(mode="json"), 0)

    async def authorize(self, client, params: AuthorizationParams):
        if params.resource != self.resource:
            raise AuthorizeError("invalid_request", "Incorrect or missing resource")
        if params.scopes != [SCOPE]:
            raise AuthorizeError("invalid_scope", "Request tickdb:read")
        if not re.fullmatch(r"[A-Za-z0-9_-]{43}", params.code_challenge):
            raise AuthorizeError("invalid_request", "Invalid S256 challenge")
        # Recheck against deployment policy even for previously registered clients.
        if str(params.redirect_uri) not in self.redirect_uris:
            raise AuthorizeError("invalid_request", "Redirect URI is no longer allowed")
        ticket = secrets.token_urlsafe(32)
        with self.store.transaction() as db:
            self.store.prune(db)
            if db.execute("SELECT count(*) FROM records WHERE kind='pending'").fetchone()[0] >= 1000:
                raise AuthorizeError("temporarily_unavailable", "Too many pending authorizations")
            self.store.put(db, "pending", digest(ticket), {
                "client_id": client.client_id, "client_name": client.client_name or client.client_id,
                "params": params.model_dump(mode="json"), "expires": time.time() + PENDING_TTL,
                "attempts": 0,
            }, time.time() + PENDING_TTL)
        return f"{self.issuer.rstrip('/')}/oauth/consent?ticket={ticket}"

    async def load_authorization_code(self, client, authorization_code):
        with self.store.transaction() as db:
            data = self.store.read(db, "code", digest(authorization_code))
            if not data or data["client_id"] != client.client_id:
                return None
            if data.get("used"):
                self.store.revoke(db, data["family"])
                return None
        return AuthorizationCode(code=authorization_code, **data["code"])

    def issue(self, db, family: str, grant: dict) -> OAuthToken:
        access = secrets.token_urlsafe(32)
        refresh = secrets.token_urlsafe(48)
        access_expires = min(int(time.time()) + ACCESS_TTL, grant["expires"])
        common = {"family": family, "client_id": grant["client_id"], "scopes": [SCOPE],
                  "resource": self.resource}
        self.store.put(db, "access", digest(access), {**common, "expires": access_expires},
                       access_expires, family)
        self.store.put(db, "refresh", digest(refresh),
                       {**common, "expires": grant["expires"], "used": False}, grant["expires"], family)
        return OAuthToken(access_token=access, token_type="Bearer",
                          expires_in=access_expires - int(time.time()), refresh_token=refresh, scope=SCOPE)

    async def exchange_authorization_code(self, client, authorization_code):
        result = None
        with self.store.transaction() as db:
            identifier = digest(authorization_code.code)
            data = self.store.read(db, "code", identifier)
            if data and data["client_id"] == client.client_id:
                if data.get("used"):
                    self.store.revoke(db, data["family"])
                elif data["code"]["expires_at"] > time.time():
                    grant = self.store.read(db, "grant", data["family"])
                    if grant:
                        data["used"] = True
                        self.store.put(db, "code", identifier, data, grant["expires"], data["family"])
                        result = self.issue(db, data["family"], grant)
        if result is None:
            raise TokenError("invalid_grant", "Code expired or already consumed")
        return result

    async def load_refresh_token(self, client, refresh_token):
        with self.store.transaction() as db:
            data = self.store.read(db, "refresh", digest(refresh_token))
            if not data or data["client_id"] != client.client_id:
                return None
            if data["used"]:
                # Reuse of a rotated refresh token revokes the entire grant.
                self.store.revoke(db, data["family"])
                return None
            if not self.store.read(db, "grant", data["family"]):
                return None
        return RefreshToken(token=refresh_token, client_id=client.client_id,
                            scopes=data["scopes"], expires_at=data["expires"])

    async def exchange_refresh_token(self, client, refresh_token, scopes):
        result = None
        with self.store.transaction() as db:
            identifier = digest(refresh_token.token)
            data = self.store.read(db, "refresh", identifier)
            if data and data["client_id"] == client.client_id:
                if data["used"]:
                    self.store.revoke(db, data["family"])
                elif scopes == [SCOPE]:
                    grant = self.store.read(db, "grant", data["family"])
                    if grant:
                        data["used"] = True
                        self.store.put(db, "refresh", identifier, data, data["expires"], data["family"])
                        result = self.issue(db, data["family"], grant)
        # Raise outside transaction so reuse-triggered revocation is committed.
        if result is None:
            raise TokenError("invalid_grant", "Refresh token expired, reused or scope invalid")
        return result

    async def load_access_token(self, token):
        with self.store.transaction() as db:
            data = self.store.read(db, "access", digest(token))
            if not data or data["resource"] != self.resource:
                return None
            grant = self.store.read(db, "grant", data["family"])
            if not grant:
                return None
        return BoundAccessToken(token=token, client_id=data["client_id"], scopes=data["scopes"],
                                expires_at=data["expires"], resource=self.resource, api_key=grant["api_key"])

    async def revoke_token(self, token):
        with self.store.transaction() as db:
            for kind in ("access", "refresh"):
                data = self.store.read(db, kind, digest(token.token))
                if data:
                    self.store.revoke(db, data["family"])


def validate_public_url(value: str) -> str:
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment or parsed.path not in ("", "/")):
        raise ValueError("OAUTH_PUBLIC_URL must be an HTTPS origin without a path, query or credentials")
    return value.rstrip("/")
