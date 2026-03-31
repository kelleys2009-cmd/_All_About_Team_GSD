# Bitcoin Power Law, OLS, and Quantile Review
Date: 2026-03-31

## Executive Summary
A log-log OLS fit of Bitcoin price versus network age supports the core power-law framing and implies that a price doubling requires roughly a 12.97% increase in network age, which is consistent with the "~13% lifespan" heuristic. Using daily BTCUSD data through 2026-03-31, the fitted exponent is 5.68 with R^2 = 0.961, indicating strong long-horizon trend fit despite large cyclical deviations. At current network age, the same model implies ~817 days for a doubling, directionally close to the requested ~750-day framing but not exact. Over the last five years (2021-03-31 to 2026-03-31), realized CAGR is ~3.0%, implying a much slower realized doubling pace (~23.4 years), so cycle timing dominates short-horizon outcomes.

## Context
Task scope was to evaluate the Bitcoin power-law claim over the last five years while grounding conclusions in a longer-history model and explicit OLS evidence. The claim tested: price doubles per ~13% lifespan growth and roughly every ~750 days, with expected slowdown as the network matures.

## Data/Evidence
- Daily BTCUSD closes were pulled from CryptoCompare `histoday` API and stitched in reverse chronological chunks to obtain long history from 2010-07-17 through 2026-03-31 (5,737 daily observations total; 1,827 in the last five years) ([CryptoCompare API](https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=2000)).
- Bitcoin lifespan anchor used the Genesis block date, January 3, 2009 ([Bitcoin Wiki: Genesis block](https://en.bitcoin.it/wiki/Genesis_block)).
- OLS specification: `ln(price_t) = a + b*ln(age_days_t) + e_t`, where `age_days_t` is days since 2009-01-03.

Key estimated values (full available history):
- OLS exponent `b`: 5.6823
- Intercept `a`: -37.9548
- R^2: 0.9611
- Implied age multiplier for 2x price: `2^(1/b) = 1.1297` (12.97% age increase)
- Model-implied growth for +13% age: `1.13^b = 2.0027x`
- Model-implied growth over next 750 days at 2026-03-31 age: `((age+750)/age)^b = 1.8956x`

Residual quantile bands in multiplicative terms versus central model path (`exp(residual)`):
- Q10: 0.47x
- Q25: 0.58x
- Q50: 0.86x
- Q75: 1.52x
- Q90: 2.71x

Observed 5-year realized performance:
- 2021-03-31 close: $58,793.80
- 2026-03-31 close: $68,177.07
- Realized CAGR: 3.01%
- Implied realized doubling time from CAGR: ~23.40 years

## Analysis
The long-history fit validates the specific "13% lifespan doubles price" statement mathematically: with `b = 5.68`, a doubling requires 12.97% more age, effectively 13%. This also clarifies the "750 days" narrative: doubling time is not constant in a power law. It scales with current age. At 2026-03-31 age, model-implied doubling is ~817 days, while it would have been materially shorter earlier in Bitcoin's life.

This is exactly the "slowing as network grows" mechanism: absolute time-to-double rises even when the same scaling law holds. However, the residual distribution is wide (roughly 0.47x to 2.71x between Q10 and Q90), so the power-law path is better interpreted as a structural trend envelope rather than a near-term trading clock.

The last-five-year realized path underperformed the structural curve pace because it spans a full post-2021 cycle drawdown/recovery regime. That divergence is not evidence the power law fails; it indicates regime and cycle conditions can dominate for multi-year windows.

## Implications
- For Strategy #1 research, treat power-law outputs as strategic regime context (valuation/position-sizing envelope), not a direct timing signal for entries/exits.
- Cross-reference with Devin's workstream: the model should be integrated as a low-frequency feature in backtest architecture (TEA-46) with explicit handling for wide residual regimes, not as deterministic forecast input.
- Cross-reference with Roy's workstream: any external communication should include clear non-advice framing and licensing/compliance checks before publication of model-driven commentary.

## Open Questions
- Should we fit rolling-window exponents (e.g., 4-year trailing) to quantify structural drift in `b` over time instead of assuming one global exponent?
- Should we formally estimate quantile regressions (rather than OLS residual quantiles) to build explicit upper/lower "power curve" channels for risk throttles?
- Do we want exchange-specific BTC spot composites (Coinbase/Kraken/Bitstamp) to test sensitivity versus aggregate-vendor data?
- Should this feature feed only exposure scaling, or also turnover caps in regime-aware deployment logic?

## Confidence Level
**Medium.** Confidence is high on the mathematical relationship between fitted exponent and lifespan-based doubling, and medium on operational conclusions because results depend on data-vendor construction and a single global-specification OLS fit. Confidence would increase with multi-vendor replication and explicit quantile-regression channel estimation.
