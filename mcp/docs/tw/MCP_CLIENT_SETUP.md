# TickDB MCP — 使用者接入設定指南

**其他語言：** [简体中文](../../MCP_CLIENT_SETUP.md) · [English](../en/MCP_CLIENT_SETUP.md)

v0.2.3 提供 43 個工具：13 個行情工具、29 個公司財務與事件工具、1 個 API Key 訂閱工具。支援外匯、貴金屬、指數、美股、港股、A 股、中國及香港期貨、加密貨幣。實際資料取決於市場、披露時間和方案權限。

## 選擇接入方式

| 方式 | 位址 | 驗證 |
|---|---|---|
| 自部署 HTTP | `http://localhost:8000/mcp` 或 `https://mcp.example.com/mcp` | `X-TickDB-Key`，或伺服器統一 Key |
| 自部署 OAuth | `https://mcp.example.com/oauth` | 網頁授權綁定自己的 TickDB API Key |
| 公開託管 HTTP | `https://mcp.tickdb.ai/` | `X-TickDB-Key` |
| 公開託管 OAuth | `https://mcp.tickdb.ai/oauth` | 網頁 OAuth 授權 |
| 本地 stdio | 本地 Python 程序 | `TICKDB_API_KEY` 環境變數 |

下方 HTTP 範例使用自部署位址，連接公開託管服務時可替換為 `https://mcp.tickdb.ai/`。部署步驟見 [部署指南](DEPLOYMENT.md)。

## API Key 與授權

先在 [tickdb.ai](https://tickdb.ai) 註冊並取得有效 API Key。HTTP `/mcp` 接入優先使用 `X-TickDB-Key` 請求標頭，未提供時使用伺服器 `TICKDB_API_KEY`；stdio 使用環境變數。OAuth `/oauth` 僅使用使用者確認授權後綁定的 Key，不接受 `X-TickDB-Key`，不退回伺服器統一 Key。

Header 接入不持久化保存使用者 Key；OAuth 接入會加密保存 Key 綁定，以便後續呼叫和更新授權。不要將 API Key 填入 OAuth 客戶端 ID/Secret 或聊天訊息。

## ChatGPT / Claude 網頁版

1. 新增自訂 MCP 伺服器或連接器，URL 填 `https://mcp.example.com/oauth`，或公開託管入口 `https://mcp.tickdb.ai/oauth`。
2. 選擇 OAuth，使用自動發現和動態客戶端註冊（DCR）；客戶端 ID/Secret 留空。DCR 是 OAuth 內部的註冊機制，無需尋找單獨的 DCR 驗證選項。
3. 在開啟的 TickDB 授權頁輸入自己的 API Key，驗證後核對遮罩識別及訂閱資訊，再確認授權。授權頁支援簡體、繁體和英文。
4. 返回客戶端後重新整理工具列表並呼叫工具，例如查詢 API Key 訂閱與到期時間。

自部署服務需啟用 OAuth、HTTPS 和精確的回呼允許清單：ChatGPT 新連接使用 `https://chatgpt.com/connector_platform_oauth_redirect`，Claude 網頁版使用 `https://claude.ai/api/mcp/auth_callback`。既有連接若顯示其他完整回呼位址，按實際位址設定。詳見 [OAuth 接入與自部署設定](README.md#oauth-setup)。

## 桌面與開發客戶端

### Claude Code

專案共享設定檔為 `.mcp.json`，也可使用 `claude mcp add` 管理。儲存後在 Claude Code 執行 `/mcp` 檢查連接。設定位置見 [官方 MCP 文件](https://code.claude.com/docs/en/mcp)。

```json
{
  "mcpServers": {
    "tickdb": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "headers": {
        "X-TickDB-Key": "YOUR_API_KEY"
      }
    }
  }
}
```

### Claude Desktop

遠端 OAuth 服務透過 Claude 的連接器介面新增，使用上方網頁授權流程。本地 `claude_desktop_config.json` 使用下方 stdio 設定，設定檔位置以客戶端設定為準。

### Cursor

設定檔為專案 `.cursor/mcp.json` 或全域 `~/.cursor/mcp.json`。儲存並重新連接伺服器，參見 [官方說明](https://cursor.com/docs/mcp)。

```json
{
  "mcpServers": {
    "tickdb": {
      "url": "https://mcp.example.com/mcp",
      "headers": {
        "X-TickDB-Key": "YOUR_API_KEY"
      }
    }
  }
}
```

### Kiro

在 Kiro 開啟工作區或使用者 MCP 設定（通常為 `.kiro/settings/mcp.json` 或 `~/.kiro/settings/mcp.json`），儲存後自動重新連接。版本差異以 [官方說明](https://kiro.dev/docs/mcp/configuration/) 為準。

```json
{
  "mcpServers": {
    "tickdb": {
      "url": "https://mcp.example.com/mcp",
      "headers": {
        "X-TickDB-Key": "YOUR_API_KEY"
      }
    }
  }
}
```

### Codex (OpenAI)

使用 `~/.codex/config.toml`，專案設定可放在受信任專案的 `.codex/config.toml`。檢查連接可執行 `codex mcp list`，格式見 [OpenAI 官方 MCP 文件](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)。

```toml
[mcp_servers.tickdb]
url = "https://mcp.example.com/mcp"
http_headers = { "X-TickDB-Key" = "YOUR_API_KEY" }
```

### Zed

在 **Settings → AI → MCP Servers** 新增遠端伺服器，或編輯設定檔的 `context_servers`。下方範例用於設定了 `MCP_ACCESS_TOKEN` 的自部署服務；無 Authorization 標頭時 Zed 可能嘗試 OAuth，應使用啟用 OAuth 的 `/oauth` 入口，或改用下方本地 stdio 設定。參見 [官方說明](https://zed.dev/docs/ai/mcp)。

```json
{
  "context_servers": {
    "tickdb": {
      "url": "https://mcp.example.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_ACCESS_TOKEN",
        "X-TickDB-Key": "YOUR_API_KEY"
      }
    }
  }
}
```

### Cherry Studio

進入 **設定 → MCP 伺服器 → 新增**，名稱填 `tickdb`，類型選擇 Streamable HTTP，URL 填 `https://mcp.example.com/mcp`，Header 填 `X-TickDB-Key: YOUR_API_KEY`。若服務設定了存取 Token，另加 `Authorization: Bearer YOUR_MCP_ACCESS_TOKEN`。

## 自部署存取 Token

若伺服器設定了 `MCP_ACCESS_TOKEN`，在上述 HTTP 客戶端的請求標頭中同時加入 `Authorization: Bearer YOUR_MCP_ACCESS_TOKEN`。本地 HTTP 將 URL 改為 `http://localhost:8000/mcp`；公網服務使用 HTTPS。OAuth 入口的 Authorization 使用 OAuth 令牌，與該固定存取 Token 獨立。

## 本地 stdio（Claude Desktop 等）

先在此倉庫的 `mcp/` 目錄建立虛擬環境並安裝相依套件（`python -m pip install -e .`）。客戶端以絕對路徑啟動 Python：

```json
{
  "mcpServers": {
    "tickdb": {
      "command": "/absolute/path/to/mcp/.venv/bin/python",
      "args": [
        "/absolute/path/to/mcp/main.py"
      ],
      "env": {
        "MCP_TRANSPORT": "stdio",
        "TICKDB_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

替換 Python 與 `main.py` 為實際絕對路徑；Python 使用專案虛擬環境的 `.venv/bin/python`。儲存後完全退出並重新啟動客戶端。stdio 不啟動 HTTP 或 OAuth 端點，不載入 OAuth 資料庫。Zed 使用相同伺服器物件，但外層鍵改為 `context_servers`。

## 標的代碼速查

| 市場 | 範例 |
|---|---|
| 加密貨幣 | `BTCUSDT`、`ETHUSDT` |
| 外匯 / 貴金屬 | `EURUSD`、`USDJPY`、`XAUUSD`、`XAGUSD` |
| 美股 | `AAPL.US`、`TSLA.US` |
| 港股 | `700.HK`、`9988.HK` |
| A 股 | `600519.SH`、`000858.SZ` |
| 指數 | `SPX`、`NDX`、`VIX` |
| 中國 / 香港期貨 | 使用 `get_available_symbols(type="futures", market="CN"/"HK")` 查詢當前代碼 |

代碼不確定時先呼叫 `get_available_symbols`。公司財務工具也接受無後綴代碼（例如 `AAPL`、`700`、`600519`）；發生歧義時補充 `type=stock`。

## 可用工具（43 個）

### 行情工具（13 個）

| 工具 | 功能 |
|---|---|
| `get_ticker` | 即時行情快照 |
| `get_kline` | 歷史 OHLCV K 線，支援股票復權 |
| `get_kline_latest` | 最新 K 線，可能仍未收盤 |
| `get_order_book` | 買賣盤深度 |
| `get_recent_trades` | 逐筆成交明細 |
| `get_available_symbols` | 標的查詢與分頁 |
| `get_ex_factors` | 股票前復權 / 後復權因子 |
| `get_stock_info` | 股票基本資訊 |
| `get_intraday` | 當日分時資料 |
| `get_trading_sessions` | 單個或全部股票市場的交易時段安排 |
| `get_trade_days` | 交易日曆 |
| `get_market_metrics` | 市值、估值與綜合指標 |
| `get_capital_flow` | 大中小單資金流向 |

### 公司財務與事件工具（29 個）

| 分類 | 工具 |
|---|---|
| 公司資料 | `get_company_profile`, `get_company_executives` |
| 財務報表 | `get_financials_latest`, `get_financials_annual`, `get_financials_ttm` |
| 業務分部 | `get_segments_latest`, `get_segments_history` |
| 估值與產業 | `get_valuation_latest`, `get_valuation_history`, `get_industry_peers`, `get_industry_distribution`, `get_industries_rank`, `get_industries_tree` |
| 資本行動 | `get_dividends`, `get_dividends_ttm`, `get_buyback`, `get_corporate_actions` |
| 股東與基金 | `get_shareholders_latest`, `get_shareholders_top`, `get_shareholder_detail`, `get_fund_holdings_latest` |
| 新聞與市場狀態 | `get_company_news`, `get_news_detail`, `get_market_status` |
| 分類日曆 | `get_report_calendar`, `get_dividend_calendar`, `get_split_calendar`, `get_ipo_calendar`, `get_other_calendar` |

### API Key 訂閱工具（1 個）

`get_api_key_subscriptions` 使用空參數 `{}` 查詢當前 Key 的方案、狀態、到期時間與剩餘秒數；不需要官網登入。

## 呼叫約定

- K 線支援週期為 `1m 3m 5m 15m 30m 1h 2h 4h 1d 1w 1M`，以工具參數說明為準。
- 股票歷史和最新 K 線支援 `adjust=none/forward/backward`；歷史最後一根 K 線可能仍在形成。
- 訂單簿與逐筆成交支援美股、港股、A 股、中港期貨及加密。
- `get_trading_sessions` 回傳交易時段安排；查詢現在是否開盤使用 `get_market_status`。
- 財報參數 `n` 表示期數；估值歷史使用 `from_date` / `to_date` 篩選日期。
- 財經日曆包括報告、分紅、拆股、IPO 和其他事件五類工具；其他事件日曆需傳 `category`。分紅、基金持倉及日曆按頂層 `page.next_cursor` 翻頁，保持篩選條件一致。

## 自然語言範例

- 查詢黃金 XAUUSD 的即時價格。
- 比較蘋果最近五年的營收和淨利。
- 查詢騰訊的前復權日 K 線。
- 查詢我的 API Key 訂閱狀態和到期時間。

## 常見問題

- `No TickDB API key provided`：Header 或 stdio 接入需補充 Key；OAuth 接入需完成網頁授權。
- `Symbol not found` / `AMBIGUOUS_SYMBOL`：查詢正確代碼，必要時補充 `type`；股票行情代碼使用市場後綴。
- `3001` 表示頻率限制，按 `Retry-After` 等待；`3002` 表示配額耗盡；`1005` 表示 Key 已過期。
- `40405` 表示當前條件下無業務資料，不能按數值零使用；`5005` / `5006` 可嘗試稍後查詢、更換週期或 `adjust=none`。
- 客戶端未載入工具：檢查 JSON / TOML 格式、絕對路徑與相依套件，重新連接或重啟客戶端。服務不會自動重試業務呼叫。
