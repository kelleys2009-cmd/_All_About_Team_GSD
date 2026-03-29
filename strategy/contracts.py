"""Core interfaces and data shapes for strategy experimentation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class MarketSnapshot:
    """Single market observation used by strategies."""

    index: int
    price: float
    rolling_mean: float
    volatility: float


class Strategy(Protocol):
    """Contract all candidate strategies must satisfy."""

    name: str

    def signal(self, snapshot: MarketSnapshot) -> int:
        """Return -1 (short), 0 (flat), or 1 (long)."""


@dataclass(frozen=True)
class BacktestSummary:
    strategy: str
    periods: int
    final_equity: float
    total_return_pct: float
    trades: int
