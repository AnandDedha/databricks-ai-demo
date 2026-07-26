"""
generate_customers.py
----------------------
Generate synthetic NovaBank customers.

Fields: customer_id, customer_name, email, city, state, risk_category, customer_since

Usage (standalone, writes CSV to ./sample_data for inspection):
    python generate_customers.py

Usage (imported by the loader / notebook 02):
    from generate_customers import generate_customers
    df = generate_customers(n=500, seed=42)   # -> pandas DataFrame

All data is fabricated with Faker + a fixed seed. NO real PII.
"""
from __future__ import annotations

import random
from datetime import date, timedelta

import pandas as pd
from faker import Faker

# A small, India-flavoured city/state set so the demo feels realistic.
CITIES = [
    ("Mumbai", "MH"), ("Pune", "MH"), ("Bengaluru", "KA"), ("Chennai", "TN"),
    ("Hyderabad", "TS"), ("Delhi", "DL"), ("Noida", "UP"), ("Gurugram", "HR"),
    ("Ahmedabad", "GJ"), ("Kolkata", "WB"), ("Jaipur", "RJ"), ("Kochi", "KL"),
]
RISK_CATEGORIES = ["LOW", "MEDIUM", "HIGH"]
RISK_WEIGHTS = [0.6, 0.3, 0.1]  # most customers are low risk


def generate_customers(n: int = 500, seed: int = 42) -> pd.DataFrame:
    """Return a DataFrame of `n` synthetic customers.

    IDs are zero-padded and stable across runs given the same seed, so other
    generators can reference them deterministically.
    """
    fake = Faker("en_IN")
    Faker.seed(seed)
    random.seed(seed)

    today = date.today()
    rows = []
    for i in range(1, n + 1):
        name = fake.name()
        # Build an email from the name to keep it self-consistent + obviously fake.
        handle = name.lower().replace(" ", ".").replace("'", "")
        city, state = random.choice(CITIES)
        # customer_since: joined 30 days to ~12 years ago.
        days_ago = random.randint(30, 365 * 12)
        rows.append({
            "customer_id": f"CUST{i:06d}",
            "customer_name": name,
            "email": f"{handle}{random.randint(1, 999)}@example.com",
            "city": city,
            "state": state,
            "risk_category": random.choices(RISK_CATEGORIES, weights=RISK_WEIGHTS)[0],
            "customer_since": today - timedelta(days=days_ago),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    import os

    df = generate_customers()
    os.makedirs("sample_data", exist_ok=True)
    out = "sample_data/customers.csv"
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} customers -> {out}")
    print(df.head().to_string(index=False))
