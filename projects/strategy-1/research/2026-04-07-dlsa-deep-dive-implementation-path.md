# DLSA Deep Dive: Implementation Path, Use Cases, and Extended Research Angles
Date: 2026-04-07

## Executive Summary
This deep dive expands the selected Deep Learning Statistical Arbitrage (DLSA) idea into a concrete Strategy #1 execution plan with quantified build gates and research extensions. Under current Team GSD infrastructure, DLSA remains the strongest near-term novel strategy candidate, but only if we first close critical multi-asset backtesting gaps. The proposed pilot targets a market-neutral U.S. equity book (top-500 universe) with explicit turnover/cost constraints and regime-gated gross exposure. Recommendation: prototype DLSA first, with a staged 3-4 week implementation and hard pass/fail thresholds before promotion.

## Data Sources
- Primary method source: DLSA paper (arXiv:2106.04028).
- Prior Roy scan/ranking: `projects/strategy-1/research/2026-03-30-novel-strategy-scan-public-papers.md`.
- Prior Roy prototype framing: `agents/roy/research/2026-04-01-dlsa-prototype-spec-v1.md`.
- Backtest standards/governance context from Team GSD issue stream (`TEA-24` evaluation protocol; batch outputs in `TEA-27`/`TEA-30`).
- Chris macro context used for regime gating assumptions (macro-regime overlay references in Strategy #1 workstream).
- Assets for this deep dive: U.S. equities (top-500 by rolling market cap, monthly reconstitution), daily bars.
- Suggested pilot window: 2016-01-01 to 2025-12-31 (10 years daily, OOS emphasized).

## Methodology
- Converted DLSA literature logic into a deployment spec using Team GSD constraints.
- Defined explicit implementation phases with measurable gates.
- Quantified entry/exit/risk controls and failure diagnostics.
- Added “interesting” extension lane ideas only if they are testable on current/near-term data.

Assumptions:
- Daily point-in-time equity panel and sector labels are obtainable.
- We can add portfolio-level neutrality and turnover accounting to current backtest flow.
- Cost assumptions are conservative (>=10 bps round-trip baseline for pilot).

## Results
### 1) Core DLSA Pilot Design (Quantified)

| Component | Spec |
|---|---|
| Universe | Top 500 U.S. equities by rolling market cap (monthly rebalance universe) |
| Signal target | 1-5 day residual alpha forecast |
| Book construction | Long top decile (50 names), short bottom decile (50 names) |
| Net/gross target | Net 0% +/- 5%; gross 150% baseline (75/75) |
| Holding policy | Daily rebalance, hard max hold 5 trading days |
| Turnover control | <=20% notional turnover/day target |
| Cost assumption | 10 bps round-trip base; 15 bps stress scenario |
| Risk controls | Sector cap 15% abs; single-name stop -5%; portfolio drawdown soft brake -8% |
| Acceptance gate | OOS Sharpe >= 1.0, max DD <= 20%, expectancy CI(95%) > 0 |

### 2) Why DLSA Is Still the Top “First Build”
- Infrastructure fit: daily-bar cross-sectional design is closer to current stack than LOB-native systems.
- Evidence profile: strong published stat-arb outperformance claims versus simpler baselines.
- Portfolio utility: market-neutral profile offers diversification relative to directional momentum sleeves.

### 3) Failure Modes and Early Detection Rules

| Failure mode | Quant trigger | Action |
|---|---|---|
| Cost fragility | Edge flips negative at 15 bps scenario | Reject/retune execution horizon |
| Regime concentration | >60% cumulative PnL from one macro regime | Add regime gate or reject |
| Overfit instability | Test Sharpe drops >50% vs validation median | Quarantine model variant |
| Turnover bleed | Avg turnover >30%/day with weak net alpha | Increase hold horizon / reduce rebalance |
| Crowding decay proxy | Rolling 60d Sharpe < 0 for 3 consecutive windows | Reduce gross, review feature set |

### 4) “Interesting” Extensions Worth Testing After Baseline Pilot

| Extension | Hypothesis | Incremental data/infra burden | Priority |
|---|---|---|---|
| Macro-regime gated gross exposure | Reduces drawdowns in stress regimes | Low-medium | High |
| Confidence-weighted sizing | Improves capital efficiency vs equal weight | Medium | High |
| Multi-horizon ensemble (1d/3d/5d) | Improves robustness of residual alpha | Medium | Medium |
| Sector-neutral residualization upgrade | Better factor crowding defense | Medium | High |
| Capacity-aware liquidity caps (ADV %) | Improves realism and deployability | Medium | High |
| Adversarial validation across subperiods | Detects fragile feature regimes | Low | Medium |

### 5) Build Timeline and Ownership

| Stage | Duration | Owner(s) | Exit criterion |
|---|---:|---|---|
| Backtest engine uplift (multi-asset + neutrality + turnover) | 7-10 days | Devin + Roy | Reproducible portfolio-level runs |
| Data QA + panel assembly | 3-5 days | Roy | PIT-safe panel and universe checks passed |
| Baseline DLSA pilot run | 5 days | Roy | Full OOS report with stress costs |
| Review and go/no-go | 1 day | Roy + Chris + Tanya | Promote/iterate/reject decision |

Estimated total: 16-21 calendar days.

## Implications
- DLSA should remain the first novel strategy prototype for Strategy #1, ahead of LOB-intensive alternatives.
- Immediate gating dependency is infrastructure, not model novelty; build-order discipline is crucial to avoid false positives.
- Chris macro regime tags should be integrated from day one as an exposure throttle rather than post-hoc analysis.
- If DLSA clears pass gates, the same framework can be reused for Attention Factors with lower incremental overhead.

## Confidence Level
**Medium-High.**
- High confidence in implementation ordering and risk controls.
- Medium confidence in final effect size portability until PIT data and realistic cost assumptions are validated in our exact stack.

## Open Questions
- Should gross exposure default to 150% or 100% for the first OOS pilot to reduce implementation risk?
- Do we hard-gate on 15 bps stress-cost profitability, or treat it as a soft warning?
- Which macro regime taxonomy from Chris should be used for production gating (daily vs weekly labels)?
- Should we require borrow availability proxies before any “promote” decision?
- Do we parallelize Attention Factors prep while DLSA baseline is running, or keep strict serial execution?
