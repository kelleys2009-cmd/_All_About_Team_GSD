# Probe Check-Mode Normalization
Date: 2026-04-01
Author: Devin Sailer

## Summary
Added check-mode normalization in probe metric emission so externally supplied check-mode values cannot inflate metric cardinality.

## Implementation details
- Added `_normalize_probe_check_mode(value)` in `code/market_data/notifier_slo_state_store.py`.
- Probe metric emission now normalizes `check_mode` to `read`, `read_write`, or `other`.
- Added unit test in `code/tests/test_notifier_slo_state_store.py` proving non-whitelisted `check_mode` values emit as `other`.
- Updated `code/README.md` documentation for check-mode normalization.

## Usage
- Existing callsites remain compatible.
- Probe metrics now guarantee bounded `check_mode` tags.
- Validation:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- Current check-mode taxonomy is fixed and coarse.
- New probe modes require explicit whitelist updates.
- No per-service override for check-mode mapping.
