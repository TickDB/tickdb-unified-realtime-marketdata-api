"""TickDB HTTP client with per-request API key resolution.

Key priority (highest → lowest):
  1. X-TickDB-Key request header  — user's own key, injected by middleware
  2. TICKDB_API_KEY env var        — server-wide key set by operator

A valid API key is required. Register at https://tickdb.ai to obtain one.
"""

import json
import time
from contextvars import ContextVar

import httpx
from mcp.server.auth.middleware.auth_context import get_access_token

from tickdb_mcp.config import settings
from tickdb_mcp.logging import get_logger

logger = get_logger("client")

BASE_URL = "https://api.tickdb.ai"

# Set by AuthMiddleware on each request; None = fall through to env var
request_api_key: ContextVar[str | None] = ContextVar("tickdb_request_api_key", default=None)


def _get_api_key() -> str:
    if token := get_access_token():
        # OAuth tokens carry a server-side binding, never an API key from headers.
        # A missing binding MUST NOT fall through to a shared server credential.
        key = getattr(token, "api_key", None)
        if not key:
            raise RuntimeError("OAuth authorization has no API key binding; reconnect your account")
        return key
    if key := request_api_key.get():
        return key
    if key := settings.tickdb_api_key:
        return key
    raise RuntimeError(
        "No TickDB API key provided. "
        "Pass your key via the X-TickDB-Key request header "
        "or set the TICKDB_API_KEY environment variable. "
        "Register at https://tickdb.ai to obtain a key."
    )


def _mask_key(key: str) -> str:
    """Mask API key for safe logging: show first 4 and last 4 chars."""
    if len(key) <= 8:
        return key[:2] + "***"
    return key[:4] + "***" + key[-4:]


async def get(path: str, **params: object) -> dict:
    """Authenticated GET request to the TickDB API."""
    api_key = _get_api_key()
    clean = {k: v for k, v in params.items() if v is not None}

    key_source = "oauth" if get_access_token() else ("header" if request_api_key.get() else "env")
    logger.info("→ GET %s params=%s key_source=%s key=%s", path, clean, key_source, _mask_key(api_key))

    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{BASE_URL}{path}",
                params=clean or None,
                headers={"X-API-Key": api_key, "Accept-Encoding": "gzip"},
            )
    except httpx.TimeoutException:
        elapsed = (time.perf_counter() - start) * 1000
        logger.error("✗ TIMEOUT %s elapsed=%.0fms", path, elapsed)
        raise RuntimeError(f"TickDB API timeout after {elapsed:.0f}ms on {path}")
    except httpx.RequestError as exc:
        elapsed = (time.perf_counter() - start) * 1000
        logger.error("✗ NETWORK_ERROR %s elapsed=%.0fms error=%s", path, elapsed, exc)
        raise RuntimeError(f"TickDB API network error on {path}: {exc}")

    elapsed = (time.perf_counter() - start) * 1000

    try:
        body = resp.json()
    except ValueError as exc:
        raise RuntimeError(
            f"TickDB HTTP {resp.status_code}: response is not valid JSON on {path}"
        ) from exc
    if not isinstance(body, dict) or "code" not in body:
        raise RuntimeError(f"TickDB HTTP {resp.status_code}: invalid response envelope on {path}")

    code = str(body["code"])
    # Observed gateway alias for documented 1001; keep body unchanged for diagnostics.
    if resp.status_code == 401 and code == "Invalid or expired token":
        code = "1001"
    if not resp.is_success or code != "0":
        message = body.get("message") or f"HTTP {resp.status_code}"
        logger.warning(
            "✗ %s status=%d code=%s msg=%s elapsed=%.0fms",
            path, resp.status_code, code, message, elapsed,
        )
        _raise(
            code, message, status=resp.status_code,
            retry_after=resp.headers.get("Retry-After"), details=body,
        )

    logger.info("✓ %s status=%d elapsed=%.0fms", path, resp.status_code, elapsed)
    logger.debug("  response_size=%d bytes", len(resp.content))
    return body


# Codes are normalized as strings; never infer the error type from message text.
_HINTS: dict[str, str] = {
    "1001": "API key invalid — check your key at https://tickdb.ai",
    "1002": "API key missing — provide X-TickDB-Key or set TICKDB_API_KEY",
    "1004": "Insufficient permissions — check your plan",
    "1005": "API key expired — renew or upgrade your plan",
    "2001": "Invalid parameters — check required fields, formats and combinations",
    "2002": "Symbol missing or unsupported — verify with get_available_symbols",
    "2003": "Invalid time range; for ambiguous WS symbols check available_types and type",
    "2004": "Request quantity exceeds this endpoint's limit — reduce the requested quantity",
    "2005": "Unsupported symbol format — use the documented market suffix/code",
    "2006": "Symbol suffix conflicts with type — make them consistent",
    "2008": "Full-market snapshots require HTTP compression — enable gzip, br or zstd",
    "3001": "Rate limit exceeded — wait according to Retry-After before retrying",
    "3002": "Quota exhausted — wait for reset or upgrade your plan",
    "3003": "WebSocket connection limit exceeded — close unused connections",
    "3004": "Subscription limit exceeded — unsubscribe or reduce symbols",
    "3005": "This symbol was requested too frequently — wait before requesting it again",
    "3006": "Product not supported by your plan — choose another product or change plan",
    "3007": "K-line history exceeds plan limits — shorten the range or change plan",
    "3008": "Time-range K-line queries not supported by your plan — change query mode or plan",
    "3009": "API key cannot access this endpoint — check permissions or plan",
    "3010": "Fundamentals market not allowed — choose an allowed market or change plan",
    "3011": "Fundamentals history exceeds plan limits — shorten the history range",
    "3012": "Fundamentals batch exceeds plan limits — reduce the symbol count",
    "4005": "WebSocket channel not allowed — check channel permissions",
    "5000": "Internal server error — retry later; contact support if persistent",
    "5001": "Market data temporarily unavailable — retry later",
    "5002": "Service temporarily unavailable — retry later",
    "5003": "No data service available — retry later or change symbol/query",
    "5004": "Live quotes unavailable — retry only the symbols marked retryable",
    "5005": "Adjustment factors unavailable — retry later or use adjust=none",
    "5006": "Base data missing for adjusted candles — change interval or use adjust=none",
    "AMBIGUOUS_SYMBOL": "Pass type using data.available_types to disambiguate the symbol",
    "UNAUTHORIZED": "API key missing — supply the key for the requested transport",
    "INVALID_TOKEN": "API key invalid or expired — check or regenerate it",
    "PERMISSION_DENIED": "Access denied — check plan and connection permissions",
    "40001": "Fundamentals parameters invalid — check formats and combinations",
    "40101": "Fundamentals authentication failed — check API key",
    "40404": "Resource not found — check symbol, object ID or query",
    "40405": "No business data for this query — change symbol, date range or filters",
    "50001": "Fundamentals internal error — retry later; contact support if persistent",
}


class TickDBAPIError(RuntimeError):
    """Preserve HTTP status, business code and response details for callers."""

    def __init__(
        self, code: object, message: str, *, status: int | None = None,
        retry_after: str | None = None, details: dict | None = None,
    ) -> None:
        self.code = str(code)
        self.status = status
        self.retry_after = retry_after
        self.details = details
        text = f"TickDB error {self.code}: {message}"
        if status is not None:
            text += f" (HTTP {status})"
        if hint := _HINTS.get(self.code):
            text += f" — {hint}"
        if retry_after:
            text += f"; Retry-After: {retry_after}"
        if details and details.get("data") is not None:
            text += "; data=" + json.dumps(details["data"], ensure_ascii=False)
        super().__init__(text)


def _raise(code: object, message: str, **context: object) -> None:
    raise TickDBAPIError(code, message, **context)
