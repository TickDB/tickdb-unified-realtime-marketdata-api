"""Exercise all tools against the independently captured documentation contract."""

import json
import re
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest

from tickdb_mcp import client
from tickdb_mcp.server import create_mcp

CONTRACT = json.loads((Path(__file__).parent / "fixtures/api_contract_v021.json").read_text())
OPERATIONS = CONTRACT["operations"]
ALIASES = {"from": "from_date", "to": "to_date"}


@pytest.mark.asyncio
async def test_tool_surface_matches_documented_rest_contract():
    tools = {tool.name: tool for tool in await create_mcp().list_tools()}
    assert set(tools) == {op["tool"] for op in OPERATIONS}
    assert len(tools) == 43
    for op in OPERATIONS:
        params = [p for p in op["parameters"] if p["in"] != "header"]
        schema = tools[op["tool"]].inputSchema
        assert set(schema["properties"]) == {ALIASES.get(p["name"], p["name"]) for p in params}
        for param in params:
            prop = schema["properties"][ALIASES.get(param["name"], param["name"])]
            types = {item.get("type") for item in prop.get("anyOf", [prop])}
            assert param["schema"]["type"] in types
            for value in param["schema"].get("enum", []):
                assert re.search(rf"\b{re.escape(value)}\b", prop["description"])
        assert set(schema.get("required", [])) == {
            ALIASES.get(p["name"], p["name"]) for p in params if p["required"]
        }


@pytest.mark.asyncio
@pytest.mark.parametrize("op", OPERATIONS, ids=lambda op: op["tool"])
@pytest.mark.parametrize("optional", [True, False], ids=["all-parameters", "required-only"])
async def test_mcp_call_forwards_documented_http_request(op, optional):
    params = [
        p for p in op["parameters"]
        if p["in"] != "header" and (optional or p["required"])
    ]
    arguments = {ALIASES.get(p["name"], p["name"]): p["sample"] for p in params}
    expected_path = op["path"]
    for p in params:
        if p["in"] == "path":
            expected_path = expected_path.replace("{" + p["name"] + "}", str(p["sample"]))
    expected_query = {p["name"]: str(p["sample"]) for p in params if p["in"] == "query"}
    body = {"code": 0, "data": {"rows": [], "nullable": None}, "page": {"next_cursor": "abc=="}}
    requests = []

    def handler(request):
        requests.append(request)
        assert request.method == "GET"
        assert request.url.path == expected_path
        assert dict(request.url.params) == expected_query
        assert request.headers["X-API-Key"] == "test-key"
        assert request.headers["Accept-Encoding"] == "gzip"
        return httpx.Response(200, json=body)

    http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    with (
        patch.object(client.settings, "tickdb_api_key", "test-key"),
        patch.object(client.httpx, "AsyncClient", return_value=http),
    ):
        result = await create_mcp().call_tool(op["tool"], arguments)
    assert len(requests) == 1
    # MCP 1.x versions expose either text blocks or (text, structured) results.
    payload = result[1] if isinstance(result, tuple) else json.loads(result[0].text)
    assert payload == body


@pytest.mark.asyncio
@pytest.mark.parametrize("news_id", ["../profile", "1?symbol=AAPL", "0", "1/2", "abc"])
async def test_news_id_cannot_change_request_path(news_id):
    with patch.object(client, "get") as get:
        with pytest.raises(Exception, match="pattern"):
            await create_mcp().call_tool("get_news_detail", {"news_id": news_id})
        get.assert_not_called()


@pytest.mark.asyncio
async def test_parameter_guidance_is_visible_to_mcp_clients():
    for tool in await create_mcp().list_tools():
        for name, schema in tool.inputSchema["properties"].items():
            assert schema.get("description"), f"{tool.name}.{name} has no published guidance"
