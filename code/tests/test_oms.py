from __future__ import annotations

import tempfile
import unittest
from typing import Dict, List, Tuple

from trading.oms import InMemoryOrderStore, OrderIntent, OrderManagementService
from trading.order_store import SQLiteOrderStore
from trading.risk_controls import AccountState, PositionState, PreTradeRiskEngine, RiskLimits


def build_limits() -> RiskLimits:
    return RiskLimits(
        max_order_notional_usd=10_000.0,
        max_total_notional_usd=20_000.0,
        max_leverage=2.0,
        max_daily_realized_loss_usd=2_000.0,
        max_slippage_bps=20.0,
        max_orders_per_minute=5,
        allowed_symbols={"BTC", "ETH"},
    )


class OMSTests(unittest.TestCase):
    def setUp(self) -> None:
        self.metrics: List[Tuple[str, float, Dict[str, str]]] = []
        self.events: List[Tuple[str, Dict[str, object]]] = []
        self.oms = OrderManagementService(
            risk_engine=PreTradeRiskEngine(build_limits()),
            order_store=InMemoryOrderStore(),
            metric_hook=lambda name, value, tags: self.metrics.append((name, value, tags)),
            event_hook=lambda name, payload: self.events.append((name, payload)),
        )

    def test_submit_order_accepts_when_risk_passes(self) -> None:
        result = self.oms.submit_order(
            intent=OrderIntent(
                client_order_id="ord-1",
                symbol="BTC",
                side="buy",
                quantity=0.1,
                limit_price=50_000.0,
                timestamp_ms=1_000,
                expected_slippage_bps=5.0,
            ),
            account_state=AccountState(
                equity_usd=100_000.0,
                realized_pnl_day_usd=0.0,
                positions={"BTC": PositionState(quantity=0.1, mark_price=50_000.0)},
            ),
        )

        self.assertTrue(result.accepted)
        self.assertFalse(result.duplicate)
        self.assertEqual(result.order.status, "pending_submit")
        self.assertIn("oms.order.accepted", [m[0] for m in self.metrics])
        self.assertEqual(self.events[-1][0], "order_accepted")

    def test_submit_order_rejects_on_risk_violation(self) -> None:
        result = self.oms.submit_order(
            intent=OrderIntent(
                client_order_id="ord-2",
                symbol="BTC",
                side="buy",
                quantity=1.0,
                limit_price=20_000.0,
                timestamp_ms=1_000,
                expected_slippage_bps=5.0,
            ),
            account_state=AccountState(
                equity_usd=100_000.0,
                realized_pnl_day_usd=0.0,
            ),
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.order.status, "rejected_risk")
        self.assertIn("max_order_notional_exceeded", result.order.risk_violations)
        self.assertIn("oms.order.rejected", [m[0] for m in self.metrics])
        self.assertIn("oms.order.rejected_violation", [m[0] for m in self.metrics])
        self.assertEqual(self.events[-1][0], "order_rejected_risk")

    def test_submit_order_is_idempotent_by_client_order_id(self) -> None:
        account_state = AccountState(equity_usd=100_000.0, realized_pnl_day_usd=0.0)
        first = self.oms.submit_order(
            intent=OrderIntent(
                client_order_id="ord-3",
                symbol="BTC",
                side="buy",
                quantity=0.1,
                limit_price=50_000.0,
                timestamp_ms=1_000,
            ),
            account_state=account_state,
        )
        second = self.oms.submit_order(
            intent=OrderIntent(
                client_order_id="ord-3",
                symbol="BTC",
                side="buy",
                quantity=0.1,
                limit_price=50_000.0,
                timestamp_ms=1_500,
            ),
            account_state=account_state,
        )

        self.assertTrue(first.accepted)
        self.assertTrue(second.accepted)
        self.assertTrue(second.duplicate)
        self.assertEqual(first.order.order_id, second.order.order_id)
        self.assertIn("oms.order.duplicate", [m[0] for m in self.metrics])
        self.assertEqual(self.events[-1][0], "order_duplicate")

    def test_submit_order_works_with_sqlite_store(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            oms = OrderManagementService(
                risk_engine=PreTradeRiskEngine(build_limits()),
                order_store=SQLiteOrderStore(f"{tmpdir}/oms.sqlite3"),
            )
            account_state = AccountState(equity_usd=100_000.0, realized_pnl_day_usd=0.0)
            first = oms.submit_order(
                intent=OrderIntent(
                    client_order_id="ord-sqlite",
                    symbol="BTC",
                    side="buy",
                    quantity=0.1,
                    limit_price=50_000.0,
                    timestamp_ms=1_000,
                ),
                account_state=account_state,
            )
            second = oms.submit_order(
                intent=OrderIntent(
                    client_order_id="ord-sqlite",
                    symbol="BTC",
                    side="buy",
                    quantity=0.1,
                    limit_price=50_000.0,
                    timestamp_ms=2_000,
                ),
                account_state=account_state,
            )

            self.assertTrue(first.accepted)
            self.assertTrue(second.duplicate)
            self.assertEqual(first.order.order_id, second.order.order_id)


if __name__ == "__main__":
    unittest.main()
