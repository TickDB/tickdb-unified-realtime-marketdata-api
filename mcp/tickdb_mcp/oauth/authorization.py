"""Add RFC 9207 issuer identification to the SDK's validated error callbacks."""

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from mcp.server.auth.handlers.authorize import AuthorizationHandler
from starlette.responses import RedirectResponse

from tickdb_mcp.oauth.consent import SECURE_HEADERS


def identify_issuer(uri: str, issuer: str) -> str:
    """Keep callback parameters, replacing any existing issuer with our exact issuer."""
    parsed = urlsplit(uri)
    query = [(key, value) for key, value in parse_qsl(parsed.query, keep_blank_values=True)
             if key != "iss"]
    query.append(("iss", issuer))
    return urlunsplit(parsed._replace(query=urlencode(query)))


class IssuerAuthorizationHandler(AuthorizationHandler):
    async def handle(self, request):
        response = await super().handle(request)
        # The SDK validates the client and registered redirect URI before issuing
        # these callbacks. Leave direct errors and the consent-page redirect alone.
        if isinstance(response, RedirectResponse):
            location = response.headers["location"]
            if any(key == "error" for key, _ in parse_qsl(urlsplit(location).query)):
                response.headers["location"] = identify_issuer(location, self.provider.issuer)
                response.headers.update(SECURE_HEADERS)
        return response
