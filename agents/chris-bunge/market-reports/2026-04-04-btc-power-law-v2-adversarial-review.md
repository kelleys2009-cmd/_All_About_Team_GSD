# Adversarial Review: BTC Power Law V2 (Deep-Discount Framing)
Date: 2026-04-04

## Executive Summary
Verdict: **Revise**. Roy's V2 correctly identifies BTC as below the model's 25th-percentile residual band (discount regime), but the draft overstates confidence for publication without stronger stress testing and framing controls. Independent replication confirms the core fit (`n ~= 5.64`, `R^2 ~= 0.960`) and confirms the 13% lifespan rule is not reliable (`~40%` of windows >=2x), which supports the regime-tool framing over deterministic timing. The key weaknesses are model class fragility, endpoint dependence, and translation risk from in-sample valuation to investor-facing action language.

## Context
This memo reviews Roy's V2 draft in [TEA-75](/TEA/issues/TEA-75#document-2026-04-02-bitcoin-power-law-v2-deep-discount) and is scoped to pre-publication adversarial checks requested in [TEA-76](/TEA/issues/TEA-76). The aim is to test whether the deep-discount thesis survives replication and basic falsification.

## Data/Evidence
- Roy V2 inputs and claims were pulled from [TEA-75 V2](/TEA/issues/TEA-75#document-2026-04-02-bitcoin-power-law-v2-deep-discount).
- Independent replication used Blockchain.com daily BTC USD history (`market-price` API), 2009-01-03 to 2026-04-04, with positive-price observations only (5,709 rows).
- Replication results:
  - Power-law fit on log-log data: `log(P)=a+n*log(D)` with `n=5.642`, `R^2(log)=0.9595`.
  - Exponential alternative in log space (`log(P)=a+b*D`) materially weaker: `R^2(log)=0.8735`.
  - 13%-lifespan test (annual windows 2011-2025): median multiple `1.69x`, share >=`2.0x` = `40%`.
  - Train/test split (fit through 2017-12-31, evaluate 2018+): log-RMSE train `0.864`, test `0.501`; residual-band rotation on test period outperformed buy/hold in this run (total return `+1091.6%` vs `+385.2%`, max drawdown `-49.7%` vs `-81.2%`).
- Cross-team implementation constraints were referenced from Devin's pipeline in [TEA-78](/TEA/issues/TEA-78#document-2026-04-02-multi-asset-backtest-pipeline), especially static cost assumptions and close-only bar schema.

## Analysis
### Verdict
**Revise**

### Critical Findings
1. **Core discount signal is directionally valid but not publication-ready as a standalone call.**
The 18th-percentile residual claim is consistent with independent replication and remains within a discount regime interpretation.

2. **Deterministic doubling narratives fail under direct test.**
Both Roy's table and replication show the 13% lifespan heuristic is regime-dependent and fails often; it must not be framed as clock-like timing.

3. **In-sample fit is strong but structurally vulnerable to trend artifacts.**
High log-log `R^2` is expected for long non-stationary adoption series and is insufficient by itself as proof of predictive edge.

4. **Actionability risk remains under-specified for new investors.**
"Discount" can persist through deep drawdowns; messaging needs explicit scenario ranges and invalidation triggers to avoid false precision.

5. **Execution realism is under-modeled relative to production pipeline standards.**
Given TEA-78's current constraints (static costs, close-only bars), the current strategy framing should be treated as research-grade signal context, not deployment guidance.

### Falsification Attempts
- **Model-class challenge:** compared power-law against an exponential log-price trend. Result: power-law fit remains stronger in-sample, but this does not settle causal validity.
- **Heuristic falsification:** re-ran the 13%-lifespan doubling test. Result: median <2x and only ~40% >=2x, invalidating deterministic claims.
- **Out-of-sample sanity check:** fit model pre-2018 and evaluated 2018+. Result: discount-band rotation still showed favorable drawdown/return profile in this sample, so the idea was not falsified here.
- **Engineering realism check (with Devin's work):** mapped signal requirements to current pipeline constraints. Result: reproducibility is improving, but execution/cost realism remains too coarse for investor-grade confidence.

### Suggested Improvements
- Add strict walk-forward reporting as a first-class table in V3 (window-by-window, not single aggregate).
- Add explicit uncertainty language: "discount regime" is probabilistic, not timing guarantee.
- Add robustness matrix: parameter perturbation (+/-20-50%), alternate vendors, and close-time sensitivity.
- Add deployment guardrails: invalidation conditions, max drawdown tolerance, and position-sizing policy linked to volatility regime.
- Harmonize with TEA-78 artifact schema so each weekly report can be reproduced from a single command and manifest.

## Implications
For Team GSD and Bart Bot publication quality, this research should be positioned as a **long-horizon valuation regime indicator** with constrained confidence, not a near-term buy signal. The thesis survives basic adversarial replication, but publication should wait for stronger robustness disclosures and tighter investor-risk language.

## Open Questions
- Does residual-band edge survive exchange-specific data and alternate close definitions?
- How stable are percentile classifications under rolling re-estimation windows?
- What macro filter set materially improves false-positive control in prolonged bear/liquidity stress regimes?
- Can TEA-78's pipeline be extended to include dynamic spread/funding/slippage so this signal can be compared fairly to simpler baselines?

## Confidence Level
**Medium.** Confidence is medium because the core discount finding replicated and key non-determinism claims held up, but substantial model-risk and implementation-risk remain before publication-grade conviction.
