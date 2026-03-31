# Notifier Metric Hooks

Date: 2026-03-30
Author: Devin Sailer

## Summary

Added structured metric hooks to notifier sender and dispatch paths so alert transport reliability is observable at runtime. The implementation emits counters for send success, sender drops, classified failures, and circuit-breaker open transitions.

## Implementation details

- Extended `WebhookAlertSender` and `SlackWebhookAlertSender` with optional:
  - `metric_fn(name, value, tags)` callback
  - `metric_tags` base tags map
- Added sender-level metric emissions:
  - `notifier.sent`
  - `notifier.failure` with `reason=permanent|transient`
  - `notifier.circuit_open`
  - `notifier.circuit_open_drop`
- Extended `dispatch_routed_alerts` with optional metric callback and base tags.
- Added dispatch-level metrics:
  - `notifier.alert_sent`
  - `notifier.alert_dropped` with `reason=missing_sender|sender_error`
  - `notifier.batch_sent`
  - `notifier.batch_dropped`
- Added tests to verify metric emission for sender errors and circuit-open behavior.

## Usage

Run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_alert_notifiers.py tests/test_ingestion_alerts.py tests/test_ingestion_worker.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py
```

Example metric wiring:

```python
from market_data import WebhookAlertSender

metrics = []
sender = WebhookAlertSender(
    webhook_url="https://ops.example/hook",
    metric_fn=lambda name, value, tags: metrics.append((name, value, tags)),
    metric_tags={"venue": "BINANCE_PERP", "symbol": "BTC-USD-PERP"},
)
```

## Known limitations or TODOs

- Metrics are callback-driven and not yet wired to a concrete backend (Prometheus/StatsD).
- No histogram/timer metrics yet for transport latency.
- Circuit state remains process-local and should be externalized for multi-worker coordination.
