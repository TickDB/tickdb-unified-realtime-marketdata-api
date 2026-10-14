"""Exercise authentication and key propagation through the real MCP HTTP stack."""

import json
from unittest.mock import patch

import httpx
import pytest

from tickdb_mcp import client
from tickdb_mcp.config import settings
from tickdb_mcp.middleware import AuthMiddleware
from tickdb_mcp.server import create_mcp


@pytest.mark.asyncio
@pytest.mark.parametrize("request_key", ["request-key", None])
@pytest.mark.parametrize("tool,path,arguments,data", [
    ("get_ticker", "/v1/market/ticker", {"symbols": "AAPL.US"}, [{"symbol": "AAPL.US"}]),
    ("get_api_key_subscriptions", "/v1/apikeys/subscriptions", {}, {"total": 0, "api_keys": []}),
])
async def test_http_initialize_discover_and_call_with_key_resolution(
    monkeypatch, request_key, tool, path, arguments, data,
):
    monkeypatch.setattr(settings, "mcp_access_token", "test-access-token")
    monkeypatch.setattr(settings, "tickdb_api_key", "env-key")
    server = create_mcp()
    app = AuthMiddleware(server.streamable_http_app())
    requests = []
    original_client = httpx.AsyncClient

    def upstream(request):
        requests.append(request)
        assert request.headers["X-API-Key"] == (request_key or "env-key")
        assert request.url.path == path
        assert dict(request.url.params) == arguments
        return httpx.Response(200, json={"code": 0, "data": data})

    def make_client(**kwargs):
        return original_client(transport=httpx.MockTransport(upstream), **kwargs)

    async with server.session_manager.run():
        async with original_client(
            transport=httpx.ASGITransport(app=app), base_url="http://localhost:8000",
        ) as http:
            init = {
                "jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                           "clientInfo": {"name": "test", "version": "1"}},
            }
            rejected = await http.post("/mcp", json=init)
            assert rejected.status_code == 401
            assert not requests
            # Deliberately omit text/event-stream: middleware must repair Accept.
            headers = {"Authorization": "Bearer test-access-token", "Accept": "application/json"}
            if request_key:
                headers["X-TickDB-Key"] = request_key

            async def rpc(body):
                response = await http.post("/mcp", headers=headers, json=body)
                assert response.status_code == 200
                if "text/event-stream" in response.headers.get("content-type", ""):
                    return json.loads(next(
                        line[6:] for line in response.text.splitlines() if line.startswith("data: ")
                    ))
                return response.json()

            with patch.object(client.httpx, "AsyncClient", side_effect=make_client):
                initialized = await rpc(init)
                assert "serverInfo" in initialized["result"]
                listed = await rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
                names = {tool["name"] for tool in listed["result"]["tools"]}
                assert len(names) == 43
                assert not any(name.endswith("_stock_tickers") for name in names)
                called = await rpc({
                    "jsonrpc": "2.0", "id": 3, "method": "tools/call",
                    "params": {"name": tool, "arguments": arguments},
                })
                assert not called["result"].get("isError")
                assert json.loads(called["result"]["content"][0]["text"]) == {
                    "code": 0, "data": data,
                }
    assert len(requests) == 1
    assert client.request_api_key.get() is None
