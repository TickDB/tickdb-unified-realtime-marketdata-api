"""Browser-only API-key verification and explicit OAuth consent."""

import hmac
import html
import secrets
import time
from datetime import datetime
from urllib.parse import urlsplit

import httpx
from mcp.server.auth.provider import AuthorizationParams, construct_redirect_uri
from starlette.responses import HTMLResponse, RedirectResponse

from tickdb_mcp.oauth.localization import LANGUAGES, message, select_language
from tickdb_mcp.oauth.provider import CODE_TTL, GRANT_TTL, SCOPE
from tickdb_mcp.oauth.store import digest

SECURE_HEADERS = {
    "Cache-Control": "no-store", "Pragma": "no-cache", "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
    "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; "
                               "frame-ancestors 'none'; base-uri 'none'",
}


class KeyValidationError(Exception):
    pass


def subscription_summary(body: dict, key: str) -> dict:
    data = body.get("data")
    if not isinstance(data, dict) or not isinstance(data.get("api_keys"), list):
        raise KeyValidationError("subscription_format")
    rows = [row for row in data["api_keys"] if isinstance(row, dict)]
    # Only use a unique, sufficiently long unmasked prefix matching the submitted
    # Key. Short, masked or ambiguous prefixes cannot identify its subscription.
    matches = [row for row in rows if isinstance(row.get("key_prefix"), str)
               and len(row["key_prefix"]) >= 8
               and not any(marker in row["key_prefix"] for marker in ("*", "…", "..."))
               and key.startswith(row["key_prefix"])]
    if len(matches) == 1:
        row = matches[0]
        if str(row.get("status", "")).lower() in {"expired", "revoked", "disabled", "inactive"}:
            raise KeyValidationError("key_inactive")
        remaining = row.get("remaining_seconds")
        if isinstance(remaining, (int, float)) and not isinstance(remaining, bool) and remaining <= 0:
            raise KeyValidationError("key_expired")
        try:
            if row.get("expires_at") and data.get("server_time"):
                expiry = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
                server = datetime.fromisoformat(data["server_time"].replace("Z", "+00:00"))
                if expiry <= server:
                    raise KeyValidationError("key_expired")
        except (ValueError, TypeError, AttributeError):
            pass
    # Never persist unrelated account records in a browser authorization request.
    return {"server_time": data.get("server_time"), "subscription": {
        field: matches[0].get(field)
        for field in ("name", "plan", "status", "expires_at", "remaining_seconds")
    } if len(matches) == 1 else None}


async def validate_key(key: str) -> dict:
    if not key or len(key) > 512 or not key.isascii() or any(ord(c) <= 32 or ord(c) == 127 for c in key):
        raise KeyValidationError("invalid_key")
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as http:
            response = await http.get("https://api.tickdb.ai/v1/apikeys/subscriptions",
                                      headers={"X-API-Key": key, "Accept-Encoding": "gzip"})
        body = response.json()
    except (httpx.RequestError, ValueError):
        raise KeyValidationError("subscription_unavailable") from None
    if (not response.is_success or not isinstance(body, dict)
            or str(body.get("code")) != "0"):
        # Never echo upstream messages/details: they may contain submitted credentials.
        if response.status_code == 429 or (isinstance(body, dict) and str(body.get("code")) == "3001"):
            raise KeyValidationError("rate_limited")
        raise KeyValidationError("key_rejected")
    return subscription_summary(body, key)


def escape(value) -> str:
    return html.escape(str(value), quote=True)


def masked_key(key: str) -> str:
    return key[:4] + "••••" + key[-4:] if len(key) > 8 else "••••"


def page(pending=None, ticket="", csrf="", error="", status=200, language="en"):
    language = select_language(language)

    def text(key):
        return message(key, language)

    pending = pending or {}
    verified = "api_key" in pending
    nonce = secrets.token_urlsafe(24)
    switcher = '<form class="language" id="language-form" method="get" action="/oauth/consent">'
    switcher += f'<input type="hidden" name="ticket" value="{escape(ticket)}">'
    switcher += f'<label for="language">{text("language")}</label><select id="language" name="lang">'
    for value, label in LANGUAGES.items():
        selected = " selected" if value == language else ""
        switcher += f'<option value="{value}"{selected}>{label}</option>'
    switcher += f'</select><noscript><button>{text("switch")}</button></noscript></form>'
    content = ""
    if pending:
        client_name = escape(pending["client_name"])
        callback = escape(pending["params"]["redirect_uri"])
        content += f'<p>{text("request").format(client=client_name)}</p>'
        content += f'<p>{text("scope")}</p>'
        content += f'<p class="muted">{text("callback")}: {callback}</p>'
        if verified:
            summary = pending["summary"]
            content += f'<div class="success">{text("verified")}</div>'
            content += f'<p>{text("connection_key")}</p>'
            content += f'<p class="key"><span>TickDB API Key</span><code>{escape(masked_key(pending["api_key"]))}</code></p>'
            # Older pending requests can contain account-wide summaries. Only
            # the new explicitly selected subscription is eligible for display.
            row = summary.get("subscription")
            if row:
                content += '<dl class="subscription">'
                for label, field in (("name", "name"), ("plan", "plan"), ("status", "status"), ("expires", "expires_at")):
                    value = row.get(field) if row.get(field) is not None else text("unavailable")
                    content += f'<div><dt>{text(label)}</dt><dd>{escape(value)}</dd></div>'
                content += '</dl>'
        content += '<form method="post" action="/oauth/consent">'
        content += f'<input type="hidden" name="ticket" value="{escape(ticket)}">'
        content += f'<input type="hidden" name="csrf" value="{escape(csrf)}">'
        content += f'<input type="hidden" name="lang" value="{language}">'
        if verified:
            content += f'<button name="action" value="approve">{text("approve")}</button>'
        else:
            content += '<label for="api_key">TickDB API Key</label><input id="api_key" name="api_key" '
            content += 'type="password" maxlength="512" autocomplete="off" spellcheck="false">'
            content += f'<p class="muted">{text("key_notice")}</p>'
            content += f'<button name="action" value="verify">{text("verify")}</button>'
        content += f'<button class="secondary" name="action" value="deny">{text("cancel")}</button></form>'
    else:
        content = f'<p>{text("reconnect")}</p>'
    output = f'''<!doctype html><html lang="{language}"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{text("title")}</title>'''
    output += '''
<style>body{margin:0;background:#f5f7fa;color:#182638;font:16px/1.7 system-ui,sans-serif}
main{max-width:640px;margin:7vh auto;padding:36px;background:white;border:1px solid #dfe5ed;border-radius:16px}
.top{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:16px}
.language{display:flex;align-items:center;gap:8px;font-size:13px}.language select{max-width:150px;padding:6px;border:1px solid #a9b8c7;border-radius:6px;background:white;color:#182638;font:inherit}
h1{font-size:28px;margin:0 0 20px}.brand{color:#166c69;font-weight:700;letter-spacing:1px}
input[type=password]{display:block;box-sizing:border-box;width:100%;padding:12px;margin:8px 0;border:1px solid #a9b8c7;border-radius:8px}
button{background:#166c69;color:white;border:0;border-radius:8px;padding:12px 18px;font:inherit;cursor:pointer;margin:8px 12px 0 0}
.secondary{background:#eaf0f4;color:#263747}.muted{color:#566779;font-size:13px;overflow-wrap:anywhere}
.key{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;padding:12px;background:#f5f7fa;border-radius:8px}.key code{font:15px ui-monospace,monospace;overflow-wrap:anywhere}
.error{background:#fff0ed;color:#9c2920;padding:12px;border-radius:8px}.success{background:#e9f6ef;padding:12px;border-radius:8px}
.subscription{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin:16px 0 24px}.subscription div{min-width:0}.subscription dt{font-size:13px;color:#566779}.subscription dd{margin:4px 0 0;overflow-wrap:anywhere}
@media(max-width:720px){main{margin:20px 12px;padding:24px}.subscription{grid-template-columns:1fr}}</style>
'''
    output += f'<main><div class="top"><div class="brand">TickDB</div>{switcher}</div><h1>{text("heading")}</h1>'
    if error:
        output += f'<p class="error" role="alert">{escape(text(error))}</p>'
    headers = dict(SECURE_HEADERS)
    headers["Content-Language"] = language
    headers["Content-Security-Policy"] += f"; script-src 'nonce-{nonce}'"
    script = f'''<script nonce="{nonce}">document.getElementById("language").addEventListener("change", function() {{ this.form.requestSubmit(); }});</script>'''
    if pending:
        # no-referrer makes browser form POSTs send Origin: null, which our
        # origin check rejects. Preserve the origin for same-origin forms while
        # withholding the ticket-bearing Referer from external callbacks.
        headers["Referrer-Policy"] = "same-origin"
        # Browsers can apply form-action to the POST's 303 redirect as well.
        # This URI has already passed the exact registered callback allowlist.
        callback_url = urlsplit(pending["params"]["redirect_uri"])
        callback_origin = f"{callback_url.scheme}://{callback_url.netloc}"
        headers["Content-Security-Policy"] = headers["Content-Security-Policy"].replace(
            "form-action 'self';", f"form-action 'self' {callback_origin};",
        )
    return HTMLResponse(output + content + '</main>' + script + '</html>', status_code=status, headers=headers)


class Consent:
    def __init__(self, provider):
        self.provider = provider
        self.store = provider.store

    @staticmethod
    def cookie_name(ticket):
        return "__Host-tickdb-" + digest(ticket)[:16]

    async def handle(self, request):
        if request.method == "GET":
            language = select_language(request.query_params.get("lang"), request.headers.get("accept-language", ""))
            ticket = request.query_params.get("ticket", "")
            csrf = secrets.token_urlsafe(32)
            with self.store.transaction() as db:
                pending = self.store.read(db, "pending", digest(ticket))
                if not pending:
                    return page(error="request_expired", status=400, ticket=ticket, language=language)
                pending["csrf"] = digest(csrf)
                self.store.put(db, "pending", digest(ticket), pending, pending["expires"])
            response = page(pending, ticket, csrf, language=language)
            response.set_cookie(self.cookie_name(ticket), csrf, max_age=600, secure=True,
                                httponly=True, samesite="lax", path="/")
            return response
        form = await request.form()
        language = select_language(str(form.get("lang", "")), request.headers.get("accept-language", ""))
        ticket, csrf = str(form.get("ticket", "")), str(form.get("csrf", ""))
        cookie = request.cookies.get(self.cookie_name(ticket), "")
        origin = request.headers.get("origin")
        if (not csrf or not hmac.compare_digest(csrf, cookie)
                or (origin is not None and origin != self.provider.issuer.rstrip("/"))):
            return page(error="page_verification_failed", status=403, language=language)
        with self.store.transaction() as db:
            pending = self.store.read(db, "pending", digest(ticket))
            if not pending or not hmac.compare_digest(pending.get("csrf", ""), digest(csrf)):
                return page(error="request_expired", status=400, language=language)
            params = AuthorizationParams.model_validate(pending["params"])
            action = form.get("action")
            if action in ("deny", "approve"):
                if action == "approve" and "api_key" not in pending:
                    return page(pending, ticket, csrf, "verify_first", 400, language=language)
                if str(params.redirect_uri) not in self.provider.redirect_uris:
                    return page(error="callback_disabled", status=400, language=language)
                self.store.delete(db, "pending", digest(ticket))
                fields = {"state": params.state, "iss": self.provider.issuer}
                if action == "deny":
                    fields["error"] = "access_denied"
                else:
                    family = secrets.token_urlsafe(32)
                    expires = int(time.time()) + GRANT_TTL
                    self.store.put(db, "grant", family, {"api_key": pending["api_key"],
                                   "client_id": pending["client_id"], "expires": expires}, expires, family)
                    code = secrets.token_urlsafe(32)
                    self.store.put(db, "code", digest(code), {
                        "client_id": pending["client_id"], "family": family,
                        "code": {"client_id": pending["client_id"], "scopes": [SCOPE],
                                 "expires_at": time.time() + CODE_TTL,
                                 "code_challenge": params.code_challenge,
                                 "redirect_uri": str(params.redirect_uri),
                                 "redirect_uri_provided_explicitly": params.redirect_uri_provided_explicitly,
                                 "resource": params.resource},
                    }, time.time() + CODE_TTL, family)
                    fields["code"] = code
                response = RedirectResponse(construct_redirect_uri(str(params.redirect_uri), **fields),
                                            status_code=303, headers=SECURE_HEADERS)
                response.delete_cookie(self.cookie_name(ticket), secure=True, httponly=True, samesite="lax")
                return response
            if action != "verify" or "api_key" in pending or pending["attempts"] >= 5:
                return page(error="restart_authorization", status=400, language=language)
            pending["attempts"] += 1
            revision = pending["attempts"]
            self.store.put(db, "pending", digest(ticket), pending, pending["expires"])
        key = str(form.get("api_key", "")).strip()
        try:
            summary = await validate_key(key)
        except KeyValidationError as exc:
            return page(pending, ticket, csrf, str(exc), 400, language=language)
        with self.store.transaction() as db:
            current = self.store.read(db, "pending", digest(ticket))
            if (not current or current["attempts"] != revision
                    or current.get("csrf") != digest(csrf) or "api_key" in current):
                return page(error="request_updated", status=400, language=language)
            current.update(api_key=key, summary=summary)
            self.store.put(db, "pending", digest(ticket), current, current["expires"])
        return page(current, ticket, csrf, language=language)
