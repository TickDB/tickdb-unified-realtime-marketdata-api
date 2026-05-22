"""Structured logging configuration for TickDB MCP server.

Outputs to both stdout and a daily-rotating log file under logs/.
File rotation: one file per day, retains LOG_RETAIN_DAYS (default 7).
"""

import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from tickdb_mcp.config import settings

_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOG_FILE = _LOG_DIR / "tickdb_mcp.log"


def setup_logging() -> None:
    """Configure logger with stdout + daily rotating file handler."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    formatter = logging.Formatter(_FORMAT, datefmt=_DATE_FORMAT)

    root = logging.getLogger("tickdb_mcp")
    root.setLevel(level)
    root.propagate = False

    # Avoid duplicate handlers on repeated calls
    if root.handlers:
        return

    # stdout handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    root.addHandler(stdout_handler)

    # Daily rotating file handler
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = TimedRotatingFileHandler(
        filename=str(_LOG_FILE),
        when="midnight",
        interval=1,
        backupCount=settings.log_retain_days,
        encoding="utf-8",
    )
    file_handler.suffix = "%Y-%m-%d"  # tickdb_mcp.log.2026-05-19
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a child logger under the tickdb_mcp namespace."""
    return logging.getLogger(f"tickdb_mcp.{name}")
