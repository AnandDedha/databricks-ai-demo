"""
tools.py  (Mosaic AI agent)
---------------------------
Bridges Databricks MCP tools into the OpenAI tool-calling format the LLM speaks,
and dispatches the LLM's tool calls back to MCP.

Flow:
    Databricks MCP server  --list_tools-->  we convert each to an OpenAI "function"
    LLM decides to call `banking_ai__tools__check_transaction_status(...)`
    we route that call back through the MCP client's call_tool()

We use the MANAGED MCP server for the Unity Catalog functions (no server to run),
and OPTIONALLY the custom MCP server for support tickets / external info.

Requires: databricks-mcp, databricks-sdk. Runs inside Databricks (uses the
notebook's default auth) or anywhere DATABRICKS_HOST/TOKEN are set.
"""
from __future__ import annotations

import json
from typing import Any, Callable

from model_config import CONFIG


def _make_mcp_client(server_url: str):
    """Create a DatabricksMCPClient for a given server URL."""
    from databricks.sdk import WorkspaceClient
    from databricks_mcp import DatabricksMCPClient

    ws = WorkspaceClient()
    return DatabricksMCPClient(server_url=server_url, workspace_client=ws)


def _mcp_tool_to_openai(tool) -> dict:
    """Convert one MCP tool definition to an OpenAI `tools` entry."""
    # MCP tools expose name, description, and an inputSchema (JSON schema).
    schema = getattr(tool, "inputSchema", None) or {"type": "object", "properties": {}}
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": getattr(tool, "description", "") or "",
            "parameters": schema,
        },
    }


class ToolRegistry:
    """Discovers tools from one or more MCP servers and dispatches calls.

    Attributes:
        openai_tools: list of tool specs to pass to the LLM.
        resources:    Databricks resources to log with the model (so the deployed
                      endpoint is granted access to exactly these tools).
    """

    def __init__(self) -> None:
        from databricks.sdk import WorkspaceClient

        self.ws = WorkspaceClient()
        self.host = self.ws.config.host
        self._clients: dict[str, Any] = {}          # tool_name -> mcp client
        self.openai_tools: list[dict] = []
        self.resources: list = []
        self._discover()

    def _add_server(self, server_url: str) -> None:
        client = _make_mcp_client(server_url)
        for tool in client.list_tools():
            self.openai_tools.append(_mcp_tool_to_openai(tool))
            self._clients[tool.name] = client
        # Collect resources for deployment auth (managed servers support this).
        try:
            self.resources.extend(client.get_databricks_resources())
        except Exception:
            pass  # custom servers may not implement this

    def _discover(self) -> None:
        # 1) Managed MCP server for the UC functions (always on).
        uc_url = f"{self.host}{CONFIG.uc_functions_mcp_path()}"
        self._add_server(uc_url)

        # 2) Optional custom MCP server (support tickets + external info).
        if CONFIG.custom_mcp_url:
            try:
                self._add_server(CONFIG.custom_mcp_url)
            except Exception as e:  # don't fail the whole agent if custom server is down
                print(f"[tools] custom MCP server unavailable, skipping: {e}")

    def call(self, name: str, arguments: dict) -> str:
        """Execute a tool call and return a string result for the LLM."""
        client = self._clients.get(name)
        if client is None:
            return json.dumps({"error": f"unknown tool '{name}'"})
        result = client.call_tool(name, arguments)
        # MCP results carry a `.content` list of blocks; join their text.
        try:
            parts = [getattr(b, "text", str(b)) for b in result.content]
            return "\n".join(parts) if parts else json.dumps({"result": "empty"})
        except Exception:
            return str(result)


# Convenience for notebook 04 to eyeball the discovered tools.
def describe_tools() -> list[str]:
    reg = ToolRegistry()
    return [t["function"]["name"] for t in reg.openai_tools]


if __name__ == "__main__":
    # Only works inside Databricks / with workspace auth configured.
    print("Discovered tools:")
    for n in describe_tools():
        print("  -", n)
