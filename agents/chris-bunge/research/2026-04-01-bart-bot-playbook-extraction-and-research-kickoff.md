# Bart Bot Research Playbook Extraction and Kickoff
Date: 2026-04-01

## Executive Summary
The Bart Bot project playbook is now extracted and operationalized into a concrete weekly research workflow, with explicit ownership, deadlines, and quality controls centered on a Monday 05:00 MST publish cadence. The first report brief is confirmed as a Bitcoin power-law study, with Roy leading model development and Chris leading adversarial falsification. Existing Team GSD artifacts already provide a partial analytical base for this topic, including an OLS/quantile review that supports the ~13% lifespan-doubling heuristic while warning about large regime dispersion. Immediate execution risk is workflow-location ambiguity: the configured project workspace path does not currently exist on disk, so a synchronized snapshot path was used to unblock kickoff work. The team can proceed now, but workspace normalization is required before production handoff.

## Context
Issue [TEA-74](/TEA/issues/TEA-74) requested: "pull all the information from the MD file in this project and get started." The project is "Bart Bot Website Research" and the referenced markdown was identified as `BBR-AGENT-PLAYBOOK.md` (project playbook + first report brief) in a synced local snapshot at `/Users/amonkelley/Downloads/.../bart-bot-research/`.

Scope of this kickoff memo:
- Extract actionable operating requirements from the playbook
- Map those requirements to current Team GSD artifacts
- Define immediate next-step execution path for Report #1

## Data/Evidence
Primary source extracted:
- `BBR-AGENT-PLAYBOOK.md` (contains production schedule, role-level instructions, and Report #1 brief)

Key directives captured from playbook:
- Publish cadence: every Monday at 05:00 MST
- Weekly sequence: Roy research scan/draft (Thu-Fri), Chris adversarial review (Sat AM), Irene signal summary (Sat EOD), AK final review (Sun AM), Irene final formatting (Sun PM)
- Chris review checklist for each idea: cost survival, beta decomposition, momentum proxy, vol proxy, concentration, sensitivity, data integrity, regime dependency, capacity, crowding
- First report assignment: Bitcoin Power Law (Roy primary, Chris review), including OLS on log-log age curve, quantile corridor analysis, and validation of "13% lifespan -> ~2x price" claim

Cross-referenced internal evidence:
- Roy research baseline (methodology and implementation ranking framework): `agents/roy/research/2026-03-30-novel-strategy-scan-public-papers.md`
- Devin platform constraints and reliability status: `agents/devin-sailer/2026-03-30-strategy-sync-brief.md`
- Existing BTC power-law empirical analysis in Team GSD: `projects/strategy-1/research/2026-03-31-bitcoin-power-law-ols-and-quantile-review.md`
  - Reported OLS exponent ~5.68, R^2 ~0.961, and implied doubling at ~12.97% network-age increase

## Analysis
The playbook is operationally specific enough to execute immediately: sequencing, owners, report structure, and quality gates are explicit. For Chris's lane, the review mandate is clear and should be treated as a falsification protocol rather than editorial commentary.

The first-report topic (Bitcoin power law) is already partially de-risked by existing internal work: the 2026-03-31 analysis supports the central heuristic while also showing broad residual dispersion and weak near-term timing precision. This means the likely high-quality output stance is: structural model is useful as valuation/regime envelope, but not a standalone short-horizon trade trigger.

A practical blocker remains at the environment layer: project metadata points to `/Users/amonkelley/Projects/bart-bot-research/`, but that path is missing. Work was unblocked via the synced snapshot copy in Downloads, which is acceptable for kickoff but fragile for weekly production unless normalized.

## Implications
- Research process can start now for the Monday publication cycle without waiting on new framework design.
- Chris review should enforce a strict reject/revise bias unless Roy demonstrates net-of-cost robustness and model distinctiveness versus simple momentum/beta proxies.
- Existing power-law analysis should be treated as a seed artifact, then upgraded into the exact BBR publish format required in the playbook.
- Platform direction: Devin's infrastructure constraints imply any recurring analytics should favor reproducible daily pipelines before higher-frequency complexity.
- Operationally, owner should normalize the project workspace path to prevent missed handoffs or stale-source risk.

## Open Questions
- Which path is canonical for Bart Bot going forward: `/Users/amonkelley/Projects/bart-bot-research/` or the synced snapshot location?
- Is Roy's first draft already available for Saturday adversarial review, or does TEA-74 represent pre-draft setup only?
- Should the existing 2026-03-31 BTC power-law memo be treated as upstream input to Roy's report, or as a separate independent check by Chris?
- What is the required storage location for final publish-ready BBR reports inside Team GSD (project repo vs shared docs)?

## Confidence Level
Medium.

Confidence is high that the playbook directives and first-report requirements were extracted accurately from the source markdown. Confidence is medium on execution continuity because the configured project workspace path is currently unresolved, creating potential source-of-truth drift until path normalization is completed.
