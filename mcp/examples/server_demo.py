"""TickDB MCP — server demo / smoke test.

Starts the MCP server in-process and verifies it initializes correctly.
Useful for local development and CI smoke testing without a full HTTP stack.

Prerequisites:
    pip install -e .

Usage:
    python examples/server_demo.py
"""

import asyncio
import os
import sys

# Allow running from repo root without installing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def demo_server_creation() -> None:
    """Demonstrate server creation and tool listing."""
    from tickdb_mcp.server import create_mcp

    print("Creating TickDB MCP server instance...")
    mcp = create_mcp()

    print(f"\n✓ Server name: {mcp.name}")
    print(f"✓ Instructions preview: {mcp.instructions[:80].strip()}...")

    tools = mcp._tool_manager._tools
    print(f"\n✓ Registered tools ({len(tools)}):")
    for name, tool in sorted(tools.items()):
        desc = (tool.description or "").splitlines()[0][:60]
        print(f"   • {name:<28} {desc}")


def demo_config() -> None:
    """Show current server configuration."""
    from tickdb_mcp.config import settings

    print("\n--- Server Configuration ---")
    print(f"  Transport : {settings.mcp_transport}")
    print(f"  Host      : {settings.mcp_host}")
    print(f"  Port      : {settings.mcp_port}")
    print(f"  Log level : {settings.log_level}")
    print(f"  API key   : {'configured' if settings.tickdb_api_key else 'not set (per-request header required)'}")
    print(f"  Auth token: {'enabled' if settings.mcp_access_token else 'disabled (open access)'}")


async def demo_tool_call_mock() -> None:
    """Call a tool with a mocked HTTP backend to verify the call chain."""
    import httpx
    import respx

    import tickdb_mcp.client as api_client
    from tickdb_mcp.server import create_mcp

    mock_response = {
        "code": 0,
        "data": [
            {
                "symbol": "BTCUSDT",
                "price": "67500.00",
                "change": "1250.00",
                "changePercent": "1.89",
                "volume": "28450.123",
            }
        ],
    }

    print("\n--- Mock Tool Call: get_ticker(BTCUSDT) ---")

    # Set a fake API key so the client doesn't raise
    token = api_client.request_api_key.set("demo-key-1234")
    try:
        with respx.mock:
            respx.get("https://api.tickdb.ai/v1/market/ticker").mock(
                return_value=httpx.Response(200, json=mock_response)
            )
            mcp = create_mcp()
            tool = mcp._tool_manager._tools["get_ticker"]
            result = await tool.fn(symbols="BTCUSDT")

        print(f"  ✓ Result: {result}")
    finally:
        api_client.request_api_key.reset(token)


def main() -> None:
    from tickdb_mcp.logging import setup_logging
    setup_logging()

    print("=" * 60)
    print("  TickDB MCP Server Demo")
    print("=" * 60)

    demo_server_creation()
    demo_config()

    try:
        import respx  # noqa: F401
        asyncio.run(demo_tool_call_mock())
    except ImportError:
        print("\n  (Skipping mock tool call — install respx: pip install respx)")

    print("\n✓ Demo complete. To start the HTTP server, run: python main.py")


if __name__ == "__main__":
    main()
