# Setup Guide

Follow this end to end and you'll go from an empty workspace to a deployed agent.

## 0. Prerequisites
- A Databricks workspace (**Azure**, AWS, GCP, or **Free Edition**) with:
  - **Unity Catalog** enabled.
  - **Serverless compute** enabled (needed to run UC functions as tools and to
    deploy agents).
  - A **Foundation Model** endpoint that supports tool calling, e.g.
    `databricks-claude-3-7-sonnet` or `databricks-meta-llama-3-3-70b-instruct`
    (Serving → Foundation Models).
- Permissions: ability to create a catalog **or** an existing catalog you own.
  If you use a different catalog name, change it in `setup/*.sql` **and**
  `mosaic_ai_agent/model_config.py`.

## 1. Get the code into Databricks
- **Repos** (recommended): Workspace → Repos → *Add Repo* → paste the Git URL.
- Or upload the folder to your workspace.

## 2. Run the notebooks in order
| Notebook | Does |
|---|---|
| `01_environment_setup` | Creates catalog, schemas, tables, grants |
| `02_generate_sample_data` | Generates + loads 6 synthetic datasets |
| `03_create_uc_functions` | Creates the 4 UC-function tools + tests them |
| `04_test_mcp_tools` | Lists/calls managed MCP tools; tests custom MCP logic |
| `05_build_mosaic_agent` | Loads + runs the `ResponsesAgent` |
| `06_evaluate_and_deploy` | Evaluates, then deploys to Model Serving |

Each notebook ends with a **Verify** section and a **Troubleshooting** box.

## 3. AI Playground (approach 1, UI)
1. Left nav → **Playground**, pick a tool-calling model.
2. Attach the four `banking_ai.tools.*` functions (Tools → Add tool → Unity Catalog
   function). Optionally add the managed MCP server URL.
3. Paste the system prompt from `ai_playground/system_prompt.md`.
4. Work through `ai_playground/testing_scenarios.md` — especially scenario #4.

## 4. Agent Bricks (approach 2, low-code)
1. Export a few policy notes to a Unity Catalog **Volume** (reuse the text in
   `mcp/tools.py → EXTERNAL_BANKING_INFO`).
2. Agents → **Agent Bricks → Knowledge Assistant → Create**.
3. Add the knowledge sources, paste `agent_bricks/sample_instructions.md`.
4. Evaluate with `agent_bricks/evaluation_questions.json`, then **Deploy**.
See `agent_bricks/agent_bricks_setup.md` for the full walkthrough.

## 5. Mosaic AI Agent Framework (approach 3, code)
Notebooks 05 + 06 do this. Under the hood:
- `mosaic_ai_agent/model_config.py` — all settings.
- `mosaic_ai_agent/tools.py` — discovers MCP tools, dispatches calls.
- `mosaic_ai_agent/agent.py` — the `ResponsesAgent` + tool-calling loop.
- `mosaic_ai_agent/evaluate_agent.py` — AI-as-a-Judge evaluation.
- `mosaic_ai_agent/deploy_agent.py` — log → register → deploy.

## 6. (Optional) Run the custom MCP server locally
```bash
cd mcp
pip install "mcp>=1.2.0" databricks-sql-connector
python mcp_server.py --http     # then open the MCP Inspector at :8000
```

## Required permissions cheat-sheet
| Action | Needs |
|---|---|
| Create catalog | Metastore admin (or pre-created catalog) |
| Create schemas/tables | `USE CATALOG` + `CREATE SCHEMA`/`CREATE TABLE` |
| Create UC functions | `CREATE FUNCTION` on `banking_ai.tools` |
| Run tools (you/agent) | `EXECUTE` on function + `SELECT` on table |
| Deploy agent | `CREATE MODEL` on `banking_ai.agents` + `CAN QUERY` on LLM endpoint |

## Estimated cost/time
- Setup + data + functions: ~10 min, minimal DBUs (serverless SQL).
- Playground experiments: pennies (per-token model calls).
- Deploying the agent: a Model Serving endpoint runs until you delete it — **tear it
  down** when done (Serving → endpoint → Delete) to avoid ongoing cost.
