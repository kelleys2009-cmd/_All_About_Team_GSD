from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate candidate-vs-baseline delta table from strategy_summary.json"
    )
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--baseline", default="buy_and_hold")
    parser.add_argument("--out-csv", required=True)
    parser.add_argument("--out-md", required=True)
    parser.add_argument("--data-window", required=True)
    return parser.parse_args()


def _load_summary(path: str) -> Dict[str, Dict[str, float]]:
    with open(path, "r") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError("Expected strategy summary JSON object")
    return payload


def main() -> None:
    args = parse_args()
    summary = _load_summary(args.summary_json)

    if args.baseline not in summary:
        raise ValueError(f"Baseline '{args.baseline}' not found in summary")

    baseline = summary[args.baseline]
    rows = []
    for strategy_name, metrics in sorted(summary.items()):
        if strategy_name == args.baseline:
            continue
        rows.append(
            {
                "candidate": strategy_name,
                "data_window": args.data_window,
                "baseline_avg_total_return": baseline["average_total_return"],
                "candidate_avg_total_return": metrics["average_total_return"],
                "delta_avg_total_return": metrics["average_total_return"]
                - baseline["average_total_return"],
                "baseline_avg_sharpe": baseline["average_sharpe_ratio"],
                "candidate_avg_sharpe": metrics["average_sharpe_ratio"],
                "delta_avg_sharpe": metrics["average_sharpe_ratio"]
                - baseline["average_sharpe_ratio"],
                "baseline_avg_max_drawdown": baseline["average_max_drawdown"],
                "candidate_avg_max_drawdown": metrics["average_max_drawdown"],
                "delta_avg_max_drawdown": metrics["average_max_drawdown"]
                - baseline["average_max_drawdown"],
                "baseline_total_trades": baseline["total_trades"],
                "candidate_total_trades": metrics["total_trades"],
                "delta_total_trades": metrics["total_trades"] - baseline["total_trades"],
            }
        )

    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)

    md_lines = [
        "# Candidate vs Baseline",
        "",
        f"- Baseline: `{args.baseline}`",
        f"- Data window: `{args.data_window}`",
        "",
        "| Candidate | Delta Avg Total Return vs Baseline | Delta Avg Sharpe vs Baseline | Delta Avg Max Drawdown vs Baseline |",
        "|---|---:|---:|---:|",
    ]
    for row in rows:
        md_lines.append(
            "| {candidate} | {dret:.6f} | {dsharpe:.6f} | {ddd:.6f} |".format(
                candidate=row["candidate"],
                dret=row["delta_avg_total_return"],
                dsharpe=row["delta_avg_sharpe"],
                ddd=row["delta_avg_max_drawdown"],
            )
        )

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(md_lines) + "\n")

    print("Candidate-vs-baseline artifacts generated.")
    print(f"- CSV: {out_csv}")
    print(f"- MD: {out_md}")


if __name__ == "__main__":
    main()
