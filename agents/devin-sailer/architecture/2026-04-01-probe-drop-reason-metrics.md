# Probe Drop-Reason Metrics
Date: 2026-04-01
Author: Devin Sailer

## Summary
Extended probe dropped-tag observability by splitting dropped counts into invalid-tag drops versus over-cap drops, while preserving the total dropped metric.

## Implementation details
- Updated `_sanitize_metric_tags(...)` in `code/market_data/notifier_slo_state_store.py` to return:
  - sanitized tags
  - `dropped_invalid`
  - `dropped_over_cap`
- `emit_notifier_slo_probe_metrics(...)` now emits:
  - `notifier.state_probe.custom_tags_dropped` (total)
  - `notifier.state_probe.custom_tags_dropped_invalid`
  - `notifier.state_probe.custom_tags_dropped_over_cap`
- Added/updated tests in `code/tests/test_notifier_slo_state_store.py` to validate both split counters in invalid-tag and over-cap scenarios.
- Updated `code/README.md` documentation.

## Usage
- Existing callsites unchanged.
- Use split counters to diagnose why tags were dropped.
- Validation:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- No reason code is attached to individual tags; counts are aggregate per emission.
- No rate/ratio helper metrics yet for dropped vs accepted tags.
- Alert thresholds for sustained drop-reason spikes are not yet defined.
