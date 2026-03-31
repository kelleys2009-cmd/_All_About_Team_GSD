from __future__ import annotations

from dataclasses import dataclass

from .ingestion_alerts import IngestionAlert


@dataclass(frozen=True)
class NotifierSLOPolicy:
    metric_name: str
    threshold: float
    severity: str
    alert_name: str
    description: str


def default_notifier_slo_policies() -> list[NotifierSLOPolicy]:
    return [
        NotifierSLOPolicy(
            metric_name="notifier.alert_dropped",
            threshold=1.0,
            severity="high",
            alert_name="notifier_delivery_drop",
            description="notifier dropped at least one alert in the policy window",
        ),
        NotifierSLOPolicy(
            metric_name="notifier.circuit_open",
            threshold=1.0,
            severity="critical",
            alert_name="notifier_circuit_open",
            description="notifier circuit breaker opened for at least one channel",
        ),
    ]


def evaluate_notifier_slo_policies(
    *,
    metrics: list[tuple[str, float, dict[str, str]]],
    policies: list[NotifierSLOPolicy] | None = None,
) -> list[IngestionAlert]:
    selected_policies = default_notifier_slo_policies() if policies is None else policies
    alerts: list[IngestionAlert] = []
    for policy in selected_policies:
        matched = [
            (value, tags)
            for (metric_name, value, tags) in metrics
            if metric_name == policy.metric_name
        ]
        total_value = sum(value for value, _tags in matched)
        if total_value < policy.threshold:
            continue

        sample_tags = {} if not matched else dict(matched[0][1])
        tag_summary = ", ".join(f"{key}={value}" for key, value in sorted(sample_tags.items()))
        alerts.append(
            IngestionAlert(
                name=policy.alert_name,
                severity=policy.severity,
                message=f"{policy.description}; metric={policy.metric_name}; total={total_value}; tags={tag_summary}",
            )
        )
    return alerts
