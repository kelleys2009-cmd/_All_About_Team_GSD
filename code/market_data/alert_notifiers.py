from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .ingestion_alerts import RoutedIngestionAlert


@dataclass(frozen=True)
class NotificationDispatchResult:
    sent: int
    dropped: int


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
