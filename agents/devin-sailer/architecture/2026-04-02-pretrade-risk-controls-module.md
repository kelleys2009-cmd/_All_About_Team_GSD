# Pre-Trade Risk Controls Module for OMS Admission
Date: 2026-04-02
Author: Devin Sailer

## Summary
Implemented a shared deterministic pre-trade risk control module to gate order admission before exchange submission. This establishes hard risk boundaries (kill switch, notional/exposure, leverage, slippage, rate limits) required for live-safe execution.

Why: `TEA-46` requires live-capable safeguards and failure containment from day one. A focused, auditable pre-trade gate is the minimum control plane needed before expanding OMS/execution logic.

## Implementation details
- Added `code/trading/risk_controls.py`.
- Added data contracts:
  - `ProposedOrder`
  - `PositionState`
  - `RiskLimits`
  - `AccountState`
  - `RiskDecision`
- Added engine: `PreTradeRiskEngine.evaluate(order, state) -> RiskDecision`.

Checks implemented:
- `kill_switch_active`
- `allowed_symbols`
- `max_daily_realized_loss_usd`
- `max_slippage_bps`
- `max_order_notional_usd`
- `max_position_abs_qty` (per symbol)
- `max_symbol_notional_usd` (per symbol)
- `max_total_notional_usd` (portfolio gross notional)
- `max_leverage` (gross notional / equity)
- `max_orders_per_minute` (rolling 60s)

Design choices:
- Deterministic and side-effect free evaluation for reproducibility.
- Explicit violation codes to support audit logs, dashboards, and alert fan-out.
- Zero/negative equity is treated as infinite leverage (hard fail).
- Symbol normalization is uppercase for consistent keying.

Testing:
- Added `code/tests/test_risk_controls.py` with coverage for happy-path + each major guardrail violation.
- Updated `code/README.md` test commands to include the new suite.

## Usage
Run unit tests:

```bash
cd ~/Desktop/Team\ GSD/code
PYTHONPATH=. python3 -m unittest tests/test_risk_controls.py
```

Example integration call path (OMS side):

```python
decision = risk_engine.evaluate(order=proposed_order, state=current_account_state)
if not decision.approved:
    # reject order, persist violations, emit alert
```

## Known limitations or TODOs
- Rate limit currently uses in-memory timestamp sequence; OMS should back this with Redis for multi-worker consistency.
- No venue-specific min notional/tick-size constraints yet (needs exchange adapter metadata).
- No dynamic volatility-based slippage thresholds yet.
- No post-trade reconciliation coupling yet; this module currently only performs pre-trade admission.
- Needs integration into the execution path with structured metrics (`risk.reject.count`, by violation code).
