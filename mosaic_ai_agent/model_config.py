"""
model_config.py
---------------
One place for every value the agent, deploy, and eval scripts share. Edit this,
not the other files.

WHY A CONFIG FILE: the agent code should be identical across dev/staging/prod;
only these values change. Keeping them here also lets MLflow log the config
alongside the model.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    # --- Unity Catalog locations ---
    catalog: str = "banking_ai"
    data_schema: str = "core"          # tables live here
    tools_schema: str = "tools"        # UC functions live here

    # Where the registered agent model will live in Unity Catalog.
    registered_model_name: str = "banking_ai.agents.ABCbank_support_agent"

    # --- LLM endpoint (must support tool calling) ---
    # Check Serving -> Foundation Models for what's available in your workspace.
    llm_endpoint: str = "databricks-claude-3-7-sonnet"

    # --- Managed MCP server for our UC functions ---
    # Full URL is built at runtime from the workspace host:
    #   {host}/api/2.0/mcp/functions/{catalog}/{tools_schema}
    # Tools appear as: banking_ai__tools__<function_name>
    def uc_functions_mcp_path(self) -> str:
        return f"/api/2.0/mcp/functions/{self.catalog}/{self.tools_schema}"

    # --- Optional custom MCP server (mcp/mcp_server.py) ---
    # If you deploy it (e.g. as a Databricks App) put its base URL here to enable
    # the support_tickets / external_banking_info tools. Leave None to skip.
    custom_mcp_url: str | None = None

    # --- Agent behaviour ---
    max_tool_iterations: int = 5   # safety cap on the tool-calling loop
    system_prompt: str = (
        "You are ABCBank's customer support agent. You answer questions about "
        "accounts, credit cards, transactions, and support history by calling the "
        "provided tools. Rules:\n"
        "1. Never guess balances, limits, utilization, available credit, or decline "
        "reasons — always call a tool and use its result.\n"
        "2. Chain tools when needed (e.g. check a decline reason AND look up available "
        "credit before answering).\n"
        "3. If you lack an identifier (customer/account/card/transaction id), ask for it.\n"
        "4. Quote the exact figures the tools return.\n"
        "5. End declined-transaction answers with one practical next step.\n"
    )

    # Tags attached to the MLflow run / model.
    tags: dict = field(default_factory=lambda: {"project": "banking-ai-agents", "pattern": "responses-agent"})


CONFIG = AgentConfig()
