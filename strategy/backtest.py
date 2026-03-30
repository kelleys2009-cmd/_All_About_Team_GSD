"""Standardized backtest harness for candidate strategy swaps."""

from __future__ import annotations

import random
from collections import deque
from typing import Iterable

from strategy.contracts import BacktestSummary, MarketSnapshot, Strategy


def _simulate_prices(periods: int, seed: int) -> Iterable[float]:
    random.seed(seed)
    price = 100.0
    for _ in range(periods):
        drift = 0.0006
        shock = random.uniform(-0.02, 0.02)
        price *= 1 + drift + shock
        yield max(price, 1.0)


def run_backtest(strategy: Strategy, periods: int, seed: int) -> BacktestSummary:
    window = deque(maxlen=20)
    prev_price = None
    equity = 10_000.0
    position = 0
    trades = 0

    for idx, price in enumerate(_simulate_prices(periods=periods, seed=seed)):
        window.append(price)
        rolling_mean = sum(window) / len(window)

        if prev_price is None:
            volatility = 0.0
        else:
            volatility = abs(price - prev_price) / max(prev_price, 1e-9)
            equity *= 1 + position * ((price - prev_price) / max(prev_price, 1e-9))

        snapshot = MarketSnapshot(
            index=idx,
            price=price,
            rolling_mean=rolling_mean,
            volatility=volatility,
        )
        next_position = strategy.signal(snapshot)
        if next_position != position:
            trades += 1
        position = next_position
        prev_price = price

    total_return_pct = ((equity / 10_000.0) - 1.0) * 100
    return BacktestSummary(
        strategy=strategy.name,
        periods=periods,
        final_equity=round(equity, 2),
        total_return_pct=round(total_return_pct, 2),
        trades=trades,
    )
