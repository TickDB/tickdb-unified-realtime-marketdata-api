"""Security boundaries of the public HTTP application; no real upstream requests."""

import asyncio
import json
from contextlib import asynccontextmanager

import httpx
import pytest
import respx
from cryptography.fernet import Fernet

from tickdb_mcp import client
from tickdb_mcp.config import settings
from tickdb_mcp.http import create_http_app

ACCEPT = {"Accept": "application/json, text/event-stream"}
SHARED_KEY = "test-server-key-not-for-anonymous-use"
REQUEST_KEY = "test-caller-key"
TICKER_URL = "https://api.tickdb.ai/v1/market/ticker"


@pytest.fixture(autouse=True)
def isolated_configuration(monkeypatch):
    # Do not inherit a developer's .env credentials or transport settings.
    for name, value in {
        "tickdb_api_key": "", "mcp_access_token": "", "oauth_enabled": False,
        "mcp_stateless_http": True,
    }.items():
        monkeypatch.setattr(settings, name, value)
    token = client.request_api_key.set(None)
    yield
    client.request_api_key.reset(token)


@pytest.fixture
def upstream():
    with respx.mock(assert_all_called=False) as router:
        yield router.get(TICKER_URL).mock(
            return_value=httpx.Response(200, json={"code": 0, "data": [{"symbol": "AAPL.US"}]}),
        )


@asynccontextmanager
async def open_http():
    app = create_http_app()
    lifecycle_app = app if settings.oauth_enabled else app.app
    async with lifecycle_app.router.lifespan_context(lifecycle_app):
        async with httpx.AsyncClient(
            # A remote peer can choose a localhost Host header; it is not authentication.
            transport=httpx.ASGITransport(app=app, client=("192.0.2.20", 41000)),
            base_url="http://localhost:8000",
        ) as connection:
            yield connection


async def rpc(http, method, params=None, headers=None, path="/mcp"):
    return await http.post(
        path, headers={**ACCEPT, **(headers or {})},
        json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}},
    )


def payload(response):
    assert response.status_code == 200, response.text
    if "text/event-stream" in response.headers.get("content-type", ""):
        return json.loads(next(
            line[6:] for line in response.text.splitlines() if line.startswith("data: ")
        ))
    return response.json()


def ticker_params(symbol="AAPL.US"):
    return {"name": "get_ticker", "arguments": {"symbols": symbol}}


@pytest.mark.parametrize("headers", [
    {}, {"Authorization": "Bearer unconfigured-token"}, {"X-TickDB-Key": "   "},
])
@pytest.mark.parametrize("method,params", [
    ("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                    "clientInfo": {"name": "security-test", "version": "1"}}),
    ("tools/list", {}),
    ("tools/call", ticker_params()),
])
async def test_shared_key_is_never_available_to_anonymous_http(
    monkeypatch, upstream, headers, method, params,
):
    monkeypatch.setattr(settings, "tickdb_api_key", SHARED_KEY)
    async with open_http() as http:
        response = await rpc(http, method, params, headers)
    assert response.status_code == 401
    assert SHARED_KEY not in response.text
    assert not upstream.called
    assert client.request_api_key.get() is None


@pytest.mark.parametrize("authorization", [None, "Bearer wrong-token"])
async def test_configured_access_token_is_required_even_for_byok(monkeypatch, upstream, authorization):
    monkeypatch.setattr(settings, "tickdb_api_key", SHARED_KEY)
    monkeypatch.setattr(settings, "mcp_access_token", "test-access-token")
    headers = {"X-TickDB-Key": REQUEST_KEY}
    if authorization:
        headers["Authorization"] = authorization
    async with open_http() as http:
        response = await rpc(http, "tools/call", ticker_params(), headers)
    assert response.status_code == 401
    assert not upstream.called


async def test_authenticated_http_can_use_shared_key(monkeypatch, upstream):
    monkeypatch.setattr(settings, "tickdb_api_key", SHARED_KEY)
    monkeypatch.setattr(settings, "mcp_access_token", "test-access-token")
    async with open_http() as http:
        called = payload(await rpc(
            http, "tools/call", ticker_params(),
            {"Authorization": "Bearer test-access-token"},
        ))
    assert not called["result"].get("isError")
    assert upstream.call_count == 1
    assert upstream.calls[0].request.headers["X-API-Key"] == SHARED_KEY
    assert client.request_api_key.get() is None


@pytest.mark.parametrize("server_key", ["", SHARED_KEY])
async def test_anonymous_byok_uses_its_own_key_and_does_not_leak_to_next_request(
    monkeypatch, upstream, server_key,
):
    monkeypatch.setattr(settings, "tickdb_api_key", server_key)
    async with open_http() as http:
        called = payload(await rpc(
            http, "tools/call", ticker_params(), {"X-TickDB-Key": REQUEST_KEY},
        ))
        assert not called["result"].get("isError")
        missing_key = await rpc(http, "tools/call", ticker_params())
        if server_key:
            assert missing_key.status_code == 401
        else:
            result = payload(missing_key)["result"]
            assert result["isError"] is True
            assert "No TickDB API key provided" in result["content"][0]["text"]
    assert upstream.call_count == 1
    assert upstream.calls[0].request.headers["X-API-Key"] == REQUEST_KEY
    assert client.request_api_key.get() is None


async def test_no_key_allows_discovery_but_never_queries_upstream(upstream):
    async with open_http() as http:
        initialized = payload(await rpc(http, "initialize", {
            "protocolVersion": "2025-03-26", "capabilities": {},
            "clientInfo": {"name": "security-test", "version": "1"},
        }))
        assert initialized["result"]["serverInfo"]["name"] == "tickdb-market-data"
        listed = payload(await rpc(http, "tools/list"))
        assert "get_ticker" in {tool["name"] for tool in listed["result"]["tools"]}
        result = payload(await rpc(http, "tools/call", ticker_params()))["result"]
        assert result["isError"] is True
        assert "No TickDB API key provided" in result["content"][0]["text"]
    assert not upstream.called


async def test_concurrent_callers_keep_separate_request_keys(monkeypatch, upstream):
    monkeypatch.setattr(settings, "tickdb_api_key", SHARED_KEY)
    arrived = asyncio.Event()
    seen = {}

    async def overlapping_responses(request):
        symbol = request.url.params["symbols"]
        seen[symbol] = request.headers["X-API-Key"]
        if len(seen) == 2:
            arrived.set()
        await asyncio.wait_for(arrived.wait(), timeout=5)
        return httpx.Response(200, json={"code": 0, "data": [{"symbol": symbol}]})

    upstream.mock(side_effect=overlapping_responses)
    async with open_http() as http:
        responses = await asyncio.gather(*(
            rpc(http, "tools/call", ticker_params(symbol), {"X-TickDB-Key": key})
            for symbol, key in (("AAPL.US", "caller-a-key"), ("MSFT.US", "caller-b-key"))
        ))
        assert all(not payload(response)["result"].get("isError") for response in responses)
        assert (await rpc(http, "tools/call", ticker_params())).status_code == 401
    assert seen == {"AAPL.US": "caller-a-key", "MSFT.US": "caller-b-key"}
    assert upstream.call_count == 2
    assert client.request_api_key.get() is None


async def test_oauth_does_not_leave_an_anonymous_shared_key_path(monkeypatch, tmp_path, upstream):
    for name, value in {
        "tickdb_api_key": SHARED_KEY, "oauth_enabled": True,
        "oauth_public_url": "https://mcp.example.com",
        "oauth_encryption_key": Fernet.generate_key().decode(),
        "oauth_database_path": str(tmp_path / "oauth.sqlite3"),
        "oauth_redirect_uris": ["https://client.example.com/callback"],
    }.items():
        monkeypatch.setattr(settings, name, value)
    async with open_http() as http:
        assert (await rpc(http, "tools/list")).status_code == 401
        assert (await rpc(http, "tools/call", ticker_params())).status_code == 401
        oauth_response = await rpc(
            http, "tools/list", headers={"Host": "mcp.example.com"}, path="/oauth",
        )
        assert oauth_response.status_code == 401
        assert not upstream.called
        called = payload(await rpc(
            http, "tools/call", ticker_params(), {"X-TickDB-Key": REQUEST_KEY},
        ))
        assert not called["result"].get("isError")
    assert upstream.call_count == 1
    assert upstream.calls[0].request.headers["X-API-Key"] == REQUEST_KEY
