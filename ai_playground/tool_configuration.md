# AI Playground — Tool Configuration

Two kinds of tools, both attached from the Playground UI.

## A. Unity Catalog function tools (governed SQL)

Prerequisite: you ran `notebooks/03_create_uc_functions.py`, so these exist:

- `banking_ai.tools.get_customer_balance`
- `banking_ai.tools.calculate_credit_utilization`
- `banking_ai.tools.get_recent_transactions`
- `banking_ai.tools.check_transaction_status`

**Attach them:**

1. Open **Playground** and pick a tool-calling model.
2. Click **Tools → Add tool → Unity Catalog function**.
3. Search `banking_ai.tools` and add all four functions.
4. (Optional) Add built-in `system.ai.python_exec` if you want the model to do
   arithmetic in a sandbox.

Unity Catalog checks that *you* (the Playground caller) have `EXECUTE` on each
function and `SELECT` on the underlying table on **every** call. If a tool
returns a permission error, revisit `setup/grant_permissions.sql`.

## B. MCP tools

You can give the Playground agent MCP tools in two ways.

### B1. Managed MCP server (recommended — no server to run)

Databricks exposes your UC functions as an MCP server automatically at:

```
https://<workspace-host>/api/2.0/mcp/functions/banking_ai/tools
```

Each function shows up as a tool named `banking_ai__tools__<function_name>`.
AI Search indexes and Genie spaces get their own managed URLs
(`/api/2.0/mcp/ai-search/...`, `/api/2.0/mcp/genie/<space_id>`). Add the server
under **Tools → Add tool → MCP server** and paste the URL.

### B2. Custom MCP server (for data outside the lakehouse)

Our custom server (`mcp/mcp_server.py`) exposes `support_tickets` and
`external_banking_info`. In Playground you typically consume a custom server by
deploying it (e.g. as a Databricks App) and registering its URL, or by testing it
from agent code (see `mosaic_ai_agent/tools.py`). For pure Playground
experimentation, the managed UC-function server above is usually enough; the
custom server shines in the code-based agent.

## How the model decides to call a tool (mental model)

```
user question
   │
   ▼
model sees: system prompt + list of tools (name, description, params)
   │
   ├─ needs live data?  ──► emits a tool call  ──► Databricks runs the UC function
   │                                                (UC permission check here)
   │                                                        │
   │                        tool result (rows) ◄────────────┘
   ▼
model reads the tool result and writes the final natural-language answer
```

The model may loop this several times (multi-tool) before answering. In
Playground, expand each response to see the **tool call trace** — the arguments
it chose and the rows it got back. That trace is your #1 debugging aid.
