-- ============================================================================
-- create_catalog.sql
-- Creates the Unity Catalog container for the banking AI agents demo.
--
-- REQUIRED PERMISSIONS: CREATE CATALOG on the metastore (metastore admin), OR
--                       ask your admin to create `banking_ai` and grant you
--                       ALL PRIVILEGES on it, then skip this file.
-- RUN ON:               A SQL warehouse or serverless notebook.
-- EXPECTED OUTPUT:      Catalog `banking_ai` exists and is selectable.
-- ============================================================================

-- Idempotent: safe to re-run.
CREATE CATALOG IF NOT EXISTS banking_ai
  COMMENT 'Synthetic banking data + AI agent tools for the Databricks agents tutorial. NO real PII.';

-- Verify (should return one row).
-- SHOW CATALOGS LIKE 'banking_ai';
