# TickDB MCP — Market Data and Company Fundamentals for AI

[![CI](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-lightgrey.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)](../../LICENSE)

> This directory contains the MCP server implementation for [tickdb-unified-realtime-marketdata-api](../../../), version **v0.2.3**, deployable as a standalone Python package or Docker container.

**TickDB-MCP** connects AI assistants through the [Model Context Protocol](https://modelcontextprotocol.io) with **43 tools: 13 market data tools, 29 company financials and fundamentals tools, and 1 API Key subscription tool**. Calls use the [TickDB REST API](https://tickdb.ai); this service does not provide WebSocket streaming subscriptions.

Market data covers **forex · precious metals · indices · US stocks · HK stocks · A-shares · China/Hong Kong futures · crypto**. Financials and fundamentals cover US/HK/CN stocks; availability depends on the symbol, disclosure period, and API Key plan permissions.

**Links:** [Website](https://tickdb.ai) · [API Docs](https://docs.tickdb.ai) · [Contact Us](mailto:support@tickdb.ai)

**Language:** [简体中文](../../README.md) · [繁體中文](../tw/README.md) · **English**

## Quick Start

For a new installation, run the Bash commands in a Linux terminal from the repository root. Python 3.11+ is required. Preserve your existing `.env` during upgrades instead of copying it again.

```bash
cd mcp
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cp .env.example .env
# Edit .env and set TICKDB_API_KEY, or supply a Key in the client header
python main.py
```

The server listens on port 8000 by default. A client that supports HTTP MCP can connect to the local endpoint:

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

The local HTTP endpoint is `http://localhost:8000/mcp`; the public hosted header endpoint is `https://mcp.tickdb.ai/`. Omit `X-TickDB-Key` when the server supplies a shared Key. If `MCP_ACCESS_TOKEN` is set, also add `Authorization: Bearer <token>`.

Claude Desktop local mode uses `MCP_TRANSPORT=stdio`, a Python command, and the `TICKDB_API_KEY` environment variable. See the [client setup guide](MCP_CLIENT_SETUP.md).

<a id="oauth-setup"></a>

## Web OAuth Access and Self-hosting

ChatGPT / Claude web clients connect through OAuth. Use `https://mcp.tickdb.ai/oauth` for the public hosted service or `https://your-domain/oauth` for your deployment. Users verify their own TickDB API Key on the consent page and explicitly approve access; no custom header is required.

OAuth is **disabled by default**. Enable it on a single instance with public HTTPS and persistent local SQLite storage. Header-based `/mcp` access and stdio continue to provide the same 43 tools.

### Configuration and persistence

Install the dependencies as described in Quick Start and add these settings to your private `.env`:

```dotenv
OAUTH_ENABLED=true
OAUTH_PUBLIC_URL=https://mcp.example.com
OAUTH_DATABASE_PATH=data/oauth.sqlite3
OAUTH_ENCRYPTION_KEY=REPLACE_WITH_THE_GENERATED_FERNET_KEY
OAUTH_REDIRECT_URIS=["https://chatgpt.com/connector_platform_oauth_redirect","https://claude.ai/api/mcp/auth_callback"]
```

For a new installation, generate a Fernet key once, save it as `OAUTH_ENCRYPTION_KEY`, and back it up separately from the database. With the virtual environment activated, run:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

`OAUTH_PUBLIC_URL` must be an HTTPS origin without a path, query, or fragment. Redirect URIs must match their complete URLs exactly; wildcards and arbitrary HTTP loopback callbacks are unsupported. `.env.example` includes the ChatGPT callback only. Add the Claude callback when enabling Claude web access; if a client shows a different callback, add that exact URL.

The service must be able to write the local database directory. For Docker, use `/app/data/oauth.sqlite3` and retain the `/app/data` volume shown under [Docker Deployment](#docker-deployment). Keep configuration, encryption keys, and databases outside Git and images. Network-shared SQLite is not a supported multi-instance store.

### HTTPS reverse proxy and discovery

Obtain a certificate for your domain and forward all paths unchanged, including discovery, registration, authorization, consent, token, and revocation routes. This Nginx example terminates HTTPS and preserves SSE responses:

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

Do not rewrite OAuth routes to `/mcp` or mount the service under a subpath. `GET /.well-known/oauth-authorization-server` and `GET /.well-known/oauth-protected-resource/oauth` publish discovery metadata. An unauthenticated MCP request to `/oauth` returns 401 with discovery information. The resource is `https://mcp.example.com/oauth`; preserve the complete issuer returned by discovery, including its trailing slash.

### Client authorization

Choose OAuth and dynamic client registration when exposed by the client; otherwise use automatic discovery. Leave manually supplied client ID/secret fields empty. A TickDB API Key is not an OAuth client ID or secret.

On the consent page, enter your own API Key, verify its masked identity and matching subscription, then explicitly approve access. The page supports Simplified Chinese, Traditional Chinese, and English, with browser-language detection and manual switching. It shows only the submitted Key's masked identity and its uniquely matched subscription, rather than the full account Key list.

New ChatGPT connections use `https://chatgpt.com/connector_platform_oauth_redirect`, for which the server advertises issuer identification. Claude web uses `https://claude.ai/api/mcp/auth_callback`. Configure a different client callback using its exact URL and reconnect. See the [client setup guide](MCP_CLIENT_SETUP.md) for connection examples.

### Authorization behavior and upgrades

- Dynamic registration uses `POST /register`; supported client authentication is `none` or `client_secret_post`. All clients require PKCE S256.
- Authorization uses `/authorize`, `/oauth/consent`, and `/token`, with scope `tickdb:read`. `/revoke` revokes tokens; refresh-token reuse revokes the grant.
- `/oauth` uses `Authorization: Bearer <access_token>`. It rejects `X-TickDB-Key` overrides and never falls back to the server-wide TickDB Key. Key bindings and sensitive authorization data are encrypted in SQLite; consent requests check browser Cookie, Origin, and CSRF values.
- Before upgrades, back up the configuration and database consistently, including any outstanding WAL data, using SQLite's backup API or stopping the service before copying the database. Replace code or images while retaining the same encryption key, database path/volume, public origin, callback allowlist, and valid authorizations. Do not delete or reinitialize the database or regenerate the key during ordinary upgrades. Keep the previous image and backups for rollback.
- Changing the encryption key or database-bound public resource causes startup validation to fail. After deployment, check discovery, browser authorization, tool discovery/calls, and client reconnection.

## 43 MCP Tools

### Market Data Tools (13)

| Tool | Function |
|---|---|
| `get_ticker` | Real-time snapshot for specified symbols |
| `get_kline` | Historical OHLCV; stocks support `adjust=none/forward/backward` |
| `get_kline_latest` | Current unfinished candle, including stock adjustment |
| `get_ex_factors` | US/HK/CN stock adjustment factors |
| `get_order_book` | Bid/ask depth |
| `get_recent_trades` | Recent tick-by-tick trades |
| `get_available_symbols` | Discover tradable symbols, including China/Hong Kong futures |
| `get_stock_info` | Stock information such as EPS, BPS, and dividend yield |
| `get_intraday` | Intraday data |
| `get_trading_sessions` | Session schedules for one or all stock markets |
| `get_trade_days` | Stock-market trading calendar |
| `get_market_metrics` | PE/PB, market cap, capital flow, and related metrics |
| `get_capital_flow` | Large/medium/small order flow |

Order books and tick-by-tick trades support US/HK/CN stocks, China/Hong Kong futures, and crypto. Stock information, intraday data, sessions, calendars, adjustment factors, and stock metrics apply to US/HK/CN stocks.

### Company Financials and Fundamentals Tools (29)

| Category | Tools |
|---|---|
| Company information (2) | `get_company_profile`, `get_company_executives` |
| Financial statements (3) | `get_financials_latest`, `get_financials_annual`, `get_financials_ttm` |
| Business segments (2) | `get_segments_latest`, `get_segments_history` |
| Valuation and industries (6) | `get_valuation_latest`, `get_valuation_history`, `get_industry_peers`, `get_industry_distribution`, `get_industries_rank`, `get_industries_tree` |
| Dividends, buybacks, and corporate actions (4) | `get_dividends`, `get_dividends_ttm`, `get_buyback`, `get_corporate_actions` |
| Shareholders and funds (4) | `get_shareholders_latest`, `get_shareholders_top`, `get_shareholder_detail`, `get_fund_holdings_latest` |
| News and market status (3) | `get_company_news`, `get_news_detail`, `get_market_status` |
| Event calendars (5) | `get_report_calendar`, `get_dividend_calendar`, `get_split_calendar`, `get_ipo_calendar`, `get_other_calendar` |

Financial tools cover income statements, balance sheets, and cash-flow statements; TTM supports income or cash-flow statements. Current and historical valuation tools currently return PE. The other-events calendar requires `category`.

### API Key Subscription Tool (1)

`get_api_key_subscriptions()` takes no query parameters and calls `GET /v1/apikeys/subscriptions` to return plan, status, expiration, and remaining seconds without a TickDB website login. The tool retains the account-level subscription response; the OAuth consent page displays only information matching the submitted Key. Use server-provided times for expiration checks; missing or null values are not zero.

## Symbols and Query Conventions

| Market | Examples |
|---|---|
| Forex | `EURUSD`, `USDJPY` |
| Precious metals | `XAUUSD`, `XAGUSD` |
| Indices | `SPX`, `NDX`, `VIX` |
| US stocks | `AAPL.US`, `TSLA.US` |
| HK stocks | `700.HK`, `9988.HK` |
| A-shares | `600519.SH`, `000858.SZ` |
| China/Hong Kong futures | Discover with `get_available_symbols(type="futures")`, e.g. `BU2609`, `HSI8888` |
| Crypto | `BTCUSDT`, `ETHUSDT` |

- K-line intervals: `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `1d`, `1w`, `1M`. The last historical candle may still be forming, and adjusted history may change.
- Stock information accepts up to 500 symbols; ticker, latest K-line, and intraday accept 50. Tick-by-tick trade queries default to 100 with a maximum of 1000.
- Dividends, fund holdings, and event calendars paginate with top-level `page.next_cursor`; keep filters unchanged. If calendar dates are omitted, reuse the first response's `data.from` and `data.to` on subsequent pages.
- `get_trading_sessions` can omit `market` to retrieve all markets; trading times are market-local. Trading calendar requests span at most 31 days and start within the most recent year.
- Most market timestamps use milliseconds, capital flow uses seconds, and financial records use documented date/RFC3339 fields. Missing or null values are not zero.
- Tools preserve the API envelope, pagination, and optional fields, and check both HTTP status and business `code`. There are no automatic retries; follow error hints to adjust parameters, permissions, or wait.
- Errors retain original messages, permission hints, non-null data, and `Retry-After` when supplied, including business failures returned with HTTP 200. Only HTTP 401 responses whose business `code` is exactly `Invalid or expired token` are normalized to `1001`; the original response remains in `TickDBAPIError.details`.
- Financial availability depends on market, disclosure period, and plan. Full-market snapshots are outside this MCP tool scope; use `get_ticker` for specified symbols.

<a id="api-migration"></a>

## Upgrade Guide

Review the [changelog](CHANGELOG.md) for features and compatibility changes before upgrading, then refresh the MCP client's tool list and parameter schemas. Use the current tool descriptions on this page and the schemas discovered by your client.

See the [deployment guide](DEPLOYMENT.md) for self-hosted upgrades and backups. OAuth deployments must retain encryption keys, databases, and authorization configuration.

## Configuration

Copy `.env.example` to a private local `.env`. Dependencies are managed in `pyproject.toml`, including `mcp[cli]>=1.26.0,<2.0.0` and `cryptography>=46.0.0`.

| Variable | Default | Description |
|---|---|---|
| `TICKDB_API_KEY` | Empty | Server-wide Key; a request-header Key takes priority |
| `MCP_ACCESS_TOKEN` | Empty | Static Bearer access token for header-based `/mcp` access; empty disables this gate |
| `MCP_TRANSPORT` | `streamable-http` | Can be set to `stdio` |
| `MCP_HOST` | `0.0.0.0` | HTTP bind address |
| `MCP_PORT` | `8000` | HTTP listen port |
| `MCP_STATELESS_HTTP` | `true` | Avoid retaining abandoned HTTP sessions |
| `MCP_SESSION_LOG_TTL_SECONDS` | `3600` | Retention seconds for lifecycle-log session IDs |
| `MCP_SESSION_LOG_MAX_ENTRIES` | `1000` | Maximum cached lifecycle-log session IDs |
| `LOG_LEVEL` | `INFO` | Log level |
| `LOG_RETAIN_DAYS` | `7` | Rotated-log retention days |
| `LOG_DIR` | `logs` | Writable directory relative to the working directory, or an absolute path |
| `OAUTH_ENABLED` | `false` | Enable the separate `/oauth` endpoint |
| `OAUTH_PUBLIC_URL` | Empty | Public HTTPS origin without a path |
| `OAUTH_ENCRYPTION_KEY` | Empty | Persisted Fernet encryption key |
| `OAUTH_DATABASE_PATH` | `data/oauth.sqlite3` | Persistent SQLite path |
| `OAUTH_REDIRECT_URIS` | `[]` | Exact callback allowlist; the example configuration includes a ChatGPT callback |

Logging always uses stderr, leaving stdout available for the stdio protocol. A writable directory also enables daily rotating files; if file logging is unavailable, stderr logging continues. HTTP header Key priority is `X-TickDB-Key` → `TICKDB_API_KEY`; stdio uses the environment Key, and OAuth uses the authorized Key binding.

A regular installation with `python -m pip install .` also provides the `tickdb-mcp` command.

## Project Structure

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

CI lives in the parent repository at [../../../.github/workflows/mcp-ci.yml](../../../.github/workflows/mcp-ci.yml) and runs lint, unit tests, and a Docker build.

## Docker Deployment

From the repository root, enter `mcp/` and build directly. Run:

```bash
cd mcp
docker build -t tickdb-mcp:0.2.3 .
docker volume create tickdb-mcp-data
docker run -d --name tickdb-mcp --restart unless-stopped -p 127.0.0.1:8000:8000 --env-file .env -v tickdb-mcp-data:/app/data tickdb-mcp:0.2.3
```

The build uses this directory's source and Dockerfile; optional `RELEASE_VERSION` and `VCS_REF` build arguments set OCI image labels. Connect locally at `http://localhost:8000/mcp`; use an HTTPS reverse proxy for remote or OAuth access. The container works in `/app`, so `data/oauth.sqlite3` also resolves inside the persistent `/app/data` volume. Retain the same volume and encryption key for OAuth; see [OAuth configuration](#oauth-setup). Recreate the container after changing `.env`; `docker restart` does not update injected environment variables. See the [deployment guide](DEPLOYMENT.md) for background services and cloud hosting.

## Development

Run from `mcp/` with the virtual environment activated:

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest tests/ -v
python examples/server_demo.py
```

Unit tests use simulated API responses and temporary databases, require no real API Key, and do not call live market endpoints. `server_demo.py` demonstrates tool registration and a mock call; real client queries require a valid Key.

## Documentation

| Document | Link |
|---|---|
| Self-hosting guide | [DEPLOYMENT.md](DEPLOYMENT.md) |
| Client setup | [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md) |
| Web OAuth and persistent configuration | [OAuth configuration on this page](#oauth-setup) |
| Upgrade guide | [Upgrade guidance on this page](#api-migration) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |

## License

MIT — see [LICENSE](../../LICENSE).
