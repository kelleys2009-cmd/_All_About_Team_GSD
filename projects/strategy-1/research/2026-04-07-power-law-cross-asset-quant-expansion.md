# Power Law: Cross-Asset Quant Expansion (Broad Crypto Universe)
Date: 2026-04-07

## 1. Executive Summary
This study expanded the power-law analysis from a small coin set to a broader, liquidity-filtered crypto universe and quantified which assets show statistically strong log-log scaling behavior. Starting from the top-120 market-cap list, 73 non-stablecoin assets met minimum history and liquidity screens and were modeled using a unified power-law specification. BTC remains the strongest reference (`R^2=0.782`, exponent `b=1.700`), while only 11 non-BTC assets simultaneously show positive exponent and `R^2 >= 0.60`. The best non-BTC fits with positive exponent were `OKB`, `QNT`, `KAS`, `BNB`, and `BGB`; however, cross-asset heterogeneity is large, so deployment should treat power law as a regime/valuation feature, not a standalone signal.

## 2. Asset Coverage and Inclusion Criteria
Universe construction and filters:
- Initial universe: top 120 assets by USD market cap snapshot.
- Liquidity filter: `24h volume >= $10,000,000` (CoinGecko snapshot proxy).
- History filter: `>= 365` daily close observations from Yahoo (`<SYMBOL>-USD`).
- Stablecoin exclusion proxy: latest price in `[0.97, 1.03]` removed.

Coverage counts:
- Universe rows: `120`
- Passed liquidity + history: `82`
- Final modeled non-stable set: `73`
- Positive exponent assets: `44 / 73`
- Positive exponent with `R^2 >= 0.60`: `11 / 73`

## 3. Data Sources and Sampling Windows
- Market-cap and liquidity snapshot: CoinGecko public API (`coins/markets`) pulled on 2026-04-07.
- Price history: Yahoo Finance daily close via `yfinance` (`period=max`, `interval=1d`) pulled on 2026-04-07.
- BTC reference window from this run: 2014-09-17 to 2026-04-08 (`n=4,221`).
- Asset windows vary by listing history; each asset modeled on full available Yahoo history after filters.

Data-quality notes:
- Some symbols in top-cap lists did not map cleanly to Yahoo tickers (`FIGR_HELOC`, `USYC`, `TAO`, etc.).
- Several yield/stable or wrapped-style symbols pass basic history filters but may still distort power-law interpretation.

## 4. Model Specification and Statistical Outputs
Per-asset model:
- `ln(price_t) = a + b * ln(days_since_first_observation_t)`

Reported outputs per asset:
- `R^2`, exponent `b`, intercept `a`
- latest price and current `price_to_model` multiplier
- residual distribution multipliers (`Q10`, `Q50`, `Q90`) on `exp(residual)`
- distance to BTC exponent: `|b_asset - b_btc|`

Internal ranking score (for cross-asset triage):
- `score = 0.50*R^2 + 0.30*(1/(1+|b-b_btc|)) + 0.20*liquidity_component`
- where `liquidity_component` is a bounded log-volume transform.

Assumptions:
- First available Yahoo date is used as lifecycle start proxy (not true chain genesis).
- 24h volume snapshot is used as liquidity proxy (not historical turnover series).

## 5. Cross-Asset Comparison Tables
### 5.1 BTC reference

| Asset | Obs | R^2 | Exponent b |
|---|---:|---:|---:|
| BTC | 4,221 | 0.782 | 1.700 |

### 5.2 Highest-fit non-BTC assets (positive exponent)

| Asset | MCap Rank | Obs | R^2 | Exponent b | \\|b-BTC\\| | Price/Model |
|---|---:|---:|---:|---:|---:|---:|
| OKB | 46 | 2,535 | 0.809 | 1.069 | 0.631 | 1.421x |
| QNT | 65 | 2,798 | 0.763 | 1.383 | 0.317 | 0.528x |
| KAS | 73 | 1,407 | 0.754 | 1.398 | 0.302 | 0.220x |
| BNB | 4 | 3,072 | 0.718 | 1.461 | 0.239 | 1.214x |
| BGB | 61 | 1,714 | 0.711 | 1.201 | 0.499 | 0.847x |
| SOL | 7 | 2,189 | 0.677 | 1.319 | 0.381 | 0.541x |
| LINK | 17 | 3,072 | 0.673 | 1.197 | 0.502 | 0.500x |
| LTC | 26 | 4,221 | 0.637 | 1.135 | 0.565 | 0.452x |

### 5.3 Exponent-proximity leaders vs BTC (non-BTC)

| Asset | Exponent b | \\|b-BTC\\| | R^2 |
|---|---:|---:|---:|
| WLD | 1.722 | 0.022 | 0.475 |
| BNB | 1.461 | 0.239 | 0.718 |
| KAS | 1.398 | 0.302 | 0.754 |
| QNT | 1.383 | 0.317 | 0.763 |
| DOGE | 1.359 | 0.341 | 0.514 |

## 6. Findings and Strategic Implications
- Breadth finding: only `~15%` (`11/73`) of modeled assets show both positive exponent and `R^2 >= 0.60`, so robust power-law structure is not universal.
- BTC benchmark finding: BTC remains among the strongest structural fits and retains the most interpretable baseline for power-law framing.
- Candidate shortlist for deeper follow-up (high fit + positive exponent + liquidity): `OKB`, `QNT`, `KAS`, `BNB`, `SOL`, `LINK`.
- Signal design implication: use power-law outputs as slow-moving state variables (valuation percentile / trend-distance) rather than direct entry triggers.
- Cross-team implication:
- For Chris: integrate macro regime labels with power-law state before any production claims.
- For Devin: implement this as a periodic feature-generation pipeline with reproducible snapshots and backtest hooks.

## 7. Risks / Limitations
- Ticker mapping risk: symbol-to-Yahoo mapping can misclassify or drop assets, especially newer tokens and wrapped/yield instruments.
- Lifecycle anchor risk: using first Yahoo observation instead of protocol genesis affects exponent comparability.
- Liquidity proxy risk: single-day 24h volume is not a full liquidity history and can be event-distorted.
- Regime/structural-break risk: single-factor log-log fits can look strong while failing in forward regime shifts.
- Stablecoin contamination risk: price-based stablecoin exclusion may miss edge cases.

## 8. Reproducibility Notes (commands, artifacts, file paths)
Primary artifacts:
- `artifacts/tea-91/2026-04-07-power-law-coverage.csv`
- `artifacts/tea-91/2026-04-07-power-law-quant-expansion-metrics.csv`
- `artifacts/tea-91/2026-04-07-power-law-quant-expansion-meta.json`

Execution command (from workspace root):
```bash
python3 code/market_data/tea91_power_law_quant_expansion.py
```

Practical rerun guidance:
- Re-pull CoinGecko universe snapshot.
- Recompute history/liquidity filters.
- Refit log-log model for all eligible assets.
- Re-rank by fit + exponent proximity + liquidity.
- Export the same three artifact files for diff comparison over time.
