from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IngestionSLOConfig:
    max_checkpoint_age_ms: int
    max_retries_per_window: int
    max_idle_cycles: int


@dataclass(frozen=True)
class IngestionObservation:
    checkpoint_age_ms: int
    retries_in_window: int
    consecutive_idle_cycles: int


@dataclass(frozen=True)
class IngestionAlert:
    name: str
    severity: str
    message: str


@dataclass(frozen=True)
class IngestionAlertPolicy:
    channel: str
    dedup_window_ms: int


@dataclass(frozen=True)
class RoutedIngestionAlert:
    alert: IngestionAlert
    channel: str


def evaluate_ingestion_slo(
    observation: IngestionObservation,
    config: IngestionSLOConfig,
) -> list[IngestionAlert]:
    alerts: list[IngestionAlert] = []

    if observation.checkpoint_age_ms > config.max_checkpoint_age_ms:
        alerts.append(
            IngestionAlert(
                name="ingestion_checkpoint_lag",
                severity="critical",
                message=(
                    f"checkpoint age {observation.checkpoint_age_ms}ms exceeds "
                    f"{config.max_checkpoint_age_ms}ms"
                ),
            )
        )

    if observation.retries_in_window > config.max_retries_per_window:
        alerts.append(
            IngestionAlert(
                name="ingestion_retry_spike",
                severity="high",
                message=(
                    f"retries {observation.retries_in_window} exceed "
                    f"{config.max_retries_per_window} per window"
                ),
            )
        )

    if observation.consecutive_idle_cycles > config.max_idle_cycles:
        alerts.append(
            IngestionAlert(
                name="ingestion_idle_stall",
                severity="medium",
                message=(
                    f"idle cycles {observation.consecutive_idle_cycles} exceed "
                    f"{config.max_idle_cycles}"
                ),
            )
        )

    return alerts


def route_ingestion_alerts(
    alerts: list[IngestionAlert],
    policy_by_name: dict[str, IngestionAlertPolicy],
    default_channel: str = "ops",
) -> list[RoutedIngestionAlert]:
    routed: list[RoutedIngestionAlert] = []
    for alert in alerts:
        policy = policy_by_name.get(alert.name)
        routed.append(
            RoutedIngestionAlert(
                alert=alert,
                channel=default_channel if policy is None else policy.channel,
            )
        )
    return routed


def dedupe_ingestion_alerts(
    alerts: list[IngestionAlert],
    *,
    policy_by_name: dict[str, IngestionAlertPolicy],
    now_ms: int,
    last_sent_ms: dict[str, int] | None = None,
) -> tuple[list[IngestionAlert], dict[str, int]]:
    state = {} if last_sent_ms is None else dict(last_sent_ms)
    filtered: list[IngestionAlert] = []
    for alert in alerts:
        policy = policy_by_name.get(alert.name)
        dedup_window_ms = 0 if policy is None else policy.dedup_window_ms
        last_sent = state.get(alert.name)
        if last_sent is not None and now_ms - last_sent < dedup_window_ms:
            continue
        state[alert.name] = now_ms
        filtered.append(alert)
    return filtered, state
