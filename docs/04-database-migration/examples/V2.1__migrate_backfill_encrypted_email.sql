-- MIGRATE phase: batched, throttled, idempotent, resumable backfill.
-- Why a PROCEDURE with COMMIT: a plain DO $$ ... LOOP $$ block runs as ONE transaction, so all batches would
-- hold their row locks until the end, bloat WAL and make the throttling pointless.
-- Flyway: run outside a transaction -> V2.1__migrate_backfill_encrypted_email.sql.conf
-- The encryption key is supplied per session by the runner (from Vault): SET app.encryption_key = '...';
-- Prefer app-side/KMS encryption in production so the key never appears in SQL logs (log_statement = 'none').

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE OR REPLACE PROCEDURE backfill_encrypted_email(
    p_batch_size  INT     DEFAULT 5000,   -- rows per batch
    p_sleep_secs  NUMERIC DEFAULT 0.05,   -- throttle between batches
    p_from_id     BIGINT  DEFAULT 0       -- resume point after an abort
)
LANGUAGE plpgsql AS $$
DECLARE
    v_last_id BIGINT := p_from_id;
    v_max_id  BIGINT;
    v_rows    INT;
    v_total   BIGINT := 0;
BEGIN
    SELECT COALESCE(MAX(id), 0) INTO v_max_id FROM customer_profiles;
    WHILE v_last_id < v_max_id LOOP
        -- Primary-key range scan: each batch touches a bounded, indexed slice (no repeated "IS NULL" scans)
        UPDATE customer_profiles
           SET encrypted_email = pgp_sym_encrypt(email, current_setting('app.encryption_key'))
         WHERE id >  v_last_id
           AND id <= v_last_id + p_batch_size
           AND email IS NOT NULL
           AND encrypted_email IS NULL;            -- idempotent: re-running skips finished rows
        GET DIAGNOSTICS v_rows = ROW_COUNT;

        v_total   := v_total + v_rows;
        v_last_id := v_last_id + p_batch_size;
        COMMIT;                                     -- release locks, let WAL/replication catch up
        RAISE NOTICE 'checkpoint: last_id=% batch_rows=% total=%', v_last_id, v_rows, v_total;
        PERFORM pg_sleep(p_sleep_secs);             -- throttle (runner raises this when guards trip)
    END LOOP;
END
$$;

-- Run (outside a transaction):  CALL backfill_encrypted_email(5000, 0.05);
-- Resume after abort:           CALL backfill_encrypted_email(5000, 0.05, <last checkpoint id>);

-- Verification (also used as the gate before app V(N+1)):
--   SELECT count(*) FROM customer_profiles WHERE email IS NOT NULL AND encrypted_email IS NULL;   -- must be 0
--   Sample check: SELECT count(*) FROM (SELECT id FROM customer_profiles TABLESAMPLE SYSTEM (0.01)
--     WHERE pgp_sym_decrypt(encrypted_email, current_setting('app.encryption_key')) <> email) t;  -- must be 0
