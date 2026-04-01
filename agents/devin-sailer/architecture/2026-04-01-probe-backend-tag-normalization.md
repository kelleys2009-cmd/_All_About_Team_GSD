# Probe Backend Tag Normalization
Date: 2026-04-01
Author: Devin Sailer

## Summary
Added backend-tag normalization for notifier probe metrics so backend labels are bounded and safe for metrics cardinality.

## Implementation details
- Added `_normalize_probe_backend(value)` in `code/market_data/notifier_slo_state_store.py`.
- Metric emission now normalizes backend tags to `sqlite`, `redis`, or `other`.
- Added test coverage in `code/tests/test_notifier_slo_state_store.py` to assert a custom backend string is emitted as `backend=other`.
- Updated `code/README.md` with backend tag normalization behavior.

## Usage
- Existing callsites are unchanged.
- Failed/success probe metrics now enforce bounded backend tag values.
- Validation commands:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- Only `sqlite` and `redis` are currently first-class backend tags.
- New backend implementations must be added to normalization intentionally.
- No runtime config exists yet for backend-tag mapping.
