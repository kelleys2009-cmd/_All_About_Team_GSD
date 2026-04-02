from __future__ import annotations

import tempfile
import unittest
from typing import Dict, List, Optional, Tuple

from trading.oms import (
    ExchangeAdapter,
    InMemoryOrderStore,
    OrderIntent,
    OrderManagementService,
)
from trading.order_store import SQLiteOrderStore
from trading.risk_controls import AccountState, PositionState, PreTradeRiskEngine, RiskLimits


class FakeExchangeAdapter(ExchangeAdapter):
    def __init__(self, submit_ok: bool = True, cancel_ok: bool = True) -> None:
        self.submit_ok = submit_ok
        self.cancel_ok = cancel_ok
        self.submits: List[str] = []
        self.cancels: List[str] = []

    def submit_limit(self, order):
        self.submits.append(order.order_id)
        if self.submit_ok:
            return True, f"ex-{order.order_id}", None
        return False, None, "venue_down"

    def cancel(self, order):
        self.cancels.append(order.order_id)
        if self.cancel_ok:
            return True, None
        return False, "cancel_rejected"


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
        self.exchange = FakeExchangeAdapter()
        self.oms = OrderManagementService(
            risk_engine=PreTradeRiskEngine(build_limits()),
            order_store=InMemoryOrderStore(),
            exchange_adapter=self.exchange,
            metric_hook=lambda name, value, tags: self.metrics.append((name, value, tags)),
            event_hook=lambda name, payload: self.events.append((name, payload)),
        )

    def _submit_ok_order(self, client_order_id: str = "ord-1"):
        return self.oms.submit_order(
            intent=OrderIntent(
                client_order_id=client_order_id,
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

    def test_submit_order_accepts_when_risk_passes(self) -> None:
        result = self._submit_ok_order("ord-accept")

        self.assertTrue(result.accepted)
        self.assertFalse(result.duplicate)
        self.assertEqual(result.order.status, "pending_submit")
        self.assertIn("oms.order.accepted", [m[0] for m in self.metrics])
        self.assertEqual(self.events[-1][0], "order_accepted")

    def test_submit_order_rejects_on_risk_violation(self) -> None:
        result = self.oms.submit_order(
            intent=OrderIntent(
                client_order_id="ord-reject",
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
        first = self._submit_ok_order("ord-dupe")
        second = self._submit_ok_order("ord-dupe")

        self.assertTrue(first.accepted)
        self.assertTrue(second.accepted)
        self.assertTrue(second.duplicate)
        self.assertEqual(first.order.order_id, second.order.order_id)
        self.assertIn("oms.order.duplicate", [m[0] for m in self.metrics])
        self.assertEqual(self.events[-1][0], "order_duplicate")

    def test_dispatch_pending_transitions_to_open(self) -> None:
        created = self._submit_ok_order("ord-dispatch")

        result = self.oms.dispatch_pending(created.order.order_id)

        self.assertTrue(result.success)
        assert result.order is not None
        self.assertEqual(result.order.status, "open")
        self.assertEqual(result.order.exchange_order_id, f"ex-{created.order.order_id}")
        self.assertIn("oms.order.submitted", [m[0] for m in self.metrics])
        self.assertEqual(self.events[-1][0], "order_submitted")

    def test_cancel_open_order_transitions_to_canceled(self) -> None:
        created = self._submit_ok_order("ord-cancel")
        dispatched = self.oms.dispatch_pending(created.order.order_id)
        assert dispatched.order is not None

        canceled = self.oms.cancel_order(dispatched.order.order_id)

        self.assertTrue(canceled.success)
        assert canceled.order is not None
        self.assertEqual(canceled.order.status, "canceled")
        self.assertIn("oms.order.canceled", [m[0] for m in self.metrics])
        self.assertEqual(self.events[-1][0], "order_canceled")

    def test_dispatch_submit_failure_sets_submit_failed_status(self) -> None:
        failing = OrderManagementService(
            risk_engine=PreTradeRiskEngine(build_limits()),
            order_store=InMemoryOrderStore(),
            exchange_adapter=FakeExchangeAdapter(submit_ok=False),
        )
        created = failing.submit_order(
            intent=OrderIntent(
                client_order_id="ord-fail",
                symbol="BTC",
                side="buy",
                quantity=0.1,
                limit_price=50_000.0,
                timestamp_ms=1_000,
            ),
            account_state=AccountState(equity_usd=100_000.0, realized_pnl_day_usd=0.0),
        )

        result = failing.dispatch_pending(created.order.order_id)

        self.assertFalse(result.success)
        assert result.order is not None
        self.assertEqual(result.order.status, "submit_failed")

    def test_submit_order_works_with_sqlite_store(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            oms = OrderManagementService(
                risk_engine=PreTradeRiskEngine(build_limits()),
                order_store=SQLiteOrderStore(f"{tmpdir}/oms.sqlite3"),
                exchange_adapter=self.exchange,
            )
            first = oms.submit_order(
                intent=OrderIntent(
                    client_order_id="ord-sqlite",
                    symbol="BTC",
                    side="buy",
                    quantity=0.1,
                    limit_price=50_000.0,
                    timestamp_ms=1_000,
                ),
                account_state=AccountState(equity_usd=100_000.0, realized_pnl_day_usd=0.0),
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
                account_state=AccountState(equity_usd=100_000.0, realized_pnl_day_usd=0.0),
            )
            dispatched = oms.dispatch_pending(first.order.order_id)

            self.assertTrue(first.accepted)
            self.assertTrue(second.duplicate)
            self.assertEqual(first.order.order_id, second.order.order_id)
            self.assertTrue(dispatched.success)


if __name__ == "__main__":
    unittest.main()
