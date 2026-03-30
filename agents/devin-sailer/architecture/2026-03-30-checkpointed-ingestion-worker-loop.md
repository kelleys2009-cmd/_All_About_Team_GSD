# Checkpointed Ingestion Worker Loop
Date: 2026-03-30
Author: Devin Sailer

## Summary
Built a checkpoint-aware ingestion worker orchestration module for daemon market-data jobs. The worker now supports bounded source pulls, idempotent persistence with automatic checkpoint advancement, and exponential retry backoff so live ingestion can recover cleanly from intermittent venue or network failures.

## Implementation details
Implemented in `code/market_data/ingestion_worker.py` and exported through `code/market_data/__init__.py`.

Design choices:
- Added `IngestionWorkerConfig` for stream key, batch size, idle sleep, and retry backoff bounds.
- Added `CheckpointedIngestionWorker.run_once()`:
  - reads stream checkpoint from raw store
  - fetches bounded batch from source via injected callback
  - persists events and advances checkpoint via `append_and_advance_checkpoint`
  - sleeps on idle polls
  - applies exponential backoff on errors (capped by `max_backoff_seconds`)
- Kept sleep function injectable for deterministic tests.

Validation:
- Added `code/tests/test_ingestion_worker.py` covering:
  - successful persist + checkpoint advance
  - idle behavior sleep
  - bounded exponential backoff under repeated failures
- Full suite run:
  - `PYTHONPATH=. python3 -m unittest tests/test_ingestion_worker.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py`
  - Result: `Ran 14 tests ... OK`

## Usage
Example invocation pattern:
- Construct a store (`SqliteRawEventStore` or `PostgresRawEventStore`).
- Provide `fetch_events(checkpoint, limit)` callback for venue/API pulls.
- Instantiate `CheckpointedIngestionWorker` and call `run_once()` in scheduler loop.

Command to run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_ingestion_worker.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py
```

## Known limitations or TODOs
- `run_once()` intentionally processes one poll iteration only; caller controls lifecycle and scheduling policy.
- No built-in metrics/logging emitters yet; add structured telemetry hooks in next increment.
- No live Postgres integration test harness yet; currently unit-level coverage only.
