"""Backtesting package for multi-strategy evaluation."""

from .engine import BacktestEngine, BacktestResult
from .strategy import Strategy, load_strategy_from_module
from .types import BacktestConfig, Bar, Metrics, WalkForwardConfig
from .walkforward import (
    WalkForwardRunner,
    WalkForwardStrategySummary,
    WalkForwardWindowResult,
)

__all__ = [
    "BacktestConfig",
    "BacktestEngine",
    "BacktestResult",
    "Bar",
    "Metrics",
    "Strategy",
    "WalkForwardConfig",
    "WalkForwardRunner",
    "WalkForwardStrategySummary",
    "WalkForwardWindowResult",
    "load_strategy_from_module",
]
