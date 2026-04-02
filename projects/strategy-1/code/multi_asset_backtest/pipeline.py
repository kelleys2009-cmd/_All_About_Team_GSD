from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from backtesting.io import load_bars_from_csv, write_summary_artifacts
from backtesting.strategy import Strategy, load_strategy_from_module
from backtesting.types import BacktestConfig, WalkForwardConfig
from backtesting.walkforward import WalkForwardRunner

DEFAULT_ASSETS: Sequence[str] = ("BTC", "ETH", "SOL", "XRP", "DOGE")


@dataclass(frozen=True)
class CostModel:
    per_trade_commission: float
    slippage_bps: float


DEFAULT_COSTS: Dict[str, CostModel] = {
    "BTC": CostModel(per_trade_commission=0.50, slippage_bps=3.0),
    "ETH": CostModel(per_trade_commission=0.50, slippage_bps=3.0),
    "SOL": CostModel(per_trade_commission=0.50, slippage_bps=5.0),
    "XRP": CostModel(per_trade_commission=0.50, slippage_bps=5.0),
    "DOGE": CostModel(per_trade_commission=0.50, slippage_bps=8.0),
}


@dataclass(frozen=True)
class PipelineConfig:
    dataset_dir: Path
    output_dir: Path
    assets: List[str]
    strategy_paths: List[str]
    initial_cash: float
    bars_per_year: int
    train_size: int
    test_size: int
    step_size: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a reproducible 5-coin walk-forward backtest pipeline."
    )
    parser.add_argument(
        "--dataset-dir",
        required=True,
        help="Directory containing <ASSET>.csv files with timestamp,close columns.",
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--asset",
        action="append",
        dest="assets",
        help="Asset symbol. Repeat per symbol. Defaults to BTC/ETH/SOL/XRP/DOGE.",
    )
    parser.add_argument(
        "--strategy",
        action="append",
        required=False,
        dest="strategies",
        help="Path to a strategy module exposing build_strategy().",
    )
    parser.add_argument("--initial-cash", type=float, default=100_000.0)
    parser.add_argument("--bars-per-year", type=int, default=365)
    parser.add_argument("--train-size", type=int, required=True)
    parser.add_argument("--test-size", type=int, required=True)
    parser.add_argument("--step-size", type=int, required=True)
    return parser.parse_args()


def resolve_assets(raw_assets: Iterable[str] | None) -> List[str]:
    assets = [a.upper() for a in (raw_assets or DEFAULT_ASSETS)]
    deduped = sorted(set(assets), key=assets.index)
    if not deduped:
        raise ValueError("At least one asset must be specified")
    return deduped


def resolve_strategies(raw_paths: Iterable[str] | None) -> List[str]:
    if raw_paths:
        return list(raw_paths)
    return [str(Path(__file__).with_name("buy_hold_strategy.py"))]


def sha256_for_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def assert_expected_schema(path: Path) -> int:
    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        required = {"timestamp", "close"}
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header")
        found = {name.strip() for name in reader.fieldnames}
        if not required.issubset(found):
            raise ValueError(
                f"{path} missing required columns. Expected {sorted(required)} got {sorted(found)}"
            )

        rows = 0
        for row in reader:
            _ = datetime.fromisoformat(row["timestamp"])
            _ = float(row["close"])
            rows += 1

    if rows < 2:
        raise ValueError(f"{path} must contain at least 2 rows")
    return rows


def load_strategies(paths: Iterable[str]) -> List[Strategy]:
    return [load_strategy_from_module(path) for path in paths]


def git_rev_parse_head(cwd: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def run_pipeline(config: PipelineConfig) -> Path:
    output_dir = config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    strategies = load_strategies(config.strategy_paths)
    strategy_names = [s.name for s in strategies]

    wf_config = WalkForwardConfig(
        train_size=config.train_size,
        test_size=config.test_size,
        step_size=config.step_size,
    )

    combined_rows: List[Dict[str, object]] = []
    source_files: List[Dict[str, object]] = []

    for asset in config.assets:
        csv_path = config.dataset_dir / f"{asset}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing dataset file: {csv_path}")

        row_count = assert_expected_schema(csv_path)
        bars = load_bars_from_csv(str(csv_path))

        cost_model = DEFAULT_COSTS.get(asset, CostModel(0.50, 8.0))
        runner = WalkForwardRunner(
            backtest_config=BacktestConfig(
                initial_cash=config.initial_cash,
                per_trade_commission=cost_model.per_trade_commission,
                slippage_bps=cost_model.slippage_bps,
                bars_per_year=config.bars_per_year,
            ),
            wf_config=wf_config,
        )
        windows = runner.run(bars, strategies)
        summary = runner.summarize(windows)

        asset_dir = output_dir / asset
        write_summary_artifacts(str(asset_dir), summary, windows)

        for strategy_name, stats in sorted(summary.items()):
            combined_rows.append(
                {
                    "asset": asset,
                    "strategy_name": strategy_name,
                    "average_total_return": stats.average_total_return,
                    "average_sharpe_ratio": stats.average_sharpe_ratio,
                    "average_max_drawdown": stats.average_max_drawdown,
                    "total_trades": stats.total_trades,
                    "windows": stats.windows,
                    "per_trade_commission": cost_model.per_trade_commission,
                    "slippage_bps": cost_model.slippage_bps,
                }
            )

        source_files.append(
            {
                "asset": asset,
                "path": str(csv_path),
                "rows": row_count,
                "sha256": sha256_for_file(csv_path),
                "cost_model": asdict(cost_model),
            }
        )

    combined_summary = output_dir / "combined_strategy_summary.csv"
    with combined_summary.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "asset",
                "strategy_name",
                "average_total_return",
                "average_sharpe_ratio",
                "average_max_drawdown",
                "total_trades",
                "windows",
                "per_trade_commission",
                "slippage_bps",
            ],
        )
        writer.writeheader()
        writer.writerows(combined_rows)

    manifest = output_dir / "run_manifest.json"
    with manifest.open("w") as f:
        json.dump(
            {
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "assets": config.assets,
                "strategy_paths": config.strategy_paths,
                "strategy_names": strategy_names,
                "walkforward": {
                    "train_size": config.train_size,
                    "test_size": config.test_size,
                    "step_size": config.step_size,
                },
                "initial_cash": config.initial_cash,
                "bars_per_year": config.bars_per_year,
                "source_files": source_files,
                "combined_summary": str(combined_summary),
                "git_head": git_rev_parse_head(Path.cwd()),
            },
            f,
            indent=2,
            sort_keys=True,
        )

    return manifest


def main() -> None:
    args = parse_args()
    config = PipelineConfig(
        dataset_dir=Path(args.dataset_dir),
        output_dir=Path(args.output_dir),
        assets=resolve_assets(args.assets),
        strategy_paths=resolve_strategies(args.strategies),
        initial_cash=args.initial_cash,
        bars_per_year=args.bars_per_year,
        train_size=args.train_size,
        test_size=args.test_size,
        step_size=args.step_size,
    )
    manifest = run_pipeline(config)

    print("Multi-asset backtest pipeline completed.")
    print(f"- Assets: {config.assets}")
    print(f"- Strategies: {config.strategy_paths}")
    print(f"- Output: {config.output_dir.resolve()}")
    print(f"- Manifest: {manifest.resolve()}")


if __name__ == "__main__":
    main()
