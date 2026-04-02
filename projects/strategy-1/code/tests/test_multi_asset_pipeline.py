from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_CODE = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_CODE.parents[2]
SHARED_CODE = REPO_ROOT / "code"

for path in (PROJECT_CODE, SHARED_CODE):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from multi_asset_backtest.pipeline import (  # noqa: E402
    PipelineConfig,
    resolve_assets,
    run_pipeline,
)


class MultiAssetPipelineTest(unittest.TestCase):
    def test_resolve_assets_dedupes_and_normalizes(self) -> None:
        self.assertEqual(resolve_assets(["btc", "ETH", "btc"]), ["BTC", "ETH"])

    def test_run_pipeline_writes_expected_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            dataset_dir = tmp / "dataset"
            output_dir = tmp / "artifacts"
            dataset_dir.mkdir(parents=True, exist_ok=True)

            assets = ["BTC", "ETH", "SOL", "XRP", "DOGE"]
            start = datetime(2024, 1, 1)
            for i, asset in enumerate(assets):
                self._write_asset_csv(dataset_dir / f"{asset}.csv", start, base=100 + i * 10)

            config = PipelineConfig(
                dataset_dir=dataset_dir,
                output_dir=output_dir,
                assets=assets,
                strategy_paths=[str(PROJECT_CODE / "multi_asset_backtest" / "buy_hold_strategy.py")],
                initial_cash=10_000.0,
                bars_per_year=365,
                train_size=20,
                test_size=10,
                step_size=10,
            )

            manifest_path = run_pipeline(config)
            self.assertTrue(manifest_path.exists())

            with manifest_path.open("r") as f:
                manifest = json.load(f)
            self.assertEqual(manifest["assets"], assets)
            self.assertEqual(len(manifest["source_files"]), 5)

            combined_csv = output_dir / "combined_strategy_summary.csv"
            self.assertTrue(combined_csv.exists())
            with combined_csv.open("r", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 5)
            self.assertTrue(all(row["strategy_name"] == "buy_and_hold" for row in rows))

            for asset in assets:
                self.assertTrue((output_dir / asset / "strategy_summary.json").exists())
                self.assertTrue((output_dir / asset / "strategy_summary.csv").exists())
                self.assertTrue((output_dir / asset / "walkforward_windows.json").exists())

    @staticmethod
    def _write_asset_csv(path: Path, start: datetime, base: float) -> None:
        with path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "close"])
            price = base
            for day in range(50):
                ts = start + timedelta(days=day)
                # Deterministic mild trend with tiny oscillation.
                price = price * (1.001 + ((day % 5) - 2) * 0.0002)
                writer.writerow([ts.isoformat(), f"{price:.6f}"])


if __name__ == "__main__":
    unittest.main()
