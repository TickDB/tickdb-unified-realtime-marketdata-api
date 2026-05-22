<div align="center">

<img src="assets/logo.svg" alt="TickDB Logo" width="320">

# TickDB — Unified Real-time Market Data API for Forex, Stocks, Crypto

*One connection for Forex, Precious Metals, Indices, US Stocks, HK Stocks, A-Shares, and Crypto*

*Open-source toolkit · API docs + AI Skill + MCP server implementation*

[![API Status](https://img.shields.io/badge/API-Live-green)](https://tickdb.ai)
[![AI-Native](https://img.shields.io/badge/AI--Native-Skill%20%7C%20MCP%20%7C%20CLI-purple)](#ai-access)
[![MCP CI](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml)
[![Docs Check](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/docs-quality.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/docs-quality.yml)
[![WebSocket](https://img.shields.io/badge/WebSocket-Supported-blue)](https://tickdb.ai)
[![Latency](https://img.shields.io/badge/Latency-10--50ms-blue)](#)
[![Docs](https://img.shields.io/badge/Docs-docs.tickdb.ai-brightgreen)](https://docs.tickdb.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**Languages:** [🇨🇳 简体中文](README.md) • [🇹🇼 繁體中文](README_tw.md) • [🇺🇸 English](README_en.md)

[📚 Online Docs](https://docs.tickdb.ai) • [🌐 Website](https://tickdb.ai) • [🤖 AI Access ↓](#ai-access)

</div>

---

## 🎯 What is TickDB?

TickDB is an **AI-native real-time market data API** for developers, AI agents, and multi-market financial applications.

Through **one connection**, access real-time and historical market data across Forex, Precious Metals, Indices, US Stocks (NASDAQ / NYSE), HK Stocks, A-Shares, and Cryptocurrency — all through a unified interface.

It is built for developers who **require reliable, low-latency, and production-grade** market data without the overhead of managing multiple data sources, protocols, or vendors.

> Supports tick-level trades, order book depth, and candlestick (K-line) data via REST API and WebSocket streams,
> covering quantitative trading, AI agents, real-time market dashboards, trading platforms, and market data analytics.

---

## 🚀 Quick Start

📦 **Full source code in this repo**: [`SKILL/`](SKILL/) (AI Skill config) · [`mcp/`](mcp/) (Python MCP server — 13 tools · Dockerfile · 46 unit tests · CI · MIT). The hosted endpoint `mcp.tickdb.ai` runs the exact same code in [`mcp/`](mcp/) — what you read, what you deploy, and what we run in production are the same thing.

Pick the integration that fits you:

| Method | Best For | What You Get |
|--------|----------|--------------|
| 💬 **[Skill](#skill)** | Chat-ready, zero config | One-line npx install, AI auto-fetches a trial key |
| 🔌 **[MCP](#mcp)** | AI coding clients / self-hosted | Hosted endpoint + JSON config, or self-host from [`mcp/`](mcp/) |
| 💻 **[CLI](#cli)** | Terminal / scripts / AI agents | npm global install, query markets from your shell |
| 🔧 **[REST API](#rest-api)** | Application integration | HTTP API with 6 endpoint examples |
| 🌐 **[WebSocket](#websocket)** | Real-time streaming | Low-latency subscriptions for ticker / depth / trade |

---

## ✨ Key Features

- **🔌 Unified Access** - One API for Forex, Precious Metals, Indices, US/HK/A-Share Stocks, and Crypto
- **⚡ Real-time Data** - WebSocket streaming with ~10-50ms end-to-end latency
- **🤖 AI-Native** - Official Skill / MCP / CLI integrations — AI agents and coding assistants ready out of the box
- **🛠️ Developer-Friendly** - RESTful API + WebSocket, structured JSON responses, complete docs and multi-language examples
- **🌍 Global Coverage** - 37,527+ symbols across 6 major markets (US/HK/CN + Forex/Crypto/Indices)
- **🆓 Free to Start** - No credit card required, get an API key instantly

---

## 🏗️ Use Cases

- **Quantitative Trading** - Real-time data source for algorithmic and strategy systems
- **AI Agents & Coding Assistants** - Let AI assistants invoke market data directly via Skill / MCP, natural-language driven queries
- **Market Dashboards** - Real-time price displays, asset and portfolio monitoring
- **Trading Applications** - Build TradingView-like market interfaces and charting systems
- **Data Analytics & Backtesting** - Historical analysis, strategy backtesting, and quantitative research
- **Financial Services Integration** - Drop into existing trading platforms or financial infrastructure
- **Self-Hosting / Private Deployment** - Don't want the hosted endpoint? Self-deploy from this repo's [`mcp/`](mcp/) source for full data control

---

<a id="rest-api"></a>
## 🚀 Quick Start — REST API

### 1. Register and Get an API Key

Visit [TickDB.ai](https://tickdb.ai) to register an account and get your API key.

#### 🔑 Authentication

All HTTP API requests require an API key in the request header:

```http
X-API-Key: YOUR_API_KEY
```

#### 🌐 Base URL

```
https://api.tickdb.ai
```

#### 📋 Core HTTP API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/market/kline` | GET | Historical K-line / candlestick data |
| `/v1/market/ticker` | GET | Real-time ticker data |
| `/v1/market/depth` | GET | Order book depth data |
| `/v1/market/trades` | GET | Recent trades history |

#### 🏪 Supported Markets

| Market Type | Symbol Format Example | Description |
|-------------|----------------------|-------------|
| Forex (FX) | `GBPUSD` | Major currency pairs (Base/Quote) |
| Precious Metals | `XAUUSD` | Precious metals vs USD |
| US Stocks | `AAPL.US` | NYSE / NASDAQ listed stocks |
| Indices | `SPX` | Stock indices (e.g., S&P 500) |
| HK Stocks | `700.HK` | Hong Kong Stock Exchange securities |
| A-Shares | `600519.SH` | Shanghai / Shenzhen Exchange stocks |
| Cryptocurrency | `BTCUSDT` | Crypto asset trading pairs |

### 2. Get K-line Data

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/kline?symbol=700.HK&interval=1h&limit=24"
```

### 3. Get Real-time Ticker Data

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/ticker?symbols=AAPL.US,700.HK,BTCUSDT"
```

### 4. Get Order Book Depth Data

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/depth?symbol=AAPL.US&limit=10"
```

### 5. Get Trade Records

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/trades?symbols=AAPL.US&limit=20"
```

### 6. Query Available Symbols

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/symbols/available?market=HK&limit=10"
```

---

<a id="websocket"></a>
## 🌐 Real-time Streaming — WebSocket

Low-latency (10-50ms) streaming, ideal for real-time dashboards, quantitative strategies, and Agent automation.

### Supported Channels

- `ticker` - Real-time price updates
- `depth` - Order book changes
- `trade` - Real-time trade executions

```javascript
const ws = new WebSocket('wss://api.tickdb.ai/v1/realtime?api_key=YOUR_API_KEY');

ws.onopen = () => {
    // Subscribe to real-time prices
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'ticker', symbols: ['BTCUSDT'] }
    }));

    // Subscribe to order book changes
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'depth', symbols: ['BTCUSDT'] }
    }));

    // Subscribe to real-time trades
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'trade', symbols: ['BTCUSDT'] }
    }));
};
```

---

<a id="ai-access"></a>
## 🤖 AI-Native Access

TickDB is an **AI-native** market data API offering three tiers of integration, from zero-config chat to production-grade deep integration.

<a id="skill"></a>
### 💬 Skill — Chat-ready

Install and the AI automatically gets a trial key — query 72 popular symbols with no registration:

```bash
npx clawhub@latest install tickdb-market-data
```

Or use the [SKILL file](SKILL/SKILL.md) directly from this repo.

<a id="mcp"></a>
### 🔌 MCP — Permanent Integration

One-time setup gives Claude, Cursor, Kiro, and other AI coding clients permanent access to 13 market data tools.

**Hosted endpoint (recommended, no self-hosting required):**

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

Supported clients: Claude Code · Claude Desktop · Cursor · Kiro · Codex · Zed · Cherry Studio

**The MCP server is open source**, located in the [`mcp/`](mcp/) directory of this repo.

📊 **mcp/ at a glance**: 13 MCP tools · Python 3.11+ · Docker-ready · 46 unit tests · MIT license · CI-validated

| Document | Link |
|----------|------|
| Client Setup Guide | [mcp/docs/en/MCP_CLIENT_SETUP.md](mcp/docs/en/MCP_CLIENT_SETUP.md) |
| Deployment Guide (self-host) | [mcp/docs/en/DEPLOYMENT.md](mcp/docs/en/DEPLOYMENT.md) |
| MCP Full README | [mcp/docs/en/README.md](mcp/docs/en/README.md) |

<a id="cli"></a>
### 💻 CLI — Terminal & Agent

```bash
npm install -g tickdb
tickdb config set-key YOUR_API_KEY
tickdb ticker BTCUSDT,XAUUSD
```

See [AI access on our website](https://tickdb.ai/ai-tools).

---

## 📚 Documentation

Complete API reference, parameter descriptions, and runnable examples:

- **Docs**: https://docs.tickdb.ai
- **Website**: https://tickdb.ai
- **AI Access Page**: https://tickdb.ai/ai-tools

---

## 🤝 Community & Support

- **GitHub Issues** - [Report bugs or request features](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/issues)
- **Technical Support** - [Telegram](https://t.me/TickDB_Support)
- **Email** - [support@tickdb.ai](mailto:support@tickdb.ai)
- **Documentation** - [docs.tickdb.ai](https://docs.tickdb.ai)

---

## 📄 License

This documentation is licensed under the [MIT License](LICENSE).
