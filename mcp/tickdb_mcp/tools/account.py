"""Read-only API key subscription tools."""

from mcp.server.fastmcp import FastMCP

import tickdb_mcp.client as api


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def get_api_key_subscriptions() -> dict:
        """Query API key subscriptions and expiration information without website login.

        Uses the current request's X-TickDB-Key or the server's TICKDB_API_KEY;
        no tool arguments are required. Preserves the upstream response envelope.
        Data includes user_id, server_time, total and api_keys. Key records include
        id, key_prefix, name, plan, status, expires_at, remaining_seconds and
        created_at. Use server_time and remaining_seconds to assess expiration;
        preserve missing/null values rather than treating them as zero.
        """
        return await api.get("/v1/apikeys/subscriptions")
