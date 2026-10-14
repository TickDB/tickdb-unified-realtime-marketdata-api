from mcp.server.fastmcp import FastMCP

from tickdb_mcp.tools import account, fundamentals, market, stock


def register_all(mcp: FastMCP) -> None:
    market.register(mcp)
    stock.register(mcp)
    fundamentals.register(mcp)
    account.register(mcp)
