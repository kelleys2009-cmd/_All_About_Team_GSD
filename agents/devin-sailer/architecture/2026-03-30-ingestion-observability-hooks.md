# Ingestion Observability Hooks
Date: 2026-03-30
Author: Devin Sailer

## Summary
Added observability hooks to the checkpointed ingestion worker so daemonized market-data jobs can emit structured metrics and logs for checkpoint lag, fetched/inserted volume, and retry behavior. This improves operational visibility and incident triage for live ingestion reliability.

## Implementation details
Files changed:
- `code/market_data/ingestion_worker.py`
- `code/tests/test_ingestion_worker.py`
- `code/README.md`

Design choices:
- Added optional injected callbacks to `CheckpointedIngestionWorker`:
  - `metric_fn(name, value, tags)`
  - `log_fn(event, payload)`
  - `now_ms_fn()` to make checkpoint-age tests deterministic.
- Added standard metric emission points:
  - `ingestion.checkpoint_age_ms`
  - `ingestion.events_fetched`
  - `ingestion.events_inserted`
  - `ingestion.retries`
- Added structured log events:
  - `ingestion.ok`
  - `ingestion.idle`
  - `ingestion.retry`
- Kept hooks optional so existing callers remain backward-compatible.

Validation:
- Extended tests verify metrics/log calls and bounded retry behavior.
- Full suite:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_ingestion_worker.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py`
  - Result: `Ran 14 tests ... OK`

## Usage
To enable observability:
- Pass `metric_fn` and `log_fn` when constructing `CheckpointedIngestionWorker`.
- Route metrics to your telemetry backend and logs to structured log ingestion.

Example test command:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_ingestion_worker.py
```

## Known limitations or TODOs
- Metrics names are currently plain strings; central naming registry is not yet in place.
- Worker does not yet include built-in histogram bucketing or rate calculations.
- Next step: wire a concrete production sink (Prometheus/OpenTelemetry adapter) and dashboard templates.
