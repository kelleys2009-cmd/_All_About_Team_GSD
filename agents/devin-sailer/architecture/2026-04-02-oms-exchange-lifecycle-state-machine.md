# OMS Exchange Lifecycle State Machine Slice
Date: 2026-04-02
Author: Devin Sailer

## Summary
Extended OMS from admission-only behavior to lifecycle-aware execution state transitions with exchange adapter hooks and persistent status updates.

Why: `TEA-46` requires reliable order handling beyond admission, including submit acknowledgement handling and cancel path behavior with auditable state progression.

## Implementation details
- Updated `code/trading/oms.py`:
  - Added `ExchangeAdapter` protocol.
  - Added lifecycle methods:
    - `dispatch_pending(order_id)`
    - `cancel_order(order_id)`
  - Added `LifecycleResult` contract.
  - Added state transitions:
    - `pending_submit -> open` on exchange ack
    - `pending_submit -> submit_failed` on submit failure
    - `open|pending_submit -> canceled` on cancel success
  - Added `exchange_order_id` on `OrderRecord`.
- Updated `code/trading/order_store.py`:
  - Added `get_by_order_id(...)` lookup.
  - Added `exchange_order_id` persistence.
  - Added backward-compatible schema migration for existing SQLite files.
- Updated tests:
  - `code/tests/test_oms.py` now covers dispatch, cancel, and submit-failure paths.
  - `code/tests/test_order_store.py` now validates `order_id` lookup + exchange id persistence.

Observability additions:
- Metrics:
  - `oms.order.submitted`
  - `oms.order.submit_failed`
  - `oms.order.canceled`
  - `oms.order.cancel_failed`
- Events:
  - `order_submitted`
  - `order_submit_failed`
  - `order_canceled`
  - `order_cancel_failed`

## Usage
Run focused OMS lifecycle tests:

```bash
cd ~/Desktop/Team\ GSD/code
PYTHONPATH=. python3 -m unittest tests/test_oms.py tests/test_order_store.py
```

Minimal lifecycle flow:

```python
submit_result = oms.submit_order(intent, account_state)
if submit_result.accepted:
    dispatch = oms.dispatch_pending(submit_result.order.order_id)
    # optional later cancel: oms.cancel_order(submit_result.order.order_id)
```

## Known limitations or TODOs
- No partial-fill event model yet.
- No cancel/replace sequence modeling yet.
- No retry/backoff policy around submit/cancel transport errors.
- Exchange adapter is protocol-only; concrete CEX websocket/rest adapters still needed.
- Lifecycle persistence currently local SQLite-first; production should use HA-backed state store.
