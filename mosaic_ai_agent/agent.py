"""
agent.py  (Mosaic AI Agent Framework)
-------------------------------------
A production-shaped support agent built on the interface Databricks recommends:
MLflow's `ResponsesAgent`. Wrapping our logic in ResponsesAgent gives us
out-of-the-box compatibility with AI Playground, Agent Evaluation, Model Serving,
and tracing — without hand-writing any of that plumbing.

WHAT THE AGENT DOES (step by step)
  1. Receives the customer's message(s).
  2. Sends them to a tool-calling LLM along with the tool catalog discovered from
     the Databricks managed MCP server (our UC functions) + optional custom MCP.
  3. If the model asks to call a tool, we run it through MCP (Unity Catalog checks
     permissions), feed the result back, and loop — up to a safety cap.
  4. When the model stops asking for tools, we return its final answer PLUS a short
     "tools used" explanation (a tutorial requirement, and good for transparency).

This file ends with `mlflow.models.set_model(AGENT)` so `deploy_agent.py` can log
it. Run it directly (inside Databricks) for a quick local smoke test.
"""
from __future__ import annotations

import json
import uuid
from typing import Any, Generator

import mlflow
from mlflow.pyfunc import ResponsesAgent
from mlflow.types.responses import (
    ResponsesAgentRequest,
    ResponsesAgentResponse,
    ResponsesAgentStreamEvent,
)

from model_config import CONFIG
from tools import ToolRegistry

# Trace every LLM + tool call automatically so the MLflow UI shows the full reasoning.
mlflow.openai.autolog()


class NovaBankSupportAgent(ResponsesAgent):
    """A tool-calling support agent."""

    def __init__(self) -> None:
        self._registry: ToolRegistry | None = None
        self._client = None

    # ---- lazy init so model loading is cheap; connections open on first call ----
    @property
    def registry(self) -> ToolRegistry:
        if self._registry is None:
            self._registry = ToolRegistry()
        return self._registry

    @property
    def client(self):
        if self._client is None:
            from databricks.sdk import WorkspaceClient
            self._client = WorkspaceClient().serving_endpoints.get_open_ai_client()
        return self._client

    # ---- helpers -----------------------------------------------------------
    @staticmethod
    def _to_chat_messages(request: ResponsesAgentRequest) -> list[dict]:
        """Convert Responses-style input items to chat.completions messages."""
        messages: list[dict] = [{"role": "system", "content": CONFIG.system_prompt}]
        for item in request.input:
            item = item.model_dump() if hasattr(item, "model_dump") else dict(item)
            role = item.get("role", "user")
            content = item.get("content", "")
            # content can be a string or a list of content blocks — normalise to text.
            if isinstance(content, list):
                content = " ".join(
                    b.get("text", "") if isinstance(b, dict) else str(b) for b in content
                )
            messages.append({"role": role, "content": content})
        return messages

    @mlflow.trace(name="tool_calling_loop")
    def _run(self, messages: list[dict]) -> tuple[str, list[dict]]:
        """Run the tool-calling loop; return (final_text, tools_used)."""
        tools = self.registry.openai_tools
        tools_used: list[dict] = []

        for _ in range(CONFIG.max_tool_iterations):
            resp = self.client.chat.completions.create(
                model=CONFIG.llm_endpoint,
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )
            msg = resp.choices[0].message

            # No tool calls -> we have the final answer.
            if not getattr(msg, "tool_calls", None):
                return msg.content or "", tools_used

            # Record the assistant's tool-call turn, then execute each call.
            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [tc.model_dump() for tc in msg.tool_calls],
            })
            for tc in msg.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result = self.registry.call(name, args)
                tools_used.append({"tool": name, "arguments": args})
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

        # Hit the iteration cap — ask for a best-effort final answer with no tools.
        resp = self.client.chat.completions.create(
            model=CONFIG.llm_endpoint, messages=messages,
        )
        return resp.choices[0].message.content or "", tools_used

    @staticmethod
    def _explain(tools_used: list[dict]) -> str:
        if not tools_used:
            return "\n\n_(No tools were needed for this answer.)_"
        lines = [f"- `{t['tool']}` with {json.dumps(t['arguments'])}" for t in tools_used]
        return "\n\n**Tools used:**\n" + "\n".join(lines)

    # ---- required entry point ---------------------------------------------
    def predict(self, request: ResponsesAgentRequest) -> ResponsesAgentResponse:
        messages = self._to_chat_messages(request)
        answer, tools_used = self._run(messages)
        answer_with_explanation = answer + self._explain(tools_used)

        output_item = self.create_text_output_item(
            text=answer_with_explanation,
            id=str(uuid.uuid4()),
        )
        return ResponsesAgentResponse(
            output=[output_item],
            custom_outputs={"tools_used": tools_used},
        )

    # ---- optional streaming (nice-to-have; Playground uses it if present) --
    def predict_stream(
        self, request: ResponsesAgentRequest
    ) -> Generator[ResponsesAgentStreamEvent, None, None]:
        # Simple non-incremental stream: compute, then emit as one completed item.
        response = self.predict(request)
        for item in response.output:
            yield ResponsesAgentStreamEvent(type="response.output_item.done", item=item)


AGENT = NovaBankSupportAgent()
mlflow.models.set_model(AGENT)


if __name__ == "__main__":
    # Local smoke test (run inside Databricks). Uses the flagship question.
    req = ResponsesAgentRequest(input=[{
        "role": "user",
        "content": (
            "For customer CUST000481: why was transaction TXN00000010 declined, "
            "and what is my available credit?"
        ),
    }])
    out = AGENT.predict(req)
    print(out.output[0]["content"] if isinstance(out.output[0], dict) else out.output[0].content)
