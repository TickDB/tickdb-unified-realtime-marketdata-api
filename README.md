<div align="center">

![TickDB Logo](assets/images/logo.png)

*一个连接，覆盖外汇、贵金属、指数、美股、港股、A股、加密货币*

[![API Status](https://img.shields.io/badge/API-Live-green)](https://tickdb.ai)
[![WebSocket](https://img.shields.io/badge/WebSocket-Supported-blue)](https://tickdb.ai)
[![Latency](https://img.shields.io/badge/Latency-10--50ms-blue)](#)
[![Docs](https://img.shields.io/badge/Docs-docs.tickdb.ai-brightgreen)](https://docs.tickdb.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**语言版本:** [🇨🇳 简体中文](README.md) • [🇹🇼 繁體中文](README_tw.md) • [🇺🇸 English](README_en.md)

[📚 在线文档](https://docs.tickdb.ai) • [🌐 官网](https://tickdb.ai)

</div>

---

## 🎯 什么是 TickDB？

TickDB 是一个**面向开发者的统一实时行情数据 API** 服务。

通过 **一次接入（one connection）**，即可无缝访问多个金融市场的实时与历史行情数据。

TickDB 专为需要**可靠、低延迟、可长期依赖**行情数据的开发者而构建， 

帮助你**避免管理多个数据源、协议和供应商的复杂性**，专注于业务和策略本身。

> TickDB 提供覆盖外汇、贵金属、股票、指数、加密货币等市场的实时金融行情数据服务，
> 支持 tick 级成交数据、盘口深度（order book）、K 线（candlestick）等多种行情形式，
> 可通过 REST API 与 WebSocket 接入，适用于量化交易、实时行情系统、交易平台与数据分析场景。


---

### ✨ 核心特性

- **🔌 统一接入** - 一套 API 覆盖多个市场和资产类别
- **⚡ 实时数据** - 基于 WebSocket 的流式推送，端到端延迟约 50ms
- **🌍 多市场支持** - 外汇、贵金属、指数、美股、港股、A股、加密货币
- **🛠️ 开发者友好** - RESTful API + WebSocket，示例丰富、文档完整

### 🏗️ 典型使用场景

- **量化交易** - 作为算法与策略系统的实时行情数据源
- **行情看板** - 实时价格展示、资产与投资组合监控
- **交易应用** - 构建类似 TradingView 的行情界面与图表系统
- **数据分析与回测** - 历史行情分析、策略回测与研究
- **金融服务集成** - 集成到现有交易平台或金融基础设施中

---

## 🚀 快速开始

### 1. 注册并获取 API 密钥

访问 [TickDB.ai](https://tickdb.ai) 注册账户，即可获取 API 密钥。

#### 🔑 身份认证

所有 HTTP API 请求都需要在请求头中包含 API 密钥：

```http
X-API-Key: YOUR_API_KEY
```

#### 🌐 基础 URL

```
https://api.tickdb.ai
```

#### 📋 HTTP API 核心接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/v1/market/kline` | GET | 历史 K 线/蜡烛图数据 |
| `/v1/market/ticker` | GET | 实时行情数据 |
| `/v1/market/depth` | GET | 订单簿深度数据 |
| `/v1/market/trades` | GET | 最近交易历史 |

#### 🏪 支持的市场

| 市场类型 | Symbol 格式示例 | 说明 |
|---------|----------------|------|
| 外汇（FX） | `GBPUSD` | 主要货币对（Base/Quote） |
| 贵金属 | `XAUUSD` | 贵金属对美元（Commodity / USD） |
| 美股 | `AAPL.US` | NYSE / NASDAQ 上市股票 |
| 指数 | `SPX` | 股票指数（如标准普尔 500） |
| 港股 | `700.HK` | 港交所上市证券 |
| A 股 | `600519.SH` | 上海 / 深圳交易所股票 |
| 加密货币 | `BTCUSDT` | 加密资产交易对 |

### 2. 获取 K 线数据

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/kline?symbol=700.HK&interval=1h&limit=24"
```

### 3. 获取实时行情（ticker）数据

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/ticker?symbols=AAPL.US,700.HK,BTCUSDT"
```

### 4. 获取盘口深度（depth）数据

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/depth?symbol=AAPL.US&limit=10"
```

### 5. 获取成交记录（trades）数据

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/market/trades?symbols=AAPL.US&limit=20"
```

### 6. 查询可用交易品种

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://api.tickdb.ai/v1/symbols/available?market=HK&limit=10"
```

### 7. 使用WebSocket 订阅实时数据

#### 支持的频道

- `ticker` - 实时价格更新
- `depth` - 订单簿变化
- `trade` - 实时交易执行

```javascript
const ws = new WebSocket('ws://api.tickdb.ai/v1/realtime?api_key=YOUR_API_KEY');

ws.onopen = () => {
    // 订阅实时价格
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: {
            channel: 'ticker',
            symbols: ['BTCUSDT']
        }
    }));

    // 订阅实时订单簿变化
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: {
            channel: 'depth',
            symbols: ['BTCUSDT']
        }
    }));

    // 订阅实时成交数据
    ws.send(JSON.stringify({
        cmd: 'subscribe',
        data: {
            channel: 'trade',
            symbols: ['BTCUSDT']
        }
    }));
};
```

### 📚 在线文档（推荐）

完整的 API 参考、参数说明、以及可直接运行的示例请求，请访问在线文档：

- **Docs**: https://docs.tickdb.ai

---

## 🚀 开发者体验

### 简单接入
- **免费开始** - 无需信用卡，立即获取 API 密钥
- **完整文档** - 详细的 API 参考和代码示例
- **多语言支持** - JavaScript、Python 等示例代码
- **支持渠道** - Telegram 社区与邮件支持

### 强大功能
- **统一接口** - 一套 API 覆盖多个市场
- **实时数据** - WebSocket 流式传输，延迟约10-50ms
- **历史数据** - 完整的 K 线和交易历史
- **高可用性** - 99.9% 服务可用性保证

### 快速上手
1. **注册账户** - 访问 [TickDB.ai](https://tickdb.ai)
2. **获取 API 密钥** - 在控制面板生成密钥
3. **运行示例** - 使用我们的代码示例快速测试
4. **构建应用** - 集成到您的项目中

[立即开始 →](https://tickdb.ai)

---

## 🤝 社区和支持

- **GitHub Issues** - [报告错误或请求功能](https://github.com/tickdb/tickdb-unified-realtime-marketdata-api/issues)
- **技术支持** - [Telegram](https://t.me/TickDB_Support)
- **邮箱** - [support@tickdb.ai](mailto:support@tickdb.ai)
- **文档** - [docs.tickdb.ai](https://docs.tickdb.ai)


---

## 📄 许可证

本文档采用 [MIT 许可证](LICENSE)。

</div>