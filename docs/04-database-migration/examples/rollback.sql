-- Per-phase rollback scripts (run the section for the phase that failed)

-- EXPAND rollback (safe, nothing depends on the new objects yet)
SET lock_timeout = '3s';
DROP INDEX CONCURRENTLY IF EXISTS idx_customer_email_hash;     -- cannot run inside a transaction block
ALTER TABLE customer_profiles DROP COLUMN IF EXISTS email_hash;
ALTER TABLE customer_profiles DROP COLUMN IF EXISTS encrypted_email;

-- MIGRATE rollback (stop the job first; plaintext email is untouched, so it is safe to discard the new data)
-- Batched so the undo is also throttled:
--   UPDATE customer_profiles SET encrypted_email = NULL
--    WHERE id > :last AND id <= :last + 5000 AND encrypted_email IS NOT NULL;   -- loop with COMMIT

-- APP rollback: redeploy the previous image digest (Deliverable 6). Schema needs no change: S1/S2 work with V(N-1) and V(N).

-- CONTRACT rollback: only possible before the DROP -> ALTER TABLE customer_profiles RENAME COLUMN email_deprecated TO email;
-- After the DROP: restore from backup / point-in-time recovery (this is why the DROP is a separate approved deployment).
