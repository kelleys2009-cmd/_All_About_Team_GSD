# Postgres Recovery Integration Harness
Date: 2026-03-30
Author: Devin Sailer

## Summary
Added an environment-gated Postgres integration harness to validate replay checkpoint recovery behavior against a real database connection. This supports TEA-46 reliability goals by testing resume semantics beyond in-memory/unit mocks while keeping default local test runs lightweight.

## Implementation details
Files changed:
- `code/tests/integration/test_postgres_raw_store_integration.py`
- `code/README.md`

Design choices:
- Integration test is gated by `TEAM_GSD_TEST_POSTGRES_DSN` using `unittest.skipUnless`.
- Test provisions unique runtime table names per run using UUID suffixes to avoid collisions.
- Validates key recovery contracts end-to-end:
  - idempotent append into Postgres-backed raw store
  - checkpoint update/read semantics
  - `replay_after_checkpoint` resume ordering
  - `append_and_advance_checkpoint` cursor progression after restart-style replay flow
- Cleanup drops temporary integration tables in `finally` block.

Dependencies:
- Requires reachable Postgres instance and `psycopg` available in environment.

## Usage
Run unit tests (default local flow):

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_ingestion_worker.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py
```

Run Postgres integration harness:

```bash
cd code
TEAM_GSD_TEST_POSTGRES_DSN='postgresql://user:pass@localhost:5432/dbname' \
PYTHONPATH=. python3 -m unittest tests.integration.test_postgres_raw_store_integration
```

## Known limitations or TODOs
- Current harness validates functional recovery semantics but not performance under sustained high ingest load.
- Does not yet assert Timescale-specific hypertable policies or compression behavior.
- Next step: wire this integration harness into CI with ephemeral Postgres service and alert on regression.
