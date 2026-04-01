# Probe Metric Custom Tag Cap
Date: 2026-04-01
Author: Devin Sailer

## Summary
Added a hard cap on caller-provided custom probe metric tags to prevent excessive label sets and reduce cardinality risk.

## Implementation details
- Added `PROBE_METRIC_MAX_CUSTOM_TAGS = 12` in `code/market_data/notifier_slo_state_store.py`.
- Updated `_sanitize_metric_tags(...)` to stop collecting caller tags after the cap.
- Added test coverage in `code/tests/test_notifier_slo_state_store.py` verifying only the capped number of custom keys are emitted.
- Updated `code/README.md` with the custom-tag cap behavior.

## Usage
- Existing callers remain source compatible.
- If more than 12 custom tags are provided, extra tags are ignored.
- Validation:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- Current cap is static and not runtime-configurable.
- Extra tags are dropped silently; no overflow metric is emitted yet.
- Ordering follows input mapping order.
