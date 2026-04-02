from __future__ import annotations

from typing import List

from backtesting.types import Bar


class BuyAndHoldStrategy:
    name = "buy_and_hold"

    def generate_signals(self, bars: List[Bar]) -> List[int]:
        if not bars:
            return []
        return [1] * len(bars)


def build_strategy() -> BuyAndHoldStrategy:
    return BuyAndHoldStrategy()
