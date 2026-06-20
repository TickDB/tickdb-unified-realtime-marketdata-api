"""Auth middleware — Bearer token gate + TickDB key injection + session logging."""

import time
from collections import OrderedDict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from tickdb_mcp import client
from tickdb_mcp.client import _mask_key
from tickdb_mcp.config import settings
from tickdb_mcp.logging import get_logger

logger = get_logger("middleware")

# Track known sessions for logging only. Keep this bounded because remote clients
# can reconnect frequently or fail to send MCP session termination requests.
_known_sessions: OrderedDict[str, float] = OrderedDict()
_last_session_cleanup = 0.0

# Required Accept types for MCP Streamable HTTP
_REQUIRED_ACCEPT = "application/json, text/event-stream"


def _session_log_ttl_seconds() -> int:
    return max(0, settings.mcp_session_log_ttl_seconds)


def _session_log_max_entries() -> int:
    return max(1, settings.mcp_session_log_max_entries)


def _prune_known_sessions(now: float | None = None) -> None:
    """Remove expired and excess session labels from the logging cache."""
    global _last_session_cleanup

    now = time.monotonic() if now is None else now
    ttl_seconds = _session_log_ttl_seconds()
    max_entries = _session_log_max_entries()

    if ttl_seconds and now - _last_session_cleanup >= min(ttl_seconds, 60):
        cutoff = now - ttl_seconds
        while _known_sessions:
            _, seen_at = next(iter(_known_sessions.items()))
            if seen_at >= cutoff:
                break
            _known_sessions.popitem(last=False)
        _last_session_cleanup = now

    while len(_known_sessions) > max_entries:
        _known_sessions.popitem(last=False)


def _touch_known_session(session_id: str, now: float | None = None) -> bool:
    """Refresh a session label if known; return whether it was present."""
    now = time.monotonic() if now is None else now
    _prune_known_sessions(now)
    if session_id not in _known_sessions:
        return False

    _known_sessions[session_id] = now
    _known_sessions.move_to_end(session_id)
    return True


def _remember_known_session(session_id: str, now: float | None = None) -> bool:
    """Store a session label and return True when it already existed."""
    now = time.monotonic() if now is None else now
    existed = session_id in _known_sessions
    _known_sessions[session_id] = now
    _known_sessions.move_to_end(session_id)
    _prune_known_sessions(now)
    return existed


def _forget_known_session(session_id: str) -> None:
    _known_sessions.pop(session_id, None)


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
        now = time.monotonic()
        _prune_known_sessions(now)

        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        # --- Accept header compatibility fix ---
        accept_header = request.headers.get("accept", "")
        if accept_header and _needs_accept_fix(accept_header):
            # Patch the request scope headers to include both required types
            logger.info(
                "ACCEPT_FIX ip=%s original_accept='%s' — injecting required types for MCP compatibility",
                client_ip, accept_header,
            )
            # Rebuild headers with corrected Accept
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
            # Client is initiating a new session (initialize request)
            logger.info(
                "SESSION_INIT ip=%s key=%s — client requesting new session",
                client_ip, key_label,
            )
        elif _touch_known_session(req_session_id, now):
            logger.debug(
                "SESSION_REUSE ip=%s key=%s session=%s",
                client_ip, key_label, session_label,
            )
        else:
            # First time we see this session ID — could be new or unknown
            logger.info(
                "SESSION_ATTACH ip=%s key=%s session=%s — first request with this session",
                client_ip, key_label, session_label,
            )

        # --- Request log ---
        logger.info(
            "REQUEST ip=%s method=%s path=%s key=%s session=%s",
            client_ip, method, path, key_label, session_label,
        )

        # --- Execute request ---
        ctx_token = client.request_api_key.set(tickdb_key)
        try:
            response = await call_next(request)

            # --- Detect session creation from response headers ---
            resp_session_id = response.headers.get("mcp-session-id")
            if resp_session_id and not _remember_known_session(resp_session_id):
                resp_session_label = resp_session_id[:8]
                logger.info(
                    "SESSION_CREATED ip=%s key=%s session=%s — new session established",
                    client_ip, key_label, resp_session_label,
                )

            # --- Detect session not found (404 with no session) ---
            if response.status_code == 404 and req_session_id:
                logger.warning(
                    "SESSION_NOT_FOUND ip=%s key=%s session=%s — session expired or invalid",
                    client_ip, key_label, session_label,
                )
                # Clean up from known set if we had it
                _forget_known_session(req_session_id)

            # --- Response log ---
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
