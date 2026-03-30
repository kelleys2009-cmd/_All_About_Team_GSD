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
