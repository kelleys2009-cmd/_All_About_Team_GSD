# Notifier SLO State Factory

Date: 2026-03-31
Author: Devin Sailer

## Summary

Added an environment-driven factory for notifier SLO state backends so runtime can select SQLite or Redis without code changes. This enables simple local defaults and distributed production deployment options.

## Implementation details

- Extended `code/market_data/notifier_slo_state_store.py` with:
  - `create_notifier_slo_state_store_from_env(...)`
- Factory behavior:
  - `TEAM_GSD_NOTIFIER_SLO_STATE_BACKEND=sqlite|redis`
  - SQLite path via `TEAM_GSD_NOTIFIER_SLO_SQLITE_PATH` (default `artifacts/notifier_slo_state.db`)
  - Redis URL via `TEAM_GSD_NOTIFIER_SLO_REDIS_URL`
  - Redis key via `TEAM_GSD_NOTIFIER_SLO_REDIS_KEY`
- Redis backend requires injected `redis_client_factory` for runtime client creation.
- Added tests in `code/tests/test_notifier_slo_state_store.py` for:
  - default SQLite selection
  - Redis selection and URL propagation
  - required Redis factory guardrail
- Exported factory via `market_data.__init__`.
- Updated `code/README.md`.

## Usage

Run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py tests/test_notifier_slo_policy.py tests/test_alert_notifiers.py tests/test_ingestion_worker.py tests/test_ingestion_alerts.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py
```

Example:

```python
store = create_notifier_slo_state_store_from_env(
    redis_client_factory=lambda url: redis.from_url(url)
)
```

## Known limitations or TODOs

- Factory does not yet include a health-check handshake for Redis at creation time.
- No centralized config validation layer for environment variables yet.
- Adapter-level telemetry (which backend was selected) is not emitted yet.
