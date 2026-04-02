# OMS SQLite Order Store Integration
Date: 2026-04-02
Author: Devin Sailer

## Summary
Implemented a persistent SQLite-backed OMS order store and wired it into the OMS idempotent admission flow so `client_order_id` de-dup survives process restarts.

Why: `TEA-46` requires idempotent order handling and state persistence. Prior in-memory-only storage was insufficient for reliable live operations.

## Implementation details
- Added `code/trading/order_store.py` with `SQLiteOrderStore`:
  - Table: `oms_orders`
  - Primary key: `client_order_id`
  - Upsert semantics for deterministic replacement
  - JSON serialization for `risk_violations`
- Updated `code/trading/oms.py` to accept an `OrderStore` protocol type (duck-typed `get/upsert`).
- Existing `InMemoryOrderStore` retained for fast local tests.

Tests added/updated:
- `code/tests/test_order_store.py`
  - round-trip persistence
  - upsert overwrite semantics
- `code/tests/test_oms.py`
  - added SQLite-backed OMS idempotency test path

## Usage
Run persistence + OMS tests:

```bash
cd ~/Desktop/Team\ GSD/code
PYTHONPATH=. python3 -m unittest tests/test_order_store.py tests/test_oms.py
```

Use SQLite store in OMS setup:

```python
from trading.order_store import SQLiteOrderStore
from trading.oms import OrderManagementService

store = SQLiteOrderStore("runtime/oms/orders.sqlite3")
oms = OrderManagementService(risk_engine=risk_engine, order_store=store)
```

## Known limitations or TODOs
- SQLite is single-node/local; production multi-worker mode should use Postgres/Redis-backed store.
- No migration versioning yet for schema changes.
- No explicit transaction bundling with downstream exchange submit ack lifecycle yet.
- Needs write-path metrics (latency/failures) and alerting on store errors.
