# Team GSD — All About Team GSD

This is the central workspace for Team GSD's AI agents running on Paperclip.

## Projects
- **Strategy #1** — Core trading strategy research and implementation (target: May 31 2026)
- **Onboarding** — Agent setup and tooling

## Structure
- `/strategy/` — Strategy research, backtests, signals, config
- `/research/` — Market research, data analysis, reports
- `/code/` — Scripts, agents, automation
- `/docs/` — Documentation, notes, decisions

## Agents
| Agent | Role | Model |
|-------|------|-------|
| CEO | Orchestrator | gpt-5.3-codex |
| Code Agent | Software Engineer | gpt-5.3-codex |
| Founding Engineer | Engineer | gpt-5.3-codex |
| Research Analyst | Senior Research Analyst | gpt-5.3-codex |
| Roy | Finance Research Analyst | gpt-5.3-codex |

## Strategy Experimentation Scaffold
- Contract: `strategy/contracts.py`
- Candidates: `strategy/candidates/`
- Backtest harness: `strategy/backtest.py`
- CLI: `code/run_backtest.py`

Run standardized backtests:

```bash
python3 code/run_backtest.py --strategy mean_reversion --periods 250 --seed 42
python3 code/run_backtest.py --strategy momentum_breakout --periods 250 --seed 42
python3 code/run_backtest.py --strategy volatility_regime --periods 250 --seed 42
```

## Backtesting Engine

The core walk-forward backtesting framework lives in `/code/backtesting/`.

### What It Supports
- Consistent transaction-cost model:
  - per-trade commission
  - configurable slippage in basis points
- Multi-strategy evaluation over identical windows
- Walk-forward window slicing (`train_size`, `test_size`, `step_size`)
- Comparable summary artifacts:
  - `strategy_summary.json`
  - `strategy_summary.csv`
  - `walkforward_windows.json`
- Strategy scaffold integration through module contract:
  - strategy module must expose `build_strategy()`
  - returned object must provide `name` and `generate_signals(bars)`

### Run Example

Run from repository root:

```bash
PYTHONPATH=code python code/run_backtests.py \
  --prices-csv research/sample_prices.csv \
  --strategy strategy/scaffold_strategy.py \
  --strategy strategy/sma_crossover_strategy.py \
  --train-size 80 \
  --test-size 40 \
  --step-size 20 \
  --commission 1.0 \
  --slippage-bps 2.0 \
  --output-dir artifacts/backtests
```

### Current Limitations
- Single-asset only (`timestamp`, `close`)
- No borrow fees or funding model for shorts
- No intrabar fills; execution is close-price based
- No benchmark-relative metrics yet
