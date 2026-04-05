# Multi-Coin Research Claims and Subscriber Language Risk Memo (TEA-79)
Date: 2026-04-05

## Executive Summary
Current BTC V2 and multi-coin draft language is directionally compliant but still contains phrases that could be interpreted as investment recommendations when read by retail subscribers. The highest-risk statements are prescriptive buy-timing language ("best time to buy") and any wording that implies predictable return outcomes from model signals. With strict disclaimer placement, neutralized phrasing, and prohibition of deterministic language, publication risk is manageable. Until those edits are applied, publication risk remains elevated.

## Jurisdiction(s) Affected
- United States (federal and state): SEC/CFTC anti-fraud and adviser-marketing sensitivity, consumer-protection exposure, state unfair/deceptive practice standards
- International distribution channels (if report is externally available): UK/EU and other local regimes governing financial promotions and retail-facing market communications

## Risk Rating
High (pre-redline); Medium (post-redline with mandatory disclaimer controls)

## Recommended Next Action
Implement all redlines and disclaimer controls below before Sunday final approval, with legal spot-check completed by **2026-04-05 20:00 America/Denver**.

## 1) Risk Rating by Claim Type
| Claim Type | Example in Current Direction | Legal Risk | Required Control |
| --- | --- | --- | --- |
| Buy-timing recommendation | "best time to buy", "favorable accumulation regime" | High | Replace with descriptive historical framing and explicit non-recommendation caveat |
| Deterministic return framing | "13% lifespan = 2x" (if presented as expected outcome) | High | Keep as tested historical claim only; include failure rate and non-predictive caveat |
| Signal-as-advice phrasing | "use this signal to..." without limits | Medium-High | Reframe as research indicator; prohibit directive trading language |
| Performance implication statements | "better entries" / "improved outcomes" without conditions | Medium | Add sample limitations, in-sample caveat, no guarantee language |
| Factual market-stat reporting | 30D/90D returns, vol, turnover table | Low | Retain source/date/time window labels and data quality caveats |

## 2) Required Disclaimer Updates for Multi-Coin Coverage
Use these controls in every subscriber-facing version.

1. Mandatory standard disclaimer (verbatim, near top and footer):
   "Bart Bot Research provides educational trading research and market analysis. All content is for informational purposes only. We are not registered investment advisors. Past performance is not indicative of future results. Always do your own research and never trade with money you cannot afford to lose."
2. Add model-risk sentence adjacent to any signal section:
   "Model outputs are probabilistic, based on historical data, and may fail under new market regimes."
3. Add non-personalization sentence in summary/conclusion:
   "This report does not consider any reader's objectives, financial situation, or risk tolerance."
4. Add data limitations sentence near methodology:
   "Data is aggregated from third-party sources and may contain methodology differences or revisions."
5. Add forward-looking caution when discussing scenarios:
   "Any forward-looking scenarios are illustrative research assumptions, not forecasts or promises."

## 3) Redline Guidance (Prohibited or Ambiguous Phrasing)
Apply these substitutions before publication.

| Do Not Publish | Approved Replacement |
| --- | --- |
| "Now is the best time to buy BTC." | "BTC currently screens in a lower historical valuation regime under this model; this is not a buy recommendation." |
| "Subscribers should accumulate here." | "Readers evaluating long-horizon exposure may review this regime context alongside their own risk framework." |
| "The model suggests BTC will double in ~750 days." | "Historically, some windows approached 2x over similar age intervals, but outcomes were inconsistent and non-deterministic." |
| "This signal can be used to trade SOL/XRP/DOGE." | "This indicator is a research input and requires independent validation, risk controls, and regime filters before any deployment." |
| "ETH is the strongest coin to buy this month." | "In this snapshot, ETH showed the strongest 30-day relative performance among covered assets; no recommendation is implied." |
| "Discount regime means upside is likely from here." | "Discount regime indicates lower relative positioning versus model history, but future path remains highly uncertain." |

## 4) Publication Gate (Pass/Fail)
Pass only if all of the following are true:
- Standard disclaimer appears verbatim in the final report.
- No imperative language ("buy", "sell", "should enter", "best time").
- All return/doubling references are framed as historical tests with non-guarantee language.
- Signal section includes model-risk and data-quality caveats.
- Final legal spot-check confirms no personalized-advice framing.

If any gate item fails, hold publication and return to editorial for legal revisions.
