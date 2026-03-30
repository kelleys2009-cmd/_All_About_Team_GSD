# Ingestion SLO Alert Evaluator
Date: 2026-03-30
Author: Devin Sailer

## Summary
Implemented a threshold-based ingestion SLO alert evaluator for checkpoint lag, retry spikes, and prolonged idle behavior. This provides a deterministic control layer to convert worker observability metrics into actionable incident signals.

## Implementation details
Files changed:
- `code/market_data/ingestion_alerts.py`
- `code/tests/test_ingestion_alerts.py`
- `code/market_data/__init__.py`
- `code/README.md`

Design choices:
- Added immutable dataclasses for configuration and runtime observations:
  - `IngestionSLOConfig`
  - `IngestionObservation`
  - `IngestionAlert`
- Added `evaluate_ingestion_slo(observation, config)` that emits alerts with fixed severities:
  - `ingestion_checkpoint_lag` -> `critical`
  - `ingestion_retry_spike` -> `high`
  - `ingestion_idle_stall` -> `medium`
- Kept evaluator pure and side-effect free so routing/escalation remains external.

Validation:
- Added tests for no-alert and multi-breach scenarios.
- Full unit run:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_ingestion_alerts.py tests/test_ingestion_worker.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py`
  - Result: `Ran 16 tests ... OK`

## Usage
Example run path:
- Feed worker metrics/derived counters into `IngestionObservation`.
- Apply `evaluate_ingestion_slo(...)` with agreed thresholds.
- Route returned alerts to logging, pager, or incident tooling.

Test command:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_ingestion_alerts.py
```

## Known limitations or TODOs
- Current evaluator uses static thresholds; dynamic/adaptive thresholds are not included.
- No built-in de-dup/suppression windows yet for repeated alerts.
- Next increment should map alert types to explicit escalation policies and notification channels.
