# Probe Metric Tag Length Bounds
Date: 2026-04-01
Author: Devin Sailer

## Summary
Added explicit key/value length bounds to probe metric tag sanitization to reduce cardinality and protect downstream metric sink constraints.

## Implementation details
- Added constants in `code/market_data/notifier_slo_state_store.py`:
  - `PROBE_METRIC_MAX_TAG_KEY_LEN = 64`
  - `PROBE_METRIC_MAX_TAG_VALUE_LEN = 128`
- Updated `_sanitize_metric_tags(...)` to truncate keys/values to those limits.
- Added test coverage in `code/tests/test_notifier_slo_state_store.py` for long key/value truncation.
- Updated `code/README.md` to document bounded key/value behavior.

## Usage
- Existing emit calls remain compatible.
- Overlong metric tag keys/values are now truncated before emission.
- Validation:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- Truncation may merge previously distinct long tag values.
- Length limits are static constants and not runtime-configurable.
- No collision metrics are emitted yet when truncation occurs.
