# Redis Notifier SLO State Adapter

Date: 2026-03-31
Author: Devin Sailer

## Summary

Added a Redis-backed notifier SLO state adapter to support cooldown coordination across multiple workers/processes. This complements the SQLite local adapter and enables shared cooldown state in distributed deployments.

## Implementation details

- Extended `code/market_data/notifier_slo_state_store.py` with `RedisNotifierSLOStateStore`.
- Redis storage model:
  - single hash key (default `teamgsd:notifier_slo_state`)
  - field = alert name
  - value = `last_sent_ms`
- Adapter operations:
  - `get_last_sent_ms(alert_name)`
  - `load_state()`
  - `save_state(state)`
- Reused existing `dedupe_notifier_slo_alerts_with_store(...)` helper with either SQLite or Redis store implementations.
- Added fake-client-based unit tests in `code/tests/test_notifier_slo_state_store.py` to verify Redis round-trip behavior.
- Exported adapter via `market_data.__init__` and updated shared docs in `code/README.md`.

## Usage

Run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py tests/test_notifier_slo_policy.py tests/test_alert_notifiers.py tests/test_ingestion_worker.py tests/test_ingestion_alerts.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py
```

Example:

```python
redis_store = RedisNotifierSLOStateStore(redis_client, key="teamgsd:notifier_slo_state")
filtered_alerts = dedupe_notifier_slo_alerts_with_store(alerts, now_ms=now_ms, store=redis_store)
```

## Known limitations or TODOs

- No Redis TTL/expiry strategy for stale alert keys yet.
- No optimistic locking or CAS semantics for concurrent update contention.
- Production wiring still needs adapter selection by environment config.
