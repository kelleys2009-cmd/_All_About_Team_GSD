# Power Law Comparison Across Top-50 Crypto Market Cap Universe
Date: 2026-04-07

## Executive Summary
I screened a top-50 market-cap crypto universe to find assets whose early lifecycle price path most closely resembles BTC under a power-law style lens. After data-quality filtering, 38 symbols were analyzable and only 2 met the similarity thresholds (`R^2 >= 0.60` and early-path correlation vs BTC `>= 0.70`): `LINK` and `LEO`. `LINK` ranked strongest overall (`R^2=0.673`, early-path correlation `0.765`, exponent distance to BTC `0.502`), while `OKB` had the highest non-BTC `R^2` (`0.809`) but weaker BTC path similarity. Result: very few large-cap assets currently show BTC-like early power-law path behavior under this specification.

## Data Sources
- Universe selection: CoinGecko public API `coins/markets` endpoint (top 50 by USD market cap), fetched on 2026-04-07.
- Price histories: Yahoo Finance daily close (`<SYMBOL>-USD`) via `yfinance`, fetched on 2026-04-07.
- Coverage:
- 50 symbols requested.
- 44 returned >=365 daily observations in Yahoo.
- 38 remained after stablecoin-peg exclusion (`latest_price` in `[0.97, 1.03]` removed).
- BTC reference sample: 2014-09-17 to 2026-04-08 (`n=4,221`).
- Produced artifacts:
- `agents/roy/research/data/2026-04-07-power-law-comparison-top50-metrics.csv`
- `agents/roy/research/data/2026-04-07-power-law-comparison-top50-candidates.csv`
- `agents/roy/research/data/2026-04-07-power-law-comparison-top50-meta.json`

## Methodology
- For each asset, fit log-log OLS using trading-age indexing:
- `ln(price_t) = a + b * ln(days_since_first_observation_t)`.
- Compute per asset:
- Power-law fit quality (`R^2`).
- Exponent `b` and absolute exponent distance to BTC.
- Early lifecycle path similarity to BTC over first `min(730, len(asset), len(BTC))` days:
- Correlation of normalized log paths `corr(log(P_t/P_0)_asset, log(P_t/P_0)_BTC)`.
- RMSE between those same normalized log paths.
- Composite ranking score:
- `0.45*R^2 + 0.35*early_corr + 0.20*(1/(1+exp_distance_to_btc))`.
- Candidate gate for “BTC-like” behavior:
- `R^2 >= 0.60` and `early_corr >= 0.70` (non-BTC assets only).

## Results
### BTC reference
- BTC fit under this spec: `R^2=0.782`, exponent `b=1.700`.

### Top non-BTC assets by composite score

| Rank | Symbol | Obs | R^2 | Exponent b | |b-BTC| | Early Corr vs BTC | Early RMSE | Score |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | LINK | 3,072 | 0.673 | 1.197 | 0.502 | 0.765 | 1.350 | 0.704 |
| 2 | OKB | 2,535 | 0.809 | 1.069 | 0.631 | 0.607 | 1.370 | 0.699 |
| 3 | LEO | 2,514 | 0.659 | 0.617 | 1.083 | 0.807 | 0.507 | 0.675 |
| 4 | SOL | 2,189 | 0.677 | 1.319 | 0.381 | 0.595 | 3.479 | 0.657 |
| 5 | LTC | 4,221 | 0.637 | 1.135 | 0.565 | 0.693 | 0.360 | 0.657 |

### Assets passing BTC-like candidate gate
- `LINK`: passes (`R^2=0.673`, early corr `0.765`).
- `LEO`: passes (`R^2=0.659`, early corr `0.807`).
- Candidate count: `2 / 38` analyzable non-stablecoin assets (`5.3%`).

### Notable non-candidates
- `OKB`: high fit quality (`R^2=0.809`) but early BTC-path correlation below gate (`0.607`).
- `BNB`: moderate fit (`R^2=0.718`) but low early BTC-path correlation (`0.389`).
- `DOGE`: did not make top cohort under this lifecycle-normalized spec.

## Implications
- A broad top-50 scan does not support a strong claim that “many” large-cap coins follow BTC-like early power-law behavior; evidence is sparse under consistent scoring.
- For Strategy work, `LINK` and `LEO` are the best next-step candidates for deeper adversarial validation rather than immediate signal deployment.
- This aligns with Chris’s broader macro caution from prior BTC power-law reviews: structural trend signals can be useful context, but asset-specific regime behavior and idiosyncratic shocks dominate implementation risk.
- Recommended coordination with Devin: wire this scan as a periodic feature-generation job and backtest any candidate-based allocation rule against baseline BTC-only and equal-weight alternatives.

## Confidence Level
**Medium.**
- Positive: fully reproducible artifacts and explicit quantitative filters.
- Limitations: ticker mapping from CoinGecko symbols to Yahoo symbols is imperfect; some top-50 entries were unavailable/mismatched (`FIGR_HELOC`, `USYC`, `TAO` pull failure).
- Limitations: using first Yahoo observation as lifecycle anchor is a practical proxy, not true chain genesis for every asset.

## Open Questions
- Should we replace Yahoo with a crypto-native vendor (CoinMetrics/CryptoCompare/Kaiko) to improve symbol coverage and listing-history integrity?
- Should candidate gating include a maximum RMSE threshold (not just correlation) to reduce false positives from scale differences?
- Should we rerun with chain-genesis anchors per asset and compare rank stability vs listing-age anchors?
- Do we want a monthly automated rerun to detect emerging BTC-like candidates as the top-50 membership changes?
