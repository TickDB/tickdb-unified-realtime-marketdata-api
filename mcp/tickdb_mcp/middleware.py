"""Auth middleware — Bearer token gate + TickDB key injection + session logging."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from tickdb_mcp import client
from tickdb_mcp.client import _mask_key
from tickdb_mcp.config import settings
from tickdb_mcp.logging import get_logger

logger = get_logger("middleware")

# Track known sessions to detect new vs reuse
_known_sessions: set[str] = set()

# Required Accept types for MCP Streamable HTTP
_REQUIRED_ACCEPT = "application/json, text/event-stream"


def _resolve_key_label(header_key: str | None) -> str:
    """Return a masked key string for log correlation."""
    if header_key:
        return _mask_key(header_key)
    if settings.tickdb_api_key:
        return _mask_key(settings.tickdb_api_key)
    return "none"


def _needs_accept_fix(accept_header: str) -> bool:
    """Check if Accept header is missing required types for MCP SSE transport."""
    types = [t.strip().split(";")[0] for t in accept_header.split(",")]
    has_json = any(t.startswith("application/json") for t in types)
    has_sse = any(t.startswith("text/event-stream") for t in types)
    return not (has_json and has_sse)


class AuthMiddleware(BaseHTTPMiddleware):
    """Handles four concerns per request:

    1. Accept header compatibility — auto-fix clients that don't send both
       application/json and text/event-stream (e.g. Hermes MCP client).
    2. Bearer token gate — rejects requests when MCP_ACCESS_TOKEN is set
       and the Authorization header doesn't match.
    3. TickDB key injection — reads X-TickDB-Key header and stores it in
       a ContextVar so tool handlers can use the caller's own API key.
    4. Session lifecycle logging — tracks session creation, reuse, and errors.
    """

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        # --- Accept header compatibility fix ---
        accept_header = request.headers.get("accept", "")
        if accept_header and _needs_accept_fix(accept_header):
            logger.info(
                "ACCEPT_FIX ip=%s original_accept='%s' — injecting required types for MCP compatibility",
                client_ip, accept_header,
            )
            raw_headers = [
                (k, v) for k, v in request.scope["headers"]
                if k.lower() != b"accept"
            ]
            raw_headers.append((b"accept", _REQUIRED_ACCEPT.encode()))
            request.scope["headers"] = raw_headers

        # --- Auth gate ---
        if settings.mcp_access_token:
            auth = request.headers.get("authorization", "")
            if auth != f"Bearer {settings.mcp_access_token}":
                logger.warning(
                    "AUTH_REJECTED ip=%s method=%s path=%s reason=invalid_token",
                    client_ip, method, path,
                )
                return JSONResponse(
                    {"error": "Unauthorized", "hint": "Provide: Authorization: Bearer <token>"},
                    status_code=401,
                )

        # --- Key resolution ---
        tickdb_key = request.headers.get("x-tickdb-key", "").strip() or None
        key_label = _resolve_key_label(tickdb_key)

        # --- Session tracking ---
        req_session_id = request.headers.get("mcp-session-id")
        session_label = req_session_id[:8] if req_session_id else "none"

        if req_session_id is None:
            logger.info(
                "SESSION_INIT ip=%s key=%s — client requesting new session",
                client_ip, key_label,
            )
        elif req_session_id in _known_sessions:
            logger.debug(
                "SESSION_REUSE ip=%s key=%s session=%s",
                client_ip, key_label, session_label,
            )
        else:
            logger.info(
                "SESSION_ATTACH ip=%s key=%s session=%s — first request with this session",
                client_ip, key_label, session_label,
            )

        logger.info(
            "REQUEST ip=%s method=%s path=%s key=%s session=%s",
            client_ip, method, path, key_label, session_label,
        )

        ctx_token = client.request_api_key.set(tickdb_key)
        try:
            response = await call_next(request)

            resp_session_id = response.headers.get("mcp-session-id")
            if resp_session_id and resp_session_id not in _known_sessions:
                _known_sessions.add(resp_session_id)
                resp_session_label = resp_session_id[:8]
                logger.info(
                    "SESSION_CREATED ip=%s key=%s session=%s — new session established",
                    client_ip, key_label, resp_session_label,
                )

            if response.status_code == 404 and req_session_id:
                logger.warning(
                    "SESSION_NOT_FOUND ip=%s key=%s session=%s — session expired or invalid",
                    client_ip, key_label, session_label,
                )
                _known_sessions.discard(req_session_id)

            final_session = resp_session_id[:8] if resp_session_id else session_label
            logger.info(
                "RESPONSE ip=%s method=%s path=%s status=%d key=%s session=%s",
                client_ip, method, path, response.status_code, key_label, final_session,
            )
            return response

        except Exception as exc:
            logger.error(
                "ERROR ip=%s method=%s path=%s key=%s session=%s error=%s",
                client_ip, method, path, key_label, session_label, exc,
            )
            raise
        finally:
            client.request_api_key.reset(ctx_token)
