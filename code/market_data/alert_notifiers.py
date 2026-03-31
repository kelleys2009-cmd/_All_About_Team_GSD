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


@dataclass(frozen=True)
class NotifierMetricSchema:
    required_base_tags: tuple[str, ...] = ("venue", "symbol", "timeframe")
    allowed_reason_tags: tuple[str, ...] = (
        "missing_sender",
        "sender_error",
        "permanent",
        "transient",
    )


class NotifierPermanentError(Exception):
    pass


class NotifierTransientError(Exception):
    pass


class NotifierCircuitOpenError(Exception):
    pass


class NotifierMetricContractError(Exception):
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


def validate_notifier_metric_tags(
    metric_name: str,
    tags: dict[str, str],
    schema: NotifierMetricSchema,
) -> None:
    if not metric_name.startswith("notifier."):
        return
    missing_tags = [key for key in schema.required_base_tags if key not in tags]
    if missing_tags:
        raise NotifierMetricContractError(
            f"{metric_name} missing required tags: {', '.join(missing_tags)}"
        )
    reason = tags.get("reason")
    if reason is not None and reason not in schema.allowed_reason_tags:
        raise NotifierMetricContractError(
            f"{metric_name} invalid reason '{reason}'"
        )


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
        metric_fn: Callable[[str, float, dict[str, str]], None] | None = None,
        metric_tags: dict[str, str] | None = None,
        metric_schema: NotifierMetricSchema | None = None,
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
        self._metric_fn = metric_fn
        self._metric_tags = {} if metric_tags is None else dict(metric_tags)
        self._metric_schema = metric_schema or NotifierMetricSchema()

    def _emit_metric(self, name: str, value: float, **extra_tags: str) -> None:
        if self._metric_fn is None:
            return
        tags = dict(self._metric_tags)
        tags.update(extra_tags)
        try:
            validate_notifier_metric_tags(name, tags, self._metric_schema)
        except NotifierMetricContractError:
            return
        self._metric_fn(name, value, tags)

    def __call__(self, alert: RoutedIngestionAlert) -> None:
        if self._now() < self._circuit_open_until:
            self._emit_metric("notifier.circuit_open_drop", 1.0, channel=alert.channel)
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
                self._emit_metric("notifier.sent", 1.0, channel=alert.channel)
                return
            except (HTTPError, URLError, TimeoutError) as raw_error:
                classified = _classify_notifier_error(raw_error)
                if isinstance(classified, NotifierPermanentError):
                    self._emit_metric("notifier.failure", 1.0, channel=alert.channel, reason="permanent")
                    self._trip_circuit()
                    raise classified
                if attempt >= self._retry_policy.max_attempts:
                    self._emit_metric("notifier.failure", 1.0, channel=alert.channel, reason="transient")
                    self._trip_circuit()
                    raise classified
                backoff = self._retry_policy.backoff_seconds * (2 ** (attempt - 1))
                self._sleep(backoff)

    def _trip_circuit(self) -> None:
        self._consecutive_failures += 1
        if self._consecutive_failures >= self._circuit_breaker.failure_threshold:
            self._circuit_open_until = self._now() + self._circuit_breaker.open_seconds
            self._emit_metric("notifier.circuit_open", 1.0)


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
        metric_fn: Callable[[str, float, dict[str, str]], None] | None = None,
        metric_tags: dict[str, str] | None = None,
        metric_schema: NotifierMetricSchema | None = None,
    ) -> None:
        super().__init__(
            webhook_url,
            retry_policy=retry_policy,
            circuit_breaker=circuit_breaker,
            payload_builder=build_slack_payload,
            post_json=post_json,
            sleep=sleep,
            now=now,
            metric_fn=metric_fn,
            metric_tags=metric_tags,
            metric_schema=metric_schema,
        )


def format_routed_alert(alert: RoutedIngestionAlert) -> str:
    return f"[{alert.channel}] {alert.alert.severity.upper()} {alert.alert.name}: {alert.alert.message}"


def dispatch_routed_alerts(
    alerts: list[RoutedIngestionAlert],
    *,
    senders: dict[str, Callable[[RoutedIngestionAlert], None]],
    metric_fn: Callable[[str, float, dict[str, str]], None] | None = None,
    metric_tags: dict[str, str] | None = None,
    metric_schema: NotifierMetricSchema | None = None,
) -> NotificationDispatchResult:
    base_tags = {} if metric_tags is None else dict(metric_tags)
    schema = metric_schema or NotifierMetricSchema()

    def emit_metric(name: str, value: float, **extra_tags: str) -> None:
        if metric_fn is None:
            return
        tags = dict(base_tags)
        tags.update(extra_tags)
        try:
            validate_notifier_metric_tags(name, tags, schema)
        except NotifierMetricContractError:
            return
        metric_fn(name, value, tags)

    sent = 0
    dropped = 0
    for alert in alerts:
        sender = senders.get(alert.channel)
        if sender is None:
            dropped += 1
            emit_metric("notifier.alert_dropped", 1.0, channel=alert.channel, reason="missing_sender")
            continue
        try:
            sender(alert)
            sent += 1
            emit_metric("notifier.alert_sent", 1.0, channel=alert.channel)
        except Exception:
            dropped += 1
            emit_metric("notifier.alert_dropped", 1.0, channel=alert.channel, reason="sender_error")
    emit_metric("notifier.batch_sent", float(sent))
    emit_metric("notifier.batch_dropped", float(dropped))
    return NotificationDispatchResult(sent=sent, dropped=dropped)
