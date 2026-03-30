# Strategy #1 Consolidated Legal Risk Register
Date: 2026-03-30

## Executive Summary
All legal intake responses for the Team GSD legal checklist are now complete and consolidated in this register. The highest-priority launch risks are regulatory classification/licensing posture, AML/KYC and sanctions controls, market-data licensing restrictions, and market-conduct surveillance readiness. Medium-priority risks center on privacy governance, IP/licensing chain-of-title, employment/insurance readiness, and cross-border compliance scaling. Strategy #1 should continue only within a tightly scoped proprietary-trading perimeter until High-risk controls are implemented and evidenced.

## Jurisdiction(s) Affected
- United States federal: SEC, CFTC, FinCEN/BSA-AML, OFAC, BIS/EAR
- United States state: securities, privacy, employment/tax, and money-transmission analyses as applicable
- Potential non-US exposure: UK/EU (including privacy/market-abuse analogs), plus venue/vendor contractual jurisdictions

## Risk Rating
High

## Recommended Next Action
Approve and execute the High-risk action plan below by **2026-04-10** for launch gating, with remaining medium-risk control milestones completed no later than **2026-04-30**.

## Consolidated Risk Register
| ID | Risk | Jurisdiction(s) | Rating | Business Impact | Owner | Required Action | Deadline |
|---|---|---|---|---|---|---|---|
| LR-01 | Licensing/registration misclassification for platform model (broker-dealer/ATS/commodity derivatives/MSB-adjacent triggers) | US federal + state | High | Launch delay, enforcement exposure, partner onboarding friction | Legal + CEO | Complete written licensing matrix tied to product scope and entity structure | 2026-04-10 |
| LR-02 | AML/KYC and sanctions controls not production-ready for onboarding or counterparties | US (BSA/OFAC) + non-US sanctions overlaps | High | Penalties, onboarding freeze, operational interruptions | Legal + Engineering | Implement sanctions screening, escalation workflow, and evidence-grade logs | 2026-04-10 |
| LR-03 | Market-data licensing/redistribution violations across feeds and derived data | US + venue/vendor contract jurisdictions | High | Contract breach, retroactive fees, potential data shutdown | Legal + Research + Engineering | Publish source-by-source entitlement matrix and gate usage by rights | 2026-04-05 |
| LR-04 | Research outputs potentially characterized as investment advice/solicitation | US federal/state; non-US marketing regimes where applicable | High | Forced content changes, registration risk, go-to-market delay | Legal + Research | Enforce disclaimer policy and pre-publication legal signoff | 2026-04-10 |
| LR-05 | Market-conduct/surveillance controls insufficient (spoofing/layering/wash-risk patterns) | US (SEC/CFTC) + potential UK/EU analogs | High | Regulatory/reputational exposure and venue restrictions | Engineering + Legal | Deploy surveillance alerts and escalation playbook with retention evidence | 2026-04-10 |
| LR-06 | Privacy controls incomplete for telemetry, alt-data, and user/account data | US state privacy + potential GDPR/UK GDPR | Medium | Rework, remediation cost, trust impact, possible regulatory action | Legal + Engineering | Finalize data map, retention schedule, and deletion/rights workflows | 2026-04-15 |
| LR-07 | IP chain-of-title and OSS/license compliance gaps in code/models/data/vendor SDKs | US/international copyright + contract | Medium | Takedown/rewrite risk, diligence friction, commercialization constraints | Legal + Engineering | Enforce SBOM/license checks and IP assignment coverage | 2026-04-20 |
| LR-08 | Export-control/geofencing controls not aligned with global availability plans | US (OFAC/BIS/EAR) + non-US sanctions interplay | Medium | Restricted-region access risk, penalties, remediation overhead | Engineering + Legal | Validate jurisdiction controls in onboarding and account lifecycle | 2026-04-15 |
| LR-09 | Money-transmission/custody exposure if product scope expands beyond proprietary model | US federal + multi-state MTL analyses | High | Major licensing burden and architecture redesign risk | CEO + Legal + Engineering | Keep Phase 1 non-custodial; require approval gate before scope expansion | 2026-04-10 |
| LR-10 | Employment/tax nexus and insurance coverage not aligned with scaling plan | US state/federal + insurance contracts | Medium | Hiring friction, balance-sheet risk, enterprise deal blockers | CEO + Legal | Standardize hiring compliance checklist and insurance coverage review | 2026-04-30 |

## Current Launch Perimeter Recommendation
- Approved for initial execution:
  - Proprietary capital only
  - Approved venues and assets under legal-reviewed terms
  - No customer custody/order-routing for external clients
- Not approved without additional legal decision memo:
  - Customer-capital products
  - Leverage/derivatives/staking/lending expansion
  - Broad non-US onboarding

## Source Intake Coverage
- Completed intake issues: [TEA-38](/TEA/issues/TEA-38), [TEA-39](/TEA/issues/TEA-39), [TEA-40](/TEA/issues/TEA-40), [TEA-41](/TEA/issues/TEA-41), [TEA-42](/TEA/issues/TEA-42)
- Parent legal checklist issue: [TEA-37](/TEA/issues/TEA-37)

## Open Decisions Requiring Leadership Signoff
- Confirm final Phase 1 jurisdiction list and prohibited jurisdictions
- Confirm whether any customer-facing capability remains out of scope until licensing analysis is complete
- Confirm legal/compliance evidence package owner and weekly reporting cadence
