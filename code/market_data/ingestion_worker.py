from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

from .raw_store import RawMarketEvent, ReplayCheckpoint


@dataclass(frozen=True)
class IngestionWorkerConfig:
    venue: str
    symbol: str
    timeframe: str
    replay_batch_size: int = 500
    idle_sleep_seconds: float = 0.25
    base_backoff_seconds: float = 0.5
    max_backoff_seconds: float = 10.0


class CheckpointedIngestionWorker:
    """Polls source events, persists idempotently, and advances replay checkpoint."""

    def __init__(
        self,
        *,
        store: object,
        config: IngestionWorkerConfig,
        fetch_events: Callable[[ReplayCheckpoint | None, int], list[RawMarketEvent]],
        sleep_fn: Callable[[float], None] | None = None,
        now_ms_fn: Callable[[], int] | None = None,
        metric_fn: Callable[[str, float, dict[str, str]], None] | None = None,
        log_fn: Callable[[str, dict[str, object]], None] | None = None,
    ) -> None:
        self.store = store
        self.config = config
        self.fetch_events = fetch_events
        self.sleep_fn = sleep_fn or time.sleep
        self.now_ms_fn = now_ms_fn or (lambda: int(time.time() * 1000))
        self.metric_fn = metric_fn
        self.log_fn = log_fn
        self._consecutive_failures = 0

    def _tags(self) -> dict[str, str]:
        return {
            "venue": self.config.venue,
            "symbol": self.config.symbol,
            "timeframe": self.config.timeframe,
        }

    def _emit_metric(self, name: str, value: float, **extra_tags: str) -> None:
        if self.metric_fn is None:
            return
        tags = self._tags()
        tags.update(extra_tags)
        self.metric_fn(name, value, tags)

    def notifier_metric_tags(self, **extra_tags: str) -> dict[str, str]:
        tags = self._tags()
        tags["component"] = "notifier"
        tags.update(extra_tags)
        return tags

    def notifier_metric_fn(self) -> Callable[[str, float, dict[str, str]], None]:
        def emit(name: str, value: float, tags: dict[str, str]) -> None:
            if self.metric_fn is None:
                return
            merged_tags = self._tags()
            merged_tags.update(tags)
            self.metric_fn(name, value, merged_tags)

        return emit

    def _log(self, event: str, **fields: object) -> None:
        if self.log_fn is None:
            return
        payload: dict[str, object] = self._tags()
        payload.update(fields)
        self.log_fn(event, payload)

    def run_once(self) -> dict[str, int | str | None]:
        try:
            checkpoint = self.store.get_checkpoint(
                venue=self.config.venue,
                symbol=self.config.symbol,
                timeframe=self.config.timeframe,
            )
            if checkpoint is not None:
                self._emit_metric(
                    "ingestion.checkpoint_age_ms",
                    float(self.now_ms_fn() - checkpoint.last_event_time_ms),
                )
            events = self.fetch_events(checkpoint, self.config.replay_batch_size)
            self._emit_metric("ingestion.events_fetched", float(len(events)))
            if not events:
                self._consecutive_failures = 0
                self.sleep_fn(self.config.idle_sleep_seconds)
                self._log("ingestion.idle", sleep_seconds=self.config.idle_sleep_seconds)
                return {"status": "idle", "fetched": 0, "inserted": 0, "checkpoint": None}

            inserted, advanced_checkpoint = self.store.append_and_advance_checkpoint(events=events)
            self._consecutive_failures = 0
            self._emit_metric("ingestion.events_inserted", float(inserted))
            if advanced_checkpoint is not None:
                self._log(
                    "ingestion.ok",
                    fetched=len(events),
                    inserted=inserted,
                    checkpoint_event_time_ms=advanced_checkpoint.last_event_time_ms,
                    checkpoint_ingest_seq=advanced_checkpoint.last_ingest_seq,
                )
            return {
                "status": "ok",
                "fetched": len(events),
                "inserted": inserted,
                "checkpoint": None if advanced_checkpoint is None else advanced_checkpoint.last_event_time_ms,
            }
        except Exception as exc:
            self._consecutive_failures += 1
            multiplier = 2 ** (self._consecutive_failures - 1)
            delay = min(self.config.max_backoff_seconds, self.config.base_backoff_seconds * multiplier)
            self.sleep_fn(delay)
            self._emit_metric("ingestion.retries", 1.0, reason=exc.__class__.__name__)
            self._log(
                "ingestion.retry",
                delay_seconds=delay,
                consecutive_failures=self._consecutive_failures,
                error_type=exc.__class__.__name__,
            )
            raise
