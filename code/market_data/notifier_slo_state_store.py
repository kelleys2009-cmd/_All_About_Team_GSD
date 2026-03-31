from __future__ import annotations

import sqlite3
from pathlib import Path

from .ingestion_alerts import IngestionAlert
from .notifier_slo_policy import NotifierSLOCooldownPolicy, dedupe_notifier_slo_alerts


class SqliteNotifierSLOStateStore:
    def __init__(self, db_path: Path | str):
        self._db_path = Path(db_path)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notifier_slo_state (
                    alert_name TEXT PRIMARY KEY,
                    last_sent_ms INTEGER NOT NULL
                )
                """
            )

    def get_last_sent_ms(self, alert_name: str) -> int | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT last_sent_ms FROM notifier_slo_state WHERE alert_name = ?",
                (alert_name,),
            ).fetchone()
        if row is None:
            return None
        return int(row[0])

    def load_state(self) -> dict[str, int]:
        with self._connect() as conn:
            rows = conn.execute("SELECT alert_name, last_sent_ms FROM notifier_slo_state").fetchall()
        return {str(alert_name): int(last_sent_ms) for alert_name, last_sent_ms in rows}

    def save_state(self, state: dict[str, int]) -> None:
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO notifier_slo_state (alert_name, last_sent_ms)
                VALUES (?, ?)
                ON CONFLICT(alert_name) DO UPDATE SET
                    last_sent_ms = excluded.last_sent_ms
                """,
                [(alert_name, int(last_sent_ms)) for alert_name, last_sent_ms in state.items()],
            )


class RedisNotifierSLOStateStore:
    def __init__(self, redis_client: object, *, key: str = "teamgsd:notifier_slo_state"):
        self._redis = redis_client
        self._key = key

    def get_last_sent_ms(self, alert_name: str) -> int | None:
        value = self._redis.hget(self._key, alert_name)
        if value is None:
            return None
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        return int(value)

    def load_state(self) -> dict[str, int]:
        raw = self._redis.hgetall(self._key)
        out: dict[str, int] = {}
        for key, value in raw.items():
            alert_name = key.decode("utf-8") if isinstance(key, bytes) else str(key)
            raw_value = value.decode("utf-8") if isinstance(value, bytes) else str(value)
            out[alert_name] = int(raw_value)
        return out

    def save_state(self, state: dict[str, int]) -> None:
        if not state:
            return
        self._redis.hset(self._key, mapping={name: int(ts_ms) for name, ts_ms in state.items()})


def dedupe_notifier_slo_alerts_with_store(
    alerts: list[IngestionAlert],
    *,
    now_ms: int,
    store: SqliteNotifierSLOStateStore | RedisNotifierSLOStateStore,
    cooldown_policy_by_alert: dict[str, NotifierSLOCooldownPolicy] | None = None,
) -> list[IngestionAlert]:
    last_sent_ms = store.load_state()
    filtered, new_state = dedupe_notifier_slo_alerts(
        alerts,
        now_ms=now_ms,
        cooldown_policy_by_alert=cooldown_policy_by_alert,
        last_sent_ms=last_sent_ms,
    )
    store.save_state(new_state)
    return filtered
