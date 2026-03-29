from __future__ import annotations

from typing import List

from backtesting.types import Bar


class BuyAndHoldStrategy:
    name = "buy_and_hold"

    def generate_signals(self, bars: List[Bar]) -> List[int]:
        if not bars:
            return []
        return [1 for _ in bars]


def build_strategy() -> BuyAndHoldStrategy:
    """
    Scaffold hook used by the backtest runner.
    Keep this signature stable for quick strategy onboarding.
    """
    return BuyAndHoldStrategy()
