# Notifier Metric To SLO Policy Mapping

Date: 2026-03-30
Author: Devin Sailer

## Summary

Added a policy-mapping layer that converts notifier transport metrics into actionable SLO alert records. This provides a deterministic bridge between metric streams (`notifier.*`) and incident-facing alert signals.

## Implementation details

- Added `code/market_data/notifier_slo_policy.py` with:
  - `NotifierSLOPolicy` policy model
  - `default_notifier_slo_policies()` for baseline drop/circuit-open mappings
  - `evaluate_notifier_slo_policies(...)` for metric-to-alert evaluation
- Default mappings include:
  - `notifier.alert_dropped` -> `notifier_delivery_drop` (`high`)
  - `notifier.circuit_open` -> `notifier_circuit_open` (`critical`)
- Reused existing `IngestionAlert` structure to keep alert handling uniform with current ingestion alert pipeline.
- Exported new APIs through `market_data.__init__`.
- Added `code/tests/test_notifier_slo_policy.py` for default and custom policy behavior.
- Updated shared docs in `code/README.md`.

## Usage

Run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_policy.py tests/test_alert_notifiers.py tests/test_ingestion_worker.py tests/test_ingestion_alerts.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py
```

Example:

```python
from market_data import evaluate_notifier_slo_policies

alerts = evaluate_notifier_slo_policies(metrics=metric_buffer)
```

## Known limitations or TODOs

- Current evaluator is threshold-based only; no rolling time-window aggregation yet.
- Policy definitions are in code and not yet externally configurable.
- Alert de-dup and escalation routing for notifier SLO alerts still rely on upstream policy handlers.
