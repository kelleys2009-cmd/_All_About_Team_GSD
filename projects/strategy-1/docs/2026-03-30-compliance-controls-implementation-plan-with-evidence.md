# Compliance Controls Implementation Plan with Evidence
Date: 2026-03-30
Author: Devin Sailer

## Summary
This document defines the engineering implementation plan and evidence package for Strategy #1 launch compliance controls required for legal signoff by 2026-04-10. The scope covers immutable audit logging, privileged-access monitoring, conduct-surveillance alerts, and records-retention mapping so Legal and Engineering can evaluate completeness against launch gates with concrete artifacts.

## Implementation details
### 1) Immutable audit-log coverage map
Control objective: Every material trading action and strategy decision is captured in immutable, queryable logs with actor, timestamp, inputs, outputs, and decision rationale.

Coverage map:
- Order lifecycle events (OMS/exchange connectivity):
  - `order.submitted`
  - `order.acknowledged`
  - `order.partially_filled`
  - `order.filled`
  - `order.canceled`
  - `order.rejected`
  - `order.amended`
- Strategy decision events (strategy layer):
  - `signal.generated`
  - `signal.filtered`
  - `risk.check_passed`
  - `risk.check_failed`
  - `execution.intent_created`

Required fields for all events:
- `event_id` (UUIDv7)
- `event_type`
- `occurred_at_utc` (RFC3339)
- `trace_id`
- `strategy_id`
- `account_id`
- `instrument`
- `actor_type` (`human|service|strategy`)
- `actor_id`
- `source_host`
- `payload_hash_sha256`
- `prev_event_hash_sha256` (hash chain anchor)

Storage and immutability design:
- Primary write path: application emits JSON logs to append-only stream.
- Persistence: PostgreSQL/TimescaleDB table `audit_events` with row-level insert-only policy for service role.
- Tamper-evidence: hash chaining by entity stream plus daily Merkle-root snapshot stored in object storage and copied to an independent backup bucket.
- Access model: read via compliance role; write restricted to service account.

Evidence artifacts:
- Schema migration for `audit_events` and indexes.
- Sample event exports from each lifecycle state and strategy decision state.
- Daily integrity check job report (hash-chain verification + root snapshot ID).

### 2) Access logging and privileged-action monitoring plan
Control objective: Every privileged action is attributable and reviewable.

Privileged action scope:
- Deployment approvals/rollbacks
- Strategy parameter updates
- Exchange API key rotation
- Risk limit overrides
- Manual order interventions

Implementation:
- Enforce authenticated admin actions through a single control-plane API.
- Emit `privileged.action` event with actor identity, action diff, approval reference, and justification.
- Mirror authn/authz decisions into audit stream (`access.granted`, `access.denied`).
- Daily anomaly job flags:
  - repeated denied attempts (>10/hour per actor)
  - out-of-hours privileged actions
  - action without approval reference when required

Observability dependencies:
- Structured logging (JSON)
- Metrics counters: `privileged_actions_total`, `access_denied_total`
- Alert routes: Slack + pager for critical anomalies

Evidence artifacts:
- RBAC policy snapshot (roles/permissions matrix)
- 7-day privileged-action report export
- Alert test evidence (fired + acknowledged)

### 3) Conduct-surveillance alert design
Control objective: Detect suspicious or manipulative execution behavior and operational anomalies.

Alert set (phase 1):
- Cancel-to-fill ratio breach:
  - Trigger: ratio > configured threshold over rolling 15-minute window per account/strategy.
- Burst-cancel pattern:
  - Trigger: consecutive cancel bursts near touch level within short interval.
- Layering-like quote churn heuristic:
  - Trigger: repeated placement/cancel at multiple price levels without execution persistence.
- Unusual fill slippage anomaly:
  - Trigger: execution slippage z-score above threshold vs intraday baseline.

Implementation:
- Stream processor computes rolling metrics from order/execution events.
- Alerts written to `surveillance_alerts` table and pushed to incident channel.
- Every alert includes replay context: last N related orders/events and feature values.
- Analyst workflow: triage status (`new|investigating|closed`), disposition, notes.

Evidence artifacts:
- Alert rule config file and threshold rationale
- Backtest/replay output on last 30 days of data (precision/false positive review)
- Triage runbook and sample closed investigations

### 4) Records-retention mapping
Control objective: Retain required records for legal/regulatory review, retrieval, and auditability.

System mapping:
- OMS + execution events -> `audit_events` (TimescaleDB)
- Strategy configs/versioning -> Git repo + release metadata table
- Market data snapshots used in decisions -> parquet object storage partitioned by date/venue
- Access/auth logs -> `audit_events` + auth provider logs
- Surveillance cases -> `surveillance_alerts` + case notes store

Retention policy (initial legal gate defaults pending final legal confirmation):
- Trading/audit events: 7 years
- Access logs: 2 years hot + archive to 7 years
- Surveillance investigations: 7 years
- Config and release artifacts: permanent while strategy active, then 7 years

Controls:
- Immutable backups with lifecycle lock
- Monthly restore drill for random sample records
- Record retrieval SLA: <= 24 hours for legal requests

Evidence artifacts:
- Retention policy config (DB and object lifecycle)
- Restore drill report template and latest run output
- Record retrieval checklist and sample request completion log

### Delivery timeline to legal signoff gate (2026-04-10)
Milestones:
- 2026-03-31:
  - Finalize control schemas (`audit_events`, `surveillance_alerts`)
  - Approve event taxonomy and required fields
- 2026-04-02:
  - Complete immutable logging write path in OMS + strategy services
  - Enable privileged action eventing
- 2026-04-04:
  - Deploy surveillance phase-1 alerts in shadow mode
  - Start false-positive calibration
- 2026-04-06:
  - Freeze retention configs and backup lifecycle policies
  - Execute first restore drill and integrity verification
- 2026-04-08:
  - Assemble evidence package (exports, reports, config snapshots)
  - Internal engineering/legal review session
- 2026-04-10:
  - Legal signoff gate submission with final evidence bundle

Dependencies and owners:
- Engineering (Devin): schemas, pipelines, monitoring, evidence exports
- Legal (Tanya + counsel): acceptance criteria finalization and signoff
- Ops: alert routing and on-call validation

## Usage
How to use this document:
- Use as source-of-truth checklist for implementation work through 2026-04-10.
- Attach listed evidence artifacts to the legal signoff packet as they are produced.
- Track milestone completion in task updates and include links to artifact locations.

Execution guidance:
- Prioritize immutable audit logging and privileged-access instrumentation first.
- Run surveillance in shadow mode before enforcing operational responses.
- Perform at least one restore drill before legal review.

## Known limitations or TODOs
- Final legal acceptance thresholds for surveillance rules are not yet confirmed.
- Retention durations are provisional defaults pending counsel confirmation.
- Cross-venue harmonization for alert features may require venue-specific calibration.
- Need dedicated dashboard views for compliance users to reduce manual report assembly.
