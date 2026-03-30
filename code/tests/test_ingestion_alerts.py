from __future__ import annotations

import unittest

from market_data.ingestion_alerts import (
    IngestionObservation,
    IngestionSLOConfig,
    evaluate_ingestion_slo,
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


if __name__ == "__main__":
    unittest.main()
