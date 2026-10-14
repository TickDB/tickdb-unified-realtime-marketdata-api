"""Logging must not corrupt stdio or require a writable installed package."""

import logging

import pytest

from tickdb_mcp import logging as server_logging


@pytest.fixture
def isolated_logging(monkeypatch, tmp_path):
    root = logging.getLogger("tickdb_mcp")
    monkeypatch.setattr(root, "handlers", [])
    monkeypatch.setattr(root, "level", root.level)
    monkeypatch.setattr(root, "propagate", root.propagate)
    monkeypatch.setattr(server_logging.settings, "log_level", "INFO")
    monkeypatch.setattr(server_logging.settings, "log_dir", str(tmp_path / "logs"))
    yield tmp_path / "logs"
    for handler in root.handlers:
        handler.close()


def test_info_logging_uses_stderr_and_configured_directory(isolated_logging, capsys):
    server_logging.setup_logging()
    server_logging.get_logger("test").info("stdio-safe startup")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "stdio-safe startup" in captured.err
    assert "stdio-safe startup" in (isolated_logging / "tickdb_mcp.log").read_text()


def test_unwritable_log_file_does_not_prevent_startup(isolated_logging, monkeypatch, capsys):
    def unavailable(*args, **kwargs):
        raise PermissionError("read-only working directory")

    monkeypatch.setattr(server_logging, "TimedRotatingFileHandler", unavailable)
    server_logging.setup_logging()
    server_logging.get_logger("test").info("server can start")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "File logging unavailable" in captured.err
    assert "server can start" in captured.err
