from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import mean, pstdev
from typing import List

from .strategy import Strategy
from .types import BacktestConfig, Bar, Metrics


@dataclass(frozen=True)
class BacktestResult:
    strategy_name: str
    equity_curve: List[float]
    returns: List[float]
    trade_count: int
    metrics: Metrics


class BacktestEngine:
    def __init__(self, config: BacktestConfig):
        self.config = config

    def run(self, bars: List[Bar], strategy: Strategy) -> BacktestResult:
        if len(bars) < 2:
            raise ValueError("At least 2 bars are required")

        signals = strategy.generate_signals(bars)
        if len(signals) != len(bars):
            raise ValueError(
                f"Signal length mismatch for strategy {strategy.name}: "
                f"got {len(signals)} expected {len(bars)}"
            )

        cash = self.config.initial_cash
        position = 0
        equity_curve: List[float] = []
        returns: List[float] = []
        trade_count = 0
        previous_equity = self.config.initial_cash
        slippage = self.config.slippage_bps / 10_000.0

        for i, bar in enumerate(bars):
            target = int(signals[i])
            if target not in (-1, 0, 1):
                raise ValueError(
                    f"Signal at index {i} must be -1, 0, or 1. Got {target}."
                )

            delta = target - position
            if delta != 0:
                exec_price = self._execution_price(bar.close, delta, slippage)
                cash -= delta * exec_price
                cash -= self.config.per_trade_commission
                position = target
                trade_count += 1

            equity = cash + position * bar.close
            equity_curve.append(equity)
            if i == 0:
                returns.append(0.0)
            else:
                returns.append((equity / previous_equity) - 1.0)
            previous_equity = equity

        metrics = self._compute_metrics(returns, equity_curve, trade_count)
        return BacktestResult(
            strategy_name=strategy.name,
            equity_curve=equity_curve,
            returns=returns,
            trade_count=trade_count,
            metrics=metrics,
        )

    @staticmethod
    def _execution_price(price: float, delta: int, slippage: float) -> float:
        if delta > 0:
            return price * (1.0 + slippage)
        return price * (1.0 - slippage)

    def _compute_metrics(
        self, returns: List[float], equity_curve: List[float], trade_count: int
    ) -> Metrics:
        total_return = (equity_curve[-1] / self.config.initial_cash) - 1.0
        periods = max(len(returns) - 1, 1)
        annualized_return = (
            (1.0 + total_return) ** (self.config.bars_per_year / periods)
        ) - 1.0

        realized_returns = returns[1:] if len(returns) > 1 else [0.0]
        vol = pstdev(realized_returns) if len(realized_returns) > 1 else 0.0
        if vol == 0:
            sharpe = 0.0
        else:
            sharpe = (
                mean(realized_returns)
                / vol
                * math.sqrt(self.config.bars_per_year)
            )

        peak = equity_curve[0]
        max_drawdown = 0.0
        for equity in equity_curve:
            peak = max(peak, equity)
            drawdown = (equity / peak) - 1.0
            max_drawdown = min(max_drawdown, drawdown)

        if len(realized_returns) == 0:
            win_rate = 0.0
        else:
            wins = sum(1 for r in realized_returns if r > 0)
            win_rate = wins / len(realized_returns)

        return Metrics(
            total_return=total_return,
            annualized_return=annualized_return,
            sharpe_ratio=sharpe,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            trade_count=trade_count,
        )
