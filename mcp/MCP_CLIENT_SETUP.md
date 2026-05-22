# TickDB MCP — 用户接入配置指南

通过 MCP 协议，让 AI 助手直接查询实时行情数据，无需手动调用 API。

**语言：** **简体中文** · [繁體中文](docs/tw/MCP_CLIENT_SETUP.md) · [English](docs/en/MCP_CLIENT_SETUP.md)

---

## 托管端点 vs 自部署

| 方式 | 地址 | 适合场景 |
|---|---|---|
| **托管端点**（推荐） | `https://mcp.tickdb.ai/` | 无需服务器，开箱即用 |
| **自部署** | 自定义地址 | 需要私有化、定制中间件 |

> 托管端点由 TickDB 官方维护，HTTPS + Header 鉴权，无需 Docker 或服务器配置。

---

## API Key 说明

使用前需要有效的 TickDB API Key，前往 [tickdb.ai](https://tickdb.ai) 注册获取。

Key 的提供方式（优先级从高到低）：

| 方式 | 说明 |
|---|---|
| `X-TickDB-Key` 请求头 | 在 MCP 配置的 `headers` 中填写，每次请求随调用传入 |
| `TICKDB_API_KEY` 环境变量 | 自部署时由服务器运营方统一配置，用户无需自带 Key |

---

## 各客户端配置

### Claude Code

配置文件：`.claude/settings.json`（项目级）或 `~/.claude/settings.json`（全局）

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

配置保存后，在 Claude Code 中执行 `/mcp` 命令刷新，看到 `tickdb` 出现在列表中即接入成功。

---

### Claude Desktop

配置文件路径：

| 系统 | 路径 |
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

配置后**完全退出并重启** Claude Desktop 生效。工具栏出现锤子图标即表示工具已加载。

---

### Cursor

配置文件：`~/.cursor/mcp.json`

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

配置文件：`~/.kiro/settings/mcp.json`

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

### Codex（OpenAI）

配置文件：`~/.codex/config.json`

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

配置文件：`~/.config/zed/settings.json`

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

进入 **设置 → MCP 服务器 → 添加**，填写：

| 字段 | 值 |
|---|---|
| 名称 | `tickdb` |
| 类型 | HTTP |
| URL | `https://mcp.tickdb.ai/` |
| Header | `X-TickDB-Key: YOUR_API_KEY` |

---

## 需要访问控制 Token 时（自部署）

如果你连接的是自部署服务器且运营方设置了 `MCP_ACCESS_TOKEN`，需要同时传入 Authorization 头：

```json
{
  "mcpServers": {
    "tickdb": {
      "type": "http",
      "url": "https://your-mcp-server.com/mcp",
      "headers": {
        "Authorization": "Bearer 服务商提供的Token",
        "X-TickDB-Key": "YOUR_API_KEY"
      }
    }
  }
}
```

---

## 本地 stdio 模式（Claude Desktop 直连自部署）

无需 HTTP 服务，直接本地运行：

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

## 标的代码格式速查

| 市场 | 格式 | 示例 |
|---|---|---|
| 加密货币 | `基础货币 + 计价货币` | `BTCUSDT`、`ETHUSDT` |
| 外汇 | 6 字母货币对 | `EURUSD`、`USDJPY`、`GBPUSD` |
| 贵金属 | `XAU/XAG + USD` | `XAUUSD`、`XAGUSD` |
| 美股 | `股票代码.US` | `AAPL.US`、`TSLA.US`、`NVDA.US` |
| 港股 | `数字代码.HK` | `700.HK`、`9988.HK` |
| 沪市 A 股 | `6位代码.SH` | `600519.SH`、`601318.SH` |
| 深市 A 股 | `6位代码.SZ` | `000858.SZ`、`000333.SZ` |
| 指数 | 指数代码 | `SPX`、`NDX`、`VIX`、`DXY` |

不确定代码？直接问 AI：*"帮我查一下比亚迪的股票代码"*，会自动调用 `get_available_symbols` 查询。

---

## 可用工具（13 个）

| 工具 | 功能 | 支持市场 |
|---|---|---|
| `get_ticker` | 实时行情快照（价格、涨跌幅、成交量） | 全部 |
| `get_kline` | 历史 K 线数据（OHLCV） | 全部 |
| `get_kline_latest` | 最新实时 K 线（当前未收盘） | 全部 |
| `get_order_book` | 买卖盘深度 | 美股、港股、加密 |
| `get_recent_trades` | 最近成交明细 | 港股、加密 |
| `get_available_symbols` | 查询可交易标的（37,527+） | 全部 |
| `get_kline_intervals` | 支持的 K 线周期列表 | 全部 |
| `get_stock_info` | 股票基本信息（EPS、BPS、股息率等） | 美股、港股、A 股 |
| `get_intraday` | 当日分时数据 | 美股、港股、A 股 |
| `get_trading_sessions` | 当前交易时段 | 美股、港股、A 股 |
| `get_trade_days` | 交易日历查询 | 美股、港股、A 股 |
| `get_market_metrics` | 市值、PE/PB、资金流等综合指标 | 美股、港股、A 股 |
| `get_capital_flow` | 大中小单资金流向分析 | 美股、港股、A 股 |

---

## 使用示例

```
你：黄金现在什么价格？
AI：（调用 get_ticker，返回 XAUUSD 实时价格）

你：帮我看看比特币最近 7 天的日线走势
AI：（调用 get_kline，获取 BTCUSDT 1d 数据）

你：腾讯股票的市盈率是多少？
AI：（调用 get_market_metrics，返回 700.HK 的 PE TTM）

你：美股今天开盘了吗？
AI：（调用 get_trading_sessions，返回 US 市场当前时段）

你：帮我看看贵州茅台的资金流向
AI：（调用 get_capital_flow，返回 600519.SH 大中小单流向）
```

---

## 常见问题

**提示"No TickDB API key provided"**
在 MCP 配置的 `headers` 中添加 `X-TickDB-Key`，或前往 [tickdb.ai](https://tickdb.ai) 注册获取 Key。

**提示"Symbol not found"**
检查标的代码格式，美股需要加 `.US` 后缀（如 `AAPL.US`），港股加 `.HK`，A 股加 `.SH` 或 `.SZ`。

**提示"Quota exhausted"或"Rate limit exceeded"**
当前 Key 的配额已用完或超过频率限制。前往 [tickdb.ai](https://tickdb.ai) 查看套餐详情或升级计划。

**Claude Desktop 配置后没有看到工具**
确认 JSON 格式正确（无多余逗号），并**完全退出**后重新启动 Claude Desktop。

**我的 Key 会暴露给服务器吗？**
`X-TickDB-Key` 仅用于转发给 TickDB API 鉴权，服务器不做持久化存储。
