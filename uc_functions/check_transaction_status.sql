-- ============================================================================
-- check_transaction_status
-- Agent tool: look up a single transaction and explain its status. For declined
-- transactions it returns a human-readable explanation of the decline_reason so
-- the agent can answer "why was my transaction declined?" directly. This is the
-- first half of the flagship question.
--
-- TEST:
--   SELECT * FROM banking_ai.tools.check_transaction_status('TXN00000042');
-- EXPECTED OUTPUT: one row (or none if the ID doesn't exist).
-- ============================================================================

CREATE OR REPLACE FUNCTION banking_ai.tools.check_transaction_status(
  input_transaction_id STRING COMMENT 'Transaction identifier in the form TXN00000001.'
)
RETURNS TABLE (
  transaction_id     STRING,
  account_id         STRING,
  transaction_status STRING,
  decline_reason     STRING,
  explanation        STRING,
  transaction_amount DECIMAL(12,2),
  merchant_name      STRING
)
COMMENT 'Returns the status of a specific transaction and, if it was declined, a plain-English explanation of why. Use this when a customer references a particular transaction ID or asks why a payment failed.'
RETURN
  SELECT
    transaction_id,
    account_id,
    transaction_status,
    decline_reason,
    CASE
      WHEN transaction_status <> 'DECLINED' THEN 'Transaction was ' || lower(transaction_status) || '.'
      WHEN decline_reason = 'INSUFFICIENT_CREDIT_LIMIT' THEN 'Declined because the card had insufficient available credit. Ask the customer to make a payment or request a limit increase.'
      WHEN decline_reason = 'INSUFFICIENT_FUNDS'        THEN 'Declined because the account balance was too low to cover the amount.'
      WHEN decline_reason = 'CARD_BLOCKED'              THEN 'Declined because the card is currently blocked. Verify identity before unblocking.'
      WHEN decline_reason = 'EXPIRED_CARD'              THEN 'Declined because the card has expired. A replacement card is required.'
      WHEN decline_reason = 'SUSPECTED_FRAUD'           THEN 'Declined by fraud controls as a precaution. Verify the customer and the transaction.'
      WHEN decline_reason = 'ACCOUNT_FROZEN'            THEN 'Declined because the account is frozen. Check for holds or compliance actions.'
      WHEN decline_reason = 'DAILY_LIMIT_EXCEEDED'      THEN 'Declined because the daily transaction limit was exceeded.'
      WHEN decline_reason IN ('INCORRECT_CVV', 'INVALID_PIN') THEN 'Declined due to an incorrect security code or PIN entry.'
      WHEN decline_reason = 'MERCHANT_NOT_SUPPORTED'    THEN 'Declined because the merchant category is not supported on this card.'
      ELSE 'Declined: ' || COALESCE(decline_reason, 'reason unavailable') || '.'
    END AS explanation,
    transaction_amount,
    merchant_name
  FROM banking_ai.core.transactions
  WHERE transaction_id = input_transaction_id;
