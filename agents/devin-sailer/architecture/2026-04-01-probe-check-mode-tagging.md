# Probe Check-Mode Tagging
Date: 2026-04-01
Author: Devin Sailer

## Summary
Added explicit probe check-mode tagging so observability can separate read-only health checks from read/write validation probes.

## Implementation details
- Extended `NotifierSLOStateStoreProbeResult` with `check_mode` (`read` by default).
- `probe_notifier_slo_state_store_connectivity(...)` now sets:
  - `check_mode=read` for standard checks
  - `check_mode=read_write` when `write_check=True`
- `emit_notifier_slo_probe_metrics(...)` now includes `check_mode` metric tag.
- Updated tests in `code/tests/test_notifier_slo_state_store.py` to assert `check_mode` on probe outputs and metric tags.
- Updated shared docs in `code/README.md`.

## Usage
- Existing callers are source compatible.
- Read `probe.check_mode` for programmatic handling.
- Metrics now include `check_mode=read|read_write`.
- Validation commands:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- `check_mode` is currently binary; no finer-grained probe-phase taxonomy yet.
- Historical dashboards may need updating to include/check the new tag.
- No automated migration for existing alert queries.
