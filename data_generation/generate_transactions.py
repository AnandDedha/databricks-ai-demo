"""
generate_transactions.py
------------------------
Generate synthetic transactions across BOTH deposit/checking accounts and
credit cards. About 12% are DECLINED, each with a realistic decline_reason.

For credit-card declines we make the reason consistent with the card's state
where we can (BLOCKED card -> CARD_BLOCKED; near-limit -> INSUFFICIENT_CREDIT_LIMIT),
so the tutorial's flagship question is answerable end-to-end:

    "Why was my credit card transaction declined, and what is my available credit?"

Fields: transaction_id, account_id, transaction_type, merchant_name,
        transaction_amount, transaction_status, transaction_timestamp, decline_reason
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

import pandas as pd

MERCHANTS = [
    "Amazon India", "Flipkart", "Swiggy", "Zomato", "BigBasket", "Reliance Digital",
    "IRCTC", "MakeMyTrip", "Croma", "DMart", "Apollo Pharmacy", "BookMyShow",
    "Uber", "Ola", "Myntra", "Tata CLiQ", "Nykaa", "Jio Recharge",
]
TXN_TYPES = ["PURCHASE", "WITHDRAWAL", "DEPOSIT", "TRANSFER", "PAYMENT"]

# Reasons split by the kind of account so they read sensibly.
CARD_DECLINE_REASONS = [
    "INSUFFICIENT_CREDIT_LIMIT",
    "CARD_BLOCKED",
    "SUSPECTED_FRAUD",
    "EXPIRED_CARD",
    "INCORRECT_CVV",
    "MERCHANT_NOT_SUPPORTED",
]
ACCOUNT_DECLINE_REASONS = [
    "INSUFFICIENT_FUNDS",
    "ACCOUNT_FROZEN",
    "DAILY_LIMIT_EXCEEDED",
    "SUSPECTED_FRAUD",
    "INVALID_PIN",
]


def generate_transactions(
    accounts: pd.DataFrame,
    cards: pd.DataFrame,
    n: int = 5000,
    seed: int = 45,
) -> pd.DataFrame:
    random.seed(seed)
    now = datetime.now()

    account_ids = accounts["account_id"].tolist()
    # Fast lookups for card-aware decline reasons.
    card_status = dict(zip(cards["card_id"], cards["card_status"]))
    card_util = dict(zip(cards["card_id"], cards["utilization_percentage"]))
    card_ids = cards["card_id"].tolist()

    rows = []
    for i in range(1, n + 1):
        # ~45% of transactions are on cards (they generate the interesting declines).
        is_card = random.random() < 0.45
        acct = random.choice(card_ids) if is_card else random.choice(account_ids)

        status = random.choices(["APPROVED", "DECLINED", "PENDING"], weights=[0.85, 0.12, 0.03])[0]
        decline_reason = None
        if status == "DECLINED":
            if is_card:
                # Prefer a reason consistent with the card's real state.
                if card_status.get(acct) == "BLOCKED":
                    decline_reason = "CARD_BLOCKED"
                elif card_status.get(acct) == "EXPIRED":
                    decline_reason = "EXPIRED_CARD"
                elif card_util.get(acct, 0) >= 85:
                    decline_reason = "INSUFFICIENT_CREDIT_LIMIT"
                else:
                    decline_reason = random.choice(CARD_DECLINE_REASONS)
            else:
                decline_reason = random.choice(ACCOUNT_DECLINE_REASONS)

        rows.append({
            "transaction_id": f"TXN{i:08d}",
            "account_id": acct,
            "transaction_type": "PURCHASE" if is_card else random.choice(TXN_TYPES),
            "merchant_name": random.choice(MERCHANTS),
            "transaction_amount": round(random.uniform(50, 75_000), 2),
            "transaction_status": status,
            # Spread timestamps across the last 120 days.
            "transaction_timestamp": now - timedelta(
                days=random.randint(0, 120),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            ),
            "decline_reason": decline_reason,
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    import os
    from generate_customers import generate_customers
    from generate_accounts import generate_accounts
    from generate_credit_cards import generate_credit_cards

    customers = generate_customers()
    accounts, _ = generate_accounts(customers)
    cards = generate_credit_cards(customers)
    txns = generate_transactions(accounts, cards)
    os.makedirs("sample_data", exist_ok=True)
    txns.to_csv("sample_data/transactions.csv", index=False)
    n_declined = (txns["transaction_status"] == "DECLINED").sum()
    print(f"Wrote {len(txns)} transactions ({n_declined} declined) -> sample_data/transactions.csv")
    print(txns.head().to_string(index=False))
