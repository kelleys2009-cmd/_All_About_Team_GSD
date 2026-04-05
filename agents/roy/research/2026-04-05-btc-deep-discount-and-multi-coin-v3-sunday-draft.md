# BTC Deep-Discount + Multi-Coin Deep Dive (V3 Sunday Draft)
Date: 2026-04-05

Bart Bot Research provides educational trading research and market analysis. All content is for informational purposes only. We are not registered investment advisors. Past performance is not indicative of future results. Always do your own research and never trade with money you cannot afford to lose.

## Executive Summary
This V3 draft merges prior BTC-only work with the multi-coin kickoff and integrates cross-team inputs from Chris (adversarial review), Irene (signal reporting template), Devin (backtest pipeline), and Brandon (legal redlines). As of 2026-04-04, BTC remains in a model-defined discount regime (18.1st residual percentile; 7.1% below the model's 25th-percentile band and 38.3% below model median), but this is a probabilistic valuation state, not a timing guarantee. Across BTC/ETH/SOL/XRP/DOGE, all five assets are still negative on a 90-day basis (-28.5% to -43.9%) despite mixed 30-day stabilization. Publication can proceed at Medium confidence if this legal-safe framing is preserved and language remains non-prescriptive.

## Non-Technical Summary
Bitcoin currently sits in a historically lower zone versus its long-run age trend in our model. That makes current conditions look more like prior "discount" periods than euphoric highs, but discount periods can still include sharp drawdowns. The broader market is still weak over 90 days across all five covered coins, so this should be read as a cautious regime map, not a simple "buy now" call.

## Data Sources
- Blockchain.com daily BTC USD `market-price` series (2009-01-03 through 2026-04-04 for power-law fit).
- CryptoCompare `histoday` daily series for BTC, ETH, SOL, XRP, DOGE (latest close through 2026-04-05 UTC).
- Internal Team GSD inputs:
- Chris adversarial memo: `agents/chris-bunge/market-reports/2026-04-04-btc-power-law-v2-adversarial-review.md`
- Irene signal template: `agents/irene/notes/2026-04-02-weekly-multi-coin-signal-summary-template.md`
- Devin infra memo: `projects/strategy-1/docs/2026-04-02-multi-asset-backtest-pipeline.md`
- Brandon legal memo: `agents/brandon-saniz/compliance/2026-04-05-multi-coin-research-claims-subscriber-language-risk-memo.md`

Data quality caveat: data is aggregated from third-party sources and may contain methodology differences or revisions.

## Methodology
1. Refit BTC power-law model: `log(P_t) = a + n*log(D_t) + epsilon_t`, where `D_t` is days since 2009-01-03.
2. Recompute residual quantile corridor (10/25/50/75/90) and current residual percentile.
3. Re-validate 13%-lifespan doubling heuristic on annual windows.
4. Compute cross-asset snapshot metrics: 30-day return, 90-day return, 30-day annualized realized volatility, and 30-day average daily USD turnover.
5. Integrate adversarial, infrastructure, and legal constraints into final recommendation language.

Model outputs are probabilistic, based on historical data, and may fail under new market regimes.

## Results
### 1) BTC Power-Law State (as of 2026-04-04)
- Fitted exponent `n`: **5.643**
- Log-space `R^2`: **0.9598**
- Spot BTC: **$66,931.75**
- Residual percentile: **18.1st percentile** (discount regime)
- Distance to model median path: **-38.3%**
- 13%-lifespan historical test (14 windows): median **1.75x**, windows >=2.0x **42.9%**

| Quantile | Model Price (USD) | Spot Distance |
| --- | ---: | ---: |
| 10th | 57,935.50 | +15.5% |
| 25th | 72,071.30 | -7.1% |
| 50th | 108,458.51 | -38.3% |
| 75th | 185,022.28 | -63.8% |
| 90th | 336,131.37 | -80.1% |

Interpretation: BTC remains below the Q25 band, consistent with "discount" positioning versus long-run model history.

### 2) Multi-Coin Snapshot (latest close 2026-04-05 UTC)
| Asset | Close (USD) | 30D Return | 90D Return | 30D Ann. Vol | 30D Avg Daily Turnover (USD) |
| --- | ---: | ---: | ---: | ---: | ---: |
| BTC | 67,152.44 | -1.41% | -28.46% | 38.35% | 1,748,276,663 |
| ETH | 2,059.46 | +4.09% | -36.15% | 54.10% | 816,652,697 |
| SOL | 80.58 | -4.84% | -41.57% | 50.97% | 183,738,952 |
| XRP | 1.3170 | -3.37% | -43.91% | 39.24% | 163,616,227 |
| DOGE | 0.09151 | +0.26% | -39.68% | 45.89% | 35,277,520 |

Key readout:
- All 5 assets remain negative over 90 days.
- ETH has strongest 30-day relative rebound (+4.09%), SOL/XRP remain weak.
- Liquidity remains concentrated in BTC/ETH; DOGE liquidity is materially lower.

### 3) Cross-Team Integration Summary
- Chris (TEA-76): verdict **Revise**, confirms discount signal but requires stronger uncertainty framing and robustness disclosure.
- Irene (TEA-77): weekly signal template complete, but live signal logs are currently missing in workspace (performance fields `N/A` until feed is connected).
- Devin (TEA-78): reproducible 5-coin walk-forward pipeline is available, but current cost model is static and bar schema is close-only.
- Brandon (TEA-79): pre-redline risk high; with required disclaimer and language controls, publication risk reduces to medium.

## Implications
- Team GSD can describe BTC as screening in a lower historical valuation regime under this model, but should not frame this as a buy recommendation.
- Cross-asset conditions still show broad medium-term weakness; a risk-staged and volatility-aware framework is required.
- Near-term product value is highest from transparent regime framing plus explicit uncertainty, not deterministic return promises.
- This report does not consider any reader's objectives, financial situation, or risk tolerance.
- Any forward-looking scenarios are illustrative research assumptions, not forecasts or promises.

## Confidence Level
**Medium.** Confidence is medium because the core BTC discount signal replicated and multi-coin metrics are internally consistent, but confidence is capped by model-class fragility, in-sample bias risk, missing production signal logs, and coarse execution-cost assumptions.

## Open Questions
- Does BTC residual-band behavior remain stable under alternate vendors and close-time definitions?
- Which macro filters most reduce false positives in prolonged bear/liquidity-stress regimes?
- When Irene's live signal feed is connected, do weekly realized P&L and win-rate metrics validate this framework?
- Can Devin's pipeline be upgraded to dynamic spread/funding/slippage assumptions for closer deployment realism?
- What publication checklist evidence is required each week to keep legal risk at Medium or lower?

Bart Bot Research provides educational trading research and market analysis. All content is for informational purposes only. We are not registered investment advisors. Past performance is not indicative of future results. Always do your own research and never trade with money you cannot afford to lose.
