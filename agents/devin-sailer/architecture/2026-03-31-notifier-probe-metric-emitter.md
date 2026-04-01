# Notifier Probe Metric Emitter

Date: 2026-03-31
Author: Devin Sailer

## Summary

Added a helper that emits structured metrics from notifier state probe results so probe health can be monitored in the same metric pipeline as ingestion/notifier telemetry.

## Implementation details

- Added `emit_notifier_slo_probe_metrics(...)` in `code/market_data/notifier_slo_state_store.py`.
- Emits:
  - `notifier.state_probe.latency_ms`
  - `notifier.state_probe.success`
  - `notifier.state_probe.failure`
- Metric tags include backend and probe result status (`ok=true|false`) plus caller-provided base tags.
- Added unit test coverage in `code/tests/test_notifier_slo_state_store.py` for emitted metric names/values/tags.
- Exported helper in `market_data.__init__`.
- Updated `code/README.md`.

## Usage

Run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_notifier_slo_state_store.py tests/test_notifier_slo_policy.py tests/test_alert_notifiers.py tests/test_ingestion_worker.py tests/test_ingestion_alerts.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py tests.integration.test_redis_notifier_slo_state_store_integration
```

Example:

```python
emit_notifier_slo_probe_metrics(probe, metric_fn=metric_sink, metric_tags={"service": "ingestion"})
```

## Known limitations or TODOs

- No histogram bucket helper is included yet; only raw latency value is emitted.
- Emitter assumes metric callback reliability and does not add retry/backoff.
- Does not currently include probe detail/error-type tag to avoid high-cardinality risk.
