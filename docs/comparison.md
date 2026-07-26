# Comparison: three ways to build agents on Databricks

## The one-line version

| Option | Best suited for |
|--------|-----------------|
| **AI Playground** | Prompt testing, model comparison, and quick tool experiments |
| **Agent Bricks** | Low-code agent development using predefined patterns |
| **Mosaic AI Agent Framework** | Fully customizable, code-based production agents |

## Deeper comparison

| Dimension | AI Playground | Agent Bricks | Mosaic AI Agent Framework |
|---|---|---|---|
| Interface | UI chat | UI (pattern wizard) | Python + MLflow |
| Code required | None | Little/none | Yes (`ResponsesAgent`) |
| Time to first result | Minutes | Minutes | An hour+ |
| Control over logic | Low | Medium | Full |
| Tools | UC functions, MCP | Knowledge sources, MCP, tools | Anything callable + MCP |
| Grounding/RAG | Manual | Built-in (Instructed Retrieval) | You build it |
| Evaluation | Manual, ad-hoc | Built-in (CLEARS) | Agent Evaluation (AI judge) |
| Deployment | Export → deploy | One-click serving + review app | `agents.deploy` |
| Monitoring | — | Built-in traces | MLflow traces + serving monitoring |
| Governance | Unity Catalog | Unity Catalog | Unity Catalog |
| Best for | Experimentation | Fast, governed, standard patterns | Bespoke production agents |

## A simple decision guide

```
Are you just experimenting with prompts, models, or tools?
        │ yes ──► AI Playground
        │ no
        ▼
Does a predefined pattern fit (knowledge Q&A, extraction, supervisor)
and you want it live fast with eval + deploy + monitor included?
        │ yes ──► Agent Bricks
        │ no
        ▼
Do you need custom control flow, precise tool orchestration,
or to package the agent as your own model?
        │ yes ──► Mosaic AI Agent Framework
```

## They're a pipeline, not rivals

A realistic workflow uses all three:

1. **Prototype** the prompt and try tools in **AI Playground**; compare two models.
2. If a pattern fits, ship a first version fast with **Agent Bricks** and evaluate it.
3. When you outgrow the pattern (custom steps, multi-tool orchestration, bespoke
   packaging), rebuild in the **Mosaic AI Agent Framework** — reusing the same UC
   functions, MCP tools, and eval questions you already created.

Because tools are **Unity Catalog functions / MCP servers**, they're shared across
all three — you never rewrite the tools, only the agent around them.

## For our banking demo specifically
- **Playground:** proved the flagship multi-tool question works and picked a model.
- **Agent Bricks (Knowledge Assistant):** a grounded support-knowledge assistant
  over ticket history + policy notes, deployed in minutes.
- **Agent Framework:** the `ResponsesAgent` that chains `check_transaction_status`
  + `calculate_credit_utilization`, returns the tools it used, and deploys to
  Model Serving — the version you'd actually run in production.
