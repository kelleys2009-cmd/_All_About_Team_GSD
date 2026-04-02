# OMS Partial Fill and Cancel-Replace Workflow
Date: 2026-04-02
Author: Devin Sailer

## Summary
Extended OMS lifecycle handling to support partial/full fills, fill quality telemetry, and cancel-replace order updates. This closes key execution-path gaps for real venue behavior where orders fill incrementally and must be repriced.

Why: `TEA-46` requires realistic execution reliability with observability, including fill progression and order modification flows.

## Implementation details
- Updated `code/trading/oms.py`:
  - Added `OrderRecord` fields:
    - `filled_quantity`
    - `avg_fill_price`
  - Added `apply_fill(order_id, fill_quantity, fill_price, ack_latency_ms=None)`:
    - transitions `open -> partially_filled -> filled`
    - computes directional `fill_slippage_bps`
    - emits `oms.order.ack_latency_ms` when provided
  - Added `replace_order(...)` cancel-replace helper:
    - cancels existing live order
    - submits replacement order with new client id/price/size
    - emits replacement metrics/events
- Updated `code/trading/order_store.py`:
  - Persisted new fill fields.
  - Added migration guards for older schemas.

Observability additions:
- Metrics:
  - `oms.order.fill_count`
  - `oms.order.fill_slippage_bps`
  - `oms.order.ack_latency_ms`
  - `oms.order.replace_count`
- Events:
  - `order_filled`
  - `order_replaced`

## Usage
Run tests:

```bash
cd ~/Desktop/Team\ GSD/code
PYTHONPATH=. python3 -m unittest tests/test_oms.py tests/test_order_store.py tests/test_risk_controls.py
```

Lifecycle example:

```python
submit = oms.submit_order(intent, account_state)
opened = oms.dispatch_pending(submit.order.order_id)
oms.apply_fill(opened.order.order_id, fill_quantity=0.25, fill_price=101.2, ack_latency_ms=12.4)
oms.replace_order(opened.order.order_id, "new-client-id", 100.8, 0.75, now_ms, account_state)
```

## Known limitations or TODOs
- No explicit partial-fill fee model yet.
- No native multi-fill execution report sequence ids.
- Replace flow currently modeled as cancel + new submit; no dedicated venue-level amend API abstraction yet.
- No persisted execution timeline table yet (currently latest state only in order row).
