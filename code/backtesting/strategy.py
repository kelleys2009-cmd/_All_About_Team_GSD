from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import List, Protocol, runtime_checkable

from .types import Bar


@runtime_checkable
class Strategy(Protocol):
    name: str

    def generate_signals(self, bars: List[Bar]) -> List[int]:
        """
        Return target position per bar, one of -1 (short), 0 (flat), 1 (long).
        The list length must equal len(bars).
        """


def load_strategy_from_module(module_path: str) -> Strategy:
    """
    Load a strategy module that exposes `build_strategy() -> Strategy`.
    """
    path = Path(module_path)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load strategy module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]

    build_strategy = getattr(module, "build_strategy", None)
    if build_strategy is None:
        raise ValueError(
            f"Strategy module {module_path} must define build_strategy()"
        )
    strategy = build_strategy()
    if not isinstance(strategy, Strategy):
        raise ValueError(
            f"build_strategy() in {module_path} did not return a Strategy"
        )
    return strategy
