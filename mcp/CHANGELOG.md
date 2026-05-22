# Changelog

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
  - `get_recent_trades` — latest executed trades
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
