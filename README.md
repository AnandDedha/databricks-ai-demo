# Databricks Banking AI Agents

Build AI agents on Databricks **three different ways** — using a single, realistic **banking / fintech** dataset — and learn exactly when to reach for each one.

This repo is the companion code for the YouTube tutorial. Everything is **100% synthetic**: no real customer, account, or card data is used anywhere.

| # | Approach | You build with | Best for |
|---|----------|----------------|----------|
| 1 | **AI Playground** | UI + tool calling (UC functions + MCP) | Prompt testing, model comparison, quick tool experiments |
| 2 | **Agent Bricks** | Low-code patterns (Information Extraction) | Fast, governed agents from predefined patterns |
| 3 | **Mosaic AI Agent Framework** | Python + MLflow `ResponsesAgent` | Fully customizable, code-based production agents |

---

## The banking scenario

We run a fictional retail bank, **ABCBank**. The agent helps customers and support staff answer questions like:

> *"Why was my credit card transaction declined, and what is my available credit?"*

To answer that, an agent needs to reason over six datasets:

- **Customers** — profile + risk category
- **Accounts** — checking / savings, balances, status
- **Deposit accounts** — fixed / recurring deposits
- **Credit card accounts** — limit, outstanding, available credit, utilization
- **Transactions** — 5,000 rows including declines with reasons
- **Support tickets** — customer service history

## Architecture at a glance

See docs/Architecture Diagram.PNG

---

## Quickstart (≈ 20 minutes)

> Works on **Azure Databricks**, AWS, GCP, or **Databricks Free Edition**. You need Unity Catalog + Serverless compute enabled.

1. **Clone** this repo into a Databricks Repo (or run the notebooks directly).
2. **Create the catalog, schemas, and tables:**
   Run the notebook [`notebooks/01_environment_setup.py`](notebooks/01_environment_setup.py) (it executes the SQL in `setup/`).
3. **Generate the sample data:**
   Run [`notebooks/02_generate_sample_data.py`](notebooks/02_generate_sample_data.py).
4. **Create the Unity Catalog functions (agent tools):**
   Run [`notebooks/03_create_uc_functions.py`](notebooks/03_create_uc_functions.py).
5. **(Optional) Start / test the custom MCP server:**
   Run [`notebooks/04_test_mcp_tools.py`](notebooks/04_test_mcp_tools.py).
6. **Build the Mosaic AI agent:**
   Run [`notebooks/05_build_mosaic_agent.py`](notebooks/05_build_mosaic_agent.py).
7. **Evaluate & deploy:**
   Run [`notebooks/06_evaluate_and_deploy.py`](notebooks/06_evaluate_and_deploy.py).

For AI Playground and Agent Bricks (both UI-driven), follow [`ai_playground/`](ai_playground/) and [`agent_bricks/`](agent_bricks/).

---

## Repository map

```
databricks-banking-ai-agents/
├── setup/                    # SQL: catalog, schemas, tables, grants
├── data_generation/          # Python: synthetic data generators
├── unity_catalog_functions/  # SQL: the 4 agent tools
├── mcp/                       # Custom MCP server (tickets + external info)
├── ai_playground/            # Approach 1 — prompts, tool config, test cases
├── agent_bricks/             # Approach 2 — Knowledge Assistant setup + eval
├── mosaic_ai_agent/          # Approach 3 — ResponsesAgent code + deploy + eval
├── notebooks/                # Run these top-to-bottom
└── docs/                     # Architecture, YouTube script, guides, comparison
```

## Prerequisites

- A Databricks workspace with **Unity Catalog** and **Serverless compute** enabled.
- Permission to `CREATE CATALOG` (or an existing catalog you can write to — change the name in `setup/`).
- A **Foundation Model** endpoint available (e.g. `databricks-claude-3-7-sonnet` / `databricks-meta-llama-3-3-70b-instruct`). Check **Serving → Foundation Models**.
- Python packages in [`requirements.txt`](requirements.txt).

## Safety & data note

All data is generated with [Faker](https://faker.readthedocs.io/) and fixed random seeds. Names, emails, card numbers, and balances are fabricated. **Do not** point these scripts at, or load, real PII.

## License

MIT — see the tutorial description for details. Use freely for learning.
