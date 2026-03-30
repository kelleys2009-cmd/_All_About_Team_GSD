from __future__ import annotations

import unittest
from urllib.error import URLError

from market_data.alert_notifiers import (
    NotifierRetryPolicy,
    SlackWebhookAlertSender,
    WebhookAlertSender,
    build_slack_payload,
    build_webhook_payload,
    dispatch_routed_alerts,
    format_routed_alert,
)
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

    def test_webhook_sender_retries_then_succeeds(self) -> None:
        calls: list[tuple[str, float]] = []
        sleeps: list[float] = []
        state = {"count": 0}

        def fake_post(url: str, _payload: dict[str, str], timeout: float) -> None:
            calls.append((url, timeout))
            state["count"] += 1
            if state["count"] == 1:
                raise URLError("temporary network error")

        sender = WebhookAlertSender(
            "https://ops.example.test/hook",
            retry_policy=NotifierRetryPolicy(max_attempts=3, backoff_seconds=0.1, timeout_seconds=1.5),
            post_json=fake_post,
            sleep=lambda seconds: sleeps.append(seconds),
        )
        sender(
            RoutedIngestionAlert(
                alert=IngestionAlert(name="ingestion_retry_spike", severity="high", message="retry spike"),
                channel="ops",
            )
        )

        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0], ("https://ops.example.test/hook", 1.5))
        self.assertEqual(sleeps, [0.1])

    def test_webhook_sender_raises_after_max_attempts(self) -> None:
        calls: list[int] = []

        def always_fail(_url: str, _payload: dict[str, str], _timeout: float) -> None:
            calls.append(1)
            raise URLError("down")

        sender = WebhookAlertSender(
            "https://ops.example.test/hook",
            retry_policy=NotifierRetryPolicy(max_attempts=2, backoff_seconds=0.05, timeout_seconds=0.5),
            post_json=always_fail,
            sleep=lambda _seconds: None,
        )
        with self.assertRaises(URLError):
            sender(
                RoutedIngestionAlert(
                    alert=IngestionAlert(name="ingestion_checkpoint_lag", severity="critical", message="lag"),
                    channel="ops",
                )
            )
        self.assertEqual(len(calls), 2)

    def test_payload_builders(self) -> None:
        alert = RoutedIngestionAlert(
            alert=IngestionAlert(name="ingestion_idle_stall", severity="medium", message="idle"),
            channel="ops",
        )
        self.assertEqual(
            build_webhook_payload(alert),
            {
                "channel": "ops",
                "severity": "medium",
                "name": "ingestion_idle_stall",
                "message": "idle",
            },
        )
        self.assertEqual(
            build_slack_payload(alert),
            {"text": "[ops] MEDIUM ingestion_idle_stall: idle"},
        )

    def test_slack_webhook_sender_uses_slack_payload(self) -> None:
        seen_payloads: list[dict[str, str]] = []

        def fake_post(_url: str, payload: dict[str, str], _timeout: float) -> None:
            seen_payloads.append(payload)

        sender = SlackWebhookAlertSender(
            "https://hooks.slack.test/services/abc",
            post_json=fake_post,
        )
        sender(
            RoutedIngestionAlert(
                alert=IngestionAlert(name="ingestion_retry_spike", severity="high", message="retry high"),
                channel="pager",
            )
        )
        self.assertEqual(
            seen_payloads,
            [{"text": "[pager] HIGH ingestion_retry_spike: retry high"}],
        )


if __name__ == "__main__":
    unittest.main()
