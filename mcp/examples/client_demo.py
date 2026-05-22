"""TickDB MCP — client demo using the MCP Python SDK.

Demonstrates how to connect to a running TickDB MCP server and call tools
programmatically via the MCP client protocol.

Prerequisites:
    pip install mcp httpx

Usage:
    # Start the server first (in another terminal):
    #   python main.py
    #
    # Then run this demo:
    #   TICKDB_API_KEY=your_key python examples/client_demo.py
    #
    # Or pass the key via environment:
    #   export TICKDB_API_KEY=your_key
    #   python examples/client_demo.py
"""

import asyncio
import json
import os

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
TICKDB_KEY = os.getenv("TICKDB_API_KEY", "")


def _print_result(title: str, result: object) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)
    if hasattr(result, "content"):
        for block in result.content:
            if hasattr(block, "text"):
                try:
                    data = json.loads(block.text)
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                except json.JSONDecodeError:
                    print(block.text)
    else:
        print(result)


async def main() -> None:
    headers = {}
    if TICKDB_KEY:
        headers["X-TickDB-Key"] = TICKDB_KEY

    print(f"Connecting to TickDB MCP server at {SERVER_URL} ...")

    async with streamablehttp_client(SERVER_URL, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✓ Connected\n")

            # List available tools
            tools = await session.list_tools()
            print(f"Available tools ({len(tools.tools)}):")
            for tool in tools.tools:
                print(f"  • {tool.name}: {tool.description.splitlines()[0]}")

            # --- Demo 1: Real-time ticker ---
            result = await session.call_tool(
                "get_ticker",
                {"symbols": "XAUUSD,BTCUSDT,AAPL.US"},
            )
            _print_result("get_ticker — XAUUSD, BTCUSDT, AAPL.US", result)

            # --- Demo 2: Historical K-line ---
            result = await session.call_tool(
                "get_kline",
                {"symbol": "BTCUSDT", "interval": "1h", "limit": 5},
            )
            _print_result("get_kline — BTCUSDT 1h (last 5 candles)", result)

            # --- Demo 3: Order book depth ---
            result = await session.call_tool(
                "get_order_book",
                {"symbol": "BTCUSDT", "limit": 5},
            )
            _print_result("get_order_book — BTCUSDT top 5 levels", result)

            # --- Demo 4: Stock fundamentals ---
            result = await session.call_tool(
                "get_stock_info",
                {"symbols": "AAPL.US,700.HK"},
            )
            _print_result("get_stock_info — AAPL.US, 700.HK", result)

            # --- Demo 5: Market metrics ---
            result = await session.call_tool(
                "get_market_metrics",
                {"symbols": "AAPL.US"},
            )
            _print_result("get_market_metrics — AAPL.US", result)

            # --- Demo 6: Trading session ---
            result = await session.call_tool(
                "get_trading_sessions",
                {"market": "US"},
            )
            _print_result("get_trading_sessions — US market", result)

            print("\n✓ Demo complete")


if __name__ == "__main__":
    asyncio.run(main())
