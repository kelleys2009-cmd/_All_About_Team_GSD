# Raw Market Event Store Contract for Deterministic Replay
Date: 2026-03-30
Author: Devin Sailer

## Summary
Built a deterministic raw market-event persistence layer for OHLCV/trade ingestion that supports idempotent writes and ordered replay. The immediate goal is to make paper trading and backtesting consume the same event contract while preserving source payload/version metadata for reproducibility.

## Implementation details
- Added `code/market_data/raw_store.py`.
- Introduced `RawMarketEvent` contract with fields: venue, symbol, timeframe, event time, ingest sequence, source, payload version, payload JSON.
- Implemented `SqliteRawEventStore` for local development:
  - append-only writes with composite primary key `(venue, symbol, timeframe, event_time_ms, ingest_seq)`
  - idempotent behavior via `INSERT OR IGNORE`
  - deterministic replay ordered by `(event_time_ms, ingest_seq)`
- Added `timescaledb_schema_sql()` to define the production table contract using JSONB payload storage and a pair/time index.
- Added tests in `code/tests/test_raw_store.py` for deterministic ordering, idempotent duplicate handling, and DDL contract checks.

Dependencies:
- Python stdlib (`sqlite3`, `json`, `dataclasses`)
- No external runtime dependencies added.

## Usage
Run the market-data tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_raw_store.py tests/test_normalization.py
```

Example usage in Python:

```python
from pathlib import Path
from market_data.raw_store import RawMarketEvent, SqliteRawEventStore

store = SqliteRawEventStore(Path("artifacts/raw_events.db"))
store.append_events([
    RawMarketEvent(
        venue="BINANCE_PERP",
        symbol="BTC-USD-PERP",
        timeframe="1m",
        event_time_ms=1711670400000,
        ingest_seq=1,
        source="binance_ws",
        payload_version="binance_trade_v1",
        payload={"price": "70000.5", "qty": "0.01"},
    )
])

events = store.replay(venue="BINANCE_PERP", symbol="BTC-USD-PERP", timeframe="1m")
```

## Known limitations or TODOs
- Current implementation uses SQLite only; a PostgreSQL/TimescaleDB runtime writer still needs implementation.
- No retention policy or partition lifecycle automation yet.
- Replay cursor/checkpoint support is not implemented.
- No WAL-based throughput tuning yet for high-frequency live ingestion.
