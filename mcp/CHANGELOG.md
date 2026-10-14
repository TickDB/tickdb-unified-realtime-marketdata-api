# 更新记录

**语言：** **简体中文** · [繁體中文](docs/tw/CHANGELOG.md) · [English](docs/en/CHANGELOG.md)

## v0.2.3 — 2026-10-15

相对于 v0.1.3 的变化。

### 新增

- 工具扩展至 43 个：13 个行情工具、29 个公司财务与基本面工具、1 个 API Key 订阅工具。
- 新增公司概况、高管、财务报表、营收分部、估值、行业数据、股息、回购、股东与基金持仓、新闻、公司事件及分类财经日历查询。
- 新增股票复权因子、K 线 `adjust`、股息 TTM、新闻详情、市场状态及 `get_api_key_subscriptions`；更新中港期货覆盖范围。
- 新增可选的 OAuth 网页授权，支持 S256 PKCE、动态客户端注册、refresh token 轮换与撤销；授权确认页支持简体中文、繁体中文和英文。
- OAuth 通过用户验证并明确授权的 TickDB API Key 查询数据；Key 绑定加密存储于持久化 SQLite。
- 提供三语言部署与客户端接入指南，以及工具和 HTTP 传输的离线测试。

### 修复与改进

- 更新 REST 端点和参数映射、批量查询上限、逐笔成交笔数限制、分页及时间戳处理。
- 保留响应结构、HTTP 状态、业务错误与 `Retry-After`，识别 HTTP 200 中的业务失败，并支持 gzip 响应。
- 完善 OAuth 的 CSRF、同源提交、精确回调白名单与 issuer 识别；授权确认页仅展示提交的 Key 对应的脱敏信息和订阅。
- 修复 Python wheel 的 `tickdb-mcp` 入口模块打包及 Docker 源码构建，支持独立安装和自部署。
- 日志输出至 stderr，避免干扰 stdio JSON-RPC；通过 `LOG_DIR` 配置日志目录，无法写入文件时继续输出至 stderr。

### 升级注意事项

- 刷新客户端工具列表。移除 `get_kline_intervals`、`get_financial_fields` 与原 `get_financial_calendar`；财经日历改用分类工具。
- 移除财务 `fields`、历史估值 `metric` 和买卖盘 `limit` 参数；按代号查询的基本面工具要求 `symbol`。详见 [升级指引](README.md#api-migration)。
- OAuth 默认关闭；原 `/mcp` 请求头接入与 stdio 保留。启用 OAuth 时使用 `/oauth` 工具入口、公网 HTTPS 与持久化数据库，升级时保留加密密钥、数据库和有效授权。详见 [OAuth 自部署](README.md#oauth-setup)。
- 依赖要求 MCP SDK `>=1.26.0,<2.0.0` 与 `cryptography>=46.0.0`。

## v0.1.3 - 2026-06-15

### 修正

- 透过 `MCP_STATELESS_HTTP=true` 默认启用无状态 Streamable HTTP，避免在内存中保留已弃用的 MCP 会话。
- 为中间件的会话生命周期日志加入 TTL 与最大条目数限制，避免重新连接时 `_known_sessions` 无限增长。

### 新增

- 新增 `MCP_SESSION_LOG_TTL_SECONDS` 与 `MCP_SESSION_LOG_MAX_ENTRIES`，配置会话生命周期日志的保留策略。
- 新增会话生命周期缓存边界的单元测试。

---

## v0.1.2 — 2026-05-20

### 新增

- **结构化日志**覆盖完整请求生命周期：
  - 启动：服务器配置摘要（传输、端口、认证状态、API Key 状态）
  - 中间件：请求 IP、方法、路径、Key 来源与认证结果
  - 客户端：API 呼叫路径、参数、Key 来源、响应状态与耗时
  - 错误：超时、网络错误、API 错误码与完整上下文
- **会话生命周期日志**：追踪 `SESSION_INIT`、`SESSION_CREATED`、`SESSION_REUSE`、`SESSION_ATTACH`、`SESSION_NOT_FOUND` 事件，关联 Key 与会话 ID。
- **每日轮换日志文件**：`logs/tickdb_mcp.log` 自动每日轮换，透过 `LOG_RETAIN_DAYS` 配置保留天数（默认 7 天）。
- **`LOG_LEVEL` 环境变数**：控制日志详细程度（DEBUG／INFO／WARNING／ERROR，默认 INFO）。
- **`LOG_RETAIN_DAYS` 环境变数**：控制轮换日志的保留天数。
- **API Key 脱敏**：日志仅显示前 4 个与后 4 个字符。
- **按 Key 关联日志**：请求、响应与错误日志均包含脱敏后的 API Key，便於在并发环境中追踪用户的完整呼叫链。
- **请求计时**：每次 TickDB API 呼叫均记录毫秒精度的耗时。
- **明确的错误分类**：分别记录 TIMEOUT、NETWORK_ERROR 与 API 错误码。

### 修正

- **Hermes MCP 客户端兼容性**：自动修正未同时发送 `application/json` 与 `text/event-stream` 的客户端的 `Accept` 请求头，解决阻止 SSE 会话建立的 406 Not Acceptable 错误。

---

## v0.1.1 — 2026-05-14

### 新增

- 为 9 个工具新增 **`type` 参数**，解决代码歧义：`get_ticker`、`get_kline`、`get_kline_latest`、`get_order_book`、`get_recent_trades`、`get_stock_info`、`get_intraday`、`get_market_metrics`、`get_capital_flow`。
- 可用值：`stock`、`crypto`、`forex`、`indices`、`futures`。
- 仅在同一代码对应多个产品类型时必填，例如中国市场的 `000001` 同时代表平安银行股票与上证指数。
- 唯一代码（如 `AAPL.US`、`BTCUSDT`）仍可省略 `type`。

### 修正

- 解决中国市场股票与指数共用代码时的 `AMBIGUOUS_SYMBOL` 错误。

---

## v0.1.0 — 2026-05-01

### 首次发布

- **13 个 MCP 工具**覆盖实时与历史行情：
  - `get_ticker`：实时行情快照
  - `get_kline` / `get_kline_latest` / `get_kline_intervals`：K 线数据
  - `get_order_book`：买卖盘深度
  - `get_recent_trades`：最新逐笔成交
  - `get_available_symbols`：查询 37,527+ 个可交易代码
  - `get_stock_info`：股票基本信息
  - `get_intraday`：分钟级分时数据
  - `get_trading_sessions`：市场交易时段
  - `get_trade_days`：交易日历
  - `get_market_metrics`：估值与市场指标
  - `get_capital_flow`：资金流向分析
- **资产覆盖**：外汇、贵金属、指数、美股、港股、A 股与加密货币。
- **两层 API Key 解析**：每次请求的 `X-TickDB-Key` 请求头 → `TICKDB_API_KEY` 环境变数。
- **传输**：Streamable HTTP（远端）与 stdio（本地 Claude Desktop）。
- **认证中间件**：透过 `MCP_ACCESS_TOKEN` 提供可选的 Bearer token 存取控制。
- **Docker 支持**：可用於正式部署的 Dockerfile。
