# Structured Probe Error-Class Field
Date: 2026-03-31
Author: Devin Sailer

## Summary
Extended notifier SLO connectivity probe results with a structured `error_class` field so failure categorization is explicit at probe time and does not rely only on parsing human-readable detail strings.

## Implementation details
- Updated `NotifierSLOStateStoreProbeResult` in `code/market_data/notifier_slo_state_store.py` to include optional `error_class`.
- Added `_classify_probe_exception(exc)` to map exception types into bounded classes:
  - `timeout`, `connection`, `auth`, `runtime`, `other`
- Updated probe result creation:
  - timeout budget failures now set `error_class="timeout"`
  - exception-path failures set `error_class` from `_classify_probe_exception`
- Updated metric emission to prefer `probe.error_class` and fallback to detail parsing for backward compatibility.
- Added/updated tests in `code/tests/test_notifier_slo_state_store.py` to assert `error_class` values on runtime and timeout failure paths.
- Updated `code/README.md` with probe result `error_class` behavior.

## Usage
- Run tests:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`
- Existing callers of `probe_notifier_slo_state_store_connectivity(...)` continue working; they can now read `probe.error_class` for structured handling.

## Known limitations or TODOs
- Exception-name heuristics are still string based and should eventually map from explicit, domain-level error codes.
- Current classes are intentionally coarse to preserve metric cardinality.
- No per-backend remediation hints are attached yet.
