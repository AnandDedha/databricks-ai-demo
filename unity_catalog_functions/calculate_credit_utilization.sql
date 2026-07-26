-- ============================================================================
-- calculate_credit_utilization
-- Agent tool: for a customer's credit card(s), return the limit, outstanding,
-- available credit and utilization %. Utilization is recomputed here from limit
-- and outstanding so the answer is always correct even if the stored column is
-- stale. This is the tool that answers the "...and what is my available credit?"
-- half of the flagship question.
--
-- TEST:
--   SELECT * FROM banking_ai.tools.calculate_credit_utilization('CUST000001');
-- EXPECTED OUTPUT: one row per active credit card for that customer.
-- ============================================================================

CREATE OR REPLACE FUNCTION banking_ai.tools.calculate_credit_utilization(
  input_customer_id STRING COMMENT 'Customer identifier in the form CUST000001.'
)
RETURNS TABLE (
  card_id                STRING,
  card_type              STRING,
  card_status            STRING,
  credit_limit           DECIMAL(12,2),
  outstanding_balance    DECIMAL(12,2),
  available_credit       DECIMAL(12,2),
  utilization_percentage DECIMAL(6,2)
)
COMMENT 'Returns credit card limit, outstanding balance, available credit and utilization percentage for a customer. Use this when the customer asks about their credit card, credit limit, available credit, or how much of their card they have used.'
RETURN
  SELECT
    card_id,
    card_type,
    card_status,
    credit_limit,
    outstanding_balance,
    -- Recompute rather than trust the stored column.
    ROUND(credit_limit - outstanding_balance, 2)              AS available_credit,
    ROUND(outstanding_balance / NULLIF(credit_limit, 0) * 100, 2) AS utilization_percentage
  FROM banking_ai.core.credit_card_accounts
  WHERE customer_id = input_customer_id;
