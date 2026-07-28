# Agent Bricks — Information Extraction (low-code)

Agent Bricks is Databricks' governed surface for building agents from **predefined
templates** without writing the agent loop yourself. The UI has evolved: it's now the
umbrella for Databricks' AI capabilities, and the templates you'll see today are:

| Template | What it does | Usacases |
|---|---|---|
| **Supervisor** | Orchestrates multiple sub-agents/tools and Genie spaces behind one interface (GA). |  **Supervisor** is the scale-up once you have several agents/Genie spaces to route between. |
| **Information Extraction** ✅ | Turns a large volume of unstructured text/PDFs/images into a **structured table** of fields you define. **We use this.** |
| **Genie** | Natural-language analytics over governed tables via a Genie space. |  **Genie** would be the pick for "answer analytics questions over the tables. |
| **Text Classification** | Sorts documents into predefined categories at scale. | **Text Classification** fits if you only need a single category label per ticket. |
| **Custom** | Bring any model/framework (Custom LLM / Custom Agents) with full lifecycle support. | **Custom** is for when no template fits and you want full control (that's what the `mosaic_ai_agent/` code path demonstrates instead). |

## Use case 1 — Extract from PDFs in a Volume

Drop your PDFs into a Unity Catalog Volume and let the agent read them directly. You define the schema — the fields you want back — and Information Extraction pulls those fields from every document, no OCR or parsing code to write. Ideal when the source is scanned or born-digital PDFs (KYC forms, statements, contracts): point the agent at the Volume, define the schema, and get one structured row per document.

## Use case 2 — Structure free-text support tickets

Turn the free-text issue_description on our support tickets into a clean, queryable table — issue category, product, urgency, referenced IDs, and requested action. This is exactly what the template is built for: transforming unlabelled text into structured fields, one row per document, then evaluated and deployed as a serverless endpoint you can call at scale with ai_query().

## Input data

Information Extraction reads a **column of text** (must be `string`). We use the
support tickets:

- **Source:** `banking_ai.core.support_tickets`
- **Request column (text to extract from):** `issue_description`
- (Optional) **Ground-truth column:** a hand-labelled `expected_json` column on a
  small sample, used for evaluation.

If your tickets were PDFs/images instead of text, you'd first run
`ai_parse_document()` to get the text column — not needed here, our descriptions are
already text.

Requirements checklist:
- **Mosaic AI Agent Bricks** enabled for the workspace (Beta preview toggle).
- **Serverless compute** enabled.
- **Unity Catalog** enabled, with access to foundation models via the `system.ai`
  schema.
- A **serverless budget policy** with a non-zero budget.
- `SELECT` on `banking_ai.core.support_tickets`.

## The extraction schema (the heart of it)

Define the fields you want pulled from each ticket. Each field = **name + type +
description** (the description is what the model uses, so write it well):

| Field | Type | Description (what to tell the agent) |
|---|---|---|
| `issue_category` | string | The main issue: one of declined_transaction, dispute, card_lost, statement_query, limit_increase, other. |
| `product` | string | Product referenced: credit_card, savings_account, current_account, or fixed_deposit. |
| `mentioned_transaction_id` | string | Any transaction ID referenced (format TXN########), else null. |
| `mentioned_card_id` | string | Any card ID referenced (format CARD######), else null. |
| `customer_sentiment` | string | frustrated, neutral, or satisfied. |
| `urgency` | string | low, medium, or high, based on tone and issue. |
| `requested_action` | string | Short phrase for what the customer wants done. |
| `contains_pii` | boolean | true if the text contains PII (full card number, ID, etc.). |

This is also why IE is a nice demo for our flagship: a ticket that mentions
**TXN00000010** gets that ID extracted into `mentioned_transaction_id`, which you can
then join straight back to `banking_ai.core.transactions`.

## Build it (UI, ~5–10 minutes)

1. Left nav → **Agent Bricks** → **Information Extraction** → *Build*.
2. **Name:** `novabank-ticket-extraction`.
3. **Connect data:** select `banking_ai.core.support_tickets` and set the request
   column to `issue_description`.
4. **Define the schema:** in the **Schema Editor**, add the fields from the table
   above (Add new field → name, type, description → Confirm). Sample responses render
   on the left from your real tickets as you edit.
5. **Guidelines & Instructions** (optional but recommended): add global rules, e.g.
   *"Return null for any field not present. Never invent an ID. Normalise product
   names to the four allowed values."*
6. Iterate: review the auto-generated sample responses, refine field descriptions
   until they look right, click **Save and update**.

## Configuration you actually touch
- **Schema fields** — names, types, and especially **descriptions**.
- **Guidelines/Instructions** — edge-case handling, allowed value normalisation,
  null behaviour.
- Everything else (chunking, model choice, optimisation) is managed.

## Optimize & evaluate
- Click **Optimize** — Agent Bricks runs evaluation and optimisation in the
  background (built on **MLflow + Agent Evaluation**) to improve quality and cost.
- For a measured score, provide a small **ground-truth** sample (a column of expected
  JSON on ~20–50 hand-checked tickets). Agent Bricks compares extractions against it
  and reports the cost-quality tradeoff so you can choose the right point.
- `evaluation_questions.json` in this folder is written for a Q&A-style agent; for IE
  you instead supply labelled examples — see the note at the end of this file.

## Deployment
- Click **Use** → deploy as a **serverless endpoint** in one click. No
  `deploy_agent.py` needed on this path (that script is only for the code-based
  Mosaic AI agent).
- Run it **at scale** from SQL with `ai_query()`:

```sql
-- Extract structured fields for every ticket into a new table
CREATE OR REPLACE TABLE banking_ai.core.support_tickets_structured AS
SELECT
  ticket_id,
  customer_id,
  ai_query(
    'novabank-ticket-extraction',      -- the deployed IE endpoint
    issue_description
  ) AS extracted
FROM banking_ai.core.support_tickets;
```

You now have a governed, structured table you can join back to customers,
transactions, and cards.

## Monitoring
- **Traces & monitoring** are built in — every extraction request is logged and
  governed in the lakehouse. Watch latency, cost per document, and low-confidence
  extractions, then tighten field descriptions or guidelines and re-optimise.

