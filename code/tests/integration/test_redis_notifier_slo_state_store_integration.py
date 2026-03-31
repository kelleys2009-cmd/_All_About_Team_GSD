from __future__ import annotations

import os
import unittest
import uuid

from market_data.ingestion_alerts import IngestionAlert
from market_data.notifier_slo_policy import NotifierSLOCooldownPolicy
from market_data.notifier_slo_state_store import create_notifier_slo_state_store_from_env, dedupe_notifier_slo_alerts_with_store


class RedisNotifierSLOStateStoreIntegrationTests(unittest.TestCase):
    def test_redis_store_round_trip_and_dedupe(self) -> None:
        redis_url = os.getenv("TEAM_GSD_TEST_REDIS_URL")
        if not redis_url:
            self.skipTest("TEAM_GSD_TEST_REDIS_URL not set")

        try:
            import redis  # type: ignore
        except Exception:
            self.skipTest("redis package not installed")

        redis_client = redis.from_url(redis_url, decode_responses=True)
        key = f"teamgsd:test:notifier_slo:{uuid.uuid4().hex}"
        store = create_notifier_slo_state_store_from_env(
            env={
                "TEAM_GSD_NOTIFIER_SLO_STATE_BACKEND": "redis",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_URL": redis_url,
                "TEAM_GSD_NOTIFIER_SLO_REDIS_KEY": key,
            },
            redis_client_factory=lambda _url: redis_client,
        )
        alerts = [IngestionAlert(name="notifier_delivery_drop", severity="high", message="drop")]
        policy = {"notifier_delivery_drop": NotifierSLOCooldownPolicy(cooldown_ms=5000)}

        try:
            first = dedupe_notifier_slo_alerts_with_store(
                alerts,
                now_ms=1000,
                store=store,
                cooldown_policy_by_alert=policy,
            )
            second = dedupe_notifier_slo_alerts_with_store(
                alerts,
                now_ms=2000,
                store=store,
                cooldown_policy_by_alert=policy,
            )
            third = dedupe_notifier_slo_alerts_with_store(
                alerts,
                now_ms=7000,
                store=store,
                cooldown_policy_by_alert=policy,
            )

            self.assertEqual(len(first), 1)
            self.assertEqual(second, [])
            self.assertEqual(len(third), 1)
        finally:
            redis_client.delete(key)


if __name__ == "__main__":
    unittest.main()
