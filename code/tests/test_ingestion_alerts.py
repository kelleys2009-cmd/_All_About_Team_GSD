from __future__ import annotations

import unittest

from market_data.ingestion_alerts import (
    IngestionAlert,
    IngestionAlertPolicy,
    IngestionObservation,
    IngestionSLOConfig,
    dedupe_ingestion_alerts,
    evaluate_ingestion_slo,
    route_ingestion_alerts,
)


class IngestionAlertTests(unittest.TestCase):
    def test_no_alerts_when_within_thresholds(self) -> None:
        alerts = evaluate_ingestion_slo(
            IngestionObservation(checkpoint_age_ms=500, retries_in_window=1, consecutive_idle_cycles=2),
            IngestionSLOConfig(max_checkpoint_age_ms=1000, max_retries_per_window=3, max_idle_cycles=5),
        )
        self.assertEqual(alerts, [])

    def test_emits_expected_alerts_for_threshold_breaches(self) -> None:
        alerts = evaluate_ingestion_slo(
            IngestionObservation(checkpoint_age_ms=5000, retries_in_window=7, consecutive_idle_cycles=9),
            IngestionSLOConfig(max_checkpoint_age_ms=1000, max_retries_per_window=3, max_idle_cycles=5),
        )
        self.assertEqual([a.name for a in alerts], [
            "ingestion_checkpoint_lag",
            "ingestion_retry_spike",
            "ingestion_idle_stall",
        ])
        self.assertEqual([a.severity for a in alerts], ["critical", "high", "medium"])

    def test_routes_alerts_to_policy_channels(self) -> None:
        alerts = [
            IngestionAlert(name="ingestion_checkpoint_lag", severity="critical", message="lag"),
            IngestionAlert(name="unknown", severity="medium", message="other"),
        ]
        routed = route_ingestion_alerts(
            alerts,
            policy_by_name={
                "ingestion_checkpoint_lag": IngestionAlertPolicy(channel="pager", dedup_window_ms=30000),
            },
            default_channel="ops",
        )
        self.assertEqual([r.channel for r in routed], ["pager", "ops"])

    def test_dedup_filters_recent_alerts_by_policy_window(self) -> None:
        alerts = [
            IngestionAlert(name="ingestion_retry_spike", severity="high", message="retry"),
            IngestionAlert(name="ingestion_idle_stall", severity="medium", message="idle"),
        ]
        policy = {
            "ingestion_retry_spike": IngestionAlertPolicy(channel="ops", dedup_window_ms=60000),
            "ingestion_idle_stall": IngestionAlertPolicy(channel="ops", dedup_window_ms=10000),
        }
        first, state = dedupe_ingestion_alerts(
            alerts,
            policy_by_name=policy,
            now_ms=1_000_000,
            last_sent_ms={},
        )
        self.assertEqual([a.name for a in first], ["ingestion_retry_spike", "ingestion_idle_stall"])

        second, state2 = dedupe_ingestion_alerts(
            alerts,
            policy_by_name=policy,
            now_ms=1_005_000,
            last_sent_ms=state,
        )
        self.assertEqual([a.name for a in second], [])

        third, _ = dedupe_ingestion_alerts(
            alerts,
            policy_by_name=policy,
            now_ms=1_061_000,
            last_sent_ms=state2,
        )
        self.assertEqual([a.name for a in third], ["ingestion_retry_spike", "ingestion_idle_stall"])


if __name__ == "__main__":
    unittest.main()
