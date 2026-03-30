# VLCC Fallback Execution Plan (TEA-32)

- Date: 2026-03-30
- Author: Devin Sailer

## Summary
A narrowed fallback path was prepared to keep VLCC securement moving under CEO-approved workaround policy when full prerequisite data is delayed. The approach enables RFQ + shortlist activity immediately, with explicit assumptions and kill-switches to prevent unsafe final fixture.

## Implementation details
- Added readiness validation script: `agents/devin-sailer/spikes/vlcc_readiness_validator.py`.
- Validation model separates two gates:
  - `ready_for_rfq`: minimal market metadata present (ports + cargo fields).
  - `ready_for_fixture`: all mandatory execution fields present and route risk not red.
- Provisional assumptions used when data is missing:
  - `laycan_flex_days = 3`
  - `cost_tolerance_pct = 10`
  - `route_risk_status = amber`
- Risk delta under fallback mode:
  - increased pricing uncertainty before final strategy envelope,
  - elevated legal/commercial variance risk if broker terms diverge,
  - mitigated by hold-before-fixture and explicit escalation triggers.

## Usage
1. Create a JSON payload with current known inputs:
```json
{
  "load_port": "Ras Tanura",
  "discharge_port": "Ningbo",
  "cargo_grade": "Arab Light",
  "cargo_quantity_bbl": 2000000,
  "laycan_start_utc": "2026-04-03T00:00:00Z",
  "laycan_end_utc": "2026-04-06T00:00:00Z",
  "signing_authority": "board",
  "cost_cap_usd": 14500000,
  "route_risk_status": "amber"
}
```
2. Run validator:
```bash
python3 agents/devin-sailer/spikes/vlcc_readiness_validator.py /path/to/payload.json
```
3. Interpret output:
- If `ready_for_rfq=true`, continue broker outreach and shortlist.
- If `ready_for_fixture=false`, do not fix vessel; post missing fields and risk delta in TEA-32.

## Known limitations or TODOs
- No live broker API integration yet; inputs are manual.
- No sanctions screening hook in validator; add integration with compliance service.
- No dynamic insurance quote feed; costs are static unless manually updated.
- TODO: wire this gate into OMS pre-trade checks once platform execution module is active.
