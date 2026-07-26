# Architecture

## The idea in one picture

```
                          ┌──────────────────────────┐
   Customer question ───► │        THE AGENT         │
                          │  (one of three builders) │
                          └────────────┬─────────────┘
                                       │ decides which tool(s) to call
        ┌──────────────────────────────┼──────────────────────────────┐
        ▼                              ▼                               ▼
┌───────────────┐          ┌──────────────────────┐        ┌────────────────────┐
│ UC Functions  │          │  Managed MCP server  │        │  Custom MCP server │
│ (governed SQL)│◄─────────│ /api/2.0/mcp/functions│        │ tickets + external │
│ 4 tools       │          │ /banking_ai/tools    │        │ info (this repo)   │
└───────┬───────┘          └──────────┬───────────┘        └─────────┬──────────┘
        │                             │                              │
        └─────────────┬───────────────┴──────────────────────────────┘
                      ▼
        ┌──────────────────────────────────────┐
        │   Delta tables — banking_ai.core.*    │
        │  customers · accounts · deposits ·    │
        │  cards · transactions · tickets       │
        └──────────────────────────────────────┘
                      ▲
                      │ Unity Catalog governs every read + every tool call
```

## Layers

**1. Data (Delta + Unity Catalog).** Six synthetic tables in `banking_ai.core`.
Unity Catalog is the governance boundary — grants decide who (and which agent
service principal) can read data or run a tool.

**2. Tools.**
- *Unity Catalog functions* (`banking_ai.tools.*`) wrap SQL as callable tools.
  Their `COMMENT`s are the descriptions the LLM reads to choose them.
- *Managed MCP server* auto-exposes those functions over MCP — no server to run.
- *Custom MCP server* (`mcp/`) adds tools for data outside the lakehouse.

**3. The agent — three ways to build it.**
- **AI Playground** — UI; attach tools, test prompts, compare models.
- **Agent Bricks** — low-code patterns (we use Knowledge Assistant) with eval +
  deploy + monitor built in.
- **Mosaic AI Agent Framework** — code; an MLflow `ResponsesAgent` you fully control.

**4. Lifecycle (MLflow + Model Serving).** Log → register in Unity Catalog →
evaluate (AI-as-a-Judge, CLEARS rubric) → deploy to Model Serving → monitor traces.

## How a question becomes an answer (flagship example)

> "For customer CUST000481: why was transaction TXN00000010 declined, and what is
> my available credit?"

1. The LLM sees the tools' descriptions and the question.
2. It calls `check_transaction_status('TXN00000010')` → reason:
   `INSUFFICIENT_CREDIT_LIMIT` + plain-English explanation.
3. It calls `calculate_credit_utilization('CUST000481')` → available credit
   ₹39,263.08, utilization 86.9%.
4. Unity Catalog authorises each call; results come back.
5. The LLM composes one answer combining both facts and a next step ("make a
   payment or request a limit increase"), and lists the tools it used.

## Where each builder fits in the lifecycle

| Stage | AI Playground | Agent Bricks | Agent Framework |
|-------|---------------|--------------|-----------------|
| Prototype prompt/tools | ✅ best | ✅ | ✅ (code) |
| Ground in documents | — | ✅ (Knowledge Assistant) | ✅ (add retrieval) |
| Custom control flow | — | limited | ✅ best |
| Evaluate | manual | ✅ built-in | ✅ (Agent Evaluation) |
| Deploy to Serving | export then deploy | ✅ one click | ✅ `agents.deploy` |
| Monitor | — | ✅ built-in | ✅ traces + monitoring |

See `comparison.md` for the decision guide.
