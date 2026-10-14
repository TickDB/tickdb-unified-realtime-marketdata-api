"""Unit tests for bounded MCP session lifecycle logging."""

from unittest.mock import patch

import pytest

import tickdb_mcp.middleware as middleware


@pytest.fixture(autouse=True)
def reset_known_sessions():
    middleware._known_sessions.clear()
    middleware._last_session_cleanup = 0.0
    yield
    middleware._known_sessions.clear()
    middleware._last_session_cleanup = 0.0


def test_session_log_cache_is_bounded_by_max_entries():
    with (
        patch.object(middleware.settings, "mcp_session_log_max_entries", 2),
        patch.object(middleware.settings, "mcp_session_log_ttl_seconds", 3600),
    ):
        middleware._remember_known_session("a", now=1)
        middleware._remember_known_session("b", now=2)
        middleware._remember_known_session("c", now=3)

    assert list(middleware._known_sessions) == ["b", "c"]


def test_session_log_cache_prunes_expired_entries():
    with (
        patch.object(middleware.settings, "mcp_session_log_max_entries", 10),
        patch.object(middleware.settings, "mcp_session_log_ttl_seconds", 10),
    ):
        middleware._remember_known_session("old", now=0)
        middleware._remember_known_session("fresh", now=7)
        middleware._prune_known_sessions(now=17)

    assert list(middleware._known_sessions) == ["fresh"]


def test_touch_known_session_refreshes_lru_position():
    with (
        patch.object(middleware.settings, "mcp_session_log_max_entries", 2),
        patch.object(middleware.settings, "mcp_session_log_ttl_seconds", 3600),
    ):
        middleware._remember_known_session("a", now=1)
        middleware._remember_known_session("b", now=2)

        assert middleware._touch_known_session("a", now=3) is True

        middleware._remember_known_session("c", now=4)

    assert list(middleware._known_sessions) == ["a", "c"]
    assert middleware._touch_known_session("missing", now=5) is False
