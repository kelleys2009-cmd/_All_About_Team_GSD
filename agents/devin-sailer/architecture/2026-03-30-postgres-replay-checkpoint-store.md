# Postgres Replay Checkpoint Store Increment

- Date: 2026-03-30
- Author: Devin Sailer

## Summary
Implemented the next TEA-46 market-data persistence increment: a Postgres/Timescale runtime raw-event store path and replay checkpoint primitives. This closes the deterministic replay checkpoint gap for long-running paper/live ingestion jobs while keeping local SQLite parity for tests.

## Implementation details
- Extended `code/market_data/raw_store.py` with:
  - `ReplayCheckpoint` dataclass.
  - `timescaledb_checkpoint_schema_sql()` helper.
  - `SqliteRawEventStore.upsert_checkpoint()` and `get_checkpoint()`.
  - `PostgresRawEventStore` with schema init, idempotent appends, replay reads, and checkpoint upsert/get.
- Exported new contracts in `code/market_data/__init__.py`.
- Added tests in `code/tests/test_raw_store.py`:
  - checkpoint upsert/read/update behavior,
  - checkpoint schema SQL contract coverage.
- Updated `code/README.md` with new module capabilities.

## Usage
1. Local deterministic path:
```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_raw_store.py
```
2. Build DDL for Timescale migrations:
```python
from market_data.raw_store import timescaledb_schema_sql, timescaledb_checkpoint_schema_sql
print(timescaledb_schema_sql())
print(timescaledb_checkpoint_schema_sql())
```
3. Runtime Postgres store (requires `psycopg` installed):
```python
from market_data.raw_store import PostgresRawEventStore
store = PostgresRawEventStore(dsn="postgresql://user:pass@host:5432/db")
```

## Known limitations or TODOs
- `PostgresRawEventStore` currently expects `psycopg` availability and does not include connection pooling.
- No migration runner wiring yet; DDL is currently generated in-app.
- Replay checkpoint advancement is manual; next step is auto-commit checkpointing in ingestion loops.
