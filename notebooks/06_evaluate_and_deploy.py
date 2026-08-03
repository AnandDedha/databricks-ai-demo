# Databricks notebook source
# MAGIC %md
# MAGIC # 06 · Evaluate & Deploy
# MAGIC
# MAGIC 1. **Evaluate** the agent with Mosaic AI Agent Evaluation (AI-as-a-Judge).
# MAGIC 2. **Log → register → deploy** it to Model Serving with the Agent Framework.
# MAGIC
# MAGIC After deployment you get a **serving endpoint** and a **review app** to chat with.

# COMMAND ----------

# MAGIC %pip install -r ../requirements.txt
# MAGIC %restart_python

# COMMAND ----------

import os, sys
REPO_ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "mosaic_ai_agent"))
# Deploy logs code relative to CWD, so run from the agent folder.
os.chdir(os.path.join(REPO_ROOT, "mosaic_ai_agent"))
print("CWD:", os.getcwd())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Evaluate
# MAGIC Scores Correctness, Relevance, Safety, and our banking guidelines. Review low
# MAGIC scores before deploying. Expand the eval set in `evaluate_agent.py` for real use.

# COMMAND ----------

import evaluate_agent
evaluate_agent.main()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Deploy
# MAGIC Logs the agent (code-based), attaches resources (LLM + UC functions),
# MAGIC registers to `banking_ai.agents.abcbank_support_agent`, and deploys.

# COMMAND ----------

# Make sure the target schema for the registered model exists.
spark.sql("CREATE SCHEMA IF NOT EXISTS banking_ai.agents COMMENT 'Registered agent models.'")

# COMMAND ----------

import deploy_agent
deploy_agent.main()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Query the deployed endpoint
# MAGIC Give the endpoint a couple of minutes to reach READY, then:

# COMMAND ----------

from mlflow.deployments import get_deploy_client

ENDPOINT_NAME = "agents_banking_ai-agents-abcbank_support_agent"  # adjust if printed differently
client = get_deploy_client("databricks")
resp = client.predict(
    endpoint=ENDPOINT_NAME,
    inputs={"input": [{"role": "user",
        "content": ("For customer CUST000481: why was transaction TXN00000010 declined, "
                    "and what is my available credit?")}]},
)
print(resp)

# COMMAND ----------

# MAGIC %md
# MAGIC 🎉 Done — you built, tested, evaluated, and deployed an agent three ways.
# MAGIC
# MAGIC **Monitoring:** open the serving endpoint → **Monitoring/Traces** to watch
# MAGIC latency, requests, and per-request tool traces. Feed failures back into the
# MAGIC tools, prompt, or eval set.
# MAGIC
# MAGIC **Troubleshooting**
# MAGIC - Deploy `PERMISSION_DENIED` → you need `CREATE MODEL` on `banking_ai.agents`
# MAGIC   and `CAN QUERY` on the LLM endpoint.
# MAGIC - Endpoint name differs → copy it from the `deploy_agent.main()` output or the
# MAGIC   Serving UI.
# MAGIC - Agent 500s in serving but works in the notebook → the endpoint's service
# MAGIC   principal is missing `EXECUTE`/`SELECT` grants; re-check
# MAGIC   `setup/grant_permissions.sql` for that principal.
