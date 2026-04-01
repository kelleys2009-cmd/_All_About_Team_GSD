# Probe Metric Tag Sanitization
Date: 2026-04-01
Author: Devin Sailer

## Summary
Added sanitization for caller-provided probe metric tags so emitted tags are consistently string-typed and safe for downstream metric sinks.

## Implementation details
- Added `_sanitize_metric_tags(...)` in `code/market_data/notifier_slo_state_store.py`.
- `emit_notifier_slo_probe_metrics(...)` now:
  - accepts `metric_tags` as generic object values
  - coerces tag keys/values to strings
  - drops empty tag keys
- Added test coverage in `code/tests/test_notifier_slo_state_store.py` for mixed-type input tags and empty-key dropping.
- Updated `code/README.md` docs.

## Usage
- Existing callsites remain compatible.
- You can pass non-string tag values; they will be stringified before metric emission.
- Validation:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- String coercion currently uses Python default `str(...)` semantics.
- No explicit max-length enforcement for user-supplied tags.
- Structured/nested tag values are flattened via string conversion.
