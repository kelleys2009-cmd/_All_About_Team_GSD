from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from backtesting.io import load_bars_from_csv, write_summary_artifacts
from backtesting.strategy import Strategy, load_strategy_from_module
from backtesting.types import BacktestConfig, WalkForwardConfig
from backtesting.walkforward import WalkForwardRunner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run walk-forward multi-strategy backtests."
    )
    parser.add_argument("--prices-csv", required=True, help="CSV with timestamp,close")
    parser.add_argument(
        "--strategy",
        action="append",
        required=True,
        dest="strategies",
        help="Path to strategy module exposing build_strategy()",
    )
    parser.add_argument("--output-dir", default="artifacts/backtests")
    parser.add_argument("--initial-cash", type=float, default=100_000.0)
    parser.add_argument("--commission", type=float, default=1.0)
    parser.add_argument("--slippage-bps", type=float, default=2.0)
    parser.add_argument("--bars-per-year", type=int, default=252)
    parser.add_argument("--train-size", type=int, required=True)
    parser.add_argument("--test-size", type=int, required=True)
    parser.add_argument("--step-size", type=int, required=True)
    return parser.parse_args()


def load_strategies(paths: List[str]) -> List[Strategy]:
    return [load_strategy_from_module(path) for path in paths]


def main() -> None:
    args = parse_args()
    bars = load_bars_from_csv(args.prices_csv)
    strategies = load_strategies(args.strategies)

    backtest_config = BacktestConfig(
        initial_cash=args.initial_cash,
        per_trade_commission=args.commission,
        slippage_bps=args.slippage_bps,
        bars_per_year=args.bars_per_year,
    )
    wf_config = WalkForwardConfig(
        train_size=args.train_size,
        test_size=args.test_size,
        step_size=args.step_size,
    )

    runner = WalkForwardRunner(backtest_config=backtest_config, wf_config=wf_config)
    windows = runner.run(bars, strategies)
    summary = runner.summarize(windows)
    write_summary_artifacts(args.output_dir, summary, windows)

    out = Path(args.output_dir)
    print("Backtest completed.")
    print(f"- Strategies: {[s.name for s in strategies]}")
    print(f"- Walk-forward windows: {len(windows)}")
    print(f"- Artifacts: {out.resolve()}")


if __name__ == "__main__":
    main()
