from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from market_data.ingestion_alerts import IngestionAlert
from market_data.notifier_slo_policy import NotifierSLOCooldownPolicy
from market_data.notifier_slo_state_store import (
    SqliteNotifierSLOStateStore,
    dedupe_notifier_slo_alerts_with_store,
)


class NotifierSLOStateStoreTests(unittest.TestCase):
    def test_sqlite_state_store_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SqliteNotifierSLOStateStore(Path(tmp) / "notifier_slo_state.db")
            store.save_state({"notifier_delivery_drop": 1234})
            self.assertEqual(store.get_last_sent_ms("notifier_delivery_drop"), 1234)
            self.assertEqual(store.load_state(), {"notifier_delivery_drop": 1234})

    def test_dedupe_with_store_persists_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SqliteNotifierSLOStateStore(Path(tmp) / "notifier_slo_state.db")
            alerts = [
                IngestionAlert(
                    name="notifier_delivery_drop",
                    severity="high",
                    message="drop",
                )
            ]

            first = dedupe_notifier_slo_alerts_with_store(
                alerts,
                now_ms=1000,
                store=store,
                cooldown_policy_by_alert={"notifier_delivery_drop": NotifierSLOCooldownPolicy(cooldown_ms=5000)},
            )
            self.assertEqual(len(first), 1)

            second = dedupe_notifier_slo_alerts_with_store(
                alerts,
                now_ms=2000,
                store=store,
                cooldown_policy_by_alert={"notifier_delivery_drop": NotifierSLOCooldownPolicy(cooldown_ms=5000)},
            )
            self.assertEqual(second, [])

            third = dedupe_notifier_slo_alerts_with_store(
                alerts,
                now_ms=7000,
                store=store,
                cooldown_policy_by_alert={"notifier_delivery_drop": NotifierSLOCooldownPolicy(cooldown_ms=5000)},
            )
            self.assertEqual(len(third), 1)


if __name__ == "__main__":
    unittest.main()
