# Webhook Notifier Retry/Timeout Policy

Date: 2026-03-30
Author: Devin Sailer

## Summary

Implemented concrete alert transport senders for market-data incident notifications with explicit timeout and retry/backoff behavior. This closes the gap between routed alert generation and production-ready outbound delivery, while keeping dependencies minimal and deterministic.

## Implementation details

- Added `NotifierRetryPolicy` with configurable `max_attempts`, `backoff_seconds`, and `timeout_seconds`.
- Added `WebhookAlertSender` with:
  - injectable `post_json` transport function
  - injectable `sleep` function for testability
  - exponential backoff retry loop on transient network/timeout errors
- Added `SlackWebhookAlertSender` wrapper that reuses the webhook sender and applies Slack text payload formatting.
- Added payload builders:
  - `build_webhook_payload` for generic webhook sinks
  - `build_slack_payload` for Slack incoming-webhook shape
- Exported new notifier APIs through `market_data.__init__`.
- Added/expanded tests in `code/tests/test_alert_notifiers.py` for retry success, retry exhaustion, payload shape, and Slack sender behavior.

## Usage

Run notifier tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_alert_notifiers.py tests/test_ingestion_alerts.py tests/test_ingestion_worker.py
```

Example wiring:

```python
from market_data import NotifierRetryPolicy, SlackWebhookAlertSender

sender = SlackWebhookAlertSender(
    webhook_url="https://hooks.slack.com/services/xxx/yyy/zzz",
    retry_policy=NotifierRetryPolicy(max_attempts=3, backoff_seconds=0.25, timeout_seconds=2.0),
)
```

## Known limitations or TODOs

- Current transport path uses Python stdlib HTTP; no connection pooling yet.
- Retry classification is currently broad for HTTP/network failures; follow-up should distinguish permanent client errors from transient server/network faults.
- No circuit-breaker state is implemented yet across repeated outage windows.
