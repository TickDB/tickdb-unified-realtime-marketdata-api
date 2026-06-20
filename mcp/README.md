# TickDB MCP — Real-time Market Data for AI

[![CI](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![TickDB](https://img.shields.io/badge/Powered%20by-TickDB-orange)](https://tickdb.ai)

> 📍 本目录是 [tickdb-unified-realtime-marketdata-api](../) 仓库的 MCP 服务端实现，提供 13 个 MCP 工具，可作为 Python 包独立部署。

**TickDB-MCP** 是基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io) 的 Python 服务端实现，通过统一的 REST API 接口为 AI 助手提供实时行情数据（Real-time Market Data）与历史 K 线（Historical K-line）数据。

覆盖 **外汇（Forex/FX） · 贵金属（Precious Metals） · 指数（Indices） · 美股（US Stocks / NASDAQ / NYSE） · 港股（HK Stocks） · A 股（A-shares / CN Stocks） · 加密货币（Cryptocurrency）**，由 13 个 MCP 工具组成，数据来源于 [TickDB Unified Market Data API](https://tickdb.ai)。

**链接：** [官网](https://tickdb.ai) · [文档](https://docs.tickdb.ai) · [联系我们](mailto:support@tickdb.ai)

**语言：** **简体中文** · [繁體中文](docs/tw/README.md) · [English](docs/en/README.md)

---

## 快速开始

```bash
# 1. 安装 Python 依赖（Python 3.11+）
pip install -e .

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填写 TICKDB_API_KEY（前往 https://tickdb.ai 注册获取）

# 3. 启动 MCP 服务端
python main.py          # HTTP 服务，监听 :8000
```

在 AI 客户端配置中添加（也可直接使用托管端点 `https://mcp.tickdb.ai/`）：

```json
{
  "mcpServers": {
    "tickdb": {
      "type": "http",
      "url": "https://mcp.tickdb.ai/",
      "headers": {
        "X-TickDB-Key": "YOUR_TICKDB_API_KEY"
      }
    }
  }
}
```

支持的 AI 客户端：Claude Code · Claude Desktop · Cursor · Kiro · Codex · Zed · Cherry Studio

---

## 13 个 MCP 工具

| 工具 | 说明 | 数据类型 |
|---|---|---|
| `get_ticker` | 实时行情快照（Ticker）：价格、涨跌幅、成交量 | Real-time |
| `get_kline` | 历史 K 线（Candlestick / K-line）OHLCV 数据 | Historical |
| `get_kline_latest` | 最新实时 K 线（当前未收盘） | Real-time |
| `get_order_book` | 买卖盘深度（Order Book / Depth） | Real-time |
| `get_recent_trades` | 最近成交明细（Recent Trades） | Real-time |
| `get_available_symbols` | 查询全部可交易标的（37,527+ 品种） | Reference |
| `get_kline_intervals` | 支持的 K 线周期列表 | Reference |
| `get_stock_info` | 股票基本信息：EPS、BPS、股息率等 | Fundamental |
| `get_intraday` | 当日分时数据（Intraday Data） | Intraday |
| `get_trading_sessions` | 当前交易时段（Trading Session） | Reference |
| `get_trade_days` | 交易日历（Trading Calendar） | Reference |
| `get_market_metrics` | 市场快照（Market Snapshot）：PE/PB、市值、资金流 | Fundamental |
| `get_capital_flow` | 大中小单资金流向分析（Capital Flow） | Real-time |

---

## 覆盖市场与标的代码格式

| 市场 | 品种数 | 代码格式 | 示例 |
|---|---|---|---|
| 加密货币（Cryptocurrency） | 875+ | `BASE + QUOTE` | `BTCUSDT`、`ETHUSDT` |
| 外汇（Forex / FX） | 1,207 | 6 字母货币对 | `EURUSD`、`USDJPY`、`XAUUSD` |
| 贵金属（Precious Metals） | — | `XAU/XAG + USD` | `XAUUSD`、`XAGUSD` |
| 美股（US Stocks / NASDAQ / NYSE） | 12,409 | `TICKER.US` | `AAPL.US`、`TSLA.US`、`NVDA.US` |
| 港股（HK Stocks） | 4,305 | `CODE.HK` | `700.HK`、`9988.HK` |
| A 股 / 沪市（A-shares / CN Stocks） | 6,023 | `6位代码.SH` | `600519.SH`、`601318.SH` |
| A 股 / 深市（A-shares / CN Stocks） | — | `6位代码.SZ` | `000858.SZ`、`000333.SZ` |
| 指数（Indices） | 12,708 | 指数代码 | `SPX`、`NDX`、`VIX`、`DXY` |

---

## 配置说明（Configuration）

将 `.env.example` 复制为 `.env`：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `TICKDB_API_KEY` | _（空）_ | 服务器统一 API Key；空时要求用户通过 `X-TickDB-Key` 请求头自带 |
| `MCP_ACCESS_TOKEN` | _（空）_ | MCP 服务访问 Token；空时服务开放访问 |
| `MCP_TRANSPORT` | `streamable-http` | `stdio` 用于本地 Claude Desktop 直连模式 |
| `MCP_HOST` | `0.0.0.0` | 监听地址 |
| `MCP_PORT` | `8000` | 监听端口 |
| `MCP_STATELESS_HTTP` | `true` | Streamable HTTP 无状态模式；避免遗留 MCP session 占用内存 |
| `MCP_SESSION_LOG_TTL_SECONDS` | `3600` | 会话 ID 仅用于生命周期日志的保留秒数 |
| `MCP_SESSION_LOG_MAX_ENTRIES` | `1000` | 会话 ID 日志缓存最大条数（防止内存无限增长） |
| `LOG_LEVEL` | `INFO` | 日志（Logging）级别：DEBUG / INFO / WARNING / ERROR |
| `LOG_RETAIN_DAYS` | `7` | 日志文件保留天数 |

**API Key 优先级：** `X-TickDB-Key` 请求头 → `TICKDB_API_KEY` 环境变量。

---

## 项目结构

```
tickdb-mcp/
├── main.py                  # 入口文件（Python MCP Server）
├── pyproject.toml           # 包配置与依赖
├── Dockerfile               # Docker 容器化部署
├── .env.example             # 环境变量（Environment）模板
├── tickdb_mcp/              # 核心包
│   ├── config.py            # 配置（Pydantic-settings）
│   ├── client.py            # TickDB REST API HTTP 客户端 + API Key 解析
│   ├── middleware.py        # Bearer Token 鉴权中间件（Middleware）+ Key 注入
│   ├── server.py            # FastMCP 实例工厂
│   └── tools/
│       ├── market.py        # Ticker、K-line、Order Book、Trades、Symbols
│       └── stock.py         # Stock Info、Intraday、Sessions、Metrics、Capital Flow
├── tests/                   # 单元测试（Unit Tests）
│   ├── test_client.py       # API Key 解析与错误处理
│   ├── test_server.py       # MCP 服务创建与工具注册
│   ├── test_middleware.py   # 鉴权与 Accept 头修复
│   └── test_tools.py        # 工具端点映射
├── examples/
│   ├── client_demo.py       # Python MCP 客户端示例
│   └── server_demo.py       # 服务端 smoke test / 工具列表
└── (CI 配置位于上级仓库 ../.github/workflows/mcp-ci.yml)
```

---

## Docker 部署

```bash
# 构建 Docker 镜像
docker build -t tickdb-mcp .

# 运行容器（用户自带 X-TickDB-Key 请求头）
docker run -d -p 8000:8000 tickdb-mcp

# 运行容器（指定服务器统一 API Key）
docker run -d -p 8000:8000 \
  -e TICKDB_API_KEY=YOUR_KEY \
  -e MCP_ACCESS_TOKEN=YOUR_TOKEN \
  tickdb-mcp
```

---

## 开发（Development）

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 代码检查（Lint）
ruff check .

# 运行单元测试（Unit Tests）
pytest tests/ -v

# 运行示例
python examples/server_demo.py
```

---

## 文档

| 文档 | 简体中文 | 繁體中文 | English |
|---|---|---|---|
| 部署说明 | [DEPLOYMENT.md](DEPLOYMENT.md) | [部署說明](docs/tw/DEPLOYMENT.md) | [Deployment Guide](docs/en/DEPLOYMENT.md) |
| 客户端接入 | [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md) | [接入設定指南](docs/tw/MCP_CLIENT_SETUP.md) | [Client Setup Guide](docs/en/MCP_CLIENT_SETUP.md) |
| 更新记录 | [CHANGELOG.md](CHANGELOG.md) | — | — |

---

## 贡献指南

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/my-feature`
3. 遵循 [PEP 8](https://peps.python.org/pep-0008/)，由 `ruff` 强制检查
4. 新功能需包含单元测试（Unit Tests）
5. 提交 PR 并附上清晰的描述

---

## 许可证

MIT — 详见 [LICENSE](LICENSE)。
