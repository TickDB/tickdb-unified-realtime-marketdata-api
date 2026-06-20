from mcp.server.fastmcp import FastMCP

from tickdb_mcp.config import settings
from tickdb_mcp.tools import register_all

_INSTRUCTIONS = """\
Real-time and historical market data for forex, precious metals, indices,
US stocks, Hong Kong stocks, A-shares, and cryptocurrencies via TickDB API.

Symbol formats:
  Crypto:    BTCUSDT, ETHUSDT
  Forex:     EURUSD, GBPUSD, USDJPY
  Metals:    XAUUSD, XAGUSD
  Indices:   SPX, DJI, IXIC, NDX, VIX, DXY
  US stocks: AAPL.US, TSLA.US, NVDA.US
  HK stocks: 700.HK, 9988.HK
  A-shares:  600519.SH, 000858.SZ

A valid TickDB API key is required. Register at https://tickdb.ai to obtain one.
Pass your key via the X-TickDB-Key request header or set TICKDB_API_KEY on the server.
"""


def create_mcp() -> FastMCP:
    mcp = FastMCP(
        name="tickdb-market-data",
        instructions=_INSTRUCTIONS,
        stateless_http=settings.mcp_stateless_http,
    )
    register_all(mcp)
    return mcp
