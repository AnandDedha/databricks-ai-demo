-- ============================================================================
-- create_schemas.sql
-- Two schemas:
--   banking_ai.core   -> source Delta tables (customers, accounts, ...)
--   banking_ai.tools  -> Unity Catalog functions the agent calls as tools
--
-- Keeping functions in their own schema gives us a clean managed-MCP URL:
--   https://<workspace-host>/api/2.0/mcp/functions/banking_ai/tools
--
-- REQUIRED PERMISSIONS: USE CATALOG + CREATE SCHEMA on `banking_ai`.
-- EXPECTED OUTPUT:      Both schemas exist.
-- ============================================================================

USE CATALOG banking_ai;

CREATE SCHEMA IF NOT EXISTS core
  COMMENT 'Synthetic source tables: customers, accounts, deposits, cards, transactions, tickets.';

CREATE SCHEMA IF NOT EXISTS tools
  COMMENT 'Unity Catalog functions exposed to agents as governed tools.';

-- SHOW SCHEMAS IN banking_ai;
