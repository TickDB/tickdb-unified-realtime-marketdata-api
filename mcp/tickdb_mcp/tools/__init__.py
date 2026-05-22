from mcp.server.fastmcp import FastMCP

from tickdb_mcp.tools import market, stock


def register_all(mcp: FastMCP) -> None:
    market.register(mcp)
    stock.register(mcp)
