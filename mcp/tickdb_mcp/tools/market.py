"""Market data tools — quotes, K-lines, depth, trades, symbol discovery."""

from typing import Annotated

from mcp.server.fastmcp import FastMCP

import tickdb_mcp.client as api


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def get_ticker(
        symbols: Annotated[str, "Comma-separated symbol codes, max 50. E.g. 'XAUUSD,BTCUSDT,AAPL.US'"],
        type: Annotated[str | None, "Product type for disambiguation when symbols share the same code across types. Values: stock, crypto, forex, indices, futures. E.g. type='indices' for '000001' = Shanghai Composite vs type='stock' for '000001' = Ping An Bank"] = None,
    ) -> dict:
        """Get real-time price snapshots for one or more symbols.

        Returns last price, 24h volume, 24h high/low, price change and percent change.
        """
        return await api.get("/v1/market/ticker", symbols=symbols, type=type)

    @mcp.tool()
    async def get_kline(
        symbol: Annotated[str, "Single symbol code, e.g. 'BTCUSDT'"],
        interval: Annotated[str, "Candle interval: 1m 3m 5m 15m 30m 1h 2h 4h 1d 1w 1M"],
        type: Annotated[str | None, "Product type for disambiguation: stock, crypto, forex, indices, futures"] = None,
        limit: Annotated[int | None, "Number of candles, default 100, max 1000"] = None,
        start_time: Annotated[int | None, "Start time as Unix milliseconds"] = None,
        end_time: Annotated[int | None, "End time as Unix milliseconds"] = None,
    ) -> dict:
        """Get historical K-line (OHLCV candlestick) data for a symbol."""
        return await api.get(
            "/v1/market/kline",
            symbol=symbol,
            interval=interval,
            type=type,
            limit=limit,
            start_time=start_time,
            end_time=end_time,
        )

    @mcp.tool()
    async def get_kline_latest(
        symbols: Annotated[str, "Comma-separated symbol codes. E.g. 'AAPL.US,TSLA.US'"],
        interval: Annotated[str, "Candle interval: 1m 3m 5m 15m 30m 1h 2h 4h 1d 1w 1M"],
        type: Annotated[str | None, "Product type for disambiguation: stock, crypto, forex, indices, futures"] = None,
    ) -> dict:
        """Get the most recent (live/incomplete) K-line candle for one or more symbols."""
        return await api.get("/v1/market/kline/latest", symbols=symbols, interval=interval, type=type)

    @mcp.tool()
    async def get_order_book(
        symbol: Annotated[str, "Single symbol. Supported: US stocks, HK stocks, crypto. E.g. 'BTCUSDT'"],
        type: Annotated[str | None, "Product type for disambiguation: stock, crypto, forex, indices, futures"] = None,
        limit: Annotated[int | None, "Price levels per side, default 10, max 50"] = None,
    ) -> dict:
        """Get order book (market depth) with bid and ask price levels.

        Returns bids and asks as [price, quantity] arrays, best price first.
        """
        return await api.get("/v1/market/depth", symbol=symbol, type=type, limit=limit)

    @mcp.tool()
    async def get_recent_trades(
        symbol: Annotated[str, "Single symbol. Supported: HK stocks, crypto only. E.g. 'BTCUSDT'"],
        type: Annotated[str | None, "Product type for disambiguation: stock, crypto, forex, indices, futures"] = None,
        limit: Annotated[int | None, "Number of trades, default 50, max 200"] = None,
    ) -> dict:
        """Get the most recent executed trades for a symbol.

        Returns trade id, price, quantity, side (buy/sell), and timestamp.
        """
        return await api.get("/v1/market/trades", symbol=symbol, type=type, limit=limit)

    @mcp.tool()
    async def get_available_symbols(
        type: Annotated[str | None, "Asset type: stock, crypto, forex, indices"] = None,
        market: Annotated[str | None, "Market: GLOBAL, US, HK, CN"] = None,
        limit: Annotated[int | None, "Results per page, default 100, max 1000"] = None,
        offset: Annotated[int | None, "Pagination offset"] = None,
    ) -> dict:
        """Query all tradable symbols on TickDB (37,527+ products).

        Use this to discover and verify correct symbol codes before other calls.
        """
        return await api.get(
            "/v1/symbols/available",
            type=type,
            market=market,
            limit=limit,
            offset=offset,
        )

    @mcp.tool()
    async def get_kline_intervals() -> dict:
        """List all supported K-line candlestick interval strings."""
        return await api.get("/v1/market/intervals/kline")
