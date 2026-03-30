from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from market_data.raw_store import RawMarketEvent, SqliteRawEventStore, timescaledb_schema_sql


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


if __name__ == "__main__":
    unittest.main()
