# TickDB MCP — 使用者接入設定指南

透過 MCP 協定，讓 AI 助理直接查詢即時行情資料，無需手動呼叫 API。

**其他語言：** [简体中文](../../MCP_CLIENT_SETUP.md) · [English](../en/MCP_CLIENT_SETUP.md)

---

## 托管端點 vs 自部署

| 方式 | 位址 | 適合場景 |
|---|---|---|
| **托管端點**（推薦） | `https://mcp.tickdb.ai/` | 無需伺服器，開箱即用 |
| **自部署** | 自訂位址 | 需要私有化、定製中介軟體 |

> 托管端點由 TickDB 官方維護，HTTPS + Header 鑑權，無需 Docker 或伺服器設定。

---

## API Key 說明

使用前需要有效的 TickDB API Key，前往 [tickdb.ai](https://tickdb.ai) 註冊取得。

Key 的提供方式（優先順序由高至低）：

| 方式 | 說明 |
|---|---|
| `X-TickDB-Key` 請求標頭 | 在 MCP 設定的 `headers` 中填寫，每次請求隨呼叫傳入 |
| `TICKDB_API_KEY` 環境變數 | 自部署時由伺服器營運方統一設定，使用者無需自帶 Key |

---

## 各客戶端設定

### Claude Code

設定檔：`.claude/settings.json`（專案級）或 `~/.claude/settings.json`（全域）

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

設定儲存後，在 Claude Code 中執行 `/mcp` 指令重新整理，看到 `tickdb` 出現在列表中即接入成功。

---

### Claude Desktop

設定檔路徑：

| 系統 | 路徑 |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

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

設定後**完全退出並重新啟動** Claude Desktop 才會生效。工具列出現錘子圖示即表示工具已載入。

---

### Cursor

設定檔：`~/.cursor/mcp.json`

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

---

### Kiro

設定檔：`~/.kiro/settings/mcp.json`

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

---

### Codex（OpenAI）

設定檔：`~/.codex/config.json`

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

---

### Zed

設定檔：`~/.config/zed/settings.json`

```json
{
  "context_servers": {
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

---

### Cherry Studio

進入 **設定 → MCP 伺服器 → 新增**，填寫：

| 欄位 | 值 |
|---|---|
| 名稱 | `tickdb` |
| 類型 | HTTP |
| URL | `https://mcp.tickdb.ai/` |
| Header | `X-TickDB-Key: YOUR_API_KEY` |

---

## 需要存取控制 Token 時（自部署）

如果連接的是自部署伺服器且營運方設定了 `MCP_ACCESS_TOKEN`，需要同時傳入 Authorization 標頭：

```json
{
  "mcpServers": {
    "tickdb": {
      "type": "http",
      "url": "https://your-mcp-server.com/mcp",
      "headers": {
        "Authorization": "Bearer 服務商提供的Token",
        "X-TickDB-Key": "YOUR_API_KEY"
      }
    }
  }
}
```

---

## 本地 stdio 模式（Claude Desktop 直連自部署）

無需 HTTP 服務，直接本地執行：

```json
{
  "mcpServers": {
    "tickdb": {
      "command": "python",
      "args": ["/path/to/tickdb-mcp/main.py"],
      "env": {
        "MCP_TRANSPORT": "stdio",
        "TICKDB_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

---

## 標的代碼格式速查

| 市場 | 格式 | 範例 |
|---|---|---|
| 加密貨幣 | `基礎貨幣 + 計價貨幣` | `BTCUSDT`、`ETHUSDT` |
| 外匯 | 6 字母貨幣對 | `EURUSD`、`USDJPY`、`GBPUSD` |
| 貴金屬 | `XAU/XAG + USD` | `XAUUSD`、`XAGUSD` |
| 美股 | `股票代碼.US` | `AAPL.US`、`TSLA.US`、`NVDA.US` |
| 港股 | `數字代碼.HK` | `700.HK`、`9988.HK` |
| 滬市 A 股 | `6位代碼.SH` | `600519.SH`、`601318.SH` |
| 深市 A 股 | `6位代碼.SZ` | `000858.SZ`、`000333.SZ` |
| 指數 | 指數代碼 | `SPX`、`NDX`、`VIX`、`DXY` |

不確定代碼？直接問 AI：*「幫我查一下比亞迪的股票代碼」*，會自動呼叫 `get_available_symbols` 查詢。

---

## 可用工具（13 個）

| 工具 | 功能 | 支援市場 |
|---|---|---|
| `get_ticker` | 即時行情快照（價格、漲跌幅、成交量） | 全部 |
| `get_kline` | 歷史 K 線資料（OHLCV） | 全部 |
| `get_kline_latest` | 最新即時 K 線（當前未收盤） | 全部 |
| `get_order_book` | 買賣盤深度 | 美股、港股、加密 |
| `get_recent_trades` | 最近成交明細 | 港股、加密 |
| `get_available_symbols` | 查詢可交易標的（37,527+） | 全部 |
| `get_kline_intervals` | 支援的 K 線週期列表 | 全部 |
| `get_stock_info` | 股票基本資訊（EPS、BPS、股息率等） | 美股、港股、A 股 |
| `get_intraday` | 當日分時資料 | 美股、港股、A 股 |
| `get_trading_sessions` | 當前交易時段 | 美股、港股、A 股 |
| `get_trade_days` | 交易日曆查詢 | 美股、港股、A 股 |
| `get_market_metrics` | 市值、PE/PB、資金流等綜合指標 | 美股、港股、A 股 |
| `get_capital_flow` | 大中小單資金流向分析 | 美股、港股、A 股 |

---

## 使用範例

```
你：黃金現在什麼價格？
AI：（呼叫 get_ticker，回傳 XAUUSD 即時價格）

你：幫我看看比特幣最近 7 天的日線走勢
AI：（呼叫 get_kline，取得 BTCUSDT 1d 資料）

你：騰訊股票的本益比是多少？
AI：（呼叫 get_market_metrics，回傳 700.HK 的 PE TTM）

你：美股今天開盤了嗎？
AI：（呼叫 get_trading_sessions，回傳 US 市場當前時段）

你：幫我看看貴州茅台的資金流向
AI：（呼叫 get_capital_flow，回傳 600519.SH 大中小單流向）
```

---

## 常見問題

**提示「No TickDB API key provided」**
在 MCP 設定的 `headers` 中新增 `X-TickDB-Key`，或前往 [tickdb.ai](https://tickdb.ai) 註冊取得 Key。

**提示「Symbol not found」**
檢查標的代碼格式，美股需要加 `.US` 後綴（如 `AAPL.US`），港股加 `.HK`，A 股加 `.SH` 或 `.SZ`。

**提示「Quota exhausted」或「Rate limit exceeded」**
當前 Key 的配額已用完或超過頻率限制。前往 [tickdb.ai](https://tickdb.ai) 查看方案詳情或升級計畫。

**Claude Desktop 設定後沒有看到工具**
確認 JSON 格式正確（無多餘逗號），並**完全退出**後重新啟動 Claude Desktop。

**我的 Key 會暴露給伺服器嗎？**
`X-TickDB-Key` 僅用於轉發給 TickDB API 驗證，伺服器不做持久化儲存。
