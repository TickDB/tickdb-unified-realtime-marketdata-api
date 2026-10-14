"""HTTP regressions for the error and compression contract in the 2026-09-21 docs."""

import gzip
import json
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest

from tickdb_mcp import client


async def request_with(response, path="/v1/market/ticker", **params):
    requests = []

    def handler(request):
        requests.append(request)
        return response

    http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    with (
        patch.object(client.settings, "tickdb_api_key", "test-key"),
        patch.object(client.httpx, "AsyncClient", return_value=http),
    ):
        result = await client.get(path, **params)
    return result, requests


@pytest.mark.asyncio
async def test_business_error_on_http_200_is_not_success():
    response = httpx.Response(200, json={"code": "3011", "message": "History denied", "data": None})
    with pytest.raises(RuntimeError, match="TickDB error 3011.*History denied"):
        await request_with(response)


@pytest.mark.asyncio
async def test_error_retains_ambiguity_details_and_retry_header():
    details = {"available_types": ["stock", "indices"]}
    response = httpx.Response(
        400, json={"code": "AMBIGUOUS_SYMBOL", "message": "Ambiguous", "data": details},
        headers={"Retry-After": "3"},
    )
    with pytest.raises(RuntimeError) as caught:
        await request_with(response)
    assert "available_types" in str(caught.value)
    assert "indices" in str(caught.value)
    assert "Retry-After: 3" in str(caught.value)
    assert caught.value.status == 400
    assert caught.value.code == "AMBIGUOUS_SYMBOL"
    assert caught.value.details["data"] == details


@pytest.mark.asyncio
@pytest.mark.parametrize("code", [0, "0"])
async def test_success_preserves_envelope_pagination_and_optional_fields(code):
    body = {"code": code, "data": {"events": []}, "page": {"next_cursor": "opaque+cursor=="}}
    result, requests = await request_with(httpx.Response(200, json=body), symbol="700.HK", type=None)
    assert result == body
    assert dict(requests[0].url.params) == {"symbol": "700.HK"}
    assert requests[0].headers["X-API-Key"] == "test-key"


@pytest.mark.asyncio
async def test_gzip_ticker_response_is_decoded_without_losing_records():
    body = {"code": 0, "data": [{"symbol": "600519.SH", "open": "1234.00"}]}
    response = httpx.Response(
        200, stream=httpx.ByteStream(gzip.compress(json.dumps(body).encode())),
        headers={"Content-Encoding": "gzip"},
    )
    result, requests = await request_with(response, "/v1/market/ticker", symbols="600519.SH")
    assert requests[0].headers["Accept-Encoding"] == "gzip"
    assert result == body


@pytest.mark.asyncio
@pytest.mark.parametrize("status,body", [(503, "unavailable"), (200, "<html>proxy</html>")])
async def test_non_json_is_actionable_http_error(status, body):
    with pytest.raises(RuntimeError, match=f"HTTP {status}.*JSON"):
        await request_with(httpx.Response(status, text=body))


@pytest.mark.asyncio
@pytest.mark.parametrize("body", [[], {"data": {}}, None])
async def test_invalid_envelope_is_rejected(body):
    with pytest.raises(RuntimeError, match="response envelope"):
        await request_with(httpx.Response(200, content=json.dumps(body)))


@pytest.mark.asyncio
async def test_http_failure_cannot_be_hidden_by_success_code():
    with pytest.raises(RuntimeError, match="HTTP 503"):
        await request_with(httpx.Response(503, json={"code": 0, "message": "unavailable"}))


DOCUMENTED_CODES = json.loads(
    (Path(__file__).parent / "fixtures/api_contract_v021.json").read_text()
)["error_codes"]


@pytest.mark.asyncio
@pytest.mark.parametrize("code", DOCUMENTED_CODES)
async def test_every_documented_error_has_a_hint_and_preserves_the_message(code):
    representations = [code, int(code)] if code.isdecimal() else [code]
    messages = []
    for value in representations:
        with pytest.raises(client.TickDBAPIError) as caught:
            await request_with(httpx.Response(400, json={"code": value, "message": "upstream detail"}))
        error = caught.value
        assert error.code == code
        assert error.status == 400
        assert "upstream detail" in str(error)
        assert " — " in str(error), f"Missing documented hint for {code}"
        messages.append(str(error))
    assert len(set(messages)) == 1


@pytest.mark.asyncio
async def test_unknown_business_error_is_preserved_on_http_success():
    with pytest.raises(client.TickDBAPIError, match="TickDB error FUTURE_CODE: new error") as caught:
        await request_with(httpx.Response(200, json={"code": "FUTURE_CODE", "message": "new error"}))
    assert caught.value.status == 200


@pytest.mark.asyncio
async def test_rate_limit_retains_retry_after():
    with pytest.raises(client.TickDBAPIError) as caught:
        await request_with(httpx.Response(
            429, json={"code": 3001, "message": "slow down"}, headers={"Retry-After": "10"},
        ))
    assert caught.value.retry_after == "10"
    assert "Retry-After: 10" in str(caught.value)


@pytest.mark.asyncio
async def test_gateway_invalid_key_alias_uses_documented_code_and_keeps_raw_response():
    body = {
        "error": "Invalid or expired token",
        "message": "[1001] Invalid or expired token",
        "code": "Invalid or expired token",
    }
    with pytest.raises(client.TickDBAPIError) as caught:
        await request_with(httpx.Response(401, json=body))
    error = caught.value
    assert error.code == "1001"
    assert error.status == 401
    assert error.details == body
    assert body["message"] in str(error)
    assert "API key invalid" in str(error)


@pytest.mark.asyncio
@pytest.mark.parametrize("status,code", [
    (200, "Invalid or expired token"),
    (403, "Invalid or expired token"),
    (500, "Invalid or expired token"),
    (401, "FUTURE_CODE"),
    (401, 1005),
    (401, "INVALID_TOKEN"),
    (401, "invalid or expired token"),
])
async def test_auth_compatibility_does_not_infer_codes_from_message(status, code):
    body = {"code": code, "message": "[1001] Invalid or expired token"}
    with pytest.raises(client.TickDBAPIError) as caught:
        await request_with(httpx.Response(status, json=body))
    assert caught.value.code == str(code)
    assert caught.value.details == body
