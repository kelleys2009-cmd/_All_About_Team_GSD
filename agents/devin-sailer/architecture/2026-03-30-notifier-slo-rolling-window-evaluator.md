# Notifier SLO Rolling Window Evaluator

Date: 2026-03-30
Author: Devin Sailer

## Summary

Extended notifier SLO policy evaluation to support rolling-window aggregation using timestamped metric points. This enables policy checks over explicit time slices instead of raw per-batch totals.

## Implementation details

- Added `NotifierMetricPoint` model in `code/market_data/notifier_slo_policy.py`.
- Extended `evaluate_notifier_slo_policies(...)` with:
  - `metric_points` input (timestamped metrics)
  - `window_ms` + `now_ms` filtering for rolling-window evaluation
- Preserved backward compatibility:
  - legacy `metrics=[(name, value, tags), ...]` path still works
- Exported `NotifierMetricPoint` from `market_data.__init__`.
- Added test coverage in `code/tests/test_notifier_slo_policy.py` for old/new window boundary filtering behavior.
- Updated shared docs in `code/README.md`.

## Usage

Run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_policy.py tests/test_alert_notifiers.py tests/test_ingestion_worker.py tests/test_ingestion_alerts.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py
```

Example:

```python
from market_data import NotifierMetricPoint, evaluate_notifier_slo_policies

alerts = evaluate_notifier_slo_policies(
    metrics=[],
    metric_points=[
        NotifierMetricPoint(ts_ms=1711900000000, metric_name="notifier.alert_dropped", value=1.0, tags={...}),
    ],
    window_ms=60_000,
    now_ms=1711900060000,
)
```

## Known limitations or TODOs

- No built-in bucketed histogram/percentile aggregation yet.
- Windowing is currently caller-driven (`now_ms` is supplied externally).
- Policy storage remains in code and is not yet dynamically configurable.
