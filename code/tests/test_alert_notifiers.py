from __future__ import annotations

import unittest

from market_data.alert_notifiers import dispatch_routed_alerts, format_routed_alert
from market_data.ingestion_alerts import IngestionAlert, RoutedIngestionAlert


class AlertNotifierTests(unittest.TestCase):
    def test_format_routed_alert(self) -> None:
        formatted = format_routed_alert(
            RoutedIngestionAlert(
                alert=IngestionAlert(
                    name="ingestion_checkpoint_lag",
                    severity="critical",
                    message="checkpoint age 12000ms exceeds 5000ms",
                ),
                channel="pager",
            )
        )
        self.assertEqual(
            formatted,
            "[pager] CRITICAL ingestion_checkpoint_lag: checkpoint age 12000ms exceeds 5000ms",
        )

    def test_dispatch_routed_alerts_counts_sent_and_dropped(self) -> None:
        sent_pager: list[str] = []
        sent_ops: list[str] = []
        alerts = [
            RoutedIngestionAlert(
                alert=IngestionAlert(name="ingestion_checkpoint_lag", severity="critical", message="lag"),
                channel="pager",
            ),
            RoutedIngestionAlert(
                alert=IngestionAlert(name="ingestion_idle_stall", severity="medium", message="idle"),
                channel="ops",
            ),
            RoutedIngestionAlert(
                alert=IngestionAlert(name="unknown", severity="low", message="x"),
                channel="missing",
            ),
        ]

        result = dispatch_routed_alerts(
            alerts,
            senders={
                "pager": lambda alert: sent_pager.append(alert.alert.name),
                "ops": lambda alert: sent_ops.append(alert.alert.name),
            },
        )

        self.assertEqual(result.sent, 2)
        self.assertEqual(result.dropped, 1)
        self.assertEqual(sent_pager, ["ingestion_checkpoint_lag"])
        self.assertEqual(sent_ops, ["ingestion_idle_stall"])


if __name__ == "__main__":
    unittest.main()
