"""
mcp_server.py
-------------
A minimal, custom MCP (Model Context Protocol) server exposing two tools:

    get_support_tickets(customer_id, limit)
    get_external_banking_info(topic)

Why a CUSTOM server when Databricks has managed MCP servers?
  - Managed MCP servers expose *Unity Catalog functions, Genie, AI Search, DBSQL*.
    Great for governed data already in the lakehouse.
  - You build a custom MCP server when a tool needs to reach OUTSIDE the lakehouse
    (a third-party/core-banking API, a partner service, bespoke Python logic).
  This file demonstrates that pattern with a stand-in "external info" source.

RUN IT (stdio transport — how most MCP clients launch a server):
    pip install "mcp>=1.2.0"
    python mcp_server.py

RUN IT (HTTP, for quick manual testing with the MCP Inspector):
    python mcp_server.py --http    # serves streamable-http on :8000

TEST without a client:
    python -m mcp.tools            # or: python tools.py  (smoke test)
See README.md in this folder for wiring it into an agent.
"""
from __future__ import annotations

import sys

try:
    from mcp.server.fastmcp import FastMCP
except Exception as e:  # pragma: no cover
    raise SystemExit(
        "The 'mcp' package is required. Install with:  pip install 'mcp>=1.2.0'\n"
        f"Original import error: {e}"
    )

# Import our logic. Support both `python mcp_server.py` and package import.
try:
    from tools import get_support_tickets, get_external_banking_info
except ImportError:
    from mcp.tools import get_support_tickets, get_external_banking_info  # type: ignore

# The server name is what shows up in the client's tool list.
mcp = FastMCP("novabank-external")


@mcp.tool()
def support_tickets(customer_id: str, limit: int = 5) -> dict:
    """Retrieve recent customer support tickets for a NovaBank customer.

    Args:
        customer_id: Customer ID like CUST000001.
        limit: Max tickets to return (default 5).

    Use when the customer references a past complaint, an open case, or you need
    service history to answer their question.
    """
    return get_support_tickets(customer_id, limit)


@mcp.tool()
def external_banking_info(topic: str) -> dict:
    """Look up external/reference banking information not stored in the lakehouse.

    Args:
        topic: A short topic such as 'credit card decline reasons',
               'interest rates', 'credit utilization guidance', 'card block policy',
               or 'dispute process'.

    Use for policy explanations, indicative rates, or general guidance that isn't
    specific to one customer's records.
    """
    return get_external_banking_info(topic)


def main() -> None:
    if "--http" in sys.argv:
        # Streamable HTTP transport for the MCP Inspector / remote clients.
        mcp.run(transport="streamable-http")
    else:
        # Default: stdio, launched by the MCP client as a subprocess.
        mcp.run()


if __name__ == "__main__":
    main()
