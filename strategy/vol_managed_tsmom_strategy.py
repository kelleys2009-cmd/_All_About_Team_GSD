from __future__ import annotations

import math
from typing import List

from backtesting.types import Bar


class VolManagedTSMOMStrategy:
    """
    Price-only approximation of vol-managed time-series momentum.

    - Momentum signal: lookback return over `momentum_lookback`
    - Vol management: realized volatility over `vol_lookback`
    - Position mapping: take trend direction only when risk budget allows.

    The current engine supports only discrete positions {-1, 0, 1}, so we map
    continuous target leverage into a gated discrete exposure.
    """

    name = "vol_managed_tsmom_proxy"

    def __init__(
        self,
        momentum_lookback: int = 6,
        vol_lookback: int = 5,
        target_daily_vol: float = 0.012,
        min_leverage_to_trade: float = 0.30,
        max_leverage: float = 1.5,
    ):
        if momentum_lookback <= 1 or vol_lookback <= 1:
            raise ValueError("Lookbacks must be > 1")
        self.momentum_lookback = momentum_lookback
        self.vol_lookback = vol_lookback
        self.target_daily_vol = target_daily_vol
        self.min_leverage_to_trade = min_leverage_to_trade
        self.max_leverage = max_leverage

    def generate_signals(self, bars: List[Bar]) -> List[int]:
        if not bars:
            return []

        closes = [b.close for b in bars]
        returns = [0.0]
        for i in range(1, len(closes)):
            prev = closes[i - 1]
            returns.append((closes[i] / prev) - 1.0 if prev != 0 else 0.0)

        signals = [0 for _ in bars]
        for i in range(len(bars)):
            if i < max(self.momentum_lookback, self.vol_lookback):
                signals[i] = 0
                continue

            momentum = (closes[i] / closes[i - self.momentum_lookback]) - 1.0
            vol_slice = returns[i + 1 - self.vol_lookback : i + 1]
            realized_vol = self._stdev(vol_slice)

            if realized_vol <= 1e-9:
                leverage = self.max_leverage
            else:
                leverage = min(self.max_leverage, self.target_daily_vol / realized_vol)

            if leverage < self.min_leverage_to_trade:
                signals[i] = 0
            elif momentum > 0:
                signals[i] = 1
            elif momentum < 0:
                signals[i] = -1
            else:
                signals[i] = 0

        return signals

    @staticmethod
    def _stdev(values: List[float]) -> float:
        if len(values) <= 1:
            return 0.0
        avg = sum(values) / len(values)
        var = sum((v - avg) ** 2 for v in values) / len(values)
        return math.sqrt(var)


def build_strategy() -> VolManagedTSMOMStrategy:
    return VolManagedTSMOMStrategy()
