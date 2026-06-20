"""Unit tests for tickdb_mcp.middleware — auth gate and Accept header fix."""

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

import tickdb_mcp.middleware as middleware
from tickdb_mcp.middleware import AuthMiddleware, _needs_accept_fix

# ---------------------------------------------------------------------------
# Helper: build a minimal ASGI app wrapped in AuthMiddleware
# ---------------------------------------------------------------------------

async def _echo(request: Request) -> JSONResponse:
    return JSONResponse({"ok": True})


def _make_client(access_token: str = "") -> TestClient:
    from unittest.mock import patch

    app = Starlette(routes=[Route("/mcp", _echo, methods=["POST", "GET"])])
    wrapped = AuthMiddleware(app)
    # Patch settings so tests are isolated from real env
    with patch("tickdb_mcp.middleware.settings") as mock_settings:
        mock_settings.mcp_access_token = access_token
        mock_settings.tickdb_api_key = ""
        client = TestClient(wrapped, raise_server_exceptions=True)
        return client, mock_settings


# ---------------------------------------------------------------------------
# _needs_accept_fix
# ---------------------------------------------------------------------------

class TestNeedsAcceptFix:
    def test_both_present_no_fix_needed(self):
        assert not _needs_accept_fix("application/json, text/event-stream")

    def test_only_json_needs_fix(self):
        assert _needs_accept_fix("application/json")

    def test_only_sse_needs_fix(self):
        assert _needs_accept_fix("text/event-stream")

    def test_empty_header_no_fix(self):
        # Empty accept header also lacks required types — fix should be applied
        assert _needs_accept_fix("")

    def test_wildcard_needs_fix(self):
        # */* does not satisfy the specific type requirements
        assert _needs_accept_fix("*/*")

    def test_with_quality_values(self):
        # application/json;q=0.9, text/event-stream;q=0.8 — both present
        assert not _needs_accept_fix("application/json;q=0.9, text/event-stream;q=0.8")


# ---------------------------------------------------------------------------
# Auth gate
# ---------------------------------------------------------------------------

class TestAuthGate:
    def test_open_server_allows_any_request(self):
        """No MCP_ACCESS_TOKEN → all requests pass through."""
        app = Starlette(routes=[Route("/mcp", _echo, methods=["POST"])])
        wrapped = AuthMiddleware(app)

        from unittest.mock import patch
        with patch("tickdb_mcp.middleware.settings") as s:
            s.mcp_access_token = ""
            s.tickdb_api_key = ""
            s.mcp_session_log_ttl_seconds = 3600
            s.mcp_session_log_max_entries = 1000
            client = TestClient(wrapped, raise_server_exceptions=True)
            resp = client.post("/mcp", json={})
        assert resp.status_code == 200

    def test_valid_token_passes(self):
        """Correct Bearer token is accepted."""
        app = Starlette(routes=[Route("/mcp", _echo, methods=["POST"])])
        wrapped = AuthMiddleware(app)

        from unittest.mock import patch
        with patch("tickdb_mcp.middleware.settings") as s:
            s.mcp_access_token = "secret"
            s.tickdb_api_key = ""
            s.mcp_session_log_ttl_seconds = 3600
            s.mcp_session_log_max_entries = 1000
            client = TestClient(wrapped, raise_server_exceptions=True)
            resp = client.post("/mcp", json={}, headers={"Authorization": "Bearer secret"})
        assert resp.status_code == 200

    def test_invalid_token_rejected(self):
        """Wrong Bearer token returns 401."""
        app = Starlette(routes=[Route("/mcp", _echo, methods=["POST"])])
        wrapped = AuthMiddleware(app)

        from unittest.mock import patch
        with patch("tickdb_mcp.middleware.settings") as s:
            s.mcp_access_token = "secret"
            s.tickdb_api_key = ""
            s.mcp_session_log_ttl_seconds = 3600
            s.mcp_session_log_max_entries = 1000
            client = TestClient(wrapped, raise_server_exceptions=True)
            resp = client.post("/mcp", json={}, headers={"Authorization": "Bearer wrong"})
        assert resp.status_code == 401
        assert "Unauthorized" in resp.json()["error"]

    def test_missing_token_rejected(self):
        """No Authorization header returns 401 when token is required."""
        app = Starlette(routes=[Route("/mcp", _echo, methods=["POST"])])
        wrapped = AuthMiddleware(app)

        from unittest.mock import patch
        with patch("tickdb_mcp.middleware.settings") as s:
            s.mcp_access_token = "secret"
            s.tickdb_api_key = ""
            s.mcp_session_log_ttl_seconds = 3600
            s.mcp_session_log_max_entries = 1000
            client = TestClient(wrapped, raise_server_exceptions=True)
            resp = client.post("/mcp", json={})
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Bounded MCP session lifecycle logging (added in v0.1.3)
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_known_sessions():
    middleware._known_sessions.clear()
    middleware._last_session_cleanup = 0.0
    yield
    middleware._known_sessions.clear()
    middleware._last_session_cleanup = 0.0


def test_session_log_cache_is_bounded_by_max_entries():
    from unittest.mock import patch
    with (
        patch.object(middleware.settings, "mcp_session_log_max_entries", 2),
        patch.object(middleware.settings, "mcp_session_log_ttl_seconds", 3600),
    ):
        middleware._remember_known_session("a", now=1)
        middleware._remember_known_session("b", now=2)
        middleware._remember_known_session("c", now=3)

    assert list(middleware._known_sessions) == ["b", "c"]


def test_session_log_cache_prunes_expired_entries():
    from unittest.mock import patch
    with (
        patch.object(middleware.settings, "mcp_session_log_max_entries", 10),
        patch.object(middleware.settings, "mcp_session_log_ttl_seconds", 10),
    ):
        middleware._remember_known_session("old", now=0)
        middleware._remember_known_session("fresh", now=7)
        middleware._prune_known_sessions(now=17)

    assert list(middleware._known_sessions) == ["fresh"]


def test_touch_known_session_refreshes_lru_position():
    from unittest.mock import patch
    with (
        patch.object(middleware.settings, "mcp_session_log_max_entries", 2),
        patch.object(middleware.settings, "mcp_session_log_ttl_seconds", 3600),
    ):
        middleware._remember_known_session("a", now=1)
        middleware._remember_known_session("b", now=2)

        assert middleware._touch_known_session("a", now=3) is True

        middleware._remember_known_session("c", now=4)

    assert list(middleware._known_sessions) == ["a", "c"]
    assert middleware._touch_known_session("missing", now=5) is False
