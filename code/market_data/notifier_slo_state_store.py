from __future__ import annotations

import os
import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .ingestion_alerts import IngestionAlert
from .notifier_slo_policy import NotifierSLOCooldownPolicy, dedupe_notifier_slo_alerts

PROBE_METRIC_MAX_TAG_KEY_LEN = 64
PROBE_METRIC_MAX_TAG_VALUE_LEN = 128
PROBE_METRIC_MAX_CUSTOM_TAGS = 12


@dataclass(frozen=True)
class NotifierSLOStateEnvDebugSnapshot:
    backend: str
    valid: bool
    errors: list[str]
    redacted_env: dict[str, str]


@dataclass(frozen=True)
class NotifierSLOStateStoreProbeResult:
    backend: str
    ok: bool
    detail: str
    latency_ms: float
    error_class: str | None = None
    check_mode: str = "read"


def _classify_probe_error(detail: str) -> str | None:
    lowered = detail.strip().lower()
    if not lowered:
        return None
    if "timeout budget" in lowered:
        return "timeout"
    if "failed:" in lowered:
        raw_class = detail.split("failed:", 1)[1].strip().split()[0]
        token = raw_class.replace("Error", "").replace("Exception", "").strip().lower()
        if "timeout" in token:
            return "timeout"
        if "connection" in token or "socket" in token or "network" in token:
            return "connection"
        if "auth" in token or "permission" in token or "credential" in token:
            return "auth"
        if "value" in token or "type" in token or "runtime" in token:
            return "runtime"
        return "other"
    return None


def _classify_probe_exception(exc: Exception) -> str:
    token = exc.__class__.__name__.lower()
    if "timeout" in token:
        return "timeout"
    if "connection" in token or "socket" in token or "network" in token:
        return "connection"
    if "auth" in token or "permission" in token or "credential" in token:
        return "auth"
    if "value" in token or "type" in token or "runtime" in token:
        return "runtime"
    return "other"


def _normalize_probe_error_class(value: str | None) -> str | None:
    allowed = {"timeout", "connection", "auth", "runtime", "other"}
    if value is None:
        return None
    normalized = value.strip().lower()
    if not normalized:
        return None
    if normalized in allowed:
        return normalized
    return "other"


def _normalize_probe_backend(value: str) -> str:
    normalized = value.strip().lower()
    if normalized in {"sqlite", "redis"}:
        return normalized
    return "other"


def _normalize_probe_check_mode(value: str) -> str:
    normalized = value.strip().lower()
    if normalized in {"read", "read_write"}:
        return normalized
    return "other"


def _sanitize_metric_tags(metric_tags: dict[str, object] | None) -> tuple[dict[str, str], int]:
    if metric_tags is None:
        return {}, 0
    sanitized: dict[str, str] = {}
    count = 0
    dropped = 0
    for key, value in metric_tags.items():
        if count >= PROBE_METRIC_MAX_CUSTOM_TAGS:
            dropped += 1
            continue
        key_str = str(key).strip()[:PROBE_METRIC_MAX_TAG_KEY_LEN]
        if not key_str:
            dropped += 1
            continue
        if value is None:
            dropped += 1
            continue
        sanitized[key_str] = str(value)[:PROBE_METRIC_MAX_TAG_VALUE_LEN]
        count += 1
    return sanitized, dropped


def validate_notifier_slo_state_env(
    env: dict[str, str],
) -> list[str]:
    backend = env.get("TEAM_GSD_NOTIFIER_SLO_STATE_BACKEND", "sqlite").strip().lower()
    errors: list[str] = []
    if backend != "redis":
        return errors

    redis_url = env.get("TEAM_GSD_NOTIFIER_SLO_REDIS_URL", "").strip()
    redis_ssl = str(env.get("TEAM_GSD_NOTIFIER_SLO_REDIS_SSL", "")).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    redis_username = env.get("TEAM_GSD_NOTIFIER_SLO_REDIS_USERNAME", "").strip()
    redis_password = env.get("TEAM_GSD_NOTIFIER_SLO_REDIS_PASSWORD", "").strip()
    redis_ssl_ca = env.get("TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CA_CERT", "").strip()
    redis_ssl_certfile = env.get("TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CERTFILE", "").strip()
    redis_ssl_keyfile = env.get("TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_KEYFILE", "").strip()

    if not redis_url:
        errors.append("TEAM_GSD_NOTIFIER_SLO_REDIS_URL is required when backend=redis")
    if redis_username and not redis_password:
        errors.append("TEAM_GSD_NOTIFIER_SLO_REDIS_PASSWORD is required when TEAM_GSD_NOTIFIER_SLO_REDIS_USERNAME is set")
    if redis_ssl and not redis_ssl_ca:
        errors.append("TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CA_CERT is required when TEAM_GSD_NOTIFIER_SLO_REDIS_SSL=true")
    if bool(redis_ssl_certfile) != bool(redis_ssl_keyfile):
        errors.append("TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CERTFILE and TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_KEYFILE must be set together")
    return errors


def redact_notifier_slo_state_env(
    env: dict[str, str],
) -> dict[str, str]:
    redacted = dict(env)
    secret_keys = [
        "TEAM_GSD_NOTIFIER_SLO_REDIS_PASSWORD",
        "TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_KEYFILE",
    ]
    for key in secret_keys:
        if key in redacted and redacted[key]:
            redacted[key] = "***REDACTED***"
    return redacted


def build_notifier_slo_state_env_debug_snapshot(
    env: dict[str, str],
) -> NotifierSLOStateEnvDebugSnapshot:
    backend = env.get("TEAM_GSD_NOTIFIER_SLO_STATE_BACKEND", "sqlite").strip().lower()
    errors = validate_notifier_slo_state_env(env)
    return NotifierSLOStateEnvDebugSnapshot(
        backend=backend,
        valid=len(errors) == 0,
        errors=errors,
        redacted_env=redact_notifier_slo_state_env(env),
    )


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


def probe_notifier_slo_state_store_connectivity(
    store: SqliteNotifierSLOStateStore | RedisNotifierSLOStateStore,
    *,
    write_check: bool = False,
    timeout_ms: float | None = None,
    now_fn: Callable[[], float] | None = None,
) -> NotifierSLOStateStoreProbeResult:
    clock = now_fn or time.perf_counter
    started = clock()
    check_mode = "read_write" if write_check else "read"

    def _result(
        backend: str,
        ok: bool,
        detail: str,
        *,
        error_class: str | None = None,
    ) -> NotifierSLOStateStoreProbeResult:
        latency_ms = (clock() - started) * 1000.0
        if timeout_ms is not None and latency_ms > timeout_ms:
            return NotifierSLOStateStoreProbeResult(
                backend=backend,
                ok=False,
                detail=f"{backend} connectivity probe exceeded timeout budget",
                latency_ms=latency_ms,
                error_class="timeout",
                check_mode=check_mode,
            )
        return NotifierSLOStateStoreProbeResult(
            backend=backend,
            ok=ok,
            detail=detail,
            latency_ms=latency_ms,
            error_class=error_class,
            check_mode=check_mode,
        )

    try:
        if isinstance(store, SqliteNotifierSLOStateStore):
            with store._connect() as conn:
                conn.execute("SELECT 1").fetchone()
                if write_check:
                    conn.execute(
                        "CREATE TABLE IF NOT EXISTS notifier_slo_probe (id TEXT PRIMARY KEY, created_at INTEGER NOT NULL)"
                    )
                    probe_id = uuid.uuid4().hex
                    conn.execute(
                        "INSERT INTO notifier_slo_probe (id, created_at) VALUES (?, ?)",
                        (probe_id, 1),
                    )
                    conn.execute("DELETE FROM notifier_slo_probe WHERE id = ?", (probe_id,))
            return _result(
                backend="sqlite",
                ok=True,
                detail="sqlite connectivity OK" if not write_check else "sqlite read/write probe OK",
            )

        ping = getattr(store._redis, "ping", None)
        if callable(ping):
            ping()
        else:
            store.load_state()
        if write_check:
            set_fn = getattr(store._redis, "set", None)
            get_fn = getattr(store._redis, "get", None)
            del_fn = getattr(store._redis, "delete", None)
            if not (callable(set_fn) and callable(get_fn) and callable(del_fn)):
                raise RuntimeError("redis client missing set/get/delete for write_check")
            probe_key = f"{store._key}:probe:{uuid.uuid4().hex}"
            set_fn(probe_key, "1")
            got = get_fn(probe_key)
            del_fn(probe_key)
            if str(got) not in {"1", "b'1'"}:
                raise RuntimeError("redis write_check value mismatch")
        return _result(
            backend="redis",
            ok=True,
            detail="redis connectivity OK" if not write_check else "redis read/write probe OK",
        )
    except Exception as exc:
        backend = "redis" if isinstance(store, RedisNotifierSLOStateStore) else "sqlite"
        return _result(
            backend=backend,
            ok=False,
            detail=f"{backend} connectivity probe failed: {exc.__class__.__name__}",
            error_class=_classify_probe_exception(exc),
        )


def emit_notifier_slo_probe_metrics(
    probe: NotifierSLOStateStoreProbeResult,
    *,
    metric_fn: Callable[[str, float, dict[str, str]], None] | None,
    metric_tags: dict[str, object] | None = None,
) -> None:
    if metric_fn is None:
        return
    tags, custom_tags_dropped = _sanitize_metric_tags(metric_tags)
    tags["backend"] = _normalize_probe_backend(probe.backend)
    tags["ok"] = "true" if probe.ok else "false"
    tags["check_mode"] = _normalize_probe_check_mode(probe.check_mode)
    if not probe.ok:
        error_class = _normalize_probe_error_class(probe.error_class)
        if error_class is None:
            error_class = _normalize_probe_error_class(_classify_probe_error(probe.detail))
        if error_class is not None:
            tags["error_class"] = error_class
    metric_fn("notifier.state_probe.latency_ms", probe.latency_ms, dict(tags))
    metric_fn("notifier.state_probe.success", 1.0 if probe.ok else 0.0, dict(tags))
    metric_fn("notifier.state_probe.failure", 0.0 if probe.ok else 1.0, dict(tags))
    metric_fn("notifier.state_probe.custom_tags_dropped", float(custom_tags_dropped), dict(tags))


def create_notifier_slo_state_store_from_env(
    *,
    env: dict[str, str] | None = None,
    redis_client_factory: Callable[..., object] | None = None,
) -> SqliteNotifierSLOStateStore | RedisNotifierSLOStateStore:
    def _parse_bool(value: str | None) -> bool:
        return str(value or "").strip().lower() in {"1", "true", "yes", "on"}

    source = os.environ if env is None else env
    validation_errors = validate_notifier_slo_state_env(source)
    if validation_errors:
        raise ValueError("; ".join(validation_errors))
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
        redis_ssl_certfile = source.get("TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CERTFILE")
        redis_ssl_keyfile = source.get("TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_KEYFILE")
        if redis_username:
            redis_kwargs["username"] = redis_username
        if redis_password:
            redis_kwargs["password"] = redis_password
        if redis_ssl:
            redis_kwargs["ssl"] = True
        if redis_ssl_ca:
            redis_kwargs["ssl_ca_certs"] = redis_ssl_ca
        if redis_ssl_certfile:
            redis_kwargs["ssl_certfile"] = redis_ssl_certfile
        if redis_ssl_keyfile:
            redis_kwargs["ssl_keyfile"] = redis_ssl_keyfile

        try:
            redis_client = redis_client_factory(redis_url, **redis_kwargs)
        except TypeError:
            # Backward compatibility for factories that only accept the URL.
            redis_client = redis_client_factory(redis_url)
        return RedisNotifierSLOStateStore(redis_client, key=redis_key)

    sqlite_path = source.get("TEAM_GSD_NOTIFIER_SLO_SQLITE_PATH", "artifacts/notifier_slo_state.db")
    return SqliteNotifierSLOStateStore(sqlite_path)
