# TEA-30 Batch-2 Backtests: Vol-Managed TSMOM + BAB Proxy

## Scope
This run executes the [TEA-30](/TEA/issues/TEA-30) batch-2 candidates selected from [TEA-28](/TEA/issues/TEA-28):
- `vol_managed_tsmom_proxy`
- `bab_proxy_single_asset`

Baseline for comparison:
- `buy_and_hold`

## Engine and Protocol Alignment
- Engine base: `code/backtesting/` from [TEA-26](/TEA/issues/TEA-26)
- Walk-forward shape: `train=40`, `test=20`, `step=10` (same as [TEA-27](/TEA/issues/TEA-27))
- Cost model: `commission=1.0`, `slippage_bps=2.0`
- Dataset: `research/sample_prices.csv`

## Reproducible Commands
```bash
PYTHONPATH=code python3 -m unittest discover -s code/tests -v

PYTHONPATH=code python3 code/run_backtests.py \
  --prices-csv research/sample_prices.csv \
  --strategy strategy/scaffold_strategy.py \
  --strategy strategy/vol_managed_tsmom_strategy.py \
  --strategy strategy/bab_proxy_strategy.py \
  --train-size 40 \
  --test-size 20 \
  --step-size 10 \
  --commission 1.0 \
  --slippage-bps 2.0 \
  --output-dir artifacts/backtests/tea30_batch2

python3 code/generate_candidate_vs_baseline_table.py \
  --summary-json artifacts/backtests/tea30_batch2/strategy_summary.json \
  --baseline buy_and_hold \
  --out-csv artifacts/backtests/tea30_batch2/candidate_vs_baseline.csv \
  --out-md artifacts/backtests/tea30_batch2/candidate_vs_baseline.md \
  --data-window "2025-02-10 to 2025-03-11 (WF test windows)"
```

## Results Snapshot
From `artifacts/backtests/tea30_batch2/strategy_summary.json`:

| Strategy | Avg Total Return | Avg Sharpe | Avg Max Drawdown | Total Trades |
|---|---:|---:|---:|---:|
| buy_and_hold | 0.00012424 | 15.011604 | -0.00000800 | 2 |
| vol_managed_tsmom_proxy | 0.00008173 | 8.836091 | -0.00001027 | 2 |
| bab_proxy_single_asset | 0.00000066 | 0.060588 | -0.00001271 | 6 |

Candidate deltas vs baseline (`candidate_vs_baseline.md`):
- `vol_managed_tsmom_proxy`: return `-0.000043`, Sharpe `-6.175513`, drawdown `-0.000002`
- `bab_proxy_single_asset`: return `-0.000124`, Sharpe `-14.951016`, drawdown `-0.000005`

## Simplifications and Limitations
- `vol_managed_tsmom_proxy` is a discrete-position approximation because the current engine supports `{-1,0,1}` position targets only (no continuous leverage sizing).
- `bab_proxy_single_asset` is **not** full BAB. True BAB needs a cross-sectional long-short basket with beta-neutral weighting and borrow/financing treatment. Current engine/data are single-asset close-only.
- No borrow fees, funding rates, or intrabar execution microstructure in this run.

## Recommendation
- `vol_managed_tsmom_proxy`: **Iterate**
  - Rationale: closer to baseline than BAB proxy and directionally aligned with TEA-28 thesis, but still under baseline on return and Sharpe in this sample.
- `bab_proxy_single_asset`: **Reject for now** (as implemented)
  - Rationale: proxy materially underperforms baseline and does not represent true BAB mechanics.

Next requirement before another BAB decision: expand engine/data to multi-asset cross-sectional inputs and borrow/financing cost modeling.

## Artifacts
- `artifacts/backtests/tea30_batch2/strategy_summary.json`
- `artifacts/backtests/tea30_batch2/strategy_summary.csv`
- `artifacts/backtests/tea30_batch2/walkforward_windows.json`
- `artifacts/backtests/tea30_batch2/candidate_vs_baseline.csv`
- `artifacts/backtests/tea30_batch2/candidate_vs_baseline.md`
