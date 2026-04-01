# Probe Custom-Tag Drop Metric
Date: 2026-04-01
Author: Devin Sailer

## Summary
Added a dedicated probe metric for dropped caller tags so sanitization/cap side effects are observable in production.

## Implementation details
- Updated `_sanitize_metric_tags(...)` in `code/market_data/notifier_slo_state_store.py` to return both sanitized tags and a dropped-tag count.
- Added emission of `notifier.state_probe.custom_tags_dropped` with the per-call dropped count.
- Updated tests in `code/tests/test_notifier_slo_state_store.py` to validate dropped-count behavior for:
  - standard cases (`0`)
  - invalid tags (`None`/empty-key)
  - over-cap tag sets
- Updated `code/README.md` to document the new metric.

## Usage
- Existing callsites remain compatible.
- Monitor `notifier.state_probe.custom_tags_dropped` to identify instrumentation callers that exceed/supply invalid tags.
- Validation:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- Metric does not currently break down drop reasons (invalid vs over-cap).
- Dropped counts are per emission; no built-in rolling aggregation.
- No alert thresholds are defined yet for sustained drops.
