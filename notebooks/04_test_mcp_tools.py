# Databricks notebook source
# MAGIC %md
# MAGIC # 04 · Test MCP Tools
# MAGIC
# MAGIC Two kinds of MCP tools power our agent:
# MAGIC 1. **Managed MCP server** — Databricks auto-exposes our UC functions at
# MAGIC    `/api/2.0/mcp/functions/banking_ai/tools`. No server to run.
# MAGIC 2. **Custom MCP server** — `../mcp/mcp_server.py` adds `support_tickets` and
# MAGIC    `external_banking_info` (data outside the lakehouse).
# MAGIC
# MAGIC This notebook lists + calls tools from the managed server, and smoke-tests the
# MAGIC custom server's logic locally.

# COMMAND ----------

# MAGIC %pip install databricks-mcp>=0.2.0
# MAGIC %restart_python

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksMCPClient

ws = WorkspaceClient()
host = ws.config.host
uc_url = f"{host}/api/2.0/mcp/functions/banking_ai/tools"
print("Managed MCP server:", uc_url)

client = DatabricksMCPClient(server_url=uc_url, workspace_client=ws)

# COMMAND ----------

# MAGIC %md
# MAGIC ## List the tools the managed server exposes
# MAGIC Each UC function becomes a tool named `banking_ai__tools__<function_name>`.

# COMMAND ----------

tools = client.list_tools()
for t in tools:
    print("-", t.name)
    print("   ", (t.description or "")[:100])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Call a tool through MCP (the flagship pieces)

# COMMAND ----------

res = client.call_tool(
    "banking_ai__tools__check_transaction_status",
    {"input_transaction_id": "TXN00000010"},
)
for block in res.content:
    print(getattr(block, "text", block))

# COMMAND ----------

res = client.call_tool(
    "banking_ai__tools__calculate_credit_utilization",
    {"input_customer_id": "CUST000481"},
)
for block in res.content:
    print(getattr(block, "text", block))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Custom MCP server — test the tool logic locally
# MAGIC (We test the functions directly here; to run the full server, launch
# MAGIC `python ../mcp/mcp_server.py` and connect a client, or deploy it as a
# MAGIC Databricks App and set `custom_mcp_url` in `model_config.py`.)

# COMMAND ----------

import os, sys
REPO_ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "mcp"))

# Point the tool at Delta by setting env vars (else it uses the local CSV fallback).
os.environ["DATABRICKS_HOST"] = host
# os.environ["DATABRICKS_TOKEN"] = dbutils.secrets.get("scope", "token")   # recommended
# os.environ["DATABRICKS_HTTP_PATH"] = "/sql/1.0/warehouses/<warehouse_id>"

from tools import get_external_banking_info, get_support_tickets  # from ../mcp/tools.py

print(get_external_banking_info("credit card decline reasons")["info"])
print("---")
print(get_support_tickets("CUST000481"))

# COMMAND ----------

# MAGIC %md
# MAGIC ✅ MCP tools reachable. Next: **`05_build_mosaic_agent`**.
# MAGIC
# MAGIC **Troubleshooting**
# MAGIC - `list_tools()` empty → confirm notebook 03 created the functions and you have
# MAGIC   `EXECUTE` on `banking_ai.tools`.
# MAGIC - `PERMISSION_DENIED` on a call → Unity Catalog is enforcing grants; see
# MAGIC   `setup/grant_permissions.sql`.
# MAGIC - Custom server tickets empty → that customer may have no tickets; try another
# MAGIC   `customer_id`, or set the `DATABRICKS_*` env vars to query Delta directly.
