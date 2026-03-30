# Strategy #1 Live Deployment Legal Signoff Checklist
Date: 2026-03-30

## Executive Summary
This checklist defines the minimum legal and compliance controls required before any live deployment of Strategy #1. The immediate objective is to constrain launch to a defensible proprietary-trading perimeter while preserving a clear approval path for later expansion. Items below are structured as go/no-go gates so legal, engineering, and leadership can document readiness. Any unchecked High-risk item blocks launch.

## Jurisdiction(s) Affected
- United States (federal + state)
- Venue/vendor contractual jurisdictions
- Any non-US jurisdictions targeted for onboarding

## Risk Rating
High

## Recommended Next Action
Run this checklist as a formal gate review and obtain written signoff from Legal, Engineering, and CEO by **2026-04-10**.

## Go/No-Go Checklist
### A. Operating Scope and Entity
- [ ] Launch mode confirmed as proprietary capital only (no customer custody/order handling)
- [ ] Legal entity and ownership for strategy operations documented
- [ ] IP ownership and invention-assignment coverage verified for employees/contractors

### B. Venue, Counterparty, and Data Rights
- [ ] Approved venue list documented with jurisdiction eligibility per venue
- [ ] Venue/API terms reviewed for prohibited trading behavior and account-control limits
- [ ] Data-license entitlement matrix completed (internal, display, derived, redistribution)
- [ ] Custody/collateral/clawback provisions reviewed for each venue/counterparty
- [ ] Governing-law, dispute-resolution, indemnity, and liability cap positions accepted

### C. Market Conduct and Surveillance
- [ ] Pre-trade manipulative-pattern guardrails configured (spoofing/layering/wash-risk)
- [ ] Cancel/fill ratio and order-pattern alerts configured and tested
- [ ] Thin-liquidity safeguards defined for approved assets
- [ ] Escalation protocol documented for surveillance alerts and incident handling

### D. AML/KYC, Sanctions, and Geographic Controls
- [ ] Sanctions-screening workflow documented for counterparties and vendors
- [ ] Restricted-jurisdiction and geofencing controls validated
- [ ] AML/KYC trigger policy defined for any future customer-facing phase
- [ ] OFAC/export-control escalation owner assigned

### E. Records, Privacy, and Security
- [ ] Immutable audit log coverage verified for order lifecycle and strategy decisions
- [ ] Access logging and privileged-action monitoring enabled
- [ ] Records retention schedule approved for orders, communications, and incidents
- [ ] Privacy data inventory completed for logs/telemetry and deletion pathways
- [ ] Security incident response + legal notification workflow approved

### F. Governance and Change Control
- [ ] Material strategy-change approval workflow documented and tested
- [ ] New venue/new asset/new product expansion requires legal approval gate
- [ ] Compliance evidence package archived and version-controlled
- [ ] Board-level signoff captured for launch perimeter

## Approval Record
- Legal Counsel: Pending
- Founding Engineer: Pending
- CEO: Pending
- Target Signoff Date: 2026-04-10

## Blockers
- Pending legal-intake responses on open issues currently prevent final consolidated risk closure.
- Customer-capital, leverage/derivatives, staking, lending, and non-US rollout remain out of scope until dedicated approvals are complete.
