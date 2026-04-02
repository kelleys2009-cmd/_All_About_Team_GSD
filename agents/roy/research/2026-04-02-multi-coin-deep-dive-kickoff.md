# Multi-Coin Deep Dive Kickoff (BTC, ETH, SOL, XRP, DOGE)
Date: 2026-04-02

## Executive Summary
Per board direction, the research scope is expanding from BTC-only to a full five-asset deep dive (BTC, ETH, SOL, XRP, DOGE). Initial baseline data shows broad 90-day weakness across all five assets (range: -26.3% to -40.4%) with 30-day realized volatility between 46.2% and 64.0% annualized. ETH is the only asset with positive 30-day return in the current snapshot (+3.1%), while SOL has the weakest 30-day performance (-9.4%). This confirms a high-volatility, mixed short-term momentum regime and supports asset-specific rather than one-size-fits-all signal thresholds.

## Data Sources
- CryptoCompare `histoday` endpoint (`fsym`, `tsym=USD`, `limit=365`) for daily OHLCV-derived fields.
- Assets covered: BTC, ETH, SOL, XRP, DOGE.
- Snapshot period for reported metrics: latest available close through 2026-04-01 UTC, with trailing 30-day and 90-day returns and 30-day realized volatility.
- Liquidity proxy: trailing 30-day average daily USD turnover (`volumeto`).
- Data quality flags:
  - Aggregated venue data (not single-exchange execution data).
  - Turnover field methodology is vendor-specific and should be cross-validated before production ranking decisions.

## Methodology
1. Pull 365 daily observations per asset from CryptoCompare.
2. Compute:
- Spot close (latest close)
- 30-day return
- 90-day return
- 30-day annualized realized volatility (`stdev(daily returns) * sqrt(365)`)
- 30-day average daily turnover in USD
3. Use the baseline to set priority lanes for deeper factor work and adversarial review.
4. Coordinate roles:
- Chris: macro/regime overlays and falsification checks.
- Devin: reproducible multi-asset backtest infra for signal testing.

## Results
| Asset | Close USD | 30D Return | 90D Return | 30D Ann. Vol | 30D Avg Daily Turnover (USD) |
| --- | ---: | ---: | ---: | ---: | ---: |
| BTC | 66,323.25 | -2.95% | -26.27% | 48.39% | 1,985,192,506 |
| ETH | 2,044.91 | +3.13% | -34.56% | 64.03% | 903,622,839 |
| SOL | 78.81 | -9.40% | -40.41% | 56.73% | 204,875,307 |
| XRP | 1.3080 | -3.89% | -34.80% | 46.18% | 182,796,849 |
| DOGE | 0.08974 | -0.27% | -36.71% | 62.39% | 40,192,385 |

Key quantified takeaways:
- All five assets are negative over 90 days; drawdown pressure is broad, not isolated.
- ETH leads 30-day rebound (+3.13%), while SOL lags (-9.40%).
- Highest recent volatility: ETH (64.03%) and DOGE (62.39%).
- Liquidity concentration remains heavy in BTC/ETH; DOGE turnover is ~2.0% of BTC turnover in this snapshot.

## Implications
- Strategy work should move to a multi-asset framework with per-asset risk budgets and volatility-scaled thresholds.
- BTC-only valuation framing is no longer sufficient for platform-level insight; coin-specific diagnostics are needed weekly.
- Near-term action should prioritize robust cross-asset backtesting and macro regime conditioning before public recommendations.
- Chris's macro filters should be used to segment results by regime (risk-on/risk-off/liquidity shock), and Devin should operationalize repeatable daily data pulls and signal evaluation.

## Confidence Level
**Medium.** Baseline metrics are internally consistent and quantified, but confidence is constrained by single-vendor aggregation, no exchange-level slippage modeling yet, and no multi-factor attribution in this kickoff pass.

## Open Questions
- Which factors survive costs across all five assets versus only in BTC?
- How much of each signal's performance is beta-to-BTC versus true idiosyncratic alpha?
- Should turnover thresholds exclude low-liquidity windows for DOGE/XRP signal deployment?
- Which macro filters from Chris materially improve hit rate by asset?
- What is Devin's recommended canonical data stack for reproducible cross-asset backtests?
