CREATE OR REPLACE FUNCTION banking_ai.tools.get_recent_transactions(
  input_account_id STRING
    COMMENT 'Account ID (ACC0000001) or credit card ID (CARD000001) to list transactions for.',

  row_limit INT
    COMMENT 'Maximum number of transactions to return. Defaults to 10 and is capped at 50.'
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
COMMENT 'Returns the most recent transactions, newest first, for a given account or credit card. Includes approved and declined transactions.'
RETURN
  WITH ranked_transactions AS (
    SELECT
      transaction_id,
      transaction_type,
      merchant_name,
      transaction_amount,
      transaction_status,
      decline_reason,
      transaction_timestamp,

      ROW_NUMBER() OVER (
        ORDER BY transaction_timestamp DESC, transaction_id DESC
      ) AS row_num

    FROM banking_ai.core.transactions
    WHERE account_id = input_account_id
  )

  SELECT
    transaction_id,
    transaction_type,
    merchant_name,
    transaction_amount,
    transaction_status,
    decline_reason,
    transaction_timestamp

  FROM ranked_transactions
  WHERE row_num <= LEAST(
    GREATEST(COALESCE(row_limit, 10), 1),
    50
  )
  ORDER BY transaction_timestamp DESC, transaction_id DESC;
