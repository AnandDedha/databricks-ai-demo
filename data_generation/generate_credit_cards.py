"""
generate_credit_cards.py
------------------------
Generate synthetic credit card accounts. utilization_percentage and
available_credit are computed (not random) so the numbers are internally
consistent — important, because one of our UC functions recomputes utilization
and we want the agent's answer to match the table.

Fields: card_id, customer_id, card_type, credit_limit, outstanding_balance,
        available_credit, utilization_percentage, card_status, payment_due_date

Usage (imported):
    from generate_credit_cards import generate_credit_cards
    cards = generate_credit_cards(customers, n=300)
"""
from __future__ import annotations

import random
from datetime import date, timedelta

import pandas as pd

CARD_TYPES = ["VISA", "MASTERCARD", "AMEX", "RUPAY"]
CARD_STATUS = ["ACTIVE", "BLOCKED", "EXPIRED"]
CARD_STATUS_WEIGHTS = [0.85, 0.10, 0.05]
CREDIT_LIMITS = [50_000, 100_000, 150_000, 200_000, 300_000, 500_000]


def generate_credit_cards(customers: pd.DataFrame, n: int = 300, seed: int = 44) -> pd.DataFrame:
    random.seed(seed)
    today = date.today()
    customer_ids = customers["customer_id"].tolist()

    rows = []
    for i in range(1, n + 1):
        limit = float(random.choice(CREDIT_LIMITS))
        # Bias a chunk of cards toward HIGH utilization so "available credit is
        # low" and "transaction declined for insufficient limit" are realistic.
        util_target = random.choices(
            [random.uniform(0, 0.3), random.uniform(0.3, 0.7), random.uniform(0.7, 0.99)],
            weights=[0.5, 0.3, 0.2],
        )[0]
        outstanding = round(limit * util_target, 2)
        available = round(limit - outstanding, 2)
        utilization = round(outstanding / limit * 100, 2)
        rows.append({
            "card_id": f"CARD{i:06d}",
            "customer_id": random.choice(customer_ids),
            "card_type": random.choices(CARD_TYPES, weights=[0.35, 0.3, 0.1, 0.25])[0],
            "credit_limit": limit,
            "outstanding_balance": outstanding,
            "available_credit": available,
            "utilization_percentage": utilization,
            "card_status": random.choices(CARD_STATUS, weights=CARD_STATUS_WEIGHTS)[0],
            "payment_due_date": today + timedelta(days=random.randint(1, 28)),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    import os
    from generate_customers import generate_customers

    customers = generate_customers()
    cards = generate_credit_cards(customers)
    os.makedirs("sample_data", exist_ok=True)
    cards.to_csv("sample_data/credit_card_accounts.csv", index=False)
    print(f"Wrote {len(cards)} credit card accounts -> sample_data/credit_card_accounts.csv")
    print(cards.head().to_string(index=False))
