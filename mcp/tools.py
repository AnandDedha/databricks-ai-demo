"""
tools.py
--------
Business logic for the custom MCP server, kept separate from the server wiring
so it's easy to unit-test.

Two capabilities the managed UC-function tools don't cover:
  1. get_support_tickets(customer_id)  -> a customer's recent service tickets
  2. get_external_banking_info(topic)  -> "external" reference info (rates,
     policies, RBI-style guidance) that doesn't live in our tables.

Data source resolution (in order):
  - If DATABRICKS_HOST + DATABRICKS_TOKEN + DATABRICKS_HTTP_PATH are set, query
    Delta via the Databricks SQL connector.
  - Otherwise fall back to the local CSV in ../data_generation/sample_data
    (great for local dev + the tutorial's offline test).
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

# ---------------------------------------------------------------------------
# Static "external" knowledge base. In the real world this might be a call to a
# core-banking API or an RBI circular service; here it's a curated dict so the
# demo is deterministic and offline-friendly.
# ---------------------------------------------------------------------------
EXTERNAL_BANKING_INFO: dict[str, str] = {
    "credit_card_decline_reasons": (
        "Common reasons a credit card transaction is declined: insufficient available "
        "credit, a blocked or expired card, suspected fraud, incorrect CVV/PIN, or an "
        "unsupported merchant category. The customer can usually resolve limit issues by "
        "paying down the balance or requesting a limit increase."
    ),
    "interest_rates": (
        "Indicative NovaBank rates (illustrative, not live): Savings 3.0-3.5% p.a.; "
        "Fixed Deposit 5.5-7.75% p.a. depending on tenure; Credit card finance charge "
        "up to 3.5% per month on revolving balances."
    ),
    "credit_utilization_guidance": (
        "Keeping credit utilization below 30% is generally good for a customer's credit "
        "score. Above 80% utilization increases the chance of a transaction being declined "
        "for insufficient available credit."
    ),
    "card_block_policy": (
        "A card may be auto-blocked after repeated failed attempts or fraud signals. "
        "Unblocking requires identity verification. Report lost/stolen cards immediately "
        "to have them hot-listed."
    ),
    "dispute_process": (
        "To dispute a charge, raise a ticket within 60 days. NovaBank provisionally credits "
        "the amount and files a chargeback; resolution typically takes 7-45 days."
    ),
}


def get_external_banking_info(topic: str) -> dict[str, Any]:
    """Return reference info for a topic. Fuzzy-matches on substrings so the LLM
    doesn't need the exact key."""
    key = (topic or "").strip().lower().replace(" ", "_")
    if key in EXTERNAL_BANKING_INFO:
        return {"topic": key, "info": EXTERNAL_BANKING_INFO[key]}
    # substring match
    for k, v in EXTERNAL_BANKING_INFO.items():
        if key and (key in k or k in key):
            return {"topic": k, "info": v}
    return {
        "topic": topic,
        "info": "No specific reference found. Available topics: " + ", ".join(EXTERNAL_BANKING_INFO),
    }


# ---------------------------------------------------------------------------
# Support tickets — Databricks first, local CSV fallback.
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _local_tickets():
    import csv

    here = os.path.dirname(__file__)
    path = os.path.join(here, "..", "data_generation", "sample_data", "support_tickets.csv")
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _query_databricks(customer_id: str, limit: int) -> list[dict] | None:
    host = os.environ.get("DATABRICKS_HOST")
    token = os.environ.get("DATABRICKS_TOKEN")
    http_path = os.environ.get("DATABRICKS_HTTP_PATH")
    if not (host and token and http_path):
        return None
    try:
        from databricks import sql  # databricks-sql-connector
    except Exception:
        return None
    conn = sql.connect(server_hostname=host.replace("https://", ""),
                       http_path=http_path, access_token=token)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ticket_id, issue_type, issue_description, ticket_status,
                       CAST(created_timestamp AS STRING) AS created_timestamp
                FROM banking_ai.core.support_tickets
                WHERE customer_id = ?
                ORDER BY created_timestamp DESC
                LIMIT ?
                """,
                [customer_id, limit],
            )
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        conn.close()


def get_support_tickets(customer_id: str, limit: int = 5) -> dict[str, Any]:
    """Return up to `limit` recent support tickets for a customer."""
    rows = _query_databricks(customer_id, limit)
    if rows is None:  # local fallback
        rows = [r for r in _local_tickets() if r.get("customer_id") == customer_id]
        rows = sorted(rows, key=lambda r: r.get("created_timestamp", ""), reverse=True)[:limit]
        rows = [
            {k: r[k] for k in ("ticket_id", "issue_type", "issue_description",
                               "ticket_status", "created_timestamp") if k in r}
            for r in rows
        ]
    return {"customer_id": customer_id, "count": len(rows), "tickets": rows}


if __name__ == "__main__":
    # Smoke test against local CSV.
    print(get_external_banking_info("credit card decline reasons")["info"][:80], "...")
    sample = get_support_tickets("CUST000001")
    print("tickets for CUST000001:", sample["count"])
