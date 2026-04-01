# Probe Drop-Rate Reason Split
Date: 2026-04-01
Author: Devin Sailer

## Summary
Extended probe drop-rate observability by splitting drop-rate metrics into invalid-tag and over-cap components.

## Implementation details
- Updated `emit_notifier_slo_probe_metrics(...)` in `code/market_data/notifier_slo_state_store.py`.
- Added:
  - `notifier.state_probe.custom_tags_drop_rate_invalid`
  - `notifier.state_probe.custom_tags_drop_rate_over_cap`
- Both are computed over total caller tags (`accepted + dropped`).
- Updated tests in `code/tests/test_notifier_slo_state_store.py` for expected reason-specific rates in invalid-tag and over-cap scenarios.
- Updated `code/README.md` docs.

## Usage
- Existing callsites unchanged.
- Use reason-specific rates to distinguish quality issues in caller instrumentation from over-cap behavior.
- Validation:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- Rates are per emission and not pre-aggregated.
- No rolling window helper exists for smoothing noisy per-call rates.
- No default alert thresholds are configured.
