# TickDB MCP — AI 行情与公司基本面服务

[![CI](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-lightgrey.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

> 本目录是 [tickdb-unified-realtime-marketdata-api](../) 仓库的 MCP 服务端实现，当前版本 **v0.2.3**，可作为 Python 包或 Docker 容器独立部署。

**TickDB-MCP** 通过 [Model Context Protocol](https://modelcontextprotocol.io) 为 AI 助手提供 **43 个工具：13 个行情工具、29 个公司财务与基本面工具、1 个 API Key 订阅查询工具**。工具调用由 [TickDB REST API](https://tickdb.ai) 提供数据；本服务不提供 WebSocket 流式订阅。

行情覆盖 **外汇 · 贵金属 · 指数 · 美股 · 港股 · A 股 · 中港期货 · 加密货币**。公司财务与基本面覆盖美股、港股和 A 股，具体可用性取决于品种、披露时间及 API Key 套餐权限。

**链接：** [官网](https://tickdb.ai) · [API 文档](https://docs.tickdb.ai) · [联系我们](mailto:support@tickdb.ai)

**语言：** **简体中文** · [繁體中文](docs/tw/README.md) · [English](docs/en/README.md)

## 快速开始

首次安装时，在 Linux 终端中从本仓库根目录执行以下 Bash 命令。需要 Python 3.11+；升级时保留已有 `.env`，无需重新复制：

```bash
cd mcp
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cp .env.example .env
# 编辑 .env，填写 TICKDB_API_KEY；也可由客户端通过请求头提供 Key
python main.py
```

服务默认监听端口 8000。支持 HTTP MCP 的客户端可连接本地端点：

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

本地 HTTP 端点为 `http://localhost:8000/mcp`；公开托管请求头端点为 `https://mcp.tickdb.ai/`。已配置服务器统一 Key 时，可省略示例中的 `X-TickDB-Key`。若设置 `MCP_ACCESS_TOKEN`，客户端还须添加 `Authorization: Bearer <token>`。

Claude Desktop 本地模式使用 `MCP_TRANSPORT=stdio`、Python 命令及 `TICKDB_API_KEY` 环境变量，详见 [客户端接入指南](MCP_CLIENT_SETUP.md)。

<a id="oauth-setup"></a>
## 网页 OAuth 接入与自部署

ChatGPT / Claude 网页端使用 OAuth 连接。公开托管 URL 为 `https://mcp.tickdb.ai/oauth`；自部署使用 `https://你的域名/oauth`。用户在授权页面验证自己的 TickDB API Key 并确认授权，无需自定义请求头。

OAuth **默认关闭**，启用时使用单实例服务、持久化本地 SQLite 和公网 HTTPS。现有 `/mcp` 请求头接入与 stdio 模式仍可使用相同的 43 个工具。

### 配置与持久化

按快速开始安装依赖，并在私有 `.env` 中配置：

```dotenv
OAUTH_ENABLED=true
OAUTH_PUBLIC_URL=https://mcp.example.com
OAUTH_DATABASE_PATH=data/oauth.sqlite3
OAUTH_ENCRYPTION_KEY=REPLACE_WITH_THE_GENERATED_FERNET_KEY
OAUTH_REDIRECT_URIS=["https://chatgpt.com/connector_platform_oauth_redirect","https://claude.ai/api/mcp/auth_callback"]
```

首次安装时生成一次 Fernet 密钥，将结果填入 `OAUTH_ENCRYPTION_KEY`，单独备份。在已激活的虚拟环境中执行以下命令：

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

`OAUTH_PUBLIC_URL` 必须是 HTTPS origin，不带路径、查询或片段。回调白名单按完整 URL 精确匹配，不支持通配符或任意 HTTP loopback 回调。`.env.example` 默认只列出 ChatGPT 回调，Claude 网页接入需加入上述 Claude 回调；客户端显示其他回调时，按实际完整 URL 配置。

Python 部署使用可写的本地数据库路径。Docker 部署把数据库路径改为 `/app/data/oauth.sqlite3`，并在 `mcp/` 中执行以下命令：

```bash
docker build -t tickdb-mcp:0.2.3 .
docker volume create tickdb-mcp-data
docker run -d --name tickdb-mcp --restart unless-stopped -p 127.0.0.1:8000:8000 --env-file .env -v tickdb-mcp-data:/app/data tickdb-mcp:0.2.3
```

配置、数据库与密钥须保存在 Git 和镜像之外。SQLite 网络共享不适合作为多实例存储。

### HTTPS 反向代理

所有发现、注册、授权、确认、Token 和撤销路径须原样转发，不能把所有请求重写到 `/mcp`。例如配置 Nginx，并替换域名与证书路径：

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

`GET /.well-known/oauth-authorization-server` 和 `GET /.well-known/oauth-protected-resource/oauth` 返回发现信息；未认证的 `/oauth` MCP 请求返回 401 并提示发现地址。OAuth resource 为 `https://mcp.example.com/oauth`，使用发现结果中的完整 issuer，包括末尾斜杠。

### 客户端授权

客户端选择 OAuth；如有动态客户端注册选项则启用，否则使用自动发现。手工填写的客户端 ID/Secret 留空，TickDB API Key 不能填入这些字段。在 TickDB 授权页面输入自己的 Key，验证脱敏标识与对应订阅，再确认授权。页面支持简体、繁体和英文，自动匹配浏览器语言，也可手工切换。

授权页面只展示本次提交 Key 的脱敏标识及唯一匹配的订阅。新 ChatGPT 连接的固定回调为 `https://chatgpt.com/connector_platform_oauth_redirect`，服务端为其提供 issuer 标识；Claude 网页回调为 `https://claude.ai/api/mcp/auth_callback`。客户端设置示例见 [接入指南](MCP_CLIENT_SETUP.md)。

### 授权与升级

- 动态注册使用 `POST /register`，支持 `none` 或 `client_secret_post` 客户端认证；所有客户端均须使用 PKCE S256。
- 授权流程使用 `/authorize`、`/oauth/consent` 和 `/token`，scope 为 `tickdb:read`；`/revoke` 撤销 Token，刷新 Token 重用会撤销对应授权。
- `/oauth` 使用 `Authorization: Bearer <access_token>`，拒绝 `X-TickDB-Key` 覆盖，不回退到服务器统一 Key。API Key 绑定加密存入 SQLite，浏览器确认请求检查 Cookie、Origin 和 CSRF。
- 常规升级时保留同一加密密钥、数据库路径或数据卷、公网 origin、回调白名单及已有授权。升级前一致性备份配置与数据库，可使用 SQLite 备份接口，或停止服务后再复制数据库；如存在 WAL 须包含尚未合并的数据。替换代码或镜像时不要删除、重新初始化数据库或重新生成加密密钥。保留旧镜像以便回滚。
- 加密密钥或数据库绑定的公网 resource 改变时，服务启动校验会失败。首次公开部署后检查发现、浏览器授权、工具发现与调用，以及客户端重连。

## 43 个 MCP 工具

### 行情工具（13 个）

| 工具 | 功能 |
|---|---|
| `get_ticker` | 指定品种的实时行情快照 |
| `get_kline` | 历史 OHLCV；股票支持 `adjust=none/forward/backward` |
| `get_kline_latest` | 当前未收盘 K 线；支持股票复权 |
| `get_ex_factors` | 美股、港股、A 股前复权／后复权因子 |
| `get_order_book` | 买卖盘深度 |
| `get_recent_trades` | 逐笔成交明细 |
| `get_available_symbols` | 查询可交易品种，含中国与香港期货 |
| `get_stock_info` | 股票基本信息，如 EPS、BPS、股息率 |
| `get_intraday` | 当日分时数据 |
| `get_trading_sessions` | 单个或全部股票市场的交易时段 |
| `get_trade_days` | 股票市场交易日历 |
| `get_market_metrics` | PE/PB、市值及资金流等指标 |
| `get_capital_flow` | 大中小单资金流向 |

买卖盘与逐笔成交支持美股、港股、A 股、中港期货和加密货币。股票信息、分时、交易时段、交易日历、复权因子与股票指标的适用范围为美股、港股和 A 股。

### 公司财务与基本面工具（29 个）

| 分类 | 工具 |
|---|---|
| 公司资料（2） | `get_company_profile`、`get_company_executives` |
| 财务报表（3） | `get_financials_latest`、`get_financials_annual`、`get_financials_ttm` |
| 业务分部（2） | `get_segments_latest`、`get_segments_history` |
| 估值与行业（6） | `get_valuation_latest`、`get_valuation_history`、`get_industry_peers`、`get_industry_distribution`、`get_industries_rank`、`get_industries_tree` |
| 分红、回购与资本行动（4） | `get_dividends`、`get_dividends_ttm`、`get_buyback`、`get_corporate_actions` |
| 股东与基金（4） | `get_shareholders_latest`、`get_shareholders_top`、`get_shareholder_detail`、`get_fund_holdings_latest` |
| 新闻与市场状态（3） | `get_company_news`、`get_news_detail`、`get_market_status` |
| 事件日历（5） | `get_report_calendar`、`get_dividend_calendar`、`get_split_calendar`、`get_ipo_calendar`、`get_other_calendar` |

财报工具覆盖利润表、资产负债表及现金流量表；TTM 支持利润表或现金流量表。最新与历史估值当前返回 PE。其他事件日历须传入 `category`。

### API Key 订阅工具（1 个）

`get_api_key_subscriptions()` 无查询参数，调用 `GET /v1/apikeys/subscriptions`，查询 Key 的套餐、状态、到期时间和剩余秒数，无需 TickDB 网站登录。保留 API 返回的账户级订阅响应；OAuth 授权页面仅展示本次提交 Key 的对应信息。到期判断使用响应中的服务器时间，缺失或 null 值不能视为零。

## 品种代码与调用约定

| 市场 | 示例 |
|---|---|
| 外汇 | `EURUSD`、`USDJPY` |
| 贵金属 | `XAUUSD`、`XAGUSD` |
| 指数 | `SPX`、`NDX`、`VIX` |
| 美股 | `AAPL.US`、`TSLA.US` |
| 港股 | `700.HK`、`9988.HK` |
| A 股 | `600519.SH`、`000858.SZ` |
| 中港期货 | 用 `get_available_symbols(type="futures")` 查询，如 `BU2609`、`HSI8888` |
| 加密货币 | `BTCUSDT`、`ETHUSDT` |

- K 线周期为 `1m`、`3m`、`5m`、`15m`、`30m`、`1h`、`2h`、`4h`、`1d`、`1w`、`1M`；历史最后一根 K 线可能仍在形成，复权历史可能变化。
- 股票信息最多 500 个代码；行情快照、最新 K 线和分时最多 50 个代码。逐笔成交查询默认 100 条、最多 1000 条。
- 分红、基金持仓与事件日历使用顶层 `page.next_cursor` 翻页，筛选条件须保持一致。日历省略日期时，后续页复用首次响应的日期范围。
- `get_trading_sessions` 可省略 `market` 以查询全部市场，交易时间按市场当地时区解释。交易日历单次跨度最多 31 天，开始日期须在最近一年内。
- 多数行情时间戳为毫秒，资金流向为秒，财务记录按日期或 RFC3339 字段解析。缺失值和 null 不等于零；日历分页复用首次响应的 `data.from` 与 `data.to`。
- 工具保留 API 响应包、分页与可选字段，同时检查 HTTP 状态及业务 `code`。服务不自动重试；按错误提示调整参数、权限或等待。
- 错误信息保留原始消息、权限提示、非 null 数据及上游提供的 `Retry-After`，HTTP 200 中的业务失败也会报错。仅将 HTTP 401 且业务 `code` 为 `Invalid or expired token` 的响应归一化为 `1001`，原始响应保留在 `TickDBAPIError.details`。
- 财务数据可用性受市场、披露时间及套餐限制。全市场行情快照不在本 MCP 工具范围内，按指定代码使用 `get_ticker`。

<a id="api-migration"></a>

## 升级指引

升级前查看 [更新记录](CHANGELOG.md)，确认功能与兼容性变化；升级后刷新 MCP 客户端的工具列表与参数结构。当前调用方式以本页工具说明和客户端发现的参数结构为准。

自部署升级与数据备份步骤见 [部署指南](DEPLOYMENT.md)。启用 OAuth 的服务须保留加密密钥、数据库及授权配置。

## 配置

从 `.env.example` 创建本地 `.env`，配置文件保持私有。依赖由 `pyproject.toml` 管理，包含 `mcp[cli]>=1.26.0,<2.0.0` 与 `cryptography>=46.0.0`。

| 变量 | 默认值 | 说明 |
|---|---|---|
| `TICKDB_API_KEY` | 空 | 服务器统一 Key；请求头 Key 优先 |
| `MCP_ACCESS_TOKEN` | 空 | 请求头接入 `/mcp` 的静态 Bearer 访问 Token；空时无此访问限制 |
| `MCP_TRANSPORT` | `streamable-http` | 可设为 `stdio` |
| `MCP_HOST` | `0.0.0.0` | HTTP 监听地址 |
| `MCP_PORT` | `8000` | HTTP 监听端口 |
| `MCP_STATELESS_HTTP` | `true` | 避免保留废弃的 HTTP 会话 |
| `MCP_SESSION_LOG_TTL_SECONDS` | `3600` | 生命周期日志会话 ID 保留秒数 |
| `MCP_SESSION_LOG_MAX_ENTRIES` | `1000` | 日志会话 ID 最大缓存条数 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `LOG_RETAIN_DAYS` | `7` | 轮转日志保留天数 |
| `LOG_DIR` | `logs` | 工作目录下的可写日志目录，也可使用绝对路径 |
| `OAUTH_ENABLED` | `false` | 启用独立的 `/oauth` 接口 |
| `OAUTH_PUBLIC_URL` | 空 | 公网 HTTPS origin，不带路径 |
| `OAUTH_ENCRYPTION_KEY` | 空 | 持久保存的 Fernet 加密密钥 |
| `OAUTH_DATABASE_PATH` | `data/oauth.sqlite3` | 持久化 SQLite 路径 |
| `OAUTH_REDIRECT_URIS` | `[]` | 精确回调白名单；示例配置含 ChatGPT 回调 |

日志写入 stderr，保证 stdio 协议的 stdout 可用；目录可写时同时输出每日轮转文件，文件日志不可用时继续使用 stderr。请求头接入的 Key 优先级为 `X-TickDB-Key` → `TICKDB_API_KEY`，stdio 使用环境 Key；OAuth 使用授权绑定的 Key。

也可用 `python -m pip install .` 常规安装，随后运行 `tickdb-mcp`。

## 项目结构

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

CI 位于父仓库的 [../.github/workflows/mcp-ci.yml](../.github/workflows/mcp-ci.yml)，执行代码检查、单元测试及 Docker 构建。

## Docker 部署

从仓库根目录进入 `mcp/` 后直接构建：

```bash
cd mcp
docker build -t tickdb-mcp:0.2.3 .
docker run -d --name tickdb-mcp -p 127.0.0.1:8000:8000 --env-file .env tickdb-mcp:0.2.3
```

构建直接使用本目录源码与 Dockerfile。客户端访问本机 `http://localhost:8000/mcp`；远程访问及 OAuth 部署使用 HTTPS 反向代理。启用 OAuth 时，按上方[自部署配置](#oauth-setup)挂载数据库持久化卷并保留同一加密密钥。

## 开发

在 `mcp/` 且已激活虚拟环境时执行：

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest tests/ -v
python examples/server_demo.py
```

单元测试使用模拟 API 响应和临时数据库，无需真实 API Key，不调用真实行情接口。`server_demo.py` 展示工具注册与模拟调用；实际客户端查询需要有效 Key。

## 文档

| 文档 | 链接 |
|---|---|
| 自部署指南 | [DEPLOYMENT.md](DEPLOYMENT.md) |
| 客户端接入 | [MCP_CLIENT_SETUP.md](MCP_CLIENT_SETUP.md) |
| 网页 OAuth 与持久化配置 | [本页 OAuth 配置](#oauth-setup) |
| 升级指引 | [本页升级指引](#api-migration) |
| 更新记录 | [CHANGELOG.md](CHANGELOG.md) |

## 许可证

MIT — 详见 [LICENSE](LICENSE)。
