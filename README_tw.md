<div align="center">

<img src="assets/logo.svg" alt="TickDB Logo" width="320">

# TickDB — Unified Real-time Market Data API for Forex, Stocks, Futures, Crypto

*One connection for Forex, Precious Metals, Indices, US Stocks, HK Stocks, A-Shares, China/Hong Kong Futures, and Crypto*

*開源工具集 · 完整 API 文件 + AI Skill + MCP 服務端實作*

[![MCP CI](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml)
[![Docs Check](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/docs-quality.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/docs-quality.yml)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

**語言版本:** [简体中文](README.md) • [繁體中文](README_tw.md) • [English](README_en.md)

[在線文件](https://docs.tickdb.ai) • [官網](https://tickdb.ai) • [AI 接入](#ai-access)

</div>

---

## 什麼是 TickDB？

TickDB 是面向開發者、AI 代理和多市場金融應用的 **AI 原生即時行情資料 API**（AI-native real-time market data API）。

通過 **一次接入（one connection）**，無縫存取外匯（Forex）、貴金屬（Precious Metals）、指數（Indices）、美股（US Stocks / NASDAQ / NYSE）、港股（HK Stocks）、A 股（A-Shares）、中國及香港期貨（China/Hong Kong Futures）、加密貨幣（Cryptocurrency）等多個金融市場的即時與歷史行情資料。

TickDB 專為需要**可靠、低延遲、可長期依賴**行情資料的開發者構建，幫助你**避免管理多個資料源、協定和供應商的複雜性**，專注於業務和策略本身。

> 支援逐筆成交（tick-by-tick trades）、盤口深度（order book / depth）、K 線（candlestick）等多種行情形式，
> 透過 REST API 與 WebSocket 接入，覆蓋量化交易、AI Agent、即時行情系統、交易平台與資料分析場景。

---

## 快速接入

**本倉庫提供完整原始碼**：[`SKILL/`](SKILL/)（AI Skill，含介面參考）· [`mcp/`](mcp/)（Python MCP 服務端，43 工具 · Dockerfile · 自動化測試 · CI · MIT）。可基於 [`mcp/`](mcp/) 自部署，也可使用公開託管端點 `mcp.tickdb.ai`。

選一種適合你的接入方式：

| 方式 | 適合 | 說明 |
|------|------|------|
| [Skill](#skill) | AI 對話即用，零配置 | npx 一鍵安裝，AI 自動取得試用 Key |
| [MCP](#mcp) | AI 編碼客戶端 / 自部署開源 | 基於 [`mcp/`](mcp/) 自部署，或使用託管 OAuth / 請求標頭接入 |
| [CLI](#cli) | 終端 / 腳本 / AI Agent | npm 全域安裝，命令列直查行情 |
| [REST API](#rest-api) | 應用整合 | 行情、期貨與財務基本面 HTTP API |
| [WebSocket](#websocket) | 即時串流資料 | 低延遲訂閱 ticker / depth / trade |

---

## 核心特性

- 統一接入：一套 API 覆蓋外匯、貴金屬、指數、美股、港股、A 股、中國及香港期貨、加密貨幣
- 即時資料：基於 WebSocket 的串流推送，端到端延遲約 10-50ms
- 公司財務與基本面：REST API 提供美股、港股、A 股財報、PE 估值、營收組成、股東與公司事件查詢
- AI 原生：官方提供 Skill / MCP / CLI 三檔 AI 接入，AI Agent 與編碼助理開箱即用
- 開發者友好：RESTful API + WebSocket，結構化 JSON 回應，完整文件與多語言範例
- 全球覆蓋：涵蓋股票、外匯、貴金屬、指數、中國及香港期貨與加密貨幣；品種及數量以產品目錄回傳為準
- 免費開始：無需信用卡，立即取得 API 金鑰

---

## 典型使用場景

- 量化交易（Quantitative Trading）：演算法與策略系統的即時行情資料源
- AI Agent / 編碼助理：透過 Skill / MCP 讓 AI 助理直接呼叫行情資料，自然語言驅動查詢
- 行情看板：即時價格展示、資產與投資組合監控
- 交易應用：構建類似 TradingView 的行情介面與圖表系統
- 資料分析與回測（Backtesting）：歷史行情分析、策略回測與研究
- 金融服務整合：整合到現有交易平台或金融基礎設施中
- 自部署 / 私有化：不想用托管端點？基於本倉庫 [`mcp/`](mcp/) 代碼自部署，完全掌控資料流

---

<a id="rest-api"></a>
## 快速開始 — REST API

同一 REST API 提供行情與公司財務和基本面查詢；財務介面包括財報、估值、股東持股與分類財經日曆。

[身份驗證與基礎資訊](#rest-auth) · [行情核心 API](#market-api) · [公司財務與基本面 API](#fundamentals-api)

<a id="rest-auth"></a>
### 身份驗證與基礎資訊

訪問 [TickDB.ai](https://tickdb.ai) 註冊帳戶，即可取得 API 金鑰。

#### 身份驗證

所有 HTTP API 請求都需要在請求標頭中包含 API 金鑰：

```http
X-API-Key: YOUR_API_KEY
```

#### 基礎 URL

```
https://api.tickdb.ai
```

#### API Key 訂閱查詢

- `GET /v1/apikeys/subscriptions` — 查詢目前驗證帳戶下 API Key 的方案、狀態與到期情況

#### 支援的市場

| 市場類型 | Symbol 格式範例 | 說明 |
|---------|----------------|------|
| 外匯（Forex / FX） | `GBPUSD` | 主要貨幣對（Base/Quote） |
| 貴金屬（Precious Metals） | `XAUUSD` | 貴金屬對美元（Commodity / USD） |
| 美股（US Stocks） | `AAPL.US` | NYSE / NASDAQ 上市股票 |
| 指數（Indices） | `SPX` | 股票指數（如標準普爾 500） |
| 港股（HK Stocks） | `700.HK` | 港交所上市證券 |
| A 股（A-Shares） | `600519.SH` | 上海 / 深圳交易所股票 |
| 中國期貨（China Futures） | `AP8888` | `type=futures`、`market=CN`；具體合約及連續合約以目錄為準 |
| 香港期貨（HK Futures） | `HSI8888` | `type=futures`、`market=HK`；具體合約及連續合約以目錄為準 |
| 加密貨幣（Cryptocurrency） | `BTCUSDT` | 加密資產交易對 |

期貨支援即時行情、K 線、買賣盤與逐筆成交查詢；K 線可回傳持倉量 `open_interest`。代碼須從 `/v1/symbols/available?type=futures` 查詢，一般合約隨交割月變化；`7777`、`8888`、`9999` 分別表示次主力、主力和加權連續，連續合約不代表實際可交割合約。上表僅展示代碼格式，資料可用性取決於品種與 Key 權限。

<a id="market-api"></a>
### 行情核心 API

#### 通用行情

- `GET /v1/symbols/available` — 產品目錄，含中國及香港期貨
- `GET /v1/market/ticker` — 指定品種的即時行情快照
- `GET /v1/market/kline` — 歷史 K 線
- `GET /v1/market/kline/latest` — 目前週期的即時 K 線
- `GET /v1/market/depth` — 買賣盤深度
- `GET /v1/market/trades` — 逐筆成交（Tick-by-Tick Trades）

#### 全量行情快照

- `GET /v1/market/ticker/cn-stock` — A 股全量行情快照
- `GET /v1/market/ticker/hk-stock` — 港股全量行情快照
- `GET /v1/market/ticker/us-stock` — 美股全量行情快照

#### 股票行情與市場資訊

- `GET /v1/market/stock-info` — 股票基本資訊
- `GET /v1/market/intraday` — 股票當日分時
- `GET /v1/market/kline/ex-factors` — 股票復權因子
- `GET /v1/market/calc-index` — 股票綜合指標
- `GET /v1/market/capital-flow` — 股票資金流向
- `GET /v1/market/trading-sessions` — 市場交易時段
- `GET /v1/market/trade-days` — 市場交易日曆

#### 取得 K 線（K-line）資料

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/kline?symbol=700.HK&interval=1h&limit=24"
```

#### 取得即時行情（Ticker）資料

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/ticker?symbols=AAPL.US,700.HK,BTCUSDT"
```

#### 取得盤口深度（Depth）資料

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/depth?symbol=AAPL.US"
```

#### 取得逐筆成交（Tick-by-Tick Trades）資料

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/trades?symbol=AAPL.US&limit=20"
```

#### 查詢可用交易品種

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/symbols/available?market=HK&limit=10"
```

查詢中國及香港期貨目錄：

```bash
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/symbols/available?type=futures&market=CN&limit=10"
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/symbols/available?type=futures&market=HK&limit=10"
```

<a id="fundamentals-api"></a>
### 公司財務與基本面 API

財務與基本面提供 29 個 HTTP 端點，涵蓋美股、港股和 A 股；直接使用同一 Base URL 與 `X-API-Key`，無需透過 MCP。資料涵蓋範圍取決於品種、披露時間和 Key 的介面及市場權限。

#### 公司概況

- `GET /v1/fundamentals/profile` — 公司資料
- `GET /v1/fundamentals/executives` — 高階主管與董事
- `GET /v1/fundamentals/segments/latest` — 最新業務與地區營收組成
- `GET /v1/fundamentals/segments/history` — 歷史營收組成

#### 財務報表

- `GET /v1/fundamentals/financials/latest` — 最新財報：損益表、資產負債表、現金流量表
- `GET /v1/fundamentals/financials/annual` — 年度財務報表
- `GET /v1/fundamentals/financials/ttm` — TTM 損益表與現金流量表

#### 估值與產業

- `GET /v1/fundamentals/valuation/latest` — 最新 PE 估值
- `GET /v1/fundamentals/valuation/ts` — 歷史 PE 時序
- `GET /v1/fundamentals/industry/peers` — 同業公司比較
- `GET /v1/fundamentals/industry/dist` — 個股產業指標分布
- `GET /v1/fundamentals/industries/rank` — 市場產業排行
- `GET /v1/fundamentals/industries/tree` — 產業分類層級

#### 股利與公司行動

- `GET /v1/fundamentals/dividends` — 歷史與已知未來股利事件
- `GET /v1/fundamentals/dividends/ttm` — 過去 12 個月每股現金股利
- `GET /v1/fundamentals/buyback` — 公司回購
- `GET /v1/fundamentals/corp-actions` — 公司資本行動

#### 股東與基金持股

- `GET /v1/fundamentals/shareholders/latest` — 最新股東持股
- `GET /v1/fundamentals/shareholders/top` — 多個報告期的主要股東
- `GET /v1/fundamentals/shareholders/detail` — 股東持股與交易明細
- `GET /v1/fundamentals/fund-holdings/latest` — 持有該股票的基金

#### 財經日曆

- `GET /v1/fundamentals/calendar/report` — 財報與業績日曆
- `GET /v1/fundamentals/calendar/dividend` — 股利日曆
- `GET /v1/fundamentals/calendar/split` — 拆股與合股日曆
- `GET /v1/fundamentals/calendar/ipo` — 發行與上市日曆
- `GET /v1/fundamentals/calendar/other` — 其他分類事件

#### 新聞與市場狀態

- `GET /v1/fundamentals/news` — 公司新聞列表
- `GET /v1/fundamentals/news/{news_id}` — 新聞正文或節錄
- `GET /v1/fundamentals/market/status` — 美股、港股、A 股市場狀態

詳細參數、回應欄位與錯誤碼見[官方 API 文件](https://docs.tickdb.ai/zh-Hant/index)。

#### 查詢財務報表

以下範例分別查詢最近四期損益表、最近三年資產負債表與 TTM 現金流量表：

```bash
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/financials/latest?symbol=AAPL.US&type=stock&kind=IS&n=4"
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/financials/annual?symbol=AAPL.US&type=stock&kind=BS&n=3"
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/financials/ttm?symbol=AAPL.US&type=stock&kind=CF"
```

#### 查詢 PE 估值與股利

```bash
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/valuation/latest?symbol=AAPL.US&type=stock"
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/dividends?symbol=AAPL.US&type=stock&limit=20"
```

#### 查詢分類財報日曆

```bash
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/calendar/report?market=US&symbols=AAPL.US&limit=100"
```

---

<a id="websocket"></a>
## 即時訂閱 — WebSocket

低延遲（10-50ms）的串流資料推送，適合即時行情看板、量化策略與 Agent 自動化場景。

### 一般行情訂閱

- [`ticker`](https://docs.tickdb.ai/zh-Hant/websocket/ticker) — 指定品種的即時行情
- [`depth`](https://docs.tickdb.ai/zh-Hant/websocket/depth) — 買賣盤更新
- [`trade`](https://docs.tickdb.ai/zh-Hant/websocket/trade) — 逐筆成交即時推送

### 全量行情訂閱

- [`CN_Stock`](https://docs.tickdb.ai/zh-Hant/websocket/ticker_cn_stock) — A 股全量行情
- [`HK_Stock`](https://docs.tickdb.ai/zh-Hant/websocket/ticker_hk_stock) — 港股全量行情
- [`US_Stock`](https://docs.tickdb.ai/zh-Hant/websocket/ticker_us_stock) — 美股全量行情

### 連線控制與使用說明

- [`ping / pong`](https://docs.tickdb.ai/zh-Hant/websocket/ping) — 連線心跳檢測
- [`unsubscribe`](https://docs.tickdb.ai/zh-Hant/websocket/ticker) — 取消訂閱

全量行情需在連線時協商 `permessage-deflate`；訊息格式、心跳、斷線重連與恢復訂閱見[官方連線指南](https://docs.tickdb.ai/zh-Hant/websocket/websocket_quickstart)。

#### 多市場訂閱與壓縮（Node.js）

以下範例使用 Node.js 的 `ws` 函式庫。先執行 `npm install ws`，設定環境變數 `TICKDB_API_KEY`，將程式碼儲存為 `market-stream.cjs` 後執行 `node market-stream.cjs`。訂閱品種和全市場集合須符合 Key 權限，代碼以產品目錄實際回傳為準；只需一般行情時，將 `fullMarkets` 設為空陣列。

`perMessageDeflate` 直接在 `new WebSocket` 中啟用，壓縮在交握階段協商，`ws` 自動解壓縮訊息。範例同時處理一般單筆訊息與全量快照、增量更新的陣列訊息。瀏覽器原生 WebSocket 不接受此選項。

```javascript
const WebSocket = require('ws');

const apiKey = process.env.TICKDB_API_KEY;
if (!apiKey) throw new Error('Set TICKDB_API_KEY before running this example');

const tickerSymbols = [
    'EURUSD', // 外匯
    'XAUUSD', // 貴金屬
    'SPX', // 指數
    'AAPL.US', // 美股
    '700.HK', // 港股
    '600519.SH', // A 股
    'AP8888', // 中國期貨
    'HSI8888', // 香港期貨
    'BTCUSDT', // 加密貨幣
];
const depthSymbols = ['AAPL.US', '700.HK', '600519.SH', 'AP8888', 'BTCUSDT'];
const tradeSymbols = [...depthSymbols, 'HSI8888'];
const fullMarkets = ['CN_Stock', 'HK_Stock', 'US_Stock'];

const endpoint = new URL('wss://api.tickdb.ai/v1/realtime');
endpoint.searchParams.set('api_key', apiKey);
const ws = new WebSocket(endpoint, {
    perMessageDeflate: true // 在連線交握時協商 permessage-deflate 壓縮，ws 自動解壓縮。
});

ws.on('open', () => {
    if (fullMarkets.length && !ws.extensions.includes('permessage-deflate')) {
        console.error('Full-market data requires permessage-deflate');
        ws.close();
        return;
    }

    // 混合產品類型時省略 type；有歧義的代碼按類型另行訂閱。
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'ticker', symbols: tickerSymbols }
    }));
    // 買賣盤範例：美股、港股、A 股、中國期貨與加密貨幣。
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'depth', symbols: depthSymbols }
    }));
    // 逐筆成交範例額外包含香港期貨。
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'trade', symbols: tradeSymbols }
    }));

    // 全量與個股 ticker 獨立訂閱，可同時使用，不影響 depth 和 trade。
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

    // 一般推送為物件；全量快照和增量更新為陣列。
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
## AI 接入

TickDB 是 **AI-native** 行情資料 API，提供三檔原生接入方式，覆蓋從零配置對話到生產級深度整合的全場景需求。

<a id="skill"></a>
### Skill — 對話即用

安裝後 AI 自動取得試用 Key，無需註冊即可查詢清單中的 62 個品種：

```bash
npx clawhub@latest install tickdb-market-data
```

或將本倉庫完整的 [`SKILL/` 目錄](SKILL/)複製到用戶端的 Skill 目錄，並命名為 `tickdb-market-data`，保留 `SKILL.md` 和 `references/`。支援行情、復權 K 線、期貨、財務基本面及 API Key 套餐與到期查詢；實際可用範圍取決於 Key 權限。

<a id="mcp"></a>
### MCP — 永久整合

本倉庫 MCP 與 Skill 涵蓋 43 個 REST 端點，不包含上述三市場全量行情與 WebSocket 能力。

一次設定，讓 AI 助理透過 MCP 服務使用 **43 個工具：13 個行情工具、29 個公司財務與基本面工具、1 個 API Key 訂閱查詢工具**。

| 能力 | 使用者可查詢的內容 |
|------|--------------------|
| 行情與股票（13 工具） | 即時報價、復權 K 線、復權因子、買賣盤、逐筆成交、資金流向與期貨品種 |
| 公司財務與基本面（29 工具） | 公司資料、財報、PE 估值、產業、股東持股、股利回購、新聞與分類財經日曆 |
| API Key 訂閱（1 工具） | 目前 Key 所屬帳戶回傳的方案、狀態、到期時間與剩餘時長 |

行情涵蓋外匯、貴金屬、指數、美股、港股、A 股、中港期貨和加密貨幣；公司財務與基本面涵蓋美股、港股和 A 股，具體可用性取決於品種、披露時間及方案權限。

**自部署：** 使用 [`mcp/`](mcp/) 中的 Python 原始碼或 Dockerfile，參見下方部署指南。網頁 OAuth 預設關閉，按指南設定後可啟用。

**本地啟動（Python 3.11+）：** 在 Linux 終端機中從倉庫根目錄執行；首次安裝複製 `.env`，升級時保留既有設定。

```bash
cd mcp
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cp .env.example .env
# 編輯 .env，填寫 TICKDB_API_KEY；也可由客戶端透過請求標頭提供 Key
python main.py
```

本地服務位址為 `http://localhost:8000/mcp`。Docker 和 HTTPS OAuth 設定見[自部署指南](mcp/docs/tw/DEPLOYMENT.md)。

**公開託管端點（可選，無需自部署）：**

- **網頁 OAuth 接入（ChatGPT / Claude）：** 伺服器 URL 使用 `https://mcp.tickdb.ai/oauth`，選擇 OAuth，在 TickDB 授權頁驗證自己的 API Key 並確認授權。
- **請求標頭接入（AI 編碼客戶端）：** 使用 `https://mcp.tickdb.ai/`，透過 `X-TickDB-Key` 傳入 API Key，設定如下。

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

各客戶端設定及 Claude Desktop 本地 stdio 模式見下方接入指南。

**MCP 服務端已開源**，代碼位於本倉庫 [`mcp/`](mcp/) 目錄。

**mcp/ 概覽**：v0.2.3 · 43 個 MCP 工具 · Python 3.11+ · Docker 就緒 · 自動化測試 · MIT 授權條款 · CI 持續驗證

| 文件 | 連結 |
|------|------|
| 客戶端接入設定 | [mcp/docs/tw/MCP_CLIENT_SETUP.md](mcp/docs/tw/MCP_CLIENT_SETUP.md) |
| 部署說明（自部署） | [mcp/docs/tw/DEPLOYMENT.md](mcp/docs/tw/DEPLOYMENT.md) |
| MCP 完整文件 | [mcp/docs/tw/README.md](mcp/docs/tw/README.md) |
| 網頁 OAuth 接入與自部署設定 | [MCP OAuth 設定](mcp/docs/tw/README.md#oauth-setup) |
| 版本更新記錄 | [MCP Changelog](mcp/docs/tw/CHANGELOG.md) |

<a id="cli"></a>
### CLI — 終端 & Agent

```bash
npm install -g tickdb
tickdb config set-key YOUR_API_KEY
tickdb ticker BTCUSDT,XAUUSD
```

詳見 [官網 AI 接入頁面](https://tickdb.ai/ai-tools)。

---

## 在線文件

完整的 API 參考、參數說明、以及可直接執行的範例請求：

- **Docs**: https://docs.tickdb.ai
- **官網**: https://tickdb.ai
- **AI 接入頁面**: https://tickdb.ai/ai-tools

---

## 社群和支援

- GitHub Issues：[回報錯誤或請求功能](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/issues)
- 技術支援：[Telegram](https://t.me/TickDB_Support)
- 電子郵件：[support@tickdb.ai](mailto:support@tickdb.ai)
- 文件：[docs.tickdb.ai](https://docs.tickdb.ai)

---

## 授權條款

本文件採用 [MIT 授權條款](LICENSE)。
