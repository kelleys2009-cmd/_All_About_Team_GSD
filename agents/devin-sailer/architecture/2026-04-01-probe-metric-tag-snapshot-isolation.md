# Probe Metric Tag Snapshot Isolation
Date: 2026-04-01
Author: Devin Sailer

## Summary
Hardened notifier probe metric emission by sending isolated tag snapshots per metric call. This prevents callback-side tag mutation from leaking across `latency`, `success`, and `failure` emissions.

## Implementation details
- Updated `emit_notifier_slo_probe_metrics(...)` in `code/market_data/notifier_slo_state_store.py`.
- Each metric call now receives `dict(tags)` instead of a shared mutable map.
- Added regression test in `code/tests/test_notifier_slo_state_store.py` to verify mutation inside `metric_fn` does not break expected base tags.
- Updated `code/README.md` with the emitter isolation behavior.

## Usage
- Existing metric callback signatures are unchanged.
- Validation commands:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py`
  - `cd code && PYTHONPATH=. python3 -m unittest discover -s tests`

## Known limitations or TODOs
- Isolated snapshots avoid intra-emitter mutation leaks but do not prevent mutation after callback completion.
- No immutable mapping type is enforced at the API boundary.
- Future enhancement could type callbacks as read-only mappings.
