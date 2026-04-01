# Probe Custom-Tag Drop-Rate Metric
Date: 2026-04-01
Author: Devin Sailer

## Summary
Added a drop-rate metric for probe custom tags so observability can track the ratio of dropped tags to total caller tags per emission.

## Implementation details
- Updated `emit_notifier_slo_probe_metrics(...)` in `code/market_data/notifier_slo_state_store.py`.
- Added `notifier.state_probe.custom_tags_drop_rate` where:
  - denominator = accepted + dropped caller tags
  - value = dropped / total
  - defaults to `0.0` when total is zero
- Added/updated test assertions in `code/tests/test_notifier_slo_state_store.py` for:
  - invalid-tag scenario (`0.4`)
  - over-cap scenario (`5/17`)
- Updated `code/README.md` docs.

## Usage
- Existing callsites unchanged.
- Use alongside accepted/dropped counters for quick quality monitoring of caller-provided tag sets.
- Validation:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- Ratio is per emission and not window-aggregated.
- No built-in alert thresholds for elevated drop rate.
- No reason-weighted rate variants yet.
