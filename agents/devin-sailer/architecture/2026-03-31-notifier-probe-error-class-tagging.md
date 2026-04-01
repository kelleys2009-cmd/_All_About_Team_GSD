# Notifier Probe Error-Class Metric Tagging
Date: 2026-03-31
Author: Devin Sailer

## Summary
Added bounded error-class tagging for notifier state store probe metrics so failed probes can be segmented by failure family without creating high-cardinality metric labels.

## Implementation details
- Updated `code/market_data/notifier_slo_state_store.py` with `_classify_probe_error(detail)`.
- Classification maps probe failure details into a fixed set: `timeout`, `connection`, `auth`, `runtime`, `other`.
- `emit_notifier_slo_probe_metrics(...)` now includes `error_class` only when `probe.ok == False` and classification succeeds.
- Kept existing metrics unchanged (`latency_ms`, `success`, `failure`) and added tests to verify both runtime-class and timeout-class tagging behavior.
- Updated `code/README.md` to document the bounded `error_class` tag contract.

## Usage
- No API change for callers: continue calling `emit_notifier_slo_probe_metrics(...)`.
- On failed probes, emitted tags now include `error_class` with one of the bounded values.
- Run validation:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- Classification is string-pattern based and depends on probe detail text shape.
- Future improvement: classify from structured error codes/types generated at probe time instead of parsing detail strings.
