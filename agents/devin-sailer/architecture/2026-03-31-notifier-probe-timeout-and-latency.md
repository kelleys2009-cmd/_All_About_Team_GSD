# Notifier Probe Timeout And Latency

Date: 2026-03-31
Author: Devin Sailer

## Summary

Extended notifier state connectivity probes with latency measurement and optional timeout budgeting. This makes health checks measurable and allows callers to enforce bounded diagnostic behavior.

## Implementation details

- Updated `NotifierSLOStateStoreProbeResult` in `code/market_data/notifier_slo_state_store.py`:
  - added `latency_ms`
- Extended `probe_notifier_slo_state_store_connectivity(...)` with:
  - `timeout_ms` budget
  - `now_fn` test hook for deterministic timing tests
- Behavior:
  - captures elapsed probe time in milliseconds
  - marks probe as failed with timeout detail when elapsed exceeds `timeout_ms`
- Added tests in `code/tests/test_notifier_slo_state_store.py`:
  - latency field assertions
  - timeout budget failure behavior
- Updated `code/README.md` documentation.

## Usage

Run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py tests/test_notifier_slo_policy.py tests/test_alert_notifiers.py tests/test_ingestion_worker.py tests/test_ingestion_alerts.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py tests.integration.test_redis_notifier_slo_state_store_integration
```

Example:

```python
probe = probe_notifier_slo_state_store_connectivity(store, write_check=True, timeout_ms=250.0)
```

## Known limitations or TODOs

- Timeout budget is post-check validation (not an interrupt/cancel mechanism).
- No percentile/histogram aggregation of probe latencies yet.
- Probe latency includes Python runtime overhead and is not a strict transport-only metric.
