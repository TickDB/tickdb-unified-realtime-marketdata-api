"""Unit tests for tickdb_mcp.tools — market and stock tool registration."""

from unittest.mock import AsyncMock, patch

import pytest

from tickdb_mcp.server import create_mcp


@pytest.fixture()
def mcp():
    return create_mcp()


class TestMarketToolsRegistered:
    """Verify all market tools are registered with correct names."""

    @pytest.mark.parametrize("tool_name", [
        "get_ticker",
        "get_kline",
        "get_kline_latest",
        "get_order_book",
        "get_recent_trades",
        "get_available_symbols",
        "get_kline_intervals",
    ])
    def test_market_tool_exists(self, mcp, tool_name):
        assert tool_name in mcp._tool_manager._tools, f"Missing tool: {tool_name}"


class TestStockToolsRegistered:
    """Verify all stock tools are registered with correct names."""

    @pytest.mark.parametrize("tool_name", [
        "get_stock_info",
        "get_intraday",
        "get_trading_sessions",
        "get_trade_days",
        "get_market_metrics",
        "get_capital_flow",
    ])
    def test_stock_tool_exists(self, mcp, tool_name):
        assert tool_name in mcp._tool_manager._tools, f"Missing tool: {tool_name}"


class TestMarketToolCallsApi:
    """Verify market tools call the correct API endpoints."""

    @pytest.mark.asyncio
    async def test_get_ticker_calls_correct_endpoint(self):
        with patch("tickdb_mcp.tools.market.api.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": []}
            mcp = create_mcp()
            tool = mcp._tool_manager._tools["get_ticker"]
            await tool.fn(symbols="BTCUSDT")
            mock_get.assert_called_once_with("/v1/market/ticker", symbols="BTCUSDT", type=None)

    @pytest.mark.asyncio
    async def test_get_kline_calls_correct_endpoint(self):
        with patch("tickdb_mcp.tools.market.api.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": []}
            mcp = create_mcp()
            tool = mcp._tool_manager._tools["get_kline"]
            await tool.fn(symbol="BTCUSDT", interval="1h")
            mock_get.assert_called_once_with(
                "/v1/market/kline",
                symbol="BTCUSDT",
                interval="1h",
                type=None,
                limit=None,
                start_time=None,
                end_time=None,
            )

    @pytest.mark.asyncio
    async def test_get_order_book_calls_correct_endpoint(self):
        with patch("tickdb_mcp.tools.market.api.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": {}}
            mcp = create_mcp()
            tool = mcp._tool_manager._tools["get_order_book"]
            await tool.fn(symbol="BTCUSDT", limit=20)
            mock_get.assert_called_once_with(
                "/v1/market/depth", symbol="BTCUSDT", type=None, limit=20
            )

    @pytest.mark.asyncio
    async def test_get_available_symbols_calls_correct_endpoint(self):
        with patch("tickdb_mcp.tools.market.api.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": []}
            mcp = create_mcp()
            tool = mcp._tool_manager._tools["get_available_symbols"]
            await tool.fn(type="crypto", market="GLOBAL")
            mock_get.assert_called_once_with(
                "/v1/symbols/available",
                type="crypto",
                market="GLOBAL",
                limit=None,
                offset=None,
            )


class TestStockToolCallsApi:
    """Verify stock tools call the correct API endpoints."""

    @pytest.mark.asyncio
    async def test_get_stock_info_calls_correct_endpoint(self):
        with patch("tickdb_mcp.tools.stock.api.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": []}
            mcp = create_mcp()
            tool = mcp._tool_manager._tools["get_stock_info"]
            await tool.fn(symbols="AAPL.US,700.HK")
            mock_get.assert_called_once_with(
                "/v1/market/stock-info", symbols="AAPL.US,700.HK", type=None
            )

    @pytest.mark.asyncio
    async def test_get_trading_sessions_calls_correct_endpoint(self):
        with patch("tickdb_mcp.tools.stock.api.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": {}}
            mcp = create_mcp()
            tool = mcp._tool_manager._tools["get_trading_sessions"]
            await tool.fn(market="US")
            mock_get.assert_called_once_with("/v1/market/trading-sessions", market="US")

    @pytest.mark.asyncio
    async def test_get_capital_flow_calls_correct_endpoint(self):
        with patch("tickdb_mcp.tools.stock.api.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": {}}
            mcp = create_mcp()
            tool = mcp._tool_manager._tools["get_capital_flow"]
            await tool.fn(symbol="700.HK")
            mock_get.assert_called_once_with(
                "/v1/market/capital-flow", symbol="700.HK", type=None
            )

    @pytest.mark.asyncio
    async def test_get_trade_days_calls_correct_endpoint(self):
        with patch("tickdb_mcp.tools.stock.api.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": []}
            mcp = create_mcp()
            tool = mcp._tool_manager._tools["get_trade_days"]
            await tool.fn(market="HK", beg_day="20260101", end_day="20260131")
            mock_get.assert_called_once_with(
                "/v1/market/trade-days",
                market="HK",
                beg_day="20260101",
                end_day="20260131",
            )
