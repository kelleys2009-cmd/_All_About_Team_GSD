#!/usr/bin/env python3
"""CLI entrypoint for strategy experimentation backtests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from strategy.backtest import run_backtest
from strategy.registry import STRATEGY_REGISTRY, create_strategy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a standardized strategy backtest")
    parser.add_argument(
        "--strategy",
        required=True,
        choices=sorted(STRATEGY_REGISTRY.keys()),
        help="Candidate strategy to run",
    )
    parser.add_argument("--periods", type=int, default=250, help="Number of simulated periods")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic runs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    strategy = create_strategy(args.strategy)
    summary = run_backtest(strategy, periods=args.periods, seed=args.seed)
    print(json.dumps(summary.__dict__, indent=2))


if __name__ == "__main__":
    main()
