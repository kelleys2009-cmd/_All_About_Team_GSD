# Power Law: Macro and Regime Context (TEA-92)
Date: 2026-04-06

## Executive Summary
Power-law valuation framing is most useful for BTC when global liquidity is not tightening and credit stress is contained; it is least reliable during dollar spikes, widening credit spreads, and market-structure shocks. In 2018-01-01 to 2026-04-06 data, BTC forward 90-day returns are materially weaker when high-yield spreads widen (+50 bps in 30 days) and when the trade-weighted dollar strengthens (>3% in 60 days). The practical implication is that Strategy #1 should treat power law as a slow-moving structural anchor, then gate exposure with macro and microstructure regime filters rather than using power law as a standalone timing signal. Cross-team dependency: Roy's cross-asset expansion ([TEA-91](/TEA/issues/TEA-91)) and Devin's featureization runbook ([TEA-93](/TEA/issues/TEA-93)) should consume this regime map directly.

## Context
This memo addresses when power-law assumptions are likely to hold versus break for crypto assets, with BTC as the calibration anchor for Strategy #1. The scope is macro regime state, liquidity plumbing, and market-structure break conditions that can overwhelm long-horizon log-log trend fitting. The objective is not to disprove power laws; it is to define operating conditions under which the model has acceptable decision value.

## Data/Evidence
### Sources
- BTC spot history (`BTC-USD`) via Yahoo Finance/yfinance (downloaded 2026-04-06): https://finance.yahoo.com/quote/BTC-USD/
- U.S. 10Y real yield (`DFII10`, FRED): https://fred.stlouisfed.org/series/DFII10
- Federal Reserve total assets (`WALCL`, FRED/H.4.1 proxy): https://fred.stlouisfed.org/series/WALCL
- U.S. M2 (`M2SL`, FRED): https://fred.stlouisfed.org/series/M2SL
- ICE BofA U.S. High Yield OAS (`BAMLH0A0HYM2`, FRED): https://fred.stlouisfed.org/series/BAMLH0A0HYM2
- Broad trade-weighted U.S. dollar (`DTWEXBGS`, FRED): https://fred.stlouisfed.org/series/DTWEXBGS
- Aggregate stablecoin supply history (DeFiLlama endpoint): https://stablecoins.llama.fi/stablecoincharts/all
- SEC spot-BTC ETP approval order (Release No. 34-99306, January 10, 2024): https://www.sec.gov/files/rules/sro/nysearca/2024/34-99306.pdf
- SEC complaint regarding FTX/Alameda conduct (December 13, 2022; event context for 2022 break regime): https://www.sec.gov/files/litigation/complaints/2022/comp-pr2022-219.pdf

### Quantified Regime Tests (sample: 2018-01-01 to 2026-04-06)
Forward return metric: BTC 90-day return.

- Real yield falling regime (`DFII10` down >10 bps over 20 trading days):
  - `n=721`, median +10.6%, hit rate 61.3%.
- Real yield rising regime (`DFII10` up >10 bps over 20 trading days):
  - `n=778`, median +0.7%, hit rate 50.9%.
- HY spread widening stress (`BAMLH0A0HYM2` up >50 bps over 30 days):
  - `n=281`, median -14.7%, hit rate 25.6%.
- HY spread tightening (`BAMLH0A0HYM2` down >30 bps over 30 days):
  - `n=624`, median +11.0%, hit rate 63.5%.
- Dollar strengthening (`DTWEXBGS` up >3% over 60 days):
  - `n=250`, median -11.5%, hit rate 23.2%.
- Dollar weakening (`DTWEXBGS` down >3% over 60 days):
  - `n=231`, median +16.6%, hit rate 65.4%.

Monthly correlation check (same sample; BTC 3M forward returns):
- vs real-yield change: `-0.31`
- vs HY-spread change: `-0.18`
- vs dollar change: `-0.37`
- vs Fed balance-sheet 3M change: `+0.03` (weak in this simple spec)

Event windows (BTC close-based):
- FTX failure window (`2022-11-08`): 7D `-8.9%`, 30D `-7.0%`, 90D `+22.8%`.
- U.S. spot ETF launch (`2024-01-11`): 7D `-11.0%`, 30D `+3.0%`, 90D `+52.2%`.
Interpretation: structural shocks can cause short-horizon dislocations around long-run trend, including both downside breaks and fast repricing rebounds.

## Analysis
## Macro Regime Framework
Power-law trend adherence is strongest when three conditions co-occur: disinflationary real-rate pressure, easing/risk-on credit conditions, and non-strengthening dollar regimes. The data suggests credit-spread and dollar regimes dominate near-term deviations, while Fed balance-sheet direction alone is too blunt to time returns.

## Liquidity and Market-Structure Dependencies
Power-law assumptions implicitly require durable market access and reflexive risk capacity. In practice, that means:
- Fiat/stablecoin conversion remains functional and deep.
- Derivatives basis/funding is not in forced unwind mode.
- Counterparty confidence is intact (custody, exchange solvency, collateral valuation).

When these conditions fail, price can gap far from smooth age-based trend estimates, even if the long-run curve later reasserts.

## Failure Regimes / Break Conditions
Most relevant break regimes for Strategy #1:
- Macro stress: rapid HY spread widening and dollar upshifts.
- Policy shock: abrupt regulatory/legal constraints that alter access or leverage.
- Microstructure shock: major venue/counterparty failures and liquidation cascades.
- Data-construction risk: truncated history, survivorship bias, and anchor sensitivity in cross-asset fits.

## Scenario Analysis
### Scenario A: Disinflation + dollar softness + tighter credit spreads
Expected behavior: power-law residual mean reversion has higher reliability; allow wider participation but keep volatility caps.

### Scenario B: Sticky inflation + rising real yields + strong dollar
Expected behavior: power-law "cheapness" can stay cheap longer; reduce gross exposure and require confirmation from momentum/liquidity metrics.

### Scenario C: Credit stress spike (HY widening >50 bps in 30 days)
Expected behavior: highest probability of trend breaks and deep undercuts; power-law should be treated as background valuation only, not timing.

### Scenario D: Structural-positive catalyst (e.g., access expansion like ETF rails)
Expected behavior: short-term whipsaw around event date, followed by possible fast repricing; implement staggered entry logic and avoid single-point triggers.

## How This Should Be Used in Strategy #1
- Use power law as a low-frequency valuation/regime feature, not a direct entry rule.
- Add hard regime gates before risk-on sizing:
  - HY spread change filter.
  - Dollar trend filter.
  - Real-yield trend filter.
- Connect to Devin's implementation track ([TEA-93](/TEA/issues/TEA-93)) as pre-trade risk gates and to Roy's cross-asset work ([TEA-91](/TEA/issues/TEA-91)) as asset-selection constraints (higher confidence on BTC than non-BTC until validated).
- Treat market-structure events as override states where model residuals are informational but not tradable by themselves.

## Risks / Limitations
- Regime thresholds are heuristic and can be overfit if optimized excessively.
- BTC-based macro mapping may transfer poorly to thinner alt markets.
- FRED macro series publish with lags/revisions; live-trading implementation needs nowcast proxies.
- Stablecoin aggregate growth signal is noisy in this sample and not sufficient alone.

## Implications
For Team GSD and BartBotResearch.com publication quality, the defensible claim is conditional: power-law framing is useful under specific macro/liquidity conditions, and fragile during stress regimes. This increases research credibility versus unconditional claims and gives the platform a concrete policy for exposure throttling during breaks. Product direction should favor a modular regime stack where power law is one layer among macro, liquidity, and market-structure controls.

## Open Questions
- Should regime filters be global (same across all assets) or asset-specific with liquidity-tier buckets?
- What is the minimum live data stack needed for real-time stress-state detection (credit, dollar, funding, OI, stablecoin flows)?
- How much out-of-sample lift do these regime gates provide when added to Roy's cross-asset specification?
- Should we codify an explicit "structural-break override" state in Strategy #1 execution logic?

## Confidence Level
**Medium.**
The directional regime effects (credit spreads, dollar, real yields) are consistent and economically coherent, but threshold design and cross-asset transfer remain uncertain. Confidence should move to High only after Devin's implementation backtests and Roy's expanded cross-asset validation confirm out-of-sample robustness.
