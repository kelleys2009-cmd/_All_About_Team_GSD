# Notifier State Connectivity Probe

Date: 2026-03-31
Author: Devin Sailer

## Summary

Added a runtime connectivity probe helper for notifier SLO state stores so support workflows can quickly confirm SQLite/Redis backend reachability without mutating state.

## Implementation details

- Added `NotifierSLOStateStoreProbeResult` dataclass in `code/market_data/notifier_slo_state_store.py`.
- Added `probe_notifier_slo_state_store_connectivity(store)`:
  - SQLite: executes `SELECT 1`
  - Redis: calls `ping()` when available; otherwise falls back to state read
  - returns structured backend/ok/detail payload instead of raising to callers
- Added tests in `code/tests/test_notifier_slo_state_store.py` for:
  - SQLite success
  - Redis success
  - Redis failure path with structured error detail
- Exported APIs through `market_data.__init__`.
- Updated shared docs in `code/README.md`.

## Usage

Run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py tests/test_notifier_slo_policy.py tests/test_alert_notifiers.py tests/test_ingestion_worker.py tests/test_ingestion_alerts.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py tests.integration.test_redis_notifier_slo_state_store_integration
```

Example:

```python
probe = probe_notifier_slo_state_store_connectivity(store)
```

## Known limitations or TODOs

- Probe does not currently verify write-path health (read/connectivity only).
- Redis probe uses a simple ping/read and does not validate latency budgets.
- No automatic retry/backoff behavior is implemented in probe helper.
