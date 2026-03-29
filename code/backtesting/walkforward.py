from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from .engine import BacktestEngine, BacktestResult
from .strategy import Strategy
from .types import BacktestConfig, Bar, Metrics, WalkForwardConfig


@dataclass(frozen=True)
class WalkForwardWindowResult:
    window_index: int
    train_start: datetime
    train_end: datetime
    test_start: datetime
    test_end: datetime
    by_strategy: Dict[str, BacktestResult]


@dataclass(frozen=True)
class WalkForwardStrategySummary:
    strategy_name: str
    average_total_return: float
    average_sharpe_ratio: float
    average_max_drawdown: float
    total_trades: int
    windows: int

    def to_dict(self) -> Dict[str, float]:
        return {
            "average_total_return": self.average_total_return,
            "average_sharpe_ratio": self.average_sharpe_ratio,
            "average_max_drawdown": self.average_max_drawdown,
            "total_trades": float(self.total_trades),
            "windows": float(self.windows),
        }


class WalkForwardRunner:
    def __init__(self, backtest_config: BacktestConfig, wf_config: WalkForwardConfig):
        self.backtest_config = backtest_config
        self.wf_config = wf_config

    def run(
        self, bars: List[Bar], strategies: List[Strategy]
    ) -> List[WalkForwardWindowResult]:
        if self.wf_config.train_size <= 0 or self.wf_config.test_size <= 0:
            raise ValueError("train_size and test_size must both be > 0")
        if self.wf_config.step_size <= 0:
            raise ValueError("step_size must be > 0")

        required = self.wf_config.train_size + self.wf_config.test_size
        if len(bars) < required:
            raise ValueError(
                f"Insufficient bars for walk-forward: need at least {required}, got {len(bars)}"
            )

        engine = BacktestEngine(self.backtest_config)
        windows: List[WalkForwardWindowResult] = []
        start = 0
        window_index = 0

        while (start + required) <= len(bars):
            train_slice = bars[start : start + self.wf_config.train_size]
            test_slice = bars[
                start
                + self.wf_config.train_size : start
                + self.wf_config.train_size
                + self.wf_config.test_size
            ]

            by_strategy: Dict[str, BacktestResult] = {}
            for strategy in strategies:
                by_strategy[strategy.name] = engine.run(test_slice, strategy)

            windows.append(
                WalkForwardWindowResult(
                    window_index=window_index,
                    train_start=train_slice[0].timestamp,
                    train_end=train_slice[-1].timestamp,
                    test_start=test_slice[0].timestamp,
                    test_end=test_slice[-1].timestamp,
                    by_strategy=by_strategy,
                )
            )

            window_index += 1
            start += self.wf_config.step_size

        return windows

    @staticmethod
    def summarize(
        window_results: List[WalkForwardWindowResult],
    ) -> Dict[str, WalkForwardStrategySummary]:
        if not window_results:
            return {}

        by_strategy_metrics: Dict[str, List[Metrics]] = {}
        by_strategy_trades: Dict[str, int] = {}
        for window in window_results:
            for strategy_name, result in window.by_strategy.items():
                by_strategy_metrics.setdefault(strategy_name, []).append(result.metrics)
                by_strategy_trades[strategy_name] = (
                    by_strategy_trades.get(strategy_name, 0) + result.trade_count
                )

        summary: Dict[str, WalkForwardStrategySummary] = {}
        for strategy_name, metrics_list in by_strategy_metrics.items():
            count = len(metrics_list)
            summary[strategy_name] = WalkForwardStrategySummary(
                strategy_name=strategy_name,
                average_total_return=sum(m.total_return for m in metrics_list) / count,
                average_sharpe_ratio=sum(m.sharpe_ratio for m in metrics_list) / count,
                average_max_drawdown=sum(m.max_drawdown for m in metrics_list) / count,
                total_trades=by_strategy_trades[strategy_name],
                windows=count,
            )
        return summary
