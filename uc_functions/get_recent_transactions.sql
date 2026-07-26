-- ============================================================================
-- get_recent_transactions
-- Agent tool: return the most recent transactions for an account OR a card.
-- Accepts a row limit so the model can ask for "the last 5" etc. Works for both
-- account_ids (ACC...) and card_ids (CARD...) because transactions.account_id
-- holds either.
--
-- TEST:
--   SELECT * FROM banking_ai.tools.get_recent_transactions('CARD000001', 5);
-- EXPECTED OUTPUT: up to `row_limit` rows, newest first.
-- ============================================================================

CREATE OR REPLACE FUNCTION banking_ai.tools.get_recent_transactions(
  input_account_id STRING COMMENT 'Account ID (ACC0000001) or credit card ID (CARD000001) to list transactions for.',
  row_limit        INT    COMMENT 'Maximum number of transactions to return, e.g. 5. Defaults sensibly if a large value is passed.'
)
RETURNS TABLE (
  transaction_id        STRING,
  transaction_type      STRING,
  merchant_name         STRING,
  transaction_amount    DECIMAL(12,2),
  transaction_status    STRING,
  decline_reason        STRING,
  transaction_timestamp TIMESTAMP
)
COMMENT 'Returns the most recent transactions (newest first) for a given account or credit card, including whether each was approved or declined. Use this when the customer asks about recent activity, a specific purchase, or a declined transaction.'
RETURN
  SELECT
    transaction_id, transaction_type, merchant_name, transaction_amount,
    transaction_status, decline_reason, transaction_timestamp
  FROM banking_ai.core.transactions
  WHERE account_id = input_account_id
  ORDER BY transaction_timestamp DESC
  LIMIT LEAST(COALESCE(row_limit, 10), 50);
