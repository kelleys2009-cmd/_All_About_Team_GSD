from __future__ import annotations

import unittest

from trading.risk_controls import (
    AccountState,
    PositionState,
    PreTradeRiskEngine,
    ProposedOrder,
    RiskLimits,
)


def build_limits() -> RiskLimits:
    return RiskLimits(
        max_order_notional_usd=10_000.0,
        max_total_notional_usd=50_000.0,
        max_leverage=2.0,
        max_daily_realized_loss_usd=2_500.0,
        max_slippage_bps=20.0,
        max_orders_per_minute=3,
        max_position_abs_qty={"BTC": 2.0},
        max_symbol_notional_usd={"BTC": 80_000.0},
        allowed_symbols={"BTC", "ETH", "SOL", "XRP", "DOGE"},
    )


class PreTradeRiskEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = PreTradeRiskEngine(build_limits())

    def test_approves_order_when_within_limits(self) -> None:
        decision = self.engine.evaluate(
            order=ProposedOrder(
                symbol="BTC",
                side="buy",
                quantity=0.1,
                price=50_000.0,
                timestamp_ms=1_000_000,
                expected_slippage_bps=10.0,
            ),
            state=AccountState(
                equity_usd=100_000.0,
                realized_pnl_day_usd=500.0,
                positions={"BTC": PositionState(quantity=0.5, mark_price=50_000.0)},
                recent_order_timestamps_ms=[900_000, 930_000],
            ),
        )
        self.assertTrue(decision.approved)
        self.assertEqual(decision.violations, [])

    def test_blocks_kill_switch(self) -> None:
        decision = self.engine.evaluate(
            order=ProposedOrder(
                symbol="BTC",
                side="buy",
                quantity=0.1,
                price=50_000.0,
                timestamp_ms=1_000_000,
            ),
            state=AccountState(
                equity_usd=100_000.0,
                realized_pnl_day_usd=0.0,
                kill_switch_active=True,
            ),
        )
        self.assertFalse(decision.approved)
        self.assertIn("kill_switch_active", decision.violations)

    def test_blocks_when_order_notional_exceeds_limit(self) -> None:
        decision = self.engine.evaluate(
            order=ProposedOrder(
                symbol="BTC",
                side="buy",
                quantity=1.0,
                price=20_000.0,
                timestamp_ms=1_000_000,
            ),
            state=AccountState(equity_usd=100_000.0, realized_pnl_day_usd=0.0),
        )
        self.assertFalse(decision.approved)
        self.assertIn("max_order_notional_exceeded", decision.violations)

    def test_blocks_when_position_limit_exceeded(self) -> None:
        decision = self.engine.evaluate(
            order=ProposedOrder(
                symbol="BTC",
                side="buy",
                quantity=1.6,
                price=50_000.0,
                timestamp_ms=1_000_000,
            ),
            state=AccountState(
                equity_usd=100_000.0,
                realized_pnl_day_usd=0.0,
                positions={"BTC": PositionState(quantity=0.7, mark_price=50_000.0)},
            ),
        )
        self.assertFalse(decision.approved)
        self.assertIn("max_position_abs_qty_exceeded", decision.violations)

    def test_blocks_when_leverage_exceeded(self) -> None:
        decision = self.engine.evaluate(
            order=ProposedOrder(
                symbol="BTC",
                side="buy",
                quantity=0.8,
                price=50_000.0,
                timestamp_ms=1_000_000,
            ),
            state=AccountState(
                equity_usd=10_000.0,
                realized_pnl_day_usd=0.0,
                positions={"ETH": PositionState(quantity=10.0, mark_price=2_000.0)},
            ),
        )
        self.assertFalse(decision.approved)
        self.assertIn("max_leverage_exceeded", decision.violations)

    def test_blocks_when_daily_loss_exceeded(self) -> None:
        decision = self.engine.evaluate(
            order=ProposedOrder(
                symbol="ETH",
                side="sell",
                quantity=1.0,
                price=2_500.0,
                timestamp_ms=1_000_000,
            ),
            state=AccountState(
                equity_usd=80_000.0,
                realized_pnl_day_usd=-2_500.0,
            ),
        )
        self.assertFalse(decision.approved)
        self.assertIn("max_daily_loss_exceeded", decision.violations)

    def test_blocks_when_slippage_exceeds_limit(self) -> None:
        decision = self.engine.evaluate(
            order=ProposedOrder(
                symbol="SOL",
                side="buy",
                quantity=10.0,
                price=120.0,
                timestamp_ms=1_000_000,
                expected_slippage_bps=25.0,
            ),
            state=AccountState(equity_usd=50_000.0, realized_pnl_day_usd=0.0),
        )
        self.assertFalse(decision.approved)
        self.assertIn("slippage_limit_exceeded", decision.violations)

    def test_blocks_when_rate_limit_exceeded(self) -> None:
        decision = self.engine.evaluate(
            order=ProposedOrder(
                symbol="XRP",
                side="buy",
                quantity=1_000.0,
                price=1.0,
                timestamp_ms=1_000_000,
            ),
            state=AccountState(
                equity_usd=100_000.0,
                realized_pnl_day_usd=0.0,
                recent_order_timestamps_ms=[950_100, 970_000, 999_500],
            ),
        )
        self.assertFalse(decision.approved)
        self.assertIn("order_rate_limit_exceeded", decision.violations)


if __name__ == "__main__":
    unittest.main()
