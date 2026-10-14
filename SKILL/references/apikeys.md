# API Key 套餐与到期查询

本参考说明 API Key 的套餐、状态与到期查询。

`GET https://api.tickdb.ai/v1/apikeys/subscriptions`

用途：查询当前认证账户下返回的 API Key 列表、套餐、状态及到期情况。使用用户提供的正式 Key，通过必填请求头 `X-API-Key` 认证；无需登录网页。不传查询参数或请求体。

```bash
curl --request GET "https://api.tickdb.ai/v1/apikeys/subscriptions" \
  --header "X-API-Key: YOUR_API_KEY"
```

这是账户查询，不能自动获取公共试用 Key 代替用户的账户凭据。未提供本人账户 Key 时，请用户提供已配置的环境变量名或凭据路径。除非用户要求查询套餐或到期情况，不要为普通行情查询额外调用该端点。

## 响应字段

成功需 HTTP 200 且 `code=0`，主数据为 `response.data`：

| 字段 | 说明 |
|---|---|
| user_id | 当前认证账户标识；无需在普通结果中展示 |
| server_time | 服务端计算时间，RFC3339，解析时保留时区与小数秒 |
| total | 本次返回的 Key 数量 |
| api_keys[] | API Key 记录数组，不是只有本次认证 Key 的单条对象 |
| api_keys[].id | 记录 ID，不是可用于认证的 Key |
| api_keys[].key_prefix | Key 前缀，用于辅助识别；不能拼接、还原或用作认证 Key |
| api_keys[].name | Key 名称 |
| api_keys[].plan | 套餐名称；例如 professional，不将示例当作完整枚举 |
| api_keys[].status | 状态；例如 active，不将示例当作完整枚举 |
| api_keys[].expires_at | 到期时间，RFC3339 |
| api_keys[].remaining_seconds | 以服务端时间计算的剩余秒数 |
| api_keys[].created_at | 创建时间，RFC3339 |

## 展示和错误处理

- 默认展示名称、必要的脱敏识别、套餐、原始状态、到期时间和剩余时长，不显示 user_id、记录 ID 或完整 Key；不把原始账户响应保存到日志或报告。
- 用 `server_time` 解读 `remaining_seconds`；天数可按 86400 秒换算并注明取整方式。到期时间可以转换为用户时区，须标明时区，不能用本机日期代替服务端计算时间。
- 不按列表顺序、名称或前缀唯一性猜测“当前使用的 Key”；如果无法唯一匹配用户所指记录，应先澄清。
- 不因 status=active 就承诺所有市场、接口或配额均可用；本端点不是完整权限清单。null、未知状态或未说明的长期有效形式按原值说明，不推断为永久有效。
- 空列表说明本次返回零条，不能改称认证失败。HTTP 401/1002 表示缺认证；401/1001（含已知文本业务码）表示无效或已过期；其余按 [HTTP 错误参考](errors.md) 处理，不自动切换试用 Key。
- 本端点仅查询，不支持创建、续费、撤销、修改 Key，也不会自行建立定时提醒。
