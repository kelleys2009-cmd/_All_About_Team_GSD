from __future__ import annotations

import tempfile
import unittest

from trading.oms import OrderRecord
from trading.order_store import SQLiteOrderStore


class SQLiteOrderStoreTests(unittest.TestCase):
    def test_upsert_and_get_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SQLiteOrderStore(f"{tmpdir}/orders.sqlite3")
            record = OrderRecord(
                order_id="ord-1",
                client_order_id="client-1",
                symbol="BTC",
                side="buy",
                quantity=0.25,
                limit_price=50_000.0,
                timestamp_ms=1_000,
                status="pending_submit",
                risk_violations=[],
                exchange_order_id="ex-ord-1",
                filled_quantity=0.1,
                avg_fill_price=50_005.0,
            )
            store.upsert(record)

            loaded = store.get("client-1")
            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual(loaded.order_id, "ord-1")
            self.assertEqual(loaded.symbol, "BTC")
            self.assertEqual(loaded.status, "pending_submit")
            self.assertEqual(loaded.exchange_order_id, "ex-ord-1")
            self.assertAlmostEqual(loaded.filled_quantity, 0.1, places=8)
            self.assertAlmostEqual(loaded.avg_fill_price or 0.0, 50_005.0, places=8)

            by_order_id = store.get_by_order_id("ord-1")
            self.assertIsNotNone(by_order_id)
            assert by_order_id is not None
            self.assertEqual(by_order_id.client_order_id, "client-1")

    def test_upsert_overwrites_same_client_order_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SQLiteOrderStore(f"{tmpdir}/orders.sqlite3")
            first = OrderRecord(
                order_id="ord-1",
                client_order_id="client-2",
                symbol="ETH",
                side="buy",
                quantity=1.0,
                limit_price=2_000.0,
                timestamp_ms=1_000,
                status="pending_submit",
                risk_violations=[],
                exchange_order_id=None,
            )
            second = OrderRecord(
                order_id="ord-2",
                client_order_id="client-2",
                symbol="ETH",
                side="sell",
                quantity=1.0,
                limit_price=1_950.0,
                timestamp_ms=2_000,
                status="rejected_risk",
                risk_violations=["max_daily_loss_exceeded"],
                exchange_order_id=None,
            )
            store.upsert(first)
            store.upsert(second)

            loaded = store.get("client-2")
            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual(loaded.order_id, "ord-2")
            self.assertEqual(loaded.side, "sell")
            self.assertEqual(loaded.risk_violations, ["max_daily_loss_exceeded"])


if __name__ == "__main__":
    unittest.main()
