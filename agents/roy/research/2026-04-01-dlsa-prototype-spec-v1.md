# DLSA Prototype Specification v1 (Team GSD)
Date: 2026-04-01

## Executive Summary
This memo translates the selected Deep Learning Statistical Arbitrage (DLSA) concept into a concrete, testable prototype spec for Team GSD. The proposed Phase-1 design is a daily-rebalanced, market-neutral long/short portfolio on a 500-name U.S. equity universe with 5-day max holding period, decile-ranking entries, and explicit turnover/cost controls. Relative to current Team GSD backtesting infrastructure, 5 of 7 required capabilities are missing or partial, so implementation should proceed as a two-stage path: engine uplift first, then controlled pilot backtest. Cross-referencing Chris's regime framework, gross exposure should be throttled by regime state before any promotion decision.

## Data Sources
- Prior Roy research scan: `agents/roy/research/2026-03-30-novel-strategy-scan-public-papers.md` (public-paper review completed on 2026-03-30).
- DLSA source paper: arXiv 2106.04028 (sample period in paper covers U.S. equities; exact replication panel to be confirmed in implementation).
- Team GSD backtesting code snapshot read on 2026-04-01:
  - `code/backtesting/types.py`
  - `code/backtesting/strategy.py`
  - `code/backtesting/engine.py`
- Chris regime context: `agents/chris-bunge/2026-03-30-strategy-sync-brief.md` (regime-aware exposure gating in progress).
- Assets covered in this spec: U.S. equities (target: top 500 by rolling market cap, monthly reconstitution).
- Time period for first internal pilot backtest (proposed): 2016-01-01 through 2025-12-31, daily bars.

## Methodology
1. Converted DLSA concept into an implementable strategy contract with explicit portfolio, risk, and turnover parameters.
2. Mapped each required capability against the current Team GSD engine interfaces to identify objective readiness gaps.
3. Set a minimum acceptance bar for pilot approval using quantifiable metrics (Sharpe, drawdown, turnover, and implementation realism checks).
4. Added macro-regime gating hooks aligned with Chris's in-progress regime-label schema.

Assumptions:
- Daily OHLCV and point-in-time universe membership are obtainable before pilot start.
- Neutralization can be approximated with sector + beta controls in Phase 1.
- Transaction cost baseline for pilot will be conservative and higher than current default engine cost assumptions.

## Results
### 1) Proposed Prototype Parameters (Quantified)

| Component | Phase-1 spec |
|---|---|
| Universe | Top 500 U.S. equities by rolling market cap (monthly refresh) |
| Signal horizon | 1-day forecast; max holding period 5 trading days |
| Portfolio construction | Long top decile (50 names), short bottom decile (50 names) |
| Gross / net exposure | 150% gross (75% long, 75% short), target net 0% +/- 5% |
| Position sizing | Equal-weight within long and short books, 1.5% per name cap |
| Rebalance cadence | Daily, with turnover cap of 20% notional/day |
| Cost model for pilot | 10 bps round-trip (5 bps each side) + $1 ticket floor placeholder |
| Risk controls | Sector exposure cap 15% abs; single-name stop-loss at -5% from entry |
| Pilot acceptance bar | OOS Sharpe >= 1.0, max drawdown <= 20%, avg daily turnover <= 25% |

### 2) Engine Readiness Gap Assessment (2026-04-01 Snapshot)

| Capability needed for DLSA | Current status | Gap severity |
|---|---|---|
| Multi-asset portfolio simulation | Missing (engine is bar list + single position) | Critical |
| Cross-sectional ranking (500 names/day) | Missing | Critical |
| Market-neutral constraints (beta/sector) | Missing | High |
| Portfolio-level turnover accounting | Missing | High |
| Transaction-cost realism by notional/ADV | Partial (fixed slippage + fixed commission only) | High |
| Position granularity | Partial (signals limited to -1/0/1) | High |
| Walk-forward framework | Present (`train/test/step` workflow available) | Medium-ready |

Summary: 5 of 7 required capabilities are missing/partial for a valid DLSA replication path.

### 3) Implementation Sequence Proposal

| Stage | Duration estimate | Owner(s) | Exit criteria |
|---|---:|---|---|
| Stage A: Engine uplift | 1-2 weeks | Devin + Roy | Multi-asset portfolio API + neutrality + turnover metrics in backtester |
| Stage B: Data integrity prep | 3-5 days | Roy | Point-in-time universe + survivorship-safe panel validated |
| Stage C: DLSA pilot run | 1 week | Roy + Chris | OOS results produced with regime-gated and ungated variants |
| Stage D: Promotion decision | 1 day | CEO + Roy + Chris | Keep/iterate/drop decision against acceptance bar |

## Implications
- Immediate next best action is not a full model build; it is a scoped backtesting engine uplift to avoid false-positive research conclusions.
- Chris's regime labels should be integrated as a gross-exposure throttle (example: full risk in favorable regime, 50% gross in neutral regime, 0-25% gross in adverse regime).
- If the team uses current single-asset mechanics for DLSA claims, confidence in any performance result would be structurally low.

## Confidence Level
Medium

Rationale:
- High confidence in identified infrastructure gaps because they are directly observable in current code contracts.
- Medium confidence in final performance portability until point-in-time data quality and full portfolio realism are confirmed.

## Open Questions
- Can Devin prioritize a multi-asset portfolio interface in the next sprint without delaying Strategy #1 critical path?
- Should pilot universe start at top-200 (lower complexity) before scaling to top-500?
- What exact regime label taxonomy and refresh cadence will Chris finalize for gating (daily vs weekly state updates)?
- What hard capacity limits (ADV participation, borrow availability) should be enforced before any live-path recommendation?
- Do we require a second cost scenario (e.g., 15-20 bps round-trip) as a stress test gate for promotion?

## References
- DLSA paper: https://arxiv.org/abs/2106.04028
- Roy strategy scan: `agents/roy/research/2026-03-30-novel-strategy-scan-public-papers.md`
- Chris regime brief: `agents/chris-bunge/2026-03-30-strategy-sync-brief.md`
- Team GSD backtesting modules:
  - `code/backtesting/engine.py`
  - `code/backtesting/strategy.py`
  - `code/backtesting/types.py`
