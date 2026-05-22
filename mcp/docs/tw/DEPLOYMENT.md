# TickDB MCP 伺服器 — 部署說明

## 概述

本服務將 TickDB 即時行情 API 封裝為 MCP（Model Context Protocol）服務，供 AI 客戶端（Claude Desktop、Claude Code、Cursor 等）呼叫。

**支援資產類別：** 外匯 · 貴金屬 · 指數 · 美股 · 港股 · A 股 · 加密貨幣

**其他語言：** [简体中文](../../DEPLOYMENT.md) · [English](../en/DEPLOYMENT.md)

---

## 環境需求

| 項目 | 需求 |
|---|---|
| Python | 3.11+ |
| 作業系統 | Linux / macOS / Windows |
| 網路 | 能存取 `api.tickdb.ai` |
| 埠號 | 預設 8000（可設定） |

---

## 方式一：直接執行（本地 / VPS）

### 1. 安裝相依套件

```bash
pip install -e .
```

### 2. 設定環境變數

```bash
cp .env.example .env
# 依需求編輯 .env
```

關鍵設定項目：

```bash
# 伺服器統一 TickDB API Key（可選，使用者也可透過 X-TickDB-Key 請求標頭自帶）
TICKDB_API_KEY=YOUR_KEY

# MCP 服務存取控制 Token（可選）
MCP_ACCESS_TOKEN=YOUR_TOKEN

# 服務監聽設定
MCP_TRANSPORT=streamable-http
MCP_HOST=0.0.0.0
MCP_PORT=8000
```

### 3. 啟動服務

```bash
python main.py
```

啟動成功日誌：

```
2026-05-20 10:00:00 [INFO] tickdb_mcp.main: TickDB MCP Server starting...
2026-05-20 10:00:00 [INFO] tickdb_mcp.main: Running in HTTP mode on 0.0.0.0:8000
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 4. 驗證服務

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

回應中包含 `"serverInfo":{"name":"tickdb-market-data"}` 即表示服務正常運行。

### 5. 生產環境：systemd 服務

```ini
# /etc/systemd/system/tickdb-mcp.service
[Unit]
Description=TickDB MCP Server
After=network.target

[Service]
WorkingDirectory=/path/to/tickdb-mcp
EnvironmentFile=/path/to/tickdb-mcp/.env
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable tickdb-mcp
sudo systemctl start tickdb-mcp
sudo systemctl status tickdb-mcp
```

---

## 方式二：Docker 部署

### 建置映像

```bash
docker build -t tickdb-mcp .
```

### 執行容器

```bash
# 開放存取（使用者自帶 X-TickDB-Key 請求標頭）
docker run -d -p 8000:8000 --name tickdb-mcp tickdb-mcp

# 指定伺服器統一 Key 和存取控制 Token
docker run -d \
  -p 8000:8000 \
  -e TICKDB_API_KEY=YOUR_TICKDB_KEY \
  -e MCP_ACCESS_TOKEN=YOUR_ACCESS_TOKEN \
  --name tickdb-mcp \
  tickdb-mcp
```

### 查看日誌

```bash
docker logs -f tickdb-mcp
```

---

## 方式三：Railway 一鍵部署（推薦雲端託管）

1. 將本專案推送至 GitHub 倉庫
2. 登入 [railway.app](https://railway.app)，選擇 **Deploy from GitHub repo**
3. 選擇對應倉庫，Railway 自動識別 Dockerfile
4. 在 **Variables** 面板設定環境變數：
   - `TICKDB_API_KEY`（可選）
   - `MCP_ACCESS_TOKEN`（可選）
   - `MCP_PORT=8000`
5. 部署完成後，在 **Settings → Networking** 產生公網域名

服務位址格式：`https://your-app.up.railway.app/mcp`

---

## 方式四：Render 部署

1. 登入 [render.com](https://render.com)，新建 **Web Service**
2. 連接 GitHub 倉庫，Runtime 選擇 **Docker**
3. 在 **Environment** 中新增環境變數
4. 點擊 Deploy

---

## HTTPS / Nginx 反向代理

Railway 和 Render 已自動提供 HTTPS，無需額外設定。

自建 VPS 推薦使用 Nginx 反代：

```nginx
server {
    listen 443 ssl;
    server_name mcp.yourdomain.com;

    ssl_certificate     /etc/letsencrypt/live/mcp.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mcp.yourdomain.com/privkey.pem;

    location /mcp {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;        # SSE 串流傳輸必要項目
        proxy_read_timeout 300s;    # SSE 長連線必要項目
    }
}
```

> `proxy_buffering off` 和 `proxy_read_timeout` 是 SSE 長連線的必要設定，缺少會導致工具呼叫逾時。

---

## 環境變數完整參考

| 變數 | 預設值 | 說明 |
|---|---|---|
| `TICKDB_API_KEY` | _（空）_ | 伺服器統一 TickDB Key；空時要求使用者透過 `X-TickDB-Key` 請求標頭自帶 Key |
| `MCP_ACCESS_TOKEN` | _（空）_ | MCP 服務存取 Token；空時服務開放存取 |
| `MCP_TRANSPORT` | `streamable-http` | 傳輸模式；`stdio` 用於本地 Claude Desktop 直連 |
| `MCP_HOST` | `0.0.0.0` | 監聽位址 |
| `MCP_PORT` | `8000` | 監聽埠號 |
| `LOG_LEVEL` | `INFO` | 日誌等級：DEBUG / INFO / WARNING / ERROR |
| `LOG_RETAIN_DAYS` | `7` | 日誌檔案保留天數 |

---

## 常見問題

**`Address already in use`（埠號被佔用）**
```bash
# 查找佔用程序
lsof -i :8000
# 或改用其他埠號
MCP_PORT=8123 python main.py
```

**`TickDB error 1001: API key invalid`**
檢查 `.env` 中的 `TICKDB_API_KEY`，或前往 [tickdb.ai](https://tickdb.ai) 重新取得。

**`TickDB error 2002: Symbol not found`**
使用 `get_available_symbols` 工具查詢正確代碼，常見格式：
- 美股：`AAPL.US` · 港股：`700.HK` · A 股：`600519.SH` / `000858.SZ`
- 加密：`BTCUSDT` · 外匯：`EURUSD` · 貴金屬：`XAUUSD`

**Nginx 反代後工具呼叫無回應**
確認 Nginx 設定了 `proxy_buffering off` 和足夠的 `proxy_read_timeout`，SSE 連線不能被提前中斷。
