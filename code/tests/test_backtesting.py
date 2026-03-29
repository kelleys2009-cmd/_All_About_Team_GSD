from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from backtesting.engine import BacktestEngine
from backtesting.io import write_summary_artifacts
from backtesting.types import BacktestConfig, Bar, WalkForwardConfig
from backtesting.walkforward import WalkForwardRunner


class LongOnlyStrategy:
    name = "long_only"

    def generate_signals(self, bars):
        return [1 for _ in bars]


class FlipFlopStrategy:
    name = "flip_flop"

    def generate_signals(self, bars):
        return [1 if i % 2 == 0 else -1 for i in range(len(bars))]


def build_bars(n: int) -> list[Bar]:
    start = datetime(2024, 1, 1)
    return [
        Bar(timestamp=start + timedelta(days=i), close=100.0 + float(i))
        for i in range(n)
    ]


class BacktestingTests(unittest.TestCase):
    def test_commission_and_slippage_reduce_returns(self):
        bars = build_bars(30)
        strat = LongOnlyStrategy()

        base_result = BacktestEngine(
            BacktestConfig(
                initial_cash=10_000,
                per_trade_commission=0.0,
                slippage_bps=0.0,
                bars_per_year=252,
            )
        ).run(bars, strat)
        costly_result = BacktestEngine(
            BacktestConfig(
                initial_cash=10_000,
                per_trade_commission=5.0,
                slippage_bps=25.0,
                bars_per_year=252,
            )
        ).run(bars, strat)

        self.assertGreater(
            base_result.metrics.total_return, costly_result.metrics.total_return
        )

    def test_walk_forward_outputs_summary_and_artifacts(self):
        bars = build_bars(80)
        runner = WalkForwardRunner(
            backtest_config=BacktestConfig(
                initial_cash=50_000,
                per_trade_commission=1.0,
                slippage_bps=2.0,
            ),
            wf_config=WalkForwardConfig(train_size=30, test_size=20, step_size=10),
        )

        windows = runner.run(bars, [LongOnlyStrategy(), FlipFlopStrategy()])
        summary = runner.summarize(windows)

        self.assertGreaterEqual(len(windows), 1)
        self.assertIn("long_only", summary)
        self.assertIn("flip_flop", summary)
        self.assertGreater(summary["flip_flop"].total_trades, 0)

        with tempfile.TemporaryDirectory() as tmpdir:
            write_summary_artifacts(tmpdir, summary, windows)
            root = Path(tmpdir)
            self.assertTrue((root / "strategy_summary.json").exists())
            self.assertTrue((root / "strategy_summary.csv").exists())
            self.assertTrue((root / "walkforward_windows.json").exists())

            parsed = json.loads((root / "strategy_summary.json").read_text())
            self.assertIn("long_only", parsed)
            self.assertIn("average_sharpe_ratio", parsed["long_only"])


if __name__ == "__main__":
    unittest.main()
