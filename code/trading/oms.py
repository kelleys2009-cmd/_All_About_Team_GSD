from __future__ import annotations

import uuid
from dataclasses import dataclass, field, replace
from typing import Callable, Dict, List, Optional, Protocol

from .risk_controls import AccountState, PreTradeRiskEngine, ProposedOrder, RiskDecision

MetricHook = Callable[[str, float, Dict[str, str]], None]
EventHook = Callable[[str, Dict[str, object]], None]


@dataclass(frozen=True)
class OrderIntent:
    client_order_id: str
    symbol: str
    side: str
    quantity: float
    limit_price: float
    timestamp_ms: int
    expected_slippage_bps: float = 0.0


@dataclass(frozen=True)
class OrderRecord:
    order_id: str
    client_order_id: str
    symbol: str
    side: str
    quantity: float
    limit_price: float
    timestamp_ms: int
    status: str
    risk_violations: List[str] = field(default_factory=list)
    exchange_order_id: Optional[str] = None


@dataclass(frozen=True)
class OrderSubmitResult:
    accepted: bool
    duplicate: bool
    order: OrderRecord
    risk_decision: Optional[RiskDecision] = None


@dataclass(frozen=True)
class LifecycleResult:
    success: bool
    order: Optional[OrderRecord]
    reason: Optional[str] = None


class OrderStore(Protocol):
    def get(self, client_order_id: str) -> Optional[OrderRecord]:
        ...

    def get_by_order_id(self, order_id: str) -> Optional[OrderRecord]:
        ...

    def upsert(self, record: OrderRecord) -> None:
        ...


class ExchangeAdapter(Protocol):
    def submit_limit(self, order: OrderRecord) -> tuple[bool, Optional[str], Optional[str]]:
        """Return (ok, exchange_order_id, error_message)."""

    def cancel(self, order: OrderRecord) -> tuple[bool, Optional[str]]:
        """Return (ok, error_message)."""


class InMemoryOrderStore:
    def __init__(self) -> None:
        self._by_client_order_id: Dict[str, OrderRecord] = {}
        self._by_order_id: Dict[str, OrderRecord] = {}

    def get(self, client_order_id: str) -> Optional[OrderRecord]:
        return self._by_client_order_id.get(client_order_id)

    def get_by_order_id(self, order_id: str) -> Optional[OrderRecord]:
        return self._by_order_id.get(order_id)

    def upsert(self, record: OrderRecord) -> None:
        self._by_client_order_id[record.client_order_id] = record
        self._by_order_id[record.order_id] = record


class OrderManagementService:
    """Risk-gated OMS admission path with idempotent client order IDs."""

    def __init__(
        self,
        risk_engine: PreTradeRiskEngine,
        order_store: OrderStore,
        exchange_adapter: Optional[ExchangeAdapter] = None,
        metric_hook: Optional[MetricHook] = None,
        event_hook: Optional[EventHook] = None,
    ) -> None:
        self._risk_engine = risk_engine
        self._order_store = order_store
        self._exchange_adapter = exchange_adapter
        self._metric_hook = metric_hook
        self._event_hook = event_hook

    def submit_order(
        self,
        intent: OrderIntent,
        account_state: AccountState,
    ) -> OrderSubmitResult:
        existing = self._order_store.get(intent.client_order_id)
        if existing is not None:
            self._emit_metric("oms.order.duplicate", 1.0, {"symbol": intent.symbol})
            self._emit_event(
                "order_duplicate",
                {
                    "client_order_id": intent.client_order_id,
                    "existing_order_id": existing.order_id,
                    "status": existing.status,
                },
            )
            return OrderSubmitResult(
                accepted=existing.status in ("pending_submit", "open"),
                duplicate=True,
                order=existing,
                risk_decision=None,
            )

        proposed = ProposedOrder(
            symbol=intent.symbol,
            side=intent.side,
            quantity=intent.quantity,
            price=intent.limit_price,
            timestamp_ms=intent.timestamp_ms,
            expected_slippage_bps=intent.expected_slippage_bps,
        )
        risk_decision = self._risk_engine.evaluate(proposed, account_state)

        if not risk_decision.approved:
            record = OrderRecord(
                order_id=self._new_order_id(),
                client_order_id=intent.client_order_id,
                symbol=intent.symbol,
                side=intent.side,
                quantity=intent.quantity,
                limit_price=intent.limit_price,
                timestamp_ms=intent.timestamp_ms,
                status="rejected_risk",
                risk_violations=risk_decision.violations,
            )
            self._order_store.upsert(record)
            self._emit_metric("oms.order.rejected", 1.0, {"symbol": intent.symbol})
            for violation in risk_decision.violations:
                self._emit_metric(
                    "oms.order.rejected_violation", 1.0, {"violation": violation}
                )
            self._emit_event(
                "order_rejected_risk",
                {
                    "client_order_id": intent.client_order_id,
                    "order_id": record.order_id,
                    "violations": list(risk_decision.violations),
                },
            )
            return OrderSubmitResult(
                accepted=False,
                duplicate=False,
                order=record,
                risk_decision=risk_decision,
            )

        record = OrderRecord(
            order_id=self._new_order_id(),
            client_order_id=intent.client_order_id,
            symbol=intent.symbol,
            side=intent.side,
            quantity=intent.quantity,
            limit_price=intent.limit_price,
            timestamp_ms=intent.timestamp_ms,
            status="pending_submit",
            risk_violations=[],
        )
        self._order_store.upsert(record)
        self._emit_metric("oms.order.accepted", 1.0, {"symbol": intent.symbol})
        self._emit_event(
            "order_accepted",
            {
                "client_order_id": intent.client_order_id,
                "order_id": record.order_id,
                "symbol": intent.symbol,
                "side": intent.side,
                "quantity": intent.quantity,
                "limit_price": intent.limit_price,
            },
        )
        return OrderSubmitResult(
            accepted=True,
            duplicate=False,
            order=record,
            risk_decision=risk_decision,
        )

    def dispatch_pending(self, order_id: str) -> LifecycleResult:
        order = self._order_store.get_by_order_id(order_id)
        if order is None:
            return LifecycleResult(success=False, order=None, reason="order_not_found")
        if order.status != "pending_submit":
            return LifecycleResult(success=False, order=order, reason="order_not_pending")
        if self._exchange_adapter is None:
            return LifecycleResult(success=False, order=order, reason="exchange_not_configured")

        ok, exchange_order_id, error = self._exchange_adapter.submit_limit(order)
        if not ok:
            failed = replace(order, status="submit_failed")
            self._order_store.upsert(failed)
            self._emit_metric("oms.order.submit_failed", 1.0, {"symbol": order.symbol})
            self._emit_event(
                "order_submit_failed",
                {
                    "order_id": order.order_id,
                    "client_order_id": order.client_order_id,
                    "error": error,
                },
            )
            return LifecycleResult(success=False, order=failed, reason=error or "submit_failed")

        opened = replace(order, status="open", exchange_order_id=exchange_order_id)
        self._order_store.upsert(opened)
        self._emit_metric("oms.order.submitted", 1.0, {"symbol": order.symbol})
        self._emit_event(
            "order_submitted",
            {
                "order_id": order.order_id,
                "client_order_id": order.client_order_id,
                "exchange_order_id": exchange_order_id,
            },
        )
        return LifecycleResult(success=True, order=opened, reason=None)

    def cancel_order(self, order_id: str) -> LifecycleResult:
        order = self._order_store.get_by_order_id(order_id)
        if order is None:
            return LifecycleResult(success=False, order=None, reason="order_not_found")
        if order.status not in ("open", "pending_submit"):
            return LifecycleResult(success=False, order=order, reason="order_not_cancellable")
        if self._exchange_adapter is None:
            return LifecycleResult(success=False, order=order, reason="exchange_not_configured")

        ok, error = self._exchange_adapter.cancel(order)
        if not ok:
            self._emit_metric("oms.order.cancel_failed", 1.0, {"symbol": order.symbol})
            self._emit_event(
                "order_cancel_failed",
                {
                    "order_id": order.order_id,
                    "client_order_id": order.client_order_id,
                    "error": error,
                },
            )
            return LifecycleResult(success=False, order=order, reason=error or "cancel_failed")

        canceled = replace(order, status="canceled")
        self._order_store.upsert(canceled)
        self._emit_metric("oms.order.canceled", 1.0, {"symbol": order.symbol})
        self._emit_event(
            "order_canceled",
            {
                "order_id": order.order_id,
                "client_order_id": order.client_order_id,
                "exchange_order_id": order.exchange_order_id,
            },
        )
        return LifecycleResult(success=True, order=canceled, reason=None)

    @staticmethod
    def _new_order_id() -> str:
        return str(uuid.uuid4())

    def _emit_metric(self, name: str, value: float, tags: Dict[str, str]) -> None:
        if self._metric_hook is not None:
            self._metric_hook(name, value, tags)

    def _emit_event(self, event_name: str, payload: Dict[str, object]) -> None:
        if self._event_hook is not None:
            self._event_hook(event_name, payload)
