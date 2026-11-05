<div align="center">

<img src="assets/logo.svg" alt="TickDB Logo" width="320">

# TickDB — Unified Real-time Market Data API for Forex, Stocks, Futures, Crypto

*One connection for Forex, Precious Metals, Indices, US Stocks, HK Stocks, A-Shares, China/Hong Kong Futures, and Crypto*

*开源工具集 · 完整 API 文档 + AI Skill + MCP 服务端实现*

[![MCP CI](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/mcp-ci.yml)
[![Docs Check](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/docs-quality.yml/badge.svg)](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/actions/workflows/docs-quality.yml)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

**语言版本:** [简体中文](README.md) • [繁體中文](README_tw.md) • [English](README_en.md)

[在线文档](https://docs.tickdb.ai) • [官网](https://tickdb.ai) • [AI 接入](#ai-access)

</div>

---

## 什么是 TickDB？

TickDB 是面向开发者、AI 代理和多市场金融应用的 **AI 原生实时行情数据 API**(AI-native real-time market data API)。

通过 **一次接入（one connection）**，无缝访问外汇（Forex）、贵金属（Precious Metals）、指数（Indices）、美股（US Stocks / NASDAQ / NYSE）、港股（HK Stocks）、A 股（A-Shares）、中国及香港期货（China/Hong Kong Futures）、加密货币（Cryptocurrency）等多个金融市场的实时与历史行情数据。

TickDB 专为需要**可靠、低延迟、可长期依赖**行情数据的开发者构建，帮助你**避免管理多个数据源、协议和供应商的复杂性**，专注于业务和策略本身。

> 支持逐笔成交（tick-by-tick trades）、盘口深度（order book / depth）、K 线（candlestick）等多种行情形式，
> 通过 REST API 与 WebSocket 接入，覆盖量化交易、AI Agent、实时行情系统、交易平台与数据分析场景。

---

## 快速接入

**本仓库提供完整源码**：[`SKILL/`](SKILL/)（AI Skill，含接口参考）· [`mcp/`](mcp/)（Python MCP 服务端，43 工具 · Dockerfile · 自动化测试 · CI · MIT）。可基于 [`mcp/`](mcp/) 自部署，也可使用公开托管端点 `mcp.tickdb.ai`。

选一种适合你的接入方式：

| 方式 | 适合 | 说明 |
|------|------|------|
| [Skill](#skill) | AI 对话即用，零配置 | npx 一键安装，AI 自动获取试用 Key |
| [MCP](#mcp) | AI 编码客户端 / 自部署开源 | 基于 [`mcp/`](mcp/) 自部署，或使用托管 OAuth / 请求头接入 |
| [CLI](#cli) | 终端 / 脚本 / AI Agent | npm 全局安装，命令行直查行情 |
| [REST API](#rest-api) | 应用集成 | 行情、期货与财务基本面 HTTP API |
| [WebSocket](#websocket) | 实时流式数据 | 低延迟订阅 ticker / depth / trade |

---

## 核心特性

- 统一接入：一套 API 覆盖外汇、贵金属、指数、美股、港股、A 股、中国及香港期货、加密货币
- 实时数据：基于 WebSocket 的流式推送，端到端延迟约 10-50ms
- 公司财务与基本面：REST API 提供美股、港股、A 股财报、PE 估值、营收构成、股东与公司事件查询
- AI 原生：官方提供 Skill / MCP / CLI 三档 AI 接入，AI Agent 与编码助手开箱即用
- 开发者友好：RESTful API + WebSocket，结构化 JSON 响应，完整文档与多语言示例
- 全球覆盖：覆盖股票、外汇、贵金属、指数、中国及香港期货与加密货币；品种及数量以产品目录返回为准
- 免费开始：无需信用卡，立即获取 API 密钥

---

## 典型使用场景

- 量化交易（Quantitative Trading）：算法与策略系统的实时行情数据源
- AI Agent / 编码助手：通过 Skill / MCP 让 AI 助手直接调用行情数据，自然语言驱动查询
- 行情看板：实时价格展示、资产与投资组合监控
- 交易应用：构建类似 TradingView 的行情界面与图表系统
- 数据分析与回测（Backtesting）：历史行情分析、策略回测与研究
- 金融服务集成：集成到现有交易平台或金融基础设施中
- 自部署 / 私有化：不想用托管端点？基于本仓库 [`mcp/`](mcp/) 代码自部署，完全控制数据流

---

<a id="rest-api"></a>
## 快速开始 — REST API

同一 REST API 提供行情与公司财务和基本面查询；财务接口包括财报、估值、股东持仓与分类财经日历。

[认证与基础信息](#rest-auth) · [行情核心 API](#market-api) · [公司财务与基本面 API](#fundamentals-api)

<a id="rest-auth"></a>
### 认证与基础信息

访问 [TickDB.ai](https://tickdb.ai) 注册账户，即可获取 API 密钥。

#### 身份认证

所有 HTTP API 请求都需要在请求头中包含 API 密钥：

```http
X-API-Key: YOUR_API_KEY
```

#### 基础 URL

```
https://api.tickdb.ai
```

#### API Key 订阅查询

- `GET /v1/apikeys/subscriptions` — 查询当前认证账户下 API Key 的套餐、状态与到期情况

#### 支持的市场

| 市场类型 | Symbol 格式示例 | 说明 |
|---------|----------------|------|
| 外汇（Forex / FX） | `GBPUSD` | 主要货币对（Base/Quote） |
| 贵金属（Precious Metals） | `XAUUSD` | 贵金属对美元（Commodity / USD） |
| 美股（US Stocks） | `AAPL.US` | NYSE / NASDAQ 上市股票 |
| 指数（Indices） | `SPX` | 股票指数（如标准普尔 500） |
| 港股（HK Stocks） | `700.HK` | 港交所上市证券 |
| A 股（A-Shares） | `600519.SH` | 上海 / 深圳交易所股票 |
| 中国期货（China Futures） | `AP8888` | `type=futures`、`market=CN`；具体合约及连续合约以目录为准 |
| 香港期货（HK Futures） | `HSI8888` | `type=futures`、`market=HK`；具体合约及连续合约以目录为准 |
| 加密货币（Cryptocurrency） | `BTCUSDT` | 加密资产交易对 |

期货支持实时行情、K 线、盘口与逐笔成交查询；K 线可返回持仓量 `open_interest`。代码须从 `/v1/symbols/available?type=futures` 查询，普通合约随交割月变化；`7777`、`8888`、`9999` 分别表示次主力、主力和加权连续，连续合约不代表实际可交割合约。上表仅展示代码格式，数据可用性取决于品种与 Key 权限。

<a id="market-api"></a>
### 行情核心 API

#### 通用行情

- `GET /v1/symbols/available` — 产品目录，含中国及香港期货
- `GET /v1/market/ticker` — 指定品种的实时行情快照
- `GET /v1/market/kline` — 历史 K 线
- `GET /v1/market/kline/latest` — 当前周期的实时 K 线
- `GET /v1/market/depth` — 买卖盘口深度
- `GET /v1/market/trades` — 逐笔成交（Tick-by-Tick Trades）

#### 全量行情快照

- `GET /v1/market/ticker/cn-stock` — A 股全量行情快照
- `GET /v1/market/ticker/hk-stock` — 港股全量行情快照
- `GET /v1/market/ticker/us-stock` — 美股全量行情快照

#### 股票行情与市场资讯

- `GET /v1/market/stock-info` — 股票基本信息
- `GET /v1/market/intraday` — 股票当日分时
- `GET /v1/market/kline/ex-factors` — 股票复权因子
- `GET /v1/market/calc-index` — 股票综合指标
- `GET /v1/market/capital-flow` — 股票资金流向
- `GET /v1/market/trading-sessions` — 市场交易时段
- `GET /v1/market/trade-days` — 市场交易日历

#### 获取 K 线（K-line）数据

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/kline?symbol=700.HK&interval=1h&limit=24"
```

#### 获取实时行情（Ticker）数据

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/ticker?symbols=AAPL.US,700.HK,BTCUSDT"
```

#### 获取盘口深度（Depth）数据

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/depth?symbol=AAPL.US"
```

#### 获取逐笔成交（Tick-by-Tick Trades）数据

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/trades?symbol=AAPL.US&limit=20"
```

#### 查询可用交易品种

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/symbols/available?market=HK&limit=10"
```

查询中国及香港期货目录：

```bash
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/symbols/available?type=futures&market=CN&limit=10"
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/symbols/available?type=futures&market=HK&limit=10"
```

<a id="fundamentals-api"></a>
### 公司财务与基本面 API

财务与基本面提供 29 个 HTTP 端点，覆盖美股、港股和 A 股；直接使用同一 Base URL 与 `X-API-Key`，无需经过 MCP。数据覆盖取决于品种、披露时间和 Key 的接口及市场权限。

#### 公司概况

- `GET /v1/fundamentals/profile` — 公司资料
- `GET /v1/fundamentals/executives` — 高管与董事
- `GET /v1/fundamentals/segments/latest` — 最新业务与地区营收构成
- `GET /v1/fundamentals/segments/history` — 历史营收构成

#### 财务报表

- `GET /v1/fundamentals/financials/latest` — 最新财报：利润表、资产负债表、现金流量表
- `GET /v1/fundamentals/financials/annual` — 年度财务报表
- `GET /v1/fundamentals/financials/ttm` — TTM 利润表与现金流量表

#### 估值与行业

- `GET /v1/fundamentals/valuation/latest` — 最新 PE 估值
- `GET /v1/fundamentals/valuation/ts` — 历史 PE 时序
- `GET /v1/fundamentals/industry/peers` — 同业公司对比
- `GET /v1/fundamentals/industry/dist` — 个股行业指标分布
- `GET /v1/fundamentals/industries/rank` — 市场行业排行
- `GET /v1/fundamentals/industries/tree` — 行业分类层级

#### 分红与公司行动

- `GET /v1/fundamentals/dividends` — 历史与已知未来分红事件
- `GET /v1/fundamentals/dividends/ttm` — 过去 12 个月每股现金股息
- `GET /v1/fundamentals/buyback` — 公司回购
- `GET /v1/fundamentals/corp-actions` — 公司资本行动

#### 股东与基金持仓

- `GET /v1/fundamentals/shareholders/latest` — 最新股东持仓
- `GET /v1/fundamentals/shareholders/top` — 多个报告期的主要股东
- `GET /v1/fundamentals/shareholders/detail` — 股东持仓与交易详情
- `GET /v1/fundamentals/fund-holdings/latest` — 持有该股票的基金

#### 财经日历

- `GET /v1/fundamentals/calendar/report` — 财报与业绩日历
- `GET /v1/fundamentals/calendar/dividend` — 分红日历
- `GET /v1/fundamentals/calendar/split` — 拆股与合股日历
- `GET /v1/fundamentals/calendar/ipo` — 发行与上市日历
- `GET /v1/fundamentals/calendar/other` — 其他分类事件

#### 新闻与市场状态

- `GET /v1/fundamentals/news` — 公司新闻列表
- `GET /v1/fundamentals/news/{news_id}` — 新闻正文或节选
- `GET /v1/fundamentals/market/status` — 美股、港股、A 股市场状态

详细参数、响应字段与错误码见[官方 API 文档](https://docs.tickdb.ai/zh-Hans/index)。

#### 查询财务报表

以下示例分别查询最近四期利润表、最近三年资产负债表与 TTM 现金流量表：

```bash
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/financials/latest?symbol=AAPL.US&type=stock&kind=IS&n=4"
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/financials/annual?symbol=AAPL.US&type=stock&kind=BS&n=3"
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/financials/ttm?symbol=AAPL.US&type=stock&kind=CF"
```

#### 查询 PE 估值与分红

```bash
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/valuation/latest?symbol=AAPL.US&type=stock"
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/dividends?symbol=AAPL.US&type=stock&limit=20"
```

#### 查询分类财报日历

```bash
curl -H "X-API-Key: YOUR_API_KEY" "https://api.tickdb.ai/v1/fundamentals/calendar/report?market=US&symbols=AAPL.US&limit=100"
```

---

<a id="websocket"></a>
## 实时订阅 — WebSocket

低延迟（10-50ms）的流式数据推送，适合实时行情看板、量化策略与 Agent 自动化场景。

### 普通行情订阅

- [`ticker`](https://docs.tickdb.ai/zh-Hans/websocket/ticker) — 指定品种的实时行情
- [`depth`](https://docs.tickdb.ai/zh-Hans/websocket/depth) — 买卖盘口更新
- [`trade`](https://docs.tickdb.ai/zh-Hans/websocket/trade) — 逐笔成交实时推送

### 全量行情订阅

- [`CN_Stock`](https://docs.tickdb.ai/zh-Hans/websocket/ticker_cn_stock) — A 股全量行情
- [`HK_Stock`](https://docs.tickdb.ai/zh-Hans/websocket/ticker_hk_stock) — 港股全量行情
- [`US_Stock`](https://docs.tickdb.ai/zh-Hans/websocket/ticker_us_stock) — 美股全量行情

### 连接控制与使用说明

- [`ping / pong`](https://docs.tickdb.ai/zh-Hans/websocket/ping) — 连接心跳检测
- [`unsubscribe`](https://docs.tickdb.ai/zh-Hans/websocket/ticker) — 取消订阅

全量行情需在连接时协商 `permessage-deflate`；消息格式、心跳、断线重连与恢复订阅见[官方连接指南](https://docs.tickdb.ai/zh-Hans/websocket/websocket_quickstart)。

#### 多市场订阅与压缩（Node.js）

以下示例使用 Node.js 的 `ws` 库。先执行 `npm install ws`，设置环境变量 `TICKDB_API_KEY`，将代码保存为 `market-stream.cjs` 后运行 `node market-stream.cjs`。订阅品种和全市场集合须符合 Key 权限，代码以产品目录实际返回为准；只需普通行情时，将 `fullMarkets` 设为空数组。

`perMessageDeflate` 直接在 `new WebSocket` 中启用，压缩在握手阶段协商，`ws` 自动解压消息。示例同时处理普通单条消息与全量快照、增量更新的数组消息。浏览器原生 WebSocket 不接受该选项。

```javascript
const WebSocket = require('ws');

const apiKey = process.env.TICKDB_API_KEY;
if (!apiKey) throw new Error('Set TICKDB_API_KEY before running this example');

const tickerSymbols = [
    'EURUSD', // 外汇
    'XAUUSD', // 贵金属
    'SPX', // 指数
    'AAPL.US', // 美股
    '700.HK', // 港股
    '600519.SH', // A 股
    'AP8888', // 中国期货
    'HSI8888', // 香港期货
    'BTCUSDT', // 加密货币
];
const depthSymbols = ['AAPL.US', '700.HK', '600519.SH', 'AP8888', 'BTCUSDT'];
const tradeSymbols = [...depthSymbols, 'HSI8888'];
const fullMarkets = ['CN_Stock', 'HK_Stock', 'US_Stock'];

const endpoint = new URL('wss://api.tickdb.ai/v1/realtime');
endpoint.searchParams.set('api_key', apiKey);
const ws = new WebSocket(endpoint, {
    perMessageDeflate: true // 在连接握手时协商 permessage-deflate 压缩，ws 自动解压。
});

ws.on('open', () => {
    if (fullMarkets.length && !ws.extensions.includes('permessage-deflate')) {
        console.error('Full-market data requires permessage-deflate');
        ws.close();
        return;
    }

    // 混合产品类型时省略 type；有歧义的代码按类型另行订阅。
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'ticker', symbols: tickerSymbols }
    }));
    // 盘口示例：美股、港股、A 股、中国期货与加密货币。
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'depth', symbols: depthSymbols }
    }));
    // 逐笔成交示例额外包含香港期货。
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: { channel: 'trade', symbols: tradeSymbols }
    }));

    // 全量与个股 ticker 独立订阅，可同时使用，不影响 depth 和 trade。
    if (fullMarkets.length) {
        ws.send(JSON.stringify({
            cmd: 'subscribe',
            data: { universes: fullMarkets, channels: ['ticker'] }
        }));
    }
});

ws.on('message', (raw) => {
    let payload;
    try {
        payload = JSON.parse(raw.toString());
    } catch {
        console.error('Received an invalid JSON message');
        return;
    }

    // 普通推送为对象；全量快照和增量更新为数组。
    for (const message of Array.isArray(payload) ? payload : [payload]) {
        if (['ticker', 'depth', 'trade'].includes(message.cmd)) {
            console.log(message.cmd, message.data);
        } else if (message.cmd === 'error') {
            console.error('Subscription error:', message.code, message.message);
        }
    }
});

ws.on('error', () => {
    console.error('WebSocket connection failed');
});
```

---

<a id="ai-access"></a>
## AI 接入

TickDB 是 **AI-native** 行情数据 API，提供三档原生接入方式，覆盖从零配置对话到生产级深度集成的全场景需求。

<a id="skill"></a>
### Skill — 对话即用

安装后 AI 自动获取试用 Key，无需注册即可查询清单中的 62 个品种：

```bash
npx clawhub@latest install tickdb-market-data
```

或将本仓库完整的 [`SKILL/` 目录](SKILL/)复制到客户端的 Skill 目录，并命名为 `tickdb-market-data`，保留 `SKILL.md` 和 `references/`。支持行情、复权 K 线、期货、财务基本面及 API Key 套餐与到期查询；实际可用范围取决于 Key 权限。

<a id="mcp"></a>
### MCP — 永久集成

本仓库 MCP 与 Skill 覆盖 43 个 REST 端点，不包含上述三市场全量行情与 WebSocket 能力。

一次配置，让 AI 助手通过 MCP 服务使用 **43 个工具：13 个行情工具、29 个公司财务与基本面工具、1 个 API Key 订阅查询工具**。

| 能力 | 用户可查询的内容 |
|------|------------------|
| 行情与股票（13 工具） | 实时报价、复权 K 线、复权因子、买卖盘、逐笔成交、资金流向与期货品种 |
| 公司财务与基本面（29 工具） | 公司资料、财报、PE 估值、行业、股东持仓、分红回购、新闻与分类财经日历 |
| API Key 订阅（1 工具） | 当前 Key 所属账户返回的套餐、状态、到期时间与剩余时长 |

行情覆盖外汇、贵金属、指数、美股、港股、A 股、中港期货和加密货币；公司财务与基本面覆盖美股、港股和 A 股，具体可用性取决于品种、披露时间及套餐权限。

**自部署：** 使用 [`mcp/`](mcp/) 中的 Python 源码或 Dockerfile，参见下方部署指南。网页 OAuth 默认关闭，按指南配置后可启用。

**本地启动（Python 3.11+）：** 在 Linux 终端中从仓库根目录执行；首次安装复制 `.env`，升级时保留已有配置。

```bash
cd mcp
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cp .env.example .env
# 保持服务器 Key 为空，由客户端通过 X-TickDB-Key 提供自己的 Key
python main.py
```

服务默认仅监听本机 `127.0.0.1:8000`，端点为 `http://localhost:8000/mcp`；客户端通过 `X-TickDB-Key` 提供自己的 Key。若要使用服务器共享 Key，须同时配置 `MCP_ACCESS_TOKEN`，客户端携带对应 Bearer；匿名 HTTP 请求不能借用服务器 Key。Docker 和 HTTPS OAuth 配置见[自部署指南](mcp/DEPLOYMENT.md)。

**公开托管端点（可选，无需自部署）：**

- **网页 OAuth 接入（ChatGPT / Claude）：** 服务器 URL 使用 `https://mcp.tickdb.ai/oauth`，选择 OAuth，在 TickDB 授权页验证自己的 API Key 并确认授权。
- **请求头接入（AI 编码客户端）：** 使用 `https://mcp.tickdb.ai/`，通过 `X-TickDB-Key` 传入 API Key，配置如下。

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

各客户端配置及 Claude Desktop 本地 stdio 模式见下方接入指南。

**MCP 服务端已开源**，代码位于本仓库 [`mcp/`](mcp/) 目录。

**mcp/ 概览**：v0.2.4 · 43 个 MCP 工具 · Python 3.11+ · Docker 就绪 · 自动化测试 · MIT 许可证 · CI 持续验证

| 文档 | 链接 |
|------|------|
| 客户端接入配置 | [mcp/MCP_CLIENT_SETUP.md](mcp/MCP_CLIENT_SETUP.md) |
| 部署说明（自部署） | [mcp/DEPLOYMENT.md](mcp/DEPLOYMENT.md) |
| MCP 完整文档 | [mcp/README.md](mcp/README.md) |
| 网页 OAuth 接入与自部署配置 | [MCP OAuth 配置](mcp/README.md#oauth-setup) |
| 版本更新记录 | [MCP Changelog](mcp/CHANGELOG.md) |

<a id="cli"></a>
### CLI — 终端 & Agent

```bash
npm install -g tickdb
tickdb config set-key YOUR_API_KEY
tickdb ticker BTCUSDT,XAUUSD
```

详见 [官网 AI 接入页面](https://tickdb.ai/ai-tools)。

---

## 在线文档

完整的 API 参考、参数说明、以及可直接运行的示例请求：

- **Docs**: https://docs.tickdb.ai
- **官网**: https://tickdb.ai
- **AI 接入页面**: https://tickdb.ai/ai-tools

---

## 社区和支持

- GitHub Issues：[报告错误或请求功能](https://github.com/TickDB/tickdb-unified-realtime-marketdata-api/issues)
- 技术支持：[Telegram](https://t.me/TickDB_Support)
- 邮箱：[support@tickdb.ai](mailto:support@tickdb.ai)
- 文档：[docs.tickdb.ai](https://docs.tickdb.ai)

---

## 许可证

本文档采用 [MIT 许可证](LICENSE)。
