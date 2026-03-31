from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Callable

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


def create_notifier_slo_state_store_from_env(
    *,
    env: dict[str, str] | None = None,
    redis_client_factory: Callable[..., object] | None = None,
) -> SqliteNotifierSLOStateStore | RedisNotifierSLOStateStore:
    def _parse_bool(value: str | None) -> bool:
        return str(value or "").strip().lower() in {"1", "true", "yes", "on"}

    source = os.environ if env is None else env
    backend = source.get("TEAM_GSD_NOTIFIER_SLO_STATE_BACKEND", "sqlite").strip().lower()
    if backend == "redis":
        redis_url = source.get("TEAM_GSD_NOTIFIER_SLO_REDIS_URL", "redis://127.0.0.1:6379/0")
        redis_key = source.get("TEAM_GSD_NOTIFIER_SLO_REDIS_KEY", "teamgsd:notifier_slo_state")
        if redis_client_factory is None:
            raise ValueError("redis_client_factory is required when backend=redis")
        redis_kwargs: dict[str, object] = {}
        redis_username = source.get("TEAM_GSD_NOTIFIER_SLO_REDIS_USERNAME")
        redis_password = source.get("TEAM_GSD_NOTIFIER_SLO_REDIS_PASSWORD")
        redis_ssl = _parse_bool(source.get("TEAM_GSD_NOTIFIER_SLO_REDIS_SSL"))
        redis_ssl_ca = source.get("TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CA_CERT")
        if redis_username:
            redis_kwargs["username"] = redis_username
        if redis_password:
            redis_kwargs["password"] = redis_password
        if redis_ssl:
            redis_kwargs["ssl"] = True
        if redis_ssl_ca:
            redis_kwargs["ssl_ca_certs"] = redis_ssl_ca

        try:
            redis_client = redis_client_factory(redis_url, **redis_kwargs)
        except TypeError:
            # Backward compatibility for factories that only accept the URL.
            redis_client = redis_client_factory(redis_url)
        return RedisNotifierSLOStateStore(redis_client, key=redis_key)

    sqlite_path = source.get("TEAM_GSD_NOTIFIER_SLO_SQLITE_PATH", "artifacts/notifier_slo_state.db")
    return SqliteNotifierSLOStateStore(sqlite_path)
