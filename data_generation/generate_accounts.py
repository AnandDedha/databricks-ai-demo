"""
generate_accounts.py
---------------------
Generate synthetic bank accounts (checking/savings) AND deposit accounts.
Both reference existing customer_ids so joins always resolve.

Produces two DataFrames:
  - accounts          (700 rows by default)
  - deposit_accounts  (300 rows by default)

Usage (standalone):
    python generate_accounts.py     # regenerates customers internally, writes CSVs

Usage (imported):
    from generate_customers import generate_customers
    from generate_accounts import generate_accounts
    customers = generate_customers()
    accounts, deposits = generate_accounts(customers, n_accounts=700, n_deposits=300)
"""
from __future__ import annotations

import random
from datetime import date, timedelta

import pandas as pd

ACCOUNT_TYPES = ["CHECKING", "SAVINGS"]
ACCOUNT_STATUS = ["ACTIVE", "DORMANT", "FROZEN", "CLOSED"]
ACCOUNT_STATUS_WEIGHTS = [0.82, 0.08, 0.05, 0.05]

DEPOSIT_TYPES = ["FIXED", "RECURRING"]
DEPOSIT_STATUS = ["ACTIVE", "MATURED", "CLOSED"]
DEPOSIT_STATUS_WEIGHTS = [0.75, 0.18, 0.07]


def generate_accounts(
    customers: pd.DataFrame,
    n_accounts: int = 700,
    n_deposits: int = 300,
    seed: int = 43,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (accounts_df, deposit_accounts_df).

    Every account is assigned to a random existing customer, so most customers
    have 1-2 accounts and some have none (realistic).
    """
    random.seed(seed)
    today = date.today()
    customer_ids = customers["customer_id"].tolist()

    # ---- Checking / savings accounts ----
    acc_rows = []
    for i in range(1, n_accounts + 1):
        current = round(random.uniform(500, 250_000), 2)
        # A small hold amount makes available < current sometimes.
        hold = round(random.choice([0, 0, 0, random.uniform(0, current * 0.2)]), 2)
        acc_rows.append({
            "account_id": f"ACC{i:07d}",
            "customer_id": random.choice(customer_ids),
            "account_type": random.choice(ACCOUNT_TYPES),
            "account_status": random.choices(ACCOUNT_STATUS, weights=ACCOUNT_STATUS_WEIGHTS)[0],
            "current_balance": current,
            "available_balance": round(current - hold, 2),
            "opened_date": today - timedelta(days=random.randint(30, 365 * 10)),
        })
    accounts = pd.DataFrame(acc_rows)

    # ---- Deposit accounts (FD / RD) ----
    dep_rows = []
    for i in range(1, n_deposits + 1):
        opened = today - timedelta(days=random.randint(30, 365 * 5))
        term = random.choice([6, 12, 18, 24, 36, 60])
        dep_rows.append({
            "deposit_id": f"DEP{i:07d}",
            "customer_id": random.choice(customer_ids),
            "deposit_type": random.choice(DEPOSIT_TYPES),
            "principal_amount": round(random.uniform(10_000, 1_000_000), 2),
            "interest_rate": round(random.uniform(5.5, 7.75), 2),
            "term_months": term,
            "maturity_date": opened + timedelta(days=int(term * 30.4)),
            "deposit_status": random.choices(DEPOSIT_STATUS, weights=DEPOSIT_STATUS_WEIGHTS)[0],
            "opened_date": opened,
        })
    deposit_accounts = pd.DataFrame(dep_rows)

    return accounts, deposit_accounts


if __name__ == "__main__":
    import os
    from generate_customers import generate_customers

    customers = generate_customers()
    accounts, deposits = generate_accounts(customers)
    os.makedirs("sample_data", exist_ok=True)
    accounts.to_csv("sample_data/accounts.csv", index=False)
    deposits.to_csv("sample_data/deposit_accounts.csv", index=False)
    print(f"Wrote {len(accounts)} accounts and {len(deposits)} deposit accounts -> sample_data/")
    print(accounts.head().to_string(index=False))
