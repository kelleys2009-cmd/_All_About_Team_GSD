# Probe Custom-Tag Total Metric
Date: 2026-04-01
Author: Devin Sailer

## Summary
Added `custom_tags_total` probe metric to provide an explicit denominator for accepted/dropped custom tag metrics and rates.

## Implementation details
- Updated `emit_notifier_slo_probe_metrics(...)` in `code/market_data/notifier_slo_state_store.py`.
- Added emission of `notifier.state_probe.custom_tags_total` where:
  - `custom_tags_total = custom_tags_accepted + custom_tags_dropped`
- Updated tests in `code/tests/test_notifier_slo_state_store.py` to verify totals in:
  - invalid-tag scenario (`5`)
  - over-cap scenario (`17`)
- Updated `code/README.md` docs.

## Usage
- Existing callsites unchanged.
- Use `custom_tags_total` as a direct denominator for acceptance/drop dashboards.
- Validation:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- Metric is per emission and not window-aggregated.
- No built-in accepted-rate metric yet (`accepted/total`).
- No alert defaults for low-total / high-total anomalies.
