# Strategy Experimentation Scaffold

This scaffold supports rapid candidate strategy swaps with a shared contract and backtest harness.

## Layout
- `strategy/contracts.py` - Strategy protocol and shared dataclasses
- `strategy/candidates/` - Candidate strategy modules
- `strategy/registry.py` - CLI-facing strategy registry
- `strategy/backtest.py` - Standardized simulation and summary metrics
- `code/run_backtest.py` - CLI entrypoint

## Standardized Backtest Command

```bash
python3 code/run_backtest.py --strategy <strategy_name> --periods 250 --seed 42
```

Available strategy names:
- `mean_reversion`
- `momentum_breakout`
- `volatility_regime`
