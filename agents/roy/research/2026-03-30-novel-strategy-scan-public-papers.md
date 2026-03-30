# Novel Strategy Scan from Public Papers
Date: 2026-03-30

## Executive Summary
This scan reviewed 12 public, research-backed strategy families and ranked them by implementability for Team GSD's current infrastructure. The highest implementation-potential trio is: (1) Deep Learning Statistical Arbitrage (DLSA), (2) Attention Factors for Statistical Arbitrage, and (3) LOB representation learning (HLOB/DeepLOB/ClusterLOB family). For near-term execution, the best two prototype candidates are DLSA first, then Attention Factors, because both are equity-focused and map to existing daily-bar backtest workflows with fewer microstructure dependencies than LOB-native systems. Estimated medium-term upside is highest for the LOB family, but infrastructure lift is materially larger.

## Data Sources
- Primary source type: public papers (arXiv, SSRN, NBER, journal pages) and linked open-source repositories.
- Coverage by source:
  - U.S. equities: up to 24-year samples in stat-arb papers.
  - Global equities: 58-market coverage in transfer-learning trading framework paper.
  - LOB microstructure: NASDAQ/LSE style order-book datasets in LOB papers.
  - Long-history factor/momentum references: 1903-present trend-following evidence and 1957-2016 ML asset-pricing panel.
- Key sources and sample details are listed in References.

## Methodology
1. Collected candidate methods only from public papers with explicit empirical claims.
2. Scored each method (1-5) on:
- Novelty
- Implementation complexity (inverse-scored into implementability)
- Data accessibility for Team GSD
- Evidence strength (sample length/breadth + out-of-sample claims)
3. Built a weighted implementation score:
- 35% Data accessibility
- 30% Implementation simplicity
- 20% Evidence strength
- 15% Novelty
4. Selected top 3 by implementation score, then designed deployable entry/exit logic for each.

Assumptions:
- Current engine is strongest on daily-bar, cross-sectional equity workflows.
- LOB-grade simulation and queue modeling are not yet production-ready in current stack.
- Execution cost model remains conservative and similar to TEA-24/TEA-26 standards.

## Results
### Candidate Universe (12)

| # | Strategy family | Quant evidence from source | Data burden | Implementation score (1-5) |
|---|---|---|---|---:|
| 1 | Deep Learning Statistical Arbitrage (DLSA) | Out-of-sample stat-arb Sharpe materially above benchmarks (CNN+Transformer/IPCA residual pipeline) | Medium | 4.6 |
| 2 | Attention Factors for Statistical Arbitrage | Reported out-of-sample Sharpe > 4 on largest U.S. equities over 24 years | Medium | 4.4 |
| 3 | QuantNet transfer learning across strategies | Demonstrated transfer setup across 58 global equity markets | Medium | 4.0 |
| 4 | HLOB (hierarchical LOB learning) | Compared vs 9 SOTA models on 3 LOB datasets (15 NASDAQ stocks each) | High | 3.5 |
| 5 | DeepLOB (CNN-LSTM on LOB) | Stable out-of-sample directional accuracy across instruments incl. unseen instruments | High | 3.4 |
| 6 | ClusterLOB | Cluster-derived signals produced higher Sharpe in test vs non-cluster baselines | High | 3.4 |
| 7 | Deep limit order book forecasting (LOBFrame ecosystem) | Open-source benchmarking framework for multiple LOB datasets/models | High | 3.3 |
| 8 | MAGNN (multi-modality graph lead-lag) | Evaluated on 3,714 stocks; deployed in production setting per paper | High | 3.2 |
| 9 | Empirical Asset Pricing via ML | 30,000 stocks, 60 years (1957-2016), strong forecasting improvements | Medium | 3.8 |
| 10 | Nonlinear Time Series Momentum | New nonlinear extensions to classic TSMOM with public manuscript | Low/Medium | 3.7 |
| 11 | ML-enhanced cross-sectional multi-factor (2025) | Reported ~20% annualized return, Sharpe > 2.0 on A-shares (2010-2024) | Medium | 3.6 |
| 12 | Century-scale trend-following evidence | 1903-present trend-following evidence with robust historical behavior | Low | 3.5 |

### Top 3 Ranked for Implementation Potential
1. Deep Learning Statistical Arbitrage (DLSA)
2. Attention Factors for Statistical Arbitrage
3. LOB representation-learning family (HLOB/DeepLOB/ClusterLOB)

### Top 3 Design Details

#### 1) Deep Learning Statistical Arbitrage (Rank #1)
- Entry logic:
  - Build cross-sectional residual returns (IPCA-like risk adjustment).
  - Forecast residual alpha horizon (1-5 days) using CNN+Transformer features.
  - Long top decile forecast names, short bottom decile, beta/sector neutralized.
- Exit logic:
  - Time stop: 5 trading days.
  - Signal stop: close when forecast sign flips.
  - Risk stop: close if residual z-score mean-reverts to 0.
- Expected edge:
  - Cross-sectional mispricing capture after factor-neutralization; paper reports materially higher Sharpe than benchmark models.
- Failure modes:
  - Regime shifts in residual structure, crowding in equity stat-arb, turnover-cost bleed.
- Data requirements:
  - Daily OHLCV + market cap + sector classifications + factor exposures; no L2 book required.

#### 2) Attention Factors for Statistical Arbitrage (Rank #2)
- Entry logic:
  - Train attention model to produce conditional latent factors from characteristic/state inputs.
  - Construct long-short market-neutral portfolio by ranking expected residual alpha.
- Exit logic:
  - Daily rebalance with turnover caps.
  - Confidence-based deallocation when attention signal confidence declines below threshold.
- Expected edge:
  - Nonlinear, context-dependent factor extraction; source reports out-of-sample Sharpe above 4 on largest U.S. equities over 24 years.
- Failure modes:
  - Capacity decay, hidden factor instability, and possible implementation drift if feature engineering diverges from paper design.
- Data requirements:
  - Daily cross-sectional equities panel with broad characteristics and careful survivorship handling.

#### 3) LOB Representation Learning (Rank #3)
- Entry logic:
  - Use LOB state embeddings (HLOB/DeepLOB/ClusterLOB) to predict short-horizon direction or microprice drift.
  - Trade only when predicted probability exceeds high-confidence threshold.
- Exit logic:
  - Intraday horizon timeout (seconds/minutes), microprice reversal trigger, and spread/queue-based stop.
- Expected edge:
  - Microstructure information persistence and participant-cluster effects not captured by bar data.
- Failure modes:
  - Latency sensitivity, transaction-cost slippage, queue-position modeling error.
- Data requirements:
  - Full-depth LOB + event-level timestamps + low-latency simulation/execution stack.

## Implications
- Recommended first two prototypes:
1. DLSA (highest fit with current infra and robust equity stat-arb evidence)
2. Attention Factors (high expected upside with manageable data burden)
- Defer LOB family to phase-2 until Devin expands engine support for intraday microstructure execution realism (queue/fill/latency model).
- Cross-reference to Chris's macro work:
  - Use Chris's regime labels (growth/inflation/liquidity stress) as a gating overlay for gross exposure and turnover throttling on both DLSA and Attention-Factor prototypes.

## Confidence Level
Medium

Rationale:
- High confidence in relative ranking of implementation feasibility for current stack.
- Medium confidence in effect-size portability because multiple papers use different universes/cost models than our current backtesting environment.
- Key data-quality risk: survivorship bias and execution-cost underestimation in any daily cross-sectional replication.

## Open Questions
- Can Devin's current backtest engine support portfolio-level neutrality constraints (beta/sector) and turnover penalties without major rework?
- Which equity universe should be primary for replication (U.S. top-500 vs broader top-1500)?
- Should we require feature sets that are fully point-in-time (fundamentals lag, delistings, corporate actions) before first prototype run?
- For Attention Factors, do we replicate paper architecture exactly first, or start with a reduced architecture for faster iteration?
- What exposure limits should be conditioned on Chris's macro regime tags during early testing?

## References
- Attention Factors for Statistical Arbitrage (arXiv): https://arxiv.org/abs/2510.11616
- Attention Factors for Statistical Arbitrage (SSRN): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5588830
- Deep Learning Statistical Arbitrage (arXiv): https://arxiv.org/abs/2106.04028
- Deep Learning Statistical Arbitrage (paper PDF mirror): https://cdar.berkeley.edu/sites/default/files/deep_learning_statistical_arbitrage.pdf
- QuantNet: Transferring Learning Across Systematic Trading Strategies: https://arxiv.org/abs/2004.03445
- HLOB: Information Persistence and Structure in Limit Order Books: https://arxiv.org/abs/2405.18938
- DeepLOB: Deep Convolutional Neural Networks for Limit Order Books: https://arxiv.org/abs/1808.03668
- ClusterLOB: Enhancing Trading Strategies by Clustering Orders in Limit Order Books: https://arxiv.org/abs/2504.20349
- Deep Limit Order Book Forecasting (LOBFrame paper): https://arxiv.org/abs/2408.08456
- Financial time series forecasting with multi-modality graph neural network (MAGNN): https://doi.org/10.1016/j.patcog.2021.108102
- Empirical Asset Pricing via Machine Learning (RFS): https://academic.oup.com/rfs/article/33/5/2223/5758276
- Nonlinear Time Series Momentum (SSRN): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5933974
- Machine Learning Enhanced Multi-Factor Quantitative Trading (arXiv): https://arxiv.org/abs/2507.07107
- A Century of Evidence on Trend-Following Investing (AQR): https://www.aqr.com/insights/research/journal-article/a-century-of-evidence-on-trend-following-investing
