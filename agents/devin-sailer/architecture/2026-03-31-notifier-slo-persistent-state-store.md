# Notifier SLO Persistent State Store

Date: 2026-03-31
Author: Devin Sailer

## Summary

Added a SQLite-backed persistence adapter for notifier SLO cooldown state (`last_sent_ms`) so dedup behavior survives process restarts and deployments. This closes the gap between in-memory cooldown logic and production durability requirements.

## Implementation details

- Added `code/market_data/notifier_slo_state_store.py` with:
  - `SqliteNotifierSLOStateStore`
  - `dedupe_notifier_slo_alerts_with_store(...)`
- Store schema:
  - table `notifier_slo_state(alert_name PRIMARY KEY, last_sent_ms)`
- Store operations:
  - load full state map
  - per-alert read
  - upsert state writes
- Integrated with existing cooldown logic by loading current state, applying dedupe, then persisting updated state.
- Added tests in `code/tests/test_notifier_slo_state_store.py` for round-trip persistence and restart-safe dedupe behavior.
- Exported new APIs through `market_data.__init__` and documented in `code/README.md`.

## Usage

Run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py tests/test_notifier_slo_policy.py tests/test_alert_notifiers.py tests/test_ingestion_worker.py tests/test_ingestion_alerts.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py
```

Example:

```python
store = SqliteNotifierSLOStateStore("/var/lib/teamgsd/notifier_slo_state.db")
filtered_alerts = dedupe_notifier_slo_alerts_with_store(
    alerts,
    now_ms=now_ms,
    store=store,
)
```

## Known limitations or TODOs

- SQLite adapter is local-process/local-disk; distributed multi-node coordination is not yet covered.
- No TTL or compaction policy for stale alert rows yet.
- No checksum or schema-migration versioning metadata yet.
