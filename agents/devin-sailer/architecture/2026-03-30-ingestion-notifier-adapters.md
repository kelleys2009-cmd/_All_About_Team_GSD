# Ingestion Notifier Adapters
Date: 2026-03-30
Author: Devin Sailer

## Summary
Added notifier adapter primitives for routed ingestion alerts so policy-evaluated signals can be dispatched to channel-specific handlers with deterministic accounting of sent vs dropped notifications.

## Implementation details
Files changed:
- `code/market_data/alert_notifiers.py`
- `code/tests/test_alert_notifiers.py`
- `code/market_data/__init__.py`
- `code/README.md`

Design choices:
- Added `format_routed_alert(...)` for consistent human-readable alert messages.
- Added `dispatch_routed_alerts(...)`:
  - accepts routed alerts and channel sender mapping
  - dispatches to available sender callbacks
  - returns `NotificationDispatchResult(sent, dropped)` for observability and retries
- Kept transport integration callback-based to support Slack, Pager, webhook, or internal bus senders without hard dependency.

Validation:
- Added tests covering formatting and sent/dropped dispatch accounting.
- Full run:
  - `cd code && PYTHONPATH=. python3 -m unittest tests/test_alert_notifiers.py tests/test_ingestion_alerts.py tests/test_ingestion_worker.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py`
  - Result: `Ran 20 tests ... OK`

## Usage
Integration pattern:
- Build alerts via evaluator and routing modules.
- Inject channel sender callables into `dispatch_routed_alerts(...)`.
- Use returned counts to emit operational metrics and retry dropped routes.

Test command:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_alert_notifiers.py
```

## Known limitations or TODOs
- No built-in retry queue for dropped alerts yet.
- Sender callbacks are synchronous; async/non-blocking delivery is not yet implemented.
- Next increment should provide concrete Slack/webhook adapters with retry and timeout controls.
