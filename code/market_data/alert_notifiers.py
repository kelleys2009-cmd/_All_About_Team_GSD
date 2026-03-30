from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Callable
from urllib import request
from urllib.error import HTTPError, URLError

from .ingestion_alerts import RoutedIngestionAlert


@dataclass(frozen=True)
class NotificationDispatchResult:
    sent: int
    dropped: int


@dataclass(frozen=True)
class NotifierRetryPolicy:
    max_attempts: int = 3
    backoff_seconds: float = 0.25
    timeout_seconds: float = 2.0


def _post_json_urllib(url: str, payload: dict[str, Any], timeout_seconds: float) -> None:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url=url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with request.urlopen(req, timeout=timeout_seconds):
        return


def build_webhook_payload(alert: RoutedIngestionAlert) -> dict[str, str]:
    return {
        "channel": alert.channel,
        "severity": alert.alert.severity,
        "name": alert.alert.name,
        "message": alert.alert.message,
    }


def build_slack_payload(alert: RoutedIngestionAlert) -> dict[str, str]:
    return {"text": format_routed_alert(alert)}


class WebhookAlertSender:
    def __init__(
        self,
        webhook_url: str,
        *,
        retry_policy: NotifierRetryPolicy | None = None,
        payload_builder: Callable[[RoutedIngestionAlert], dict[str, Any]] = build_webhook_payload,
        post_json: Callable[[str, dict[str, Any], float], None] = _post_json_urllib,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._webhook_url = webhook_url
        self._retry_policy = retry_policy or NotifierRetryPolicy()
        self._payload_builder = payload_builder
        self._post_json = post_json
        self._sleep = sleep

    def __call__(self, alert: RoutedIngestionAlert) -> None:
        payload = self._payload_builder(alert)
        for attempt in range(1, self._retry_policy.max_attempts + 1):
            try:
                self._post_json(
                    self._webhook_url,
                    payload,
                    self._retry_policy.timeout_seconds,
                )
                return
            except (HTTPError, URLError, TimeoutError):
                if attempt >= self._retry_policy.max_attempts:
                    raise
                backoff = self._retry_policy.backoff_seconds * (2 ** (attempt - 1))
                self._sleep(backoff)


class SlackWebhookAlertSender(WebhookAlertSender):
    def __init__(
        self,
        webhook_url: str,
        *,
        retry_policy: NotifierRetryPolicy | None = None,
        post_json: Callable[[str, dict[str, Any], float], None] = _post_json_urllib,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        super().__init__(
            webhook_url,
            retry_policy=retry_policy,
            payload_builder=build_slack_payload,
            post_json=post_json,
            sleep=sleep,
        )


def format_routed_alert(alert: RoutedIngestionAlert) -> str:
    return f"[{alert.channel}] {alert.alert.severity.upper()} {alert.alert.name}: {alert.alert.message}"


def dispatch_routed_alerts(
    alerts: list[RoutedIngestionAlert],
    *,
    senders: dict[str, Callable[[RoutedIngestionAlert], None]],
) -> NotificationDispatchResult:
    sent = 0
    dropped = 0
    for alert in alerts:
        sender = senders.get(alert.channel)
        if sender is None:
            dropped += 1
            continue
        sender(alert)
        sent += 1
    return NotificationDispatchResult(sent=sent, dropped=dropped)
