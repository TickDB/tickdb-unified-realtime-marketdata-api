<div align="center">

<img src="assets/logo.svg" alt="TickDB Logo" width="320">

# TickDB — Unified Real-time Market Data API for Forex, Stocks, Crypto

*One connection for Forex, Precious Metals, Indices, US Stocks, HK Stocks, A-Shares, and Crypto*

*開源工具集 · 完整 API 文件 + AI Skill + MCP 服務端實作*

[![API Status](https://img.shields.io/badge/API-Live-green)](https://tickdb.ai)
[![AI-Native](https://img.shields.io/badge/AI--Native-Skill%20%7C%20MCP%20%7C%20CLI-purple)](#ai-access)
[![MCP CI](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml)
[![Docs Check](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/docs-quality.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/docs-quality.yml)
[![WebSocket](https://img.shields.io/badge/WebSocket-Supported-blue)](https://tickdb.ai)
[![Latency](https://img.shields.io/badge/Latency-10--50ms-blue)](#)
[![Docs](https://img.shields.io/badge/Docs-docs.tickdb.ai-brightgreen)](https://docs.tickdb.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**語言版本:** [🇨🇳 简体中文](README.md) • [🇹🇼 繁體中文](README_tw.md) • [🇺🇸 English](README_en.md)

[📚 在線文件](https://docs.tickdb.ai) • [🌐 官網](https://tickdb.ai) • [🤖 AI 接入 ↓](#ai-access)

</div>

---

## 🎯 什麼是 TickDB？

TickDB 是面向開發者、AI 代理和多市場金融應用的 **AI 原生即時行情資料 API**（AI-native real-time market data API）。

通過 **一次接入（one connection）**，無縫存取外匯（Forex）、貴金屬（Precious Metals）、指數（Indices）、美股（US Stocks / NASDAQ / NYSE）、港股（HK Stocks）、A 股（A-Shares）、加密貨幣（Cryptocurrency）等多個金融市場的即時與歷史行情資料。

TickDB 專為需要**可靠、低延遲、可長期依賴**行情資料的開發者構建，幫助你**避免管理多個資料源、協定和供應商的複雜性**，專注於業務和策略本身。

> 支援 tick 級成交（trades）、盤口深度（order book / depth）、K 線（candlestick）等多種行情形式，
> 透過 REST API 與 WebSocket 接入，覆蓋量化交易、AI Agent、即時行情系統、交易平台與資料分析場景。

---

## 🚀 快速接入

📦 **本倉庫提供完整原始碼**：[`SKILL/`](SKILL/)（AI Skill 設定檔）· [`mcp/`](mcp/)（Python MCP 服務端，13 工具 · Dockerfile · 46 單元測試 · CI · MIT）。托管端點 `mcp.tickdb.ai` 即基於 [`mcp/`](mcp/) 代碼運行 — 你看到的、你部署的、官方在跑的，是同一套代碼。

選一種適合你的接入方式：

| 方式 | 適合 | 說明 |
|------|------|------|
| 💬 **[Skill](#skill)** | AI 對話即用，零配置 | npx 一鍵安裝，AI 自動取得試用 Key |
| 🔌 **[MCP](#mcp)** | AI 編碼客戶端 / 自部署開源 | 托管端點 + JSON 設定，或基於 [`mcp/`](mcp/) 自部署 |
| 💻 **[CLI](#cli)** | 終端 / 腳本 / AI Agent | npm 全域安裝，命令列直查行情 |
| 🔧 **[REST API](#rest-api)** | 應用整合 | HTTP API + 6 個端點範例 |
| 🌐 **[WebSocket](#websocket)** | 即時串流資料 | 低延遲訂閱 ticker / depth / trade |

---

## ✨ 核心特性

- **🔌 統一接入** - 一套 API 覆蓋外匯、貴金屬、指數、美股、港股、A 股、加密貨幣
- **⚡ 即時資料** - 基於 WebSocket 的串流推送，端到端延遲約 10-50ms
- **🤖 AI 原生** - 官方提供 Skill / MCP / CLI 三檔 AI 接入，AI Agent 與編碼助理開箱即用
- **🛠️ 開發者友好** - RESTful API + WebSocket，結構化 JSON 回應，完整文件與多語言範例
- **🌍 全球覆蓋** - 37,527+ 品種，6 大市場（US/HK/CN + Forex/Crypto/Indices）
- **🆓 免費開始** - 無需信用卡，立即取得 API 金鑰

---

## 🏗️ 典型使用場景

- **量化交易（Quantitative Trading）** - 演算法與策略系統的即時行情資料源
- **AI Agent / 編碼助理** - 透過 Skill / MCP 讓 AI 助理直接呼叫行情資料，自然語言驅動查詢
- **行情看板** - 即時價格展示、資產與投資組合監控
- **交易應用** - 構建類似 TradingView 的行情介面與圖表系統
- **資料分析與回測（Backtesting）** - 歷史行情分析、策略回測與研究
- **金融服務整合** - 整合到現有交易平台或金融基礎設施中
- **自部署 / 私有化** - 不想用托管端點？基於本倉庫 [`mcp/`](mcp/) 代碼自部署，完全掌控資料流

---

<a id="rest-api"></a>
## 🚀 快速開始 — REST API

### 1. 註冊並取得 API 金鑰

訪問 [TickDB.ai](https://tickdb.ai) 註冊帳戶，即可取得 API 金鑰。

#### 🔑 身份驗證

所有 HTTP API 請求都需要在請求標頭中包含 API 金鑰：

```http
X-API-Key: YOUR_API_KEY
```

#### 🌐 基礎 URL

```
https://api.tickdb.ai
```

#### 📋 HTTP API 核心介面

| 介面 | 方法 | 描述 |
|------|------|------|
| `/v1/market/kline` | GET | 歷史 K 線 / 蠟燭圖（Candlestick）資料 |
| `/v1/market/ticker` | GET | 即時行情（Ticker）資料 |
| `/v1/market/depth` | GET | 訂單簿深度（Order Book）資料 |
| `/v1/market/trades` | GET | 最近成交（Recent Trades）歷史 |

#### 🏪 支援的市場

| 市場類型 | Symbol 格式範例 | 說明 |
|---------|----------------|------|
| 外匯（Forex / FX） | `GBPUSD` | 主要貨幣對（Base/Quote） |
| 貴金屬（Precious Metals） | `XAUUSD` | 貴金屬對美元（Commodity / USD） |
| 美股（US Stocks） | `AAPL.US` | NYSE / NASDAQ 上市股票 |
| 指數（Indices） | `SPX` | 股票指數（如標準普爾 500） |
| 港股（HK Stocks） | `700.HK` | 港交所上市證券 |
| A 股（A-Shares） | `600519.SH` | 上海 / 深圳交易所股票 |
| 加密貨幣（Cryptocurrency） | `BTCUSDT` | 加密資產交易對 |

### 2. 取得 K 線（K-line）資料

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/kline?symbol=700.HK&interval=1h&limit=24"
```

### 3. 取得即時行情（Ticker）資料

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/ticker?symbols=AAPL.US,700.HK,BTCUSDT"
```

### 4. 取得盤口深度（Depth）資料

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/depth?symbol=AAPL.US&limit=10"
```

### 5. 取得成交記錄（Trades）資料

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/trades?symbols=AAPL.US&limit=20"
```

### 6. 查詢可用交易品種

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/symbols/available?market=HK&limit=10"
```

---

<a id="websocket"></a>
## 🌐 即時訂閱 — WebSocket

低延遲（10-50ms）的串流資料推送，適合即時行情看板、量化策略與 Agent 自動化場景。

### 支援的頻道

- `ticker` - 即時價格更新
- `depth` - 訂單簿（Order Book）變化
- `trade` - 即時成交執行

```javascript
const ws = new WebSocket('wss://api.tickdb.ai/v1/realtime?api_key=YOUR_API_KEY');

ws.onopen = () => {
    // 訂閱即時價格
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'ticker', symbols: ['BTCUSDT'] }
    }));

    // 訂閱訂單簿變化
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'depth', symbols: ['BTCUSDT'] }
    }));

    // 訂閱即時成交資料
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'trade', symbols: ['BTCUSDT'] }
    }));
};
```

---

<a id="ai-access"></a>
## 🤖 AI 接入

TickDB 是 **AI-native** 行情資料 API，提供三檔原生接入方式，覆蓋從零配置對話到生產級深度整合的全場景需求。

<a id="skill"></a>
### 💬 Skill — 對話即用

安裝後 AI 自動取得試用 Key，無需註冊即可查詢 72 個熱門品種：

```bash
npx clawhub@latest install tickdb-market-data
```

或直接使用本倉庫 [SKILL 文件](SKILL/SKILL.md)。

<a id="mcp"></a>
### 🔌 MCP — 永久整合

一次配置，讓 Claude、Cursor、Kiro 等 AI 編碼客戶端永久獲得 13 個行情工具。

**托管端點（推薦，無需自部署）：**

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

支援客戶端：Claude Code · Claude Desktop · Cursor · Kiro · Codex · Zed · Cherry Studio

**MCP 服務端已開源**，代碼位於本倉庫 [`mcp/`](mcp/) 目錄。

📊 **mcp/ 概覽**：13 個 MCP 工具 · Python 3.11+ · Docker 就緒 · 46 單元測試 · MIT 授權條款 · CI 持續驗證

| 文件 | 連結 |
|------|------|
| 客戶端接入設定 | [mcp/docs/tw/MCP_CLIENT_SETUP.md](mcp/docs/tw/MCP_CLIENT_SETUP.md) |
| 部署說明（自部署） | [mcp/docs/tw/DEPLOYMENT.md](mcp/docs/tw/DEPLOYMENT.md) |
| MCP 完整文件 | [mcp/docs/tw/README.md](mcp/docs/tw/README.md) |

<a id="cli"></a>
### 💻 CLI — 終端 & Agent

```bash
npm install -g tickdb
tickdb config set-key YOUR_API_KEY
tickdb ticker BTCUSDT,XAUUSD
```

詳見 [官網 AI 接入頁面](https://tickdb.ai/ai-tools)。

---

## 📚 在線文件

完整的 API 參考、參數說明、以及可直接執行的範例請求：

- **Docs**: https://docs.tickdb.ai
- **官網**: https://tickdb.ai
- **AI 接入頁面**: https://tickdb.ai/ai-tools

---

## 🤝 社群和支援

- **GitHub Issues** - [回報錯誤或請求功能](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/issues)
- **技術支援** - [Telegram](https://t.me/TickDB_Support)
- **電子郵件** - [support@tickdb.ai](mailto:support@tickdb.ai)
- **文件** - [docs.tickdb.ai](https://docs.tickdb.ai)

---

## 📄 授權條款

本文件採用 [MIT 授權條款](LICENSE)。
