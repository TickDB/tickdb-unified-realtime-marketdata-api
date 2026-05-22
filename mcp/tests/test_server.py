"""Unit tests for tickdb_mcp.server — MCP instance creation and tool registration."""


from tickdb_mcp.server import create_mcp


class TestCreateMcp:
    def test_returns_fastmcp_instance(self):
        """create_mcp() should return a FastMCP object."""
        from mcp.server.fastmcp import FastMCP

        mcp = create_mcp()
        assert isinstance(mcp, FastMCP)

    def test_server_name(self):
        """MCP server should be named 'tickdb-market-data'."""
        mcp = create_mcp()
        assert mcp.name == "tickdb-market-data"

    def test_instructions_mention_tickdb(self):
        """Server instructions should reference TickDB."""
        mcp = create_mcp()
        assert "tickdb.ai" in mcp.instructions.lower() or "TickDB" in mcp.instructions

    def test_tools_registered(self):
        """All 13 expected tools should be registered."""
        mcp = create_mcp()
        # FastMCP stores tools in _tool_manager
        tool_names = set(mcp._tool_manager._tools.keys())
        expected = {
            "get_ticker",
            "get_kline",
            "get_kline_latest",
            "get_order_book",
            "get_recent_trades",
            "get_available_symbols",
            "get_kline_intervals",
            "get_stock_info",
            "get_intraday",
            "get_trading_sessions",
            "get_trade_days",
            "get_market_metrics",
            "get_capital_flow",
        }
        assert expected == tool_names

    def test_create_mcp_idempotent(self):
        """Calling create_mcp() twice should produce independent instances."""
        mcp1 = create_mcp()
        mcp2 = create_mcp()
        assert mcp1 is not mcp2
