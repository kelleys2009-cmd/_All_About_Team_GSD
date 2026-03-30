# Ingestion Alert Policy and De-dup
Date: 2026-03-30
Author: Devin Sailer

## Summary
Extended ingestion SLO alerting with explicit policy-based routing and time-window de-dup filtering. This closes the next TEA-46 alerting slice by reducing noisy repeats while preserving deterministic escalation channels per alert type.

## Implementation details
Files changed:
- `code/market_data/ingestion_alerts.py`
- `code/tests/test_ingestion_alerts.py`
- `code/market_data/__init__.py`
- `code/README.md`

Design choices:
- Added policy and routed alert dataclasses:
  - `IngestionAlertPolicy(channel, dedup_window_ms)`
  - `RoutedIngestionAlert(alert, channel)`
- Added `route_ingestion_alerts(...)`:
  - maps alert types to explicit channels via policy map
  - applies default channel fallback when no policy exists
- Added `dedupe_ingestion_alerts(...)`:
  - filters repeated alerts by alert name and per-alert de-dup window
  - carries forward `last_sent_ms` state to support caller-managed scheduling loops
- Kept evaluator/policy logic pure and side-effect free so notification transport remains external.

Validation:
- Extended tests for routing and de-dup windows.
- Full unit run:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_ingestion_alerts.py tests/test_ingestion_worker.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py`
  - Result: `Ran 18 tests ... OK`

## Usage
Example flow:
- Evaluate SLO state with `evaluate_ingestion_slo(...)`.
- Route using `route_ingestion_alerts(...)` and policy map.
- De-dup with `dedupe_ingestion_alerts(...)` using a persisted `last_sent_ms` map.
- Send resulting alerts through incident channels.

Test command:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_ingestion_alerts.py
```

## Known limitations or TODOs
- De-dup currently keys on alert name only; stream-specific de-dup keys are not yet included.
- No alert suppression calendar or maintenance-window support yet.
- Next increment should wire these policies to concrete notifier adapters and escalation schedules.
