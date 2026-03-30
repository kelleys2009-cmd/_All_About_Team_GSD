# Team GSD Shared Code Modules

## Market Data

`market_data/normalization.py`
- Deterministic OHLCV normalization contract.

`market_data/raw_store.py`
- Raw event persistence and deterministic replay primitives.
- Includes local SQLite writer, Postgres/Timescale runtime writer, and schema helpers.
- Includes replay checkpoint persistence for long-running ingestion jobs.

## Tests

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_normalization.py tests/test_raw_store.py tests/test_backtesting.py
```
