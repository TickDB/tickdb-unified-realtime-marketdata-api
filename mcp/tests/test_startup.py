"""Verify secure defaults and the actual console entrypoint's transport selection."""

import os
from unittest.mock import Mock

import pytest

import main as entry
from tickdb_mcp import client
from tickdb_mcp.config import Settings


@pytest.fixture
def default_settings(monkeypatch):
    # Settings reads case-insensitive process environment as well as .env by default.
    field_names = {name.upper() for name in Settings.model_fields}
    for name in list(os.environ):
        if name.upper() in field_names:
            monkeypatch.delenv(name)
    return Settings(_env_file=None)


def test_default_http_entrypoint_only_binds_loopback(monkeypatch, default_settings):
    assert default_settings.mcp_transport == "streamable-http"
    assert default_settings.mcp_host == "127.0.0.1"
    assert default_settings.mcp_port == 8000
    assert default_settings.mcp_access_token == ""
    assert default_settings.tickdb_api_key == ""
    app_factory, run = Mock(), Mock()
    monkeypatch.setattr(entry, "settings", default_settings)
    monkeypatch.setattr(entry, "setup_logging", Mock())
    monkeypatch.setattr(entry, "get_logger", Mock())
    monkeypatch.setattr(entry, "create_http_app", app_factory)
    monkeypatch.setattr(entry.uvicorn, "run", run)
    entry.main()
    app_factory.assert_called_once_with()
    run.assert_called_once_with(app_factory.return_value, host="127.0.0.1", port=8000)


def test_stdio_keeps_environment_key_without_starting_http(monkeypatch, default_settings):
    default_settings.mcp_transport = "stdio"
    default_settings.tickdb_api_key = "test-stdio-only-key"
    app_factory, http_run, mcp_factory = Mock(), Mock(), Mock()

    def run_stdio(*, transport):
        assert transport == "stdio"
        assert client._get_api_key() == "test-stdio-only-key"

    mcp_factory.return_value.run.side_effect = run_stdio
    monkeypatch.setattr(entry, "settings", default_settings)
    monkeypatch.setattr(client, "settings", default_settings)
    monkeypatch.setattr(entry, "setup_logging", Mock())
    monkeypatch.setattr(entry, "get_logger", Mock())
    monkeypatch.setattr(entry, "create_http_app", app_factory)
    monkeypatch.setattr(entry, "create_mcp", mcp_factory)
    monkeypatch.setattr(entry.uvicorn, "run", http_run)
    token = client.request_api_key.set(None)
    try:
        entry.main()
    finally:
        client.request_api_key.reset(token)
    mcp_factory.return_value.run.assert_called_once_with(transport="stdio")
    app_factory.assert_not_called()
    http_run.assert_not_called()
