# Notifier Write Path Probe Mode

Date: 2026-03-31
Author: Devin Sailer

## Summary

Extended notifier state connectivity probes with optional write-path verification for deeper backend health checks. This validates not only read/connectivity but also basic mutation operations.

## Implementation details

- Updated `probe_notifier_slo_state_store_connectivity(...)` in `code/market_data/notifier_slo_state_store.py`:
  - Added `write_check` flag (default `False`)
  - SQLite write check: insert/delete on probe table
  - Redis write check: `set/get/delete` on temporary probe key
- Added defensive failure handling when Redis client lacks required write methods.
- Added tests in `code/tests/test_notifier_slo_state_store.py` for:
  - successful Redis write probe
  - failure when write methods are unavailable
- Updated `code/README.md` to document `write_check=True` capability.

## Usage

Run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py tests/test_notifier_slo_policy.py tests/test_alert_notifiers.py tests/test_ingestion_worker.py tests/test_ingestion_alerts.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py tests.integration.test_redis_notifier_slo_state_store_integration
```

Example:

```python
probe = probe_notifier_slo_state_store_connectivity(store, write_check=True)
```

## Known limitations or TODOs

- Write probe is intentionally minimal and not a performance benchmark.
- SQLite probe table is currently retained (empty) after first creation.
- Redis write probe uses a single temporary key and does not cover ACL edge cases.
