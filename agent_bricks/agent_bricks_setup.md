# Agent Bricks — Knowledge Assistant (low-code)

Agent Bricks is Databricks' governed platform for building agents from
**predefined patterns** without writing the agent loop yourself. As of DAIS 2026
it's a full agent platform (Choice / Context / Control); the pattern we use here,
**Knowledge Assistant**, went GA in January 2026.

## Which pattern, and why

| Pattern | What it does | Fit for our bank |
|---|---|---|
| **Knowledge Assistant** ✅ | Answers questions grounded in your documents/knowledge, with citations, using *Instructed Retrieval* (better than plain RAG). | Perfect for a support-history + policy assistant. **We use this.** |
| Information Extraction | Pulls structured fields from unstructured docs. | Good for parsing scanned KYC forms — not our demo. |
| Multi-Agent Supervisor | Orchestrates several sub-agents/tools. | The scale-up once you outgrow one assistant. |
| Custom LLM | Fine-tune / prompt-optimize a task-specific model. | For classification/labelling tasks. |

We pick **Knowledge Assistant** because our goal is a support assistant that
answers "how do we handle X?" from real ticket history + policy notes, and we
want it live in minutes with governance, evaluation, and monitoring included.

## Input data requirements

Knowledge Assistant grounds answers in **knowledge sources**. We give it two:

1. **Support ticket history** — `banking_ai.core.support_tickets`
   (`issue_description` is the useful text). Create a small text/markdown export
   or a Delta-backed source; the ticket descriptions become searchable knowledge.
2. **Policy notes** — a handful of short markdown docs (decline reasons, dispute
   process, card-block policy). You can reuse the text in `mcp/tools.py`
   (`EXTERNAL_BANKING_INFO`) — drop each entry into a `.md` file in a Unity
   Catalog **Volume**, e.g. `banking_ai.core.knowledge/policies/`.

Requirements checklist:
- A Unity Catalog **Volume** or Delta table holding the source text.
- `READ VOLUME` / `SELECT` granted to you and (later) the agent principal.
- Serverless compute enabled.

## Build it (UI, ~5–10 minutes)

1. Left nav → **Agents** → **Agent Bricks** → **Knowledge Assistant** → *Create*.
2. **Name:** `novabank-knowledge-assistant`.
3. **Add knowledge sources:** point it at the Volume with the policy docs and/or
   the ticket-description export. Give each source a one-line description (the
   agent uses it to route retrieval).
4. **Instructions:** paste `sample_instructions.md`.
5. Click **Create**. Agent Bricks builds and indexes automatically — no chunking
   or embedding code to write.

## Configuration you actually touch
- **Instructions** (tone, scope, refusal behaviour) — see `sample_instructions.md`.
- **Knowledge source descriptions** — short, accurate, one per source.
- Optionally, model choice and guardrails. Almost everything else is managed.

## Evaluation
1. Open the assistant → **Evaluate**.
2. Upload `evaluation_questions.json` (question + optional expected facts).
3. Agent Bricks runs **AI-as-a-Judge** scoring and reports quality using the
   **CLEARS** rubric (Correctness, Latency, Execution, Adherence, Relevance,
   Safety). Review low-scoring rows, then improve instructions or add a missing
   knowledge source and re-run. Aim for ≥ ~100 eval questions for a real agent;
   the JSON here is a starter set.

## Deployment
- Click **Deploy**. Agent Bricks stands up a **Model Serving** endpoint and a
  review/chat app automatically. No `deploy_agent.py` needed for this path — that
  script exists only for the *code-based* Mosaic AI agent.
- Share the endpoint or the chat app URL with reviewers.

## Monitoring
- **Traces & monitoring** are built in: every request's retrieval + generation is
  logged and governed in the lakehouse, and integrates with Lakewatch for
  PII/quality alerts. Watch latency, thumbs-up/down, and unanswered questions,
  then feed gaps back into the knowledge sources.

## When Agent Bricks beats Playground or custom code
- You want a **grounded, cited** assistant **fast**, with eval + deploy + monitor
  included, and you don't need bespoke control flow.
- Choose **AI Playground** instead for throwaway prompt/model/tool experiments.
- Choose the **Mosaic AI Agent Framework** (code) instead when you need custom
  multi-step logic, precise tool orchestration, or to package the agent as your
  own Python model. See `docs/comparison.md`.
