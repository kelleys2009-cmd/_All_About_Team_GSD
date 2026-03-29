"""Strategy registry for CLI and experimentation wiring."""

from strategy.candidates.mean_reversion import MeanReversionStrategy
from strategy.candidates.momentum_breakout import MomentumBreakoutStrategy
from strategy.candidates.volatility_regime import VolatilityRegimeStrategy

STRATEGY_REGISTRY = {
    MeanReversionStrategy.name: MeanReversionStrategy,
    MomentumBreakoutStrategy.name: MomentumBreakoutStrategy,
    VolatilityRegimeStrategy.name: VolatilityRegimeStrategy,
}


def create_strategy(strategy_name: str):
    try:
        return STRATEGY_REGISTRY[strategy_name]()
    except KeyError as exc:
        available = ", ".join(sorted(STRATEGY_REGISTRY))
        raise ValueError(f"Unknown strategy '{strategy_name}'. Available: {available}") from exc
