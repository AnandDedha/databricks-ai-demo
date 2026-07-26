-- ============================================================================
-- get_customer_balance
-- Agent tool: return every checking/savings account and its balances for a
-- customer. The FUNCTION-LEVEL COMMENT and PARAMETER COMMENT are what the LLM
-- reads to decide when to call this tool and how to fill the argument — write
-- them for the model, not just for humans.
--
-- REQUIRED PERMISSIONS to create: USE CATALOG banking_ai, USE SCHEMA tools,
--   CREATE FUNCTION on banking_ai.tools, SELECT on banking_ai.core.accounts.
-- REQUIRED PERMISSIONS to call (agent): EXECUTE on the function + SELECT on the
--   underlying table. Unity Catalog enforces both on every call.
--
-- TEST:
--   SELECT * FROM banking_ai.tools.get_customer_balance('CUST000001');
-- EXPECTED OUTPUT: 0+ rows, one per account owned by that customer.
-- ============================================================================

CREATE OR REPLACE FUNCTION banking_ai.tools.get_customer_balance(
  input_customer_id STRING COMMENT 'Customer identifier in the form CUST000001. Ask the user for it if unknown.'
)
RETURNS TABLE (
  account_id        STRING,
  account_type      STRING,
  account_status    STRING,
  current_balance   DECIMAL(12,2),
  available_balance DECIMAL(12,2)
)
COMMENT 'Returns the checking and savings account balances for a given customer. Use this when a customer asks about their bank balance, available funds, or account status.'
RETURN
  SELECT account_id, account_type, account_status, current_balance, available_balance
  FROM banking_ai.core.accounts
  WHERE customer_id = input_customer_id;
