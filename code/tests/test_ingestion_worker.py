from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from market_data.ingestion_worker import CheckpointedIngestionWorker, IngestionWorkerConfig
from market_data.raw_store import RawMarketEvent, ReplayCheckpoint, SqliteRawEventStore


class IngestionWorkerTests(unittest.TestCase):
    def test_run_once_persists_and_advances_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SqliteRawEventStore(Path(tmp) / "raw_events.db")
            sleeps: list[float] = []

            source_batches = [
                [
                    RawMarketEvent(
                        venue="BINANCE_PERP",
                        symbol="BTC-USD-PERP",
                        timeframe="1m",
                        event_time_ms=1000,
                        ingest_seq=1,
                        source="binance_ws",
                        payload_version="binance_trade_v1",
                        payload={"price": "100.0"},
                    ),
                    RawMarketEvent(
                        venue="BINANCE_PERP",
                        symbol="BTC-USD-PERP",
                        timeframe="1m",
                        event_time_ms=1001,
                        ingest_seq=1,
                        source="binance_ws",
                        payload_version="binance_trade_v1",
                        payload={"price": "101.0"},
                    ),
                ],
                [],
            ]

            def fetch_events(_checkpoint: ReplayCheckpoint | None, _limit: int) -> list[RawMarketEvent]:
                return source_batches.pop(0)

            worker = CheckpointedIngestionWorker(
                store=store,
                config=IngestionWorkerConfig(venue="BINANCE_PERP", symbol="BTC-USD-PERP", timeframe="1m"),
                fetch_events=fetch_events,
                sleep_fn=sleeps.append,
            )

            first = worker.run_once()
            self.assertEqual(first["status"], "ok")
            self.assertEqual(first["inserted"], 2)
            checkpoint = store.get_checkpoint(venue="BINANCE_PERP", symbol="BTC-USD-PERP", timeframe="1m")
            assert checkpoint is not None
            self.assertEqual(checkpoint.last_event_time_ms, 1001)
            self.assertEqual(checkpoint.last_ingest_seq, 1)

            second = worker.run_once()
            self.assertEqual(second["status"], "idle")
            self.assertEqual(sleeps, [0.25])

    def test_run_once_retries_with_bounded_backoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SqliteRawEventStore(Path(tmp) / "raw_events.db")
            sleeps: list[float] = []

            def failing_fetch(_checkpoint: ReplayCheckpoint | None, _limit: int) -> list[RawMarketEvent]:
                raise RuntimeError("temporary feed outage")

            worker = CheckpointedIngestionWorker(
                store=store,
                config=IngestionWorkerConfig(
                    venue="KRAKEN",
                    symbol="ETH-USD",
                    timeframe="1m",
                    base_backoff_seconds=1.0,
                    max_backoff_seconds=2.0,
                ),
                fetch_events=failing_fetch,
                sleep_fn=sleeps.append,
            )

            with self.assertRaises(RuntimeError):
                worker.run_once()
            with self.assertRaises(RuntimeError):
                worker.run_once()
            with self.assertRaises(RuntimeError):
                worker.run_once()

            self.assertEqual(sleeps, [1.0, 2.0, 2.0])


if __name__ == "__main__":
    unittest.main()
