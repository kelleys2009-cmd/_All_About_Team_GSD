# Probe Custom-Tag Accepted Metric
Date: 2026-04-01
Author: Devin Sailer

## Summary
Added `custom_tags_accepted` probe metric to complement dropped-tag metrics and provide full visibility into custom tag intake per emission.

## Implementation details
- Updated `emit_notifier_slo_probe_metrics(...)` in `code/market_data/notifier_slo_state_store.py` to emit:
  - `notifier.state_probe.custom_tags_accepted`
- `custom_tags_accepted` measures accepted caller tags after sanitization and before system tags are added.
- Updated tests in `code/tests/test_notifier_slo_state_store.py` to assert accepted counts in invalid-tag and over-cap scenarios.
- Updated `code/README.md` documentation.

## Usage
- Existing callsites unchanged.
- Use accepted + dropped metrics together to derive acceptance/drop rates.
- Validation:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- No direct ratio metric is emitted yet.
- Accepted count does not include system tags (`backend`, `ok`, `check_mode`, `error_class`).
- No alert threshold defaults are defined for acceptance-rate degradation.
