from __future__ import annotations

import tempfile
import unittest
from typing import Dict, List, Tuple

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

    def test_dispatch_and_fill_transitions(self) -> None:
        created = self._submit_ok_order("ord-fill")
        opened = self.oms.dispatch_pending(created.order.order_id)
        assert opened.order is not None

        partial = self.oms.apply_fill(
            opened.order.order_id,
            fill_quantity=0.04,
            fill_price=50_010.0,
            ack_latency_ms=15.0,
        )
        full = self.oms.apply_fill(
            opened.order.order_id,
            fill_quantity=0.06,
            fill_price=50_005.0,
        )

        self.assertTrue(partial.success)
        self.assertTrue(full.success)
        assert partial.order is not None
        assert full.order is not None
        self.assertEqual(partial.order.status, "partially_filled")
        self.assertEqual(full.order.status, "filled")
        self.assertAlmostEqual(full.order.filled_quantity, 0.1, places=8)
        self.assertIn("oms.order.fill_slippage_bps", [m[0] for m in self.metrics])
        self.assertIn("oms.order.ack_latency_ms", [m[0] for m in self.metrics])

    def test_replace_order_cancels_and_creates_new_order(self) -> None:
        created = self._submit_ok_order("ord-replace-old")
        opened = self.oms.dispatch_pending(created.order.order_id)
        assert opened.order is not None

        cancel_result, new_submit = self.oms.replace_order(
            order_id=opened.order.order_id,
            new_client_order_id="ord-replace-new",
            new_limit_price=49_900.0,
            new_quantity=0.1,
            timestamp_ms=2_000,
            account_state=AccountState(equity_usd=100_000.0, realized_pnl_day_usd=0.0),
        )

        self.assertTrue(cancel_result.success)
        assert cancel_result.order is not None
        self.assertEqual(cancel_result.order.status, "canceled")
        assert new_submit is not None
        self.assertTrue(new_submit.accepted)
        self.assertEqual(new_submit.order.status, "pending_submit")
        self.assertIn("oms.order.replace_count", [m[0] for m in self.metrics])

    def test_submit_order_rejects_on_risk_violation(self) -> None:
        result = self.oms.submit_order(
            intent=OrderIntent(
                client_order_id="ord-reject",
                symbol="BTC",
                side="buy",
                quantity=1.0,
                limit_price=20_000.0,
                timestamp_ms=1_000,
            ),
            account_state=AccountState(equity_usd=100_000.0, realized_pnl_day_usd=0.0),
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.order.status, "rejected_risk")

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
            opened = oms.dispatch_pending(first.order.order_id)
            assert opened.order is not None
            filled = oms.apply_fill(opened.order.order_id, fill_quantity=0.1, fill_price=50_000.0)

            self.assertTrue(first.accepted)
            self.assertTrue(opened.success)
            self.assertTrue(filled.success)
            assert filled.order is not None
            self.assertEqual(filled.order.status, "filled")


if __name__ == "__main__":
    unittest.main()
