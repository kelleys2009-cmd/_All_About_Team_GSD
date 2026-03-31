# Redis Client Cert TLS Options

Date: 2026-03-31
Author: Devin Sailer

## Summary

Extended Redis state-factory TLS support with client certificate/key options so notifier cooldown state can connect to mTLS-secured Redis deployments.

## Implementation details

- Updated `code/market_data/notifier_slo_state_store.py` env parsing to include:
  - `TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CERTFILE`
  - `TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_KEYFILE`
- These values are forwarded to Redis client factory kwargs as:
  - `ssl_certfile`
  - `ssl_keyfile`
- Existing auth/TLS options (`username/password/ssl/ssl_ca_certs`) remain supported.
- Extended tests in `code/tests/test_notifier_slo_state_store.py` to assert forwarding of full secure option set.
- Updated `code/README.md` documentation for new env vars.

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
export TEAM_GSD_NOTIFIER_SLO_REDIS_SSL=true
export TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CA_CERT=/etc/ssl/certs/ca.pem
export TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CERTFILE=/etc/ssl/certs/client.crt
export TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_KEYFILE=/etc/ssl/private/client.key
```

## Known limitations or TODOs

- No preflight validation that cert/key files exist and are readable.
- No explicit support for Redis Sentinel/Cluster connection profiles yet.
- Secure-option redaction behavior in logs is not implemented in this layer.
