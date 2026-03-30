from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class RawMarketEvent:
    venue: str
    symbol: str
    timeframe: str
    event_time_ms: int
    ingest_seq: int
    source: str
    payload_version: str
    payload: dict[str, Any]


def timescaledb_schema_sql(table_name: str = "market_data_raw_events") -> str:
    return f"""
CREATE TABLE IF NOT EXISTS {table_name} (
  venue TEXT NOT NULL,
  symbol TEXT NOT NULL,
  timeframe TEXT NOT NULL,
  event_time_ms BIGINT NOT NULL,
  ingest_seq BIGINT NOT NULL,
  source TEXT NOT NULL,
  payload_version TEXT NOT NULL,
  payload_json JSONB NOT NULL,
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (venue, symbol, timeframe, event_time_ms, ingest_seq)
);

CREATE INDEX IF NOT EXISTS idx_{table_name}_pair_time
  ON {table_name} (venue, symbol, timeframe, event_time_ms DESC);
""".strip()


class SqliteRawEventStore:
    """Local deterministic raw-event store compatible with replay semantics."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS market_data_raw_events (
                    venue TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    event_time_ms INTEGER NOT NULL,
                    ingest_seq INTEGER NOT NULL,
                    source TEXT NOT NULL,
                    payload_version TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    ingested_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (venue, symbol, timeframe, event_time_ms, ingest_seq)
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_market_data_pair_time
                ON market_data_raw_events (venue, symbol, timeframe, event_time_ms DESC)
                """
            )
            conn.commit()

    def append_events(self, events: Iterable[RawMarketEvent]) -> int:
        rows = [
            (
                ev.venue,
                ev.symbol,
                ev.timeframe,
                int(ev.event_time_ms),
                int(ev.ingest_seq),
                ev.source,
                ev.payload_version,
                json.dumps(ev.payload, sort_keys=True, separators=(",", ":")),
            )
            for ev in events
        ]
        if not rows:
            return 0

        with self._connect() as conn:
            before = conn.total_changes
            conn.executemany(
                """
                INSERT OR IGNORE INTO market_data_raw_events (
                    venue, symbol, timeframe, event_time_ms, ingest_seq,
                    source, payload_version, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            conn.commit()
            return conn.total_changes - before

    def replay(
        self,
        *,
        venue: str,
        symbol: str,
        timeframe: str,
        start_time_ms: int | None = None,
        end_time_ms: int | None = None,
    ) -> list[RawMarketEvent]:
        query = """
            SELECT venue, symbol, timeframe, event_time_ms, ingest_seq,
                   source, payload_version, payload_json
            FROM market_data_raw_events
            WHERE venue = ? AND symbol = ? AND timeframe = ?
        """
        params: list[Any] = [venue, symbol, timeframe]

        if start_time_ms is not None:
            query += " AND event_time_ms >= ?"
            params.append(int(start_time_ms))
        if end_time_ms is not None:
            query += " AND event_time_ms <= ?"
            params.append(int(end_time_ms))

        query += " ORDER BY event_time_ms ASC, ingest_seq ASC"

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()

        return [
            RawMarketEvent(
                venue=row["venue"],
                symbol=row["symbol"],
                timeframe=row["timeframe"],
                event_time_ms=int(row["event_time_ms"]),
                ingest_seq=int(row["ingest_seq"]),
                source=row["source"],
                payload_version=row["payload_version"],
                payload=json.loads(row["payload_json"]),
            )
            for row in rows
        ]
