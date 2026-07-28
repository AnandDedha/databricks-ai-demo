"""
evaluate_agent.py
-----------------
Evaluate the agent with Mosaic AI Agent Evaluation (MLflow 3 GenAI eval).
Uses AI-as-a-Judge scorers so you get quality signal without hand-labelling every
answer. Run BEFORE you deploy (notebook 06 runs eval, then deploy).

WHAT IT MEASURES
  - Correctness / Guideline adherence (did it follow our rules?)
  - Relevance to the question
  - Safety
  These map onto Databricks' CLEARS rubric (Correctness, Latency, Execution,
  Adherence, Relevance, Safety).

REQUIRED PERMISSIONS: CAN QUERY on the judge model endpoint (Databricks provides
a default judge). EXECUTE/SELECT on the tools/data so the agent can actually run.

EXPECTED OUTPUT: an MLflow evaluation run with per-question scores + an aggregate
table. Open it from the notebook's MLflow experiment.
"""
from __future__ import annotations

import mlflow

from agent import AGENT
from model_config import CONFIG


# A small but meaningful eval set. Expand to 100+ for anything real.
EVAL_DATA = [
    {
        "inputs": {"input": [{"role": "user",
            "content": "What is the credit utilization and available credit for CUST000481?"}]},
        "expectations": {
            "expected_facts": ["utilization around 86.9%", "available credit around 39,263"],
        },
    },
    {
        "inputs": {"input": [{"role": "user",
            "content": "Why was transaction TXN00000010 declined?"}]},
        "expectations": {
            "expected_facts": ["insufficient credit limit", "near the credit limit"],
        },
    },
    {
        "inputs": {"input": [{"role": "user",
            "content": ("For customer CUST000481: why was transaction TXN00000010 declined, "
                        "and what is my available credit?")}]},
        "expectations": {
            "expected_facts": [
                "declined due to insufficient available credit",
                "available credit figure is quoted",
                "suggests a payment or limit increase",
            ],
        },
    },
    {
        "inputs": {"input": [{"role": "user",
            "content": "Show the last 3 transactions on card CARD000206."}]},
        "expectations": {"expected_facts": ["lists recent transactions with status"]},
    },
    {
        "inputs": {"input": [{"role": "user",
            "content": "What's my available credit?"}]},  # no ID given
        "expectations": {"expected_facts": ["asks for a customer or card id"]},
    },
]


def predict_fn(input):  # noqa: A002  (name mirrors the request key)
    """Adapter so the evaluator can call our agent per row."""
    from mlflow.types.responses import ResponsesAgentRequest

    response = AGENT.predict(ResponsesAgentRequest(input=input))
    item = response.output[0]
    text = item["content"] if isinstance(item, dict) else item.content
    return text


def main() -> None:
    from mlflow.genai.scorers import Correctness, RelevanceToQuery, Safety, Guidelines

    guidelines = Guidelines(
        name="banking_rules",
        guidelines=(
            "The answer must not invent balances, limits, or decline reasons; it should "
            "reflect tool results. If no identifier is provided, it should ask for one. "
            "Declined-transaction answers should include a practical next step."
        ),
    )

    with mlflow.start_run(run_name="ABCbank_agent_eval"):
        results = mlflow.genai.evaluate(
            data=EVAL_DATA,
            predict_fn=predict_fn,
            scorers=[Correctness(), RelevanceToQuery(), Safety(), guidelines],
        )
        print("Evaluation complete. Aggregate metrics:")
        try:
            print(results.metrics)
        except Exception:
            print("See the MLflow experiment UI for detailed per-row scores.")


if __name__ == "__main__":
    main()
