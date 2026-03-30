# Notifier Circuit Breaker and Failure Classification

Date: 2026-03-30
Author: Devin Sailer

## Summary

Extended alert notifier reliability controls by classifying transport failures and adding a sender-level circuit breaker. This reduces repeated downstream failures from causing continuous retry storms while preserving deterministic behavior in the ingestion alert pipeline.

## Implementation details

- Added `CircuitBreakerPolicy` with:
  - `failure_threshold`
  - `open_seconds`
- Added notifier error types:
  - `NotifierTransientError`
  - `NotifierPermanentError`
  - `NotifierCircuitOpenError`
- Added HTTP/network failure classification in notifier transport:
  - HTTP 4xx (except `408`, `429`) => permanent error
  - HTTP 5xx, `408`, `429`, URL/network timeout errors => transient error
- Updated `WebhookAlertSender`:
  - tracks consecutive failures
  - opens circuit after threshold is reached
  - fast-fails while circuit is open
  - resets failure counter on successful send
- Updated `dispatch_routed_alerts` behavior:
  - sender exceptions now increment `dropped` and processing continues for subsequent alerts
- Added tests for:
  - permanent error classification on HTTP 400
  - circuit opening after repeated failures and reopening after cooldown
  - dispatch degradation behavior on sender exceptions
- Updated exports and module docs.

## Usage

Run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_alert_notifiers.py tests/test_ingestion_alerts.py tests/test_ingestion_worker.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py
```

Example sender configuration:

```python
from market_data import CircuitBreakerPolicy, NotifierRetryPolicy, WebhookAlertSender

sender = WebhookAlertSender(
    webhook_url="https://ops.example/hook",
    retry_policy=NotifierRetryPolicy(max_attempts=3, backoff_seconds=0.25, timeout_seconds=2.0),
    circuit_breaker=CircuitBreakerPolicy(failure_threshold=3, open_seconds=30.0),
)
```

## Known limitations or TODOs

- Circuit state is process-local and in-memory; it is not yet shared across workers.
- Classification is HTTP-status based and may need provider-specific tuning.
- No explicit metrics hooks are emitted yet for circuit open/close transitions.
