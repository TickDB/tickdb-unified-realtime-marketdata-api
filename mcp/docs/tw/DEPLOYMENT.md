# TickDB MCP — 自部署指南

**其他語言：** [简体中文](../../DEPLOYMENT.md) · [English](../en/DEPLOYMENT.md)

此倉庫的 `mcp/` 是可獨立執行的開源 Python MCP 服務。v0.2.4 提供 43 個工具（13 行情 + 29 公司財務與事件 + 1 API Key 訂閱），支援外匯、貴金屬、指數、美股、港股、A 股、中港期貨與加密貨幣。

需要 Python 3.11+，或 Docker；以下說明以 Linux / Bash 為基準。行情查詢與 OAuth Key 驗證均需存取 `api.tickdb.ai`。HTTP 預設監聽 8000 埠；公網 OAuth 需要 HTTPS 域名。

## 本地 / VPS：首次安裝

下方指令從此倉庫根目錄開始執行。若已在 `mcp/` 內，省略 `cd mcp`。首次安裝複製範本；升級時保留原 `.env`。

```bash
cd mcp
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cp .env.example .env
```

### 設定 API Key 與服務

預設保持 `TICKDB_API_KEY` 和 `MCP_ACCESS_TOKEN` 為空，由客戶端透過 `X-TickDB-Key` 提供自己的 Key。HTTP 僅監聽本機；如需遠端接入，明確設定監聽位址或 HTTPS 反向代理，並為伺服器共用 Key 設定存取驗證。

```dotenv
TICKDB_API_KEY=
MCP_ACCESS_TOKEN=
MCP_TRANSPORT=streamable-http
MCP_HOST=127.0.0.1
MCP_PORT=8000
MCP_STATELESS_HTTP=true
MCP_SESSION_LOG_TTL_SECONDS=3600
MCP_SESSION_LOG_MAX_ENTRIES=1000
LOG_LEVEL=INFO
LOG_RETAIN_DAYS=7
LOG_DIR=logs
OAUTH_ENABLED=false
```

使用伺服器共用 Key 時，在私有 `.env` 中同時設定以下兩項，客戶端改用 `Authorization: Bearer YOUR_MCP_ACCESS_TOKEN`，可省略 `X-TickDB-Key`：

```dotenv
TICKDB_API_KEY=YOUR_TICKDB_API_KEY
MCP_ACCESS_TOKEN=YOUR_MCP_ACCESS_TOKEN
```

存取 Token 應使用隨機強值，與 TickDB API Key 不同。設定存取 Token 後，所有 `/mcp` 請求都須攜帶正確 Bearer，包括自帶 Key 的客戶端。設定伺服器 Key 卻未設定存取 Token 時，不帶自己 Key 的 HTTP 請求回傳 401，即使來自本機或反向代理也不例外。

### 啟動與驗證

在 `mcp/` 目錄且已按上節啟用虛擬環境時，使用 `python main.py` 啟動服務。重新開啟終端機時，先進入 `mcp/`，再執行 `source .venv/bin/activate`。本文後續 `python` 指令使用該虛擬環境解譯器。

HTTP 工具位址為 `http://localhost:8000/mcp`。保留服務執行，再開另一個終端機執行下方初始化命令；它僅驗證 MCP 協定，不會呼叫真實行情 API。

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

若設定了 `MCP_ACCESS_TOKEN`，加 `-H "Authorization: Bearer YOUR_MCP_ACCESS_TOKEN"`。回應含 `serverInfo.name` 為 `tickdb-market-data` 即表示初始化成功。日誌寫入 stderr，目錄可寫時也保存到 `LOG_DIR`；日誌目錄不可寫時繼續使用 stderr。

本地 stdio：在客戶端環境中設定 `MCP_TRANSPORT=stdio` 和 `TICKDB_API_KEY`，由客戶端啟動 Python。stdio 不啟動 HTTP 或載入 OAuth 資料庫；完整設定見 [接入指南](MCP_CLIENT_SETUP.md)。

## Docker：從公開原始碼建置

`-e MCP_HOST=0.0.0.0` 僅設定容器內部監聽位址，並覆蓋 `.env` 的本機預設值；宿主連接埠仍綁定 `127.0.0.1`。對外代理時仍須遵守共用 Key 的驗證規則。

在 `mcp/` 目錄建置。首次安裝先複製 `.env.example` 為 `.env` 並按上節設定；建置內容已排除 `.env`、虛擬環境、資料與日誌。執行以下命令：

```bash
docker build -t tickdb-mcp:0.2.4 .
docker volume create tickdb-mcp-data
docker run -d --restart unless-stopped -p 127.0.0.1:8000:8000 --env-file .env -e MCP_HOST=0.0.0.0 -v tickdb-mcp-data:/app/data --name tickdb-mcp tickdb-mcp:0.2.4
docker logs -f tickdb-mcp
```

`127.0.0.1` 綁定適合本機客戶端或同機反向代理。若需其他機器直接接入，按自己的網路與存取控制設定監聽位址。容器工作目錄為 `/app`，`data/oauth.sqlite3` 存入 `/app/data` 持久磁碟區。相依套件及原始碼在映像中，設定透過 `.env` 注入。修改 `--env-file` 內容後需重新建立容器；一般 `docker restart` 不會更新已注入的環境變數。

## 可選：啟用網頁版 OAuth

預設 `OAUTH_ENABLED=false`。GPT / Claude 網頁版使用獨立 `/oauth` 工具入口；`/mcp` Header 與 stdio 為獨立接入方式。OAuth 僅使用使用者授權綁定的 Key。

僅首次安裝、尚無資料庫與加密密鑰時產生一次 Fernet 密鑰（Python 已安裝專案相依套件）。執行以下命令：

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

將輸出固定保存到 `.env` 的 `OAUTH_ENCRYPTION_KEY`，並加入下方設定。範例域名與密鑰佔位值必須替換：

```dotenv
OAUTH_ENABLED=true
OAUTH_PUBLIC_URL=https://mcp.example.com
OAUTH_DATABASE_PATH=data/oauth.sqlite3
OAUTH_ENCRYPTION_KEY=REPLACE_WITH_THE_GENERATED_FERNET_KEY
OAUTH_REDIRECT_URIS=["https://chatgpt.com/connector_platform_oauth_redirect","https://claude.ai/api/mcp/auth_callback"]
```

- `OAUTH_PUBLIC_URL` 是 HTTPS origin，不含路徑、查詢參數或 fragment；目前不支援反向代理子路徑掛載。
- 回呼位址必須完整且精確匹配，不使用萬用字元。範本預設僅包含 ChatGPT；使用 Claude 時按上方設定加入其回呼並保留其他既有位址。
- 本地 SQLite 適合單實例持久磁碟。服務帳戶須能寫入資料庫目錄；容器必須保留同一 `/app/data` 磁碟區。新資料庫檔案權限為 0600，父目錄為 0700（平台支援時）。
- 加密密鑰、資料庫、公開 origin 和回呼設定須跨重新啟動和升級保留。分別安全備份密鑰與資料庫，不將它們提交到 Git 或放入映像。
- 不要多實例共用網路檔案系統上的 SQLite；多節點服務需要另行實作共用交易儲存。

重新啟動本地服務，或使用同一 `.env` 和資料磁碟區重新建立 Docker 容器。客戶端 URL 為 `https://mcp.example.com/oauth`，驗證選 OAuth，客戶端 ID/Secret 留空，透過授權頁驗證並確認自己的 Key。協定、發現及回呼細節見 [OAuth 設定指南](README.md#oauth-setup)。

## HTTPS / Nginx 反向代理

啟用 OAuth 不會自動保護 `/mcp`。公開代理整個服務時，`/mcp` 仍按獨立驗證規則執行；匿名 HTTP 請求不能使用伺服器共用 Key。

為自己的域名申請憑證後，將整個 origin 的路徑原樣轉送至應用，包括 `/mcp`、`/oauth`、授權中繼資料、註冊、授權頁、令牌和撤銷路徑：

```nginx
server {
    listen 443 ssl;
    server_name mcp.example.com;

    ssl_certificate     /etc/letsencrypt/live/mcp.example.com/fullchain.pem;
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

關閉代理緩衝並設定足夠的讀取逾時，以支援 SSE。不要將所有 OAuth 路徑改寫至 `/mcp`，也不要僅代理一個工具路徑。

## Linux 背景執行

可將下方內容保存為 `/etc/systemd/system/tickdb-mcp.service`。先建立一般服務帳戶 `tickdb`，替換安裝絕對路徑，並授予該帳戶讀取設定、寫入資料和日誌目錄的權限。應用從工作目錄讀取 `.env`：

```ini
[Unit]
Description=TickDB MCP Server
After=network.target

[Service]
User=tickdb
WorkingDirectory=/absolute/path/to/repository/mcp
ExecStart=/absolute/path/to/repository/mcp/.venv/bin/python /absolute/path/to/repository/mcp/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now tickdb-mcp
sudo systemctl status tickdb-mcp
```

## Railway / Render 等雲平台

可以使用公開原始碼的 `mcp/Dockerfile`，或將建置根目錄設為 `mcp/`。在平台環境變數中設定 Key、監聽埠及可選 OAuth 參數，並使用 HTTPS 域名。啟用 OAuth 時，先設定持久化磁碟並將 `OAUTH_DATABASE_PATH` 指向掛載目錄；無持久磁碟的暫時實例不適合保存 OAuth 授權。平台部署不會代替回呼允許清單和加密密鑰設定。

## 升級與持久化

升級既有 HTTP 部署時，若原來僅設定了 `TICKDB_API_KEY`，不帶請求 Key 的請求現在會回傳 401。請新增隨機強值 `MCP_ACCESS_TOKEN` 並為客戶端設定對應 Bearer，或改由客戶端透過 `X-TickDB-Key` 提供自己的 Key。既有 `.env` 不會被自動改寫，若仍含 `MCP_HOST=0.0.0.0`，新驗證規則仍會阻止匿名使用共用 Key；如僅需本機服務，請主動改為 `127.0.0.1`。

1. 備份原 `.env`、OAuth 加密密鑰與資料庫。備份 SQLite 時使用 SQLite backup API，或停止服務後備份，確保備份一致。
2. 替換原始碼並在原虛擬環境執行 `python -m pip install -e .`；Docker 則建置新映像，保留原設定和同一資料磁碟區，僅替換容器與映像。
3. 保留 `OAUTH_ENCRYPTION_KEY`、資料庫檔案與路徑、`OAUTH_PUBLIC_URL`、回呼允許清單、註冊客戶端和有效授權；不要重新產生密鑰、刪除資料庫或重設授權。
4. 重新啟動後檢查 MCP 初始化和客戶端工具發現。保留原映像與備份以便還原；一般升級無需使用者重新綁定 Key。

## 環境變數參考

| 變數 | 預設值 | 說明 |
|---|---|---|
| `TICKDB_API_KEY` | 空 | 伺服器統一 Key；HTTP 回退使用須通過 Bearer 驗證，請求標頭 Key 優先；OAuth 不使用 |
| `MCP_ACCESS_TOKEN` | 空 | `/mcp` 的固定 Bearer Token；空時僅允許使用請求自己的 Key，不能借用伺服器 Key |
| `MCP_TRANSPORT` | `streamable-http` | HTTP 或本地 stdio |
| `MCP_HOST` | `127.0.0.1` | 監聽位址 |
| `MCP_PORT` | `8000` | 監聽埠號 |
| `MCP_STATELESS_HTTP` | `true` | 無狀態 HTTP，避免累積遺留工作階段 |
| `MCP_SESSION_LOG_TTL_SECONDS` | `3600` | 工作階段 ID 日誌快取的保留秒數 |
| `MCP_SESSION_LOG_MAX_ENTRIES` | `1000` | 工作階段 ID 日誌快取數量上限 |
| `LOG_LEVEL` | `INFO` | stderr 與檔案日誌等級 |
| `LOG_RETAIN_DAYS` | `7` | 日誌檔案保留天數 |
| `LOG_DIR` | `logs` | 檔案日誌目錄，相對工作目錄或絕對路徑 |
| `OAUTH_ENABLED` | `false` | 是否啟用獨立 OAuth HTTP 入口 |
| `OAUTH_PUBLIC_URL` | 空 | OAuth HTTPS origin |
| `OAUTH_DATABASE_PATH` | `data/oauth.sqlite3` | 持久 SQLite 路徑 |
| `OAUTH_ENCRYPTION_KEY` | 空 | 首次產生並固定保存的 Fernet 密鑰 |
| `OAUTH_REDIRECT_URIS` | `[]` | 精確回呼 JSON 陣列；範本含 ChatGPT 回呼 |

## 常見問題

- HTTP 401：若設定了 `MCP_ACCESS_TOKEN`，提供正確 Bearer；若僅設定伺服器共用 Key，補充存取 Token，或改由客戶端透過 `X-TickDB-Key` 提供自己的 Key。
- `Address already in use`：調整 `.env` 中的 `MCP_PORT`，並同步客戶端 URL 或代理目標。
- `No TickDB API key provided` / `1001`：檢查客戶端 `X-TickDB-Key` 或伺服器 `TICKDB_API_KEY`。`1005` 表示 Key 已過期。
- OAuth 啟動失敗：檢查 HTTPS origin、Fernet 密鑰、回呼 JSON 和資料庫寫入權限；既有資料庫須使用對應密鑰和 origin。
- 重啟後授權遺失：檢查資料庫是否在同一持久磁碟區內、設定是否保留。
- Nginx 呼叫逾時：檢查代理路徑、`proxy_buffering off` 和 `proxy_read_timeout`。
