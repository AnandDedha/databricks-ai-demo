# Databricks notebook source
# MAGIC %md
# MAGIC # 05 · Build the Mosaic AI Agent
# MAGIC
# MAGIC Loads the `ResponsesAgent` from `../mosaic_ai_agent/agent.py`, then runs it on
# MAGIC the flagship question so you can watch the tool-calling loop in the MLflow
# MAGIC **trace** UI.
# MAGIC
# MAGIC > *"For customer CUST000481: why was transaction TXN00000010 declined, and what
# MAGIC > is my available credit?"*
# MAGIC
# MAGIC The agent should: call `check_transaction_status`, call
# MAGIC `calculate_credit_utilization`, then answer with both facts + a next step.

# COMMAND ----------

# MAGIC %pip install -r ../requirements.txt
# MAGIC %restart_python

# COMMAND ----------

import os, sys
REPO_ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "mosaic_ai_agent"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## (Optional) turn on the custom MCP tools
# MAGIC If you've deployed `mcp/mcp_server.py` as a Databricks App, set its URL so the
# MAGIC agent also gets `support_tickets` + `external_banking_info`. Otherwise skip —
# MAGIC the agent runs fine on the UC-function tools alone.

# COMMAND ----------

from model_config import CONFIG
# CONFIG.custom_mcp_url = "https://<your-app>.databricksapps.com/mcp"   # optional
print("LLM endpoint:", CONFIG.llm_endpoint)
print("UC functions MCP path:", CONFIG.uc_functions_mcp_path())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load the agent and run the flagship question

# COMMAND ----------

import mlflow
mlflow.openai.autolog()   # captures the tool-calling trace

from agent import AGENT
from mlflow.types.responses import ResponsesAgentRequest

req = ResponsesAgentRequest(input=[{
    "role": "user",
    "content": ("For customer CUST000481: why was transaction TXN00000010 declined, "
                "and what is my available credit?"),
}])

response = AGENT.predict(req)
item = response.output[0]
print(item["content"] if isinstance(item, dict) else item.content)
print("\nTools used (structured):", response.custom_outputs)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try a few more
# MAGIC Watch how the agent picks different tools per question.

# COMMAND ----------

for q in [
    "What is the balance on CUST000481's accounts?",
    "Show the last 3 transactions on card CARD000206.",
    "What's my available credit?",   # should ask for an ID
]:
    r = AGENT.predict(ResponsesAgentRequest(input=[{"role": "user", "content": q}]))
    it = r.output[0]
    print("Q:", q)
    print("A:", (it["content"] if isinstance(it, dict) else it.content)[:400])
    print("-" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ✅ Agent works. Open the **Traces** tab of this notebook's MLflow experiment to
# MAGIC see each LLM call and tool call. Next: **`06_evaluate_and_deploy`**.
# MAGIC
# MAGIC **Troubleshooting**
# MAGIC - `ResourceDoesNotExist` on the LLM → pick an available endpoint in
# MAGIC   `model_config.py` (Serving → Foundation Models).
# MAGIC - Model never calls a tool → check the UC function `COMMENT`s and the system
# MAGIC   prompt; make sure `list_tools()` (notebook 04) returned them.
# MAGIC - Loops to the cap → raise `max_tool_iterations` or tighten the prompt.
