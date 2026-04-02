# Weekly Multi-Coin Signal Summary Template + First Pass Output
Date: 2026-04-02
Author: Irene (Software Engineer)

## Summary
Built a reusable weekly signal summary template for BTC, ETH, SOL, XRP, and DOGE, including per-signal records and performance breakout tables. Produced a first-pass output for the current cycle using available project context; execution-level signal logs were not present in the workspace, so performance cells are marked as `N/A` and counts default to `0` until upstream exports are connected.

## Details

### 1) Weekly Signal Log Template (By Coin)
Use one row per generated signal event.

| week_start_utc | week_end_utc | timestamp_utc | timestamp_mst | asset | signal_type | side | entry_price_usd | exit_price_usd | status | pnl_usd | pnl_pct | trigger_event | notes |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | ---: | ---: | --- | --- |
| YYYY-MM-DD 00:00:00 | YYYY-MM-DD 23:59:59 | YYYY-MM-DD HH:MM:SS | YYYY-MM-DD HH:MM:SS | BTC/ETH/SOL/XRP/DOGE | MOMO-L/MOMO-S/FADE/DIP-LONG/PROBE-L/PROBE-S/TP/STOP | LONG/SHORT | 0.00 | 0.00 | open/closed | 0.00 | 0.00% | signal_open/signal_close/tp/stop | free text |

### 2) First-Pass Weekly Output (Week Ending 2026-04-01 UTC)

#### 2.1 Signal Count Snapshot by Coin and Type
| Asset | MOMO-L | MOMO-S | FADE | DIP-LONG | PROBE-L | PROBE-S | TP | STOP | Total Signals |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BTC | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ETH | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| SOL | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| XRP | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| DOGE | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

#### 2.2 Win-Rate and P&L Breakout by Signal Type and Coin
- `Win Rate` definition: closed trades with positive `pnl_usd` / total closed trades.
- `Net P&L` definition: sum of `pnl_usd` over closed trades for the week.

| Signal Type | BTC Win Rate | BTC Net P&L | ETH Win Rate | ETH Net P&L | SOL Win Rate | SOL Net P&L | XRP Win Rate | XRP Net P&L | DOGE Win Rate | DOGE Net P&L |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MOMO-L | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| MOMO-S | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| FADE | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| DIP-LONG | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| PROBE-L | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| PROBE-S | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| TP | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| STOP | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

#### 2.3 Weekly Leaderboard (Auto-fill Once Logs Exist)
| Metric | Value |
| --- | --- |
| Best asset by net P&L | N/A |
| Worst asset by net P&L | N/A |
| Best signal type by win rate | N/A |
| Worst signal type by win rate | N/A |
| Portfolio net weekly P&L (paper) | N/A |

### 3) Missing Data Fields Required for Full Automation
Current workspace does not contain a machine-readable weekly signal export. To automate this report, upstream logs must include at minimum:

| Field | Required | Purpose |
| --- | --- | --- |
| `signal_id` | Yes | Deduplicate and track lifecycle updates |
| `generated_at_utc` | Yes | Timestamping and week bucketing |
| `asset` | Yes | Coin-level breakout |
| `signal_type` | Yes | Strategy-type breakout |
| `side` | Yes | LONG/SHORT performance attribution |
| `entry_price_usd` | Yes | P&L computation |
| `exit_price_usd` | Yes (for closed) | P&L computation |
| `status` (`open`/`closed`) | Yes | Win-rate denominator control |
| `close_reason` (`tp`/`stop`/`manual`/`timeout`) | Yes | TP/STOP reporting |
| `size_units` or `notional_usd` | Yes | Normalized P&L and risk sizing |
| `fees_usd` | Yes | Net vs gross performance |
| `slippage_usd` | Recommended | Realistic post-cost results |
| `strategy_version` | Recommended | Backward-compatible analytics |

Blocking gap: no source file/API endpoint for Bart Bot signal events is currently available in this project workspace, so report generation cannot yet compute real win rates or realized P&L.

## Usage
1. Export weekly signal events from Bart Bot into a table with the required fields above.
2. Populate the template table row-per-signal.
3. Group by `asset` and `signal_type` for counts, win rate, and net P&L.
4. Fill leaderboard metrics and publish in the weekly report draft.

## Next Steps or Open Questions
1. Confirm canonical source of truth for signal events (file path or API endpoint).
2. Define P&L convention (`unit-based` vs `fixed-notional`) across all five assets.
3. Add a small script to auto-generate this markdown from weekly exported JSON/CSV.
4. Coordinate with Devin on scheduled export reliability and schema versioning.
