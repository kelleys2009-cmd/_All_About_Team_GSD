from __future__ import annotations

import uuid
from dataclasses import dataclass, field
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


@dataclass(frozen=True)
class OrderSubmitResult:
    accepted: bool
    duplicate: bool
    order: OrderRecord
    risk_decision: Optional[RiskDecision] = None


class OrderStore(Protocol):
    def get(self, client_order_id: str) -> Optional[OrderRecord]:
        ...

    def upsert(self, record: OrderRecord) -> None:
        ...


class InMemoryOrderStore:
    def __init__(self) -> None:
        self._by_client_order_id: Dict[str, OrderRecord] = {}

    def get(self, client_order_id: str) -> Optional[OrderRecord]:
        return self._by_client_order_id.get(client_order_id)

    def upsert(self, record: OrderRecord) -> None:
        self._by_client_order_id[record.client_order_id] = record


class OrderManagementService:
    """Risk-gated OMS admission path with idempotent client order IDs."""

    def __init__(
        self,
        risk_engine: PreTradeRiskEngine,
        order_store: OrderStore,
        metric_hook: Optional[MetricHook] = None,
        event_hook: Optional[EventHook] = None,
    ) -> None:
        self._risk_engine = risk_engine
        self._order_store = order_store
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
                accepted=existing.status == "pending_submit",
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

    @staticmethod
    def _new_order_id() -> str:
        return str(uuid.uuid4())

    def _emit_metric(self, name: str, value: float, tags: Dict[str, str]) -> None:
        if self._metric_hook is not None:
            self._metric_hook(name, value, tags)

    def _emit_event(self, event_name: str, payload: Dict[str, object]) -> None:
        if self._event_hook is not None:
            self._event_hook(event_name, payload)
