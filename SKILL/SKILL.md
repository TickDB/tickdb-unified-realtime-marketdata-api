---
name: tickdb-market-data
description: >
  TickDB 统一实时行情数据 API。使用此 skill 获取外汇、贵金属、指数、美股、港股、A股、加密货币的实时和历史行情数据。
  触发场景：
  - 用户请求行情数据（"BTC现在多少钱"、"帮我查K线"、"获取股票数据"）
  - 用户询问"API Key怎么申请"、"在哪里注册"、"怎么获取key"、"我没有key"
  - 用户说"帮我获取XX行情"时，需要先检查是否已提供API Key
  - 用户返回401错误时，提示检查或重新申请API Key
---

# TickDB Market Data API

统一实时行情数据 API，通过单一连接访问多个金融市场的实时与历史行情数据。

**官网**: https://tickdb.ai  
**文档**: https://docs.tickdb.ai

## 基础信息

- **Base URL**: `https://api.tickdb.ai`
- **认证方式**: API Key（放在 HTTP Header `X-API-Key` 中）
- **时间戳单位**: 毫秒（ms），UTC 时区
- **响应格式**: JSON

## API Key 检查流程

**重要**：每次用户请求行情数据时，必须先检查是否已提供 API Key。

```
用户请求行情数据
    │
    ├─ 对话中已有 API Key？
    │   ├─ 是 → 直接调用 API
    │   └─ 否 → 请用户提供，或引导申请
    │
    └─ API 返回 401 错误？
        └─ 是 → 提示用户检查 API Key 或重新申请
```

**AI 执行步骤**：
1. 用户说"获取XXX行情"、"查一下XXX"等任何行情请求
2. 检查对话历史中用户是否已提供 API Key
3. 如未提供：
   - 询问用户"请提供您的 TickDB API Key"
   - 同时告知申请方式（见下方）
4. 如用户提供 Key 后，调用 API
5. 如返回 401 错误：
   - 提示"API Key 无效或已过期，请检查或前往 https://tickdb.ai 重新申请"

## API Key 申请指引

**申请地址**：https://tickdb.ai

**申请步骤**：
1. 访问 https://tickdb.ai
2. 点击"免费开始"或"注册"
3. 填写邮箱、密码完成注册
4. 登录后在控制面板生成 API Key

**费用说明**：
- ✅ **免费开始** - 无需信用卡，立即获取 API 密钥
- 具体订阅计划请查看官网定价

**支持渠道**：
- 官网：https://tickdb.ai
- 文档：https://docs.tickdb.ai
- 邮箱：support@tickdb.ai
- Telegram：https://t.me/TickDB_Support

## AI 调用指南

当用户询问以下问题时，直接调用对应接口：

| 用户意图 | 调用接口 | 示例请求 |
|----------|----------|----------|
| "现在价格多少" / "实时行情" | `GET /v1/market/ticker` | `symbols=BTCUSDT` |
| "K线" / "蜡烛图" / "技术分析" | `GET /v1/market/kline` | `symbol=BTCUSDT&interval=1h` |
| "当前K线" / "实时K线" | `GET /v1/market/kline/latest` | `symbols=BTCUSDT&interval=5m` |
| "买卖盘" / "订单簿" / "深度" | `GET /v1/market/depth` | `symbol=BTCUSDT&limit=20` |
| "最近成交" / "成交记录" | `GET /v1/market/trades` | `symbol=BTCUSDT&limit=20` |
| "支持哪些品种" / "有哪些股票" | `GET /v1/symbols/available` | `market=CRYPTO` |
| "股票信息" / "基本面" / "公司数据" | `GET /v1/market/stock-info` | `symbols=700.HK,AAPL.US` |
| "分时" / "当日走势" / "分钟数据" | `GET /v1/market/intraday` | `symbols=700.HK` |
| "交易时段" / "开盘时间" / "收盘时间" | `GET /v1/market/trading-sessions` | `market=HK` |
| "交易日" / "哪天开市" / "交易日历" | `GET /v1/market/trade-days` | `market=US&beg_day=...&end_day=...` |
| "市场指标" / "PE" / "市盈率" / "市值" | `GET /v1/market/calc-index` | `symbols=AAPL.US` |
| "资金流向" / "大单流入" / "主力资金" | `GET /v1/market/capital-flow` | `symbol=700.HK` |

## 响应数据提取

### 行情快照 - 提取价格和涨跌
```javascript
// 最新价
data[0].last_price
// 24h涨跌额
data[0].price_change_24h
// 24h涨跌幅 (百分比)
data[0].price_change_percent_24h
// 24h最高/最低
data[0].high_24h, data[0].low_24h
// 成交量
data[0].volume_24h
```

### K线数据 - 提取OHLCV
```javascript
// 最新一根K线
const latest = data.klines[data.klines.length - 1]
// 开盘/最高/最低/收盘
latest.open, latest.high, latest.low, latest.close
// 成交量/成交额
latest.volume, latest.quote_volume
// K线时间 (毫秒转日期)
new Date(latest.time)
```

### 订单簿 - 提取买卖盘
```javascript
// 买盘 (价格从高到低)
data.bids[0]  // 最高买价, data.bids[0][0] = 价格, data.bids[0][1] = 数量
// 卖盘 (价格从低到高)
data.asks[0]  // 最低卖价, data.asks[0][0] = 价格, data.asks[0][1] = 数量
```

### 股票信息 - 提取基本面
```javascript
data[0].name_cn       // 中文名称
data[0].exchange      // 交易所
data[0].lot_size      // 每手股数
data[0].eps_ttm       // 市盈率(TTM)
data[0].bps           // 每股净资产
data[0].dividend_yield // 股息率
```

### 市场指标 - 提取估值数据
```javascript
data[0].pe_ttm_ratio        // 市盈率
data[0].pb_ratio            // 市净率
data[0].total_market_value // 总市值
data[0].turnover_rate       // 换手率
data[0].capital_flow        // 资金流向
```

## 时间参数处理

| 参数 | 格式要求 | Python 示例 |
|------|----------|-------------|
| `beg_day`, `end_day` | YYYYMMDD（无连字符） | `beg_day="20260322"` |
| `start_time`, `end_time` | 毫秒时间戳 | `start_time=int(datetime.timestamp()*1000)` |
| `timestamp` (返回) | 毫秒，需除以1000转秒 | `datetime.fromtimestamp(ts/1000)` |

## 支持市场

| 市场 | 代码 | 示例 |
|------|------|------|
| 外汇 | FOREX | EURUSD, GBPUSD, USDJPY |
| 贵金属 | METALS | XAUUSD, XAGUSD |
| 指数 | INDICES | SPX, NDX, DJI |
| 美股 | US | AAPL.US, TSLA.US, MSFT.US |
| 港股 | HK | 700.HK, 9988.HK, 3690.HK |
| A股 | CN | 000001.SH, 000001.SZ |
| 加密货币 | CRYPTO | BTCUSDT, ETHUSDT, ADAUSDT |

## K线周期

| 类型 | 周期值 |
|------|--------|
| 分钟 | 1m, 3m, 5m, 15m, 30m |
| 小时 | 1h, 2h, 4h |
| 天 | 1d |
| 周 | 1w |
| 月 | 1M |

---

# API 接口参考

## 行情快照 (Ticker)

获取一个或多个交易品种的实时市场行情数据。

**端点**: `GET /v1/market/ticker`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbols | string | 是 | 交易品种代码，多个用逗号分隔，最多50个 |

**返回字段**:
| 字段 | 说明 |
|------|------|
| symbol | 交易产品 |
| last_price | 最新成交价 |
| volume_24h | 24小时成交量 |
| high_24h | 24小时最高价 |
| low_24h | 24小时最低价 |
| price_change_24h | 24小时价格变化 |
| price_change_percent_24h | 24小时价格变化百分比 |
| timestamp | 数据时间戳（毫秒，UTC） |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/ticker?symbols=XAUUSD,TSLA.US,BTCUSDT" \
  -H "X-API-Key: YOUR_API_KEY"
```

**示例响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "symbol": "XAUUSD",
      "last_price": "2034.50",
      "volume_24h": "125689",
      "high_24h": "2045.00",
      "low_24h": "2028.30",
      "price_change_24h": "-5.50",
      "price_change_percent_24h": "-0.27",
      "timestamp": 1773292807000
    }
  ]
}
```

---

## 历史 K 线 (Kline Historical)

获取已结束时间周期的历史K线数据。

**使用场景**：
- 策略回测
- 技术指标计算（如 MACD、RSI、布林带）
- 历史数据分析
- 数据归档存储

**注意**：如需当前正在形成的K线，使用 `/v1/market/kline/latest`

**端点**: `GET /v1/market/kline`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | string | 是 | 交易产品代码 |
| interval | string | 是 | K线周期：1m, 5m, 15m, 30m, 1h, 4h, 12h, 1d, 1w, 1M |
| limit | integer | 否 | 返回记录数，默认100，最大1000 |
| start_time | integer | 否 | 开始时间戳（毫秒） |
| end_time | integer | 否 | 结束时间戳（毫秒） |

**返回字段**:
| 字段 | 说明 |
|------|------|
| symbol | 交易产品 |
| interval | K线周期 |
| klines[] | K线数据数组 |
| klines[].time | K线时间戳（毫秒） |
| klines[].open | 开盘价 |
| klines[].high | 最高价 |
| klines[].low | 最低价 |
| klines[].close | 收盘价 |
| klines[].volume | 成交量 |
| klines[].quote_volume | 成交额 |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/kline?symbol=BTCUSDT&interval=1h&limit=10" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 实时 K 线 (Kline Latest)

获取当前周期内正在形成并实时更新的K线数据。

**使用场景**：
- 实时行情图表展示
- 当前价格监控
- 分时动态更新

**注意**：不建议用于历史回测或技术指标统计。

**端点**: `GET /v1/market/kline/latest`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbols | string | 是 | 交易产品代码，多个用逗号分隔 |
| interval | string | 是 | K线周期：1m, 3m, 5m, 15m, 30m, 1h, 4h, 12h, 1d, 1w, 1M |

**返回字段**: 同历史K线

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/kline/latest?symbols=AAPL.US,TSLA.US&interval=5m" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 订单簿 (Order Book)

获取交易品种的实时订单簿深度（买卖盘）数据。

**端点**: `GET /v1/market/depth`

**支持市场**: 美股、港股、加密货币

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | string | 是 | 交易产品代码 |
| limit | integer | 否 | 深度档位数，默认10，最大50 |

**返回字段**:
| 字段 | 说明 |
|------|------|
| symbol | 交易产品 |
| timestamp | 数据时间戳（毫秒，UTC） |
| bids | 买盘数组，每个元素为 [价格, 数量]，按价格降序排列 |
| asks | 卖盘数组，每个元素为 [价格, 数量]，按价格升序排列 |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/depth?symbol=BTCUSDT&limit=10" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 最近成交 (Recent Trades)

获取交易品种的最近成交执行记录。

**端点**: `GET /v1/market/trades`

**支持市场**: 港股、加密货币（不支持美股和A股）

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | string | 是 | 交易产品代码 |
| limit | integer | 否 | 返回成交记录数，默认50，最大200 |

**返回字段**:
| 字段 | 说明 |
|------|------|
| id | 成交ID |
| price | 成交价格 |
| quantity | 成交数量 |
| side | 成交方向（buy/sell） |
| timestamp | 成交时间（毫秒，UTC） |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/trades?symbol=BTCUSDT&limit=20" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 可用交易品种 (Available Symbols)

查询TickDB支持的所有可用交易品种。

**端点**: `GET /v1/symbols/available`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| market | string | 否 | 市场过滤：FOREX, METALS, INDICES, US, HK, CN, CRYPTO |
| limit | integer | 否 | 返回数量，默认100，最大500 |
| page | integer | 否 | 页码，默认1 |

**返回字段**:
| 字段 | 说明 |
|------|------|
| symbols[] | 交易品种数组 |
| symbols[].symbol | 交易品种代码 |
| symbols[].market | 市场代码 |
| symbols[].base_asset | 基础资产 |
| symbols[].quote_asset | 报价资产 |
| symbols[].status | 状态（active） |
| total | 总数量 |
| page | 当前页码 |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/symbols/available?market=CRYPTO&limit=20" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## K 线周期列表 (Kline Intervals)

查询系统支持的K线周期列表。

**端点**: `GET /v1/market/intervals/kline`

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/intervals/kline" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

# 股票市场接口

## 股票信息 (Stock Info)

获取股票的详细信息，包括公司名称、行业分类、市值等基本面数据。

**端点**: `GET /v1/market/stock-info`

**支持市场**: 美股、港股、A股

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbols | string | 是 | 股票代码，多个用逗号分隔，最多50个 |

**返回字段**:
| 字段 | 说明 |
|------|------|
| symbol | 交易产品 |
| name_cn | 中文简体标的名称 |
| name_en | 英文标的名称 |
| name_hk | 中文繁体标的名称 |
| exchange | 标的所属交易所 |
| currency | 交易币种（CNY/USD/HKD） |
| lot_size | 每手股数 |
| total_shares | 总股本 |
| circulating_shares | 流通股本 |
| eps | 每股盈利 |
| eps_ttm | 每股盈利（TTM） |
| bps | 每股净资产 |
| dividend_yield | 股息率 |
| stock_derivatives | 可选值：1 - 期权，2 - 轮证 |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/stock-info?symbols=700.HK,AAPL.US,000001.SZ" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 当日分时 (Intraday Data)

获取股票当日的分时数据，包括每分钟的价格、成交量、成交额等。

**端点**: `GET /v1/market/intraday`

**支持市场**: 美股、港股、A股

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbols | string | 是 | 股票代码，多个用逗号分隔，最多50个 |

**返回字段**:
| 字段 | 说明 |
|------|------|
| symbol | 交易产品 |
| lines[] | 分时数据数组 |
| lines[].timestamp | 当前分钟的开始时间（毫秒） |
| lines[].price | 当前分钟的收盘价格 |
| lines[].volume | 成交量 |
| lines[].turnover | 成交额 |
| lines[].avg_price | 均价 |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/intraday?symbols=700.HK,9988.HK" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 交易时段 (Trading Sessions)

查询指定市场的交易时段信息。

**端点**: `GET /v1/market/trading-sessions`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| market | string | 是 | 市场代码：US, HK, CN |

**返回字段**:
| 字段 | 说明 |
|------|------|
| market | 市场代码 |
| trading_sessions[] | 交易时段数组 |
| trading_sessions[].begin_time | 交易开始时间（格式：hhmm） |
| trading_sessions[].end_time | 交易结束时间（格式：hhmm） |
| trading_sessions[].trade_session | 交易时段类型（0-盘中，1-盘前，2-盘后，3-夜盘） |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/trading-sessions?market=US" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 交易日历 (Trading Days)

查询指定市场在特定时间范围内的交易日列表。

**端点**: `GET /v1/market/trade-days`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| market | string | 是 | 市场代码：US, HK, CN |
| beg_day | string | 是 | 开始日期（格式：YYYYMMDD） |
| end_day | string | 是 | 结束日期（格式：YYYYMMDD） |

**返回字段**:
| 字段 | 说明 |
|------|------|
| market | 市场代码 |
| trade_days | 全日交易日列表（YYYYMMDD格式） |
| half_trade_days | 半日交易日列表 |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/trade-days?market=CN&beg_day=20260201&end_day=20260228" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 市场指标 (Market Metrics)

获取股票的综合市场指标，包括行情统计、估值指标、资金流向等。

**端点**: `GET /v1/market/calc-index`

**支持市场**: 美股、港股、A股

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbols | string | 是 | 股票代码，多个用逗号分隔，最多50个 |

**返回字段**:
| 字段 | 说明 |
|------|------|
| symbol | 交易品种代码 |
| last_done | 最新价 |
| change_val | 涨跌额 |
| change_rate | 涨跌幅 |
| volume | 成交量 |
| turnover | 成交额 |
| ytd_change_rate | 年初至今涨幅 |
| turnover_rate | 换手率 |
| total_market_value | 总市值 |
| capital_flow | 资金流向 |
| amplitude | 振幅 |
| volume_ratio | 量比 |
| pe_ttm_ratio | 市盈率 (TTM) |
| pb_ratio | 市净率 |
| dividend_ratio_ttm | 股息率 (TTM) |
| five_day_change_rate | 五日涨幅 |
| ten_day_change_rate | 十日涨幅 |
| half_year_change_rate | 半年涨幅 |
| five_minutes_change_rate | 五分钟涨幅 |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/calc-index?symbols=700.HK,AAPL.US" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## 资金流向 (Capital Flow)

获取股票的资金流向数据，包括主力资金、大单、中单、小单的流入流出情况。

**端点**: `GET /v1/market/capital-flow`

**支持市场**: 美股、港股、A股

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| symbol | string | 是 | 股票代码 |

**返回字段**:
| 字段 | 说明 |
|------|------|
| symbol | 交易产品 |
| timestamp | 数据更新时间戳 |
| intraday_flow[] | 当日资金流向数组 |
| intraday_flow[].timestamp | 分钟开始时间戳 |
| intraday_flow[].inflow | 净流入 |
| distribution | 资金分布 |
| distribution.capital_in | 流入资金（large/medium/small） |
| distribution.capital_out | 流出资金（large/medium/small） |

**示例请求**:
```bash
curl -X GET "https://api.tickdb.ai/v1/market/capital-flow?symbol=700.HK" \
  -H "X-API-Key: YOUR_API_KEY"
```

---

# 快速使用指南

## Python 示例

```python
import requests

# ⚠️ 请替换为您自己的 API Key（从 https://tickdb.ai 免费申请）
API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.tickdb.ai"

headers = {"X-API-Key": API_KEY}

# 获取实时行情
def get_ticker(symbols):
    url = f"{BASE_URL}/v1/market/ticker"
    params = {"symbols": ",".join(symbols)}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# 获取K线数据
def get_kline(symbol, interval="1h", limit=100):
    url = f"{BASE_URL}/v1/market/kline"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# 获取股票信息
def get_stock_info(symbols):
    url = f"{BASE_URL}/v1/market/stock-info"
    params = {"symbols": ",".join(symbols)}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 获取多个品种实时价格
    tickers = get_ticker(["BTCUSDT", "ETHUSDT", "XAUUSD"])
    print(tickers)
    
    # 获取BTC历史K线
    klines = get_kline("BTCUSDT", "1h", limit=100)
    print(klines)
```

## 常见使用场景

### 场景1: 获取黄金/外汇实时价格
```
GET /v1/market/ticker?symbols=XAUUSD,XAGUSD,EURUSD,GBPUSD
```

### 场景2: 获取加密货币K线（用于技术分析）
```
GET /v1/market/kline?symbol=BTCUSDT&interval=1h&limit=500
```

### 场景3: 获取美股分时数据
```
GET /v1/market/intraday?symbols=AAPL.US,TSLA.US,MSFT.US
```

### 场景4: 查询港股交易时段
```
GET /v1/market/trading-sessions?market=HK
```

### 场景5: 获取A股近期交易日
```
GET /v1/market/trade-days?market=CN&beg_day=20260201&end_day=20260228
```

### 场景6: 获取股票市场指标（估值、资金等）
```
GET /v1/market/calc-index?symbols=000001.SZ,600000.SH
```

### 场景7: 获取订单簿深度
```
GET /v1/market/depth?symbol=BTCUSDT&limit=20
```

---

# 错误处理

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（API Key无效或缺失） |
| 403 | 权限不足 |
| 429 | 请求过于频繁（限流） |
| 500 | 服务器内部错误 |

如遇错误，请检查：
1. API Key是否正确
2. 请求参数格式是否正确
3. 是否超出接口调用限制
