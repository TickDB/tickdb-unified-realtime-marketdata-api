"""TickDB HTTP client with per-request API key resolution.

Key priority (highest → lowest):
  1. X-TickDB-Key request header  — user's own key, injected by middleware
  2. TICKDB_API_KEY env var        — server-wide key set by operator

A valid API key is required. Register at https://tickdb.ai to obtain one.
"""

import time
from contextvars import ContextVar

import httpx

from tickdb_mcp.config import settings
from tickdb_mcp.logging import get_logger

logger = get_logger("client")

BASE_URL = "https://api.tickdb.ai"

# Set by AuthMiddleware on each request; None = fall through to env var
request_api_key: ContextVar[str | None] = ContextVar("tickdb_request_api_key", default=None)


def _get_api_key() -> str:
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

    key_source = "header" if request_api_key.get() else "env"
    logger.info("→ GET %s params=%s key_source=%s key=%s", path, clean, key_source, _mask_key(api_key))

    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{BASE_URL}{path}",
                params=clean or None,
                headers={"X-API-Key": api_key},
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

    if not resp.is_success:
        try:
            body = resp.json()
            code, msg = body.get("code", resp.status_code), body.get("message", resp.text)
        except Exception:
            code, msg = resp.status_code, resp.text
        logger.warning(
            "✗ %s status=%d code=%s msg=%s elapsed=%.0fms",
            path, resp.status_code, code, msg, elapsed,
        )
        _raise(code, msg)

    logger.info("✓ %s status=%d elapsed=%.0fms", path, resp.status_code, elapsed)
    logger.debug("  response_size=%d bytes", len(resp.content))

    return resp.json()


_HINTS: dict[int, str] = {
    1001: "API key invalid or expired — register at https://tickdb.ai",
    1002: "API key missing — provide X-TickDB-Key header or set TICKDB_API_KEY",
    1003: "IP not whitelisted for this API key",
    1004: "Insufficient permissions for this endpoint",
    2001: "Parameter error — check symbol format and required fields",
    2002: "Symbol not found — use get_available_symbols to verify the correct code",
    2003: "Invalid time range",
    2004: "Request quantity exceeded (max 50 symbols per call)",
    3001: "Rate limit exceeded — check your plan at https://tickdb.ai",
    3002: "Quota exhausted — check your plan at https://tickdb.ai",
    3006: "Access restricted — check your plan at https://tickdb.ai",
}


def _raise(code: object, message: str) -> None:
    hint = _HINTS.get(int(code) if str(code).isdigit() else 0, "")
    raise RuntimeError(f"TickDB error {code}: {message}" + (f" — {hint}" if hint else ""))
