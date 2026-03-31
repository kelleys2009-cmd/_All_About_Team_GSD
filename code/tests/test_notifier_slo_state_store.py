from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from market_data.ingestion_alerts import IngestionAlert
from market_data.notifier_slo_policy import NotifierSLOCooldownPolicy
from market_data.notifier_slo_state_store import (
    NotifierSLOStateStoreProbeResult,
    NotifierSLOStateEnvDebugSnapshot,
    RedisNotifierSLOStateStore,
    SqliteNotifierSLOStateStore,
    build_notifier_slo_state_env_debug_snapshot,
    create_notifier_slo_state_store_from_env,
    dedupe_notifier_slo_alerts_with_store,
    probe_notifier_slo_state_store_connectivity,
    redact_notifier_slo_state_env,
    validate_notifier_slo_state_env,
)


class _FakeRedis:
    def __init__(self) -> None:
        self._data: dict[str, dict[str, int]] = {}
        self._kv: dict[str, str] = {}

    def hget(self, key: str, field: str) -> str | None:
        bucket = self._data.get(key, {})
        value = bucket.get(field)
        return None if value is None else str(value)

    def hgetall(self, key: str) -> dict[str, str]:
        bucket = self._data.get(key, {})
        return {field: str(value) for field, value in bucket.items()}

    def hset(self, key: str, mapping: dict[str, int]) -> None:
        bucket = self._data.setdefault(key, {})
        for field, value in mapping.items():
            bucket[field] = int(value)

    def ping(self) -> bool:
        return True

    def set(self, key: str, value: str) -> None:
        self._kv[key] = str(value)

    def get(self, key: str) -> str | None:
        return self._kv.get(key)

    def delete(self, key: str) -> None:
        self._kv.pop(key, None)


class NotifierSLOStateStoreTests(unittest.TestCase):
    def test_probe_connectivity_sqlite_and_redis(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sqlite_store = SqliteNotifierSLOStateStore(Path(tmp) / "notifier_slo_state.db")
            sqlite_probe = probe_notifier_slo_state_store_connectivity(sqlite_store)
            self.assertIsInstance(sqlite_probe, NotifierSLOStateStoreProbeResult)
            self.assertTrue(sqlite_probe.ok)
            self.assertEqual(sqlite_probe.backend, "sqlite")
            self.assertGreaterEqual(sqlite_probe.latency_ms, 0.0)

        redis_store = RedisNotifierSLOStateStore(_FakeRedis(), key="test:notifier")
        redis_probe = probe_notifier_slo_state_store_connectivity(redis_store)
        self.assertTrue(redis_probe.ok)
        self.assertEqual(redis_probe.backend, "redis")
        self.assertGreaterEqual(redis_probe.latency_ms, 0.0)
        redis_write_probe = probe_notifier_slo_state_store_connectivity(redis_store, write_check=True)
        self.assertTrue(redis_write_probe.ok)
        self.assertIn("read/write", redis_write_probe.detail)

    def test_probe_connectivity_redis_write_check_missing_methods(self) -> None:
        class _ReadOnlyRedis(_FakeRedis):
            set = None  # type: ignore
            get = None  # type: ignore
            delete = None  # type: ignore

        redis_store = RedisNotifierSLOStateStore(_ReadOnlyRedis(), key="test:notifier")
        probe = probe_notifier_slo_state_store_connectivity(redis_store, write_check=True)
        self.assertFalse(probe.ok)
        self.assertIn("RuntimeError", probe.detail)

    def test_probe_timeout_budget(self) -> None:
        times = [100.0, 100.5]

        def fake_now() -> float:
            return times.pop(0)

        store = RedisNotifierSLOStateStore(_FakeRedis(), key="test:notifier")
        probe = probe_notifier_slo_state_store_connectivity(store, timeout_ms=100.0, now_fn=fake_now)
        self.assertFalse(probe.ok)
        self.assertIn("timeout budget", probe.detail)

    def test_probe_connectivity_redis_failure(self) -> None:
        class _BrokenRedis(_FakeRedis):
            def ping(self) -> bool:
                raise RuntimeError("unreachable")

        redis_store = RedisNotifierSLOStateStore(_BrokenRedis(), key="test:notifier")
        probe = probe_notifier_slo_state_store_connectivity(redis_store)
        self.assertFalse(probe.ok)
        self.assertIn("RuntimeError", probe.detail)

    def test_build_debug_snapshot_combines_validation_and_redaction(self) -> None:
        snapshot = build_notifier_slo_state_env_debug_snapshot(
            {
                "TEAM_GSD_NOTIFIER_SLO_STATE_BACKEND": "redis",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_SSL": "true",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_PASSWORD": "secret",
            }
        )
        self.assertIsInstance(snapshot, NotifierSLOStateEnvDebugSnapshot)
        self.assertEqual(snapshot.backend, "redis")
        self.assertFalse(snapshot.valid)
        self.assertTrue(any("REDIS_URL" in error for error in snapshot.errors))
        self.assertEqual(snapshot.redacted_env["TEAM_GSD_NOTIFIER_SLO_REDIS_PASSWORD"], "***REDACTED***")

    def test_validate_env_for_redis_secure_config(self) -> None:
        errors = validate_notifier_slo_state_env(
            {
                "TEAM_GSD_NOTIFIER_SLO_STATE_BACKEND": "redis",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_URL": "redis://cache:6379/0",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_SSL": "true",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CA_CERT": "/etc/ssl/ca.pem",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CERTFILE": "/etc/ssl/client.crt",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_KEYFILE": "/etc/ssl/client.key",
            }
        )
        self.assertEqual(errors, [])

    def test_validate_env_reports_missing_fields(self) -> None:
        errors = validate_notifier_slo_state_env(
            {
                "TEAM_GSD_NOTIFIER_SLO_STATE_BACKEND": "redis",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_SSL": "true",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CERTFILE": "/etc/ssl/client.crt",
            }
        )
        self.assertTrue(any("REDIS_URL" in error for error in errors))
        self.assertTrue(any("SSL_CA_CERT" in error for error in errors))
        self.assertTrue(any("CERTFILE and TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_KEYFILE" in error for error in errors))

    def test_redact_env_masks_sensitive_fields(self) -> None:
        redacted = redact_notifier_slo_state_env(
            {
                "TEAM_GSD_NOTIFIER_SLO_REDIS_PASSWORD": "super-secret",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_KEYFILE": "/etc/ssl/private/client.key",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CERTFILE": "/etc/ssl/certs/client.crt",
            }
        )
        self.assertEqual(redacted["TEAM_GSD_NOTIFIER_SLO_REDIS_PASSWORD"], "***REDACTED***")
        self.assertEqual(redacted["TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_KEYFILE"], "***REDACTED***")
        self.assertEqual(redacted["TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CERTFILE"], "/etc/ssl/certs/client.crt")

    def test_factory_defaults_to_sqlite(self) -> None:
        store = create_notifier_slo_state_store_from_env(
            env={"TEAM_GSD_NOTIFIER_SLO_SQLITE_PATH": "/tmp/teamgsd-state.db"}
        )
        self.assertIsInstance(store, SqliteNotifierSLOStateStore)

    def test_factory_uses_redis_backend(self) -> None:
        seen_urls: list[str] = []

        def redis_factory(url: str) -> object:
            seen_urls.append(url)
            return _FakeRedis()

        store = create_notifier_slo_state_store_from_env(
            env={
                "TEAM_GSD_NOTIFIER_SLO_STATE_BACKEND": "redis",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_URL": "redis://cache:6379/2",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_KEY": "teamgsd:test:key",
            },
            redis_client_factory=redis_factory,
        )
        self.assertIsInstance(store, RedisNotifierSLOStateStore)
        self.assertEqual(seen_urls, ["redis://cache:6379/2"])

    def test_factory_passes_redis_auth_tls_options(self) -> None:
        seen: list[tuple[str, dict[str, object]]] = []

        def redis_factory(url: str, **kwargs: object) -> object:
            seen.append((url, dict(kwargs)))
            return _FakeRedis()

        store = create_notifier_slo_state_store_from_env(
            env={
                "TEAM_GSD_NOTIFIER_SLO_STATE_BACKEND": "redis",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_URL": "rediss://secure-cache:6380/0",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_USERNAME": "teamgsd",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_PASSWORD": "secret",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_SSL": "true",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CA_CERT": "/etc/ssl/ca.pem",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_CERTFILE": "/etc/ssl/client.crt",
                "TEAM_GSD_NOTIFIER_SLO_REDIS_SSL_KEYFILE": "/etc/ssl/client.key",
            },
            redis_client_factory=redis_factory,
        )
        self.assertIsInstance(store, RedisNotifierSLOStateStore)
        self.assertEqual(
            seen,
            [
                (
                    "rediss://secure-cache:6380/0",
                    {
                        "username": "teamgsd",
                        "password": "secret",
                        "ssl": True,
                        "ssl_ca_certs": "/etc/ssl/ca.pem",
                        "ssl_certfile": "/etc/ssl/client.crt",
                        "ssl_keyfile": "/etc/ssl/client.key",
                    },
                )
            ],
        )

    def test_factory_redis_requires_factory(self) -> None:
        with self.assertRaises(ValueError):
            create_notifier_slo_state_store_from_env(
                env={"TEAM_GSD_NOTIFIER_SLO_STATE_BACKEND": "redis"}
            )

    def test_sqlite_state_store_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SqliteNotifierSLOStateStore(Path(tmp) / "notifier_slo_state.db")
            store.save_state({"notifier_delivery_drop": 1234})
            self.assertEqual(store.get_last_sent_ms("notifier_delivery_drop"), 1234)
            self.assertEqual(store.load_state(), {"notifier_delivery_drop": 1234})

    def test_dedupe_with_store_persists_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SqliteNotifierSLOStateStore(Path(tmp) / "notifier_slo_state.db")
            alerts = [
                IngestionAlert(
                    name="notifier_delivery_drop",
                    severity="high",
                    message="drop",
                )
            ]

            first = dedupe_notifier_slo_alerts_with_store(
                alerts,
                now_ms=1000,
                store=store,
                cooldown_policy_by_alert={"notifier_delivery_drop": NotifierSLOCooldownPolicy(cooldown_ms=5000)},
            )
            self.assertEqual(len(first), 1)

            second = dedupe_notifier_slo_alerts_with_store(
                alerts,
                now_ms=2000,
                store=store,
                cooldown_policy_by_alert={"notifier_delivery_drop": NotifierSLOCooldownPolicy(cooldown_ms=5000)},
            )
            self.assertEqual(second, [])

            third = dedupe_notifier_slo_alerts_with_store(
                alerts,
                now_ms=7000,
                store=store,
                cooldown_policy_by_alert={"notifier_delivery_drop": NotifierSLOCooldownPolicy(cooldown_ms=5000)},
            )
            self.assertEqual(len(third), 1)

    def test_redis_state_store_round_trip(self) -> None:
        redis_client = _FakeRedis()
        store = RedisNotifierSLOStateStore(redis_client, key="test:notifier_slo")
        store.save_state({"notifier_delivery_drop": 3333})
        self.assertEqual(store.get_last_sent_ms("notifier_delivery_drop"), 3333)
        self.assertEqual(store.load_state(), {"notifier_delivery_drop": 3333})


if __name__ == "__main__":
    unittest.main()
