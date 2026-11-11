-- EXPAND phase (backward compatible): add encrypted_email beside email.
-- App V(N-1) never references the new column, so it keeps working.
-- Flyway: must run OUTSIDE a transaction (CREATE INDEX CONCURRENTLY) -> see V2.0__expand_add_encrypted_email.sql.conf

-- Fail fast instead of queueing behind a long query and blocking every other session
SET lock_timeout = '3s';
SET statement_timeout = '5min';

-- Nullable column with no default = metadata-only change in PostgreSQL (no table rewrite)
ALTER TABLE customer_profiles
  ADD COLUMN IF NOT EXISTS encrypted_email BYTEA;

-- Blind index for equality lookups. NOTE: pgp_sym_encrypt() is non-deterministic (random salt),
-- so an index on encrypted_email itself can never serve an equality lookup.
ALTER TABLE customer_profiles
  ADD COLUMN IF NOT EXISTS email_hash BYTEA;          -- HMAC-SHA256(lower(email)) computed by the app/KMS

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customer_email_hash
  ON customer_profiles (email_hash);

-- Audit entry for RBI 6.1
INSERT INTO schema_audit_log (migration_id, description, executed_by, phase)
VALUES ('V2.0', 'Add encrypted_email, email_hash columns and index', current_user, 'EXPAND');

-- IMPORTANT: do NOT drop the old email column here. That happens in V2.2 (CONTRACT) after all services migrate.
