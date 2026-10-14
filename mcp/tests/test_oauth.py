"""OAuth HTTP workflows with real SQLite/crypto/SDK; only upstream HTTP is mocked."""

import asyncio
import base64
import hashlib
import json
import re
import time
from contextlib import asynccontextmanager
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
import respx
from cryptography.fernet import Fernet, InvalidToken

from tickdb_mcp import client
from tickdb_mcp.config import settings
from tickdb_mcp.http import create_http_app
from tickdb_mcp.oauth.consent import KeyValidationError, masked_key, page, subscription_summary
from tickdb_mcp.oauth.localization import select_language
from tickdb_mcp.oauth.store import Store

ORIGIN = "https://mcp.example.com"
RESOURCE = ORIGIN + "/oauth"
CALLBACK = "https://chatgpt.com/connector_platform_oauth_redirect"
VERIFIER = "a" * 64
CHALLENGE = base64.urlsafe_b64encode(hashlib.sha256(VERIFIER.encode()).digest()).decode().rstrip("=")
KEY = "test-user-api-key-1234"
SUBSCRIPTIONS = {"code": 0, "data": {"user_id": "test-user", "server_time": "2026-10-08T12:00:00Z",
    "total": 1, "api_keys": [{"key_prefix": "test-user", "name": "My key", "plan": "professional",
                            "status": "active", "expires_at": None, "remaining_seconds": None}]}}


@pytest.fixture
def configuration(monkeypatch, tmp_path):
    for name, value in {
        "oauth_enabled": True, "oauth_public_url": ORIGIN,
        "oauth_encryption_key": Fernet.generate_key().decode(),
        "oauth_database_path": str(tmp_path / "oauth.sqlite3"), "oauth_redirect_uris": [CALLBACK],
        "mcp_access_token": "legacy-secret", "tickdb_api_key": "shared-key-do-not-use",
    }.items():
        monkeypatch.setattr(settings, name, value)
    return settings


@asynccontextmanager
async def open_http():
    app = create_http_app()
    started = asyncio.get_running_loop().create_future()
    stop = asyncio.Event()

    async def lifecycle():
        try:
            async with app.router.lifespan_context(app):
                started.set_result(None)
                await stop.wait()
        except BaseException as exc:
            if not started.done():
                started.set_exception(exc)
            raise

    task = asyncio.create_task(lifecycle())
    try:
        await started
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=ORIGIN) as http:
            yield http
    finally:
        stop.set()
        await task


@pytest.fixture
async def http(configuration):
    async with open_http() as connection:
        yield connection


async def register(http, method="none", **overrides):
    metadata = {"redirect_uris": [CALLBACK], "client_name": "ChatGPT test",
                "grant_types": ["authorization_code", "refresh_token"], "response_types": ["code"],
                "token_endpoint_auth_method": method, "scope": "tickdb:read", **overrides}
    return await http.post("/register", json=metadata)


def auth_params(client_id, **overrides):
    return {"client_id": client_id, "redirect_uri": CALLBACK, "response_type": "code",
            "scope": "tickdb:read", "state": "caller-state", "code_challenge": CHALLENGE,
            "code_challenge_method": "S256", "resource": RESOURCE, **overrides}


async def begin(http, registration=None):
    registration = registration or (await register(http)).json()
    response = await http.get("/authorize", params=auth_params(registration["client_id"]))
    assert response.status_code == 302, response.text
    response = await http.get(response.headers["location"])
    assert response.status_code == 200
    form = {field: re.search(fr'name="{field}" value="([^"]+)"', response.text).group(1)
            for field in ("ticket", "csrf")}
    return registration, form


async def code(http, key=KEY, registration=None):
    registration, form = await begin(http, registration)
    response = await http.post("/oauth/consent", data={**form, "action": "verify", "api_key": key})
    assert response.status_code == 200, response.text
    assert "Approve connection" in response.text
    assert key not in response.text
    response = await http.post("/oauth/consent", data={**form, "action": "approve"})
    assert response.status_code == 303, response.text
    query = parse_qs(urlsplit(response.headers["location"]).query)
    assert query["state"] == ["caller-state"]
    assert query["iss"] == [ORIGIN + "/"]
    return registration, query["code"][0]


def token_form(registration, authorization_code, **overrides):
    return {"client_id": registration["client_id"], "grant_type": "authorization_code",
            "code": authorization_code, "redirect_uri": CALLBACK, "code_verifier": VERIFIER,
            "resource": RESOURCE,
            **({"client_secret": registration["client_secret"]} if registration.get("client_secret") else {}),
            **overrides}


async def grant(http, key=KEY, registration=None):
    registration, value = await code(http, key, registration)
    response = await http.post("/token", data=token_form(registration, value))
    assert response.status_code == 200, response.text
    return registration, response.json()


async def rpc(http, token, method="tools/list", params=None, path="/oauth", headers=None):
    return await http.post(path, headers={"Authorization": f"Bearer {token}",
                                         "Accept": "application/json, text/event-stream", **(headers or {})},
                           json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}})


def payload(response):
    assert response.status_code == 200, response.text
    return json.loads(next(line[6:] for line in response.text.splitlines() if line.startswith("data: ")))


@pytest.fixture
def upstream():
    with respx.mock(assert_all_called=False) as router:
        router.get("https://api.tickdb.ai/v1/apikeys/subscriptions").mock(
            return_value=httpx.Response(200, json=SUBSCRIPTIONS))
        yield router


async def test_discovery_and_legacy_auth_are_independent(http):
    metadata = await http.get("/.well-known/oauth-protected-resource/oauth")
    assert metadata.status_code == 200
    assert metadata.json()["resource"] == RESOURCE
    auth = (await http.get("/.well-known/oauth-authorization-server")).json()
    assert auth["authorization_response_iss_parameter_supported"] is True
    assert metadata.json()["authorization_servers"] == [auth["issuer"]]
    assert auth["code_challenge_methods_supported"] == ["S256"]
    assert auth["registration_endpoint"] == ORIGIN + "/register"
    assert auth["token_endpoint_auth_methods_supported"] == ["none", "client_secret_post"]
    for path in ("/mcp", "/oauth"):
        assert (await rpc(http, "invalid", path=path)).status_code == 401
    rejected = await rpc(http, "legacy-secret")
    assert f'resource_metadata="{ORIGIN}/.well-known/oauth-protected-resource/oauth"' in rejected.headers["www-authenticate"]
    assert "resource_metadata" not in (await rpc(http, "invalid", path="/mcp")).headers.get("www-authenticate", "")


@pytest.mark.parametrize("method", ["none", "client_secret_post"])
async def test_complete_flow_reuses_43_tools_and_only_bound_key(http, upstream, method):
    registration = (await register(http, method)).json()
    registration, tokens = await grant(http, registration=registration)
    assert upstream.calls[0].request.headers["X-API-Key"] == KEY
    assert not upstream.calls[0].request.url.query
    listed = payload(await rpc(http, tokens["access_token"]))
    assert len(listed["result"]["tools"]) == 43
    upstream.calls.clear()
    called = payload(await rpc(http, tokens["access_token"], "tools/call",
                               {"name": "get_api_key_subscriptions", "arguments": {}}))
    assert not called["result"].get("isError")
    assert upstream.calls[0].request.headers["X-API-Key"] == KEY
    assert (await rpc(http, tokens["access_token"], headers={"X-TickDB-Key": "other-key"})).status_code == 400
    # OAuth credentials never unlock the legacy gate.
    assert (await rpc(http, tokens["access_token"], path="/mcp")).status_code == 401
    assert client.request_api_key.get() is None


@pytest.mark.parametrize("overrides", [
    {"redirect_uris": ["https://attacker.example/callback"]},
    {"redirect_uris": ["https://chatgpt.com/connector/oauth/test-callback.evil"]},
    {"token_endpoint_auth_method": "private_key_jwt"},
    {"scope": "admin"},
])
async def test_registration_rejects_unsupported_clients(http, overrides):
    assert (await register(http, **overrides)).status_code == 400


@pytest.mark.parametrize("overrides", [
    {"resource": "https://other.example/mcp"}, {"resource": ""},
    {"code_challenge_method": "plain"}, {"code_challenge": "short"}, {"scope": "admin"},
    {"redirect_uri": "https://attacker.example/callback"},
])
async def test_authorization_rejects_invalid_requests(http, overrides):
    registration = (await register(http)).json()
    response = await http.get("/authorize", params=auth_params(registration["client_id"], **overrides))
    assert response.status_code in (302, 400)
    if response.status_code == 302:
        assert response.headers["location"].startswith(CALLBACK)
        query = parse_qs(urlsplit(response.headers["location"]).query)
        assert "error" in query
        assert query["iss"] == [ORIGIN + "/"]
        assert query["state"] == ["caller-state"]


@pytest.mark.parametrize("method", ["GET", "POST"])
@pytest.mark.parametrize("overrides", [
    {"response_type": "token"}, {"code_challenge_method": "plain"},
    {"scope": "admin"}, {"resource": "https://other.example/mcp"},
])
async def test_sdk_error_callbacks_identify_the_same_issuer(http, method, overrides):
    registration = (await register(http)).json()
    params = auth_params(registration["client_id"], **overrides)
    response = await (http.get("/authorize", params=params) if method == "GET"
                      else http.post("/authorize", data=params))
    assert response.status_code == 302, response.text
    callback = urlsplit(response.headers["location"])
    assert callback.scheme + "://" + callback.netloc + callback.path == CALLBACK
    query = parse_qs(callback.query)
    issuer = (await http.get("/.well-known/oauth-authorization-server")).json()["issuer"]
    assert query["iss"] == [issuer]
    assert query["state"] == ["caller-state"]
    assert "error" in query
    assert "code" not in query


@pytest.mark.parametrize("overrides", [
    {"client_id": "unregistered"},
    {"redirect_uri": "https://attacker.example/callback"},
    {"redirect_uri": CALLBACK + ".evil"},
])
async def test_issuer_identification_never_redirects_invalid_clients(http, overrides):
    registration = (await register(http)).json()
    response = await http.get("/authorize", params={**auth_params(registration["client_id"]), **overrides})
    assert response.status_code == 400
    assert "location" not in response.headers


async def test_explicit_legacy_callback_still_works(configuration, monkeypatch):
    callback = "https://chatgpt.com/connector/oauth/existing?tenant=example"
    monkeypatch.setattr(settings, "oauth_redirect_uris", [callback])
    async with open_http() as http:
        registration = (await register(http, redirect_uris=[callback])).json()
        response = await http.get("/authorize", params=auth_params(
            registration["client_id"], redirect_uri=callback, scope="admin"))
        assert response.status_code == 302
        query = parse_qs(urlsplit(response.headers["location"]).query)
        assert query["tenant"] == ["example"]
        assert query["iss"] == [ORIGIN + "/"]
        assert query["state"] == ["caller-state"]
        response = await http.get("/authorize", params=auth_params(
            registration["client_id"], redirect_uri=callback))
        assert response.status_code == 302
        page_response = await http.get(response.headers["location"])
        form = {field: re.search(fr'name="{field}" value="([^"]+)"', page_response.text).group(1)
                for field in ("ticket", "csrf")}
        denied = await http.post("/oauth/consent", data={**form, "action": "deny"})
        assert denied.status_code == 303
        query = parse_qs(urlsplit(denied.headers["location"]).query)
        assert query["tenant"] == ["example"]
        assert query["iss"] == [ORIGIN + "/"]


async def test_csrf_preverification_and_cancellation(http, upstream):
    registration, form = await begin(http)
    assert (await http.post("/oauth/consent", data={**form, "action": "approve"})).status_code == 400
    bad = {**form, "action": "verify", "api_key": KEY, "csrf": "wrong"}
    assert (await http.post("/oauth/consent", data=bad)).status_code == 403
    assert (await http.post("/oauth/consent", data={**form, "action": "verify", "api_key": KEY},
                            headers={"Origin": "https://attacker.example"})).status_code == 403
    assert not upstream.calls
    denied = await http.post("/oauth/consent", data={**form, "action": "deny"})
    assert denied.status_code == 303
    query = parse_qs(urlsplit(denied.headers["location"]).query)
    assert query["error"] == ["access_denied"]
    assert query["state"] == ["caller-state"]
    assert query["iss"] == [ORIGIN + "/"]
    assert (await http.post("/oauth/consent", data={**form, "action": "approve"})).status_code in (400, 403)


async def test_consent_csp_allows_the_registered_callback_redirect(http):
    registration = (await register(http)).json()
    response = await http.get("/authorize", params=auth_params(registration["client_id"]))
    page_response = await http.get(response.headers["location"])
    policy = page_response.headers["content-security-policy"]
    assert "form-action 'self' https://chatgpt.com;" in policy
    assert "frame-ancestors 'none'" in policy
    assert "form-action *" not in policy


async def test_consent_preserves_browser_form_origin_and_rejects_null(http, upstream):
    registration, form = await begin(http)
    page_response = await http.get("/oauth/consent", params={"ticket": form["ticket"]})
    assert page_response.headers["referrer-policy"] == "same-origin"
    form["csrf"] = re.search(r'name="csrf" value="([^"]+)"', page_response.text).group(1)
    submission = {**form, "action": "verify", "api_key": KEY}
    rejected = await http.post("/oauth/consent", data=submission, headers={"Origin": "null"})
    assert rejected.status_code == 403
    assert not upstream.calls
    verified = await http.post("/oauth/consent", data=submission, headers={"Origin": ORIGIN})
    assert verified.status_code == 200
    assert verified.headers["referrer-policy"] == "same-origin"
    assert "Approve connection" in verified.text
    approved = await http.post("/oauth/consent", data={**form, "action": "approve"},
                               headers={"Origin": ORIGIN})
    assert approved.status_code == 303
    assert approved.headers["referrer-policy"] == "no-referrer"
    query = parse_qs(urlsplit(approved.headers["location"]).query)
    assert query["iss"] == [ORIGIN + "/"]
    assert query["state"] == ["caller-state"]


@pytest.mark.parametrize("header,expected", [
    ("zh-CN,zh;q=0.9,en;q=0.8", "zh-CN"),
    ("zh-Hans-SG", "zh-CN"), ("zh-SG", "zh-CN"), ("zh", "zh-CN"),
    ("zh-TW", "zh-TW"), ("zh-HK", "zh-TW"), ("zh-MO", "zh-TW"),
    ("zh-Hant-HK", "zh-TW"), ("zh-Hans-TW", "zh-CN"),
    ("fr-FR,zh-TW;q=0.8", "zh-TW"), ("en-US,zh-CN;q=0.8", "en"),
    ("zh-TW;q=0.2,zh-CN;q=0.9", "zh-CN"), ("zh-TW;q=0,en", "en"),
    ("zh-TW;q=invalid,en", "en"), ("de-DE,fr;q=0.9", "en"), ("", "en"),
])
async def test_browser_language_detection(http, header, expected):
    registration = (await register(http)).json()
    authorization = await http.get("/authorize", params=auth_params(registration["client_id"]))
    response = await http.get(authorization.headers["location"], headers={"Accept-Language": header})
    assert response.status_code == 200
    assert response.headers["content-language"] == expected
    assert f'<html lang="{expected}">' in response.text
    assert f'name="lang" value="{expected}"' in response.text
    nonce = re.search(r'<script nonce="([^"]+)"', response.text).group(1)
    assert f"script-src 'nonce-{nonce}'" in response.headers["content-security-policy"]
    assert "requestSubmit()" in response.text


async def test_switch_language_preserves_verified_key_and_rotates_csrf(http, upstream):
    registration, form = await begin(http)
    verified = await http.post("/oauth/consent", data={**form, "lang": "zh-CN", "action": "verify", "api_key": KEY},
                               headers={"Origin": ORIGIN})
    assert verified.status_code == 200
    assert "确认授权连接" in verified.text
    switched = await http.get("/oauth/consent", params={"ticket": form["ticket"], "lang": "zh-TW"},
                              headers={"Accept-Language": "en-US"})
    assert switched.status_code == 200
    assert "確認授權連接" in switched.text
    assert "驗證成功" in switched.text
    assert KEY not in switched.text
    assert len(upstream.calls) == 1
    csrf = re.search(r'name="csrf" value="([^"]+)"', switched.text).group(1)
    assert csrf != form["csrf"]
    stale = await http.post("/oauth/consent", data={**form, "lang": "zh-TW", "action": "approve"},
                            headers={"Origin": ORIGIN})
    assert stale.status_code == 403
    assert "授權頁面驗證失敗" in stale.text
    approved = await http.post("/oauth/consent", data={**form, "csrf": csrf, "lang": "zh-TW", "action": "approve"},
                               headers={"Origin": ORIGIN})
    assert approved.status_code == 303
    authorization_code = parse_qs(urlsplit(approved.headers["location"]).query)["code"][0]
    token = await http.post("/token", data=token_form(registration, authorization_code))
    assert token.status_code == 200


@pytest.mark.parametrize("language,expected", [
    ("zh-CN", "请输入有效的 TickDB API Key。"),
    ("zh-TW", "請輸入有效的 TickDB API Key。"),
    ("en", "Enter a valid TickDB API Key."),
])
async def test_key_errors_follow_selected_language(http, upstream, language, expected):
    _, form = await begin(http)
    response = await http.post("/oauth/consent", data={**form, "lang": language, "action": "verify", "api_key": ""},
                               headers={"Origin": ORIGIN, "Accept-Language": "fr"})
    assert response.status_code == 400
    assert expected in response.text
    assert response.headers["content-language"] == language
    assert not upstream.calls


async def test_invalid_language_is_not_reflected_and_expired_request_is_localized(http):
    value = '"><script>alert(1)</script>'
    response = await http.get("/oauth/consent", params={"ticket": "expired", "lang": value},
                             headers={"Accept-Language": "zh-Hant"})
    assert response.status_code == 400
    assert "授權請求已過期或不存在" in response.text
    assert value not in response.text
    assert response.headers["content-language"] == "zh-TW"
    assert select_language(value, "de") == "en"


@pytest.mark.parametrize("status,body", [
    (401, {"code": "Invalid or expired token", "message": KEY}),
    (200, {"code": 1005, "message": KEY}),
    (429, {"code": 3001}), (503, {"code": 5000}),
    (200, {"code": 0, "data": None}), (200, []),
])
async def test_failed_key_validation_never_grants_or_echoes_key(http, upstream, status, body):
    upstream.get("https://api.tickdb.ai/v1/apikeys/subscriptions").mock(
        return_value=httpx.Response(status, json=body))
    _, form = await begin(http)
    response = await http.post("/oauth/consent", data={**form, "action": "verify", "api_key": KEY})
    assert response.status_code == 400
    assert KEY not in response.text
    assert (await http.post("/oauth/consent", data={**form, "action": "approve"})).status_code == 400


@pytest.mark.parametrize("overrides", [
    {"code_verifier": "b" * 64}, {"redirect_uri": "https://attacker.example/callback"},
    {"resource": "https://other.example/mcp"}, {"resource": ""},
])
async def test_exchange_binds_code_to_pkce_redirect_and_resource(http, upstream, overrides):
    registration, value = await code(http)
    assert (await http.post("/token", data=token_form(registration, value, **overrides))).status_code == 400
    response = await http.post("/token", data=token_form(registration, value))
    assert response.status_code == 200
    access = response.json()["access_token"]
    assert (await http.post("/token", data=token_form(registration, value))).status_code == 400
    assert (await rpc(http, access)).status_code == 401


async def test_code_cannot_be_exchanged_by_another_client(http, upstream):
    registration, value = await code(http)
    other = (await register(http)).json()
    assert (await http.post("/token", data=token_form(other, value))).status_code == 400


async def test_refresh_rotation_reuse_revokes_entire_grant(http, upstream):
    registration, tokens = await grant(http)
    form = {"grant_type": "refresh_token", "client_id": registration["client_id"],
            "refresh_token": tokens["refresh_token"], "resource": RESOURCE}
    fresh = await http.post("/token", data=form)
    assert fresh.status_code == 200
    assert fresh.json()["refresh_token"] != tokens["refresh_token"]
    assert (await rpc(http, fresh.json()["access_token"])).status_code == 200
    assert (await http.post("/token", data=form)).status_code == 400
    assert (await rpc(http, fresh.json()["access_token"])).status_code == 401
    assert (await rpc(http, tokens["access_token"])).status_code == 401


async def test_revocation_is_idempotent_and_cannot_revoke_other_client(http, upstream):
    registration, tokens = await grant(http)
    other = (await register(http)).json()
    response = await http.post("/revoke", data={"client_id": other["client_id"],
                                               "token": tokens["access_token"]})
    assert response.status_code == 200, response.text
    assert (await rpc(http, tokens["access_token"])).status_code == 200
    for _ in range(2):
        assert (await http.post("/revoke", data={"client_id": registration["client_id"],
                                               "token": tokens["refresh_token"]})).status_code == 200
    assert (await rpc(http, tokens["access_token"])).status_code == 401


async def test_encrypted_persistence_survives_restart(configuration, upstream):
    async with open_http() as http:
        registration, tokens = await grant(http)
    content = open(configuration.oauth_database_path, "rb").read()
    for secret in (KEY, tokens["access_token"], tokens["refresh_token"]):
        assert secret.encode() not in content
    async with open_http() as http:
        assert (await rpc(http, tokens["access_token"])).status_code == 200
        response = await http.post("/token", data={"grant_type": "refresh_token",
            "client_id": registration["client_id"], "refresh_token": tokens["refresh_token"], "resource": RESOURCE})
        assert response.status_code == 200


async def test_concurrent_users_keep_their_key_bindings(http, upstream):
    _, first = await grant(http, "first-api-key-1234")
    _, second = await grant(http, "second-api-key-5678")
    observed = []

    def ticker(request):
        observed.append(request.headers["X-API-Key"])
        return httpx.Response(200, json={"code": 0, "data": request.headers["X-API-Key"]})

    upstream.get("https://api.tickdb.ai/v1/market/ticker").mock(side_effect=ticker)
    responses = await asyncio.gather(*[
        rpc(http, tokens["access_token"], "tools/call", {"name": "get_ticker", "arguments": {"symbols": "AAPL.US"}})
        for tokens in (first, second)
    ])
    assert all(not payload(r)["result"].get("isError") for r in responses)
    assert sorted(observed) == ["first-api-key-1234", "second-api-key-5678"]


async def test_expired_token_cannot_fall_back_to_server_key(http, upstream, monkeypatch):
    _, tokens = await grant(http)
    later = time.time() + 901
    monkeypatch.setattr(time, "time", lambda: later)
    upstream.calls.clear()
    assert (await rpc(http, tokens["access_token"])).status_code == 401
    assert not upstream.calls


async def test_form_limits_malformed_json_and_rate_limit(http):
    assert (await http.get("/authorize", params={"state": "x" * 16385})).status_code == 414
    assert (await http.post("/register", content="{")).status_code == 400
    assert (await http.post("/token", content="a" * 16385)).status_code == 413
    assert (await http.post("/token", content="resource=x&resource=y",
                           headers={"Content-Type": "application/x-www-form-urlencoded"})).status_code == 400
    for _ in range(12):
        response = await register(http)
    assert response.status_code == 429
    assert response.headers["retry-after"] == "60"


def test_store_detects_wrong_key_and_resource(configuration):
    Store(configuration.oauth_database_path, configuration.oauth_encryption_key, RESOURCE)
    with pytest.raises(InvalidToken):
        Store(configuration.oauth_database_path, Fernet.generate_key().decode(), RESOURCE)
    with pytest.raises(ValueError, match="different public resource"):
        Store(configuration.oauth_database_path, configuration.oauth_encryption_key, "https://other.example/mcp")


def test_previous_oauth_resource_requires_a_separate_database(configuration, tmp_path):
    previous_path = configuration.oauth_database_path
    Store(previous_path, configuration.oauth_encryption_key, ORIGIN + "/oauth/mcp")
    with pytest.raises(ValueError, match="different public resource"):
        create_http_app()
    configuration.oauth_database_path = str(tmp_path / "oauth-v023.sqlite3")
    create_http_app()
    previous = Store(previous_path, configuration.oauth_encryption_key, ORIGIN + "/oauth/mcp")
    with previous.transaction() as db:
        assert previous.read(db, "meta", "config")["resource"] == ORIGIN + "/oauth/mcp"


@pytest.mark.parametrize("row", [
    {"status": "expired"}, {"remaining_seconds": 0},
    {"expires_at": "2026-10-01T00:00:00Z"},
])
def test_matching_subscription_expiry_uses_server_data(row):
    body = {"data": {"server_time": "2026-10-08T00:00:00Z", "api_keys": [{"key_prefix": "test-user", **row}]}}
    with pytest.raises(KeyValidationError):
        subscription_summary(body, KEY)


def test_other_key_expiry_and_nulls_are_not_inferred_as_submitted_key():
    body = {"data": {"server_time": None, "api_keys": [
        {"key_prefix": "other-key", "status": "expired"},
        {"key_prefix": "test-user", "status": "active", "remaining_seconds": None, "expires_at": None},
    ]}}
    summary = subscription_summary(body, KEY)
    assert summary["subscription"]["status"] == "active"
    assert summary["subscription"]["expires_at"] is None
    assert "other-key" not in json.dumps(summary)


@pytest.mark.parametrize("rows", [
    [], [{"key_prefix": "other-key-123", "name": "Unrelated key"}],
    [{"key_prefix": "test", "name": "Short prefix"}],
    [{"key_prefix": "test-user***", "name": "Masked prefix"}],
    [{"key_prefix": "test-user", "name": "First"},
     {"key_prefix": "test-user-api", "name": "Second", "status": "expired"}],
])
def test_unidentified_subscription_never_returns_account_records(rows):
    summary = subscription_summary({"data": {"api_keys": rows}}, KEY)
    assert summary["subscription"] is None
    assert "api_keys" not in summary
    assert all(row["name"] not in json.dumps(summary) for row in rows)


def test_selected_subscription_contains_only_public_display_fields():
    selected = {"key_prefix": "test-user", "name": "Selected key", "plan": "starter",
                "status": "active", "expires_at": None, "remaining_seconds": None,
                "id": "private-key-id", "api_key": KEY, "user_id": "private-account-id"}
    other = {"key_prefix": "other-key-123", "name": "Other enterprise key", "plan": "enterprise"}
    summary = subscription_summary({"data": {"api_keys": [other, selected]}}, KEY)
    assert set(summary["subscription"]) == {"name", "plan", "status", "expires_at", "remaining_seconds"}
    assert summary["subscription"]["name"] == "Selected key"
    assert summary["subscription"]["plan"] == "starter"
    assert all(value not in json.dumps(summary) for value in (KEY, "private-key-id", "private-account-id", other["name"]))


@pytest.mark.parametrize("language,heading", [
    ("zh-CN", "当前授权连接将使用以下 API Key"),
    ("zh-TW", "目前的授權連接將使用以下 API Key"),
    ("en", "This connection will use the following API Key"),
])
async def test_verified_page_only_displays_submitted_key(http, upstream, language, heading):
    body = {"code": 0, "data": {"api_keys": [
        {"key_prefix": "other-key-123", "name": "Hidden enterprise key", "plan": "enterprise"},
        {"key_prefix": "test-user", "name": "Selected starter key", "plan": "starter", "status": "active"},
        {"key_prefix": "another-key-456", "name": "Hidden expired key", "status": "expired"},
    ]}}
    upstream.get("https://api.tickdb.ai/v1/apikeys/subscriptions").mock(return_value=httpx.Response(200, json=body))
    _, form = await begin(http)
    response = await http.post("/oauth/consent", data={**form, "lang": language, "action": "verify", "api_key": KEY})
    assert response.status_code == 200
    assert heading in response.text
    assert masked_key(KEY) in response.text
    assert KEY not in response.text
    assert "Selected starter key" in response.text
    assert all(value not in response.text for value in ("Hidden enterprise key", "Hidden expired key", "enterprise"))
    switched = await http.get("/oauth/consent", params={"ticket": form["ticket"], "lang": language})
    assert "Selected starter key" in switched.text
    assert "Hidden enterprise key" not in switched.text


@pytest.mark.parametrize("summary", [
    {"subscription": None},
    {"server_time": "2026-10-10T00:00:00Z", "api_keys": [{"name": "Legacy account key", "plan": "enterprise"}]},
])
def test_unidentified_and_legacy_pending_summaries_only_show_masked_key(summary):
    pending = {"api_key": KEY, "summary": summary, "client_name": "ChatGPT",
               "params": {"redirect_uri": CALLBACK}}
    response = page(pending)
    html = response.body.decode()
    assert "This connection will use the following API Key" in html
    assert masked_key(KEY) in html
    assert KEY not in html
    assert "Legacy account key" not in html
    assert '<dl class="subscription">' not in html
    assert "Approve connection" in html


@pytest.mark.parametrize("key", ["a", "abcd", "12345678", KEY])
def test_key_display_never_contains_complete_secret(key):
    assert key not in masked_key(key)


@pytest.mark.parametrize("request_key", [None, "legacy-request-key"])
async def test_legacy_header_and_shared_key_behavior_with_oauth_enabled(http, upstream, request_key):
    headers = {"Host": "localhost:8000"}
    if request_key:
        headers["X-TickDB-Key"] = request_key
    called = payload(await rpc(http, "legacy-secret", "tools/call",
                               {"name": "get_api_key_subscriptions", "arguments": {}},
                               path="/mcp", headers=headers))
    assert not called["result"].get("isError")
    assert len(upstream.calls) == 1
    assert upstream.calls[0].request.headers["X-API-Key"] == (request_key or "shared-key-do-not-use")


async def test_disabled_oauth_requires_no_oauth_configuration(configuration, monkeypatch):
    monkeypatch.setattr(settings, "oauth_enabled", False)
    monkeypatch.setattr(settings, "oauth_encryption_key", "")
    monkeypatch.setattr(settings, "oauth_public_url", "")
    app = create_http_app()
    # The disabled application is precisely the existing legacy middleware stack.
    async with app.app.router.lifespan_context(app.app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost:8000") as http:
            result = payload(await rpc(http, "legacy-secret", path="/mcp"))
            assert len(result["result"]["tools"]) == 43
            assert (await http.get("/.well-known/oauth-authorization-server",
                                   headers={"Authorization": "Bearer legacy-secret"})).status_code == 404


async def test_secret_client_requires_secret_at_exchange(http, upstream):
    registration = (await register(http, "client_secret_post")).json()
    registration, value = await code(http, registration=registration)
    form = token_form(registration, value, client_secret="wrong")
    assert (await http.post("/token", data=form)).status_code == 401
    assert (await http.post("/token", data=token_form(registration, value))).status_code == 200


async def test_expired_pending_and_authorization_code(http, upstream, monkeypatch):
    _, form = await begin(http)
    registration, value = await code(http)
    now = time.time()
    monkeypatch.setattr(time, "time", lambda: now + 301)
    assert (await http.post("/token", data=token_form(registration, value))).status_code == 400
    monkeypatch.setattr(time, "time", lambda: now + 601)
    assert (await http.get("/oauth/consent", params={"ticket": form["ticket"]})).status_code == 400


async def test_two_connections_cannot_consume_same_code(configuration, upstream):
    # Independent apps/stores exercise SQLite atomicity, not just one provider instance.
    async with open_http() as first, open_http() as second:
        registration, value = await code(first)
        responses = await asyncio.gather(*[
            connection.post("/token", data=token_form(registration, value))
            for connection in (first, second)
        ])
        assert sorted(response.status_code for response in responses) == [200, 400]


async def test_unbound_oauth_context_never_falls_back(configuration):
    from mcp.server.auth.middleware.auth_context import auth_context_var
    from mcp.server.auth.middleware.bearer_auth import AuthenticatedUser
    from mcp.server.auth.provider import AccessToken

    context = auth_context_var.set(AuthenticatedUser(AccessToken(token="test", client_id="test", scopes=[])))
    try:
        with pytest.raises(RuntimeError, match="no API key binding"):
            client._get_api_key()
    finally:
        auth_context_var.reset(context)


async def test_subscription_html_is_escaped_and_raw_key_is_not_returned(http, upstream):
    malicious = {"code": 0, "data": {"api_keys": [{"key_prefix": "test-user", "name": '<script>alert("x")</script>'}]}}
    upstream.get("https://api.tickdb.ai/v1/apikeys/subscriptions").mock(
        return_value=httpx.Response(200, json=malicious))
    _, form = await begin(http)
    response = await http.post("/oauth/consent", data={**form, "action": "verify", "api_key": KEY})
    assert response.status_code == 200
    assert "<script>" not in response.text
    assert "&lt;script&gt;" in response.text
    assert KEY not in response.text
    assert response.headers["referrer-policy"] == "same-origin"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]


async def test_stdio_stays_available_without_oauth_config(tmp_path):
    import sys
    from pathlib import Path

    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    root = Path(__file__).resolve().parents[1]
    parameters = StdioServerParameters(command=sys.executable, args=[str(root / "main.py")],
        cwd=str(tmp_path), env={"MCP_TRANSPORT": "stdio", "OAUTH_ENABLED": "true",
                               "OAUTH_PUBLIC_URL": "", "OAUTH_ENCRYPTION_KEY": "", "LOG_LEVEL": "INFO"})
    async with stdio_client(parameters) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        assert len((await session.list_tools()).tools) == 43
