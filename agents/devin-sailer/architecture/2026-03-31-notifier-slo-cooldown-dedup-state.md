# Notifier SLO Cooldown Dedup State

Date: 2026-03-31
Author: Devin Sailer

## Summary

Added policy-level cooldown/dedup support for notifier SLO alerts so repeated rolling-window breaches do not spam incident channels. The evaluator can now maintain per-alert last-sent state and suppress duplicates until cooldown expires.

## Implementation details

- Extended `code/market_data/notifier_slo_policy.py` with:
  - `NotifierSLOCooldownPolicy`
  - `dedupe_notifier_slo_alerts(...)`
- Dedupe behavior:
  - accepts prior `last_sent_ms` state
  - applies per-alert cooldown policy overrides
  - returns filtered alert list and updated state map
- Exported APIs via `market_data.__init__`.
- Added test coverage in `code/tests/test_notifier_slo_policy.py` for first-send, suppressed resend, and cooldown-expired resend behavior.
- Updated shared docs in `code/README.md`.

## Usage

Run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_policy.py tests/test_alert_notifiers.py tests/test_ingestion_worker.py tests/test_ingestion_alerts.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py
```

Example:

```python
filtered_alerts, state = dedupe_notifier_slo_alerts(
    alerts,
    now_ms=now_ms,
    cooldown_policy_by_alert={"notifier_delivery_drop": NotifierSLOCooldownPolicy(cooldown_ms=300000)},
    last_sent_ms=last_state,
)
```

## Known limitations or TODOs

- State store is caller-managed; no built-in persistence backend yet.
- Cooldown policy is per alert name only (no per-venue/per-symbol granularity yet).
- No jitter/backoff strategy on cooldown expiry bursts.
