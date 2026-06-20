# TickDB MCP — Real-time Market Data for AI

[![CI](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../../LICENSE)
[![TickDB](https://img.shields.io/badge/Powered%20by-TickDB-orange)](https://tickdb.ai)

> 📍 This directory is the MCP server implementation of the [tickdb-unified-realtime-marketdata-api](../../../) repository — 13 MCP tools, deployable as a standalone Python package.

**TickDB-MCP** is a Python MCP server implementation that connects AI assistants to real-time and historical market data via the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) and the [TickDB Unified Market Data API](https://tickdb.ai).

Covers **Forex/FX · Precious Metals · Indices · US Stocks (NASDAQ/NYSE) · HK Stocks · A-shares/CN Stocks · Cryptocurrency** through 13 MCP tools backed by a REST API.

**Links:** [Website](https://tickdb.ai) · [Docs](https://docs.tickdb.ai) · [Contact Us](mailto:support@tickdb.ai)

**Language:** [简体中文](../../README.md) · [繁體中文](../tw/README.md) · **English**

---

## Quick Start

```bash
# 1. Install (Python 3.11+)
pip install -e .

# 2. Configure environment
cp .env.example .env
# Edit .env — set TICKDB_API_KEY (register at https://tickdb.ai)

# 3. Start the MCP server
python main.py          # HTTP server on :8000
```

Add to your AI client config (or use the hosted endpoint `https://mcp.tickdb.ai/` directly):

```json
{
  "mcpServers": {
    "tickdb": {
      "type": "http",
      "url": "https://mcp.tickdb.ai/",
      "headers": {
        "X-TickDB-Key": "YOUR_TICKDB_API_KEY"
      }
    }
  }
}
```

Supported clients: Claude Code · Claude Desktop · Cursor · Kiro · Codex · Zed · Cherry Studio

---

## 13 MCP Tools

| Tool | Description | Data Type |
|---|---|---|
| `get_ticker` | Real-time price snapshot (Ticker): price, change, volume | Real-time |
| `get_kline` | Historical K-line / Candlestick (OHLCV) data | Historical |
| `get_kline_latest` | Current live candle (incomplete) | Real-time |
| `get_order_book` | Order book / market depth (bid/ask levels) | Real-time |
| `get_recent_trades` | Recent trades / executed transactions | Real-time |
| `get_available_symbols` | Discover all 37,527+ tradable symbols | Reference |
| `get_kline_intervals` | Supported candlestick interval list | Reference |
| `get_stock_info` | Stock fundamentals: EPS, BPS, dividend yield | Fundamental |
| `get_intraday` | Minute-level intraday data | Intraday |
| `get_trading_sessions` | Current trading session status | Reference |
| `get_trade_days` | Trading calendar for a date range | Reference |
| `get_market_metrics` | Market snapshot: PE, PB, market cap, capital flow | Fundamental |
| `get_capital_flow` | Large/medium/small order capital flow analysis | Real-time |

---

## Markets & Symbol Formats

| Market | Count | Format | Examples |
|---|---|---|---|
| Cryptocurrency | 875+ | `BASE + QUOTE` | `BTCUSDT`, `ETHUSDT` |
| Forex / FX | 1,207 | 6-letter pair | `EURUSD`, `USDJPY`, `XAUUSD` |
| Precious Metals | — | `XAU/XAG + USD` | `XAUUSD`, `XAGUSD` |
| US Stocks (NASDAQ/NYSE) | 12,409 | `TICKER.US` | `AAPL.US`, `TSLA.US`, `NVDA.US` |
| HK Stocks | 4,305 | `CODE.HK` | `700.HK`, `9988.HK` |
| A-shares / CN Stocks (SH) | 6,023 | `6-digit.SH` | `600519.SH`, `601318.SH` |
| A-shares / CN Stocks (SZ) | — | `6-digit.SZ` | `000858.SZ`, `000333.SZ` |
| Indices | 12,708 | Index code | `SPX`, `NDX`, `VIX`, `DXY` |

---

## Configuration

Copy `.env.example` to `.env`:

| Variable | Default | Description |
|---|---|---|
| `TICKDB_API_KEY` | _(empty)_ | Server-wide API key; empty = require per-request `X-TickDB-Key` header |
| `MCP_ACCESS_TOKEN` | _(empty)_ | Bearer token to gate MCP access; empty = open |
| `MCP_TRANSPORT` | `streamable-http` | `stdio` for local Claude Desktop direct mode |
| `MCP_HOST` | `0.0.0.0` | Bind address |
| `MCP_PORT` | `8000` | Listen port |
| `MCP_STATELESS_HTTP` | `true` | Avoid retaining abandoned Streamable HTTP sessions in memory |
| `MCP_SESSION_LOG_TTL_SECONDS` | `3600` | TTL for session IDs kept only for lifecycle logs |
| `MCP_SESSION_LOG_MAX_ENTRIES` | `1000` | Maximum session IDs kept only for lifecycle logs |
| `LOG_LEVEL` | `INFO` | Logging verbosity: DEBUG / INFO / WARNING / ERROR |
| `LOG_RETAIN_DAYS` | `7` | Days to keep rotated log files |

**API key priority:** `X-TickDB-Key` request header → `TICKDB_API_KEY` env var.

---

## Project Structure

```
tickdb-mcp/
├── main.py                  # Entry point (Python MCP server)
├── pyproject.toml           # Package config and dependencies
├── Dockerfile               # Dockerized deployment
├── .env.example             # Environment variable template
├── tickdb_mcp/              # Core package
│   ├── config.py            # Pydantic-settings configuration
│   ├── client.py            # TickDB REST API HTTP client + API key resolution
│   ├── middleware.py        # Auth middleware: Bearer token gate + key injection
│   ├── server.py            # FastMCP instance factory
│   └── tools/
│       ├── market.py        # Ticker, K-line, Order Book, Trades, Symbols
│       └── stock.py         # Stock Info, Intraday, Sessions, Metrics, Capital Flow
├── tests/                   # Unit tests (pytest)
│   ├── test_client.py       # API key resolution and error handling
│   ├── test_server.py       # MCP server creation and tool registration
│   ├── test_middleware.py   # Auth gate and Accept header fix
│   └── test_tools.py        # Tool endpoint mapping
├── examples/
│   ├── client_demo.py       # Python MCP client demo
│   └── server_demo.py       # Server smoke test / tool listing
└── (CI config lives in the parent repo at ../../.github/workflows/mcp-ci.yml)
```

---

## Docker

```bash
# Build Docker image
docker build -t tickdb-mcp .

# Run container
docker run -d -p 8000:8000 -e TICKDB_API_KEY=your_key tickdb-mcp
```

---

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Lint
ruff check .

# Run unit tests
pytest tests/ -v
```

---

## Documentation

| Document | Description |
|---|---|
| [DEPLOYMENT.md](DEPLOYMENT.md) | Local, Docker, Railway, Nginx deployment |
| [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md) | Client setup guide (Claude, Cursor, Kiro, etc.) |
| [../../CHANGELOG.md](../../CHANGELOG.md) | Release history |

---

## License

MIT — see [LICENSE](../../LICENSE).
