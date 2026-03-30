#!/usr/bin/env python3
"""Validate VLCC fixture prerequisites for TEA-32 workaround execution."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = [
    "load_port",
    "discharge_port",
    "cargo_grade",
    "cargo_quantity_bbl",
    "laycan_start_utc",
    "laycan_end_utc",
    "signing_authority",
    "cost_cap_usd",
]

ASSUMPTION_DEFAULTS = {
    "laycan_flex_days": 3,
    "cost_tolerance_pct": 10,
    "route_risk_status": "amber",
}


@dataclass
class ReadinessResult:
    missing_required: list[str]
    assumptions_used: dict[str, Any]
    ready_for_rfq: bool
    ready_for_fixture: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "missing_required": self.missing_required,
            "assumptions_used": self.assumptions_used,
            "ready_for_rfq": self.ready_for_rfq,
            "ready_for_fixture": self.ready_for_fixture,
        }


def _load_payload(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("Input JSON must be an object")
        return payload
    except FileNotFoundError as exc:
        raise SystemExit(f"Input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def evaluate(payload: dict[str, Any]) -> ReadinessResult:
    missing_required = [k for k in REQUIRED_FIELDS if not payload.get(k)]

    assumptions_used: dict[str, Any] = {}
    for key, value in ASSUMPTION_DEFAULTS.items():
        assumptions_used[key] = payload.get(key, value)

    # Workaround policy: RFQ can proceed if hard market metadata exists,
    # but final fixture requires all required fields.
    rfq_required = [
        "load_port",
        "discharge_port",
        "cargo_grade",
        "cargo_quantity_bbl",
    ]
    ready_for_rfq = all(payload.get(k) for k in rfq_required)
    ready_for_fixture = len(missing_required) == 0 and assumptions_used["route_risk_status"] != "red"

    return ReadinessResult(
        missing_required=missing_required,
        assumptions_used=assumptions_used,
        ready_for_rfq=ready_for_rfq,
        ready_for_fixture=ready_for_fixture,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate VLCC fixture readiness payload")
    parser.add_argument("input", type=Path, help="Path to readiness JSON payload")
    args = parser.parse_args()

    payload = _load_payload(args.input)
    result = evaluate(payload)
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
