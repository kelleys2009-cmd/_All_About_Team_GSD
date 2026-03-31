# Redis Auth TLS Factory Options

Date: 2026-03-31
Author: Devin Sailer

## Summary

Extended notifier SLO state-store factory to support Redis authentication and TLS options from environment variables. This enables secure Redis deployments without changing application code.

## Implementation details

- Updated `create_notifier_slo_state_store_from_env(...)` in `code/market_data/notifier_slo_state_store.py` to parse:
  - `TEAM_GSD_NOTIFIER_SLO_REDIS_USERNAME`
  - `TEAM_GSD_NOTIFIER_SLO_REDIS_PASSWORD`
  - `TEAM_GSD_NOTIFIER_SLO_REDIS_SSL`
  - `TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CA_CERT`
- Added compatibility behavior:
  - tries calling `redis_client_factory(url, **kwargs)`
  - falls back to `redis_client_factory(url)` for legacy one-arg factories
- Added tests in `code/tests/test_notifier_slo_state_store.py` validating auth/TLS option forwarding.
- Updated `code/README.md` with secure Redis env var documentation.

## Usage

Run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py tests/test_notifier_slo_policy.py tests/test_alert_notifiers.py tests/test_ingestion_worker.py tests/test_ingestion_alerts.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py tests.integration.test_redis_notifier_slo_state_store_integration
```

Example env setup:

```bash
export TEAM_GSD_NOTIFIER_SLO_STATE_BACKEND=redis
export TEAM_GSD_NOTIFIER_SLO_REDIS_URL=rediss://redis.example:6380/0
export TEAM_GSD_NOTIFIER_SLO_REDIS_USERNAME=teamgsd
export TEAM_GSD_NOTIFIER_SLO_REDIS_PASSWORD='***'
export TEAM_GSD_NOTIFIER_SLO_REDIS_SSL=true
export TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CA_CERT=/etc/ssl/certs/ca.pem
```

## Known limitations or TODOs

- Client-cert (`certfile`/`keyfile`) options are not yet wired.
- Factory still does not perform active connection health checks during initialization.
- Secret management is env-based only; no vault/provider integration in this layer.
