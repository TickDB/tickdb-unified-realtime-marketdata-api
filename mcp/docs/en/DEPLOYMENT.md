# TickDB MCP — Self-hosting Guide

**Other languages:** [简体中文](../../DEPLOYMENT.md) · [繁體中文](../tw/DEPLOYMENT.md)

This repository's `mcp/` directory is a standalone open-source Python MCP server. v0.2.3 exposes 43 tools (13 market + 29 company fundamentals/events + 1 API key subscription), covering forex, metals, indices, US/HK/CN stocks, CN/HK futures, and crypto.

Requires Python 3.11+ or Docker on Linux. All commands below use Bash. Market queries and OAuth key validation both require access to `api.tickdb.ai`. HTTP listens on port 8000 by default. Public OAuth requires an HTTPS domain.

## Local / VPS: first installation

Start these commands from the repository root. Omit `cd mcp` if already in that directory. Copy the template only on first installation; retain your existing `.env` during upgrades.

```bash
cd mcp
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cp .env.example .env
```

### Configure keys and the service

Edit `.env` as needed. The `X-TickDB-Key` request header takes priority; `TICKDB_API_KEY` is a server fallback. Without a server key, clients must supply their own. Set `MCP_ACCESS_TOKEN` to protect public header access and have clients send `Authorization: Bearer <token>`.

```dotenv
TICKDB_API_KEY=
MCP_ACCESS_TOKEN=
MCP_TRANSPORT=streamable-http
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_STATELESS_HTTP=true
MCP_SESSION_LOG_TTL_SECONDS=3600
MCP_SESSION_LOG_MAX_ENTRIES=1000
LOG_LEVEL=INFO
LOG_RETAIN_DAYS=7
LOG_DIR=logs
OAUTH_ENABLED=false
```

### Start and verify

From `mcp/`, with the virtual environment activated as above, run `python main.py`. In a new terminal, first enter `mcp/` and run `source .venv/bin/activate`. The HTTP tool endpoint is `http://localhost:8000/mcp`. In another terminal, run the initialization command below to check the MCP protocol without calling the market data API.

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

If `MCP_ACCESS_TOKEN` is configured, add `-H "Authorization: Bearer YOUR_MCP_ACCESS_TOKEN"` before `-d`. A response with `serverInfo.name` set to `tickdb-market-data` confirms initialization. Logs go to stderr and, when writable, `LOG_DIR`; an unwritable log directory falls back to stderr.

For local stdio, set `MCP_TRANSPORT=stdio` and `TICKDB_API_KEY` in the client process environment and let the client launch Python. Stdio does not start HTTP or load the OAuth database. See the [client setup guide](MCP_CLIENT_SETUP.md).

## Docker: build from public source

Build from `mcp/`. On first installation, copy `.env.example` to `.env` and configure it as above. The build context excludes `.env`, virtual environments, data, and logs. Run:

```bash
docker build -t tickdb-mcp:0.2.3 .
docker volume create tickdb-mcp-data
docker run -d --restart unless-stopped -p 127.0.0.1:8000:8000 --env-file .env -v tickdb-mcp-data:/app/data --name tickdb-mcp tickdb-mcp:0.2.3
docker logs -f tickdb-mcp
```

Binding `127.0.0.1` suits local clients or a reverse proxy on the same host. Configure another bind address according to your network and access controls for direct connections from other machines. The container works in `/app`, so `data/oauth.sqlite3` lives in the persistent `/app/data` volume. Code and dependencies are in the image; `.env` supplies runtime configuration. Recreate the container after changing `--env-file` contents; `docker restart` does not update injected environment variables.

## Optional: enable web OAuth

`OAUTH_ENABLED=false` by default. GPT / Claude web use a separate `/oauth` tool endpoint. Header-based `/mcp` access and stdio are separate connection options. OAuth uses only the key bound by the authorizing user.

Generate a Fernet key once, only on first installation with no existing database/key, using Python with the project dependencies installed and the virtual environment activated. Run:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Save the output as a stable `OAUTH_ENCRYPTION_KEY` in `.env` and add the following settings. Replace the example domain and key placeholder:

```dotenv
OAUTH_ENABLED=true
OAUTH_PUBLIC_URL=https://mcp.example.com
OAUTH_DATABASE_PATH=data/oauth.sqlite3
OAUTH_ENCRYPTION_KEY=REPLACE_WITH_THE_GENERATED_FERNET_KEY
OAUTH_REDIRECT_URIS=["https://chatgpt.com/connector_platform_oauth_redirect","https://claude.ai/api/mcp/auth_callback"]
```

- `OAUTH_PUBLIC_URL` must be an HTTPS origin without a path, query, or fragment. Reverse-proxy subpath mounting is not supported.
- Redirect URIs must match completely and exactly, without wildcards. The template includes ChatGPT only; add the Claude callback as above while preserving existing callbacks.
- Local SQLite is intended for one instance with persistent disk. The service account must be able to write the database directory; containers must retain the same `/app/data` volume. New database files use mode 0600 and parent directories 0700 where supported.
- Retain the encryption key, database, public origin, and callback configuration across restarts/upgrades. Back up the key and database securely and separately; never commit them or bake them into images.
- Do not share SQLite over a network filesystem across instances. Multiple nodes require a separate shared transactional storage implementation.

Restart the local process, or recreate Docker with the same `.env` and data volume. Connect clients to `https://mcp.example.com/oauth`, select OAuth, leave client ID/secret blank, and validate/authorize your own key on the consent page. See the [OAuth configuration](README.md#oauth-setup) for protocol, discovery, and callback details.

## HTTPS / Nginx reverse proxy

Obtain a certificate for your domain and proxy the entire origin without rewriting paths, including `/mcp`, `/oauth`, authorization metadata, registration, consent, token, and revocation routes:

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

Disable buffering and allow sufficient read time for SSE. Do not rewrite OAuth routes to `/mcp` or proxy only one tool endpoint.

## Linux background service

Save this example to `/etc/systemd/system/tickdb-mcp.service`. Create an unprivileged `tickdb` service account first, replace the absolute installation paths, and grant it read access to configuration and write access to data/log directories. The application reads `.env` from its working directory:

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

## Railway / Render and other cloud hosts

Use the public source's `mcp/Dockerfile`, or select `mcp/` as the build root. Configure keys, the listening port, and optional OAuth settings in the platform environment, and use HTTPS. For OAuth, attach persistent storage first and point `OAUTH_DATABASE_PATH` at its mount. Ephemeral instances without persistent disk cannot preserve authorizations. Platform deployment does not configure redirect allowlists or encryption keys for you.

## Upgrades and persistence

1. Back up the existing `.env`, OAuth encryption key, and database. Use SQLite's backup API or stop the service before copying the database to obtain a consistent backup.
2. Replace source and run `python -m pip install -e .` in the existing virtual environment. For Docker, build a new image and replace the container/image while keeping the same configuration and data volume.
3. Retain `OAUTH_ENCRYPTION_KEY`, database file/path, `OAUTH_PUBLIC_URL`, redirect allowlist, registered clients, and valid authorizations. Do not regenerate keys, delete the database, or reset authorization.
4. Restart and check MCP initialization and client tool discovery. Retain the previous image and backups for rollback; ordinary upgrades do not require users to rebind keys.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `TICKDB_API_KEY` | empty | Fallback server key; unused by OAuth |
| `MCP_ACCESS_TOKEN` | empty | Fixed bearer token for header-based `/mcp` access only |
| `MCP_TRANSPORT` | `streamable-http` | HTTP or local stdio |
| `MCP_HOST` | `0.0.0.0` | Bind address |
| `MCP_PORT` | `8000` | Listen port |
| `MCP_STATELESS_HTTP` | `true` | Stateless HTTP avoids retaining abandoned sessions |
| `MCP_SESSION_LOG_TTL_SECONDS` | `3600` | Session-label log cache TTL, in seconds |
| `MCP_SESSION_LOG_MAX_ENTRIES` | `1000` | Maximum session labels cached for logs |
| `LOG_LEVEL` | `INFO` | stderr and file log level |
| `LOG_RETAIN_DAYS` | `7` | Days to retain file logs |
| `LOG_DIR` | `logs` | File log directory, relative to working directory or absolute |
| `OAUTH_ENABLED` | `false` | Enable the separate OAuth HTTP entry point |
| `OAUTH_PUBLIC_URL` | empty | OAuth HTTPS origin |
| `OAUTH_DATABASE_PATH` | `data/oauth.sqlite3` | Persistent SQLite path |
| `OAUTH_ENCRYPTION_KEY` | empty | Fernet key generated once and kept stable |
| `OAUTH_REDIRECT_URIS` | `[]` | Exact redirect URI JSON array; template includes ChatGPT |

## Troubleshooting

- `Address already in use`: change `MCP_PORT` in `.env` and update client URLs or the proxy target.
- `No TickDB API key provided` / `1001`: check the client `X-TickDB-Key` or server `TICKDB_API_KEY`. `1005` means the key expired.
- OAuth startup failure: verify HTTPS origin, Fernet key, redirect JSON, and database permissions. Existing databases require their original key and origin.
- Authorization lost after restart: check that the same persistent volume and configuration are retained.
- Nginx timeouts: check proxy routes, `proxy_buffering off`, and `proxy_read_timeout`.
