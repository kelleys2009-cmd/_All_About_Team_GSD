# Crypto Power Law Cross-Asset Review (BTC, ETH, XRP, SOL, DOGE)
Date: 2026-04-06

## Executive Summary
Using daily USD closes through 2026-04-06, Bitcoin shows the strongest power-law fit among the five assets (`R^2 = 0.921`, exponent `b = 5.92`), while XRP is weakest (`R^2 = 0.289`). Under the same log-log specification, implied current doubling cadence spans from ~687 days (DOGE) to ~2,894 days (XRP), showing that the "age-based doubling" narrative is highly asset-specific outside BTC. Current model residuals place BTC near the 5th percentile versus its fitted trend (price at `0.52x` model fair), suggesting deep-trend discount if the BTC power-law structure remains valid. Cross-asset evidence supports using power law as a low-frequency valuation/regime feature for BTC, but not as a standalone timing model for non-BTC assets without additional factors.

## Data Sources
- Price data: Yahoo Finance daily candles via `yfinance` (`BTC-USD`, `ETH-USD`, `XRP-USD`, `SOL-USD`, `DOGE-USD`), pulled on 2026-04-06.
- Time period covered by available market data in this pull:
  - BTC: 2014-09-17 to 2026-04-06 (`n=4,219`)
  - ETH/XRP/DOGE: 2017-11-09 to 2026-04-06 (`n=3,070` each)
  - SOL: 2020-04-10 to 2026-04-06 (`n=2,187`)
- Genesis anchors used for age-in-days term:
  - BTC 2009-01-03, ETH 2015-07-30, XRP 2012-06-02, SOL 2020-03-16, DOGE 2013-12-06.
- Internal references:
  - Roy prior BTC work (`2026-03-31` and `2026-04-05` drafts in Strategy #1 research)
  - Chris macro context (`agents/chris-bunge/market-reports/2026-04-04-btc-power-law-v2-adversarial-review.md`)

## Methodology
- For each asset, fit OLS on logs:
  - `ln(price_t) = a + b * ln(age_days_t) + e_t`
  - `age_days_t` is days since chain genesis anchor.
- Computed per asset:
  - Exponent (`b`), intercept (`a`), `R^2`
  - Implied age increase required for 2x price: `2^(1/b) - 1`
  - Implied days-to-double at current age
  - Latest price vs fitted fair value (`price_to_fair`)
  - Residual percentile and residual quantile multipliers (`Q10`, `Q50`, `Q90` of `exp(residual)`)
- Additional context: trailing realized returns over 365/730/1095 days.
- Reproducibility artifacts:
  - `code/market_data/power_law_cross_asset_report.py`
  - `artifacts/tea-88/2026-04-06-power-law-cross-asset-metrics.csv`
  - `artifacts/tea-88/2026-04-06-power-law-cross-asset-returns.csv`
  - `artifacts/tea-88/2026-04-06-power-law-cross-asset-summary.json`

## Results

| Asset | Obs | Exponent b | R^2 | Implied Days to Double (Now) | Price / Model Fair | Residual Percentile |
|---|---:|---:|---:|---:|---:|---:|
| BTC | 4,219 | 5.917 | 0.921 | 783 | 0.524x | 4.9% |
| ETH | 3,070 | 2.075 | 0.583 | 1,548 | 0.604x | 24.6% |
| XRP | 3,070 | 1.531 | 0.289 | 2,894 | 1.231x | 65.0% |
| SOL | 2,187 | 1.507 | 0.692 | 1,291 | 0.465x | 23.5% |
| DOGE | 3,070 | 4.882 | 0.689 | 687 | 0.312x | 14.1% |

Residual band widths (multipliers around fitted trend) indicate very large dispersion for non-BTC assets (example: DOGE `Q10=0.236x`, `Q90=4.575x`).

Trailing realized returns:

| Asset | 1Y | 2Y | 3Y |
|---|---:|---:|---:|
| BTC | -17.1% | +2.0% | +146.8% |
| ETH | +18.2% | -35.7% | +13.9% |
| XRP | -37.3% | +128.7% | +166.9% |
| SOL | -31.9% | -53.1% | +297.2% |
| DOGE | -45.3% | -47.9% | +8.3% |

## Implications
- BTC: power law remains statistically strong enough for strategic regime framing (valuation envelope, risk throttles), consistent with Chris's macro framing that structural trend context is useful but cycle shocks dominate execution windows.
- ETH/SOL/DOGE: moderate fits with high residual dispersion imply power law alone is insufficient for signal deployment; needs blend with liquidity, momentum, and macro regime filters.
- XRP: weak fit (`R^2=0.289`) indicates this framework should not be a primary valuation anchor for XRP strategy decisions.
- For Strategy #1 platformization: coordinate with Devin to backtest this only as a low-frequency feature (position-size scalar or exposure cap input), not a direct entry/exit trigger.

## Confidence Level
**Medium.**
- Strength: Computation is reproducible and internally consistent across all five assets with explicit assumptions.
- Limitation: Yahoo history does not reach genesis-era trading for most assets, which can bias exponent estimates and cross-asset comparability.
- Limitation: Single-factor log-log OLS ignores regime changes, listing-era microstructure effects, and market structure breaks.

## Open Questions
- Should we rerun this with multi-vendor data (CryptoCompare/CoinMetrics/exchange composites) to reduce vendor-history bias?
- Should BTC use quantile regression channels (not just OLS + residual quantiles) for production risk bands?
- For ETH/SOL/DOGE, does adding macro and liquidity covariates materially improve out-of-sample regime classification vs power-law-only baseline?
- Do we want Jay to run an adversarial replication with alternate anchors/specifications before this is promoted into Strategy #1 signal stack?
