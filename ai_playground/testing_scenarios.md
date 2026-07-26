# AI Playground — Testing Scenarios

Run these in order. Each lists the prompt, which tool(s) the model *should* pick,
and what a good answer looks like. Uses the canonical demo customer
**CUST000481** (card **CARD000206**, declined txn **TXN00000010**).

> Tip: after each answer, expand the trace to confirm the model called the tool
> you expected with the right arguments.

---

### 1. Single-tool: balance lookup
**Prompt:** `What is the balance on CUST000481's accounts?`
**Expected tool:** `get_customer_balance('CUST000481')`
**Good answer:** lists each account with current + available balance, from the tool
result (no invented numbers).

### 2. Single-tool: credit utilization
**Prompt:** `What is CUST000481's credit card utilization and available credit?`
**Expected tool:** `calculate_credit_utilization('CUST000481')`
**Good answer:** utilization ≈ 86.9%, available credit ≈ ₹39,263.08 for CARD000206.

### 3. Single-tool: why declined
**Prompt:** `Why was transaction TXN00000010 declined?`
**Expected tool:** `check_transaction_status('TXN00000010')`
**Good answer:** explains `INSUFFICIENT_CREDIT_LIMIT` in plain English + a next step.

### 4. ⭐ Multi-tool: the flagship question
**Prompt:**
`For customer CUST000481: why was transaction TXN00000010 declined, and what is my available credit?`
**Expected tools (chained):**
`check_transaction_status('TXN00000010')` **then** `calculate_credit_utilization('CUST000481')`
**Good answer:** one paragraph combining the decline reason (near credit limit) and
the available credit figure, ending with "make a payment or request a limit increase."
This is the scenario to screenshot for the video — it proves multi-tool reasoning.

### 5. Recent activity
**Prompt:** `Show the last 5 transactions on card CARD000206.`
**Expected tool:** `get_recent_transactions('CARD000206', 5)`
**Good answer:** table of 5 newest transactions, flagging any declines.

### 6. Policy / external info (MCP)
**Prompt:** `In general, what causes a credit card transaction to be declined?`
**Expected tool:** `external_banking_info('credit card decline reasons')` (custom MCP)
**Good answer:** general explanation from the reference source — NOT a data lookup,
because no specific customer is named.

### 7. Support history (MCP)
**Prompt:** `Has CUST000481 raised any support tickets recently?`
**Expected tool:** `support_tickets('CUST000481')` (custom MCP)
**Good answer:** summarises the 2 tickets on file.

### 8. Guardrail check — missing identifier
**Prompt:** `What's my available credit?`
**Expected behaviour:** the model should **ask for the customer or card ID** rather
than calling a tool with a made-up value. If it hallucinates an ID, tighten rule #3
in the system prompt.

### 9. Model comparison
Re-run scenario #4 with a different model (e.g. swap Claude ↔ Llama). Compare:
tool-selection accuracy, whether it chains both tools, latency, and answer clarity.
This is exactly what Playground is *for* — quick, side-by-side experimentation
before you commit to a model in code.

---

## What "good" looks like across the board
- Correct tool chosen for the question.
- Arguments filled from the conversation (no invented IDs).
- Figures in the answer match the tool result exactly.
- Declines end with a practical next step.
- General questions use the MCP info tool, not the per-customer data tools.
