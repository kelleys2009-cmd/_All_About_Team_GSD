from __future__ import annotations

from typing import List

from backtesting.types import Bar


class SMACrossoverStrategy:
    name = "sma_crossover_5_20"

    def __init__(self, fast: int = 5, slow: int = 20):
        if fast <= 0 or slow <= 0 or fast >= slow:
            raise ValueError("Expected 0 < fast < slow")
        self.fast = fast
        self.slow = slow

    def generate_signals(self, bars: List[Bar]) -> List[int]:
        closes = [b.close for b in bars]
        signals = [0 for _ in bars]
        for i in range(len(closes)):
            if i + 1 < self.slow:
                signals[i] = 0
                continue
            fast_avg = sum(closes[i + 1 - self.fast : i + 1]) / self.fast
            slow_avg = sum(closes[i + 1 - self.slow : i + 1]) / self.slow
            signals[i] = 1 if fast_avg > slow_avg else -1
        return signals


def build_strategy() -> SMACrossoverStrategy:
    return SMACrossoverStrategy()
