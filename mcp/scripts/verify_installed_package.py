"""Verify a wheel installation from outside the source tree, without real API keys.

Run with the isolated environment's Python after installing the wheel:
    /tmp/tickdb-wheel/bin/python /path/to/mcp/scripts/verify_installed_package.py

Upstream API calls are mocked. The real console process is only asked to
initialize, discover tools, or reject unauthenticated access.
"""

import argparse
import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import sysconfig
import tempfile
import time
from contextlib import asynccontextmanager, chdir
from importlib.metadata import distribution, version
from pathlib import Path
from unittest.mock import patch

import httpx
from cryptography.fernet import Fernet

ACCEPT = {"Accept": "application/json, text/event-stream"}
INIT = {
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {"protocolVersion": "2025-03-26", "capabilities": {},
               "clientInfo": {"name": "installed-package-check", "version": "1"}},
}
CALL = {
    "jsonrpc": "2.0", "id": 2, "method": "tools/call",
    "params": {"name": "get_ticker", "arguments": {"symbols": "AAPL.US"}},
}
LIST = {"jsonrpc": "2.0", "id": 3, "method": "tools/list", "params": {}}
SHARED_KEY = "dummy-server-key-for-package-check"
ACCESS_TOKEN = "dummy-access-token-for-package-check"


def clean_environment():
    return {
        name: value for name, value in os.environ.items()
        if not name.upper().startswith(("TICKDB_", "MCP_", "OAUTH_", "FASTMCP_", "LOG_"))
        and name.upper() != "PYTHONPATH"
    }


def payload(response):
    assert response.status_code == 200, response.text
    if "text/event-stream" in response.headers.get("content-type", ""):
        return json.loads(next(
            line[6:] for line in response.text.splitlines() if line.startswith("data: ")
        ))
    return response.json()


def tool_data(response):
    result = payload(response)["result"]
    assert not result.get("isError"), result
    return json.loads(result["content"][0]["text"])


async def verify_http(settings, client, create_http_app, temporary):
    original_client = httpx.AsyncClient
    upstream_keys = []
    checks = []

    def upstream(request):
        assert request.url.host == "api.tickdb.ai"
        assert request.url.path == "/v1/market/ticker"
        key = request.headers["X-API-Key"]
        assert key in {SHARED_KEY, "dummy-request-a", "dummy-request-b"}
        upstream_keys.append(key)
        return httpx.Response(200, json={"code": 0, "data": [{"audit_key": key}]})

    def mocked_client(**kwargs):
        return original_client(transport=httpx.MockTransport(upstream), **kwargs)

    @asynccontextmanager
    async def connection(*, shared="", token="", oauth=False):
        settings.tickdb_api_key = shared
        settings.mcp_access_token = token
        settings.oauth_enabled = oauth
        if oauth:
            settings.oauth_public_url = "https://mcp.example.com"
            settings.oauth_redirect_uris = ["https://client.example.com/callback"]
            settings.oauth_encryption_key = Fernet.generate_key().decode()
            settings.oauth_database_path = str(temporary / "oauth.sqlite3")
        app = create_http_app()
        lifecycle = app if oauth else app.app
        async with lifecycle.router.lifespan_context(lifecycle):
            # A remote client can forge localhost Host; this must not grant access.
            async with original_client(
                transport=httpx.ASGITransport(app=app, client=("192.0.2.20", 40000)),
                base_url="http://localhost:8000", headers=ACCEPT,
            ) as http:
                yield http

    with (
        patch.object(client.httpx, "AsyncClient", side_effect=mocked_client),
        patch("socket.socket.connect", side_effect=AssertionError("Unexpected real network request")),
        patch("socket.socket.connect_ex", side_effect=AssertionError("Unexpected real network request")),
    ):
        async with connection() as http:
            assert "serverInfo" in payload(await http.post("/mcp", json=INIT))["result"]
            assert len(payload(await http.post("/mcp", json=LIST))["result"]["tools"]) == 43
            result = payload(await http.post("/mcp", json=CALL))["result"]
            assert result["isError"] and "No TickDB API key provided" in result["content"][0]["text"]
            assert not upstream_keys
        checks.append("anonymous_discovery_without_key_cannot_query")

        async with connection(shared=SHARED_KEY) as http:
            for headers in ({}, {"Authorization": "Bearer arbitrary"}):
                for body in (INIT, CALL):
                    assert (await http.post("/mcp", headers=headers, json=body)).status_code == 401
            assert not upstream_keys
            replies = await asyncio.gather(*[
                http.post("/mcp", headers={"X-TickDB-Key": key}, json=CALL)
                for key in ("dummy-request-a", "dummy-request-b")
            ])
            for response, key in zip(replies, ("dummy-request-a", "dummy-request-b"), strict=True):
                assert tool_data(response)["data"][0]["audit_key"] == key
            assert sorted(upstream_keys) == ["dummy-request-a", "dummy-request-b"]
        checks.extend(["anonymous_shared_key_rejected", "concurrent_byok_isolated"])

        async with connection(shared=SHARED_KEY, token=ACCESS_TOKEN) as http:
            before = len(upstream_keys)
            for headers in ({}, {"Authorization": "Bearer wrong", "X-TickDB-Key": "dummy-request-a"}):
                assert (await http.post("/mcp", headers=headers, json=CALL)).status_code == 401
            assert len(upstream_keys) == before
            headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
            assert tool_data(await http.post("/mcp", headers=headers, json=CALL))["data"][0]["audit_key"] == SHARED_KEY
            headers["X-TickDB-Key"] = "dummy-request-a"
            assert tool_data(await http.post("/mcp", headers=headers, json=CALL))["data"][0]["audit_key"] == "dummy-request-a"
        checks.append("bearer_required_for_shared_key_and_byok_keeps_priority")

        async with connection(shared=SHARED_KEY, oauth=True) as http:
            before = len(upstream_keys)
            assert (await http.post("/mcp", json=INIT)).status_code == 401
            assert (await http.post("/mcp", json=CALL)).status_code == 401
            assert (await http.post("/oauth", headers={"Host": "mcp.example.com"}, json=CALL)).status_code == 401
            assert len(upstream_keys) == before
        checks.append("oauth_does_not_leave_legacy_shared_key_open")
    assert client.request_api_key.get() is None
    return checks


def verify_console(temporary, shared_key):
    console = Path(sysconfig.get_path("scripts")) / ("tickdb-mcp.exe" if os.name == "nt" else "tickdb-mcp")
    assert console.is_file(), console
    environment = clean_environment()
    environment.update(MCP_PORT="0", LOG_DIR=str(temporary / "console-logs"))
    if shared_key:
        environment["TICKDB_API_KEY"] = SHARED_KEY
    log_path = temporary / ("console-shared.log" if shared_key else "console-default.log")
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [str(console)], cwd=temporary, env=environment,
            stdout=subprocess.DEVNULL, stderr=log,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        try:
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                output = re.sub(
                    r"\x1b\[[0-?]*[ -/]*[@-~]", "",
                    log_path.read_text(encoding="utf-8", errors="replace"),
                )
                match = re.search(r"Uvicorn running on http://127\.0\.0\.1:(\d+)", output)
                if match:
                    break
                assert process.poll() is None, output
                time.sleep(0.05)
            else:
                raise AssertionError(f"Console did not start on loopback: {output}")
            with httpx.Client(trust_env=False, timeout=5, headers=ACCEPT) as http:
                endpoint = f"http://127.0.0.1:{match[1]}/mcp"
                initialized = http.post(endpoint, json=INIT)
                if shared_key:
                    assert initialized.status_code == 401, initialized.text
                else:
                    assert "serverInfo" in payload(initialized)["result"]
                    assert len(payload(http.post(endpoint, json=LIST))["result"]["tools"]) == 43
        finally:
            if process.poll() is None:
                if os.name == "nt":
                    # Windows console launchers may own a separate Python process.
                    # Terminate only the tree rooted at the PID this check started.
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW, check=False,
                    )
                else:
                    process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional JSON verification receipt")
    args = parser.parse_args()
    output_path = args.output.resolve() if args.output else None
    previous_directory = Path.cwd()
    previous_environment = dict(os.environ)
    environment = clean_environment()
    try:
        os.environ.clear()
        os.environ.update(environment)
        # Restore cwd before TemporaryDirectory attempts cleanup on Windows.
        with tempfile.TemporaryDirectory(prefix="tickdb-wheel-check-") as directory, chdir(directory):
            temporary = Path(directory)
            # Neither application nor SDK may read the checkout's .env.
            import main as entry
            from tickdb_mcp import client
            from tickdb_mcp.config import settings
            from tickdb_mcp.http import create_http_app

            logging.disable(logging.CRITICAL)
            installed_root = Path(sys.prefix).resolve()
            assert Path(entry.__file__).resolve().is_relative_to(installed_root), entry.__file__
            assert Path(client.__file__).resolve().is_relative_to(installed_root), client.__file__
            console = next(e for e in distribution("tickdb-mcp").entry_points if e.name == "tickdb-mcp")
            assert console.value == "main:main" and console.load() is entry.main
            assert (settings.mcp_host, settings.mcp_port, settings.mcp_transport) == ("127.0.0.1", 8000, "streamable-http")
            assert not settings.tickdb_api_key and not settings.mcp_access_token
            with patch.object(entry, "setup_logging"), patch.object(entry.uvicorn, "run") as run:
                entry.main()
                assert run.call_args.kwargs == {"host": "127.0.0.1", "port": 8000}
            checks = ["installed_console_entry_and_safe_defaults"]
            checks.extend(asyncio.run(verify_http(settings, client, create_http_app, temporary)))
            settings.mcp_transport = "stdio"
            with (
                patch.object(entry, "setup_logging"),
                patch.object(entry, "create_mcp") as create,
                patch.object(entry, "create_http_app") as http_app,
                patch.object(entry.uvicorn, "run") as run,
            ):
                entry.main()
                create.return_value.run.assert_called_once_with(transport="stdio")
                assert not run.called and not http_app.called
            checks.append("stdio_starts_no_http")
            verify_console(temporary, shared_key=False)
            verify_console(temporary, shared_key=True)
            checks.append("real_console_binds_loopback_and_rejects_anonymous_shared_key")
            receipt = {
                "status": "passed", "package_version": version("tickdb-mcp"),
                "mcp_version": version("mcp"), "python_version": sys.version.split()[0],
                "upstream": "mocked_only", "checks": checks,
            }
    finally:
        os.chdir(previous_directory)
        os.environ.clear()
        os.environ.update(previous_environment)
    if output_path:
        output_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
