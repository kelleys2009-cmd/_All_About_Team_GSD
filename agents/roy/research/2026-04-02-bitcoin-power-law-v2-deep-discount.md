# Bitcoin Power Law V2: Deep-Discount Readout for New BTC Investors
Date: 2026-04-02

## Executive Summary
As of 2026-03-31, BTC was trading at **$66,694**, which is in the **18th percentile** of its long-run power-law residual range and below the model's 25th-percentile band threshold. In plain terms, BTC is currently in a historically cheaper zone versus its age-based trend, though not the absolute cheapest decile. The data supports a **"discount"** view, but does **not** support a guaranteed short-term outcome or guaranteed doubling timeline. Practical implication: this is a favorable long-horizon accumulation regime if risk is staged and drawdown tolerance is explicit.

## Non-Technical Summary (For New BTC Readers)
Bitcoin has gone through repeated boom/bust cycles, but over long periods its price has tended to grow with network age. Right now, our model says price is sitting in a lower-value zone compared with where BTC has usually traded at this stage of its life. Historically, these zones have often been better entry areas than chasing euphoric highs. That said, "good zone" does not mean "straight up from here"; volatility can still be severe.

## Data Sources
- **BTC price history:** Blockchain.com `market-price` daily USD series.
- **Coverage:** 2010-08-18 to 2026-03-31 (1,427 observations).
- **On-chain context:** Blockchain.com active addresses, hash rate, transaction count.
- **Anchor date:** Bitcoin genesis on 2009-01-03.
- **Data caveat:** Aggregate daily data (not exchange-by-exchange microstructure); early years are sparse.

## Methodology
1. Fit an age-based power-law on log-transformed data: `log(P_t) = a + n*log(D_t) + epsilon_t`.
2. Estimate residual bands at 10/25/50/75/90 percentiles.
3. Classify valuation regime:
- Deep discount: <= 25th percentile
- Neutral: 25th-75th percentile
- Euphoric: >= 75th percentile
4. Evaluate where current BTC sits vs those historical residual bands.

## Results
### Model Snapshot
- Fitted exponent `n`: **5.644**
- In-sample `R^2`: **0.960**
- Date evaluated: **2026-03-31**
- Spot price: **$66,694**
- Residual percentile: **18.0th percentile**
- Distance to model median path: **-38.3%**

### Current Valuation vs Power-Law Corridor
| quantile | model_price | distance_pct |
| --- | --- | --- |
| 10 | 57,806 | +15.4% |
| 25 | 71,853 | -7.2% |
| 50 | 108,120 | -38.3% |
| 75 | 184,451 | -63.8% |
| 90 | 335,431 | -80.1% |

Interpretation: BTC is **below Q25** and materially below median trend, which is consistent with a discount regime.

### 13% Lifespan Claim Check (Key Reality Check)
Across 14 annual checkpoints, the "every 13% of lifespan = 2x" rule did **not** hold consistently:
- Median outcome: **1.75x**
- Windows >=2.0x: **42.9%**

So this framework is better treated as a **valuation regime tool** than a deterministic doubling clock.

## e) Signal Definition (V2 Highlight)
- Core model: `log(P_t) = a + n*log(D_t) + epsilon_t`
- Fitted exponent: `n = 5.644`
- Residual corridor: empirical 10/25/50/75/90 percentiles of `epsilon_t`
- Regime labels:
  - `Deep discount`: residual <= 25th percentile
  - `Neutral`: residual 25th-75th percentile
  - `Euphoric`: residual >= 75th percentile
- **Current state (2026-03-31): residual percentile 18.0 -> discount regime**

## Implications
- For long-horizon BTC investors, current positioning is more consistent with **accumulation zone** than with late-cycle euphoria.
- For strategy: prefer staged entries (tranches) over single-shot entries because discount regimes can stay volatile.
- For platform messaging: we can fairly say BTC appears historically discounted vs power-law trend, but should avoid language implying certainty or guaranteed upside.
- Cross-reference needed: align this valuation view with Chris's macro regime work before final subscriber publication.

## Confidence Level
**Medium.** The valuation signal is quantitatively clear (18th percentile residual), but confidence is capped by model risk, non-stationary market structure, and in-sample fitting limits.

## Open Questions
- Does this discount signal hold under walk-forward out-of-sample testing?
- How sensitive is the percentile reading to data-vendor choice and close-time definitions?
- What macro/liquidity filters from Chris should gate this signal before publication?
- How should Devin operationalize this as a reproducible weekly monitor in production?
- What investor-risk language should Brandon require to keep messaging compliant?
