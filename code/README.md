# Team GSD Shared Code Modules

## Market Data

`market_data/normalization.py`
- Deterministic OHLCV normalization contract.

`market_data/raw_store.py`
- Raw event persistence and deterministic replay primitives.
- Includes local SQLite writer, Postgres/Timescale runtime writer, and schema helpers.
- Includes replay checkpoint persistence for long-running ingestion jobs.
- Includes checkpoint-aware replay resume (`replay_after_checkpoint`) with optional bounded windows.
- Includes ingestion auto-advance helper (`append_and_advance_checkpoint`) for daemon workers.

`market_data/ingestion_worker.py`
- Checkpointed ingestion worker loop orchestration for daemon jobs.
- Includes bounded source pulls and exponential retry backoff.
- Includes optional structured metric/log hooks for ingest lag and retry observability.
- Includes notifier metric adapters so alert sender metrics inherit worker tags.

`market_data/ingestion_alerts.py`
- SLO threshold evaluator for ingestion lag/retry/idle signals.
- Produces alert records that can be routed to incident systems.
- Includes channel policy mapping and de-dup window filtering helpers.

`market_data/alert_notifiers.py`
- Adapter helpers to dispatch routed alerts to channel-specific senders.
- Includes deterministic dispatch accounting (`sent`/`dropped`).
- Includes concrete webhook/slack sender classes with timeout + retry policy.
- Includes failure classification (transient vs permanent) and circuit-breaker guard.
- Includes optional metric hooks for send/drop/failure/circuit-open observability.
- Includes notifier metric schema contract validation (required base tags + reason enum checks).

`market_data/notifier_slo_policy.py`
- Maps notifier metric streams into actionable SLO alert records.
- Includes default policy bindings for drop and circuit-open events.
- Includes optional rolling-window evaluation via timestamped metric points.
- Includes cooldown/dedup helpers to suppress repeated SLO alert spam.

`market_data/notifier_slo_state_store.py`
- SQLite-backed persistence for notifier SLO cooldown `last_sent_ms` state.
- Includes helper to run dedupe with persisted state across process restarts.
- Includes Redis-backed state adapter for multi-worker cooldown coordination.
- Includes env-driven store factory (`TEAM_GSD_NOTIFIER_SLO_STATE_BACKEND=sqlite|redis`).
- Supports optional Redis auth/TLS env vars (`..._USERNAME`, `..._PASSWORD`, `..._SSL`, `..._SSL_CA_CERT`).
- Supports optional Redis client-cert TLS env vars (`..._SSL_CERTFILE`, `..._SSL_KEYFILE`).
- Includes env validation helper for fail-fast Redis config diagnostics.
- Includes env redaction helper to prevent secret leakage in diagnostics.
- Includes a debug snapshot builder combining backend/validation/redacted env payloads.
- Includes runtime connectivity probe helper for SQLite/Redis backend diagnostics.
- Probe helper supports optional write-path checks (`write_check=True`).

## Tests

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_normalization.py tests/test_raw_store.py tests/test_backtesting.py
PYTHONPATH=. python3 -m unittest tests/test_ingestion_worker.py
PYTHONPATH=. python3 -m unittest tests/test_ingestion_alerts.py
PYTHONPATH=. python3 -m unittest tests/test_alert_notifiers.py
PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_policy.py
PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py
```

Postgres integration harness (runs only when DSN is provided):

```bash
cd code
TEAM_GSD_TEST_POSTGRES_DSN='postgresql://user:pass@localhost:5432/dbname' \
PYTHONPATH=. python3 -m unittest tests.integration.test_postgres_raw_store_integration
```

Redis notifier SLO integration harness (runs only when URL is provided):

```bash
cd code
TEAM_GSD_TEST_REDIS_URL='redis://127.0.0.1:6379/0' \
PYTHONPATH=. python3 -m unittest tests.integration.test_redis_notifier_slo_state_store_integration
```
