# Troubleshooting

Common errors, why they happen, and the fix. Grouped by stage.

## Setup / Unity Catalog

**`PERMISSION_DENIED: CREATE CATALOG`**
You're not a metastore admin. Ask an admin to create `banking_ai` and grant you
`ALL PRIVILEGES`, then re-run notebook 01 from the *schemas* step. Or point
everything at an existing catalog you own (rename in `setup/*.sql` and
`model_config.py`).

**`SCHEMA_NOT_FOUND` / `TABLE_OR_VIEW_NOT_FOUND`**
Notebooks were run out of order. Run 01 → 02 → 03 in sequence.

**Wrong catalog everywhere**
The catalog name lives in three places: `setup/*.sql`, the UC-function SQL, and
`mosaic_ai_agent/model_config.py`. Change all of them.

## Data generation

**`ModuleNotFoundError: faker`**
Run the `%pip install faker` cell, then `%restart_python`, then re-run.

**Counts look wrong / duplicated**
Generators use `mode="overwrite"`, so re-running is safe and idempotent. If a table
looks doubled, you likely appended manually — just re-run notebook 02.

**A demo ID (CUST000481 / TXN00000010) returns nothing**
Those IDs are stable *given the default seeds*. If you changed seeds or volumes,
pick any real ID from `banking_ai.core.*` and use that in your tests.

## Unity Catalog functions / tools

**The model never calls a tool**
The LLM decides using the tool's **name + description + parameter comments**. Vague
`COMMENT`s → missed tools. Make them specific ("Use this when the customer asks
about available credit…"). Confirm the tool is actually attached (Playground) or
listed by `client.list_tools()` (notebook 04).

**`PERMISSION_DENIED` when a tool runs**
Unity Catalog checks `EXECUTE` on the function **and** `SELECT` on the underlying
table on every call. Re-apply `setup/grant_permissions.sql`. For a *deployed* agent,
the grant must be to the **serving endpoint's service principal**, not just you.

**Function creation fails with a serverless error**
Running UC functions as tools needs **Serverless compute enabled**. Enable it in
workspace settings.

## MCP

**Managed server `list_tools()` returns empty**
Functions weren't created (run notebook 03) or you lack `EXECUTE`/`USE SCHEMA` on
`banking_ai.tools`.

**Custom server tickets are empty**
That customer may have no tickets — try another `customer_id`. Locally the server
reads `data_generation/sample_data/support_tickets.csv`; to query Delta instead,
set `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_HTTP_PATH`.

**`ImportError: databricks_mcp` / `mcp`**
`pip install databricks-mcp` (agent side) or `pip install "mcp>=1.2.0"` (custom
server).

## Agent (code)

**`ResourceDoesNotExist` on the LLM endpoint**
The endpoint in `model_config.py` isn't available in your workspace. Pick one from
Serving → Foundation Models and update `llm_endpoint`.

**Agent loops to `max_tool_iterations`**
The model keeps calling tools without converging. Tighten the system prompt, make
tool descriptions crisper, or raise the cap slightly. Inspect the MLflow **trace** to
see what it's doing.

**Works in the notebook, 500s once deployed**
Almost always missing grants for the serving endpoint's service principal, or a
resource not attached at log time. Re-check `build_resources()` in
`deploy_agent.py` and the principal's `EXECUTE`/`SELECT` grants.

## Deployment / serving

**`agents.deploy` `PERMISSION_DENIED`**
Need `CREATE MODEL` on `banking_ai.agents` and `CAN QUERY` on the LLM endpoint.

**Endpoint stuck NOT READY**
Deployment takes several minutes. Check the endpoint's build logs (Serving → your
endpoint → Events/Logs). A bad `pip_requirements` pin is the usual culprit.

**Unexpected cost**
A Model Serving endpoint bills while it exists. Delete it when you're done
(Serving → endpoint → Delete).

## Evaluation

**Judge model errors**
You need `CAN QUERY` on the judge endpoint. Databricks provides a default judge;
if your workspace restricts it, set an available one.

**Scores look low but answers seem fine**
Check your `expected_facts` — over-strict expectations penalise correct answers.
Loosen them or switch to guideline-based scoring.
