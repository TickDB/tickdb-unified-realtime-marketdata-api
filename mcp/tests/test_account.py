"""Subscription responses retain server-provided expiry and account information."""

import json
from unittest.mock import patch

import httpx
import pytest

from tickdb_mcp import client
from tickdb_mcp.server import create_mcp


@pytest.mark.asyncio
@pytest.mark.parametrize("keys", [
    [],
    [{"id": "test-id", "key_prefix": "test", "name": "Test key", "plan": "professional",
      "status": "active", "expires_at": "2036-05-31T20:46:00Z",
      "remaining_seconds": 305876939, "created_at": "2026-04-01T12:46:04Z"}],
    [{"status": "expired", "remaining_seconds": -1, "expires_at": "2026-01-01T00:00:00Z"}],
    [{"status": "active", "remaining_seconds": None, "expires_at": None}],
])
async def test_subscription_response_preserves_empty_expired_and_nullable_values(keys):
    body = {"code": 0, "data": {
        "user_id": "test-user", "server_time": "2026-09-21T14:57:00Z",
        "total": len(keys), "api_keys": keys,
    }}
    http = httpx.AsyncClient(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json=body),
    ))
    with (
        patch.object(client.settings, "tickdb_api_key", "test-key"),
        patch.object(client.httpx, "AsyncClient", return_value=http),
    ):
        result = await create_mcp().call_tool("get_api_key_subscriptions", {})
    payload = result[1] if isinstance(result, tuple) else json.loads(result[0].text)
    assert payload == body


@pytest.mark.asyncio
async def test_subscription_invalid_key_propagates_documented_error():
    http = httpx.AsyncClient(transport=httpx.MockTransport(
        lambda request: httpx.Response(401, json={
            "code": "Invalid or expired token", "message": "[1001] Invalid or expired token",
        }),
    ))
    with (
        patch.object(client.settings, "tickdb_api_key", "test-key"),
        patch.object(client.httpx, "AsyncClient", return_value=http),
        pytest.raises(Exception, match="TickDB error 1001:.*API key invalid"),
    ):
        await create_mcp().call_tool("get_api_key_subscriptions", {})
