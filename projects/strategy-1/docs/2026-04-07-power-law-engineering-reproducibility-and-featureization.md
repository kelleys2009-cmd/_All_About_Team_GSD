# Power Law: Engineering Reproducibility and Featureization
Date: 2026-04-07
Author: Devin Sailer

## Executive Summary
Define a production-ready path to make power-law research reproducible and safely consumable by Strategy #1 as a low-frequency feature.

What was decided and why:
- Use an immutable, hashed artifact flow for power-law runs so every figure and feature can be traced to exact source data, code revision, and parameters.
- Keep power-law outputs in the research/feature layer (daily or slower cadence), not in execution hot paths.
- Introduce guardrails that block stale, low-fit, or structurally unstable power-law features before they influence position sizing.

## Current Code/Data Pipeline Inventory
Current relevant files and modules:
- Shared market-data and research module:
  - `~/Desktop/Team GSD/code/market_data/power_law_cross_asset_report.py`
- Shared backtesting framework:
  - `~/Desktop/Team GSD/code/backtesting/{engine.py,io.py,strategy.py,types.py,walkforward.py}`
- Strategy #1 pipeline entrypoints:
  - `~/Desktop/Team GSD/projects/strategy-1/code/run_multi_asset_backtest.py`
  - `~/Desktop/Team GSD/projects/strategy-1/code/multi_asset_backtest/pipeline.py`
  - `~/Desktop/Team GSD/projects/strategy-1/code/multi_asset_backtest/buy_hold_strategy.py`
  - `~/Desktop/Team GSD/projects/strategy-1/code/tests/test_multi_asset_pipeline.py`
- Existing strategy docs:
  - `~/Desktop/Team GSD/projects/strategy-1/docs/2026-04-02-multi-asset-backtest-pipeline.md`

Current state observations:
- The power-law generator already produces deterministic CSV/JSON artifacts from a fixed coin universe (`BTC`, `ETH`, `XRP`, `SOL`, `DOGE`) and explicit genesis-date assumptions.
- The multi-asset backtest pipeline already records reproducibility metadata (`run_manifest.json`) including source hashes and git HEAD.
- There is no formal bridge yet from power-law report artifacts into a standardized feature table consumed by strategy logic.
- Data pull uses `yfinance`; vendor/source changes are an explicit reproducibility risk unless snapshotting is enforced.

## Reproducibility Runbook
### 1. Pin environment and dependencies
From repo root (`~/Desktop/Team GSD`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install numpy pandas yfinance
```

Recommendation:
- Introduce pinned dependency files (`requirements-lock.txt`) for deterministic reruns.

### 2. Run cross-asset power-law generation

```bash
cd ~/Desktop/Team\ GSD
python3 code/market_data/power_law_cross_asset_report.py
```

Current default output location from script:
- `artifacts/tea-88/2026-04-06-power-law-cross-asset-metrics.csv`
- `artifacts/tea-88/2026-04-06-power-law-cross-asset-panel.csv`
- `artifacts/tea-88/2026-04-06-power-law-cross-asset-returns.csv`
- `artifacts/tea-88/2026-04-06-power-law-cross-asset-summary.json`

### 3. Freeze a run snapshot
For each completed run, persist:
- Input universe and genesis date mapping.
- Raw downloaded daily close series per ticker.
- Artifact checksums (SHA-256).
- Script commit SHA (`git rev-parse HEAD`).
- UTC run timestamp.

Suggested command pattern:

```bash
mkdir -p projects/strategy-1/code/artifacts/power_law_runs/run_$(date -u +%Y%m%dT%H%M%SZ)
cp -R artifacts/tea-88/* projects/strategy-1/code/artifacts/power_law_runs/run_$(date -u +%Y%m%dT%H%M%SZ)/
```

Implementation note:
- Use one run directory variable in shell to avoid timestamp mismatch between commands.

### 4. Build canonical feature table from summary
Target output table (daily cadence):
- Key columns: `date`, `symbol`
- Feature columns: `price_to_fair`, `residual_percentile`, `exponent_b`, `r2`, `implied_days_to_double_now`
- Metadata columns: `feature_version`, `source_run_id`, `source_git_head`, `generated_at_utc`

Storage target:
- `~/Desktop/Team GSD/projects/strategy-1/code/artifacts/features/power_law_features_daily.csv`

### 5. Integrate into Strategy #1 backtest path
- Add a feature loader in `projects/strategy-1/code/multi_asset_backtest/pipeline.py` to join feature values by `(date, asset)`.
- Keep featureized strategy modules isolated under:
  - `projects/strategy-1/code/multi_asset_backtest/strategies/`
- Preserve baseline comparability by always running:
  - baseline (`buy_and_hold`), and
  - featureized strategy in same walk-forward windows.

## Validation and Monitoring Checks
Hard checks before feature publication:
- Schema check: all required columns present and typed.
- Freshness check: latest feature date must be within 48h of expected close.
- Fit-quality check: minimum acceptable `r2` per symbol (recommended initial floor `>= 0.85`, tune by asset).
- Drift check: day-over-day delta bounds for `exponent_b` and `price_to_fair`.
- Completeness check: all required symbols present (`BTC`, `ETH`, `SOL`, `XRP`, `DOGE`).

Operational monitoring recommendations:
- Emit structured logs for each run with run id, symbol count, pass/fail counts.
- Track time-series metrics:
  - `power_law_run_success{symbol}`
  - `power_law_feature_staleness_hours{symbol}`
  - `power_law_r2{symbol}`
  - `power_law_price_to_fair{symbol}`
- Alert on:
  - run failure,
  - stale feature table,
  - missing symbol,
  - `r2` below floor,
  - extreme `price_to_fair` outlier outside configured safety band.

## Featureization Plan (low-frequency scaler, guardrails)
Design objective:
- Convert power-law outputs into a low-frequency position scaler that modulates risk budget, not raw entry/exit triggers.

Proposed scaler (`0.5x` to `1.5x` risk multiplier):
1. Compute valuation signal from `price_to_fair` and `residual_percentile`.
2. Normalize signal per asset using robust trailing percentiles.
3. Clip to safety range and map to multiplier band (`0.5` to `1.5`).
4. Apply only on daily rebalance boundary.

Guardrails:
- Disable scaler if feature row is stale or missing.
- Disable scaler if fit-quality (`r2`) below threshold.
- Cap step-change in multiplier (for example max `0.10` change per rebalance).
- Force neutral multiplier (`1.0`) during major data integrity incidents.

Backtest protocol:
- A/B compare baseline vs featureized strategy with identical windows/costs.
- Require uplift criteria on risk-adjusted return and drawdown stability before enabling live candidate mode.

## Implementation Risks
- Vendor instability risk: `yfinance` data revisions can alter historical outputs across reruns.
- Specification fragility: exponent/intercept may be unstable for newer assets with short histories.
- Regime dependency risk: model fit can degrade in macro/structure shifts.
- Leakage risk: incorrect joins or as-of logic can introduce look-ahead bias.
- Operational risk: silent stale-feature usage if freshness checks are not hard-fail.

## Recommended Next Engineering Steps
1. Add `power_law_feature_builder.py` under `code/market_data/` to emit canonical daily feature table with manifest/hash metadata.
2. Add `power_law_feature_guardrails.py` for validation checks and machine-readable pass/fail report.
3. Add unit tests for feature schema, as-of joins, and guardrail behavior under stale/missing data.
4. Add integration test in `projects/strategy-1/code/tests/` that executes baseline + featureized walk-forward and verifies artifact parity.
5. Add scheduled job wiring (daily) with alert routing and runbook link.

## Implementation details
Key design choices:
- Leverage existing reproducibility patterns from `multi_asset_backtest/pipeline.py` (`run_manifest.json`, source hashing, commit capture).
- Keep power-law feature generation decoupled from execution OMS/trading stack to protect latency-sensitive paths.
- Prefer explicit, versioned feature artifacts over implicit on-demand recomputation.

Dependencies:
- Python runtime with `numpy`, `pandas`, `yfinance`.
- Existing Team GSD backtesting modules under `~/Desktop/Team GSD/code/backtesting/`.

## Usage
1. Generate/re-generate power-law research artifacts:

```bash
cd ~/Desktop/Team\ GSD
python3 code/market_data/power_law_cross_asset_report.py
```

2. Run Strategy #1 baseline backtest for comparison:

```bash
python3 projects/strategy-1/code/run_multi_asset_backtest.py \
  --dataset-dir projects/strategy-1/code/data/prices \
  --output-dir projects/strategy-1/code/artifacts/multi_asset_run_001 \
  --train-size 365 \
  --test-size 90 \
  --step-size 30
```

3. Validate pipeline tests:

```bash
PYTHONPATH=code:projects/strategy-1/code python3 -m unittest \
  projects/strategy-1/code/tests/test_multi_asset_pipeline.py
```

## Known limitations or TODOs
- Canonical power-law feature table builder is not implemented yet (this document specifies the design path).
- Current power-law script writes to a date-stamped path in `artifacts/tea-88`; should be parameterized for run ids and environments.
- No lockfile/pinned environment has been committed yet for fully deterministic dependency resolution.
- No production scheduler/alert pipeline has been attached yet for daily power-law feature generation.
