# TickDB MCP — AI 行情與公司基本面服務

[![CI](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-lightgrey.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)](../../LICENSE)

> 本目錄是 [tickdb-unified-realtime-marketdata-api](../../../) 倉庫的 MCP 服務端實作，目前版本 **v0.2.3**，可作為 Python 套件或 Docker 容器獨立部署。

**TickDB-MCP** 透過 [Model Context Protocol](https://modelcontextprotocol.io) 為 AI 助理提供 **43 個工具：13 個行情工具、29 個公司財務與基本面工具、1 個 API Key 訂閱查詢工具**。工具呼叫由 [TickDB REST API](https://tickdb.ai) 提供資料；本服務不提供 WebSocket 串流訂閱。

行情涵蓋 **外匯 · 貴金屬 · 指數 · 美股 · 港股 · A 股 · 中港期貨 · 加密貨幣**。公司財務與基本面涵蓋美股、港股和 A 股，具體可用性取決於品種、披露時間及 API Key 方案權限。

**連結：** [官網](https://tickdb.ai) · [API 文件](https://docs.tickdb.ai) · [聯絡我們](mailto:support@tickdb.ai)

**語言：** [简体中文](../../README.md) · **繁體中文** · [English](../en/README.md)

## 快速開始

首次安裝時，在 Linux 終端機中從本倉庫根目錄執行以下 Bash 命令。需要 Python 3.11+；升級時保留已有 `.env`，無需重新複製：

```bash
cd mcp
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cp .env.example .env
# 編輯 .env，填寫 TICKDB_API_KEY；也可由客戶端透過請求標頭提供 Key
python main.py
```

服務預設監聽連接埠 8000。支援 HTTP MCP 的客戶端可連接本地端點：

```json
{
  "mcpServers": {
    "tickdb": {
      "type": "http",
      "url": "http://localhost:8000/mcp",
      "headers": {
        "X-TickDB-Key": "YOUR_TICKDB_API_KEY"
      }
    }
  }
}
```

本地 HTTP 端點為 `http://localhost:8000/mcp`；公開託管請求標頭端點為 `https://mcp.tickdb.ai/`。已設定伺服器統一 Key 時，可省略範例中的 `X-TickDB-Key`。若設定 `MCP_ACCESS_TOKEN`，客戶端還須加入 `Authorization: Bearer <token>`。

Claude Desktop 本地模式使用 `MCP_TRANSPORT=stdio`、Python 命令及 `TICKDB_API_KEY` 環境變數，詳見 [客戶端接入指南](MCP_CLIENT_SETUP.md)。

<a id="oauth-setup"></a>
## 網頁 OAuth 接入與自部署

ChatGPT / Claude 網頁端使用 OAuth 連線。公開託管 URL 為 `https://mcp.tickdb.ai/oauth`；自部署使用 `https://你的網域/oauth`。使用者在授權頁面驗證自己的 TickDB API Key 並確認授權，無需自訂請求標頭。

OAuth **預設關閉**，啟用時使用單實例服務、持久化本地 SQLite 和公開 HTTPS。既有 `/mcp` 請求標頭接入與 stdio 模式仍可使用相同的 43 個工具。

### 設定與持久化

按快速開始安裝相依套件，並在私有 `.env` 中設定：

```dotenv
OAUTH_ENABLED=true
OAUTH_PUBLIC_URL=https://mcp.example.com
OAUTH_DATABASE_PATH=data/oauth.sqlite3
OAUTH_ENCRYPTION_KEY=REPLACE_WITH_THE_GENERATED_FERNET_KEY
OAUTH_REDIRECT_URIS=["https://chatgpt.com/connector_platform_oauth_redirect","https://claude.ai/api/mcp/auth_callback"]
```

首次安裝時產生一次 Fernet 金鑰，將結果填入 `OAUTH_ENCRYPTION_KEY`，單獨備份。執行以下命令：

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

`OAUTH_PUBLIC_URL` 必須是 HTTPS origin，不帶路徑、查詢或片段。回呼白名單按完整 URL 精確匹配，不支援萬用字元或任意 HTTP loopback 回呼。`.env.example` 預設只列出 ChatGPT 回呼，Claude 網頁接入需加入上述 Claude 回呼；客戶端顯示其他回呼時，按實際完整 URL 設定。

Python 部署使用可寫的本地資料庫路徑。Docker 部署將資料庫路徑改為 `/app/data/oauth.sqlite3`，並在 `mcp/` 中執行。執行以下命令：

```bash
docker build -t tickdb-mcp:0.2.3 .
docker volume create tickdb-mcp-data
docker run -d --name tickdb-mcp --restart unless-stopped -p 127.0.0.1:8000:8000 --env-file .env -v tickdb-mcp-data:/app/data tickdb-mcp:0.2.3
```

設定、資料庫與金鑰須保存在 Git 和映像之外。SQLite 網路共享不適合作為多實例儲存。

### HTTPS 反向代理

所有發現、註冊、授權、確認、Token 和撤銷路徑須原樣轉送，不能將所有請求重寫到 `/mcp`。例如設定 Nginx，並替換網域與憑證路徑：

```nginx
server {
    listen 443 ssl;
    server_name mcp.example.com;
    ssl_certificate /etc/letsencrypt/live/mcp.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mcp.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_read_timeout 300s;
    }
}
```

`GET /.well-known/oauth-authorization-server` 和 `GET /.well-known/oauth-protected-resource/oauth` 回傳發現資訊；未驗證的 `/oauth` MCP 請求回傳 401 並提示發現位址。OAuth resource 為 `https://mcp.example.com/oauth`，使用發現結果中的完整 issuer，包括結尾斜線。

### 客戶端授權

客戶端選擇 OAuth；如有動態客戶端註冊選項則啟用，否則使用自動發現。手動填寫的客戶端 ID/Secret 留空，TickDB API Key 不能填入這些欄位。在 TickDB 授權頁面輸入自己的 Key，驗證遮蔽標識與對應訂閱，再確認授權。頁面支援簡體、繁體和英文，自動匹配瀏覽器語言，也可手動切換。

授權頁面只展示本次提交 Key 的遮蔽標識及唯一匹配的訂閱。新 ChatGPT 連接的固定回呼為 `https://chatgpt.com/connector_platform_oauth_redirect`，伺服器為其提供 issuer 標識；Claude 網頁回呼為 `https://claude.ai/api/mcp/auth_callback`。客戶端設定範例見 [接入指南](MCP_CLIENT_SETUP.md)。

### 授權與升級

- 動態註冊使用 `POST /register`，支援 `none` 或 `client_secret_post` 客戶端驗證；所有客戶端均須使用 PKCE S256。
- 授權流程使用 `/authorize`、`/oauth/consent` 和 `/token`，scope 為 `tickdb:read`；`/revoke` 撤銷 Token，刷新 Token 重用會撤銷對應授權。
- `/oauth` 使用 `Authorization: Bearer <access_token>`，拒絕 `X-TickDB-Key` 覆蓋，不回退到伺服器統一 Key。API Key 綁定加密存入 SQLite，瀏覽器確認請求檢查 Cookie、Origin 和 CSRF。
- 一般升級時保留同一加密金鑰、資料庫路徑或資料磁碟區、公開 origin、回呼白名單及已有授權。一致性備份設定與資料庫，可使用 SQLite 備份介面，或停止服務後再複製資料庫；如存在 WAL 須包含尚未合併的資料。替換程式碼或映像時不要刪除、重新初始化資料庫或重新產生加密金鑰。保留舊映像以便還原。
- 加密金鑰或資料庫綁定的公開 resource 改變時，服務啟動驗證會失敗。首次公開部署後檢查發現、瀏覽器授權、工具發現與呼叫，以及客戶端重新連接。

## 43 個 MCP 工具

### 行情工具（13 個）

| 工具 | 功能 |
|---|---|
| `get_ticker` | 指定品種的即時行情快照 |
| `get_kline` | 歷史 OHLCV；股票支援 `adjust=none/forward/backward` |
| `get_kline_latest` | 目前未收盤 K 線；支援股票復權 |
| `get_ex_factors` | 美股、港股、A 股前復權／後復權因子 |
| `get_order_book` | 買賣盤深度 |
| `get_recent_trades` | 逐筆成交明細 |
| `get_available_symbols` | 查詢可交易品種，含中國與香港期貨 |
| `get_stock_info` | 股票基本資訊，如 EPS、BPS、股息率 |
| `get_intraday` | 當日分時資料 |
| `get_trading_sessions` | 單個或全部股票市場的交易時段 |
| `get_trade_days` | 股票市場交易日曆 |
| `get_market_metrics` | PE/PB、市值及資金流等指標 |
| `get_capital_flow` | 大中小單資金流向 |

買賣盤與逐筆成交支援美股、港股、A 股、中港期貨和加密貨幣。股票資訊、分時、交易時段、交易日曆、復權因子與股票指標的適用範圍為美股、港股和 A 股。

### 公司財務與基本面工具（29 個）

| 分類 | 工具 |
|---|---|
| 公司資料（2） | `get_company_profile`、`get_company_executives` |
| 財務報表（3） | `get_financials_latest`、`get_financials_annual`、`get_financials_ttm` |
| 業務分部（2） | `get_segments_latest`、`get_segments_history` |
| 估值與產業（6） | `get_valuation_latest`、`get_valuation_history`、`get_industry_peers`、`get_industry_distribution`、`get_industries_rank`、`get_industries_tree` |
| 股利、回購與資本行動（4） | `get_dividends`、`get_dividends_ttm`、`get_buyback`、`get_corporate_actions` |
| 股東與基金（4） | `get_shareholders_latest`、`get_shareholders_top`、`get_shareholder_detail`、`get_fund_holdings_latest` |
| 新聞與市場狀態（3） | `get_company_news`、`get_news_detail`、`get_market_status` |
| 事件日曆（5） | `get_report_calendar`、`get_dividend_calendar`、`get_split_calendar`、`get_ipo_calendar`、`get_other_calendar` |

財報工具涵蓋損益表、資產負債表及現金流量表；TTM 支援損益表或現金流量表。最新與歷史估值目前回傳 PE。其他事件日曆須傳入 `category`。

### API Key 訂閱工具（1 個）

`get_api_key_subscriptions()` 無查詢參數，呼叫 `GET /v1/apikeys/subscriptions`，查詢 Key 的方案、狀態、到期時間和剩餘秒數，無需 TickDB 網站登入。保留 API 回傳的帳戶級訂閱回應；OAuth 授權頁面僅展示本次提交 Key 的對應資訊。到期判斷使用回應中的伺服器時間，缺失或 null 值不能視為零。

## 品種代碼與呼叫約定

| 市場 | 範例 |
|---|---|
| 外匯 | `EURUSD`、`USDJPY` |
| 貴金屬 | `XAUUSD`、`XAGUSD` |
| 指數 | `SPX`、`NDX`、`VIX` |
| 美股 | `AAPL.US`、`TSLA.US` |
| 港股 | `700.HK`、`9988.HK` |
| A 股 | `600519.SH`、`000858.SZ` |
| 中港期貨 | 用 `get_available_symbols(type="futures")` 查詢，如 `BU2609`、`HSI8888` |
| 加密貨幣 | `BTCUSDT`、`ETHUSDT` |

- K 線週期為 `1m`、`3m`、`5m`、`15m`、`30m`、`1h`、`2h`、`4h`、`1d`、`1w`、`1M`；歷史最後一根 K 線可能仍在形成，復權歷史可能變化。
- 股票資訊最多 500 個代碼；行情快照、最新 K 線和分時最多 50 個代碼。逐筆成交查詢預設 100 筆、最多 1000 筆。
- 股利、基金持股與事件日曆使用頂層 `page.next_cursor` 翻頁，篩選條件須保持一致。日曆省略日期時，後續頁重用首次回應的日期範圍。
- `get_trading_sessions` 可省略 `market` 以查詢全部市場，交易時間按市場當地時區解讀。交易日曆單次跨度最多 31 天，開始日期須在最近一年內。
- 多數行情時間戳為毫秒，資金流向為秒，財務記錄按日期或 RFC3339 欄位解析。缺失值和 null 不等於零；日曆分頁重用首次回應的 `data.from` 與 `data.to`。
- 工具保留 API 回應封套、分頁與選用欄位，同時檢查 HTTP 狀態及業務 `code`。服務不自動重試；按錯誤提示調整參數、權限或等待。
- 錯誤資訊保留原始訊息、權限提示、非 null 資料及上游提供的 `Retry-After`，HTTP 200 中的業務失敗也會報錯。僅在 HTTP 401 且業務 `code` 完全等於 `Invalid or expired token` 時正規化為 `1001`，原始回應保留在 `TickDBAPIError.details`。
- 財務資料可用性受市場、披露時間及方案限制。全市場行情快照不在本 MCP 工具範圍內，按指定代碼使用 `get_ticker`。

<a id="api-migration"></a>

## 升級指引

升級前查看 [更新記錄](CHANGELOG.md)，確認功能與相容性變更；升級後重新整理 MCP 客戶端的工具列表與參數結構。目前呼叫方式以本頁工具說明和客戶端發現的參數結構為準。

自部署升級與資料備份步驟見 [部署指南](DEPLOYMENT.md)。啟用 OAuth 的服務須保留加密金鑰、資料庫及授權設定。

## 設定

從 `.env.example` 建立本地 `.env`，設定檔保持私有。依賴由 `pyproject.toml` 管理，包含 `mcp[cli]>=1.26.0,<2.0.0` 與 `cryptography>=46.0.0`。

| 變數 | 預設值 | 說明 |
|---|---|---|
| `TICKDB_API_KEY` | 空 | 伺服器統一 Key；請求標頭 Key 優先 |
| `MCP_ACCESS_TOKEN` | 空 | 標頭接入 `/mcp` 的靜態 Bearer 存取 Token；空時無此存取限制 |
| `MCP_TRANSPORT` | `streamable-http` | 可設為 `stdio` |
| `MCP_HOST` | `0.0.0.0` | HTTP 監聽位址 |
| `MCP_PORT` | `8000` | HTTP 監聽連接埠 |
| `MCP_STATELESS_HTTP` | `true` | 避免保留廢棄的 HTTP 工作階段 |
| `MCP_SESSION_LOG_TTL_SECONDS` | `3600` | 生命週期日誌工作階段 ID 保留秒數 |
| `MCP_SESSION_LOG_MAX_ENTRIES` | `1000` | 日誌工作階段 ID 最大快取筆數 |
| `LOG_LEVEL` | `INFO` | 日誌等級 |
| `LOG_RETAIN_DAYS` | `7` | 輪替日誌保留天數 |
| `LOG_DIR` | `logs` | 工作目錄下的可寫日誌目錄，也可使用絕對路徑 |
| `OAUTH_ENABLED` | `false` | 啟用獨立的 `/oauth` 介面 |
| `OAUTH_PUBLIC_URL` | 空 | 公開 HTTPS origin，不帶路徑 |
| `OAUTH_ENCRYPTION_KEY` | 空 | 持久保存的 Fernet 加密金鑰 |
| `OAUTH_DATABASE_PATH` | `data/oauth.sqlite3` | 持久化 SQLite 路徑 |
| `OAUTH_REDIRECT_URIS` | `[]` | 精確回呼白名單；範例設定含 ChatGPT 回呼 |

日誌寫入 stderr，確保 stdio 協定的 stdout 可用；目錄可寫時同時輸出每日輪替檔案，檔案日誌不可用時繼續使用 stderr。標頭接入的 Key 優先序為 `X-TickDB-Key` → `TICKDB_API_KEY`，stdio 使用環境 Key；OAuth 使用授權綁定的 Key。

也可用 `python -m pip install .` 一般安裝，隨後執行 `tickdb-mcp`。

## 專案結構

```text
mcp/
├── main.py
├── pyproject.toml
├── Dockerfile
├── .env.example
├── tickdb_mcp/
│   ├── config.py
│   ├── client.py
│   ├── logging.py
│   ├── middleware.py
│   ├── http.py
│   ├── oauth/
│   ├── server.py
│   └── tools/
│       ├── account.py
│       ├── fundamentals.py
│       ├── market.py
│       └── stock.py
├── tests/
├── examples/
└── docs/
```

CI 位於父倉庫的 [../../../.github/workflows/mcp-ci.yml](../../../.github/workflows/mcp-ci.yml)，執行程式碼檢查、單元測試及 Docker 建置。

## Docker 部署

從倉庫根目錄進入 `mcp/` 後直接建置。執行以下命令：

```bash
cd mcp
docker build -t tickdb-mcp:0.2.3 .
docker run -d --name tickdb-mcp -p 127.0.0.1:8000:8000 --env-file .env tickdb-mcp:0.2.3
```

建置直接使用本目錄原始碼與 Dockerfile。客戶端存取本機 `http://localhost:8000/mcp`；遠端存取及 OAuth 部署使用 HTTPS 反向代理。啟用 OAuth 時，按上方[自部署設定](#oauth-setup)掛載資料庫持久化磁碟區並保留同一加密金鑰。

## 開發

在 `mcp/` 且已啟用虛擬環境時執行。執行以下命令：

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest tests/ -v
python examples/server_demo.py
```

單元測試使用模擬 API 回應和暫存資料庫，無需真實 API Key，不呼叫真實行情介面。`server_demo.py` 展示工具註冊與模擬呼叫；實際客戶端查詢需要有效 Key。

## 文件

| 文件 | 連結 |
|---|---|
| 自部署指南 | [DEPLOYMENT.md](DEPLOYMENT.md) |
| 客戶端接入 | [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md) |
| 網頁 OAuth 與持久化設定 | [本頁 OAuth 設定](#oauth-setup) |
| 升級指引 | [本頁升級指引](#api-migration) |
| 更新記錄 | [CHANGELOG.md](CHANGELOG.md) |

## 授權條款

MIT — 詳見 [LICENSE](../../LICENSE)。
