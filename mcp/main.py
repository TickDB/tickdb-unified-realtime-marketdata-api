"""Entry point for the TickDB MCP server.

Usage:
    python main.py                          # HTTP server on port 8000
    MCP_PORT=8123 python main.py            # custom port
    MCP_TRANSPORT=stdio python main.py      # stdio for Claude Desktop
"""

import uvicorn

from tickdb_mcp.config import settings
from tickdb_mcp.logging import get_logger, setup_logging
from tickdb_mcp.middleware import AuthMiddleware
from tickdb_mcp.server import create_mcp


def main() -> None:
    setup_logging()
    logger = get_logger("main")

    logger.info("TickDB MCP Server starting...")
    logger.info(
        "config: transport=%s host=%s port=%d log_level=%s auth=%s",
        settings.mcp_transport,
        settings.mcp_host,
        settings.mcp_port,
        settings.log_level,
        "enabled" if settings.mcp_access_token else "disabled",
    )
    logger.info(
        "api_key: %s",
        "configured (env)" if settings.tickdb_api_key else "not set (require per-request header)",
    )

    mcp = create_mcp()

    if settings.mcp_transport == "stdio":
        logger.info("Running in stdio mode (local)")
        mcp.run(transport="stdio")
    else:
        logger.info("Running in HTTP mode on %s:%d", settings.mcp_host, settings.mcp_port)
        asgi_app = mcp.streamable_http_app()
        app = AuthMiddleware(asgi_app)
        uvicorn.run(app, host=settings.mcp_host, port=settings.mcp_port)


if __name__ == "__main__":
    main()
