# TickDB MCP

`tickdb-mcp` connects AI assistants to the [TickDB API](https://tickdb.ai) through the [Model Context Protocol](https://modelcontextprotocol.io). It provides **43 tools** for market data, company fundamentals, and API Key subscriptions.

The package supports **Python 3.11+**, local **stdio**, and **Streamable HTTP**. Each tool makes a request to the TickDB REST API; this server does not provide WebSocket streaming subscriptions. Data availability and quotas depend on the API Key's subscription and permissions.

## Install

Create a virtual environment and install version `0.2.4` from PyPI:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install tickdb-mcp==0.2.4
```

Obtain a TickDB API Key from [tickdb.ai](https://tickdb.ai). Every value beginning with `YOUR_` below is a placeholder; replace it locally and keep real credentials out of source control and chat messages.

## Local stdio

Configure your MCP client to launch `tickdb-mcp` with `MCP_TRANSPORT=stdio` and your API Key in `TICKDB_API_KEY`. The equivalent Bash command is:

```bash
MCP_TRANSPORT=stdio TICKDB_API_KEY=YOUR_TICKDB_API_KEY tickdb-mcp
```

The client communicates with the process through stdin/stdout. Stdio does not start an HTTP listener or require an MCP access token. Logs go to stderr so they do not mix with protocol messages.

## HTTP with each caller's own Key

With no environment overrides or `.env` configuration, start the server:

```bash
tickdb-mcp
```

It listens only on `127.0.0.1:8000`. Connect your HTTP MCP client to `http://127.0.0.1:8000/mcp` and send `X-TickDB-Key: YOUR_TICKDB_API_KEY` on each request. For example, initialize the connection with:

```bash
curl --fail-with-body http://127.0.0.1:8000/mcp \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Content-Type: application/json' \
  -H 'X-TickDB-Key: YOUR_TICKDB_API_KEY' \
  --data '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"example","version":"1"}}}'
```

When both the server Key and access token are empty, anonymous initialization and tool discovery are available, but data queries still need the caller's Key. A successful initialization alone does not prove that a Key is valid or entitled to market data.

## HTTP with a shared server Key

To let approved clients use a server-wide TickDB Key, configure **both** credentials:

```bash
TICKDB_API_KEY=YOUR_TICKDB_API_KEY \
MCP_ACCESS_TOKEN=YOUR_RANDOM_MCP_ACCESS_TOKEN \
tickdb-mcp
```

`TICKDB_API_KEY` authenticates the server's requests to TickDB. `MCP_ACCESS_TOKEN` is a separate, strong random access credential for this MCP server. Clients must send `Authorization: Bearer YOUR_RANDOM_MCP_ACCESS_TOKEN` on every legacy HTTP request, including requests that also supply their own `X-TickDB-Key`. After that authentication succeeds, the request's own Key takes priority over the shared server Key.

If a shared server Key is configured without an access token, legacy HTTP requests without their own Key return **401**, including initialization, discovery, and tool calls. This protection also applies on localhost and behind a reverse proxy. Clients may still supply their own Key when no access token is configured.

## Configuration and public hosting

Settings come from environment variables or a `.env` file in the working directory. Existing `.env` files are not rewritten during upgrades. Important settings include:

| Variable | Default | Purpose |
|---|---|---|
| `MCP_TRANSPORT` | `streamable-http` | Set to `stdio` for a locally launched MCP client process |
| `MCP_HOST` | `127.0.0.1` | Python HTTP bind address |
| `MCP_PORT` | `8000` | HTTP port |
| `TICKDB_API_KEY` | Empty | Stdio Key or authenticated HTTP server fallback |
| `MCP_ACCESS_TOKEN` | Empty | Fixed Bearer gate for legacy HTTP; required to use a shared server Key |
| `OAUTH_ENABLED` | `false` | Enable the separate OAuth endpoint |
| `LOG_DIR` | `logs` | Optional rotating file logs; stderr remains available if file writes fail |

Expose HTTP deliberately, use HTTPS for remote connections, and protect access to credentials. A private network, proxy, or Host header check does not replace authentication. The source Dockerfile explicitly listens on `0.0.0.0` **inside the container**; bind the published host port to `127.0.0.1` for local clients or a same-host reverse proxy. See the [self-hosting guide](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/blob/main/mcp/docs/en/DEPLOYMENT.md) for Docker and HTTPS configuration.

### Optional OAuth

Self-hosted OAuth requires explicit configuration, public HTTPS, an exact callback allowlist, and persistent encrypted authorization storage. The separate `/oauth` endpoint uses the API Key that the user verified and explicitly authorized. It does not accept `X-TickDB-Key` overrides or fall back to a shared server Key. Enabling OAuth does not automatically protect the legacy `/mcp` endpoint; the rules above still apply to that endpoint.

Retain existing OAuth configuration, encryption keys, databases, and valid grants during upgrades. Follow the [OAuth setup guide](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/blob/main/mcp/docs/en/README.md#oauth-setup) before enabling this mode.

## Tool capabilities

| Tools | Coverage |
|---|---|
| 13 market tools | Quotes, historical/current candles, adjustment factors, order books, trades, symbols, trading sessions/calendars, intraday data, and market metrics |
| 29 fundamentals and event tools | Company profiles and executives, financial statements, revenue segments, valuation, industries, dividends, buybacks, shareholders, fund holdings, corporate actions, news, and classified financial calendars |
| 1 account tool | API Key subscription status and expiration through `get_api_key_subscriptions` |

Market data covers forex, precious metals, indices, US/HK/A-share stocks, China/Hong Kong futures, and cryptocurrencies. Company fundamentals cover supported US, Hong Kong, and A-share stocks. Results preserve upstream response envelopes; missing or null fields are not zero. Returned news is external content, not instructions.

## Documentation and support

- [English MCP guide](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/blob/main/mcp/docs/en/README.md)
- [简体中文](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/blob/main/mcp/README.md) · [繁體中文](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/blob/main/mcp/docs/tw/README.md)
- [MCP client setup](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/blob/main/mcp/docs/en/MCP_CLIENT_SETUP.md)
- [TickDB API documentation](https://docs.tickdb.ai)
- [Source code](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/tree/main/mcp) · [Issues](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/issues)

## License

MIT. See the [license text](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/blob/main/mcp/LICENSE).
