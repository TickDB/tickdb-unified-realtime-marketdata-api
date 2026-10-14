"""Stock market tools — fundamentals, intraday, sessions, calendar, metrics, flow."""

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

import tickdb_mcp.client as api


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def get_stock_info(
        symbols: Annotated[str, Field(description="Comma-separated stock codes, max 500. E.g. '700.HK,AAPL.US,600519.SH'")],
        type: Annotated[str | None, Field(description="Product type for disambiguation: stock, crypto, forex, indices")] = None,
    ) -> dict:
        """Get fundamental stock information.

        Returns company name (CN/EN), exchange, currency, lot size, total/circulating
        shares, EPS, EPS TTM, BPS, dividend yield, derivatives and A-share board.
        Fields vary by market/availability and may be omitted.
        Supported: US stocks, Hong Kong stocks, A-shares.
        """
        return await api.get("/v1/market/stock-info", symbols=symbols, type=type)

    @mcp.tool()
    async def get_intraday(
        symbols: Annotated[str, Field(description="Comma-separated stock codes, max 50. E.g. 'AAPL.US,700.HK'")],
        type: Annotated[str | None, Field(description="Product type for disambiguation: stock, crypto, forex, indices")] = None,
    ) -> dict:
        """Get today's intraday minute-level price data for stocks.

        Returns minute-start timestamp in milliseconds, price, volume, turnover,
        and average price. Outside trading hours, data may be present or empty.
        Supported: US stocks, Hong Kong stocks, A-shares.
        """
        return await api.get("/v1/market/intraday", symbols=symbols, type=type)

    @mcp.tool()
    async def get_trading_sessions(
        market: Annotated[str | None, Field(description="Uppercase US, HK, or CN; omit for all markets")] = None,
    ) -> dict:
        """Get trading session schedules for one or all stock markets.

        Returns market-local hhmm begin/end times and trade_session:
        0 regular, 1 pre-market, 2 after-hours, 3 overnight.
        """
        return await api.get("/v1/market/trading-sessions", market=market)

    @mcp.tool()
    async def get_trade_days(
        market: Annotated[str, Field(description="Market code: US, HK, or CN")],
        beg_day: Annotated[str, Field(description="Start date YYYYMMDD within the most recent year, e.g. '20260101'")],
        end_day: Annotated[str, Field(description="End date YYYYMMDD; query range at most 31 days, e.g. '20260131'")],
    ) -> dict:
        """Get the trading calendar (trading days and half-days) for a date range."""
        return await api.get(
            "/v1/market/trade-days",
            market=market,
            beg_day=beg_day,
            end_day=end_day,
        )

    @mcp.tool()
    async def get_market_metrics(
        symbols: Annotated[str, Field(description="Comma-separated stock codes, max 50. E.g. '700.HK,AAPL.US'")],
        type: Annotated[str | None, Field(description="Product type for disambiguation: stock, crypto, forex, indices")] = None,
    ) -> dict:
        """Get comprehensive market metrics and valuation data for stocks.

        Returns: price, change, volume, turnover, YTD change, turnover rate, market cap,
        capital flow, PE (TTM), PB ratio, dividend yield, 5/10/180-day price change rates.
        Supported: US stocks, Hong Kong stocks, A-shares.
        """
        return await api.get("/v1/market/calc-index", symbols=symbols, type=type)

    @mcp.tool()
    async def get_capital_flow(
        symbol: Annotated[str, Field(description="Single stock code. E.g. '700.HK' or 'AAPL.US'")],
        type: Annotated[str | None, Field(description="Product type for disambiguation: stock, crypto, forex, indices")] = None,
    ) -> dict:
        """Get capital flow (money flow) analysis for a stock.

        Returns intraday flow timeline and breakdown of capital inflows/outflows
        by order size: large, medium, and small. All timestamps in this response
        are Unix seconds, unlike the millisecond timestamps in most market tools.
        Supported: US stocks, Hong Kong stocks, A-shares.
        """
        return await api.get("/v1/market/capital-flow", symbol=symbol, type=type)
