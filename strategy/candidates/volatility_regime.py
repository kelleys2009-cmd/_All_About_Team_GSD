"""Candidate strategy: risk-off during high volatility, long mild uptrends otherwise."""

from strategy.contracts import MarketSnapshot


class VolatilityRegimeStrategy:
    name = "volatility_regime"

    def signal(self, snapshot: MarketSnapshot) -> int:
        if snapshot.volatility > 0.03:
            return 0
        if snapshot.price >= snapshot.rolling_mean:
            return 1
        return -1
