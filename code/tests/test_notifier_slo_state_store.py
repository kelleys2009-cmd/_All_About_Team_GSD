from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from market_data.ingestion_alerts import IngestionAlert
from market_data.notifier_slo_policy import NotifierSLOCooldownPolicy
from market_data.notifier_slo_state_store import (
    RedisNotifierSLOStateStore,
    SqliteNotifierSLOStateStore,
    dedupe_notifier_slo_alerts_with_store,
)


class _FakeRedis:
    def __init__(self) -> None:
        self._data: dict[str, dict[str, int]] = {}

    def hget(self, key: str, field: str) -> str | None:
        bucket = self._data.get(key, {})
        value = bucket.get(field)
        return None if value is None else str(value)

    def hgetall(self, key: str) -> dict[str, str]:
        bucket = self._data.get(key, {})
        return {field: str(value) for field, value in bucket.items()}

    def hset(self, key: str, mapping: dict[str, int]) -> None:
        bucket = self._data.setdefault(key, {})
        for field, value in mapping.items():
            bucket[field] = int(value)


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

    def test_redis_state_store_round_trip(self) -> None:
        redis_client = _FakeRedis()
        store = RedisNotifierSLOStateStore(redis_client, key="test:notifier_slo")
        store.save_state({"notifier_delivery_drop": 3333})
        self.assertEqual(store.get_last_sent_ms("notifier_delivery_drop"), 3333)
        self.assertEqual(store.load_state(), {"notifier_delivery_drop": 3333})


if __name__ == "__main__":
    unittest.main()
