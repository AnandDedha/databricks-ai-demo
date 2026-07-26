# Databricks notebook source
# MAGIC %md
# MAGIC # 01 · Environment Setup
# MAGIC
# MAGIC Creates the Unity Catalog **catalog → schemas → tables** and applies grants
# MAGIC by executing the SQL in `../setup/`.
# MAGIC
# MAGIC **Prerequisites**
# MAGIC - Unity Catalog + Serverless enabled.
# MAGIC - Permission to create a catalog (or an existing catalog you can write to —
# MAGIC   then edit the names in `setup/*.sql` and `mosaic_ai_agent/model_config.py`).
# MAGIC
# MAGIC **Expected output:** catalog `banking_ai`, schemas `core` + `tools`, and 6 empty tables.

# COMMAND ----------

import os

# Resolve the repo root whether this runs from a Repo or a workspace folder.
NB_DIR = os.path.dirname(os.path.abspath("__file__")) if "__file__" in dir() else os.getcwd()
REPO_ROOT = os.path.abspath(os.path.join(NB_DIR, ".."))
SETUP_DIR = os.path.join(REPO_ROOT, "setup")
print("Repo root:", REPO_ROOT)
print("Setup dir:", SETUP_DIR)

# COMMAND ----------

def run_sql_file(path: str) -> None:
    """Execute a .sql file statement-by-statement.

    We strip `--` line comments and split on ';'. Our setup + function files have
    no semicolons inside statements, so this is safe. `USE CATALOG/SCHEMA` context
    persists across statements within this SparkSession.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    # remove full-line comments
    lines = [ln for ln in raw.splitlines() if not ln.strip().startswith("--")]
    body = "\n".join(lines)
    statements = [s.strip() for s in body.split(";") if s.strip()]
    print(f"\n▶ {os.path.basename(path)} — {len(statements)} statement(s)")
    for stmt in statements:
        first = stmt.splitlines()[0][:70]
        print("   run:", first, "...")
        spark.sql(stmt)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Run the setup files in order

# COMMAND ----------

for fname in ["create_catalog.sql", "create_schemas.sql", "create_tables.sql"]:
    run_sql_file(os.path.join(SETUP_DIR, fname))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Grants
# MAGIC Open `setup/grant_permissions.sql`, replace `account users` with your own
# MAGIC users/groups if you want tighter access, then run the next cell. For a
# MAGIC personal demo the defaults are fine.

# COMMAND ----------

run_sql_file(os.path.join(SETUP_DIR, "grant_permissions.sql"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES IN banking_ai.core;

# COMMAND ----------

# MAGIC %md
# MAGIC ✅ If you see the six tables (empty for now), continue to
# MAGIC **`02_generate_sample_data`**.
# MAGIC
# MAGIC **Troubleshooting**
# MAGIC - `PERMISSION_DENIED` on `CREATE CATALOG` → ask an admin to create `banking_ai`
# MAGIC   and grant you `ALL PRIVILEGES`, then re-run from the schemas step.
# MAGIC - Wrong catalog name → change it in every `setup/*.sql` **and** in
# MAGIC   `mosaic_ai_agent/model_config.py`.
