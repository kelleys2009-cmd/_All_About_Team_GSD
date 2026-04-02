from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Optional

from .oms import OrderRecord


class SQLiteOrderStore:
    """SQLite-backed persistent order store keyed by client_order_id."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def get(self, client_order_id: str) -> Optional[OrderRecord]:
        row = self._fetch_one(
            """
            SELECT
              order_id,
              client_order_id,
              symbol,
              side,
              quantity,
              limit_price,
              timestamp_ms,
              status,
              risk_violations_json,
              exchange_order_id,
              filled_quantity,
              avg_fill_price
            FROM oms_orders
            WHERE client_order_id = ?
            """,
            (client_order_id,),
        )
        return self._row_to_order(row)

    def get_by_order_id(self, order_id: str) -> Optional[OrderRecord]:
        row = self._fetch_one(
            """
            SELECT
              order_id,
              client_order_id,
              symbol,
              side,
              quantity,
              limit_price,
              timestamp_ms,
              status,
              risk_violations_json,
              exchange_order_id,
              filled_quantity,
              avg_fill_price
            FROM oms_orders
            WHERE order_id = ?
            """,
            (order_id,),
        )
        return self._row_to_order(row)

    def upsert(self, record: OrderRecord) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO oms_orders (
                  order_id,
                  client_order_id,
                  symbol,
                  side,
                  quantity,
                  limit_price,
                  timestamp_ms,
                  status,
                  risk_violations_json,
                  exchange_order_id,
                  filled_quantity,
                  avg_fill_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(client_order_id) DO UPDATE SET
                  order_id=excluded.order_id,
                  symbol=excluded.symbol,
                  side=excluded.side,
                  quantity=excluded.quantity,
                  limit_price=excluded.limit_price,
                  timestamp_ms=excluded.timestamp_ms,
                  status=excluded.status,
                  risk_violations_json=excluded.risk_violations_json,
                  exchange_order_id=excluded.exchange_order_id,
                  filled_quantity=excluded.filled_quantity,
                  avg_fill_price=excluded.avg_fill_price
                """,
                (
                    record.order_id,
                    record.client_order_id,
                    record.symbol,
                    record.side,
                    record.quantity,
                    record.limit_price,
                    record.timestamp_ms,
                    record.status,
                    json.dumps(record.risk_violations, sort_keys=True),
                    record.exchange_order_id,
                    record.filled_quantity,
                    record.avg_fill_price,
                ),
            )
            conn.commit()

    def _fetch_one(self, query: str, params: tuple[object, ...]) -> Optional[sqlite3.Row]:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(query, params).fetchone()

    @staticmethod
    def _row_to_order(row: Optional[sqlite3.Row]) -> Optional[OrderRecord]:
        if row is None:
            return None
        return OrderRecord(
            order_id=row["order_id"],
            client_order_id=row["client_order_id"],
            symbol=row["symbol"],
            side=row["side"],
            quantity=float(row["quantity"]),
            limit_price=float(row["limit_price"]),
            timestamp_ms=int(row["timestamp_ms"]),
            status=row["status"],
            risk_violations=list(json.loads(row["risk_violations_json"])),
            exchange_order_id=row["exchange_order_id"],
            filled_quantity=float(row["filled_quantity"]),
            avg_fill_price=(float(row["avg_fill_price"]) if row["avg_fill_price"] is not None else None),
        )

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS oms_orders (
                  client_order_id TEXT PRIMARY KEY,
                  order_id TEXT NOT NULL,
                  symbol TEXT NOT NULL,
                  side TEXT NOT NULL,
                  quantity REAL NOT NULL,
                  limit_price REAL NOT NULL,
                  timestamp_ms INTEGER NOT NULL,
                  status TEXT NOT NULL,
                  risk_violations_json TEXT NOT NULL,
                  exchange_order_id TEXT,
                  filled_quantity REAL NOT NULL DEFAULT 0,
                  avg_fill_price REAL
                )
                """
            )
            columns = {
                row[1] for row in conn.execute("PRAGMA table_info(oms_orders)").fetchall()
            }
            if "exchange_order_id" not in columns:
                conn.execute("ALTER TABLE oms_orders ADD COLUMN exchange_order_id TEXT")
            if "filled_quantity" not in columns:
                conn.execute("ALTER TABLE oms_orders ADD COLUMN filled_quantity REAL NOT NULL DEFAULT 0")
            if "avg_fill_price" not in columns:
                conn.execute("ALTER TABLE oms_orders ADD COLUMN avg_fill_price REAL")
            conn.commit()
