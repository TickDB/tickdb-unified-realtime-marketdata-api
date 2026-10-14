"""Structured logging configuration for TickDB MCP server.

Outputs to stderr and a daily-rotating log file under LOG_DIR (default: logs/).
File rotation: one file per day, retains LOG_RETAIN_DAYS (default 7).
"""

import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from tickdb_mcp.config import settings

_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> None:
    """Keep stdout available for stdio protocol messages; file logging is optional."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    formatter = logging.Formatter(_FORMAT, datefmt=_DATE_FORMAT)

    root = logging.getLogger("tickdb_mcp")
    root.setLevel(level)
    root.propagate = False

    # Avoid duplicate handlers on repeated calls
    if root.handlers:
        return

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    root.addHandler(stderr_handler)

    # Daily rotating file handler
    log_dir = Path(settings.log_dir)
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            filename=str(log_dir / "tickdb_mcp.log"),
            when="midnight",
            interval=1,
            backupCount=settings.log_retain_days,
            encoding="utf-8",
        )
    except OSError:
        root.warning("File logging unavailable; continuing with stderr logging")
        return
    file_handler.suffix = "%Y-%m-%d"  # tickdb_mcp.log.2026-05-19
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a child logger under the tickdb_mcp namespace."""
    return logging.getLogger(f"tickdb_mcp.{name}")
