from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass(frozen=True)
class Bar:
    timestamp: datetime
    close: float


@dataclass(frozen=True)
class BacktestConfig:
    initial_cash: float = 100_000.0
    per_trade_commission: float = 1.0
    slippage_bps: float = 2.0
    bars_per_year: int = 252


@dataclass(frozen=True)
class WalkForwardConfig:
    train_size: int
    test_size: int
    step_size: int


@dataclass(frozen=True)
class Metrics:
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    trade_count: int

    def to_dict(self) -> Dict[str, float]:
        return {
            "total_return": self.total_return,
            "annualized_return": self.annualized_return,
            "sharpe_ratio": self.sharpe_ratio,
            "max_drawdown": self.max_drawdown,
            "win_rate": self.win_rate,
            "trade_count": float(self.trade_count),
        }
