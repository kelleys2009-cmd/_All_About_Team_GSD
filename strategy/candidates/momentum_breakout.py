"""Candidate strategy: follow momentum breakouts from rolling mean."""

from strategy.contracts import MarketSnapshot


class MomentumBreakoutStrategy:
    name = "momentum_breakout"

    def signal(self, snapshot: MarketSnapshot) -> int:
        deviation = (snapshot.price - snapshot.rolling_mean) / max(snapshot.rolling_mean, 1e-9)
        if deviation > 0.015:
            return 1
        if deviation < -0.015:
            return -1
        return 0
