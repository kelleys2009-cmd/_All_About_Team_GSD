# Strategy #1 Regulatory Operating Perimeter Memo
Date: 2026-03-30

## Executive Summary
Strategy #1 can proceed in a limited proprietary-trading mode, but legal exposure rises quickly once the platform touches customer assets, personalized advice, derivatives access, staking, or token lending. The highest immediate risks are US registration/licensing triggers, market-conduct controls, AML/sanctions controls, and exchange/data-license contract restrictions. A phased operating model is recommended: start with approved jurisdictions, approved venues, and non-custodial proprietary activity only, then expand after control evidence is in place. Existing intake responses from engineering and research also indicate elevated risk around market-data licensing, privacy/logging retention, and policy gaps for communications and MNPI-sensitive workflows.

## Jurisdiction(s) Affected
- United States (federal and state): SEC, CFTC, FinCEN/BSA-AML, OFAC, state privacy, state money-transmission regimes
- Potential near-term non-US expansion: UK/EU, Singapore, UAE, and other venue-specific regimes depending on counterparties and users
- Contractual jurisdictions set by venue/data/vendor agreements (governing law, dispute venue, and indemnity scope)

## Risk Rating
High

## Recommended Next Action
Adopt a written legal operating perimeter and launch-gating policy by **2026-04-10**, with board approval before enabling any customer-facing trading or non-US onboarding.

## Scope Assumptions
- Team is building a trading platform that may evolve from internal proprietary trading into broader services.
- Existing activity includes research, backtesting, strategy development, and infrastructure buildout.
- Final customer model and full jurisdiction footprint are not yet fixed.

## Entity/Capital Model Risk Matrix
| Model | Core Legal Posture | Primary Trigger Risk | Current Recommendation |
|---|---|---|---|
| Proprietary capital only (house funds, no customer orders/assets) | Narrowest perimeter, but still subject to anti-fraud/manipulation, sanctions, venue contracts, and tax/entity rules | Conduct and surveillance failures, contract breaches, data-license misuse | Use this as Phase 1 launch mode |
| Managed capital (SMA/fund/advisory overlays) | Material expansion of securities/commodities/adviser obligations | Investment-adviser/commodity adviser and marketing/disclosure obligations | Defer until outside-counsel licensing matrix is complete |
| Customer capital or agency execution | Highest regulatory burden across registration, AML/KYC, custody, and consumer/commercial terms | Broker/dealer, exchange/ATS, FCM/introducing broker, MSB/MTL or analogous triggers | Out of scope for initial launch; require separate go/no-go approval |

## Product Feature Risk Uplifts
### Leverage and Derivatives
- Raises CFTC/SEC and venue-rule sensitivity, including trade-surveillance and recordkeeping burden.
- Requires explicit control design for liquidation logic, margin disclosures, and market-abuse prevention.

### Staking and Token Lending
- Increases securities-characterization and custody/asset-handling risk.
- Requires dedicated product-level legal analysis before launch, not a generic add-on policy.

### Cross-Border Access
- Introduces sanctions, export-control, local licensing, and data-transfer obligations.
- Requires geofencing and jurisdiction-based entitlement controls before self-serve global onboarding.

## Elevated Scrutiny Areas (Immediate)
- Derivatives and synthetic exposure features
- Securities vs commodity characterization uncertainty for specific assets/services
- Market manipulation perception risk (spoofing/layering/wash-trade-like patterns)
- AML/KYC and sanctions-screening controls for any counterparties or users
- MNPI-adjacent information handling and external communications controls

## Venue and Counterparty Legal Checklist
- Exchange/venue terms of service reviewed and approved before API keys are used in production
- Explicit confirmation of allowed strategy behavior, including order-cancel and quote update frequency limits
- Jurisdiction and account-eligibility checks documented for each venue
- Data license rights cataloged: internal use, display rights, derived data, redistribution rights, audit rights
- Custody and collateral terms mapped, including rehypothecation/clawback or unilateral close-out rights
- Dispute resolution, governing law, limitation-of-liability, and indemnity positions documented
- Vendor outage liability and service-credit commitments accepted by business owner and legal

## Conduct Risk Guardrails
- Pre-trade controls: blocked pattern library for spoofing/layering/wash-risk behavior
- In-trade monitoring: alerts for abnormal cancel-to-fill ratios and momentum-ignition-like bursts
- Post-trade surveillance: periodic review by compliance owner with exception logging
- Token liquidity controls: tighter participation caps and throttles for thinly traded assets
- Restricted-information workflow: document and enforce MNPI-sensitive research boundaries

## Compliance-Aware System Controls (Engineering Partnership)
- Immutable audit logs for order intent, strategy version, user/service identity, and execution outcomes
- Decision traceability: preserve strategy parameters and approval state for material changes
- Access governance: role-based access, privileged-action logging, and periodic entitlement review
- Controlled change process: legal/compliance signoff for new venue, new asset class, or new product type
- Records retention: policy-backed retention schedule for orders, communications, and incident artifacts

## Entity and Operating Model Guidance
- Prefer a ring-fenced proprietary trading vehicle for Phase 1 with clean IP assignment and confidentiality coverage.
- Avoid commingling customer-like functions until licensing analysis is completed and approved.
- Require contractor and employee invention-assignment agreements for all strategy code and research outputs.
- Use standard vendor and data-contract legal review before production reliance.

## Contracting Priorities
- Market-data licensing and redistribution controls
- Cloud and infrastructure security obligations, including breach-notice timelines
- Vendor confidentiality, IP ownership, indemnity carve-outs, and liability caps
- Termination/transition rights to reduce lock-in risk for critical trading infrastructure

## Intake Signals Incorporated (Current)
- Completed legal-intake responses identified recurring high-priority risks in:
  - registration/licensing posture
  - AML/KYC and sanctions controls
  - market-data licensing restrictions
  - privacy and retention controls
  - communications/MNPI policy requirements
- Remaining intake responses are still pending and may change the final risk ranking.

## Deployment Perimeter (Current Recommendation)
- Allowed now:
  - proprietary trading only
  - approved US-friendly venues only
  - approved asset list with liquidity and conduct controls
- Not allowed at initial launch without additional approval:
  - customer funds/order handling
  - leverage/derivatives/staking/lending product expansion
  - non-US user onboarding

## Decision Deadlines
- By 2026-04-03: finalize list of intended launch venues, assets, and jurisdictions
- By 2026-04-10: approve legal operating perimeter and signoff checklist
- By 2026-04-17: complete control evidence package (audit logging, access logging, retention, surveillance)
