"""
load_sample_data.py
-------------------
One entry point that generates ALL six datasets (customers, accounts,
deposit_accounts, credit_card_accounts, transactions, support_tickets) and
loads them into Delta tables under banking_ai.core.

Support tickets are generated here (they reference customers + declined card
transactions) to keep the required file list tidy.

HOW IT RUNS
  - Inside Databricks (a SparkSession named `spark` exists): writes Delta tables
    banking_ai.core.<table> using overwrite. This is what notebook 02 calls.
  - Locally (no Spark): writes CSVs to ./sample_data/ so you can inspect the data
    on your laptop before touching Databricks.

REQUIRED PERMISSIONS (in Databricks): USE CATALOG banking_ai, USE SCHEMA core,
    CREATE/MODIFY on the six tables (created by setup/create_tables.sql).

EXPECTED OUTPUT: 6 tables populated; row counts printed. Re-running overwrites.
"""
from __future__ import annotations

import random
from datetime import timedelta

import pandas as pd

from generate_customers import generate_customers
from generate_accounts import generate_accounts
from generate_credit_cards import generate_credit_cards
from generate_transactions import generate_transactions

CATALOG = "banking_ai"
SCHEMA = "core"

# Target volumes (from the tutorial spec).
N_CUSTOMERS = 500
N_ACCOUNTS = 700
N_DEPOSITS = 300
N_CARDS = 300
N_TRANSACTIONS = 5000
N_TICKETS = 500

ISSUE_TYPES = ["CARD_DECLINED", "FRAUD", "LOGIN", "DISPUTE", "LOAN", "GENERAL"]
TICKET_STATUS = ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]
TICKET_STATUS_WEIGHTS = [0.2, 0.15, 0.4, 0.25]

# Template descriptions keyed by issue_type — these double as the knowledge
# source for the Agent Bricks Knowledge Assistant demo.
TICKET_TEMPLATES = {
    "CARD_DECLINED": [
        "Customer's card was declined at {merchant}. Investigation showed the card "
        "had reached its credit limit; advised customer to make a payment or request "
        "a limit increase.",
        "Transaction declined due to the card being temporarily blocked after "
        "suspected fraud. Verified customer identity and re-enabled the card.",
    ],
    "FRAUD": [
        "Customer reported an unrecognised transaction. Flagged for the fraud team, "
        "card hot-listed, and a replacement issued.",
    ],
    "LOGIN": [
        "Customer unable to log in to the mobile app. Reset credentials and confirmed "
        "successful login.",
    ],
    "DISPUTE": [
        "Customer disputes a duplicate charge from {merchant}. Raised a chargeback and "
        "provisionally credited the amount.",
    ],
    "LOAN": [
        "Customer enquired about a personal loan top-up. Shared eligibility and current "
        "interest rates; no action required.",
    ],
    "GENERAL": [
        "General enquiry about interest rates on fixed deposits. Provided current rate "
        "card and closed the ticket.",
    ],
}
MERCHANTS = ["Amazon India", "Swiggy", "IRCTC", "Croma", "MakeMyTrip", "Flipkart"]


def generate_support_tickets(customers: pd.DataFrame, n: int = N_TICKETS, seed: int = 46) -> pd.DataFrame:
    """Support tickets referencing existing customers."""
    import datetime as _dt
    random.seed(seed)
    now = _dt.datetime.now()
    customer_ids = customers["customer_id"].tolist()

    rows = []
    for i in range(1, n + 1):
        issue = random.choices(ISSUE_TYPES, weights=[0.3, 0.15, 0.15, 0.15, 0.1, 0.15])[0]
        template = random.choice(TICKET_TEMPLATES[issue])
        rows.append({
            "ticket_id": f"TKT{i:06d}",
            "customer_id": random.choice(customer_ids),
            "issue_type": issue,
            "issue_description": template.format(merchant=random.choice(MERCHANTS)),
            "ticket_status": random.choices(TICKET_STATUS, weights=TICKET_STATUS_WEIGHTS)[0],
            "created_timestamp": now - timedelta(days=random.randint(0, 180)),
        })
    return pd.DataFrame(rows)


def build_all() -> dict[str, pd.DataFrame]:
    """Generate every dataset and return {table_name: DataFrame}."""
    customers = generate_customers(N_CUSTOMERS)
    accounts, deposits = generate_accounts(customers, N_ACCOUNTS, N_DEPOSITS)
    cards = generate_credit_cards(customers, N_CARDS)
    transactions = generate_transactions(accounts, cards, N_TRANSACTIONS)
    tickets = generate_support_tickets(customers)
    return {
        "customers": customers,
        "accounts": accounts,
        "deposit_accounts": deposits,
        "credit_card_accounts": cards,
        "transactions": transactions,
        "support_tickets": tickets,
    }


def _write_delta(frames: dict[str, pd.DataFrame], spark) -> None:
    for name, pdf in frames.items():
        sdf = spark.createDataFrame(pdf)
        target = f"{CATALOG}.{SCHEMA}.{name}"
        (sdf.write.format("delta").mode("overwrite")
            .option("overwriteSchema", "true").saveAsTable(target))
        print(f"  wrote {len(pdf):>5} rows -> {target}")


def _write_csv(frames: dict[str, pd.DataFrame]) -> None:
    import os
    os.makedirs("sample_data", exist_ok=True)
    for name, pdf in frames.items():
        path = f"sample_data/{name}.csv"
        pdf.to_csv(path, index=False)
        print(f"  wrote {len(pdf):>5} rows -> {path}")


def main() -> None:
    frames = build_all()
    print("Generated datasets:")
    for name, pdf in frames.items():
        print(f"  {name:<22} {len(pdf):>5} rows")

    # Detect Databricks SparkSession.
    spark = None
    try:
        spark = globals().get("spark") or SparkSession.builder.getOrCreate()  # type: ignore # noqa
    except Exception:
        spark = None

    if spark is not None:
        print(f"\nWriting Delta tables to {CATALOG}.{SCHEMA} ...")
        _write_delta(frames, spark)
    else:
        print("\nNo SparkSession found — writing CSVs locally instead.")
        _write_csv(frames)
    print("Done.")


# In a Databricks notebook, `spark` is already in scope, so this also works when
# the file is %run or imported.
try:
    from pyspark.sql import SparkSession  # noqa: F401
except Exception:
    SparkSession = None  # type: ignore

if __name__ == "__main__":
    main()
