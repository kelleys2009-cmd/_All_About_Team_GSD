# Probe Error-Class Normalization Guard
Date: 2026-03-31
Author: Devin Sailer

## Summary
Added a normalization guard so probe metric `error_class` tags remain bounded even when probe results are supplied with unexpected class strings. This protects observability backends from metric-cardinality blowups.

## Implementation details
- Added `_normalize_probe_error_class(value)` in `code/market_data/notifier_slo_state_store.py`.
- Whitelisted classes: `timeout`, `connection`, `auth`, `runtime`, `other`.
- Non-empty values outside the whitelist are rewritten to `other`.
- Updated `emit_notifier_slo_probe_metrics(...)` to normalize both:
  - structured `probe.error_class`
  - fallback detail-derived class
- Added test coverage in `code/tests/test_notifier_slo_state_store.py` to verify custom/unbounded `error_class` input is emitted as `other`.
- Updated `code/README.md` with normalization behavior.

## Usage
- Existing callsites unchanged.
- On failed probes, emitted `error_class` remains bounded to the whitelist.
- Validation commands:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- Normalization is static; introducing new classes requires explicit whitelist update.
- No runtime config for class mapping yet.
- Current mapping still depends on string parsing in fallback paths.
