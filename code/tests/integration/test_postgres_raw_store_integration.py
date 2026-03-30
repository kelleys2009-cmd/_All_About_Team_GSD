from __future__ import annotations

import os
import unittest
import uuid

from market_data.raw_store import PostgresRawEventStore, RawMarketEvent, ReplayCheckpoint


class PostgresRawStoreIntegrationTests(unittest.TestCase):
    @unittest.skipUnless(os.getenv("TEAM_GSD_TEST_POSTGRES_DSN"), "TEAM_GSD_TEST_POSTGRES_DSN not set")
    def test_checkpoint_recovery_resume_contract(self) -> None:
        dsn = os.environ["TEAM_GSD_TEST_POSTGRES_DSN"]
        suffix = uuid.uuid4().hex[:10]
        table_name = f"market_data_raw_events_it_{suffix}"
        checkpoint_table_name = f"market_data_replay_checkpoints_it_{suffix}"
        store = PostgresRawEventStore(
            dsn=dsn,
            table_name=table_name,
            checkpoint_table_name=checkpoint_table_name,
        )

        try:
            inserted = store.append_events(
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
            self.assertEqual(inserted, 3)

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

            inserted2, checkpoint2 = store.append_and_advance_checkpoint(
                events=[
                    RawMarketEvent(
                        venue="BINANCE_PERP",
                        symbol="BTC-USD-PERP",
                        timeframe="1m",
                        event_time_ms=1002,
                        ingest_seq=1,
                        source="binance_ws",
                        payload_version="binance_trade_v1",
                        payload={"price": "103.0"},
                    )
                ]
            )
            self.assertEqual(inserted2, 1)
            assert checkpoint2 is not None
            self.assertEqual(checkpoint2.last_event_time_ms, 1002)
            self.assertEqual(checkpoint2.last_ingest_seq, 1)
        finally:
            conn = store._connect()
            try:
                with conn.cursor() as cur:
                    cur.execute(f"DROP TABLE IF EXISTS {table_name}")
                    cur.execute(f"DROP TABLE IF EXISTS {checkpoint_table_name}")
                conn.commit()
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
