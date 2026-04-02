# Bitcoin Power Law: First Research Draft (BBR Report #1)
Date: 2026-04-01

## Executive Summary
I tested a Bitcoin power-law model using long-horizon USD price history and found a strong in-sample log-log fit (R^2 = 0.960), but the specific claim that price reliably doubles every 13% of Bitcoin's lifespan is only partially supported. Across 14 annual start windows, the median 13%-lifespan return was 1.75x, and only 42.9% of windows reached >=2.0x. As of 2026-03-31, BTC at $66,694 sits around the 18.0th percentile of model residuals and about 38.3% below the fitted median trajectory. A quantile-band deployment concept is promising as a slow-turnover regime/value filter, but confidence is medium because model risk and endpoint sensitivity are material.

## a) Title
The Bitcoin Power-Law Corridor as a Regime-Aware Valuation and Positioning Filter

## b) One-Paragraph Summary
This study evaluates whether BTC/USD follows a power-law relationship with network age and whether that structure can be converted into a tradable, subscriber-usable signal. I fit log(price) on log(days since genesis) and construct empirical quantile corridors from residuals to classify valuation regimes (deep discount, neutral, euphoric). The fitted model explains a large share of variance in-sample, but the widely repeated "13% lifespan = 2x" heuristic is inconsistent across cycles. The practical edge appears to be in band-aware risk staging (accumulate in lower corridor, de-risk in upper corridor), not in deterministic doubling timing.

## c) Hypothesis
Bitcoin's adoption/network scaling process creates a long-run power-law price trend where expected returns decay with age rather than remaining exponential. Deviations from this trend are mean-reverting over multi-quarter horizons, so residual quantiles can be used to identify asymmetric risk/reward states. If true, lower-quantile states should offer better forward return-to-risk than upper-quantile states, especially when combined with cycle/risk overlays.

## d) Instruments
- Primary instrument: BTC/USD spot proxy (daily)
- Deployment candidates: BTC perpetuals for tactical expression; spot/ETF for strategic expression
- Venue assumptions: liquid majors (Binance/Coinbase/CME/US ETFs depending on account constraints)

## e) Signal Definition
- Core model: `log(P_t) = a + n*log(D_t) + epsilon_t`, where `D_t` is days since 2009-01-03.
- Fitted exponent: `n = 5.644`.
- Residual quantile corridor: empirical 10/25/50/75/90th percentiles of `epsilon_t`.
- Regime labels:
  - `Deep discount`: residual <= 25th percentile
  - `Neutral`: residual 25th-75th percentile
  - `Euphoric`: residual >= 75th percentile
- Current state (2026-03-31): residual percentile 18.0 (discount/low-mid corridor).

## f) Trade Construction
- Entry: stage long risk when BTC closes at or below model 25th percentile band.
- Exit/de-risk: reduce when BTC closes at or above 75th percentile band.
- Position sizing: 3-tier ladder (e.g., 30%/30%/40%) across lower-band touches, capped by portfolio VaR.
- Risk controls: max single-asset allocation cap, macro-risk kill switch (liquidity/event shocks), and time stop for stale signals.
- Cost assumption in test: 5 bps per side on position flips.

## g) Data Sources
- Price: Blockchain.com `market-price` daily USD series, sample 2010-08-18 to 2026-03-31 (1427 observations).
- On-chain context (Blockchain.com charts): active addresses, hash rate, transaction count.
- BTC genesis anchor: 2009-01-03.
- Halving dates used for interpretation: 2012-11-28, 2016-07-09, 2020-05-11, 2024-04-19.
- Data quality notes:
  - Source is daily aggregate, not exchange-level microstructure.
  - Early-period observations are sparse/noisy relative to modern market structure.
  - External replication with Kaiko/CoinMetrics/CoinGlass recommended before publication.

## Methodology
1. Construct `days_since_genesis` and run OLS on log-log transformed daily data.
2. Compute residual quantiles (10/25/50/75/90) and transform back into price corridors.
3. Validate the "13% lifespan" claim via annual rolling checkpoints (start date -> start + 13% of age).
4. Run a simple corridor strategy: long at <=Q25, flat at >=Q75, with 5 bps per side switching costs.
5. Compare outcomes to buy-and-hold baseline over the same sample.

## Results
### Model Fit and Current Valuation
- Intercept `a = -37.640`
- Exponent `n = 5.644`
- In-sample `R^2 = 0.960`
- Current BTC ($66,694) is 38.3% below fitted median path.

| quantile | model_price | distance_pct |
| --- | --- | --- |
| 10.0 | 57,806 | +15.4% |
| 25.0 | 71,853 | -7.2% |
| 50.0 | 108,120 | -38.3% |
| 75.0 | 184,451 | -63.8% |
| 90.0 | 335,431 | -80.1% |

### 13% Lifespan Validation
- Median multiple across windows: 1.75x
- Mean multiple across windows: 3.02x
- Share of windows with >=2.0x: 42.9%

| start_date | btc_age_days | window_13pct_days | start_price | end_date | end_price | multiple |
| --- | --- | --- | --- | --- | --- | --- |
| 2011-01-01 | 728 | 95 | 0.30 | 2011-04-07 | 0.75 | 2.50x |
| 2012-01-04 | 1096 | 142 | 5.37 | 2012-05-27 | 5.15 | 0.96x |
| 2013-01-02 | 1460 | 190 | 13.52 | 2013-07-13 | 93.99 | 6.95x |
| 2014-01-01 | 1824 | 237 | 732.00 | 2014-08-29 | 506.61 | 0.69x |
| 2015-01-04 | 2192 | 285 | 285.09 | 2015-10-19 | 261.04 | 0.92x |
| 2016-01-03 | 2556 | 332 | 432.76 | 2016-11-30 | 730.02 | 1.69x |
| 2017-01-01 | 2920 | 380 | 964.84 | 2018-01-16 | 13,554.14 | 14.05x |
| 2018-01-04 | 3288 | 427 | 15,039.24 | 2019-03-08 | 3,886.82 | 0.26x |
| 2019-01-03 | 3652 | 475 | 3,931.31 | 2020-04-23 | 7,130.99 | 1.81x |
| 2020-01-02 | 4016 | 522 | 7,175.68 | 2021-06-09 | 33,450.19 | 4.66x |
| 2021-01-04 | 4384 | 570 | 33,000.78 | 2022-07-30 | 23,792.00 | 0.72x |
| 2022-01-03 | 4748 | 617 | 47,327.87 | 2023-09-15 | 26,536.02 | 0.56x |
| 2023-01-02 | 5112 | 665 | 16,613.71 | 2024-10-31 | 72,329.87 | 4.35x |
| 2024-01-01 | 5476 | 712 | 42,249.69 | 2025-12-13 | 90,269.59 | 2.14x |

Interpretation: the doubling heuristic appears regime-dependent rather than invariant; several windows were materially below 1.0x.

### Trading Signal Prototype (Quantile Band Rotation)
- Trades: 6 entries / 5 exits
- Strategy total return: 130616343.2%
- Buy-and-hold total return: 95277700.0%
- Strategy CAGR: 146.4% vs buy-and-hold 141.5%
- Max drawdown: strategy -46.2% vs buy-and-hold -92.4%

Interpretation: in this backtest, corridor filtering improved drawdown and slightly improved CAGR, but this remains an in-sample result requiring adversarial review.

### Network Growth Context (Directional Evidence)
- Active addresses: 2 -> 485131 (242566x)
- Hash rate: 4.97e-08 -> 9.05e+08 (1.82e+16x)
- Transaction count: 109 -> 683419 (6269.9x)

## Quantile Forecast Table (Model-Conditional, Not Price Targets)
| date | days_since_genesis | q10 | q25 | q50 | q75 | q90 |
| --- | --- | --- | --- | --- | --- | --- |
| 2028-01-01 | 6937 | 99,913 | 124,190 | 186,875 | 318,806 | 579,762 |
| 2030-01-01 | 7668 | 175,869 | 218,602 | 328,941 | 561,169 | 1,020,508 |
| 2032-01-01 | 8398 | 293,823 | 365,218 | 549,560 | 937,542 | 1,704,959 |

## h) Test Design
- Frequency: daily
- Estimation window: full available history from 2010-08-18 to 2026-03-31
- Model family: OLS log-log trend with empirical residual quantiles
- Baseline: passive buy-and-hold BTC
- Frictions: 5 bps per side on switching events
- Known limitations: no walk-forward split, no exchange-specific costs, and no robust out-of-sample holdout yet

## i) Performance Summary
Power-law residual bands show potential as a slow-turnover valuation/regime framework, with better drawdown profile than passive exposure in this test. However, headline fit statistics overstate certainty because non-stationary time trends can inflate apparent explanatory power. The strongest practical takeaway is conditional risk budgeting, not deterministic timing.

## j) Failure Analysis
- Structural break risk: regulatory prohibition, protocol exploit, superior alternative monetary network.
- Statistical artifact risk: high `R^2` can arise from shared time trend in log-log transforms.
- Endpoint dependence: band levels and "current percentile" move with sample end date.
- Survivorship bias: BTC is an extreme winner; analog fits on failed assets are needed.
- Tradability mismatch: signal horizon is multi-month to multi-year, not high-frequency alpha.

## k) Deployment Considerations
- Best use: strategic allocation/risk overlay, not standalone short-horizon trading.
- Turnover is low; capacity is high in BTC spot/perp markets.
- Execution complexity is minimal, but governance guardrails (position caps and kill-switches) are required.
- Should be combined with macro/liquidity filters and Chris's adversarial stress tests before publication.

## l) Verdict
Promising (not Ready for implementation review yet). Keep on watchlist pending out-of-sample and adversarial falsification.

## m) Next 3 Actions
1. Run walk-forward and expanding-window tests (pre-2018 fit, 2018-2026 out-of-sample) to evaluate predictive stability.
2. Compare against alternative models (exponential, log-time, piecewise regime models) with equal evaluation protocol.
3. Coordinate with Devin to productionize a reproducible backtest pipeline and with Chris for full falsification pass.

## Implications
For subscribers, the power-law corridor is most useful as a regime map: lower-band zones historically improved long-horizon entry asymmetry, while upper-band zones signaled deteriorating reward-to-risk. This can support a disciplined accumulation/de-risking framework around major cycle extremes. It should not be marketed as a guaranteed doubling clock.

## Confidence Level
**Medium.** Quantitative structure is consistent and internally coherent, but confidence is constrained by in-sample bias, coarse source data, and lack of full out-of-sample and cross-source replication.

## Open Questions
- Does the edge survive strict out-of-sample evaluation and parameter perturbation (+/-20-50%)?
- How sensitive are conclusions to data vendor choice and exchange-specific close definitions?
- Do quantile bands add value beyond simple momentum/volatility filters after equal-cost assumptions?
- How should halving-cycle state and macro liquidity regime be integrated into the signal definition?
- Which conditions should formally invalidate use of this framework in production?
