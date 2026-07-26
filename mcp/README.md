# Custom MCP Server

A small [Model Context Protocol](https://modelcontextprotocol.io) server that gives
the agent two tools which the **managed** Databricks MCP servers don't cover:

| Tool | What it returns |
|------|-----------------|
| `support_tickets(customer_id, limit)` | Recent service tickets for a customer |
| `external_banking_info(topic)` | Reference info (decline reasons, rates, policies) — stand-in for a core-banking/partner API |

## Managed vs custom MCP — when to use which

- **Managed MCP servers** (built into Databricks) expose **Unity Catalog functions,
  Genie, AI Search, and DBSQL** with zero infrastructure and Unity Catalog
  permissions enforced on every call. Use these for anything already in the lakehouse.
  Our four UC functions are automatically available at
  `https://<host>/api/2.0/mcp/functions/banking_ai/tools`.
- **A custom MCP server** (this folder) is for logic/data **outside** the lakehouse —
  a third-party API, bespoke Python, or a service you own. That's exactly the
  `external_banking_info` use case.

## Files
- `tools.py` — the tool logic (Databricks SQL with a local-CSV fallback).
- `mcp_server.py` — wraps the logic in a FastMCP server.
- `mcp_config.json` — client config (stdio launch + managed server URLs).

## Run it

```bash
pip install "mcp>=1.2.0" databricks-sql-connector
# Local/offline (uses ../data_generation/sample_data/*.csv):
python mcp_server.py                 # stdio transport (for MCP clients)
python mcp_server.py --http          # streamable-http on :8000 (for the MCP Inspector)

# Query real Delta tables instead of CSVs:
export DATABRICKS_HOST="https://<workspace-host>"
export DATABRICKS_TOKEN="<pat>"
export DATABRICKS_HTTP_PATH="/sql/1.0/warehouses/<warehouse_id>"
python mcp_server.py
```

## Test without a client

```bash
python tools.py        # smoke test of both tools
```

## Wire it into the agent
Deploy this server (e.g. as a **Databricks App**) and set `custom_mcp_url` in
`../mosaic_ai_agent/model_config.py`. The agent's `ToolRegistry` will discover its
tools alongside the managed UC-function tools.

## Notes
- `external_banking_info` is intentionally a static dictionary so the demo is
  deterministic and offline-friendly. Swap `EXTERNAL_BANKING_INFO` for a real HTTP
  call to make it live.
- Permissions still apply: when `support_tickets` queries Delta, the connection's
  identity must have `SELECT` on `banking_ai.core.support_tickets`.
