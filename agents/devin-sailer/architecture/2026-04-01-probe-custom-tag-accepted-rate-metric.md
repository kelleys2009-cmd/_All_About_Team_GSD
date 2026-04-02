# Probe Custom-Tag Accepted-Rate Metric
Date: 2026-04-01
Author: Devin Sailer

## Summary
Added an accepted-rate probe metric to pair with drop-rate metrics and provide a direct accepted/total ratio for caller tag quality monitoring.

## Implementation details
- Updated `emit_notifier_slo_probe_metrics(...)` in `code/market_data/notifier_slo_state_store.py`.
- Added `notifier.state_probe.custom_tags_accepted_rate`:
  - `accepted_rate = accepted / total`
  - defaults to `0.0` when total is zero
- Updated tests in `code/tests/test_notifier_slo_state_store.py` for expected accepted rates in invalid-tag and over-cap scenarios.
- Updated `code/README.md` docs.

## Usage
- Existing callsites unchanged.
- Use accepted-rate metric with drop-rate metrics for quick instrumentation health checks.
- Validation:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- Rate is per emission and may be noisy without windowed aggregation.
- No default alert thresholds are set.
- No moving-average helper metric is emitted yet.
