-- ============================================================================
-- create_tables.sql
-- Six Delta tables in banking_ai.core. Column names match the data generators
-- in data_generation/ exactly.
--
-- REQUIRED PERMISSIONS: USE CATALOG banking_ai, USE SCHEMA core, CREATE TABLE.
-- EXPECTED OUTPUT:      6 empty Delta tables. Data is loaded separately by
--                       data_generation/load_sample_data.py (notebook 02).
-- NOTE:                 We define tables explicitly (rather than letting the
--                       loader infer schema) so types are stable for the UC
--                       functions and for anyone reading the DDL.
-- ============================================================================

USE CATALOG banking_ai;
USE SCHEMA core;

-- ---------- Customers ----------
CREATE TABLE IF NOT EXISTS customers (
  customer_id     STRING   COMMENT 'Primary key, e.g. CUST000001',
  customer_name   STRING,
  email           STRING,
  city            STRING,
  state           STRING,
  risk_category   STRING   COMMENT 'LOW | MEDIUM | HIGH',
  customer_since  DATE
)
USING DELTA
COMMENT 'Synthetic bank customers. No real PII.';

-- ---------- Accounts (checking / savings) ----------
CREATE TABLE IF NOT EXISTS accounts (
  account_id        STRING  COMMENT 'Primary key, e.g. ACC0000001',
  customer_id       STRING  COMMENT 'FK -> customers.customer_id',
  account_type      STRING  COMMENT 'CHECKING | SAVINGS',
  account_status    STRING  COMMENT 'ACTIVE | DORMANT | FROZEN | CLOSED',
  current_balance   DECIMAL(12,2),
  available_balance DECIMAL(12,2),
  opened_date       DATE
)
USING DELTA
COMMENT 'Checking/savings accounts.';

-- ---------- Deposit accounts (fixed / recurring) ----------
CREATE TABLE IF NOT EXISTS deposit_accounts (
  deposit_id      STRING  COMMENT 'Primary key, e.g. DEP0000001',
  customer_id     STRING  COMMENT 'FK -> customers.customer_id',
  deposit_type    STRING  COMMENT 'FIXED | RECURRING',
  principal_amount DECIMAL(12,2),
  interest_rate   DECIMAL(5,2) COMMENT 'Annual %',
  term_months     INT,
  maturity_date   DATE,
  deposit_status  STRING  COMMENT 'ACTIVE | MATURED | CLOSED',
  opened_date     DATE
)
USING DELTA
COMMENT 'Fixed and recurring deposit accounts.';

-- ---------- Credit card accounts ----------
CREATE TABLE IF NOT EXISTS credit_card_accounts (
  card_id              STRING  COMMENT 'Primary key, e.g. CARD000001',
  customer_id          STRING  COMMENT 'FK -> customers.customer_id',
  card_type            STRING  COMMENT 'VISA | MASTERCARD | AMEX | RUPAY',
  credit_limit         DECIMAL(12,2),
  outstanding_balance  DECIMAL(12,2),
  available_credit     DECIMAL(12,2) COMMENT 'credit_limit - outstanding_balance',
  utilization_percentage DECIMAL(5,2) COMMENT 'outstanding / limit * 100',
  card_status          STRING  COMMENT 'ACTIVE | BLOCKED | EXPIRED',
  payment_due_date     DATE
)
USING DELTA
COMMENT 'Credit card accounts with utilization precomputed for convenience.';

-- ---------- Transactions ----------
CREATE TABLE IF NOT EXISTS transactions (
  transaction_id        STRING  COMMENT 'Primary key, e.g. TXN00000001',
  account_id            STRING  COMMENT 'FK -> accounts.account_id OR credit_card_accounts.card_id',
  transaction_type      STRING  COMMENT 'PURCHASE | WITHDRAWAL | DEPOSIT | TRANSFER | PAYMENT',
  merchant_name         STRING,
  transaction_amount    DECIMAL(12,2),
  transaction_status    STRING  COMMENT 'APPROVED | DECLINED | PENDING',
  transaction_timestamp TIMESTAMP,
  decline_reason        STRING  COMMENT 'NULL unless status = DECLINED'
)
USING DELTA
COMMENT '5,000+ synthetic transactions including declines with reasons.';

-- ---------- Support tickets ----------
CREATE TABLE IF NOT EXISTS support_tickets (
  ticket_id         STRING  COMMENT 'Primary key, e.g. TKT000001',
  customer_id       STRING  COMMENT 'FK -> customers.customer_id',
  issue_type        STRING  COMMENT 'CARD_DECLINED | FRAUD | LOGIN | DISPUTE | LOAN | GENERAL',
  issue_description STRING,
  ticket_status     STRING  COMMENT 'OPEN | IN_PROGRESS | RESOLVED | CLOSED',
  created_timestamp TIMESTAMP
)
USING DELTA
COMMENT 'Customer service requests. Also used as the knowledge source for Agent Bricks.';

-- Quick check:
-- SHOW TABLES IN banking_ai.core;
