"""Consent-page language negotiation and translations; no external resources."""

LANGUAGES = {"zh-CN": "简体中文", "zh-TW": "繁體中文", "en": "English"}

# Each entry is Simplified Chinese, Traditional Chinese, and English.
MESSAGES = {
    "title": ("连接 TickDB", "連接 TickDB", "Connect to TickDB"),
    "heading": ("连接你的数据账户", "連接你的資料帳戶", "Connect your data account"),
    "language": ("语言", "語言", "Language"),
    "switch": ("切换", "切換", "Apply"),
    "request": ("应用 <strong>{client}</strong> 请求访问 TickDB 数据。",
                "應用程式 <strong>{client}</strong> 要求存取 TickDB 資料。",
                "<strong>{client}</strong> requests access to your TickDB data."),
    "scope": ("授权范围：行情、公司财务与 API Key 订阅信息查询。实际可用数据由你的套餐决定。",
              "授權範圍：行情、公司財務與 API Key 訂閱資訊查詢。實際可用資料由你的方案決定。",
              "Access: market data, company financials, and API Key subscriptions. Available data depends on your plan."),
    "callback": ("授权返回地址", "授權返回網址", "Authorization callback"),
    "verified": ("API Key 验证成功。", "API Key 驗證成功。", "API Key verified."),
    "connection_key": ("当前授权连接将使用以下 API Key：", "目前的授權連接將使用以下 API Key：",
                       "This connection will use the following API Key:"),
    "name": ("名称", "名稱", "Name"),
    "plan": ("套餐", "方案", "Plan"),
    "status": ("状态", "狀態", "Status"),
    "expires": ("到期时间", "到期時間", "Expires"),
    "unavailable": ("未提供", "未提供", "Not provided"),
    "server_time": ("服务端时间", "伺服器時間", "Server time"),
    "approve": ("确认授权连接", "確認授權連接", "Approve connection"),
    "key_notice": ("Key 将加密保存在此服务，用于代你查询 TickDB；不会返回给客户端应用。",
                   "Key 將加密儲存在此服務，用於代你查詢 TickDB；不會返回給用戶端應用程式。",
                   "Your Key is encrypted and stored by this service to query TickDB for you. It is not returned to the client application."),
    "verify": ("验证 API Key", "驗證 API Key", "Verify API Key"),
    "cancel": ("取消", "取消", "Cancel"),
    "reconnect": ("请回到客户端重新发起连接。", "請回到用戶端重新發起連接。",
                  "Return to your client and start a new connection."),
    "subscription_format": ("订阅服务返回格式异常，请稍后重试。", "訂閱服務返回格式異常，請稍後重試。",
                            "The subscription service returned an unexpected response. Try again later."),
    "key_inactive": ("该 API Key 已过期或已停用，请更换后重新授权。", "該 API Key 已過期或已停用，請更換後重新授權。",
                     "This API Key has expired or is inactive. Use another Key and reconnect."),
    "key_expired": ("该 API Key 已过期，请更换后重新授权。", "該 API Key 已過期，請更換後重新授權。",
                    "This API Key has expired. Use another Key and reconnect."),
    "invalid_key": ("请输入有效的 TickDB API Key。", "請輸入有效的 TickDB API Key。",
                    "Enter a valid TickDB API Key."),
    "subscription_unavailable": ("暂时无法查询订阅信息，请稍后重试。", "暫時無法查詢訂閱資訊，請稍後重試。",
                                 "Subscription information is temporarily unavailable. Try again later."),
    "rate_limited": ("查询过于频繁，请稍后重试。", "查詢過於頻繁，請稍後重試。",
                     "Too many requests. Try again later."),
    "key_rejected": ("API Key 验证未通过，请检查 Key、有效期及订阅查询权限。",
                     "API Key 驗證未通過，請檢查 Key、有效期及訂閱查詢權限。",
                     "API Key verification failed. Check your Key, its expiry, and subscription-query permissions."),
    "request_expired": ("授权请求已过期或不存在。", "授權請求已過期或不存在。",
                        "This authorization request has expired or does not exist."),
    "page_verification_failed": ("授权页面验证失败，请重新连接。", "授權頁面驗證失敗，請重新連接。",
                                 "Authorization page verification failed. Please reconnect."),
    "verify_first": ("请先验证 API Key。", "請先驗證 API Key。", "Verify your API Key first."),
    "callback_disabled": ("返回地址已停用，请重新连接。", "返回網址已停用，請重新連接。",
                          "The callback URL is no longer allowed. Please reconnect."),
    "restart_authorization": ("请重新发起授权连接。", "請重新發起授權連接。",
                              "Start a new authorization connection."),
    "request_updated": ("授权请求已更新，请重新连接。", "授權請求已更新，請重新連接。",
                        "This authorization request has changed. Please reconnect."),
}


def message(key: str, language: str) -> str:
    index = {"zh-CN": 0, "zh-TW": 1, "en": 2}.get(language, 2)
    return MESSAGES[key][index]


def select_language(explicit: str | None, accept_language: str = "") -> str:
    if explicit in LANGUAGES:
        return explicit
    preferences = []
    for item in accept_language[:4096].split(",")[:32]:
        tag, *parameters = item.strip().lower().split(";")
        quality = 1.0
        try:
            for parameter in parameters:
                name, _, value = parameter.strip().partition("=")
                if name == "q":
                    quality = float(value)
        except ValueError:
            continue
        if 0 < quality <= 1:
            preferences.append((tag.strip(), quality))
    for tag, _ in sorted(preferences, key=lambda item: item[1], reverse=True):
        parts = tag.split("-")
        if parts[0] == "en":
            return "en"
        if parts[0] == "zh":
            if "hant" in parts:
                return "zh-TW"
            if "hans" in parts:
                return "zh-CN"
            return "zh-TW" if any(part in {"tw", "hk", "mo"} for part in parts) else "zh-CN"
    return "en"
