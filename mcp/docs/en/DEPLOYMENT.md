# TickDB MCP Server — Deployment Guide

**Language:** [简体中文](../../DEPLOYMENT.md) · [繁體中文](../tw/DEPLOYMENT.md) · **English**

## Overview

This service wraps the TickDB real-time market data API as an MCP (Model Context Protocol) server,
enabling AI clients (Claude Desktop, Claude Code, Cursor, etc.) to query live market data.

**Supported asset classes:** Forex · Precious metals · Indices · US stocks · HK stocks · A-shares · Crypto

---

## Requirements

| Item | Requirement |
|---|---|
| Python | 3.11+ |
| OS | Linux / macOS / Windows |
| Network | Access to `api.tickdb.ai` |
| Port | 8000 (configurable) |

---

## Option 1: Direct (Local / VPS)

### 1. Install dependencies

```bash
pip install -e .
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your settings
```

Key variables:

```bash
# Server-wide TickDB API key (optional — users can pass their own via X-TickDB-Key header)
TICKDB_API_KEY=your_key_here

# Protect the MCP endpoint with a Bearer token (optional)
MCP_ACCESS_TOKEN=your_access_token

# Server settings
MCP_TRANSPORT=streamable-http
MCP_HOST=0.0.0.0
MCP_PORT=8000
```

### 3. Start the server

```bash
python main.py
```

Expected output:

```
2026-05-20 10:00:00 [INFO] tickdb_mcp.main: TickDB MCP Server starting...
2026-05-20 10:00:00 [INFO] tickdb_mcp.main: Running in HTTP mode on 0.0.0.0:8000
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 4. Verify the server

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

A response containing `"serverInfo":{"name":"tickdb-market-data"}` confirms the server is running.

### 5. Production: systemd service

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

## Option 2: Docker

### Build

```bash
docker build -t tickdb-mcp .
```

### Run

```bash
# Open access (users provide their own X-TickDB-Key header)
docker run -d -p 8000:8000 --name tickdb-mcp tickdb-mcp

# With server-wide API key and access token
docker run -d \
  -p 8000:8000 \
  -e TICKDB_API_KEY=your_tickdb_key \
  -e MCP_ACCESS_TOKEN=your_access_token \
  --name tickdb-mcp \
  tickdb-mcp
```

### Logs

```bash
docker logs -f tickdb-mcp
```

---

## Option 3: Railway (Recommended for cloud hosting)

1. Push this repo to GitHub
2. Log in to [railway.app](https://railway.app) → **Deploy from GitHub repo**
3. Select the repository — Railway auto-detects the Dockerfile
4. Set environment variables in the **Variables** panel:
   - `TICKDB_API_KEY` (optional)
   - `MCP_ACCESS_TOKEN` (optional)
   - `MCP_PORT=8000`
5. After deploy, go to **Settings → Networking** to generate a public domain

Your server URL will be: `https://your-app.up.railway.app/mcp`

---

## Option 4: Render

1. Log in to [render.com](https://render.com) → **New Web Service**
2. Connect your GitHub repo, set Runtime to **Docker**
3. Add environment variables
4. Deploy

---

## HTTPS / Nginx Reverse Proxy

Railway and Render provide HTTPS automatically. For self-hosted VPS with Nginx:

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
        proxy_buffering off;        # Required for SSE streaming
        proxy_read_timeout 300s;    # Required for long-lived SSE connections
    }
}
```

> `proxy_buffering off` and `proxy_read_timeout` are required for SSE connections.
> Without them, tool calls will time out.

---

## Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `TICKDB_API_KEY` | _(empty)_ | Server-wide TickDB key; empty = require per-request `X-TickDB-Key` header |
| `MCP_ACCESS_TOKEN` | _(empty)_ | Bearer token to gate MCP access; empty = open server |
| `MCP_TRANSPORT` | `streamable-http` | `stdio` for local Claude Desktop direct mode |
| `MCP_HOST` | `0.0.0.0` | Bind address |
| `MCP_PORT` | `8000` | Listen port |
| `LOG_LEVEL` | `INFO` | Logging verbosity: DEBUG / INFO / WARNING / ERROR |
| `LOG_RETAIN_DAYS` | `7` | Days to retain rotated log files |

---

## Troubleshooting

**`Address already in use`**
```bash
lsof -i :8000
MCP_PORT=8123 python main.py
```

**`TickDB error 1001: API key invalid`**
Check `TICKDB_API_KEY` in your `.env`, or register at [tickdb.ai](https://tickdb.ai).

**`TickDB error 2002: Symbol not found`**
Use `get_available_symbols` to find the correct code. Common formats:
- US stocks: `AAPL.US` · HK stocks: `700.HK` · A-shares: `600519.SH` / `000858.SZ`
- Crypto: `BTCUSDT` · Forex: `EURUSD` · Metals: `XAUUSD`

**Tool calls hang behind Nginx**
Ensure `proxy_buffering off` and `proxy_read_timeout 300s` are set in your Nginx config.
