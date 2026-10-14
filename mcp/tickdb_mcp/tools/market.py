"""Market data tools — quotes, K-lines, depth, tick-by-tick trades, symbol discovery."""

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

import tickdb_mcp.client as api


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def get_ticker(
        symbols: Annotated[str, Field(description="Comma-separated symbol codes, max 50. E.g. 'XAUUSD,BTCUSDT,AAPL.US'")],
        type: Annotated[str | None, Field(description="Product type for disambiguation when symbols share the same code across types. Values: stock, crypto, forex, indices, futures. E.g. type='indices' for '000001' = Shanghai Composite vs type='stock' for '000001' = Ping An Bank")] = None,
    ) -> dict:
        """Get real-time price snapshots for one or more symbols.

        Returns symbol, last_price and millisecond timestamp. Other fields are conditional,
        including open, prev_close, category, traded value and US extended-hours quotes.
        Crypto statistics use a rolling 24h window; traditional markets use the trading
        day/session. Supports stocks, forex/metals, indices, crypto, CN and HK futures.
        """
        return await api.get("/v1/market/ticker", symbols=symbols, type=type)

    @mcp.tool()
    async def get_kline(
        symbol: Annotated[str, Field(description="Single symbol code, e.g. 'BTCUSDT'")],
        interval: Annotated[str, Field(description="Candle interval: 1m 3m 5m 15m 30m 1h 2h 4h 1d 1w 1M")],
        type: Annotated[str | None, Field(description="Product type for disambiguation: stock, crypto, forex, indices, futures")] = None,
        limit: Annotated[int | None, Field(description="Number of candles, default 100, max 1000")] = None,
        start_time: Annotated[int | None, Field(description="Start time as Unix milliseconds")] = None,
        end_time: Annotated[int | None, Field(description="End time as Unix milliseconds")] = None,
        adjust: Annotated[str | None, Field(description="Stock price adjustment: none (default), forward, backward; US/HK/CN stocks")] = None,
    ) -> dict:
        """Get historical OHLCV candles, including CN/HK futures open_interest.

        The last candle may still be forming. Adjusted history may change after
        corporate actions; record query time and adjustment mode for backtests.
        Futures normally omit quote_volume. Limit defaults to 100, caps at 1000;
        non-positive limits use 100. start_time must not exceed end_time.
        """
        return await api.get(
            "/v1/market/kline",
            symbol=symbol,
            interval=interval,
            type=type,
            limit=limit,
            start_time=start_time,
            end_time=end_time,
            adjust=adjust,
        )

    @mcp.tool()
    async def get_kline_latest(
        symbols: Annotated[str, Field(description="Comma-separated symbol codes, max 50. E.g. 'AAPL.US,TSLA.US'")],
        interval: Annotated[str, Field(description="Candle interval: 1m 3m 5m 15m 30m 1h 2h 4h 1d 1w 1M")],
        type: Annotated[str | None, Field(description="Product type for disambiguation: stock, crypto, forex, indices, futures")] = None,
        adjust: Annotated[str | None, Field(description="Stock price adjustment: none (default), forward, backward; US/HK/CN stocks")] = None,
    ) -> dict:
        """Get the most recent (live/incomplete) K-line candle for one or more symbols."""
        return await api.get("/v1/market/kline/latest", symbols=symbols, interval=interval, type=type, adjust=adjust)

    @mcp.tool()
    async def get_order_book(
        symbol: Annotated[str, Field(description="Single symbol. Supported: US/HK/CN stocks, CN/HK futures and crypto. E.g. 'AAPL.US', '700.HK', '600519.SH', or 'BTCUSDT'")],
        type: Annotated[str | None, Field(description="Product type for disambiguation: stock, crypto, forex, indices, futures")] = None,
    ) -> dict:
        """Get order book (market depth) with bid and ask price levels.

        Returns bids/asks as [price, quantity] arrays, best price first; timestamp in ms.
        Depth is market-defined: US 1, HK 10, CN 5, CN futures 1, HK futures 10,
        crypto up to 1000 levels per side. Actual depth may be lower; no limit parameter.
        """
        return await api.get("/v1/market/depth", symbol=symbol, type=type)

    @mcp.tool()
    async def get_recent_trades(
        symbol: Annotated[str, Field(description="Single symbol. Supported: US/HK/CN stocks, CN/HK futures and crypto. E.g. 'AAPL.US', '700.HK', '600519.SH', or 'BTCUSDT'")],
        type: Annotated[str | None, Field(description="Product type for disambiguation: stock, crypto, forex, indices, futures")] = None,
        limit: Annotated[int | None, Field(description="Number of tick-by-tick trades, default 100, max 1000")] = None,
    ) -> dict:
        """Get the most recent tick-by-tick trades for a symbol.

        Returns trade id, price, quantity, side (buy/sell/neutral), and timestamp in ms.
        Futures may also return open_interest_change and position_effect
        (long_open, short_open, both_open, long_close, short_close, both_close,
        long_transfer, short_transfer).
        """
        return await api.get("/v1/market/trades", symbol=symbol, type=type, limit=limit)

    @mcp.tool()
    async def get_available_symbols(
        type: Annotated[str | None, Field(description="Asset type: stock, crypto, forex, indices, futures")] = None,
        market: Annotated[str | None, Field(description="Market: GLOBAL, US, HK, CN")] = None,
        limit: Annotated[int | None, Field(description="Results per page, default 100, max 1000")] = None,
        offset: Annotated[int | None, Field(description="Pagination offset")] = None,
    ) -> dict:
        """Query supported trading symbols with pagination.

        Use this to discover and verify codes before other calls. Query CN or HK with
        type=futures for futures, e.g. BU2609 or HSI8888. Follow pagination.total;
        market is case-insensitive. Product counts change over time.
        """
        return await api.get(
            "/v1/symbols/available",
            type=type,
            market=market,
            limit=limit,
            offset=offset,
        )

    @mcp.tool()
    async def get_ex_factors(
        symbols: Annotated[str, Field(description="Comma-separated US/HK/CN stock symbols")],
        type: Annotated[str | None, Field(description="Only stock; omit for unambiguous symbols")] = None,
        start_time: Annotated[int | None, Field(description="Inclusive start time, Unix milliseconds")] = None,
        end_time: Annotated[int | None, Field(description="Inclusive end time, Unix milliseconds")] = None,
    ) -> dict:
        """Get stock adjustment factors at data.data.{symbol} in the response envelope.

        Each event has forward/backward factors: adjusted = raw * factor_a + factor_b.
        Forward: apply factors after the candle timestamp oldest first. Backward:
        apply factors at/before the timestamp newest first. For ordinary adjusted
        candles, use get_kline or get_kline_latest with adjust instead.
        """
        return await api.get(
            "/v1/market/kline/ex-factors",
            symbols=symbols, type=type, start_time=start_time, end_time=end_time,
        )
