# Ingestion Checkpoint Resume Behavior
Date: 2026-03-30
Author: Devin Sailer

## Summary
Implemented checkpoint auto-advance and bounded replay resume behavior for market data ingestion workers so daemonized jobs can resume deterministically after restarts without reprocessing already acknowledged events. This closes the next reliability slice for TEA-46 by making replay cursor handling explicit and test-covered.

## Implementation details
Changes were made in `code/market_data/raw_store.py` and validated in `code/tests/test_raw_store.py`.

Key design choices:
- Added `replay_after_checkpoint(...)` to both `SqliteRawEventStore` and `PostgresRawEventStore`.
  - Reads current stream checkpoint.
  - Replays strictly after `(last_event_time_ms, last_ingest_seq)` lexicographic cursor.
  - Supports `max_events` to bound replay window for long catch-up scenarios.
- Added `append_and_advance_checkpoint(events=...)` to both store types.
  - Persists batch with idempotent append semantics.
  - Computes latest event cursor from batch.
  - Upserts checkpoint in the same store so workers auto-advance progress without separate caller bookkeeping.
- Added single-stream validation for auto-advance helper.
  - Raises `ValueError` if a batch mixes `(venue, symbol, timeframe)` keys.

Dependencies:
- Python stdlib only for SQLite path.
- Postgres path continues to require `psycopg` in runtime environments.

## Usage
Run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py
```

Worker resume flow:
- Call `replay_after_checkpoint(venue=..., symbol=..., timeframe=..., max_events=...)` to pull next replay window.
- Process events.
- Call `append_and_advance_checkpoint(events=batch)` on successfully acknowledged batches.

## Known limitations or TODOs
- Checkpoint update is not wrapped in explicit multi-step transaction with downstream side effects; caller still controls exactly-once guarantees across external sinks.
- No jitter/backoff orchestration is included here; worker loop scheduling remains outside the store module.
- Future increment: add integration test against a real Postgres/Timescale instance in CI.
