"""Unit tests for tickdb_mcp.middleware — auth gate and Accept header fix."""

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

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
            client = TestClient(wrapped, raise_server_exceptions=True)
            resp = client.post("/mcp", json={})
        assert resp.status_code == 401
