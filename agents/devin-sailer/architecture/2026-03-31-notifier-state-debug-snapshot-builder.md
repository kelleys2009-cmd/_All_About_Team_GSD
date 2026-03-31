# Notifier State Debug Snapshot Builder

Date: 2026-03-31
Author: Devin Sailer

## Summary

Added a structured debug snapshot builder for notifier SLO state configuration that combines backend selection, validation results, and redacted environment values. This gives support workflows safe, actionable diagnostics without exposing secrets.

## Implementation details

- Added `NotifierSLOStateEnvDebugSnapshot` dataclass in `code/market_data/notifier_slo_state_store.py`.
- Added `build_notifier_slo_state_env_debug_snapshot(env)`:
  - derives backend from env
  - runs `validate_notifier_slo_state_env`
  - includes `valid` boolean and `errors` list
  - includes redacted env output via `redact_notifier_slo_state_env`
- Added test coverage in `code/tests/test_notifier_slo_state_store.py` to verify combined validation + redaction behavior.
- Exported new APIs in `market_data.__init__`.
- Updated shared docs in `code/README.md`.

## Usage

Run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py tests/test_notifier_slo_policy.py tests/test_alert_notifiers.py tests/test_ingestion_worker.py tests/test_ingestion_alerts.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py tests.integration.test_redis_notifier_slo_state_store_integration
```

Example:

```python
snapshot = build_notifier_slo_state_env_debug_snapshot(env)
```

## Known limitations or TODOs

- Snapshot currently captures env-level diagnostics only, not live connectivity checks.
- Redaction list is static and should be extended if new secret fields are added.
- No standardized serializer/formatter helper yet for external support tooling.
