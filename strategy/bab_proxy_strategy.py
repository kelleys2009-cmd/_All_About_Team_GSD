from __future__ import annotations

from typing import List

from backtesting.types import Bar


class BABProxyStrategy:
    """
    Single-asset proxy for BAB (Betting Against Beta).

    True BAB requires a cross-sectional low-beta-minus-high-beta long/short basket.
    This proxy uses only one price series, so it approximates beta pressure with a
    regime score and applies a contrarian risk stance:

    - beta proxy = short-term absolute return / long-term absolute return
    - low-beta regime (proxy < low_threshold): favor long when medium-term trend >= 0
    - high-beta regime (proxy > high_threshold): favor short when medium-term trend < 0
    - otherwise: flat
    """

    name = "bab_proxy_single_asset"

    def __init__(
        self,
        beta_short_lookback: int = 3,
        beta_long_lookback: int = 8,
        trend_lookback: int = 8,
        low_threshold: float = 0.95,
        high_threshold: float = 1.05,
    ):
        if beta_short_lookback <= 1 or beta_long_lookback <= beta_short_lookback:
            raise ValueError("Expected 1 < beta_short_lookback < beta_long_lookback")
        if trend_lookback <= 1:
            raise ValueError("trend_lookback must be > 1")
        self.beta_short_lookback = beta_short_lookback
        self.beta_long_lookback = beta_long_lookback
        self.trend_lookback = trend_lookback
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

    def generate_signals(self, bars: List[Bar]) -> List[int]:
        if not bars:
            return []

        closes = [b.close for b in bars]
        abs_returns = [0.0]
        for i in range(1, len(closes)):
            prev = closes[i - 1]
            ret = (closes[i] / prev) - 1.0 if prev != 0 else 0.0
            abs_returns.append(abs(ret))

        signals = [0 for _ in bars]
        warmup = max(self.beta_long_lookback, self.trend_lookback)
        for i in range(len(bars)):
            if i < warmup:
                continue

            short_slice = abs_returns[i + 1 - self.beta_short_lookback : i + 1]
            long_slice = abs_returns[i + 1 - self.beta_long_lookback : i + 1]
            short_abs = sum(short_slice) / len(short_slice)
            long_abs = sum(long_slice) / len(long_slice)
            beta_proxy = short_abs / max(long_abs, 1e-9)

            trend = (closes[i] / closes[i - self.trend_lookback]) - 1.0
            if beta_proxy < self.low_threshold and trend >= 0:
                signals[i] = 1
            elif beta_proxy > self.high_threshold and trend < 0:
                signals[i] = -1
            else:
                signals[i] = 0

        return signals


def build_strategy() -> BABProxyStrategy:
    return BABProxyStrategy()
