# Databricks notebook source
# MAGIC %md
# MAGIC # 03 · Create Unity Catalog Functions (the agent's tools)
# MAGIC
# MAGIC Creates four governed SQL functions in `banking_ai.tools`. These become the
# MAGIC agent's tools — in AI Playground, Agent Bricks, and the code agent — and are
# MAGIC automatically exposed via the **managed MCP server** at
# MAGIC `/api/2.0/mcp/functions/banking_ai/tools`.
# MAGIC
# MAGIC **Expected output:** 4 functions created and smoke-tested.

# COMMAND ----------

import os

REPO_ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))
FN_DIR = os.path.join(REPO_ROOT, "unity_catalog_functions")

def run_sql_file(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    lines = [ln for ln in raw.splitlines() if not ln.strip().startswith("--")]
    body = "\n".join(lines).strip()
    if body:
        print("▶ creating from", os.path.basename(path))
        spark.sql(body)   # each function file is a single statement

# COMMAND ----------

for fname in [
    "get_customer_balance.sql",
    "calculate_credit_utilization.sql",
    "get_recent_transactions.sql",
    "check_transaction_status.sql",
]:
    run_sql_file(os.path.join(FN_DIR, fname))

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW USER FUNCTIONS IN banking_ai.tools;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Smoke-test each tool with the demo customer (CUST000481 / CARD000206 / TXN00000010)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM banking_ai.tools.calculate_credit_utilization('CUST000481');

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM banking_ai.tools.check_transaction_status('TXN00000010');

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM banking_ai.tools.get_recent_transactions('CARD000206', 5);

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM banking_ai.tools.get_customer_balance('CUST000481');

# COMMAND ----------

# MAGIC %md
# MAGIC ✅ Four tools live and tested.
# MAGIC
# MAGIC The managed MCP URL for these is:
# MAGIC ```
# MAGIC https://<your-workspace-host>/api/2.0/mcp/functions/banking_ai/tools
# MAGIC ```
# MAGIC Next: **`04_test_mcp_tools`**.
# MAGIC
# MAGIC **Troubleshooting**
# MAGIC - `TABLE_OR_VIEW_NOT_FOUND` → run notebook 02 first (functions read the tables).
# MAGIC - Function returns 0 rows → that ID may not exist in your regenerated data;
# MAGIC   pick any `customer_id`/`card_id` from `banking_ai.core.*`.
# MAGIC - The LLM ignores a tool → improve its `COMMENT` (the model reads it to decide).
