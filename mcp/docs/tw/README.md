# TickDB MCP — AI 即時行情數據服務

[![CI](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../../LICENSE)
[![TickDB](https://img.shields.io/badge/Powered%20by-TickDB-orange)](https://tickdb.ai)

> 📍 本目錄是 [tickdb-unified-realtime-marketdata-api](../../../) 倉庫的 MCP 服務端實作，提供 13 個 MCP 工具，可作為 Python 套件獨立部署。

**TickDB-MCP** 是基於 [Model Context Protocol (MCP)](https://modelcontextprotocol.io) 的 Python 服務端實作，透過統一的 REST API 介面為 AI 助理提供即時行情資料（Real-time Market Data）與歷史 K 線（Historical K-line）資料。

涵蓋 **外匯（Forex/FX） · 貴金屬（Precious Metals） · 指數（Indices） · 美股（US Stocks / NASDAQ / NYSE） · 港股（HK Stocks） · A 股（A-shares / CN Stocks） · 加密貨幣（Cryptocurrency）**，由 13 個 MCP 工具組成，資料來源為 [TickDB Unified Market Data API](https://tickdb.ai)。

**連結：** [官網](https://tickdb.ai) · [文件](https://docs.tickdb.ai) · [聯絡我們](mailto:support@tickdb.ai)

**其他語言：** [简体中文](../../README.md) · [English](../en/README.md)

---

## 快速開始

```bash
# 1. 安裝相依套件（Python 3.11+）
pip install -e .

# 2. 設定環境變數
cp .env.example .env
# 編輯 .env，填入 TICKDB_API_KEY（前往 https://tickdb.ai 註冊取得）

# 3. 啟動 MCP 服務端
python main.py          # HTTP 服務，監聽 :8000
```

在 AI 客戶端設定中加入（也可直接使用托管端點 `https://mcp.tickdb.ai/`）：

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

支援的 AI 客戶端：Claude Code · Claude Desktop · Cursor · Kiro · Codex · Zed · Cherry Studio

---

## 13 個 MCP 工具

| 工具 | 說明 | 資料類型 |
|---|---|---|
| `get_ticker` | 即時行情快照（Ticker）：價格、漲跌幅、成交量 | Real-time |
| `get_kline` | 歷史 K 線（Candlestick / K-line）OHLCV 資料 | Historical |
| `get_kline_latest` | 最新即時 K 線（當前未收盤） | Real-time |
| `get_order_book` | 買賣盤深度（Order Book / Depth） | Real-time |
| `get_recent_trades` | 最近成交明細（Recent Trades） | Real-time |
| `get_available_symbols` | 查詢全部可交易標的（37,527+ 品種） | Reference |
| `get_kline_intervals` | 支援的 K 線週期列表 | Reference |
| `get_stock_info` | 股票基本資訊：EPS、BPS、股息率等 | Fundamental |
| `get_intraday` | 當日分時資料（Intraday Data） | Intraday |
| `get_trading_sessions` | 當前交易時段（Trading Session） | Reference |
| `get_trade_days` | 交易日曆（Trading Calendar） | Reference |
| `get_market_metrics` | 市場快照（Market Snapshot）：PE/PB、市值、資金流 | Fundamental |
| `get_capital_flow` | 大中小單資金流向分析（Capital Flow） | Real-time |

---

## 覆蓋市場與標的代碼格式

| 市場 | 品種數 | 代碼格式 | 範例 |
|---|---|---|---|
| 加密貨幣（Cryptocurrency） | 875+ | `BASE + QUOTE` | `BTCUSDT`、`ETHUSDT` |
| 外匯（Forex / FX） | 1,207 | 6 字母貨幣對 | `EURUSD`、`USDJPY`、`XAUUSD` |
| 貴金屬（Precious Metals） | — | `XAU/XAG + USD` | `XAUUSD`、`XAGUSD` |
| 美股（US Stocks / NASDAQ / NYSE） | 12,409 | `TICKER.US` | `AAPL.US`、`TSLA.US`、`NVDA.US` |
| 港股（HK Stocks） | 4,305 | `CODE.HK` | `700.HK`、`9988.HK` |
| A 股 / 滬市（A-shares / CN Stocks） | 6,023 | `6位代碼.SH` | `600519.SH`、`601318.SH` |
| A 股 / 深市（A-shares / CN Stocks） | — | `6位代碼.SZ` | `000858.SZ`、`000333.SZ` |
| 指數（Indices） | 12,708 | 指數代碼 | `SPX`、`NDX`、`VIX`、`DXY` |

---

## 設定說明（Configuration）

將 `.env.example` 複製為 `.env`：

| 變數 | 預設值 | 說明 |
|---|---|---|
| `TICKDB_API_KEY` | _（空）_ | 伺服器統一 API Key；空時要求使用者透過 `X-TickDB-Key` 請求標頭自帶 |
| `MCP_ACCESS_TOKEN` | _（空）_ | MCP 服務存取 Token；空時服務開放存取 |
| `MCP_TRANSPORT` | `streamable-http` | `stdio` 用於本地 Claude Desktop 直連模式 |
| `MCP_HOST` | `0.0.0.0` | 監聽位址 |
| `MCP_PORT` | `8000` | 監聽埠號 |
| `MCP_STATELESS_HTTP` | `true` | Streamable HTTP 無狀態模式；避免遺留 MCP session 佔用記憶體 |
| `MCP_SESSION_LOG_TTL_SECONDS` | `3600` | 會話 ID 僅用於生命週期日誌的保留秒數 |
| `MCP_SESSION_LOG_MAX_ENTRIES` | `1000` | 會話 ID 日誌快取最大條數（防止記憶體無限增長） |
| `LOG_LEVEL` | `INFO` | 日誌（Logging）等級：DEBUG / INFO / WARNING / ERROR |
| `LOG_RETAIN_DAYS` | `7` | 日誌檔案保留天數 |

**API Key 優先順序：** `X-TickDB-Key` 請求標頭 → `TICKDB_API_KEY` 環境變數。

---

## 專案結構

```
tickdb-mcp/
├── main.py                  # 入口檔案（Python MCP Server）
├── pyproject.toml           # 套件設定與相依
├── Dockerfile               # Docker 容器化部署
├── .env.example             # 環境變數（Environment）範本
├── tickdb_mcp/              # 核心套件
│   ├── config.py            # 設定（Pydantic-settings）
│   ├── client.py            # TickDB REST API HTTP 客戶端 + API Key 解析
│   ├── middleware.py        # Bearer Token 驗證中介軟體（Middleware）+ Key 注入
│   ├── server.py            # FastMCP 實例工廠
│   └── tools/
│       ├── market.py        # Ticker、K-line、Order Book、Trades、Symbols
│       └── stock.py         # Stock Info、Intraday、Sessions、Metrics、Capital Flow
├── tests/                   # 單元測試（Unit Tests）
│   ├── test_client.py       # API Key 解析與錯誤處理
│   ├── test_server.py       # MCP 服務建立與工具註冊
│   ├── test_middleware.py   # 驗證與 Accept 標頭修復
│   └── test_tools.py        # 工具端點對應
├── examples/
│   ├── client_demo.py       # Python MCP 客戶端範例
│   └── server_demo.py       # 服務端 smoke test / 工具列表
└── (CI 設定位於上層倉庫 ../../.github/workflows/mcp-ci.yml)
```

---

## Docker 部署

```bash
# 建置 Docker 映像
docker build -t tickdb-mcp .

# 執行容器（使用者自帶 X-TickDB-Key 請求標頭）
docker run -d -p 8000:8000 tickdb-mcp

# 執行容器（指定伺服器統一 API Key）
docker run -d -p 8000:8000 \
  -e TICKDB_API_KEY=YOUR_KEY \
  -e MCP_ACCESS_TOKEN=YOUR_TOKEN \
  tickdb-mcp
```

---

## 開發（Development）

```bash
# 安裝開發相依套件
pip install -e ".[dev]"

# 程式碼檢查（Lint）
ruff check .

# 執行單元測試（Unit Tests）
pytest tests/ -v

# 執行範例
python examples/server_demo.py
```

---

## 文件

| 文件 | 說明 |
|---|---|
| [DEPLOYMENT.md](DEPLOYMENT.md) | 本地、Docker、Railway、Nginx 部署 |
| [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md) | AI 客戶端接入設定 |
| [../../CHANGELOG.md](../../CHANGELOG.md) | 版本更新記錄 |

---

## 貢獻指南

1. Fork 本倉庫
2. 建立功能分支：`git checkout -b feature/my-feature`
3. 遵循 [PEP 8](https://peps.python.org/pep-0008/)，由 `ruff` 強制檢查
4. 新功能需包含單元測試（Unit Tests）
5. 提交 PR 並附上清晰的說明

---

## 授權條款

MIT — 詳見 [LICENSE](../../LICENSE)。
