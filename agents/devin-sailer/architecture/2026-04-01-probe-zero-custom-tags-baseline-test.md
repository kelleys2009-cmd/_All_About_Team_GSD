# Probe Zero-Custom-Tags Baseline Test
Date: 2026-04-01
Author: Devin Sailer

## Summary
Added explicit unit coverage for the zero-custom-tag path in probe metric emission to lock baseline counter/rate behavior.

## Implementation details
- Added `test_emit_probe_metrics_zero_custom_tags_baseline` to `code/tests/test_notifier_slo_state_store.py`.
- Test validates that with `metric_tags={}` and failure probe context:
  - `custom_tags_total=0`
  - `custom_tags_accepted=0`
  - `custom_tags_dropped=0`
  - all related rates are `0.0`
- Ensures baseline tag set remains stable (`backend`, `ok`, `error_class`, `check_mode`).

## Usage
- Run:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- Test currently covers failure probe context; success-path baseline can be added separately.
- No integration-level assertion yet for downstream metrics backend ingestion.
- Baseline test does not enforce metric ordering.
