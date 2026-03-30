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

`market_data/ingestion_alerts.py`
- SLO threshold evaluator for ingestion lag/retry/idle signals.
- Produces alert records that can be routed to incident systems.
- Includes channel policy mapping and de-dup window filtering helpers.

`market_data/alert_notifiers.py`
- Adapter helpers to dispatch routed alerts to channel-specific senders.
- Includes deterministic dispatch accounting (`sent`/`dropped`).
- Includes concrete webhook/slack sender classes with timeout + retry policy.

## Tests

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_normalization.py tests/test_raw_store.py tests/test_backtesting.py
PYTHONPATH=. python3 -m unittest tests/test_ingestion_worker.py
PYTHONPATH=. python3 -m unittest tests/test_ingestion_alerts.py
PYTHONPATH=. python3 -m unittest tests/test_alert_notifiers.py
```

Postgres integration harness (runs only when DSN is provided):

```bash
cd code
TEAM_GSD_TEST_POSTGRES_DSN='postgresql://user:pass@localhost:5432/dbname' \
PYTHONPATH=. python3 -m unittest tests.integration.test_postgres_raw_store_integration
```
