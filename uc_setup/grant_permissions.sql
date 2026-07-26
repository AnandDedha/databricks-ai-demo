-- ============================================================================
-- grant_permissions.sql
-- Grants so that (a) your team can use the data and (b) the AGENT can call the
-- tools. Unity Catalog enforces these permissions on every tool call — this is
-- the whole point of building tools as UC functions.
--
-- REPLACE the principals below with your own users / groups before running.
--   `account users`  -> a built-in group meaning "everyone"; fine for a demo,
--                       tighten for anything real.
--
-- REQUIRED PERMISSIONS: you must be an owner of the catalog/schemas, or admin.
-- EXPECTED OUTPUT:      grants applied; SHOW GRANTS returns the new rows.
-- ============================================================================

-- ---- Let people read the data ----
GRANT USE CATALOG ON CATALOG banking_ai TO `account users`;
GRANT USE SCHEMA  ON SCHEMA  banking_ai.core  TO `account users`;
GRANT SELECT      ON SCHEMA  banking_ai.core  TO `account users`;

-- ---- Let people (and agents) discover + run the tools ----
GRANT USE SCHEMA      ON SCHEMA banking_ai.tools TO `account users`;
GRANT EXECUTE         ON SCHEMA banking_ai.tools TO `account users`;

-- ---- When you deploy a Model Serving agent, it runs under a service principal.
-- Grant that principal the minimum it needs. Replace the UUID/appId below.
-- (You can find it after deployment under Serving -> your endpoint -> Permissions.)
--
-- GRANT USE CATALOG ON CATALOG banking_ai                TO `<agent-service-principal>`;
-- GRANT USE SCHEMA, SELECT ON SCHEMA banking_ai.core     TO `<agent-service-principal>`;
-- GRANT USE SCHEMA, EXECUTE ON SCHEMA banking_ai.tools   TO `<agent-service-principal>`;

-- Verify:
-- SHOW GRANTS ON SCHEMA banking_ai.tools;
