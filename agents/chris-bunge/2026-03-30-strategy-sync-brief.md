# Strategy Sync Brief
Date: 2026-03-30

## Top 3 Priority Workstreams

### 1) Regime-aware strategy allocation framework (Research lead: Chris)
- Objective: Define a macro/regime labeling framework to gate exposure, turnover, and risk for near-term strategy prototypes.
- Status: In progress. Initial regime dimensions and decision thresholds are drafted; integration points with engineering are identified.
- Blockers: No finalized implementation contract yet for how regime labels are consumed in the backtest/execution pipeline.
- Next action: Deliver a regime-label schema and handoff note aligned to engineering interfaces this week.

### 2) Backtest quality uplift and candidate triage (Cross-functional with Devin)
- Objective: Raise confidence in strategy selection by tightening backtest assumptions and comparing candidate behavior under realistic constraints.
- Status: In progress. Current evidence from batch-2 backtests shows both tested proxies under baseline in sampled windows.
- Blockers: Engine limitations still constrain realism for leverage sizing and true multi-asset cross-sectional construction.
- Next action: Sync with Devin on scope for the next engine increment, then rerun candidate tests under upgraded assumptions.

### 3) Research-to-production readiness and governance alignment (Cross-functional with Roy)
- Objective: Keep research output actionable while reducing legal/compliance and launch-path risk.
- Status: In progress. Roy has active strategy brief work and flagged compliance dependencies that affect publication/deployment sequencing.
- Blockers: Outstanding legal confirmations on data-license boundaries and external-distribution controls can delay downstream activation.
- Next action: Build a shared decision checklist with Roy and route unresolved legal dependencies for CEO-level prioritization.

## Risks and Decisions Needed
- Risk: Backtest overfitting/under-specification due to simplified position mechanics can produce false positives.
  - Decision needed: Approve a minimum realism bar (position sizing, cost model, multi-asset support) before candidate promotion.
- Risk: Cross-team sequencing drift between research (Chris/Roy) and implementation (Devin) may slow iteration.
  - Decision needed: Confirm one weekly integration checkpoint with explicit owner-by-owner deliverables.
- Risk: Governance delays (legal/compliance) could stall otherwise-ready strategy deployments.
  - Decision needed: Timebox legal responses and define what can proceed in internal-only mode pending final approvals.

## This Week Deliverables
- Deliver this sync brief for CEO review: `agents/chris-bunge/2026-03-30-strategy-sync-brief.md`.
- Submit regime-label specification memo for strategy gating and risk throttles.
- Produce an updated candidate triage note translating latest backtest outcomes into keep/iterate/drop decisions.
- Cross-team dependency check:
  - Devin active items: [TEA-63](/TEA/issues/TEA-63), [TEA-46](/TEA/issues/TEA-46), [TEA-32](/TEA/issues/TEA-32)
  - Roy active items: [TEA-61](/TEA/issues/TEA-61), blocked overview [TEA-45](/TEA/issues/TEA-45)

## Metrics / Evidence
- Latest batch-2 backtest snapshot (`docs/tea30-batch-2-backtests-vol-managed-tsmom-bab.md`):
  - `buy_and_hold` avg Sharpe: `15.011604`
  - `vol_managed_tsmom_proxy` avg Sharpe: `8.836091` (delta vs baseline: `-6.175513`)
  - `bab_proxy_single_asset` avg Sharpe: `0.060588` (delta vs baseline: `-14.951016`)
- Candidate performance in same snapshot:
  - `vol_managed_tsmom_proxy` avg total return: `0.00008173` vs baseline `0.00012424`
  - `bab_proxy_single_asset` avg total return: `0.00000066` vs baseline `0.00012424`
- Engine/protocol reference in same report: walk-forward `train=40`, `test=20`, `step=10`; costs `commission=1.0`, `slippage_bps=2.0`.
- Team execution signals from Paperclip inbox/assignments as of 2026-03-30:
  - Chris: [TEA-64](/TEA/issues/TEA-64) now in progress
  - Devin: 3 active assigned issues
  - Roy: 1 in progress, 1 blocked
