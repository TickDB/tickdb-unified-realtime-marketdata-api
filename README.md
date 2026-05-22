<div align="center">

<img src="assets/logo.svg" alt="TickDB Logo" width="320">

# TickDB — Unified Real-time Market Data API for Forex, Stocks, Crypto

*One connection for Forex, Precious Metals, Indices, US Stocks, HK Stocks, A-Shares, and Crypto*

*开源工具集 · 完整 API 文档 + AI Skill + MCP 服务端实现*

[![API Status](https://img.shields.io/badge/API-Live-green)](https://tickdb.ai)
[![AI-Native](https://img.shields.io/badge/AI--Native-Skill%20%7C%20MCP%20%7C%20CLI-purple)](#ai-access)
[![MCP CI](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml)
[![Docs Check](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/docs-quality.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/docs-quality.yml)
[![WebSocket](https://img.shields.io/badge/WebSocket-Supported-blue)](https://tickdb.ai)
[![Latency](https://img.shields.io/badge/Latency-10--50ms-blue)](#)
[![Docs](https://img.shields.io/badge/Docs-docs.tickdb.ai-brightgreen)](https://docs.tickdb.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**语言版本:** [🇨🇳 简体中文](README.md) • [🇹🇼 繁體中文](README_tw.md) • [🇺🇸 English](README_en.md)

[📚 在线文档](https://docs.tickdb.ai) • [🌐 官网](https://tickdb.ai) • [🤖 AI 接入 ↓](#ai-access)

</div>

---

## 🎯 什么是 TickDB？

TickDB 是面向开发者、AI 代理和多市场金融应用的 **AI 原生实时行情数据 API**(AI-native real-time market data API)。

通过 **一次接入（one connection）**，无缝访问外汇（Forex）、贵金属（Precious Metals）、指数（Indices）、美股（US Stocks / NASDAQ / NYSE）、港股（HK Stocks）、A 股（A-Shares）、加密货币（Cryptocurrency）等多个金融市场的实时与历史行情数据。

TickDB 专为需要**可靠、低延迟、可长期依赖**行情数据的开发者构建，帮助你**避免管理多个数据源、协议和供应商的复杂性**，专注于业务和策略本身。

> 支持 tick 级成交（trades）、盘口深度（order book / depth）、K 线（candlestick）等多种行情形式，
> 通过 REST API 与 WebSocket 接入，覆盖量化交易、AI Agent、实时行情系统、交易平台与数据分析场景。

---

## 🚀 快速接入

📦 **本仓库提供完整源码**：[`SKILL/`](SKILL/)（AI Skill 配置）· [`mcp/`](mcp/)（Python MCP 服务端，13 工具 · Dockerfile · 46 单元测试 · CI · MIT）。托管端点 `mcp.tickdb.ai` 即基于 [`mcp/`](mcp/) 代码运行 — 你看到的、你部署的、官方在跑的，是同一套代码。

选一种适合你的接入方式：

| 方式 | 适合 | 说明 |
|------|------|------|
| 💬 **[Skill](#skill)** | AI 对话即用，零配置 | npx 一键安装，AI 自动获取试用 Key |
| 🔌 **[MCP](#mcp)** | AI 编码客户端 / 自部署开源 | 托管端点 + JSON 配置，或基于 [`mcp/`](mcp/) 自部署 |
| 💻 **[CLI](#cli)** | 终端 / 脚本 / AI Agent | npm 全局安装，命令行直查行情 |
| 🔧 **[REST API](#rest-api)** | 应用集成 | HTTP API + 6 个端点示例 |
| 🌐 **[WebSocket](#websocket)** | 实时流式数据 | 低延迟订阅 ticker / depth / trade |

---

## ✨ 核心特性

- **🔌 统一接入** - 一套 API 覆盖外汇、贵金属、指数、美股、港股、A 股、加密货币
- **⚡ 实时数据** - 基于 WebSocket 的流式推送，端到端延迟约 10-50ms
- **🤖 AI 原生** - 官方提供 Skill / MCP / CLI 三档 AI 接入，AI Agent 与编码助手开箱即用
- **🛠️ 开发者友好** - RESTful API + WebSocket，结构化 JSON 响应，完整文档与多语言示例
- **🌍 全球覆盖** - 37,527+ 品种，6 大市场（US/HK/CN + Forex/Crypto/Indices）
- **🆓 免费开始** - 无需信用卡，立即获取 API 密钥

---

## 🏗️ 典型使用场景

- **量化交易（Quantitative Trading）** - 算法与策略系统的实时行情数据源
- **AI Agent / 编码助手** - 通过 Skill / MCP 让 AI 助手直接调用行情数据，自然语言驱动查询
- **行情看板** - 实时价格展示、资产与投资组合监控
- **交易应用** - 构建类似 TradingView 的行情界面与图表系统
- **数据分析与回测（Backtesting）** - 历史行情分析、策略回测与研究
- **金融服务集成** - 集成到现有交易平台或金融基础设施中
- **自部署 / 私有化** - 不想用托管端点？基于本仓库 [`mcp/`](mcp/) 代码自部署，完全控制数据流

---

<a id="rest-api"></a>
## 🚀 快速开始 — REST API

### 1. 注册并获取 API 密钥

访问 [TickDB.ai](https://tickdb.ai) 注册账户，即可获取 API 密钥。

#### 🔑 身份认证

所有 HTTP API 请求都需要在请求头中包含 API 密钥：

```http
X-API-Key: YOUR_API_KEY
```

#### 🌐 基础 URL

```
https://api.tickdb.ai
```

#### 📋 HTTP API 核心接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/v1/market/kline` | GET | 历史 K 线 / 蜡烛图（Candlestick）数据 |
| `/v1/market/ticker` | GET | 实时行情（Ticker）数据 |
| `/v1/market/depth` | GET | 订单簿深度（Order Book）数据 |
| `/v1/market/trades` | GET | 最近成交（Recent Trades）历史 |

#### 🏪 支持的市场

| 市场类型 | Symbol 格式示例 | 说明 |
|---------|----------------|------|
| 外汇（Forex / FX） | `GBPUSD` | 主要货币对（Base/Quote） |
| 贵金属（Precious Metals） | `XAUUSD` | 贵金属对美元（Commodity / USD） |
| 美股（US Stocks） | `AAPL.US` | NYSE / NASDAQ 上市股票 |
| 指数（Indices） | `SPX` | 股票指数（如标准普尔 500） |
| 港股（HK Stocks） | `700.HK` | 港交所上市证券 |
| A 股（A-Shares） | `600519.SH` | 上海 / 深圳交易所股票 |
| 加密货币（Cryptocurrency） | `BTCUSDT` | 加密资产交易对 |

### 2. 获取 K 线（K-line）数据

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/kline?symbol=700.HK&interval=1h&limit=24"
```

### 3. 获取实时行情（Ticker）数据

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/ticker?symbols=AAPL.US,700.HK,BTCUSDT"
```

### 4. 获取盘口深度（Depth）数据

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/depth?symbol=AAPL.US&limit=10"
```

### 5. 获取成交记录（Trades）数据

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/trades?symbols=AAPL.US&limit=20"
```

### 6. 查询可用交易品种

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/symbols/available?market=HK&limit=10"
```

---

<a id="websocket"></a>
## 🌐 实时订阅 — WebSocket

低延迟（10-50ms）的流式数据推送，适合实时行情看板、量化策略与 Agent 自动化场景。

### 支持的频道

- `ticker` - 实时价格更新
- `depth` - 订单簿（Order Book）变化
- `trade` - 实时成交执行

```javascript
const ws = new WebSocket('wss://api.tickdb.ai/v1/realtime?api_key=YOUR_API_KEY');

ws.onopen = () => {
    // 订阅实时价格
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'ticker', symbols: ['BTCUSDT'] }
    }));

    // 订阅订单簿变化
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'depth', symbols: ['BTCUSDT'] }
    }));

    // 订阅实时成交数据
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'trade', symbols: ['BTCUSDT'] }
    }));
};
```

---

<a id="ai-access"></a>
## 🤖 AI 接入

TickDB 是 **AI-native** 行情数据 API，提供三档原生接入方式，覆盖从零配置对话到生产级深度集成的全场景需求。

<a id="skill"></a>
### 💬 Skill — 对话即用

安装后 AI 自动获取试用 Key，无需注册即可查询 72 个热门品种：

```bash
npx clawhub@latest install tickdb-market-data
```

或直接使用本仓库 [SKILL 文件](SKILL/SKILL.md)。

<a id="mcp"></a>
### 🔌 MCP — 永久集成

一次配置，让 Claude、Cursor、Kiro 等 AI 编码客户端永久获得 13 个行情工具。

**托管端点（推荐，无需自部署）：**

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

支持客户端：Claude Code · Claude Desktop · Cursor · Kiro · Codex · Zed · Cherry Studio

**MCP 服务端已开源**，代码位于本仓库 [`mcp/`](mcp/) 目录。

📊 **mcp/ 概览**：13 个 MCP 工具 · Python 3.11+ · Docker 就绪 · 46 单元测试 · MIT 许可证 · CI 持续验证

| 文档 | 链接 |
|------|------|
| 客户端接入配置 | [mcp/MCP_CLIENT_SETUP.md](mcp/MCP_CLIENT_SETUP.md) |
| 部署说明（自部署） | [mcp/DEPLOYMENT.md](mcp/DEPLOYMENT.md) |
| MCP 完整文档 | [mcp/README.md](mcp/README.md) |

<a id="cli"></a>
### 💻 CLI — 终端 & Agent

```bash
npm install -g tickdb
tickdb config set-key YOUR_API_KEY
tickdb ticker BTCUSDT,XAUUSD
```

详见 [官网 AI 接入页面](https://tickdb.ai/ai-tools)。

---

## 📚 在线文档

完整的 API 参考、参数说明、以及可直接运行的示例请求：

- **Docs**: https://docs.tickdb.ai
- **官网**: https://tickdb.ai
- **AI 接入页面**: https://tickdb.ai/ai-tools

---

## 🤝 社区和支持

- **GitHub Issues** - [报告错误或请求功能](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/issues)
- **技术支持** - [Telegram](https://t.me/TickDB_Support)
- **邮箱** - [support@tickdb.ai](mailto:support@tickdb.ai)
- **文档** - [docs.tickdb.ai](https://docs.tickdb.ai)

---

## 📄 许可证

本文档采用 [MIT 许可证](LICENSE)。
