# DOGE Attention-Sensitivity and Diversification Analysis
Date: 2026-04-07

## Executive Summary
DOGE remains highly correlated with major crypto assets in the current regime: latest 90-day return correlation is 0.86 vs BTC, 0.89 vs ETH, and 0.88 vs SOL, which limits pure diversification benefit inside a crypto-only basket. In a 2-year daily sample ending 2026-04-02, adding DOGE worsened risk-adjusted performance in a simple equal-weight crypto portfolio (Sharpe moved from -0.083 at 0% DOGE to -0.097 at 10% DOGE). On attention sensitivity, weekly DOGE returns show stronger positive linkage to Google Trends changes than BTC and slightly stronger than ETH (best lag correlation: DOGE 0.45, ETH 0.40, BTC -0.20). A simple one-factor weekly timing rule based on DOGE search spikes backtests positively over the last 52 weeks, but confidence is low due short sample and obvious overfitting risk.

## Data Sources
- Price data: Yahoo Finance (`DOGE-USD`, `BTC-USD`, `ETH-USD`, `SOL-USD`, `XRP-USD`, `^GSPC`), daily closes.
- Social attention proxy 1: Google Trends via `pytrends` (US/global default feed), weekly interest for `dogecoin`, `bitcoin`, `ethereum` over prior 52 weeks.
- Social attention proxy 2: Reddit subscriber history via SubredditStats API:
  - `r/dogecoin`, `r/bitcoin`, `r/ethereum` `subscriberCountTimeSeries`.
- Time periods:
  - Cross-asset return/correlation/portfolio tests: 2024-04-09 to 2026-04-02 (385 aligned daily observations with SPX overlap).
  - Social-sensitivity tests: trailing 52 weekly observations (Google Trends alignment window).
- Assets covered: DOGE, BTC, ETH, SOL, XRP, S&P 500.
- Reference context: Chris macro regime memo at `agents/chris-bunge/market-reports/2026-04-06-power-law-macro-and-regime-context.md`.

## Methodology
- Computed daily returns and 90-day rolling Pearson correlations for DOGE vs BTC/ETH/SOL/XRP/SPX.
- Built baseline crypto portfolio: equal-weight BTC/ETH/SOL/XRP. Re-tested with DOGE at 5% and 10% weights (remaining 4 assets scaled proportionally).
- Calculated annualized return, annualized volatility, Sharpe (rf=0), and max drawdown.
- Estimated social sensitivity using lag scans between weekly coin returns and weekly Google Trends percentage change (`lag = -4..+4 weeks`, selecting max absolute correlation).
- Tested a simple signal prototype:
  - If weekly `dogecoin` trend change > 80th percentile, go long DOGE next week; otherwise flat.
- Data quality handling:
  - X/Twitter historical mention counts were not available in this environment without paid/credentialed API access.
  - Reddit comment-volume series from SubredditStats did not overlap current period (latest points are stale), so it was excluded from lead/lag inference.

## Results
### 1) DOGE cross-asset correlation (90-day rolling)
| Asset | Latest 90d Corr | Mean 90d Corr | Min | Max |
|---|---:|---:|---:|---:|
| BTC | 0.864 | 0.812 | 0.761 | 0.864 |
| ETH | 0.889 | 0.805 | 0.644 | 0.896 |
| SOL | 0.875 | 0.799 | 0.631 | 0.914 |
| XRP | 0.872 | 0.664 | 0.293 | 0.919 |
| SPX | 0.367 | 0.439 | 0.285 | 0.562 |

Key read: DOGE currently behaves like a high-beta crypto risk factor, not an orthogonal crypto diversifier.

### 2) Diversification test: adding DOGE to a 4-asset crypto basket
| Portfolio | Ann. Return | Ann. Vol | Sharpe | Max Drawdown |
|---|---:|---:|---:|---:|
| 0% DOGE | -5.50% | 66.18% | -0.083 | -58.67% |
| 5% DOGE | -6.01% | 66.84% | -0.090 | -58.99% |
| 10% DOGE | -6.51% | 67.57% | -0.096 | -59.30% |

Result: in this sample, DOGE reduced portfolio efficiency.

### 3) Social sensitivity (Google Trends lead/lag, weekly)
| Coin | Same-Week Corr (Return vs Trend Change) | Best Lag (weeks) | Best Corr | N |
|---|---:|---:|---:|---:|
| DOGE | 0.248 | +1 | 0.448 | 52 |
| BTC | -0.181 | +1 | -0.202 | 52 |
| ETH | 0.195 | +1 | 0.398 | 52 |

Interpretation: DOGE shows the strongest positive attention linkage among tested majors in this window.

### 4) DOGE/BTC ratio spike context
- 95th percentile daily DOGE/BTC ratio move threshold: `+5.06%`.
- Spike days in sample: `37`.
- Average Google Trends daily change near spike windows: `+0.21%` vs all-day baseline `+0.14%`.

Attention is elevated around relative-outperformance events, but effect size is modest in this aggregate lens.

### 5) Prototype tradable attention signal (exploratory)
- Rule: `Long DOGE next week if current-week dogecoin trend-change > 80th percentile`, otherwise flat.
- Backtest over 52 weeks:
  - Buy-and-hold DOGE: annualized return `-13.30%`, vol `85.87%`, Sharpe `-0.155`.
  - Signal strategy: annualized return `+132.25%`, vol `55.11%`, Sharpe `2.40`, turnover `16` weeks.

This is directionally interesting but almost certainly optimistic without transaction costs, robustness checks, and out-of-sample validation.

## Implications
- DOGE is currently more useful as a tactical attention trade than as a strategic risk diversifier in a crypto sleeve.
- Portfolio construction should treat DOGE as a conditional alpha leg (event/attention regime), not a static core allocation.
- If Chris's macro view shifts toward liquidity expansion and retail reflexivity, DOGE attention-linked signals may become higher-conviction overlays.
- Next infra step with Devin: productionize weekly signal ingestion/backtest with walk-forward validation, fees/slippage, and stress tests before any live deployment.

## Confidence Level
**Medium-Low**.
- Strengths: quantified multi-source evidence, consistent correlation regime signal, explicit portfolio impact math.
- Weaknesses: no direct X mention history in this run, stale Reddit activity time series for current-period lead/lag, and only 52 weekly observations for the attention timing prototype.

## Open Questions
- Can we secure reliable historical X mention-count API access (hourly/daily) to test whether X leads DOGE more strongly than Google Trends?
- Does the attention signal survive after realistic execution assumptions (20-80 bps roundtrip, adverse selection around event spikes)?
- Are results robust across subperiods (pre/post major meme cycles, BTC halving windows, risk-on/risk-off regimes)?
- Would a multi-factor trigger (trend acceleration + DOGE/BTC breakout + options skew) outperform the single-factor trend rule?

## Supporting Artifact
- `agents/roy/research/data/2026-04-07-doge-attention-diversification-metrics.json`
