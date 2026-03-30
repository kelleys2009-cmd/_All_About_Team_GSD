# Team GSD Shared Code Modules

## Market Data

`market_data/normalization.py`
- Deterministic OHLCV normalization contract.

`market_data/raw_store.py`
- Raw event persistence and deterministic replay primitives.
- Includes local SQLite writer and TimescaleDB DDL contract helper.

## Tests

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_normalization.py tests/test_raw_store.py tests/test_backtesting.py
```
