# 更新記錄

**語言：** [简体中文](../../CHANGELOG.md) · **繁體中文** · [English](../en/CHANGELOG.md)

## v0.2.3 — 2026-10-15

相對於 v0.1.3 的變更。

### 新增

- 工具擴充至 43 個：13 個行情工具、29 個公司財務與基本面工具、1 個 API Key 訂閱工具。
- 新增公司概況、高管、財務報表、營收分部、估值、行業資料、股息、回購、股東與基金持倉、新聞、公司事件及分類財經日曆查詢。
- 新增股票復權因子、K 線 `adjust`、股息 TTM、新聞詳情、市場狀態及 `get_api_key_subscriptions`；更新中港期貨覆蓋範圍。
- 新增可選的 OAuth 網頁授權，支援 S256 PKCE、動態客戶端註冊、refresh token 輪替與撤銷；授權確認頁支援簡體中文、繁體中文和英文。
- OAuth 透過使用者驗證並明確授權的 TickDB API Key 查詢資料；Key 綁定加密儲存於持久化 SQLite。
- 提供三語言部署與客戶端接入指南，以及工具和 HTTP 傳輸的離線測試。

### 修正與改進

- 更新 REST 端點和參數對應、批次查詢上限、逐筆成交筆數限制、分頁及時間戳處理。
- 保留回應結構、HTTP 狀態、業務錯誤與 `Retry-After`，識別 HTTP 200 中的業務失敗，並支援 gzip 回應。
- 完善 OAuth 的 CSRF、同源提交、精確回呼白名單與 issuer 識別；授權確認頁僅展示提交的 Key 對應的遮罩資訊和訂閱。
- 修正 Python wheel 的 `tickdb-mcp` 入口模組打包及 Docker 原始碼建置，支援獨立安裝和自部署。
- 日誌輸出至 stderr，避免干擾 stdio JSON-RPC；透過 `LOG_DIR` 設定日誌目錄，無法寫入檔案時繼續輸出至 stderr。

### 升級注意事項

- 重新整理客戶端工具列表。移除 `get_kline_intervals`、`get_financial_fields` 與原 `get_financial_calendar`；財經日曆改用分類工具。
- 移除財務 `fields`、歷史估值 `metric` 和買賣盤 `limit` 參數；按代碼查詢的基本面工具要求 `symbol`。詳見 [升級指引](README.md#api-migration)。
- OAuth 預設關閉；原 `/mcp` 標頭接入與 stdio 保留。啟用 OAuth 時使用 `/oauth` 工具入口、公網 HTTPS 與持久化資料庫，升級時保留加密金鑰、資料庫和有效授權。詳見 [OAuth 自部署](README.md#oauth-setup)。
- 相依套件要求 MCP SDK `>=1.26.0,<2.0.0` 與 `cryptography>=46.0.0`。

## v0.1.3 - 2026-06-15

### 修正

- 透過 `MCP_STATELESS_HTTP=true` 預設啟用無狀態 Streamable HTTP，避免在記憶體中保留已棄用的 MCP 工作階段。
- 為中介軟體的工作階段生命週期日誌加入 TTL 與最大條目數限制，避免重新連線時 `_known_sessions` 無限增長。

### 新增

- 新增 `MCP_SESSION_LOG_TTL_SECONDS` 與 `MCP_SESSION_LOG_MAX_ENTRIES`，設定工作階段生命週期日誌的保留策略。
- 新增工作階段生命週期快取邊界的單元測試。

---

## v0.1.2 — 2026-05-20

### 新增

- **結構化日誌**覆蓋完整請求生命週期：
  - 啟動：伺服器設定摘要（傳輸、連接埠、認證狀態、API Key 狀態）
  - 中介軟體：請求 IP、方法、路徑、Key 來源與認證結果
  - 客戶端：API 呼叫路徑、參數、Key 來源、回應狀態與耗時
  - 錯誤：逾時、網路錯誤、API 錯誤碼與完整上下文
- **工作階段生命週期日誌**：追蹤 `SESSION_INIT`、`SESSION_CREATED`、`SESSION_REUSE`、`SESSION_ATTACH`、`SESSION_NOT_FOUND` 事件，關聯 Key 與工作階段 ID。
- **每日輪替日誌檔案**：`logs/tickdb_mcp.log` 自動每日輪替，透過 `LOG_RETAIN_DAYS` 設定保留天數（預設 7 天）。
- **`LOG_LEVEL` 環境變數**：控制日誌詳細程度（DEBUG／INFO／WARNING／ERROR，預設 INFO）。
- **`LOG_RETAIN_DAYS` 環境變數**：控制輪替日誌的保留天數。
- **API Key 遮罩**：日誌僅顯示前 4 個與後 4 個字元。
- **依 Key 關聯日誌**：請求、回應與錯誤日誌均包含遮罩後的 API Key，便於在並行環境中追蹤使用者的完整呼叫鏈。
- **請求計時**：每次 TickDB API 呼叫均記錄毫秒精度的耗時。
- **明確的錯誤分類**：分別記錄 TIMEOUT、NETWORK_ERROR 與 API 錯誤碼。

### 修正

- **Hermes MCP 客戶端相容性**：自動修正未同時傳送 `application/json` 與 `text/event-stream` 的客戶端的 `Accept` 標頭，解決阻止 SSE 工作階段建立的 406 Not Acceptable 錯誤。

---

## v0.1.1 — 2026-05-14

### 新增

- 為 9 個工具新增 **`type` 參數**，解決代碼歧義：`get_ticker`、`get_kline`、`get_kline_latest`、`get_order_book`、`get_recent_trades`、`get_stock_info`、`get_intraday`、`get_market_metrics`、`get_capital_flow`。
- 可用值：`stock`、`crypto`、`forex`、`indices`、`futures`。
- 僅在同一代碼對應多個產品類型時必填，例如中國市場的 `000001` 同時代表平安銀行股票與上證指數。
- 唯一代碼（如 `AAPL.US`、`BTCUSDT`）仍可省略 `type`。

### 修正

- 解決中國市場股票與指數共用代碼時的 `AMBIGUOUS_SYMBOL` 錯誤。

---

## v0.1.0 — 2026-05-01

### 首次發布

- **13 個 MCP 工具**覆蓋即時與歷史行情：
  - `get_ticker`：即時行情快照
  - `get_kline` / `get_kline_latest` / `get_kline_intervals`：K 線資料
  - `get_order_book`：買賣盤深度
  - `get_recent_trades`：最新逐筆成交
  - `get_available_symbols`：查詢 37,527+ 個可交易代碼
  - `get_stock_info`：股票基本資訊
  - `get_intraday`：分鐘級分時資料
  - `get_trading_sessions`：市場交易時段
  - `get_trade_days`：交易日曆
  - `get_market_metrics`：估值與市場指標
  - `get_capital_flow`：資金流向分析
- **資產覆蓋**：外匯、貴金屬、指數、美股、港股、A 股與加密貨幣。
- **兩層 API Key 解析**：每次請求的 `X-TickDB-Key` 標頭 → `TICKDB_API_KEY` 環境變數。
- **傳輸**：Streamable HTTP（遠端）與 stdio（本地 Claude Desktop）。
- **認證中介軟體**：透過 `MCP_ACCESS_TOKEN` 提供可選的 Bearer token 存取控制。
- **Docker 支援**：可用於正式部署的 Dockerfile。
