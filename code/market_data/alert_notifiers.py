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


@dataclass(frozen=True)
class CircuitBreakerPolicy:
    failure_threshold: int = 3
    open_seconds: float = 30.0


class NotifierPermanentError(Exception):
    pass


class NotifierTransientError(Exception):
    pass


class NotifierCircuitOpenError(Exception):
    pass


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


def _classify_notifier_error(error: Exception) -> Exception:
    if isinstance(error, HTTPError):
        if 400 <= error.code < 500 and error.code not in (408, 429):
            return NotifierPermanentError(str(error))
        return NotifierTransientError(str(error))
    if isinstance(error, (URLError, TimeoutError)):
        return NotifierTransientError(str(error))
    return error


class WebhookAlertSender:
    def __init__(
        self,
        webhook_url: str,
        *,
        retry_policy: NotifierRetryPolicy | None = None,
        circuit_breaker: CircuitBreakerPolicy | None = None,
        payload_builder: Callable[[RoutedIngestionAlert], dict[str, Any]] = build_webhook_payload,
        post_json: Callable[[str, dict[str, Any], float], None] = _post_json_urllib,
        sleep: Callable[[float], None] = time.sleep,
        now: Callable[[], float] = time.time,
    ) -> None:
        self._webhook_url = webhook_url
        self._retry_policy = retry_policy or NotifierRetryPolicy()
        self._circuit_breaker = circuit_breaker or CircuitBreakerPolicy()
        self._payload_builder = payload_builder
        self._post_json = post_json
        self._sleep = sleep
        self._now = now
        self._consecutive_failures = 0
        self._circuit_open_until = 0.0

    def __call__(self, alert: RoutedIngestionAlert) -> None:
        if self._now() < self._circuit_open_until:
            raise NotifierCircuitOpenError(
                f"circuit open until {self._circuit_open_until:.3f}"
            )
        payload = self._payload_builder(alert)
        for attempt in range(1, self._retry_policy.max_attempts + 1):
            try:
                self._post_json(
                    self._webhook_url,
                    payload,
                    self._retry_policy.timeout_seconds,
                )
                self._consecutive_failures = 0
                return
            except (HTTPError, URLError, TimeoutError) as raw_error:
                classified = _classify_notifier_error(raw_error)
                if isinstance(classified, NotifierPermanentError):
                    self._trip_circuit()
                    raise classified
                if attempt >= self._retry_policy.max_attempts:
                    self._trip_circuit()
                    raise classified
                backoff = self._retry_policy.backoff_seconds * (2 ** (attempt - 1))
                self._sleep(backoff)

    def _trip_circuit(self) -> None:
        self._consecutive_failures += 1
        if self._consecutive_failures >= self._circuit_breaker.failure_threshold:
            self._circuit_open_until = self._now() + self._circuit_breaker.open_seconds


class SlackWebhookAlertSender(WebhookAlertSender):
    def __init__(
        self,
        webhook_url: str,
        *,
        retry_policy: NotifierRetryPolicy | None = None,
        circuit_breaker: CircuitBreakerPolicy | None = None,
        post_json: Callable[[str, dict[str, Any], float], None] = _post_json_urllib,
        sleep: Callable[[float], None] = time.sleep,
        now: Callable[[], float] = time.time,
    ) -> None:
        super().__init__(
            webhook_url,
            retry_policy=retry_policy,
            circuit_breaker=circuit_breaker,
            payload_builder=build_slack_payload,
            post_json=post_json,
            sleep=sleep,
            now=now,
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
        try:
            sender(alert)
            sent += 1
        except Exception:
            dropped += 1
    return NotificationDispatchResult(sent=sent, dropped=dropped)
