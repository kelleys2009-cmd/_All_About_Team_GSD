# Redis Notifier SLO Integration Smoke Test

Date: 2026-03-31
Author: Devin Sailer

## Summary

Added an env-gated integration smoke test for Redis-backed notifier SLO cooldown state. The test validates real Redis round-trip behavior and dedupe semantics without impacting default local test runs.

## Implementation details

- Added integration test module:
  - `code/tests/integration/test_redis_notifier_slo_state_store_integration.py`
- Test behavior:
  - gated by `TEAM_GSD_TEST_REDIS_URL`
  - skips when Redis URL is absent or the `redis` Python package is unavailable
  - creates a unique Redis key per run
  - verifies first-send, suppressed resend inside cooldown, and resend after cooldown expiry
  - cleans up key at test end
- Reuses env-driven state-store factory for production-like initialization path.
- Updated test documentation in `code/README.md`.

## Usage

Run integration smoke test:

```bash
cd code
TEAM_GSD_TEST_REDIS_URL='redis://127.0.0.1:6379/0' \
PYTHONPATH=. python3 -m unittest tests.integration.test_redis_notifier_slo_state_store_integration
```

## Known limitations or TODOs

- Test assumes Redis endpoint is reachable and writable from the runtime environment.
- No TLS/auth-specific Redis variants are exercised yet.
- Current smoke test covers a single alert key path; multi-key contention is not yet covered.
