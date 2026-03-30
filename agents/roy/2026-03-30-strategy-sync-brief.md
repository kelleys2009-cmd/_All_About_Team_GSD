# Strategy Sync Brief
Date: 2026-03-30

## Top 3 Priority Workstreams

### 1) Strategy #1: Novel signal pipeline selection and prototype sequencing
- Objective: Select high-upside, implementable alpha families for near-term prototype work.
- Status: Completed initial scan and ranked 12 strategy families; top 3 selected and two near-term prototypes identified.
- Blockers: No blocker on research selection; implementation readiness depends on backtest feature support (neutrality constraints, turnover penalties).
- Next action: Coordinate with Devin on engine support and schedule DLSA prototype as phase 1, Attention Factors as phase 1b.

### 2) Legal/compliance gating for research-to-production path
- Objective: Reduce launch risk by identifying legal blockers before signal publication/automation.
- Status: Completed first-pass legal intake with 5 concerns; 2 rated High risk.
- Blockers: Final go/no-go requires legal confirmation on data license redistribution rights and external-distribution advice disclaimers.
- Next action: Partner with Brandon/legal owner to validate controls and set mandatory pre-release checklist dates.

### 3) Regime-aware deployment framework for upcoming prototypes
- Objective: Ensure prototype sizing and turnover are robust to macro regime shifts.
- Status: Framework requirement defined; integration design pending with Chris's macro regime labels and Devin's execution constraints.
- Blockers: Need finalized macro regime taxonomy and implementation interfaces in backtesting/deployment stack.
- Next action: Draft an integration spec for regime-gated exposure throttles and hand off to Devin for implementation feasibility.

## Risks and Decisions Needed
- Risk: Data licensing/redistribution non-compliance could invalidate published/automated signals.
  - Decision needed: Approve a source-level license matrix and block deployment for any unresolved vendor terms.
- Risk: Research outputs could be interpreted as regulated investment advice if distributed externally without controls.
  - Decision needed: Enforce standardized legal disclaimers and audience restrictions before external publication.
- Risk: LOB-family opportunities have high expected upside but require non-trivial infra expansion (latency, queue/fill realism).
  - Decision needed: Confirm whether to keep LOB in phase 2 only (recommended) versus immediate parallel build.
- Risk: Regime sensitivity may degrade live robustness if prototypes ignore macro state.
  - Decision needed: Require Chris-regime overlays for gross exposure/turnover limits in first prototype cycle.

## This Week Deliverables
- Delivered: `agents/roy/research/2026-03-30-novel-strategy-scan-public-papers.md`
- Delivered: `agents/roy/legal/2026-03-30-legal-intake-tea-39.md`
- In progress (next): Prototype implementation spec for DLSA and Attention Factors with explicit data schema, constraints, and backtest acceptance criteria.
- In progress (next): Regime-overlay handoff note (Chris labels -> Devin implementation contract).

## Metrics / Evidence
- Strategy scan coverage: 12 strategy families assessed from public research.
- Top-ranked implementation candidates: DLSA (4.6/5), Attention Factors (4.4/5), LOB representation family (3.5/5).
- Evidence breadth in selected references:
  - Attention Factors: reported out-of-sample Sharpe > 4 on largest U.S. equities over 24 years.
  - QuantNet transfer framework: 58 global equity markets.
  - ML asset pricing reference: 30,000 stocks over 60 years.
  - Century trend-following reference: 1903-present evidence horizon.
- Legal intake risk counts: 5 total concerns; 2 High, 3 Medium.
- Key legal deadline window: first two high-risk decisions targeted by 2026-04-05 and 2026-04-10.
