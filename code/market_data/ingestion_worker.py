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
    ) -> None:
        self.store = store
        self.config = config
        self.fetch_events = fetch_events
        self.sleep_fn = sleep_fn or time.sleep
        self._consecutive_failures = 0

    def run_once(self) -> dict[str, int | str | None]:
        try:
            checkpoint = self.store.get_checkpoint(
                venue=self.config.venue,
                symbol=self.config.symbol,
                timeframe=self.config.timeframe,
            )
            events = self.fetch_events(checkpoint, self.config.replay_batch_size)
            if not events:
                self._consecutive_failures = 0
                self.sleep_fn(self.config.idle_sleep_seconds)
                return {"status": "idle", "fetched": 0, "inserted": 0, "checkpoint": None}

            inserted, advanced_checkpoint = self.store.append_and_advance_checkpoint(events=events)
            self._consecutive_failures = 0
            return {
                "status": "ok",
                "fetched": len(events),
                "inserted": inserted,
                "checkpoint": None if advanced_checkpoint is None else advanced_checkpoint.last_event_time_ms,
            }
        except Exception:
            self._consecutive_failures += 1
            multiplier = 2 ** (self._consecutive_failures - 1)
            delay = min(self.config.max_backoff_seconds, self.config.base_backoff_seconds * multiplier)
            self.sleep_fn(delay)
            raise
