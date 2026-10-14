# TickDB MCP — 用户接入配置指南

**语言：** **简体中文** · [繁體中文](docs/tw/MCP_CLIENT_SETUP.md) · [English](docs/en/MCP_CLIENT_SETUP.md)

v0.2.3 提供 43 个工具：13 个行情工具、29 个公司财务与事件工具、1 个 API Key 订阅工具。支持外汇、贵金属、指数、美股、港股、A 股、中国及香港期货、加密货币。具体数据取决于市场、披露时间和套餐权限。

## 选择接入方式

| 方式 | 地址 | 鉴权 |
|---|---|---|
| 自部署 HTTP | `http://localhost:8000/mcp` 或 `https://mcp.example.com/mcp` | `X-TickDB-Key`，或服务端统一 Key |
| 自部署 OAuth | `https://mcp.example.com/oauth` | 网页授权绑定自己的 TickDB API Key |
| 公开托管 HTTP | `https://mcp.tickdb.ai/` | `X-TickDB-Key` |
| 公开托管 OAuth | `https://mcp.tickdb.ai/oauth` | 网页 OAuth 授权 |
| 本地 stdio | 本地 Python 进程 | `TICKDB_API_KEY` 环境变量 |

下面的 HTTP 示例使用自部署地址，连接公开托管服务时可替换为 `https://mcp.tickdb.ai/`。部署步骤见 [部署指南](DEPLOYMENT.md)。

## API Key 与授权

先在 [tickdb.ai](https://tickdb.ai) 注册并获取有效 API Key。HTTP `/mcp` 接入优先使用 `X-TickDB-Key` 请求头，未提供时使用服务端 `TICKDB_API_KEY`；stdio 使用环境变量。OAuth `/oauth` 仅使用用户确认授权后绑定的 Key，不接受 `X-TickDB-Key`，不回退到服务端统一 Key。

Header 接入不持久化保存用户 Key；OAuth 接入会加密保存 Key 绑定，以便后续调用和刷新授权。不要将 API Key 填入 OAuth 客户端 ID/Secret 或聊天消息。

## ChatGPT / Claude 网页版

1. 添加自定义 MCP 服务器或连接器，URL 填 `https://mcp.example.com/oauth`，或公开托管入口 `https://mcp.tickdb.ai/oauth`。
2. 选择 OAuth，使用自动发现和动态客户端注册（DCR）；客户端 ID/Secret 留空。DCR 是 OAuth 内部的注册机制，无需寻找单独的 DCR 身份验证选项。
3. 在打开的 TickDB 授权页输入自己的 API Key，验证后核对脱敏标识和订阅信息，再确认授权。授权页支持简体、繁体和英文。
4. 返回客户端后刷新工具列表并调用工具，例如查询 API Key 订阅与到期时间。

自部署服务需启用 OAuth、HTTPS 和精确的回调白名单：ChatGPT 新连接使用 `https://chatgpt.com/connector_platform_oauth_redirect`，Claude 网页版使用 `https://claude.ai/api/mcp/auth_callback`。已有连接若显示其他完整回调地址，按实际地址配置。详见 [OAuth 配置与接入说明](README.md#oauth-setup)。

## 桌面与开发客户端

### Claude Code

项目共享配置文件为 `.mcp.json`，也可使用 `claude mcp add` 管理。保存后在 Claude Code 执行 `/mcp` 检查连接。配置位置见 [官方 MCP 文档](https://code.claude.com/docs/en/mcp)。

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

远程 OAuth 服务通过 Claude 的连接器界面添加，使用上面的网页授权流程。本地 `claude_desktop_config.json` 使用下方 stdio 配置，配置文件位置以客户端设置为准。

### Cursor

配置文件为项目 `.cursor/mcp.json` 或全局 `~/.cursor/mcp.json`。保存并重新连接服务器，参见 [官方说明](https://cursor.com/docs/mcp)。

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

在 Kiro 打开工作区或用户 MCP 配置（通常为 `.kiro/settings/mcp.json` 或 `~/.kiro/settings/mcp.json`），保存后自动重新连接。版本差异以 [官方说明](https://kiro.dev/docs/mcp/configuration/) 为准。

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

使用 `~/.codex/config.toml`，项目配置可放在受信任项目的 `.codex/config.toml`。检查连接可运行 `codex mcp list`，配置格式见 [OpenAI 官方 MCP 文档](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)。

```toml
[mcp_servers.tickdb]
url = "https://mcp.example.com/mcp"
http_headers = { "X-TickDB-Key" = "YOUR_API_KEY" }
```

### Zed

在 **Settings → AI → MCP Servers** 添加远程服务器，或编辑设置文件的 `context_servers`。下面示例用于配置了 `MCP_ACCESS_TOKEN` 的自部署服务；无 Authorization 头时 Zed 可能尝试 OAuth，应使用启用 OAuth 的 `/oauth` 入口，或改用下方本地 stdio 配置。参见 [官方说明](https://zed.dev/docs/ai/mcp)。

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

进入 **设置 → MCP 服务器 → 添加**，名称填 `tickdb`，类型选择 Streamable HTTP，URL 填 `https://mcp.example.com/mcp`，Header 填 `X-TickDB-Key: YOUR_API_KEY`。如服务设置了访问 Token，另加 `Authorization: Bearer YOUR_MCP_ACCESS_TOKEN`。

## 自部署访问 Token

如果服务端设置了 `MCP_ACCESS_TOKEN`，在上述 HTTP 客户端的请求头中同时加入 `Authorization: Bearer YOUR_MCP_ACCESS_TOKEN`。本地 HTTP 将 URL 改为 `http://localhost:8000/mcp`；公网服务使用 HTTPS。OAuth 入口的 Authorization 使用 OAuth 令牌，与该固定访问 Token 独立。

## 本地 stdio（Claude Desktop 等）

先在此仓库的 `mcp/` 目录创建虚拟环境并安装依赖（`python -m pip install -e .`）。客户端以绝对路径启动 Python：

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

替换 Python 与 `main.py` 为实际绝对路径；Python 使用项目虚拟环境的 `.venv/bin/python`。保存后完全退出并重启客户端。stdio 不启动 HTTP 或 OAuth 端点，不加载 OAuth 数据库。Zed 使用同一服务器对象，但外层键改为 `context_servers`。

## 标的代码速查

| 市场 | 示例 |
|---|---|
| 加密货币 | `BTCUSDT`、`ETHUSDT` |
| 外汇 / 贵金属 | `EURUSD`、`USDJPY`、`XAUUSD`、`XAGUSD` |
| 美股 | `AAPL.US`、`TSLA.US` |
| 港股 | `700.HK`、`9988.HK` |
| A 股 | `600519.SH`、`000858.SZ` |
| 指数 | `SPX`、`NDX`、`VIX` |
| 中国 / 香港期货 | 使用 `get_available_symbols(type="futures", market="CN"/"HK")` 查询当前代码 |

代码不确定时先调用 `get_available_symbols`。公司财务工具也接受无后缀代码（例如 `AAPL`、`700`、`600519`）；发生歧义时补充 `type=stock`。

## 可用工具（43 个）

### 行情工具（13 个）

| 工具 | 功能 |
|---|---|
| `get_ticker` | 实时行情快照 |
| `get_kline` | 历史 OHLCV K 线，支持股票复权 |
| `get_kline_latest` | 最新 K 线，可仍未收盘 |
| `get_order_book` | 买卖盘深度 |
| `get_recent_trades` | 逐笔成交明细 |
| `get_available_symbols` | 标的查询与分页 |
| `get_ex_factors` | 股票前复权 / 后复权因子 |
| `get_stock_info` | 股票基本信息 |
| `get_intraday` | 当日分时数据 |
| `get_trading_sessions` | 单个或全部股票市场的交易时段安排 |
| `get_trade_days` | 交易日历 |
| `get_market_metrics` | 市值、估值与综合指标 |
| `get_capital_flow` | 大中小单资金流向 |

### 公司财务与事件工具（29 个）

| 分类 | 工具 |
|---|---|
| 公司资料 | `get_company_profile`, `get_company_executives` |
| 财务报表 | `get_financials_latest`, `get_financials_annual`, `get_financials_ttm` |
| 业务分部 | `get_segments_latest`, `get_segments_history` |
| 估值与行业 | `get_valuation_latest`, `get_valuation_history`, `get_industry_peers`, `get_industry_distribution`, `get_industries_rank`, `get_industries_tree` |
| 资本行动 | `get_dividends`, `get_dividends_ttm`, `get_buyback`, `get_corporate_actions` |
| 股东与基金 | `get_shareholders_latest`, `get_shareholders_top`, `get_shareholder_detail`, `get_fund_holdings_latest` |
| 新闻与市场状态 | `get_company_news`, `get_news_detail`, `get_market_status` |
| 分类日历 | `get_report_calendar`, `get_dividend_calendar`, `get_split_calendar`, `get_ipo_calendar`, `get_other_calendar` |

### API Key 订阅工具（1 个）

`get_api_key_subscriptions` 使用空参数 `{}` 查询当前 Key 的套餐、状态、到期时间与剩余秒数；不需要官网登录。

## 调用约定

- K 线支持周期为 `1m 3m 5m 15m 30m 1h 2h 4h 1d 1w 1M`，以工具参数说明为准。
- 股票历史和最新 K 线支持 `adjust=none/forward/backward`；历史最后一根 K 线可能仍在形成。
- 订单簿与逐笔成交支持美股、港股、A 股、中港期货及加密。
- `get_trading_sessions` 返回交易时段安排；查询现在是否开盘使用 `get_market_status`。
- 财报参数 `n` 表示期数；估值历史使用 `from_date` / `to_date` 筛选日期。
- 财经日历包括报告、分红、拆股、IPO 和其他事件五类工具；其他事件日历需传 `category`。分红、基金持仓及日历按顶层 `page.next_cursor` 翻页，保持筛选条件一致。

## 自然语言示例

- 查询黄金 XAUUSD 的实时价格。
- 比较苹果最近五年的营收和净利润。
- 查询腾讯的前复权日 K 线。
- 查询我的 API Key 订阅状态和到期时间。

## 常见问题

- `No TickDB API key provided`：Header 或 stdio 接入需补充 Key；OAuth 接入需完成网页授权。
- `Symbol not found` / `AMBIGUOUS_SYMBOL`：查询正确代码，必要时补充 `type`；股票行情代码使用市场后缀。
- `3001` 表示频率限制，按 `Retry-After` 等待；`3002` 表示配额耗尽；`1005` 表示 Key 已过期。
- `40405` 表示当前条件下无业务数据，不能按数值零使用；`5005` / `5006` 可尝试稍后查询、更换周期或 `adjust=none`。
- 客户端未加载工具：检查 JSON / TOML 格式、绝对路径与依赖，重新连接或重启客户端。服务不会自动重试业务调用。
