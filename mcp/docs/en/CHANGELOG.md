# Changelog

**Language:** [简体中文](../../CHANGELOG.md) · [繁體中文](../tw/CHANGELOG.md) · **English**

## v0.2.3 — 2026-10-15

Changes since v0.1.3.

### Added

- Expand to 43 tools: 13 market data tools, 29 company financials and fundamentals tools, and 1 API Key subscription tool.
- Add company profiles, executives, financial statements, revenue segments, valuation, industry data, dividends, buybacks, shareholder and fund holdings, news, corporate events, and classified financial calendars.
- Add stock adjustment factors, K-line `adjust`, dividend TTM, news detail, market status, and `get_api_key_subscriptions`; update CN/HK futures coverage.
- Add optional web OAuth with S256 PKCE, dynamic client registration, refresh-token rotation and revocation; consent pages support Simplified Chinese, Traditional Chinese, and English.
- OAuth queries use the TickDB API Key verified and explicitly authorized by the user; Key bindings are encrypted in persistent SQLite.
- Provide deployment and client setup guides in three languages, plus offline tests for tools and HTTP transport.

### Fixed and Improved

- Update REST endpoint and parameter mappings, batch limits, tick-by-tick trade limits, pagination, and timestamp handling.
- Preserve response envelopes, HTTP status, business errors, and `Retry-After`; detect business failures on HTTP 200 and support gzip responses.
- Improve OAuth CSRF protection, same-origin submissions, exact callback allowlisting, and issuer identification; consent pages show only the submitted Key's masked identity and subscription.
- Fix Python wheel packaging for the `tickdb-mcp` entry module and Docker builds from source, enabling standalone installation and self-hosting.
- Send logs to stderr to keep stdio JSON-RPC clean; configure the log directory through `LOG_DIR` and continue logging to stderr if file writes are unavailable.

### Upgrade Notes

- Refresh the client's tool list. Remove `get_kline_intervals`, `get_financial_fields`, and the old `get_financial_calendar`; use classified calendar tools instead.
- Remove financial `fields`, valuation-history `metric`, and order-book `limit` parameters; symbol-based fundamentals tools require `symbol`. See [upgrade guide](README.md#api-migration).
- OAuth is disabled by default; `/mcp` header access and stdio remain available. Enable OAuth with the `/oauth` tool endpoint, public HTTPS, and persistent storage; retain encryption keys, databases, and valid grants during upgrades. See [OAuth self-hosting](README.md#oauth-setup).
- Require MCP SDK `>=1.26.0,<2.0.0` and `cryptography>=46.0.0`.

## v0.1.3 - 2026-06-15

### Fixed

- Enabled stateless Streamable HTTP by default via `MCP_STATELESS_HTTP=true` to avoid retaining abandoned MCP sessions in memory.
- Bounded middleware session lifecycle logging with TTL and max-entry limits to prevent unbounded `_known_sessions` growth during reconnects.

### Added

- Added `MCP_SESSION_LOG_TTL_SECONDS` and `MCP_SESSION_LOG_MAX_ENTRIES` configuration for session lifecycle log retention.
- Added unit tests for bounded session lifecycle cache behavior.

---

## v0.1.2 — 2026-05-20

### Added

- **Structured logging** across the entire request lifecycle:
  - Startup: server config summary (transport, port, auth status, API key status)
  - Middleware: incoming request IP, method, path, key source, auth result
  - Client: outgoing API call path, params, key source, response status, elapsed time
  - Errors: timeout, network errors, API error codes with full context
- **Session lifecycle logging** — tracks `SESSION_INIT`, `SESSION_CREATED`, `SESSION_REUSE`,
  `SESSION_ATTACH`, `SESSION_NOT_FOUND` events with key + session ID correlation
- **Daily rotating log files** — `logs/tickdb_mcp.log` with automatic daily rotation,
  configurable retention via `LOG_RETAIN_DAYS` (default 7 days)
- **`LOG_LEVEL` environment variable** — control verbosity (DEBUG/INFO/WARNING/ERROR, default: INFO)
- **`LOG_RETAIN_DAYS` environment variable** — number of days to keep rotated log files
- **API key masking** in logs for security (shows first 4 + last 4 chars only)
- **Key-based log correlation** — all request/response/error logs include masked API key
  for tracing a user's full call chain in concurrent environments
- **Request timing** — millisecond-precision elapsed time on every TickDB API call
- **Explicit error categorization** — TIMEOUT, NETWORK_ERROR, and API error codes logged separately

### Fixed

- **Hermes MCP client compatibility** — auto-fix `Accept` header for clients that don't
  send both `application/json` and `text/event-stream`, resolving 406 Not Acceptable errors
  that prevented SSE session establishment

---

## v0.1.1 — 2026-05-14

### Added

- **`type` parameter** for symbol disambiguation across 9 tools:
  `get_ticker`, `get_kline`, `get_kline_latest`, `get_order_book`, `get_recent_trades`,
  `get_stock_info`, `get_intraday`, `get_market_metrics`, `get_capital_flow`
- Accepted values: `stock`, `crypto`, `forex`, `indices`, `futures`
- Required only when a symbol code exists in multiple product types (e.g. `000001` is both
  平安银行/Stock and 上证指数/indices in the CN market)
- Unique symbols (e.g. `AAPL.US`, `BTCUSDT`) continue to work without `type`

### Fixed

- Resolved `AMBIGUOUS_SYMBOL` errors for CN market codes shared between stocks and indices

---

## v0.1.0 — 2026-05-01

### Initial Release

- **13 MCP Tools** covering real-time and historical market data:
  - `get_ticker` — real-time price snapshots
  - `get_kline` / `get_kline_latest` / `get_kline_intervals` — K-line candlestick data
  - `get_order_book` — market depth (bid/ask levels)
  - `get_recent_trades` — latest tick-by-tick trades
  - `get_available_symbols` — discover 37,527+ tradable symbols
  - `get_stock_info` — fundamental stock information
  - `get_intraday` — minute-level intraday data
  - `get_trading_sessions` — market session schedules
  - `get_trade_days` — trading calendar
  - `get_market_metrics` — valuation and market metrics
  - `get_capital_flow` — capital flow analysis
- **Asset coverage:** Forex, precious metals, indices, US/HK/A-share stocks, crypto
- **Two-tier API key resolution:** per-request `X-TickDB-Key` header → `TICKDB_API_KEY` env var
- **Transport:** Streamable HTTP (remote) and stdio (local Claude Desktop)
- **Auth middleware:** optional Bearer token gating via `MCP_ACCESS_TOKEN`
- **Docker support:** production-ready Dockerfile
