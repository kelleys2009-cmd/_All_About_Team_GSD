# Legal Intake: Roy Finance Research Workstream
Date: 2026-03-30

## Executive Summary
I identified five legal/compliance concerns that could materially affect Roy's finance research outputs and downstream trading workflows. The highest-priority risks are data licensing/terms-of-use violations and regulatory characterization of published research as investment advice, each with potential to halt data access or trigger enforcement. Medium-priority risks include privacy and sanctions/export controls when ingesting external datasets or serving global users. Immediate controls are disclosure standards, source-level license inventories, and pre-release compliance checks before strategy outputs are published or automated.

## Data Sources
- Roy workstream scope from issue [TEA-39](/TEA/issues/TEA-39) and parent checklist [TEA-37](/TEA/issues/TEA-37)
- Current operating context: Team GSD workspace policies and research remit (US-based, global data intake possible)
- Time period assessed: current-state intake on 2026-03-30 (forward-looking for next 30-90 days)
- Assets covered: market data feeds, research artifacts, model/signal outputs, distribution channels

## Methodology
- Mapped Roy's workflow into legal risk domains requested by Legal: domestic, international, contractual/IP, privacy, sanctions/export, employment/insurance.
- Assigned risk ratings using a simple two-factor screen: likelihood (next 90 days) and impact (operational/regulatory).
- Estimated business impact in operational terms (potential downtime, rework, blocked launches).
- Defined action owners and decision deadlines to make follow-through auditable.

## Results
| # | Concern Summary | Jurisdiction(s) | Risk | Decision Deadline | Business Impact (Quantified) | Recommended Next Action |
|---|---|---|---|---|---|---|
| 1 | Market data licensing and redistribution restrictions (API ToS, derived-data sharing rights) | US (contract), EU/UK if non-US sources used | High | 2026-04-05 | Could force removal/rebuild of 100% of affected signals using restricted fields; potential 1-3 week research freeze for remediation | Build source-level license matrix; block publication of outputs where redistribution rights are unclear; legal review for top 10 sources by usage |
| 2 | Research outputs interpreted as investment advice or regulated solicitation | US federal/state (SEC/CFTC + state securities), non-US where distributed | High | 2026-04-10 | Potential cease-and-desist risk and forced channel shutdown for external-facing reports; could delay launch milestones by 2-4 weeks | Standardize disclaimers, audience restrictions, and "research only / not investment advice" controls; require legal sign-off before external release |
| 3 | Personal data processing in alt-data pipelines (even incidental identifiers) | US state privacy (e.g., CA), EU GDPR/UK GDPR if EU residents included | Medium | 2026-04-15 | Non-compliant data could require purge/reingestion of affected datasets (estimated 3-7 days rework per dataset) | Add data classification gate; prohibit ingestion of direct identifiers without approved lawful basis and retention policy |
| 4 | Sanctions and export-control exposure for counterparties, vendors, or distribution | US OFAC/EAR; potentially UK/EU sanctions regimes | Medium | 2026-04-15 | Could block onboarding of specific vendors/users and suspend cross-border data access paths | Add sanctions screening for vendors/users in distribution workflow; maintain deny-list controls and audit log |
| 5 | IP provenance and model/document reuse rights (papers, code snippets, content licenses) | US copyright/contract; international copyright where sourced | Medium | 2026-04-20 | Unclear rights could force takedown/rewrite of published notes or code modules (1-2 weeks remediation for major artifacts) | Require citation + license metadata for external code/content; pre-merge check for license compatibility |

## Implications
- Strategy publication velocity should remain gated by legal controls for external distribution until high-risk controls (#1 and #2) are implemented.
- Internal research can continue, but production-facing signal delivery should add compliance checkpoints to avoid rework.
- Cross-functional coordination is required with legal intake owner (Brandon), macro research (Chris), and backtesting infra (Devin) before scaling automated signals.

## Confidence Level
Medium. The risk categories and priorities are robust for a first-pass intake, but confidence is limited by the absence of finalized vendor contracts, specific distribution channels, and a confirmed jurisdiction list for end users.

## Open Questions
- Which exact data vendors and contracts are in scope for the first production release?
- Will any research outputs be customer-facing, or strictly internal?
- Are EU/UK resident users or datasets in scope in the next two quarters?
- What insurance coverage currently applies to research publication and advisory exposure?
