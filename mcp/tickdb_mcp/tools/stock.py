"""Stock market tools — fundamentals, intraday, sessions, calendar, metrics, flow."""

from typing import Annotated

from mcp.server.fastmcp import FastMCP

import tickdb_mcp.client as api


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def get_stock_info(
        symbols: Annotated[str, "Comma-separated stock codes, max 50. E.g. '700.HK,AAPL.US,600519.SH'"],
        type: Annotated[str | None, "Product type for disambiguation: stock, crypto, forex, indices, futures"] = None,
    ) -> dict:
        """Get fundamental stock information.

        Returns company name (CN/EN), exchange, currency, lot size, total/circulating
        shares, EPS, EPS TTM, BPS, and dividend yield.
        Supported: US stocks, Hong Kong stocks, A-shares.
        """
        return await api.get("/v1/market/stock-info", symbols=symbols, type=type)

    @mcp.tool()
    async def get_intraday(
        symbols: Annotated[str, "Comma-separated stock codes, max 50. E.g. 'AAPL.US,700.HK'"],
        type: Annotated[str | None, "Product type for disambiguation: stock, crypto, forex, indices, futures"] = None,
    ) -> dict:
        """Get today's intraday minute-level price data for stocks.

        Returns timestamp, price, volume, turnover, and average price per minute.
        Supported: US stocks, Hong Kong stocks, A-shares.
        """
        return await api.get("/v1/market/intraday", symbols=symbols, type=type)

    @mcp.tool()
    async def get_trading_sessions(
        market: Annotated[str, "Market code: US, HK, or CN"],
    ) -> dict:
        """Get current trading session schedule for a stock market.

        Returns session begin/end times and session type
        (pre-market, regular, after-hours, closed, etc.).
        """
        return await api.get("/v1/market/trading-sessions", market=market)

    @mcp.tool()
    async def get_trade_days(
        market: Annotated[str, "Market code: US, HK, or CN"],
        beg_day: Annotated[str, "Start date YYYYMMDD, e.g. '20260101'"],
        end_day: Annotated[str, "End date YYYYMMDD, e.g. '20260131'"],
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
        symbols: Annotated[str, "Comma-separated stock codes, max 50. E.g. '700.HK,AAPL.US'"],
        type: Annotated[str | None, "Product type for disambiguation: stock, crypto, forex, indices, futures"] = None,
    ) -> dict:
        """Get comprehensive market metrics and valuation data for stocks.

        Returns: price, change, volume, turnover, YTD change, turnover rate, market cap,
        capital flow, PE (TTM), PB ratio, dividend yield, 5/10/180-day price change rates.
        Supported: US stocks, Hong Kong stocks, A-shares.
        """
        return await api.get("/v1/market/calc-index", symbols=symbols, type=type)

    @mcp.tool()
    async def get_capital_flow(
        symbol: Annotated[str, "Single stock code. E.g. '700.HK' or 'AAPL.US'"],
        type: Annotated[str | None, "Product type for disambiguation: stock, crypto, forex, indices, futures"] = None,
    ) -> dict:
        """Get capital flow (money flow) analysis for a stock.

        Returns intraday flow timeline and breakdown of capital inflows/outflows
        by order size: large, medium, and small.
        Supported: US stocks, Hong Kong stocks, A-shares.
        """
        return await api.get("/v1/market/capital-flow", symbol=symbol, type=type)
