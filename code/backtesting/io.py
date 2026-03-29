from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

from .types import Bar
from .walkforward import WalkForwardStrategySummary, WalkForwardWindowResult


def load_bars_from_csv(path: str) -> List[Bar]:
    bars: List[Bar] = []
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamp = datetime.fromisoformat(row["timestamp"])
            close = float(row["close"])
            bars.append(Bar(timestamp=timestamp, close=close))
    bars.sort(key=lambda b: b.timestamp)
    return bars


def write_summary_artifacts(
    output_dir: str,
    strategy_summary: Dict[str, WalkForwardStrategySummary],
    windows: Iterable[WalkForwardWindowResult],
) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    summary_json = out / "strategy_summary.json"
    with summary_json.open("w") as f:
        json.dump(
            {k: v.to_dict() for k, v in strategy_summary.items()},
            f,
            indent=2,
            sort_keys=True,
        )

    summary_csv = out / "strategy_summary.csv"
    with summary_csv.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "strategy_name",
                "average_total_return",
                "average_sharpe_ratio",
                "average_max_drawdown",
                "total_trades",
                "windows",
            ]
        )
        for strategy_name, summary in sorted(strategy_summary.items()):
            writer.writerow(
                [
                    strategy_name,
                    summary.average_total_return,
                    summary.average_sharpe_ratio,
                    summary.average_max_drawdown,
                    summary.total_trades,
                    summary.windows,
                ]
            )

    windows_json = out / "walkforward_windows.json"
    serialized_windows = []
    for window in windows:
        serialized_windows.append(
            {
                "window_index": window.window_index,
                "train_start": window.train_start.isoformat(),
                "train_end": window.train_end.isoformat(),
                "test_start": window.test_start.isoformat(),
                "test_end": window.test_end.isoformat(),
                "strategies": {
                    strategy_name: result.metrics.to_dict()
                    for strategy_name, result in window.by_strategy.items()
                },
            }
        )

    with windows_json.open("w") as f:
        json.dump(serialized_windows, f, indent=2, sort_keys=True)
