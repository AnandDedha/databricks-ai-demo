# Databricks notebook source
# MAGIC %md
# MAGIC # 02 · Generate Sample Data
# MAGIC
# MAGIC Generates 500 customers, 700 accounts, 300 deposits, 300 cards, 5,000
# MAGIC transactions, and 500 support tickets — all synthetic — and writes them to
# MAGIC Delta tables in `banking_ai.core`.
# MAGIC
# MAGIC **Expected output:** row counts per table; the flagship demo customer
# MAGIC (`CUST000481`) is present with a declined card transaction (`TXN00000010`).

# COMMAND ----------

# MAGIC %pip install faker>=30.0.0
# MAGIC %restart_python

# COMMAND ----------

import os, sys

NB_DIR = os.getcwd()
REPO_ROOT = os.path.abspath(os.path.join(NB_DIR, ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "data_generation"))
print("Using generators in:", os.path.join(REPO_ROOT, "data_generation"))

# COMMAND ----------

# `load_sample_data.main()` detects the SparkSession and writes Delta tables.
import load_sample_data as loader

loader.main()   # writes banking_ai.core.* via spark

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify counts + the demo customer

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'customers' t, count(*) n FROM banking_ai.core.customers
# MAGIC UNION ALL SELECT 'accounts',            count(*) FROM banking_ai.core.accounts
# MAGIC UNION ALL SELECT 'deposit_accounts',    count(*) FROM banking_ai.core.deposit_accounts
# MAGIC UNION ALL SELECT 'credit_card_accounts',count(*) FROM banking_ai.core.credit_card_accounts
# MAGIC UNION ALL SELECT 'transactions',        count(*) FROM banking_ai.core.transactions
# MAGIC UNION ALL SELECT 'support_tickets',     count(*) FROM banking_ai.core.support_tickets
# MAGIC ORDER BY t;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- The flagship scenario, straight from the data:
# MAGIC SELECT t.transaction_id, t.transaction_status, t.decline_reason,
# MAGIC        c.card_id, c.available_credit, c.utilization_percentage
# MAGIC FROM banking_ai.core.transactions t
# MAGIC JOIN banking_ai.core.credit_card_accounts c ON t.account_id = c.card_id
# MAGIC WHERE t.transaction_id = 'TXN00000010';

# COMMAND ----------

# MAGIC %md
# MAGIC ✅ Data loaded. Next: **`03_create_uc_functions`**.
# MAGIC
# MAGIC **Troubleshooting**
# MAGIC - `ModuleNotFoundError: faker` → re-run the `%pip install` cell then
# MAGIC   `%restart_python`.
# MAGIC - Empty tables → confirm notebook 01 created them first.
# MAGIC - Re-running overwrites (mode="overwrite"), so counts stay stable.
