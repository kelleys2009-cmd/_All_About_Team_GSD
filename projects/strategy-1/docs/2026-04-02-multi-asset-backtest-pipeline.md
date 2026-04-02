# Multi-Asset Backtest Pipeline (BTC/ETH/SOL/XRP/DOGE)
Date: 2026-04-02
Author: Devin Sailer

## Summary
Built a reproducible walk-forward backtest pipeline for 5-coin research (BTC, ETH, SOL, XRP, DOGE) using shared Team GSD backtesting modules, with deterministic per-run artifacts and manifest metadata.

Why: TEA-78 requested a concrete, repeatable research pipeline with clear data ingestion and cost assumptions so research outputs are comparable across reruns.

## Implementation details
- Entry command: `projects/strategy-1/code/run_multi_asset_backtest.py`
- Pipeline package: `projects/strategy-1/code/multi_asset_backtest/`
- Shared dependencies reused from `code/backtesting/` (`BacktestEngine`, `WalkForwardRunner`, IO artifact writer).

Data ingestion spec:
- Input directory: `--dataset-dir` containing one CSV per asset named `<ASSET>.csv`.
- Supported assets by default: `BTC`, `ETH`, `SOL`, `XRP`, `DOGE`.
- Required CSV columns: `timestamp`, `close`.
- `timestamp` must be ISO-8601 parseable by Python `datetime.fromisoformat`.
- `close` must parse as float.
- Minimum rows per file: 2.
- Validation is strict and fails fast before backtest execution.

Cost/slippage model assumptions:
- BTC: commission `$0.50`/trade, slippage `3.0 bps`
- ETH: commission `$0.50`/trade, slippage `3.0 bps`
- SOL: commission `$0.50`/trade, slippage `5.0 bps`
- XRP: commission `$0.50`/trade, slippage `5.0 bps`
- DOGE: commission `$0.50`/trade, slippage `8.0 bps`
- Unknown assets fall back to commission `$0.50` and slippage `8.0 bps`

Reproducibility controls:
- Per-run manifest written to `run_manifest.json`.
- Manifest includes: UTC generation time, assets, strategy modules, walk-forward params, file hashes (SHA-256), row counts, cost model used, and current git `HEAD` (if available).
- Combined table output written to `combined_strategy_summary.csv`.
- Per-asset output folders include `strategy_summary.json`, `strategy_summary.csv`, and `walkforward_windows.json`.

Default strategy behavior:
- If no strategy is provided, pipeline uses baseline buy-and-hold strategy module at `multi_asset_backtest/buy_hold_strategy.py`.

Testing:
- Added `projects/strategy-1/code/tests/test_multi_asset_pipeline.py`.
- Test covers input normalization and full pipeline artifact generation for all 5 assets using synthetic data.

## Usage
From repo root (`~/Desktop/Team GSD`):

```bash
PYTHONPATH=code:projects/strategy-1/code python3 -m unittest \
  projects/strategy-1/code/tests/test_multi_asset_pipeline.py
```

Run the pipeline:

```bash
python3 projects/strategy-1/code/run_multi_asset_backtest.py \
  --dataset-dir projects/strategy-1/code/data/prices \
  --output-dir projects/strategy-1/code/artifacts/multi_asset_run_001 \
  --train-size 365 \
  --test-size 90 \
  --step-size 30
```

Optional custom strategy modules can be repeated:

```bash
python3 projects/strategy-1/code/run_multi_asset_backtest.py \
  --dataset-dir projects/strategy-1/code/data/prices \
  --output-dir projects/strategy-1/code/artifacts/multi_asset_custom \
  --train-size 365 --test-size 90 --step-size 30 \
  --strategy projects/strategy-1/code/multi_asset_backtest/buy_hold_strategy.py
```

Artifact format:
- `combined_strategy_summary.csv`: one row per `(asset, strategy)` with average return/sharpe/drawdown, trades, windows, and applied costs.
- `run_manifest.json`: reproducibility metadata and source hash ledger.
- `/<ASSET>/strategy_summary.{json,csv}` and `/<ASSET>/walkforward_windows.json` for detailed per-asset metrics.

## Known limitations or TODOs
- Current bar schema is close-only; no OHLCV, spread, or depth features yet.
- Strategy API currently supports only discrete target positions `-1/0/1`.
- Cost model is static per asset; should be upgraded to dynamic spread/volatility-aware costs.
- No exchange-specific fee tier modeling or funding-rate impact.
- No native portfolio-level netting across assets yet (runs are independent per asset, then summarized).
- Next iteration should include fixture market datasets in-repo (or data fetch adapter) for standardized benchmark runs.
