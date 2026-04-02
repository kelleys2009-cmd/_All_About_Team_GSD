from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set


@dataclass(frozen=True)
class ProposedOrder:
    symbol: str
    side: str
    quantity: float
    price: float
    timestamp_ms: int
    expected_slippage_bps: float = 0.0


@dataclass(frozen=True)
class PositionState:
    quantity: float
    mark_price: float


@dataclass(frozen=True)
class RiskLimits:
    max_order_notional_usd: float
    max_total_notional_usd: float
    max_leverage: float
    max_daily_realized_loss_usd: float
    max_slippage_bps: float
    max_orders_per_minute: int
    max_position_abs_qty: Dict[str, float] = field(default_factory=dict)
    max_symbol_notional_usd: Dict[str, float] = field(default_factory=dict)
    allowed_symbols: Optional[Set[str]] = None


@dataclass(frozen=True)
class AccountState:
    equity_usd: float
    realized_pnl_day_usd: float
    kill_switch_active: bool = False
    positions: Dict[str, PositionState] = field(default_factory=dict)
    recent_order_timestamps_ms: Sequence[int] = field(default_factory=tuple)


@dataclass(frozen=True)
class RiskDecision:
    approved: bool
    violations: List[str]


class PreTradeRiskEngine:
    """Deterministic pre-trade risk checks for OMS order admission."""

    def __init__(self, limits: RiskLimits):
        self.limits = limits

    def evaluate(self, order: ProposedOrder, state: AccountState) -> RiskDecision:
        violations: List[str] = []
        symbol = order.symbol.upper()
        side = order.side.lower()

        if side not in ("buy", "sell"):
            violations.append("invalid_side")
            return RiskDecision(approved=False, violations=violations)
        if order.quantity <= 0:
            violations.append("non_positive_quantity")
            return RiskDecision(approved=False, violations=violations)
        if order.price <= 0:
            violations.append("non_positive_price")
            return RiskDecision(approved=False, violations=violations)

        if state.kill_switch_active:
            violations.append("kill_switch_active")

        if self.limits.allowed_symbols is not None and symbol not in self.limits.allowed_symbols:
            violations.append("symbol_not_allowed")

        if state.realized_pnl_day_usd <= -abs(self.limits.max_daily_realized_loss_usd):
            violations.append("max_daily_loss_exceeded")

        if order.expected_slippage_bps > self.limits.max_slippage_bps:
            violations.append("slippage_limit_exceeded")

        order_notional = abs(order.quantity * order.price)
        if order_notional > self.limits.max_order_notional_usd:
            violations.append("max_order_notional_exceeded")

        position_limit = self.limits.max_position_abs_qty.get(symbol)
        current_qty = state.positions.get(symbol, PositionState(0.0, order.price)).quantity
        signed_delta = order.quantity if side == "buy" else -order.quantity
        post_qty = current_qty + signed_delta
        if position_limit is not None and abs(post_qty) > position_limit:
            violations.append("max_position_abs_qty_exceeded")

        symbol_notional_limit = self.limits.max_symbol_notional_usd.get(symbol)
        if symbol_notional_limit is not None and abs(post_qty * order.price) > symbol_notional_limit:
            violations.append("max_symbol_notional_exceeded")

        post_total_notional = self._gross_notional(state.positions, symbol, post_qty, order.price)
        if post_total_notional > self.limits.max_total_notional_usd:
            violations.append("max_total_notional_exceeded")

        leverage = self._safe_div(post_total_notional, state.equity_usd)
        if leverage > self.limits.max_leverage:
            violations.append("max_leverage_exceeded")

        orders_last_min = self._orders_in_last_minute(
            state.recent_order_timestamps_ms,
            now_ms=order.timestamp_ms,
        )
        if orders_last_min >= self.limits.max_orders_per_minute:
            violations.append("order_rate_limit_exceeded")

        return RiskDecision(approved=len(violations) == 0, violations=violations)

    @staticmethod
    def _gross_notional(
        positions: Dict[str, PositionState],
        update_symbol: str,
        update_qty: float,
        update_price: float,
    ) -> float:
        total = 0.0
        for symbol, pos in positions.items():
            if symbol.upper() == update_symbol.upper():
                continue
            total += abs(pos.quantity * pos.mark_price)
        total += abs(update_qty * update_price)
        return total

    @staticmethod
    def _orders_in_last_minute(timestamps_ms: Sequence[int], now_ms: int) -> int:
        threshold = now_ms - 60_000
        return sum(1 for ts in timestamps_ms if ts >= threshold)

    @staticmethod
    def _safe_div(numerator: float, denominator: float) -> float:
        if denominator <= 0:
            return float("inf")
        return numerator / denominator
