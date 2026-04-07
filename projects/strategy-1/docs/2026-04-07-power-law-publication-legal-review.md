# Power Law Publication and Legal Review (TEA-96)
Date: 2026-04-07

## Executive Summary
The proposed power-law deep-dive is publishable on BartBotResearch.com if language remains research-only and avoids directive trading statements. The main legal exposure is financial-promotion/advice characterization if model outputs are framed as recommendations or deterministic outcomes. Secondary exposure comes from incomplete methodology caveats (data-history bias, model fragility, and regime dependence) and broad cross-border distribution without promotion controls. With mandatory disclaimers, section-level edits, and final legal signoff, publication risk is manageable.

## Jurisdiction(s) Affected
- United States (federal and state): SEC/CFTC anti-fraud and adviser-marketing sensitivity, FTC/state UDAP consumer-protection risk
- International distribution channels (if publicly accessible): UK/EU financial-promotion and consumer-communication regimes
- Contractual jurisdictions tied to data/vendor terms for referenced datasets and downstream reuse

## Risk Rating
Medium

## Recommended Next Action
Apply all required disclaimer and redline controls below, then submit the final publication draft for Legal spot-check before release by **2026-04-08 12:00 America/Denver**.

## Claim-Risk Review
| Claim Type | Example Draft Direction | Risk Level | Why It Matters | Required Control |
| --- | --- | --- | --- | --- |
| Deterministic outcome framing | "BTC should double in ~783 days" | High | Can be read as forecast/promise | Reframe as historical model-implied cadence with explicit uncertainty/failure caveat |
| Trading recommendation language | "best time to buy" / "accumulate now" | High | Increases investment-advice and financial-promotion risk | Remove imperative language; use descriptive regime context only |
| Cross-asset generalization | Applying BTC strength to all coins | Medium-High | Could mislead on model reliability where fit is weak (e.g., XRP) | Add asset-specific confidence and limitation language |
| Under-disclosed methodology limits | No caveat on vendor-history truncation | Medium | Omissions can create deceptive-impression risk | Require data-provenance and model-limit section near top |
| Factual historical reporting | R^2, residual percentile, trailing returns | Low | Lower risk when accurately sourced and dated | Keep source dates, method notes, and reproducibility references |

## Required Disclaimers and Language Guardrails
Use these controls in every externally visible version.

1. Standard disclaimer (near top and footer):
   "Bart Bot Research provides educational trading research and market analysis. All content is for informational purposes only. We are not registered investment advisors. Past performance is not indicative of future results. Always do your own research and never trade with money you cannot afford to lose."
2. Model-risk disclaimer (adjacent to model outputs):
   "Model outputs are probabilistic, based on historical data, and may fail under new market regimes."
3. Non-personalization disclaimer (summary/conclusion):
   "This report does not consider any reader's objectives, financial situation, or risk tolerance."
4. Data-quality disclaimer (methodology section):
   "Data is sourced from third parties and may include coverage gaps, revisions, or methodology differences."
5. Forward-looking disclaimer (scenario language):
   "Any forward-looking scenarios are illustrative research assumptions, not forecasts or guarantees."
6. Language guardrails:
   - Do not use: buy/sell instructions, "best time," "should," "will" for expected returns
   - Do use: "historically," "in-sample," "conditional," "subject to invalidation"

## Compliance Concerns by Section
| Publication Section | Key Concern | Required Compliance Treatment |
| --- | --- | --- |
| 1. Thesis and Scope | Overstated certainty | State that thesis is research framing, not investment advice |
| 2. Data Provenance | Data-rights and quality ambiguity | Name source, pull date, and limitations; avoid redistribution beyond rights |
| 3. Model Specification | Hidden assumptions | Explicitly disclose log-log OLS assumptions and limits |
| 4. Cross-Asset Results | Misleading comparability | Pair results with asset-specific reliability caveats |
| 5. Regime Dependency | Cherry-picked conditions | State favorable and unfavorable macro regimes symmetrically |
| 6. Adversarial Replication | Underreporting failure modes | Include what broke, invalidation triggers, and confidence bands |
| 7. Engineering Notes | Implied production-readiness | Clarify research prototype vs deployable system status |
| 8. Vendor-Bias Caveats | Omission of sampling bias | Keep vendor-history truncation and survivorship caveats explicit |
| 9. Legal Guardrails | Disclaimer placement drift | Keep mandatory disclaimer at top and footer before publication |
| 10. Confidence Labels | Advice-like interpretation | Label confidence as conditional research confidence only |

## Redline Guidance for Publication Draft
| Do Not Publish | Approved Replacement |
| --- | --- |
| "BTC will likely double in around 783 days." | "Under this historical specification, BTC's current model-implied doubling cadence is approximately 783 days, but outcomes have varied materially." |
| "Now is the best time to buy BTC." | "BTC currently screens at a lower historical valuation percentile in this model; this is not a buy recommendation." |
| "Use this model to trade ETH/SOL/XRP/DOGE." | "For non-BTC assets, this model is a research input with weaker fit and requires additional regime and risk filters before any deployment." |
| "Power law proves long-term upside from here." | "Power-law fit indicates historical trend structure, not proof of future returns." |
| "Subscribers should accumulate during discount regimes." | "Readers may evaluate discount-regime context within their own independent risk framework." |

## Approval Recommendation
**Conditional Approve** for publication, subject to all controls below.

Publication may proceed only if:
- Required disclaimers are present verbatim at top and footer.
- No directive trading language remains.
- All model outputs are framed as historical/conditional, not predictive promises.
- Asset-specific limitations (especially weaker-fit assets) are explicitly stated.
- Final legal spot-check confirms the edited draft before release.

If any gate fails, hold publication and return to editorial revision.
