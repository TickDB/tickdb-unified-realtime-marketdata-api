"""Unit tests for tickdb_mcp.client key resolution logic."""

from unittest.mock import patch

import pytest

import tickdb_mcp.client as client


@pytest.fixture(autouse=True)
def reset_context_var():
    """Ensure request_api_key context var is clean between tests."""
    token = client.request_api_key.set(None)
    yield
    client.request_api_key.reset(token)


class TestKeyResolutionPriority:
    def test_request_key_takes_priority(self):
        """X-TickDB-Key header beats env key."""
        client.request_api_key.set("request-key")

        with patch.object(client.settings, "tickdb_api_key", "env-key"):
            key = client._get_api_key()

        assert key == "request-key"

    def test_env_key_used_when_no_request_key(self):
        """Env var key is used when no per-request key is set."""
        with patch.object(client.settings, "tickdb_api_key", "env-key"):
            key = client._get_api_key()

        assert key == "env-key"

    def test_raises_when_no_key_provided(self):
        """RuntimeError is raised when neither request nor env key is set."""
        with patch.object(client.settings, "tickdb_api_key", ""):
            with pytest.raises(RuntimeError, match="No TickDB API key provided"):
                client._get_api_key()

    def test_error_message_includes_registration_url(self):
        """Missing key error guides user to register."""
        with patch.object(client.settings, "tickdb_api_key", ""):
            with pytest.raises(RuntimeError, match="https://tickdb.ai"):
                client._get_api_key()


class TestErrorHandling:
    def test_known_error_code_includes_hint(self):
        with pytest.raises(RuntimeError, match="https://tickdb.ai"):
            client._raise(1001, "Invalid key")

    def test_unknown_error_code_no_hint(self):
        with pytest.raises(RuntimeError, match="TickDB error 9999: something"):
            client._raise(9999, "something")

    def test_non_numeric_code(self):
        with pytest.raises(RuntimeError, match="TickDB error ERR: bad"):
            client._raise("ERR", "bad")


class TestMaskKey:
    def test_long_key_masked(self):
        masked = client._mask_key("abcd1234efgh5678")
        assert masked == "abcd***5678"
        assert "1234efgh" not in masked

    def test_short_key_masked(self):
        masked = client._mask_key("abc")
        assert "***" in masked
        assert masked.startswith("ab")

    def test_exactly_8_chars(self):
        masked = client._mask_key("12345678")
        assert "***" in masked
