from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable


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


@dataclass(frozen=True)
class ReplayCheckpoint:
    venue: str
    symbol: str
    timeframe: str
    last_event_time_ms: int
    last_ingest_seq: int


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


def timescaledb_checkpoint_schema_sql(table_name: str = "market_data_replay_checkpoints") -> str:
    return f"""
CREATE TABLE IF NOT EXISTS {table_name} (
  venue TEXT NOT NULL,
  symbol TEXT NOT NULL,
  timeframe TEXT NOT NULL,
  last_event_time_ms BIGINT NOT NULL,
  last_ingest_seq BIGINT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (venue, symbol, timeframe)
);
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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS market_data_replay_checkpoints (
                    venue TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    last_event_time_ms INTEGER NOT NULL,
                    last_ingest_seq INTEGER NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (venue, symbol, timeframe)
                )
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

    def upsert_checkpoint(self, checkpoint: ReplayCheckpoint) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO market_data_replay_checkpoints (
                    venue, symbol, timeframe, last_event_time_ms, last_ingest_seq
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(venue, symbol, timeframe) DO UPDATE SET
                    last_event_time_ms = excluded.last_event_time_ms,
                    last_ingest_seq = excluded.last_ingest_seq,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    checkpoint.venue,
                    checkpoint.symbol,
                    checkpoint.timeframe,
                    int(checkpoint.last_event_time_ms),
                    int(checkpoint.last_ingest_seq),
                ),
            )
            conn.commit()

    def get_checkpoint(self, *, venue: str, symbol: str, timeframe: str) -> ReplayCheckpoint | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT venue, symbol, timeframe, last_event_time_ms, last_ingest_seq
                FROM market_data_replay_checkpoints
                WHERE venue = ? AND symbol = ? AND timeframe = ?
                """,
                (venue, symbol, timeframe),
            ).fetchone()
        if row is None:
            return None
        return ReplayCheckpoint(
            venue=row["venue"],
            symbol=row["symbol"],
            timeframe=row["timeframe"],
            last_event_time_ms=int(row["last_event_time_ms"]),
            last_ingest_seq=int(row["last_ingest_seq"]),
        )


class PostgresRawEventStore:
    """Production raw-event store for Postgres/Timescale environments."""

    def __init__(
        self,
        *,
        dsn: str,
        table_name: str = "market_data_raw_events",
        checkpoint_table_name: str = "market_data_replay_checkpoints",
        connect_fn: Callable[..., Any] | None = None,
    ) -> None:
        self.dsn = dsn
        self.table_name = table_name
        self.checkpoint_table_name = checkpoint_table_name
        self._connect_fn = connect_fn
        self._init_schema()

    def _connect(self) -> Any:
        if self._connect_fn is not None:
            return self._connect_fn(self.dsn)
        try:
            import psycopg  # type: ignore
        except ImportError as exc:
            raise RuntimeError("psycopg is required for PostgresRawEventStore") from exc
        return psycopg.connect(self.dsn)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(timescaledb_schema_sql(self.table_name))
                cur.execute(timescaledb_checkpoint_schema_sql(self.checkpoint_table_name))
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

        query = f"""
            INSERT INTO {self.table_name} (
                venue, symbol, timeframe, event_time_ms, ingest_seq,
                source, payload_version, payload_json
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (venue, symbol, timeframe, event_time_ms, ingest_seq) DO NOTHING
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.executemany(query, rows)
                inserted = cur.rowcount if cur.rowcount is not None else 0
            conn.commit()
        return inserted

    def replay(
        self,
        *,
        venue: str,
        symbol: str,
        timeframe: str,
        start_time_ms: int | None = None,
        end_time_ms: int | None = None,
    ) -> list[RawMarketEvent]:
        query = f"""
            SELECT venue, symbol, timeframe, event_time_ms, ingest_seq,
                   source, payload_version, payload_json
            FROM {self.table_name}
            WHERE venue = %s AND symbol = %s AND timeframe = %s
        """
        params: list[Any] = [venue, symbol, timeframe]
        if start_time_ms is not None:
            query += " AND event_time_ms >= %s"
            params.append(int(start_time_ms))
        if end_time_ms is not None:
            query += " AND event_time_ms <= %s"
            params.append(int(end_time_ms))
        query += " ORDER BY event_time_ms ASC, ingest_seq ASC"

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

        return [
            RawMarketEvent(
                venue=row[0],
                symbol=row[1],
                timeframe=row[2],
                event_time_ms=int(row[3]),
                ingest_seq=int(row[4]),
                source=row[5],
                payload_version=row[6],
                payload=row[7] if isinstance(row[7], dict) else json.loads(row[7]),
            )
            for row in rows
        ]

    def upsert_checkpoint(self, checkpoint: ReplayCheckpoint) -> None:
        query = f"""
            INSERT INTO {self.checkpoint_table_name} (
                venue, symbol, timeframe, last_event_time_ms, last_ingest_seq
            ) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (venue, symbol, timeframe) DO UPDATE SET
                last_event_time_ms = excluded.last_event_time_ms,
                last_ingest_seq = excluded.last_ingest_seq,
                updated_at = NOW()
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (
                        checkpoint.venue,
                        checkpoint.symbol,
                        checkpoint.timeframe,
                        int(checkpoint.last_event_time_ms),
                        int(checkpoint.last_ingest_seq),
                    ),
                )
            conn.commit()

    def get_checkpoint(self, *, venue: str, symbol: str, timeframe: str) -> ReplayCheckpoint | None:
        query = f"""
            SELECT venue, symbol, timeframe, last_event_time_ms, last_ingest_seq
            FROM {self.checkpoint_table_name}
            WHERE venue = %s AND symbol = %s AND timeframe = %s
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (venue, symbol, timeframe))
                row = cur.fetchone()
        if row is None:
            return None
        return ReplayCheckpoint(
            venue=row[0],
            symbol=row[1],
            timeframe=row[2],
            last_event_time_ms=int(row[3]),
            last_ingest_seq=int(row[4]),
        )
