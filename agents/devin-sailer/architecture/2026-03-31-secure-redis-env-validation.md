# Secure Redis Env Validation

Date: 2026-03-31
Author: Devin Sailer

## Summary

Added fail-fast environment validation for notifier SLO Redis backend configuration, including secure auth/TLS combinations. This prevents runtime misconfiguration drift and provides explicit diagnostics before state-store initialization.

## Implementation details

- Added `validate_notifier_slo_state_env(env)` in `code/market_data/notifier_slo_state_store.py`.
- Validation rules for `backend=redis` include:
  - Redis URL required
  - password required when username is set
  - CA cert required when SSL is enabled
  - client cert and key must be configured together
- Integrated validation into `create_notifier_slo_state_store_from_env(...)`:
  - raises `ValueError` with joined diagnostics when validation fails
- Added tests in `code/tests/test_notifier_slo_state_store.py` for both valid secure config and expected error cases.
- Exported validator in `market_data.__init__` and updated `code/README.md`.

## Usage

Run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py tests/test_notifier_slo_policy.py tests/test_alert_notifiers.py tests/test_ingestion_worker.py tests/test_ingestion_alerts.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py tests.integration.test_redis_notifier_slo_state_store_integration
```

## Known limitations or TODOs

- Validation currently checks presence/consistency but not file readability for cert paths.
- URL format validation is delegated to downstream Redis client.
- No centralized config-schema registry yet for cross-module reuse.
