from __future__ import annotations

import unittest

from market_data.notifier_slo_policy import (
    NotifierSLOPolicy,
    default_notifier_slo_policies,
    evaluate_notifier_slo_policies,
)


class NotifierSLOPolicyTests(unittest.TestCase):
    def test_default_policies_emit_alerts_for_drops_and_circuit_open(self) -> None:
        alerts = evaluate_notifier_slo_policies(
            metrics=[
                ("notifier.alert_dropped", 1.0, {"venue": "BINANCE_PERP", "symbol": "BTC-USD-PERP", "timeframe": "1m"}),
                ("notifier.circuit_open", 1.0, {"venue": "KRAKEN", "symbol": "ETH-USD", "timeframe": "1m"}),
            ]
        )
        self.assertEqual({alert.name for alert in alerts}, {"notifier_delivery_drop", "notifier_circuit_open"})

    def test_custom_policy_threshold(self) -> None:
        alerts = evaluate_notifier_slo_policies(
            metrics=[
                ("notifier.alert_sent", 2.0, {"venue": "BINANCE_PERP", "symbol": "BTC-USD-PERP", "timeframe": "1m"}),
            ],
            policies=[
                NotifierSLOPolicy(
                    metric_name="notifier.alert_sent",
                    threshold=3.0,
                    severity="low",
                    alert_name="sent_too_low",
                    description="sent below expected",
                )
            ],
        )
        self.assertEqual(alerts, [])

    def test_default_policy_shape(self) -> None:
        policies = default_notifier_slo_policies()
        self.assertEqual(policies[0].metric_name, "notifier.alert_dropped")
        self.assertEqual(policies[1].metric_name, "notifier.circuit_open")


if __name__ == "__main__":
    unittest.main()
