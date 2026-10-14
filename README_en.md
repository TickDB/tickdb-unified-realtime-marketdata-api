<div align="center">

<img src="assets/logo.svg" alt="TickDB Logo" width="320">

# TickDB — Unified Real-time Market Data API for Forex, Stocks, Futures, Crypto

*One connection for Forex, Precious Metals, Indices, US Stocks, HK Stocks, A-Shares, China/Hong Kong Futures, and Crypto*

*Open-source toolkit · API docs + AI Skill + MCP server implementation*

[![MCP CI](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml)
[![Docs Check](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/docs-quality.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/docs-quality.yml)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

**Languages:** [简体中文](README.md) • [繁體中文](README_tw.md) • [English](README_en.md)

[Online Docs](https://docs.tickdb.ai) • [Website](https://tickdb.ai) • [AI Access](#ai-access)

</div>

---

## What is TickDB?

TickDB is an **AI-native real-time market data API** for developers, AI agents, and multi-market financial applications.

Through **one connection**, access real-time and historical market data across Forex, Precious Metals, Indices, US Stocks (NASDAQ / NYSE), HK Stocks, A-Shares, China/Hong Kong Futures, and Cryptocurrency — all through a unified interface.

It is built for developers who **require reliable, low-latency, and production-grade** market data without the overhead of managing multiple data sources, protocols, or vendors.

> Supports tick-by-tick trades, order book depth, and candlestick (K-line) data via REST API and WebSocket streams,
> covering quantitative trading, AI agents, real-time market dashboards, trading platforms, and market data analytics.

---

## Quick Start

**Full source code in this repo**: [`SKILL/`](SKILL/) (AI Skill with API references) · [`mcp/`](mcp/) (Python MCP server — 43 tools · Dockerfile · automated tests · CI · MIT). Self-host from [`mcp/`](mcp/) or use the public hosted endpoint `mcp.tickdb.ai`.

Pick the integration that fits you:

| Method | Best For | What You Get |
|--------|----------|--------------|
| [Skill](#skill) | Chat-ready, zero config | One-line npx install, AI auto-fetches a trial key |
| [MCP](#mcp) | AI coding clients / self-hosted | Self-host from [`mcp/`](mcp/), or use hosted OAuth / header access |
| [CLI](#cli) | Terminal / scripts / AI agents | npm global install, query markets from your shell |
| [REST API](#rest-api) | Application integration | Market, futures, and fundamentals HTTP APIs |
| [WebSocket](#websocket) | Real-time streaming | Low-latency subscriptions for ticker / depth / trade |

---

## Key Features

- Unified Access: One API for Forex, Precious Metals, Indices, US/HK/A-Share Stocks, China/Hong Kong Futures, and Crypto
- Real-time Data: WebSocket streaming with ~10-50ms end-to-end latency
- Financials and Fundamentals: REST APIs for US/HK/CN statements, PE valuations, revenue segments, shareholders, and company events
- AI-Native: Official Skill / MCP / CLI integrations — AI agents and coding assistants ready out of the box
- Developer-Friendly: RESTful API + WebSocket, structured JSON responses, complete docs and multi-language examples
- Global Coverage: Stocks, forex, precious metals, indices, China/Hong Kong futures, and crypto; use the product directory for available symbols and counts
- Free to Start: No credit card required, get an API key instantly

---

## Use Cases

- Quantitative Trading: Real-time data source for algorithmic and strategy systems
- AI Agents & Coding Assistants: Let AI assistants invoke market data directly via Skill / MCP, natural-language driven queries
- Market Dashboards: Real-time price displays, asset and portfolio monitoring
- Trading Applications: Build TradingView-like market interfaces and charting systems
- Data Analytics & Backtesting: Historical analysis, strategy backtesting, and quantitative research
- Financial Services Integration: Drop into existing trading platforms or financial infrastructure
- Self-Hosting / Private Deployment: Don't want the hosted endpoint? Self-deploy from this repo's [`mcp/`](mcp/) source for full data control

---

<a id="rest-api"></a>
## Quick Start — REST API

The same REST API provides market data and company financials and fundamentals, including statements, valuations, shareholders, and classified event calendars.

[Authentication and Basics](#rest-auth) · [Core Market Data APIs](#market-api) · [Company Financials and Fundamentals API](#fundamentals-api)

<a id="rest-auth"></a>
### Authentication and Basics

Visit [TickDB.ai](https://tickdb.ai) to register an account and get your API key.

#### Authentication

All HTTP API requests require an API key in the request header:

```http
X-API-Key: YOUR_API_KEY
```

#### Base URL

```
https://api.tickdb.ai
```

#### API Key Subscriptions

- `GET /v1/apikeys/subscriptions` — Query plans, status, and expiration for API Keys returned under the authenticated account

#### Supported Markets

| Market Type | Symbol Format Example | Description |
|-------------|----------------------|-------------|
| Forex (FX) | `GBPUSD` | Major currency pairs (Base/Quote) |
| Precious Metals | `XAUUSD` | Precious metals vs USD |
| US Stocks | `AAPL.US` | NYSE / NASDAQ listed stocks |
| Indices | `SPX` | Stock indices (e.g., S&P 500) |
| HK Stocks | `700.HK` | Hong Kong Stock Exchange securities |
| A-Shares | `600519.SH` | Shanghai / Shenzhen Exchange stocks |
| China Futures | `AP8888` | `type=futures`, `market=CN`; discover dated and continuous contracts in the directory |
| HK Futures | `HSI8888` | `type=futures`, `market=HK`; discover dated and continuous contracts in the directory |
| Cryptocurrency | `BTCUSDT` | Crypto asset trading pairs |

Futures support quotes, K-lines, order books, and tick-by-tick trades; candles may include `open_interest`. Discover codes with `/v1/symbols/available?type=futures`. Dated contracts change by delivery month; `7777`, `8888`, and `9999` denote secondary-main, main, and weighted continuous series respectively. Continuous series are not deliverable contracts. The table illustrates code formats; data availability depends on the symbol and Key permissions.

<a id="market-api"></a>
### Core Market Data APIs

#### General Market Data

- `GET /v1/symbols/available` — Product directory, including China/Hong Kong futures
- `GET /v1/market/ticker` — Real-time snapshots for specified symbols
- `GET /v1/market/kline` — Historical K-lines
- `GET /v1/market/kline/latest` — Live K-lines for the current interval
- `GET /v1/market/depth` — Bid/ask order-book depth
- `GET /v1/market/trades` — Tick-by-tick trades

#### Full-Market Snapshots

- `GET /v1/market/ticker/cn-stock` — Full-market A-share snapshots
- `GET /v1/market/ticker/hk-stock` — Full-market HK stock snapshots
- `GET /v1/market/ticker/us-stock` — Full-market US stock snapshots

#### Stock Data and Market Information

- `GET /v1/market/stock-info` — Stock information
- `GET /v1/market/intraday` — Stock intraday data
- `GET /v1/market/kline/ex-factors` — Stock adjustment factors
- `GET /v1/market/calc-index` — Stock market metrics
- `GET /v1/market/capital-flow` — Stock capital flow
- `GET /v1/market/trading-sessions` — Market trading sessions
- `GET /v1/market/trade-days` — Market trading calendar

#### Get K-line Data

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/kline?symbol=700.HK&interval=1h&limit=24"
```

#### Get Real-time Ticker Data

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/ticker?symbols=AAPL.US,700.HK,BTCUSDT"
```

#### Get Order Book Depth Data

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/depth?symbol=AAPL.US"
```

#### Get Tick-by-Tick Trades

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/trades?symbol=AAPL.US&limit=20"
```

#### Query Available Symbols

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/symbols/available?market=HK&limit=10"
```

Discover China and Hong Kong futures:

```bash
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/symbols/available?type=futures&market=CN&limit=10"
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/symbols/available?type=futures&market=HK&limit=10"
```

<a id="fundamentals-api"></a>
### Company Financials and Fundamentals API

The 29 financials and fundamentals HTTP endpoints cover US/HK/CN stocks. Call them directly with the same Base URL and `X-API-Key`; MCP is optional. Coverage depends on the symbol, disclosure period, and the Key's endpoint and market permissions.

#### Company Information

- `GET /v1/fundamentals/profile` — Company profile
- `GET /v1/fundamentals/executives` — Executives and directors
- `GET /v1/fundamentals/segments/latest` — Latest business and regional revenue segments
- `GET /v1/fundamentals/segments/history` — Historical revenue segments

#### Financial Statements

- `GET /v1/fundamentals/financials/latest` — Latest income, balance-sheet, and cash-flow statements
- `GET /v1/fundamentals/financials/annual` — Annual financial statements
- `GET /v1/fundamentals/financials/ttm` — TTM income and cash-flow statements

#### Valuation and Industries

- `GET /v1/fundamentals/valuation/latest` — Latest PE valuation
- `GET /v1/fundamentals/valuation/ts` — Historical PE series
- `GET /v1/fundamentals/industry/peers` — Industry peers
- `GET /v1/fundamentals/industry/dist` — Stock industry metric distribution
- `GET /v1/fundamentals/industries/rank` — Market industry rankings
- `GET /v1/fundamentals/industries/tree` — Industry classification hierarchy

#### Dividends and Corporate Actions

- `GET /v1/fundamentals/dividends` — Historical and announced future dividends
- `GET /v1/fundamentals/dividends/ttm` — Trailing 12-month cash dividends per share
- `GET /v1/fundamentals/buyback` — Company buybacks
- `GET /v1/fundamentals/corp-actions` — Corporate actions

#### Shareholders and Fund Holdings

- `GET /v1/fundamentals/shareholders/latest` — Latest shareholder holdings
- `GET /v1/fundamentals/shareholders/top` — Major shareholders across reporting periods
- `GET /v1/fundamentals/shareholders/detail` — Shareholder holdings and trading details
- `GET /v1/fundamentals/fund-holdings/latest` — Funds holding the stock

#### Event Calendars

- `GET /v1/fundamentals/calendar/report` — Earnings and financial-report calendar
- `GET /v1/fundamentals/calendar/dividend` — Dividend calendar
- `GET /v1/fundamentals/calendar/split` — Split and consolidation calendar
- `GET /v1/fundamentals/calendar/ipo` — IPO offering and listing calendar
- `GET /v1/fundamentals/calendar/other` — Other event categories

#### News and Market Status

- `GET /v1/fundamentals/news` — Company news list
- `GET /v1/fundamentals/news/{news_id}` — News body or excerpt
- `GET /v1/fundamentals/market/status` — US/HK/CN market status

See the [official API documentation](https://docs.tickdb.ai/en/index) for parameters, response fields, and error codes.

#### Query financial statements

These examples request the latest four income-statement periods, three annual balance sheets, and TTM cash flow:

```bash
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/financials/latest?symbol=AAPL.US&type=stock&kind=IS&n=4"
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/financials/annual?symbol=AAPL.US&type=stock&kind=BS&n=3"
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/financials/ttm?symbol=AAPL.US&type=stock&kind=CF"
```

#### Query PE valuation and dividends

```bash
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/valuation/latest?symbol=AAPL.US&type=stock"
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/dividends?symbol=AAPL.US&type=stock&limit=20"
```

#### Query the earnings calendar

```bash
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/calendar/report?market=US&symbols=AAPL.US&limit=100"
```

---

<a id="websocket"></a>
## Real-time Streaming — WebSocket

Low-latency (10-50ms) streaming, ideal for real-time dashboards, quantitative strategies, and Agent automation.

### Symbol Subscriptions

- [`ticker`](https://docs.tickdb.ai/en/websocket/ticker) — Real-time data for specified symbols
- [`depth`](https://docs.tickdb.ai/en/websocket/depth) — Order-book updates
- [`trade`](https://docs.tickdb.ai/en/websocket/trade) — Real-time tick-by-tick trades

### Full-Market Subscriptions

- [`CN_Stock`](https://docs.tickdb.ai/en/websocket/ticker_cn_stock) — Full-market A-share data
- [`HK_Stock`](https://docs.tickdb.ai/en/websocket/ticker_hk_stock) — Full-market HK stock data
- [`US_Stock`](https://docs.tickdb.ai/en/websocket/ticker_us_stock) — Full-market US stock data

### Connection Control and Guidance

- [`ping / pong`](https://docs.tickdb.ai/en/websocket/ping) — Connection heartbeat checks
- [`unsubscribe`](https://docs.tickdb.ai/en/websocket/ticker) — Cancel subscriptions

Full-market subscriptions require `permessage-deflate` negotiation when connecting. See the [official connection guide](https://docs.tickdb.ai/en/websocket/websocket_quickstart) for message formats, heartbeats, reconnection, and subscription recovery.

#### Multi-Market Subscriptions and Compression (Node.js)

This example uses the Node.js `ws` library. Run `npm install ws`, set `TICKDB_API_KEY`, save the code as `market-stream.cjs`, and run `node market-stream.cjs`. Choose symbols and full markets covered by your Key; use codes returned by the product directory. Set `fullMarkets` to an empty array for symbol subscriptions only.

Enable `perMessageDeflate` directly in `new WebSocket`; compression is negotiated during the handshake, and `ws` decompresses messages automatically. The example handles single messages and arrays of full-market snapshots or updates. The native browser WebSocket does not accept this option.

```javascript
const WebSocket = require('ws');

const apiKey = process.env.TICKDB_API_KEY;
if (!apiKey) throw new Error('Set TICKDB_API_KEY before running this example');

const tickerSymbols = [
    'EURUSD', // Forex
    'XAUUSD', // Precious metals
    'SPX', // Indices
    'AAPL.US', // US stocks
    '700.HK', // HK stocks
    '600519.SH', // A-shares
    'AP8888', // China futures
    'HSI8888', // HK futures
    'BTCUSDT', // Crypto
];
const depthSymbols = ['AAPL.US', '700.HK', '600519.SH', 'AP8888', 'BTCUSDT'];
const tradeSymbols = [...depthSymbols, 'HSI8888'];
const fullMarkets = ['CN_Stock', 'HK_Stock', 'US_Stock'];

const endpoint = new URL('wss://api.tickdb.ai/v1/realtime');
endpoint.searchParams.set('api_key', apiKey);
const ws = new WebSocket(endpoint, {
    perMessageDeflate: true // Negotiate permessage-deflate during the handshake; ws decompresses automatically.
});

ws.on('open', () => {
    if (fullMarkets.length && !ws.extensions.includes('permessage-deflate')) {
        console.error('Full-market data requires permessage-deflate');
        ws.close();
        return;
    }

    // Omit type for mixed products; subscribe to ambiguous codes separately by type.
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'ticker', symbols: tickerSymbols }
    }));
    // Order-book examples: US/HK/CN stocks, China futures, and crypto.
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'depth', symbols: depthSymbols }
    }));
    // The tick-by-tick examples also include HK futures.
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'trade', symbols: tradeSymbols }
    }));

    // Full-market and symbol tickers coexist independently, without affecting depth/trade.
    if (fullMarkets.length) {
        ws.send(JSON.stringify({
            cmd: 'subscribe',
            data: { universes: fullMarkets, channels: ['ticker'] }
        }));
    }
});

ws.on('message', (raw) => {
    let payload;
    try {
        payload = JSON.parse(raw.toString());
    } catch {
        console.error('Received an invalid JSON message');
        return;
    }

    // Symbol messages are objects; full-market snapshots and updates are arrays.
    for (const message of Array.isArray(payload) ? payload : [payload]) {
        if (['ticker', 'depth', 'trade'].includes(message.cmd)) {
            console.log(message.cmd, message.data);
        } else if (message.cmd === 'error') {
            console.error('Subscription error:', message.code, message.message);
        }
    }
});

ws.on('error', () => {
    console.error('WebSocket connection failed');
});
```

---

<a id="ai-access"></a>
## AI-Native Access

TickDB is an **AI-native** market data API offering three tiers of integration, from zero-config chat to production-grade deep integration.

<a id="skill"></a>
### Skill — Chat-ready

Install and the AI automatically gets a trial key — query the 62 listed symbols with no registration:

```bash
npx clawhub@latest install tickdb-market-data
```

Or copy the complete [`SKILL/` directory](SKILL/) into your client's skills directory as `tickdb-market-data`, keeping both `SKILL.md` and `references/`. The Skill supports market data, adjusted K-lines, futures, fundamentals, and API Key plan and expiry queries; availability depends on your Key's permissions.

<a id="mcp"></a>
### MCP — Permanent Integration

The MCP server and Skill in this repository cover 43 REST endpoints, excluding the three full-market snapshots and all WebSocket capabilities.

One-time setup gives AI assistants access to **43 MCP tools: 13 market data tools, 29 company financials and fundamentals tools, and 1 API Key subscription tool**.

| Capability | What users can query |
|------------|----------------------|
| Markets and stocks (13 tools) | Quotes, adjusted K-lines, adjustment factors, order books, tick-by-tick trades, capital flow, and futures symbols |
| Company financials and fundamentals (29 tools) | Profiles, statements, PE valuations, industries, shareholders, dividends/buybacks, news, and classified event calendars |
| API Key subscriptions (1 tool) | Plans, status, expiry, and remaining time returned for the account authenticated by the current Key |

Market data covers forex, precious metals, indices, US stocks, HK stocks, A-shares, China/Hong Kong futures, and crypto. Company financials and fundamentals cover US/HK/CN stocks; availability depends on the symbol, disclosure period, and plan permissions.

**Self-hosting:** Use the Python source or Dockerfile in [`mcp/`](mcp/); see the deployment guide below. Web OAuth is disabled by default and can be enabled following the configuration guide.

**Start locally (Python 3.11+):** Run in a Linux terminal from the repository root. Copy `.env` for a new installation; keep your existing configuration during upgrades.

```bash
cd mcp
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cp .env.example .env
# Edit .env and set TICKDB_API_KEY, or supply a Key in the client header
python main.py
```

The local endpoint is `http://localhost:8000/mcp`. See the [self-hosting guide](mcp/docs/en/DEPLOYMENT.md) for Docker and HTTPS OAuth configuration.

**Public hosted endpoints (optional, no self-hosting needed):**

- **Web OAuth access (ChatGPT / Claude):** Set the server URL to `https://mcp.tickdb.ai/oauth`, select OAuth, then verify your API Key and approve access on the TickDB authorization page.
- **Header access (AI coding clients):** Use `https://mcp.tickdb.ai/` with the `X-TickDB-Key` header, as shown below.

```json
{
  "mcpServers": {
    "tickdb": {
      "type": "http",
      "url": "https://mcp.tickdb.ai/",
      "headers": {
        "X-TickDB-Key": "YOUR_API_KEY"
      }
    }
  }
}
```

See the client setup guide below for individual client settings and Claude Desktop local stdio mode.

**The MCP server is open source**, located in the [`mcp/`](mcp/) directory of this repo.

**mcp/ at a glance**: v0.2.3 · 43 MCP tools · Python 3.11+ · Docker-ready · automated tests · MIT license · CI-validated

| Document | Link |
|----------|------|
| Client Setup Guide | [mcp/docs/en/MCP_CLIENT_SETUP.md](mcp/docs/en/MCP_CLIENT_SETUP.md) |
| Deployment Guide (self-host) | [mcp/docs/en/DEPLOYMENT.md](mcp/docs/en/DEPLOYMENT.md) |
| MCP Full README | [mcp/docs/en/README.md](mcp/docs/en/README.md) |
| Web OAuth and Self-Hosting Configuration | [MCP OAuth setup](mcp/docs/en/README.md#oauth-setup) |
| Version History | [MCP Changelog](mcp/docs/en/CHANGELOG.md) |

<a id="cli"></a>
### CLI — Terminal & Agent

```bash
npm install -g tickdb
tickdb config set-key YOUR_API_KEY
tickdb ticker BTCUSDT,XAUUSD
```

See [AI access on our website](https://tickdb.ai/ai-tools).

---

## Documentation

Complete API reference, parameter descriptions, and runnable examples:

- **Docs**: https://docs.tickdb.ai
- **Website**: https://tickdb.ai
- **AI Access Page**: https://tickdb.ai/ai-tools

---

## Community & Support

- GitHub Issues: [Report bugs or request features](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/issues)
- Technical Support: [Telegram](https://t.me/TickDB_Support)
- Email: [support@tickdb.ai](mailto:support@tickdb.ai)
- Documentation: [docs.tickdb.ai](https://docs.tickdb.ai)

---

## License

This documentation is licensed under the [MIT License](LICENSE).
