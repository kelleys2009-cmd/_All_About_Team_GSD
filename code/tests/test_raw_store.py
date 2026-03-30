from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from market_data.raw_store import (
    RawMarketEvent,
    ReplayCheckpoint,
    SqliteRawEventStore,
    timescaledb_checkpoint_schema_sql,
    timescaledb_schema_sql,
)


class RawStoreTests(unittest.TestCase):
    def test_append_and_replay_in_deterministic_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SqliteRawEventStore(Path(tmp) / "raw_events.db")
            inserted = store.append_events(
                [
                    RawMarketEvent(
                        venue="BINANCE_PERP",
                        symbol="BTC-USD-PERP",
                        timeframe="1m",
                        event_time_ms=1000,
                        ingest_seq=2,
                        source="binance_ws",
                        payload_version="binance_trade_v1",
                        payload={"price": "101.0"},
                    ),
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
                ]
            )
            self.assertEqual(inserted, 2)

            replay = store.replay(
                venue="BINANCE_PERP",
                symbol="BTC-USD-PERP",
                timeframe="1m",
            )
            self.assertEqual([e.ingest_seq for e in replay], [1, 2])
            self.assertEqual(replay[0].payload["price"], "100.0")

    def test_idempotent_insert_ignores_duplicates(self) -> None:
        event = RawMarketEvent(
            venue="KRAKEN",
            symbol="ETH-USD",
            timeframe="1m",
            event_time_ms=2000,
            ingest_seq=1,
            source="kraken_rest",
            payload_version="kraken_ohlcv_v1",
            payload={"close": "2500.0"},
        )
        with tempfile.TemporaryDirectory() as tmp:
            store = SqliteRawEventStore(Path(tmp) / "raw_events.db")
            first = store.append_events([event])
            second = store.append_events([event])

            self.assertEqual(first, 1)
            self.assertEqual(second, 0)
            replay = store.replay(venue="KRAKEN", symbol="ETH-USD", timeframe="1m")
            self.assertEqual(len(replay), 1)

    def test_timescale_schema_contains_jsonb_contract(self) -> None:
        ddl = timescaledb_schema_sql()
        self.assertIn("payload_json JSONB NOT NULL", ddl)
        self.assertIn("PRIMARY KEY", ddl)

    def test_checkpoint_upsert_and_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SqliteRawEventStore(Path(tmp) / "raw_events.db")
            checkpoint = ReplayCheckpoint(
                venue="BINANCE_PERP",
                symbol="BTC-USD-PERP",
                timeframe="1m",
                last_event_time_ms=5000,
                last_ingest_seq=7,
            )
            store.upsert_checkpoint(checkpoint)

            loaded = store.get_checkpoint(venue="BINANCE_PERP", symbol="BTC-USD-PERP", timeframe="1m")
            assert loaded is not None
            self.assertEqual(loaded.last_event_time_ms, 5000)
            self.assertEqual(loaded.last_ingest_seq, 7)

            store.upsert_checkpoint(
                ReplayCheckpoint(
                    venue="BINANCE_PERP",
                    symbol="BTC-USD-PERP",
                    timeframe="1m",
                    last_event_time_ms=6000,
                    last_ingest_seq=1,
                )
            )
            updated = store.get_checkpoint(venue="BINANCE_PERP", symbol="BTC-USD-PERP", timeframe="1m")
            assert updated is not None
            self.assertEqual(updated.last_event_time_ms, 6000)
            self.assertEqual(updated.last_ingest_seq, 1)

    def test_timescale_checkpoint_schema_contains_primary_key(self) -> None:
        ddl = timescaledb_checkpoint_schema_sql()
        self.assertIn("market_data_replay_checkpoints", ddl)
        self.assertIn("PRIMARY KEY (venue, symbol, timeframe)", ddl)

    def test_replay_after_checkpoint_resumes_after_last_processed_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SqliteRawEventStore(Path(tmp) / "raw_events.db")
            store.append_events(
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
                        event_time_ms=1000,
                        ingest_seq=2,
                        source="binance_ws",
                        payload_version="binance_trade_v1",
                        payload={"price": "101.0"},
                    ),
                    RawMarketEvent(
                        venue="BINANCE_PERP",
                        symbol="BTC-USD-PERP",
                        timeframe="1m",
                        event_time_ms=1001,
                        ingest_seq=1,
                        source="binance_ws",
                        payload_version="binance_trade_v1",
                        payload={"price": "102.0"},
                    ),
                ]
            )
            store.upsert_checkpoint(
                ReplayCheckpoint(
                    venue="BINANCE_PERP",
                    symbol="BTC-USD-PERP",
                    timeframe="1m",
                    last_event_time_ms=1000,
                    last_ingest_seq=1,
                )
            )

            replay = store.replay_after_checkpoint(
                venue="BINANCE_PERP",
                symbol="BTC-USD-PERP",
                timeframe="1m",
            )
            self.assertEqual([(e.event_time_ms, e.ingest_seq) for e in replay], [(1000, 2), (1001, 1)])

            bounded = store.replay_after_checkpoint(
                venue="BINANCE_PERP",
                symbol="BTC-USD-PERP",
                timeframe="1m",
                max_events=1,
            )
            self.assertEqual([(e.event_time_ms, e.ingest_seq) for e in bounded], [(1000, 2)])

    def test_append_and_advance_checkpoint_updates_cursor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SqliteRawEventStore(Path(tmp) / "raw_events.db")
            inserted, checkpoint = store.append_and_advance_checkpoint(
                events=[
                    RawMarketEvent(
                        venue="KRAKEN",
                        symbol="ETH-USD",
                        timeframe="1m",
                        event_time_ms=2000,
                        ingest_seq=1,
                        source="kraken_ws",
                        payload_version="kraken_trade_v1",
                        payload={"price": "2500.0"},
                    ),
                    RawMarketEvent(
                        venue="KRAKEN",
                        symbol="ETH-USD",
                        timeframe="1m",
                        event_time_ms=2000,
                        ingest_seq=3,
                        source="kraken_ws",
                        payload_version="kraken_trade_v1",
                        payload={"price": "2501.0"},
                    ),
                ]
            )
            self.assertEqual(inserted, 2)
            assert checkpoint is not None
            self.assertEqual(checkpoint.last_event_time_ms, 2000)
            self.assertEqual(checkpoint.last_ingest_seq, 3)

            loaded = store.get_checkpoint(venue="KRAKEN", symbol="ETH-USD", timeframe="1m")
            assert loaded is not None
            self.assertEqual(loaded.last_event_time_ms, 2000)
            self.assertEqual(loaded.last_ingest_seq, 3)


if __name__ == "__main__":
    unittest.main()
