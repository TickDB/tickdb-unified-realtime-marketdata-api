# TickDB MCP — Client Setup Guide

**Other languages:** [简体中文](../../MCP_CLIENT_SETUP.md) · [繁體中文](../tw/MCP_CLIENT_SETUP.md)

v0.2.3 exposes 43 tools: 13 market tools, 29 company fundamentals and event tools, and 1 API key subscription tool. Supported assets include forex, precious metals, indices, US/HK/CN stocks, Chinese and Hong Kong futures, and crypto. Availability depends on the market, disclosure dates, and your subscription.

## Choose a connection

| Mode | Endpoint | Authentication |
|---|---|---|
| Self-hosted HTTP | `http://localhost:8000/mcp` or `https://mcp.example.com/mcp` | `X-TickDB-Key` or a server-wide key |
| Self-hosted OAuth | `https://mcp.example.com/oauth` | Authorize and bind your own TickDB API key |
| Public hosted HTTP | `https://mcp.tickdb.ai/` | `X-TickDB-Key` |
| Public hosted OAuth | `https://mcp.tickdb.ai/oauth` | Browser OAuth authorization |
| Local stdio | A local Python process | `TICKDB_API_KEY` environment variable |

The HTTP examples below use a self-hosted URL. Replace it with `https://mcp.tickdb.ai/` to use the public hosted service. See the [deployment guide](DEPLOYMENT.md) to host your own server.

## API keys and authorization

Register at [tickdb.ai](https://tickdb.ai) for a valid API key. HTTP `/mcp` uses the per-request `X-TickDB-Key` first, then server `TICKDB_API_KEY` when no header is provided. Stdio uses the environment key. OAuth `/oauth` uses only the key explicitly bound during authorization; it does not accept `X-TickDB-Key` or fall back to the server key.

Header connections do not persist users' keys. OAuth encrypts and persists key bindings for subsequent calls and authorization refresh. Do not put your API key in OAuth client ID/secret fields or chat messages.

## ChatGPT / Claude web

1. Add a custom MCP server or connector with `https://mcp.example.com/oauth`, or use the public endpoint `https://mcp.tickdb.ai/oauth`.
2. Select OAuth and automatic discovery with dynamic client registration (DCR). Leave client ID/secret blank. DCR is a registration mechanism within OAuth, not a separate authentication option.
3. Enter your API key on the TickDB authorization page, validate it, review its masked identifier and subscription information, then confirm authorization. The page supports Simplified Chinese, Traditional Chinese, and English.
4. Return to your client and refresh its tool list. Try querying your API key subscription and expiration.

Self-hosted servers must enable OAuth, HTTPS, and an exact redirect allowlist: new ChatGPT connections use `https://chatgpt.com/connector_platform_oauth_redirect`; Claude web uses `https://claude.ai/api/mcp/auth_callback`. If an existing connection shows a different complete callback URL, configure that exact URL. See the [OAuth configuration](README.md#oauth-setup).

## Desktop and developer clients

### Claude Code

Use project `.mcp.json`, or manage the server with `claude mcp add`. Save and run `/mcp` in Claude Code to check the connection. See [official MCP documentation](https://code.claude.com/docs/en/mcp).

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

Add remote OAuth servers through Claude's connector UI using the web authorization flow above. Use the stdio example below in local `claude_desktop_config.json`. Use the configuration file location specified by your client.

### Cursor

Use project `.cursor/mcp.json` or global `~/.cursor/mcp.json`. Save and reconnect the server; see [official documentation](https://cursor.com/docs/mcp).

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

Open Kiro's workspace or user MCP configuration, commonly `.kiro/settings/mcp.json` or `~/.kiro/settings/mcp.json`. Saving reconnects the server. Check [official documentation](https://kiro.dev/docs/mcp/configuration/) for version-specific locations.

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

Use `~/.codex/config.toml`, or `.codex/config.toml` in a trusted project. Run `codex mcp list` to inspect connections. See [official OpenAI MCP documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

```toml
[mcp_servers.tickdb]
url = "https://mcp.example.com/mcp"
http_headers = { "X-TickDB-Key" = "YOUR_API_KEY" }
```

### Zed

Add a remote server in **Settings → AI → MCP Servers**, or edit `context_servers` in the settings file. This example targets a self-hosted server with `MCP_ACCESS_TOKEN` configured. Without an Authorization header, Zed may attempt OAuth: use an enabled `/oauth` endpoint or the local stdio example below. See [official documentation](https://zed.dev/docs/ai/mcp).

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

Open **Settings → MCP Servers → Add**. Set name to `tickdb`, type to Streamable HTTP, URL to `https://mcp.example.com/mcp`, and header to `X-TickDB-Key: YOUR_API_KEY`. If your server requires an access token, also add `Authorization: Bearer YOUR_MCP_ACCESS_TOKEN`.

## Self-hosted access tokens

When the server sets `MCP_ACCESS_TOKEN`, add `Authorization: Bearer YOUR_MCP_ACCESS_TOKEN` alongside the key header in HTTP client configuration. For local HTTP use `http://localhost:8000/mcp`; use HTTPS for public servers. The OAuth entry point uses OAuth bearer tokens independently of this fixed access token.

## Local stdio (Claude Desktop and other clients)

Create a virtual environment and install dependencies in this repository's `mcp/` directory (`python -m pip install -e .`). Have the client launch Python with absolute paths:

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

Replace Python and `main.py` with actual absolute paths. Use the project virtual environment interpreter at `.venv/bin/python`. Fully quit and restart the client. Stdio does not start HTTP/OAuth endpoints or load the OAuth database. For Zed, use the same server object under `context_servers` instead of `mcpServers`.

## Symbol examples

| Market | Examples |
|---|---|
| Crypto | `BTCUSDT`, `ETHUSDT` |
| Forex / metals | `EURUSD`, `USDJPY`, `XAUUSD`, `XAGUSD` |
| US stocks | `AAPL.US`, `TSLA.US` |
| HK stocks | `700.HK`, `9988.HK` |
| A-shares | `600519.SH`, `000858.SZ` |
| Indices | `SPX`, `NDX`, `VIX` |
| CN / HK futures | Discover current codes with `get_available_symbols(type="futures", market="CN"/"HK")` |

Use `get_available_symbols` when unsure. Company fundamentals tools also accept bare stock codes such as `AAPL`, `700`, or `600519`; add `type=stock` when ambiguous.

## Available tools (43)

### Market tools (13)

| Tool | Function |
|---|---|
| `get_ticker` | Real-time price snapshots |
| `get_kline` | Historical OHLCV candles, with stock adjustment |
| `get_kline_latest` | Latest candles, which may be incomplete |
| `get_order_book` | Order book depth |
| `get_recent_trades` | Recent tick-by-tick trades |
| `get_available_symbols` | Symbol discovery and pagination |
| `get_ex_factors` | Forward/backward stock adjustment factors |
| `get_stock_info` | Basic stock information |
| `get_intraday` | Today's intraday data |
| `get_trading_sessions` | Trading session schedules for one or all stock markets |
| `get_trade_days` | Trading calendar |
| `get_market_metrics` | Market cap, valuation, and market metrics |
| `get_capital_flow` | Capital flows by order size |

### Company fundamentals and event tools (29)

| Category | Tools |
|---|---|
| Company information | `get_company_profile`, `get_company_executives` |
| Financial statements | `get_financials_latest`, `get_financials_annual`, `get_financials_ttm` |
| Business segments | `get_segments_latest`, `get_segments_history` |
| Valuation and industries | `get_valuation_latest`, `get_valuation_history`, `get_industry_peers`, `get_industry_distribution`, `get_industries_rank`, `get_industries_tree` |
| Corporate actions | `get_dividends`, `get_dividends_ttm`, `get_buyback`, `get_corporate_actions` |
| Shareholders and funds | `get_shareholders_latest`, `get_shareholders_top`, `get_shareholder_detail`, `get_fund_holdings_latest` |
| News and market status | `get_company_news`, `get_news_detail`, `get_market_status` |
| Event calendars | `get_report_calendar`, `get_dividend_calendar`, `get_split_calendar`, `get_ipo_calendar`, `get_other_calendar` |

### API key subscription tool (1)

Call `get_api_key_subscriptions` with `{}` to query the current key's subscriptions, status, expiration, and remaining seconds. No website login is required.

## Query Conventions

- Supported candle intervals are `1m 3m 5m 15m 30m 1h 2h 4h 1d 1w 1M`; follow the tool's parameter schema.
- Historical and latest stock candles accept `adjust=none/forward/backward`. The last historical candle may still be forming.
- Order books and tick-by-tick trades cover US/HK/CN stocks, CN/HK futures, and crypto.
- `get_trading_sessions` returns session schedules; use `get_market_status` to ask whether a market is currently open.
- For financial statements, `n` counts periods. Valuation history uses `from_date` / `to_date` for date filters.
- Financial calendars cover reports, dividends, splits, IPOs, and other events; the other-events calendar requires `category`. Dividends, fund holdings, and calendars use top-level `page.next_cursor`; retain filters when paginating.

## Example prompts

- Show the current price of gold XAUUSD.
- Compare Apple's revenue and net income over the last five years.
- Get Tencent's forward-adjusted daily candles.
- Check my API key subscription status and expiration.

## Troubleshooting

- `No TickDB API key provided`: supply a key for header/stdio access, or complete browser authorization for OAuth.
- `Symbol not found` / `AMBIGUOUS_SYMBOL`: discover the correct code and supply `type` when needed. Stock market data uses exchange suffixes.
- `3001` is rate limiting; wait for `Retry-After`. `3002` is exhausted quota; `1005` is an expired key.
- `40405` means no business data for the query, not numeric zero. For `5005` / `5006`, retry later, choose another interval, or use `adjust=none`.
- Missing tools: check JSON/TOML syntax, interpreter paths, and dependencies; reconnect or restart the client. Business requests are not retried automatically.
