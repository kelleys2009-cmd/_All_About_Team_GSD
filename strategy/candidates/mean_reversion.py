"""Candidate strategy: buy dips below mean and sell pops above mean."""

from strategy.contracts import MarketSnapshot


class MeanReversionStrategy:
    name = "mean_reversion"

    def signal(self, snapshot: MarketSnapshot) -> int:
        deviation = (snapshot.price - snapshot.rolling_mean) / max(snapshot.rolling_mean, 1e-9)
        if deviation < -0.01:
            return 1
        if deviation > 0.01:
            return -1
        return 0
