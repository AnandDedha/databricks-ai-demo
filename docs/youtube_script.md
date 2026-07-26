# YouTube Script — Build AI Agents in Databricks (3 Ways)

> Format: spoken narration + `[ON SCREEN: ...]` directions. Rough runtime ~28–34
> min. Demo identifiers are stable: **customer CUST000481**, **card CARD000206**
> (86.9% utilized, ₹39,263.08 available), **declined transaction TXN00000010**
> (`INSUFFICIENT_CREDIT_LIMIT`).

---

## Video title (pick one)
- **"3 Ways to Build AI Agents in Databricks (Banking Project, Beginner-Friendly)"**
- "Databricks AI Agents for Beginners: Playground vs Agent Bricks vs Mosaic AI"
- "I Built the Same Banking AI Agent 3 Ways in Databricks — Here's Which to Use"

## Thumbnail text
- Main: **AI AGENTS in DATABRICKS**
- Sub sticker: **3 WAYS** · **BANKING PROJECT**
- Small: *Playground · Agent Bricks · Mosaic AI*

---

## 0:00 — Cold open / hook
[ON SCREEN: the flagship question typed into a chat box, agent answering live.]

"Watch this. I ask an AI agent: *'Why was my credit card transaction declined, and
what's my available credit?'* — and it figures out which of my banking tables to
look in, checks the transaction, checks the card, and gives me one clean answer with
the next step. No hard-coded logic. In this video I'll build this exact agent **three
different ways** in Databricks — AI Playground, Agent Bricks, and the Mosaic AI Agent
Framework — using one realistic banking dataset. By the end you'll know exactly which
one to reach for and when. Everything is on GitHub, link in the description. Let's go."

[ON SCREEN: channel intro sting — keep it under 3 seconds.]

## 0:35 — Introduction
"Quick context. 'Agents' just means: a language model that can **call tools** —
functions that fetch real data or take actions — reason over the results, and loop
until it can answer. The model doesn't memorise your data; it *calls a tool* to get
it. Databricks gives us three ways to build that, from zero-code to full-code, and
they all share the same governed data and tools underneath. That's the key insight of
this whole video: you build the **tools once**, then choose how much control you want
over the agent around them."

[ON SCREEN: the architecture diagram from docs/architecture.md.]

## 1:20 — Learning objectives
[ON SCREEN: bullet list building in.]
"Here's what you'll be able to do after this video:
1. Set up a governed banking dataset in Unity Catalog — completely synthetic.
2. Turn SQL into **agent tools** using Unity Catalog functions.
3. Understand **MCP** — the Model Context Protocol — and use both Databricks'
   managed MCP servers and a custom one.
4. Build and test an agent in **AI Playground** with tool calling.
5. Build a low-code agent with **Agent Bricks**.
6. Build a fully custom, production-ready agent with the **Mosaic AI Agent
   Framework**, then evaluate and deploy it.
7. And most importantly — know **when to use which**."

## 2:10 — Banking use-case overview
[ON SCREEN: the six tables with row counts.]
"We're running a fictional bank called NovaBank. Six datasets, all synthetic:
customers, accounts, deposit accounts, credit card accounts, transactions — 5,000 of
them, including declines with reasons — and support tickets. I generated these with
Python and Faker; no real personal or financial data anywhere. Our star customer for
the demo is CUST000481: their card is 87% maxed out, and one of their transactions,
TXN00000010, got declined for insufficient credit limit. That one customer lets us
tell the whole story."

## 3:00 — Architecture explanation
[ON SCREEN: architecture diagram, highlight each layer as you say it.]
"Four layers. At the bottom, **Delta tables** governed by **Unity Catalog** — that's
our security boundary. Above that, **tools**: I wrap SQL queries as Unity Catalog
functions, and I expose extra capabilities through **MCP servers**. Above that, the
**agent** — built one of our three ways. And around all of it, the **lifecycle**:
MLflow for tracing and evaluation, Model Serving for deployment. The beautiful part:
switch the agent builder, keep the same tools and data. Let me show you the setup, then
we'll build all three."

## 3:45 — DEMO 1: Environment + data (fast)
[ON SCREEN: notebook 01 running.]
"Notebook one creates the catalog, two schemas — `core` for data, `tools` for
functions — and the six tables. Notebook two generates and loads the data. I'll speed
this up… and there we go: 500 customers, 700 accounts, 5,000 transactions. Let me prove
the demo scenario is real —"
[ON SCREEN: the join query on TXN00000010 returning the decline reason + available credit.]
"— declined, insufficient credit limit, available credit ₹39,263. Perfect."

## 4:40 — DEMO 2: Unity Catalog functions = tools
[ON SCREEN: notebook 03, open get_customer_balance.sql.]
"Now the tools. This is a normal SQL function — but look at the **COMMENT**. This
isn't decoration; the LLM *reads* this description to decide when to call the tool.
Write it for the model. I've got four: get customer balance, calculate credit
utilization, get recent transactions, and check transaction status — which even
returns a plain-English explanation of *why* a transaction was declined."
[ON SCREEN: run the four smoke tests, especially check_transaction_status('TXN00000010').]
"And here's the magic: the moment these exist, Databricks exposes them as a **managed
MCP server** — this URL — with zero extra work. That's our tool layer done. One set of
tools, and now we'll plug it into all three agent builders."

## 6:00 — What is MCP? (60-second explainer)
[ON SCREEN: simple MCP diagram — client ↔ server ↔ tools.]
"Thirty-second version: **MCP** is like a USB-C port for AI tools. A standard way for
an agent to discover and call tools, no matter who built them. Databricks gives you
**managed** MCP servers for Unity Catalog functions, Genie, AI Search, and SQL —
hosted, governed, nothing to run. And when a tool needs something *outside* the
lakehouse — a partner API, custom Python — you write a **custom** MCP server. I built a
tiny one for support tickets and external banking info; it's in the repo."

## 7:00 — ⭐ APPROACH 1: AI Playground
[ON SCREEN: Playground UI.]
"Approach one: **AI Playground**. This is where you experiment. I pick a tool-calling
model, click Tools, and add my four Unity Catalog functions. Then I paste a system
prompt telling it to never guess numbers and to chain tools when needed."
[ON SCREEN: paste system prompt; type scenario #2.]
"Simple question first: what's CUST000481's utilization and available credit? Watch —
it calls `calculate_credit_utilization`, gets the row, answers 86.9%, ₹39,263. Now the
flagship —"
[ON SCREEN: type scenario #4, expand the trace.]
"'Why was TXN00000010 declined, and what's my available credit?' Look at the trace: it
calls `check_transaction_status`, sees insufficient credit limit, then calls
`calculate_credit_utilization`, then combines both into one answer with a next step.
**Two tools, chained, automatically.** That's the model reasoning about which tools it
needs. And because it's Playground, I can swap the model and re-run to compare — that's
what Playground is *for*: fast prompt, tool, and model experiments. What it's *not* for
is production. So let's level up."

[ON SCREEN: lower-third — "AI Playground → experiment, compare, prototype."]

## 11:00 — ⭐ APPROACH 2: Agent Bricks
[ON SCREEN: Agent Bricks pattern gallery.]
"Approach two: **Agent Bricks** — low-code agents from predefined patterns. There's
Knowledge Assistant, Information Extraction, Multi-Agent Supervisor, and Custom LLM. For
a support assistant grounded in our ticket history and policies, **Knowledge Assistant**
is the perfect fit — and it went GA earlier this year."
[ON SCREEN: create Knowledge Assistant, add knowledge sources, paste instructions.]
"I point it at my policy notes and ticket descriptions as knowledge sources, paste
instructions — including an important rule: for *live* per-customer balances, hand off,
because a knowledge assistant is for grounded knowledge, not live lookups. Click Create.
Databricks does the chunking, embedding, and retrieval for me — no RAG code."
[ON SCREEN: Evaluate tab, upload evaluation_questions.json.]
"Then I evaluate. I upload my questions, and Agent Bricks runs an AI judge and scores
quality on the **CLEARS** rubric — Correctness, Latency, Execution, Adherence,
Relevance, Safety. One click to **Deploy**, and I get a serving endpoint *and* a chat
app, with monitoring built in. From nothing to a governed, evaluated, deployed agent in
minutes. The trade-off: you're inside a pattern. When you need custom logic, you go to
code."

[ON SCREEN: lower-third — "Agent Bricks → fast, governed, pattern-based."]

## 16:30 — ⭐ APPROACH 3: Mosaic AI Agent Framework
[ON SCREEN: mosaic_ai_agent/ files in the editor.]
"Approach three: full control, in code — the **Mosaic AI Agent Framework**. Databricks
recommends building on MLflow's **`ResponsesAgent`** interface, because wrapping your
agent in it gives you Playground compatibility, evaluation, tracing, and deployment for
free. Let me walk the code."

### Code walkthrough
[ON SCREEN: model_config.py.]
"`model_config.py` — one place for every setting: catalog, the LLM endpoint, the
managed MCP path, the system prompt, and a safety cap on tool iterations."

[ON SCREEN: tools.py.]
"`tools.py` is the bridge. It connects to the managed MCP server, lists the tools,
converts each into the format the LLM understands, and gives us a `call()` method that
routes the model's tool calls back through MCP. Notice `get_databricks_resources()` —
that's how the deployed agent gets *exactly* the permissions it needs, nothing more."

[ON SCREEN: agent.py, highlight the loop.]
"`agent.py` is the agent itself. The `predict` method does five things: takes the
messages, sends them to the LLM with the tool list, and if the model asks for a tool, we
run it, feed the result back, and loop — up to our cap. When the model stops asking for
tools, we return its answer **plus a list of the tools it used**, so the whole thing is
transparent. The `@mlflow.trace` decorator means every step shows up in the trace UI."

[ON SCREEN: run notebook 05 on the flagship question.]
"Let's run it. Same flagship question… it chains the two tools, and here's the answer:
the transaction was declined for insufficient credit limit because the card is 87%
utilized, available credit is ₹39,263, and — make a payment or request a limit increase.
Plus the structured 'tools used' list. Now let me ask without an ID — 'what's my
available credit?' — and notice it *asks who I am* instead of hallucinating. That's the
system prompt doing its job."

## 24:00 — Evaluate & deploy the code agent
[ON SCREEN: notebook 06, evaluate_agent.py running.]
"Before shipping, I evaluate — Correctness, Relevance, Safety, and a custom guideline
scorer that checks it never invents numbers and always gives a next step. Then deploy:
`deploy_agent.py` logs the agent to MLflow with its resources, registers it in Unity
Catalog, and calls `agents.deploy`. A few minutes later I've got a serving endpoint and
a review app — same destination as Agent Bricks, but I controlled every line."

[ON SCREEN: query the deployed endpoint, response prints.]
"And there it is, answering over a live REST endpoint."

[ON SCREEN: lower-third — "Mosaic AI Agent Framework → full control, production."]

## 26:00 — Comparison of all three
[ON SCREEN: the comparison table.]

| Option | Best suited for |
|--------|-----------------|
| **AI Playground** | Prompt testing, model comparison, and quick tool experiments |
| **Agent Bricks** | Low-code agent development using predefined patterns |
| **Mosaic AI Agent Framework** | Fully customizable, code-based production agents |

"So which do you use? They're not rivals — they're a **pipeline**. Prototype in
**Playground**. If a pattern fits, ship fast with **Agent Bricks**. When you outgrow the
pattern, rebuild in the **Agent Framework** — reusing the exact same tools. You never
rewrite the tools, only the agent around them. That's the payoff of building tools as
Unity Catalog functions and MCP servers."

## 28:00 — Best-practice recommendations
[ON SCREEN: checklist.]
"Five things I'd tattoo on every agent project:
1. **Write tool descriptions for the model.** The COMMENT is the interface — vague
   comments cause wrong tool calls.
2. **Let Unity Catalog do security.** Tools inherit governance; grant least privilege,
   especially to the deployed agent's service principal.
3. **Always evaluate before you deploy.** Even 20 good questions catch real bugs.
4. **Read the traces.** They show you exactly which tool ran with which arguments —
   your best debugging tool.
5. **Tear down serving endpoints** you're not using, so you don't pay for idle agents."

## 29:30 — Common errors & troubleshooting
[ON SCREEN: three quick fixes.]
"Three you'll almost certainly hit:
- **The model ignores a tool** → the description is too vague. Make it say *when* to use
  the tool.
- **`PERMISSION_DENIED` on a tool call** → Unity Catalog needs `EXECUTE` on the function
  and `SELECT` on the table — for *you* in Playground, and for the *service principal*
  once deployed.
- **Works in the notebook, fails once deployed** → a missing resource or grant for that
  service principal. Full list is in `docs/troubleshooting.md`."

## 30:30 — Conclusion
"That's three ways to build the same banking agent in Databricks — Playground for
experiments, Agent Bricks for fast pattern-based agents, and the Mosaic AI Agent
Framework for full-control production agents — all on one governed dataset and one set of
tools. Start simple, level up only when you need to."

## 31:00 — Call to action
"Everything — the data generators, the SQL, the MCP server, and all three agents — is in
the GitHub repo linked below; clone it and you can rebuild this in your own workspace in
about twenty minutes. If this helped, hit **like**, **subscribe** for more Databricks and
AI-engineering builds, and tell me in the comments: which of the three would you use for
*your* use case? Thanks for watching — see you in the next one."

[ON SCREEN: end card — subscribe + next video + GitHub link.]

---

## Recording checklist
- [ ] Pre-run notebooks 01–04 so demos are instant on camera.
- [ ] Have the Playground trace expanded and readable (zoom the UI).
- [ ] Deploy the agent *before* recording section 24:00 (deployment is slow) and just
      show the query live.
- [ ] Keep the architecture diagram on a pinned tab for quick cutaways.
- [ ] Blur/hide your real workspace URL if you don't want it public.
