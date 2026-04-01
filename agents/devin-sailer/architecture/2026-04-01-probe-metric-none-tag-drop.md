# Probe Metric None-Value Tag Drop
Date: 2026-04-01
Author: Devin Sailer

## Summary
Updated probe metric tag sanitization to drop caller-provided tags with `None` values. This avoids noisy/ambiguous tags and keeps emitted label sets stable.

## Implementation details
- Updated `_sanitize_metric_tags(...)` in `code/market_data/notifier_slo_state_store.py`.
- Tags with empty keys were already dropped; this increment also drops tags where value is `None`.
- Added assertion coverage in `code/tests/test_notifier_slo_state_store.py` to verify `None` tags are absent in emitted metrics.
- Updated `code/README.md` docs to reflect the behavior.

## Usage
- Existing callers remain compatible.
- `metric_tags={"optional": None}` now omits the `optional` tag from emission.
- Validation:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- String conversion still uses Python `str(...)` for non-`None` values.
- No explicit maximum key/value length enforcement.
- Nested objects are still flattened via string conversion.
