# Ingestion Worker Notifier Metric Adapter

Date: 2026-03-30
Author: Devin Sailer

## Summary

Added ingestion-worker-side metric adapters so notifier metrics can be emitted with the same venue/symbol/timeframe tags as ingestion metrics. This creates a consistent observability namespace across ingestion and alert transport health.

## Implementation details

- Extended `CheckpointedIngestionWorker` with:
  - `notifier_metric_fn()` -> returns a callback compatible with notifier metric hook signature.
  - `notifier_metric_tags(**extra_tags)` -> returns default worker tags plus `component=notifier`.
- Adapter behavior:
  - merges notifier-provided tags (for example `channel`, `reason`) with worker base tags (`venue`, `symbol`, `timeframe`).
  - no-op when worker `metric_fn` is unset.
- Added unit coverage in `code/tests/test_ingestion_worker.py` for:
  - merged tag shape from `notifier_metric_fn()`
  - default component tagging from `notifier_metric_tags()`
- Updated shared code docs in `code/README.md`.

## Usage

Run tests:

```bash
cd code
PYTHONPATH=. python3 -m unittest tests/test_ingestion_worker.py tests/test_alert_notifiers.py tests/test_ingestion_alerts.py tests/test_raw_store.py tests/test_normalization.py tests/test_backtesting.py
```

Example wiring:

```python
worker = CheckpointedIngestionWorker(..., metric_fn=your_metric_sink)
sender = WebhookAlertSender(
    webhook_url="https://ops.example/hook",
    metric_fn=worker.notifier_metric_fn(),
    metric_tags=worker.notifier_metric_tags(channel="ops"),
)
```

## Known limitations or TODOs

- Adapter does not enforce a fixed notifier metric schema yet.
- No automatic linkage to dashboard definitions or alert thresholds.
- Multi-process aggregation semantics depend on the downstream metrics backend.
