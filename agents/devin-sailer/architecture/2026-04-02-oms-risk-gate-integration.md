# OMS Risk Gate Integration Slice
Date: 2026-04-02
Author: Devin Sailer

## Summary
Implemented a minimal order management admission path that enforces idempotent `client_order_id` handling and integrates pre-trade risk checks before any exchange submit step.

Why: `TEA-46` requires execution reliability and risk controls that prevent invalid/unsafe orders from entering the live path. This slice provides the OMS seam where risk checks are enforced and observable.

## Implementation details
- Added `code/trading/oms.py`:
  - `OrderIntent`, `OrderRecord`, `OrderSubmitResult`
  - `InMemoryOrderStore`
  - `OrderManagementService.submit_order(...)`
- Integrated with `PreTradeRiskEngine` from `code/trading/risk_controls.py`.

Admission behavior:
- Duplicate `client_order_id`:
  - Returns existing order record (idempotent behavior)
  - Emits duplicate metric/event
- Risk reject:
  - Persists `rejected_risk` record with violation codes
  - Emits rejection metrics including per-violation metric
- Risk pass:
  - Persists `pending_submit` record
  - Emits accepted metric and order-accepted event

Observability hooks:
- Metric hook signature: `(name, value, tags)`
- Event hook signature: `(event_name, payload)`
- Emitted metric families:
  - `oms.order.accepted`
  - `oms.order.rejected`
  - `oms.order.rejected_violation`
  - `oms.order.duplicate`

Testing:
- Added `code/tests/test_oms.py`:
  - acceptance path
  - risk rejection path
  - idempotent duplicate path
- Updated `code/README.md` test command list.

## Usage
Run OMS tests:

```bash
cd ~/Desktop/Team\ GSD/code
PYTHONPATH=. python3 -m unittest tests/test_oms.py
```

Run OMS + risk tests together:

```bash
cd ~/Desktop/Team\ GSD/code
PYTHONPATH=. python3 -m unittest tests/test_risk_controls.py tests/test_oms.py
```

Integration pattern:

```python
result = oms.submit_order(intent, account_state)
if not result.accepted:
    # stop order lifecycle, alert/review violations
```

## Known limitations or TODOs
- Current store is in-memory; production path must use Redis/Postgres-backed idempotency and order ledger.
- No exchange adapter submit/cancel/replace workflow wired yet.
- No persistent event log/audit sink yet (hook-based only).
- No retry/backoff/failover state machine for venue disconnects yet.
- Needs integration with position reconciliation loop and incident alert routing.
