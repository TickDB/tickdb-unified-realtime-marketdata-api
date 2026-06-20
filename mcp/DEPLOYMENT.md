# TickDB MCP 服务端 — 部署说明（Deployment Guide）

**语言：** **简体中文** · [繁體中文](docs/tw/DEPLOYMENT.md) · [English](docs/en/DEPLOYMENT.md)

## 概述

**TickDB-MCP** 将 TickDB Unified Market Data API 封装为 MCP（Model Context Protocol）Python 服务端，供 AI 客户端（Claude Desktop、Claude Code、Cursor、Kiro 等）通过 REST API 调用实时行情数据。

**支持资产类别：** 外汇（Forex/FX） · 贵金属（Precious Metals） · 指数（Indices） · 美股（US Stocks / NASDAQ / NYSE） · 港股（HK Stocks） · A 股（A-shares / CN Stocks） · 加密货币（Cryptocurrency）

---

## 环境要求

| 项目 | 要求 |
|---|---|
| Python | 3.11+ |
| 操作系统 | Linux / macOS / Windows |
| 网络 | 能访问 `api.tickdb.ai` |
| 端口 | 默认 8000（可配置） |

---

## 方式一：直接运行（本地 / VPS）

### 1. 安装依赖

```bash
pip install -e .
```

### 2. 配置环境变量（Environment Configuration）

```bash
cp .env.example .env
# 按需编辑 .env
```

关键配置项：

```bash
# 服务器统一 TickDB API Key（可选，用户也可通过 X-TickDB-Key 请求头自带）
TICKDB_API_KEY=YOUR_KEY

# MCP 服务访问控制 Token（可选）
MCP_ACCESS_TOKEN=YOUR_TOKEN

# 服务监听配置
MCP_TRANSPORT=streamable-http
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_STATELESS_HTTP=true
MCP_SESSION_LOG_TTL_SECONDS=3600
MCP_SESSION_LOG_MAX_ENTRIES=1000
```

### 3. 启动 MCP 服务端（Python Server）

```bash
python main.py
```

启动成功日志（Logging）：

```
2026-05-20 10:00:00 [INFO] tickdb_mcp.main: TickDB MCP Server starting...
2026-05-20 10:00:00 [INFO] tickdb_mcp.main: Running in HTTP mode on 0.0.0.0:8000
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 4. 验证服务

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

响应中包含 `"serverInfo":{"name":"tickdb-market-data"}` 即表示服务正常运行。

### 5. 生产环境：systemd 服务

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

## 方式二：Docker 部署（Dockerized Deployment）

### 构建镜像

```bash
docker build -t tickdb-mcp .
```

### 运行容器

```bash
# 开放访问（用户自带 X-TickDB-Key 请求头）
docker run -d -p 8000:8000 --name tickdb-mcp tickdb-mcp

# 指定服务器统一 API Key 和访问控制 Token
docker run -d \
  -p 8000:8000 \
  -e TICKDB_API_KEY=YOUR_TICKDB_KEY \
  -e MCP_ACCESS_TOKEN=YOUR_ACCESS_TOKEN \
  --name tickdb-mcp \
  tickdb-mcp
```

### 查看日志（Logging）

```bash
docker logs -f tickdb-mcp
```

---

## 方式三：Railway 一键部署（推荐云端托管）

1. 将本项目推送到 GitHub 仓库
2. 登录 [railway.app](https://railway.app)，选择 **Deploy from GitHub repo**
3. 选择对应仓库，Railway 自动识别 Dockerfile
4. 在 **Variables** 面板设置环境变量：
   - `TICKDB_API_KEY`（可选）
   - `MCP_ACCESS_TOKEN`（可选）
   - `MCP_PORT=8000`
5. 部署完成后，在 **Settings → Networking** 生成公网域名

服务地址格式：`https://your-app.up.railway.app/mcp`

---

## 方式四：Render 部署

1. 登录 [render.com](https://render.com)，新建 **Web Service**
2. 连接 GitHub 仓库，Runtime 选择 **Docker**
3. 在 **Environment** 中添加环境变量
4. 点击 Deploy

---

## HTTPS / Nginx 反向代理

Railway 和 Render 已自动提供 HTTPS，无需额外配置。

自建 VPS 推荐用 Nginx 反代：

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
        proxy_buffering off;        # SSE 流式传输必须项
        proxy_read_timeout 300s;    # SSE 长连接必须项
    }
}
```

> `proxy_buffering off` 和 `proxy_read_timeout` 是 SSE 长连接的必要配置，缺少会导致工具调用超时。

---

## 环境变量完整参考（Environment Variables）

| 变量 | 默认值 | 说明 |
|---|---|---|
| `TICKDB_API_KEY` | _（空）_ | 服务器统一 TickDB API Key；空时要求用户通过 `X-TickDB-Key` 请求头自带 |
| `MCP_ACCESS_TOKEN` | _（空）_ | MCP 服务访问 Token；空时服务开放访问 |
| `MCP_TRANSPORT` | `streamable-http` | 传输模式；`stdio` 用于本地 Claude Desktop 直连 |
| `MCP_HOST` | `0.0.0.0` | 监听地址 |
| `MCP_PORT` | `8000` | 监听端口 |
| `MCP_STATELESS_HTTP` | `true` | Streamable HTTP 无状态模式；避免遗留 MCP session 占用内存 |
| `MCP_SESSION_LOG_TTL_SECONDS` | `3600` | 会话 ID 仅用于生命周期日志的保留秒数 |
| `MCP_SESSION_LOG_MAX_ENTRIES` | `1000` | 会话 ID 日志缓存最大条数（防止内存无限增长） |
| `LOG_LEVEL` | `INFO` | 日志（Logging）级别：DEBUG / INFO / WARNING / ERROR |
| `LOG_RETAIN_DAYS` | `7` | 日志文件保留天数 |

---

## 常见问题

**`Address already in use`（端口被占用）**
```bash
lsof -i :8000
MCP_PORT=8123 python main.py
```

**`TickDB error 1001: API key invalid`**
检查 `.env` 中的 `TICKDB_API_KEY`，或前往 [tickdb.ai](https://tickdb.ai) 重新获取。

**`TickDB error 2002: Symbol not found`**
使用 `get_available_symbols` 工具查询正确代码，常见格式：
- 美股（US Stocks）：`AAPL.US` · 港股（HK Stocks）：`700.HK` · A 股：`600519.SH` / `000858.SZ`
- 加密货币（Crypto）：`BTCUSDT` · 外汇（Forex）：`EURUSD` · 贵金属：`XAUUSD`

**Nginx 反代后工具调用无响应**
确认 Nginx 配置了 `proxy_buffering off` 和足够的 `proxy_read_timeout`，SSE 连接不能被提前断开。
