"""
deploy_agent.py
---------------
Log the agent to MLflow, register it in Unity Catalog, and deploy it to Model
Serving with the Agent Framework. Run this inside Databricks (notebook 06).

STEPS
  1. Log the agent as an MLflow model using CODE-BASED logging (point at agent.py).
  2. Attach `resources` so the deployed endpoint is granted access to exactly the
     LLM endpoint + MCP/UC-function tools it uses (least privilege, automatic auth).
  3. Register the model into Unity Catalog.
  4. agents.deploy(...) -> a serving endpoint + a review app you can chat with.

REQUIRED PERMISSIONS
  - CREATE MODEL on the target UC schema (banking_ai.agents).
  - CAN QUERY on the LLM serving endpoint.
  - EXECUTE on banking_ai.tools.* + SELECT on banking_ai.core.* (the agent's
    service principal inherits these via the logged resources / your grants).

EXPECTED OUTPUT
  - A registered model version and a Model Serving endpoint (name printed).
  - Deployment takes a few minutes; the review app URL is printed when ready.
"""
from __future__ import annotations

import mlflow
from mlflow.models.resources import (
    DatabricksServingEndpoint,
    DatabricksFunction,
)

from model_config import CONFIG
from tools import ToolRegistry


def build_resources() -> list:
    """Resources the deployed agent needs access to."""
    resources: list = [DatabricksServingEndpoint(endpoint_name=CONFIG.llm_endpoint)]

    # Add the four UC functions explicitly (works even if MCP resource discovery
    # is unavailable). These names must match unity_catalog_functions/*.sql.
    for fn in (
        "get_customer_balance",
        "calculate_credit_utilization",
        "get_recent_transactions",
        "check_transaction_status",
    ):
        resources.append(
            DatabricksFunction(function_name=f"{CONFIG.catalog}.{CONFIG.tools_schema}.{fn}")
        )

    # Plus anything the MCP client reports (e.g. managed server resources).
    try:
        resources.extend(ToolRegistry().resources)
    except Exception as e:
        print(f"[deploy] could not auto-discover MCP resources ({e}); using explicit list.")
    return resources


def main() -> None:
    input_example = {
        "input": [{
            "role": "user",
            "content": (
                "For customer CUST000481: why was transaction TXN00000010 declined, "
                "and what is my available credit?"
            ),
        }]
    }

    mlflow.set_registry_uri("databricks-uc")  # register into Unity Catalog

    with mlflow.start_run(run_name="ABCbank_support_agent"):
        mlflow.set_tags(CONFIG.tags)
        logged = mlflow.pyfunc.log_model(
            name="agent",
            python_model="agent.py",          # code-based logging
            # Ship the helper modules the agent imports.
            code_paths=["model_config.py", "tools.py"],
            resources=build_resources(),
            input_example=input_example,
            pip_requirements=[
                "mlflow>=3.1.0",
                "databricks-sdk>=0.40.0",
                "databricks-mcp>=0.2.0",
                "openai>=1.60.0",
            ],
            registered_model_name=CONFIG.registered_model_name,
        )
        print("Logged + registered:", logged.model_uri)

    # ---- Deploy the newly registered version ----
    from databricks import agents
    from mlflow import MlflowClient

    version = MlflowClient().get_latest_versions(
        CONFIG.registered_model_name, stages=["None"]
    )[0].version

    print(f"Deploying {CONFIG.registered_model_name} v{version} ...")
    deployment = agents.deploy(CONFIG.registered_model_name, int(version))
    print("Endpoint:", getattr(deployment, "endpoint_name", "<pending>"))
    print("Review app:", getattr(deployment, "review_app_url", "<pending>"))
    print("Deployment started — it may take several minutes to become READY.")


if __name__ == "__main__":
    main()
