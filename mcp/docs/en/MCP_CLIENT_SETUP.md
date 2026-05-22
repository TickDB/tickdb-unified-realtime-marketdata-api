# TickDB MCP — Client Setup Guide

Connect your AI assistant to live market data via the MCP protocol.

**Language:** [简体中文](../../MCP_CLIENT_SETUP.md) · [繁體中文](../tw/MCP_CLIENT_SETUP.md) · **English**

---

## Hosted Endpoint vs Self-Hosted

| Option | URL | Best for |
|---|---|---|
| **Hosted** (recommended) | `https://mcp.tickdb.ai/` | No server needed, works immediately |
| **Self-hosted** | Custom URL | Private deployment, custom middleware |

> The hosted endpoint is maintained by TickDB — HTTPS + header auth, no Docker or server setup required.

---

## API Key

A valid TickDB API key is required. Register at [tickdb.ai](https://tickdb.ai).

**Key delivery options** (highest priority first):

| Method | How |
|---|---|
| `X-TickDB-Key` request header | Add to MCP client config `headers` — sent with every request |
| `TICKDB_API_KEY` env var | Set on a self-hosted server — shared key for all users |

---

## Client Configuration

### Claude Code

Config file: `.claude/settings.json` (project) or `~/.claude/settings.json` (global)

```json
{
  "mcpServers": {
    "tickdb": {
      "type": "http",
      "url": "https://mcp.tickdb.ai/",
      "headers": {
        "X-TickDB-Key": "YOUR_API_KEY"
      }
    }
  }
}
```

After saving, run `/mcp` in Claude Code to refresh. `tickdb` should appear in the list.

---

### Claude Desktop

Config file location:

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

```json
{
  "mcpServers": {
    "tickdb": {
      "type": "http",
      "url": "https://mcp.tickdb.ai/",
      "headers": {
        "X-TickDB-Key": "YOUR_API_KEY"
      }
    }
  }
}
```

**Fully quit and restart** Claude Desktop after saving. The hammer icon in the toolbar confirms tools are loaded.

---

### Cursor

Config file: `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "tickdb": {
      "type": "http",
      "url": "https://mcp.tickdb.ai/",
      "headers": {
        "X-TickDB-Key": "YOUR_API_KEY"
      }
    }
  }
}
```

---

### Kiro

Config file: `~/.kiro/settings/mcp.json`

```json
{
  "mcpServers": {
    "tickdb": {
      "type": "http",
      "url": "https://mcp.tickdb.ai/",
      "headers": {
        "X-TickDB-Key": "YOUR_API_KEY"
      }
    }
  }
}
```

---

### Codex (OpenAI)

Config file: `~/.codex/config.json`

```json
{
  "mcpServers": {
    "tickdb": {
      "type": "http",
      "url": "https://mcp.tickdb.ai/",
      "headers": {
        "X-TickDB-Key": "YOUR_API_KEY"
      }
    }
  }
}
```

---

### Zed

Config file: `~/.config/zed/settings.json`

```json
{
  "context_servers": {
    "tickdb": {
      "type": "http",
      "url": "https://mcp.tickdb.ai/",
      "headers": {
        "X-TickDB-Key": "YOUR_API_KEY"
      }
    }
  }
}
```

---

### Cherry Studio

Go to **Settings → MCP Servers → Add**, fill in:

| Field | Value |
|---|---|
| Name | `tickdb` |
| Type | HTTP |
| URL | `https://mcp.tickdb.ai/` |
| Header | `X-TickDB-Key: YOUR_API_KEY` |

---

## With Access Token (Self-hosted)

If the self-hosted server has `MCP_ACCESS_TOKEN` set, include the Authorization header too:

```json
{
  "mcpServers": {
    "tickdb": {
      "type": "http",
      "url": "https://your-mcp-server.com/mcp",
      "headers": {
        "Authorization": "Bearer SERVER_ACCESS_TOKEN",
        "X-TickDB-Key": "YOUR_API_KEY"
      }
    }
  }
}
```

---

## Local stdio Mode (Claude Desktop direct)

For local use without an HTTP server:

```json
{
  "mcpServers": {
    "tickdb": {
      "command": "python",
      "args": ["/path/to/tickdb-mcp/main.py"],
      "env": {
        "MCP_TRANSPORT": "stdio",
        "TICKDB_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

---

## Symbol Format Reference

| Market | Format | Examples |
|---|---|---|
| Crypto | `BASE + QUOTE` | `BTCUSDT`, `ETHUSDT` |
| Forex | 6-letter pair | `EURUSD`, `USDJPY`, `GBPUSD` |
| Precious metals | `XAU/XAG + USD` | `XAUUSD`, `XAGUSD` |
| US stocks | `TICKER.US` | `AAPL.US`, `TSLA.US`, `NVDA.US` |
| HK stocks | `CODE.HK` | `700.HK`, `9988.HK` |
| Shanghai A-shares | `6-digit.SH` | `600519.SH`, `601318.SH` |
| Shenzhen A-shares | `6-digit.SZ` | `000858.SZ`, `000333.SZ` |
| Indices | Index code | `SPX`, `NDX`, `VIX`, `DXY` |

---

## Available Tools (13)

| Tool | Description | Markets |
|---|---|---|
| `get_ticker` | Real-time price snapshot (price, change, volume) | All |
| `get_kline` | Historical OHLCV candlestick data | All |
| `get_kline_latest` | Current live candle (incomplete) | All |
| `get_order_book` | Bid/ask depth | US stocks, HK stocks, Crypto |
| `get_recent_trades` | Latest executed trades | HK stocks, Crypto |
| `get_available_symbols` | Discover 37,527+ tradable symbols | All |
| `get_kline_intervals` | Supported candle interval list | All |
| `get_stock_info` | Fundamentals: EPS, BPS, dividend yield | US, HK, A-shares |
| `get_intraday` | Minute-level intraday data | US, HK, A-shares |
| `get_trading_sessions` | Current market session status | US, HK, A-shares |
| `get_trade_days` | Trading calendar for a date range | US, HK, A-shares |
| `get_market_metrics` | PE, PB, market cap, capital flow | US, HK, A-shares |
| `get_capital_flow` | Large/medium/small order flow analysis | US, HK, A-shares |

---

## Troubleshooting

**"No TickDB API key provided"**
Add `X-TickDB-Key` to your MCP config headers. Register at [tickdb.ai](https://tickdb.ai) to get a key.

**"Symbol not found"**
Check the symbol format. US stocks need `.US` (`AAPL.US`), HK stocks need `.HK`, A-shares need `.SH` or `.SZ`.

**"Quota exhausted" or "Rate limit exceeded"**
Your key's quota is used up. Check your plan at [tickdb.ai](https://tickdb.ai).

**Claude Desktop shows no tools after config**
Verify the JSON is valid (no trailing commas), then **fully quit** and restart Claude Desktop.

**Will the server store my API key?**
`X-TickDB-Key` is forwarded to the TickDB API for authentication only and is not persisted.
