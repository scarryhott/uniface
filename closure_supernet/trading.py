from __future__ import annotations

import hashlib
import json
import uuid
from decimal import Decimal
from typing import Any, TYPE_CHECKING

from .models import EvidenceStatus, Verdict
from .supernet_models import IntegrationStage, IntegrationStateCreate, ResourceEnvelope
from .trading_models import (
    ClassicalTransactionCreate,
    ExecutionMode,
    ExecutionSelection,
    ExecutionSelectionCreate,
    NumeraireEvaluationCreate,
    PnLEvaluationCreate,
    PriceShiftEvaluationCreate,
    TradeSide,
    TradingCircuitEvaluationCreate,
    TradingFieldProjection,
    TradingSystemEvaluationCreate,
    TransactionEvaluation,
)
from .trading_store import TradingStore, utcnow

if TYPE_CHECKING:
    from .runtime import ClosureSupernetRuntime


def _d(value: Any) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _s(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def _hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class ClassicalTradingManager:
    """NRRF780 trading as a simulation/evaluation lens of the one Supernet."""

    def __init__(self, runtime: "ClosureSupernetRuntime", store: TradingStore):
        self.runtime = runtime
        self.store = store

    def capabilities(self) -> dict[str, Any]:
        return {
            "formal_reading": "NRRF780",
            "canonical_runtime_operation": "integrate",
            "adapter_label": "trading",
            "six_layers": ["signed_size", "bid", "ask", "fill", "mark", "fee"],
            "layers_complete": True,
            "drop_fill_not_complete": True,
            "local_prices": ["bid", "ask", "fill", "mark"],
            "inf_costs": ["fee", "slippage", "cost"],
            "cost_layer_derived": True,
            "net_eq_neg_cost": True,
            "shift_invariant_flow": True,
            "numeraire_ratio_invariant": True,
            "execution_selector": "BUY→ASK / SELL→BID",
            "selector_is_rigid": True,
            "determination_issues_truth": False,
            "simulation_only": True,
            "direct_market_execution": False,
            "brokerage_connected": False,
            "automatic_order_submission": False,
            "market_data_live": False,
            "financial_advice": False,
        }

    @staticmethod
    def execution_selection(data: ExecutionSelectionCreate) -> ExecutionSelection:
        side = TradeSide.BUY if data.signed_size > 0 else TradeSide.SELL
        selected = data.ask if side == TradeSide.BUY else data.bid
        return ExecutionSelection(
            side=side,
            selected_fill=_s(selected),
            admissible_fills=[_s(selected)],
        )

    @staticmethod
    def evaluate_transaction(data: ClassicalTransactionCreate) -> TransactionEvaluation:
        size = _d(data.signed_size)
        bid = _d(data.bid)
        ask = _d(data.ask)
        fill = _d(data.fill)
        mark = _d(data.mark)
        fee = _d(data.fee)
        side = TradeSide.BUY if size > 0 else TradeSide.SELL
        selected_fill = ask if side == TradeSide.BUY else bid
        mid = (bid + ask) / Decimal("2")
        spread = ask - bid
        slippage = size * (fill - mark)
        cost = fee + slippage
        cash_flow = -(size * fill) - fee
        inventory_value = size * mark
        net = cash_flow + inventory_value
        residual = net + cost
        crossing = fill == selected_fill and mark == mid
        crossing_cost = fee + abs(size) * spread / Decimal("2") if crossing else None
        alt_fill = fill + Decimal("1")
        layers = {
            "signed_size": _s(size),
            "bid": _s(bid),
            "ask": _s(ask),
            "fill": _s(fill),
            "mark": _s(mark),
            "fee": _s(fee),
        }
        shifted_fill = fill + Decimal("1")
        shifted_mark = mark + Decimal("1")
        shifted_cost = fee + size * (shifted_fill - shifted_mark)
        shifted_net = size * (shifted_mark - shifted_fill) - fee
        ratio = net / cost if cost != 0 else None
        return TransactionEvaluation(
            side=side,
            six_layers=layers,
            layer_identity=_hash(layers),
            drop_fill_witness={
                **{key: value for key, value in layers.items() if key != "fill"},
                "fill_a": _s(fill),
                "fill_b": _s(alt_fill),
            },
            mid=_s(mid),
            spread=_s(spread),
            selected_fill=_s(selected_fill),
            execution_rigid=fill == selected_fill,
            slippage=_s(slippage),
            inf_cost=_s(cost),
            cash_flow=_s(cash_flow),
            inventory_value=_s(inventory_value),
            net_flow=_s(net),
            identity_residual=_s(residual),
            net_eq_neg_cost=residual == 0,
            flow_shift_invariant=shifted_net == net,
            fill_shift_invariant=shifted_fill == fill,
            crossing_at_quote_and_mid=crossing,
            crossing_expected_cost=_s(crossing_cost),
            crossing_strictly_negative=bool(crossing and net < 0),
            flow_cost_ratio=_s(ratio),
        )

    async def create_transaction(self, data: ClassicalTransactionCreate) -> dict[str, Any]:
        transaction_id = str(uuid.uuid4())
        evaluation = self.evaluate_transaction(data)
        exact_text = (
            f"Classical transaction {transaction_id}: symbol={data.symbol}; "
            f"signed_size={_s(data.signed_size)}; bid={_s(data.bid)}; ask={_s(data.ask)}; "
            f"fill={_s(data.fill)}; mark={_s(data.mark)}; fee={_s(data.fee)}; "
            f"net={evaluation.net_flow}; cost={evaluation.inf_cost}; net=-cost."
        )
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=exact_text,
                authored_by=data.authored_by,
                form_label="classical trading transaction",
                language_label="NRRF780 multilayer value flow",
                source_id="trading-supernet",
                perspective_id=data.perspective_id,
                problem_id=data.problem_id,
                capabilities=[
                    "six-layer monetary evaluation",
                    "local-price to inf-cost translation",
                    "source-reversible P&L return",
                ],
                constraints=[
                    "simulation and evaluation only",
                    "no broker or market-order execution",
                    "determination does not issue TRUE",
                ],
                relation_hints=[
                    "NRRF780",
                    "local prices",
                    "inf costs",
                    "multilayer value flow",
                    "execution selector",
                    data.symbol,
                ],
                affected_perspectives=[data.authored_by],
                evidence_status=EvidenceStatus.SIMULATED_UNDER_ASSUMPTIONS,
                adapter_label="trading",
                external_key=data.external_key or f"trading:transaction:{transaction_id}",
                metadata={
                    **data.metadata,
                    "trading_transaction_id": transaction_id,
                    "layers": evaluation.six_layers,
                    "evaluation": evaluation.model_dump(mode="json"),
                    "simulation_only": True,
                    "direct_market_execution": False,
                },
            )
        )
        event_id = receipt["event_id"]
        if data.execution_mode == ExecutionMode.SELECTOR_QUOTE:
            self.runtime.supernet_integrator.determine(
                event_id,
                actor_id=data.authored_by,
                rigidity_scope=["execution.fill"],
                rigidity_receipt={
                    "relation": "BUY→ASK / SELL→BID",
                    "side": evaluation.side.value,
                    "admissible_fills": [evaluation.selected_fill],
                    "unique": True,
                    "bid": _s(data.bid),
                    "ask": _s(data.ask),
                },
                determined_form={
                    "side": evaluation.side.value,
                    "fill": evaluation.selected_fill,
                    "symbol": data.symbol,
                },
                unitary_path_partition={
                    "path": ["signed_size", "quote", "fill", "mark", "fee", "cost", "net"],
                    "partition": {
                        "local": ["bid", "ask", "fill", "mark"],
                        "inf": ["fee", "slippage", "cost"],
                        "return": ["net_flow"],
                    },
                },
                reason="Rigid execution relation leaves the quote-side fill standing",
            )
        row = {
            "id": transaction_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": event_id,
            "symbol": data.symbol,
            "signed_size": _s(data.signed_size),
            "bid": _s(data.bid),
            "ask": _s(data.ask),
            "fill": _s(data.fill),
            "mark": _s(data.mark),
            "fee": _s(data.fee),
            "execution_mode": data.execution_mode.value,
            "currency": data.currency,
            "authored_by": data.authored_by,
            "perspective_id": data.perspective_id,
            "problem_id": data.problem_id,
            "evaluation": evaluation.model_dump(mode="json"),
            "metadata": {**data.metadata, "truth_issued": False},
            "created_at": utcnow(),
        }
        self.store.create_transaction(row)
        self.runtime.supernet_integrator.transition(
            event_id,
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason="Classical value-flow evaluation returned without issuing a truth verdict",
                actor_id=data.authored_by,
                returned_resource_ids=[transaction_id],
                successor_potential=[
                    {
                        "form_type": "trading-evaluation",
                        "form_id": transaction_id,
                        "symbol": data.symbol,
                        "net_flow": evaluation.net_flow,
                        "inf_cost": evaluation.inf_cost,
                    }
                ],
                metadata={
                    "nrrf780": True,
                    "net_eq_neg_cost": evaluation.net_eq_neg_cost,
                    "truth_issued": False,
                    "simulation_only": True,
                },
            ),
        )
        return self.store.get_transaction(transaction_id)

    async def evaluate_system(self, data: TradingSystemEvaluationCreate) -> dict[str, Any]:
        transactions = [self.store.get_transaction(item) for item in data.transaction_ids]
        total_cost = sum((_d(item["evaluation"]["inf_cost"]) for item in transactions), Decimal("0"))
        total_net = sum((_d(item["evaluation"]["net_flow"]) for item in transactions), Decimal("0"))
        residual = total_net + total_cost
        costs = [_d(item["evaluation"]["inf_cost"]) for item in transactions]
        all_nonnegative = all(item >= 0 for item in costs)
        any_positive = any(item > 0 for item in costs)
        ratio = total_net / total_cost if total_cost != 0 else None
        evaluation_id = str(uuid.uuid4())
        receipt = await self._integrate_analysis(
            analysis_id=evaluation_id,
            authored_by=data.authored_by,
            form_label="classical trading system evaluation",
            exact_text=(
                f"System {evaluation_id}: transactions={data.transaction_ids}; "
                f"total_net={_s(total_net)}; total_cost={_s(total_cost)}; system_net=-system_cost."
            ),
            parent_event_ids=[item["integration_event_id"] for item in transactions],
            relation_hints=["NRRF780", "sysNet_eq_neg_sysCost", "multilayer value flow"],
            metadata={"transaction_ids": data.transaction_ids, **data.metadata},
        )
        row = {
            "id": evaluation_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "transaction_ids": data.transaction_ids,
            "total_cost": _s(total_cost),
            "total_net": _s(total_net),
            "identity_residual": _s(residual),
            "sys_net_eq_neg_sys_cost": residual == 0,
            "all_costs_nonnegative": all_nonnegative,
            "any_cost_positive": any_positive,
            "nonpositive_when_charged": (not all_nonnegative) or total_net <= 0,
            "strictly_negative_once_charged": (not (all_nonnegative and any_positive)) or total_net < 0,
            "flow_cost_ratio": _s(ratio),
            "metadata": data.metadata,
            "created_at": utcnow(),
        }
        return self.store.create_system(row)

    async def evaluate_shift(self, data: PriceShiftEvaluationCreate) -> dict[str, Any]:
        tx = self.store.get_transaction(data.transaction_id)
        size, fill, mark, fee = _d(tx["signed_size"]), _d(tx["fill"]), _d(tx["mark"]), _d(tx["fee"])
        shift = _d(data.shift)
        original_cost = fee + size * (fill - mark)
        original_flow = size * (mark - fill) - fee
        shifted_fill, shifted_mark = fill + shift, mark + shift
        shifted_cost = fee + size * (shifted_fill - shifted_mark)
        shifted_flow = size * (shifted_mark - shifted_fill) - fee
        evaluation_id = str(uuid.uuid4())
        receipt = await self._integrate_analysis(
            analysis_id=evaluation_id,
            authored_by=data.authored_by,
            form_label="trading price-shift evaluation",
            exact_text=(
                f"Shift transaction {data.transaction_id} by {shift}: flow {_s(original_flow)}→{_s(shifted_flow)}, "
                f"cost {_s(original_cost)}→{_s(shifted_cost)}; local prices move while flow and cost remain."
            ),
            parent_event_ids=[tx["integration_event_id"]],
            relation_hints=["flow_shift", "fill_not_shift_invariant", "local prices"],
            metadata={"transaction_id": data.transaction_id, "shift": _s(shift)},
        )
        row = {
            "id": evaluation_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "transaction_id": data.transaction_id,
            "shift": _s(shift),
            "original_fill": _s(fill),
            "shifted_fill": _s(shifted_fill),
            "original_cost": _s(original_cost),
            "shifted_cost": _s(shifted_cost),
            "original_flow": _s(original_flow),
            "shifted_flow": _s(shifted_flow),
            "flow_shift_invariant": shifted_flow == original_flow,
            "cost_shift_invariant": shifted_cost == original_cost,
            "local_price_layer_changed": shift != 0 and shifted_fill != fill,
            "created_at": utcnow(),
        }
        return self.store.create_shift(row)

    async def evaluate_numeraire(self, data: NumeraireEvaluationCreate) -> dict[str, Any]:
        tx = self.store.get_transaction(data.transaction_id)
        scale = _d(data.scale)
        size, fill, mark, fee = _d(tx["signed_size"]), _d(tx["fill"]), _d(tx["mark"]), _d(tx["fee"])
        original_cost = fee + size * (fill - mark)
        original_flow = size * (mark - fill) - fee
        scaled_cost = fee * scale + size * ((fill * scale) - (mark * scale))
        scaled_flow = size * ((mark * scale) - (fill * scale)) - fee * scale
        original_ratio = original_flow / original_cost if original_cost != 0 else None
        scaled_ratio = scaled_flow / scaled_cost if scaled_cost != 0 else None
        evaluation_id = str(uuid.uuid4())
        receipt = await self._integrate_analysis(
            analysis_id=evaluation_id,
            authored_by=data.authored_by,
            form_label="trading numeraire evaluation",
            exact_text=f"Rescale transaction {data.transaction_id} by numeraire {scale}: flow and cost scale together.",
            parent_event_ids=[tx["integration_event_id"]],
            relation_hints=["flow_cost_ratio_invariant", "numeraire", "relative unity"],
            metadata={"transaction_id": data.transaction_id, "scale": _s(scale)},
        )
        row = {
            "id": evaluation_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "transaction_id": data.transaction_id,
            "scale": _s(scale),
            "original_cost": _s(original_cost),
            "scaled_cost": _s(scaled_cost),
            "original_flow": _s(original_flow),
            "scaled_flow": _s(scaled_flow),
            "cost_scales": scaled_cost == original_cost * scale,
            "flow_scales": scaled_flow == original_flow * scale,
            "original_ratio": _s(original_ratio),
            "scaled_ratio": _s(scaled_ratio),
            "flow_cost_ratio_invariant": original_ratio == scaled_ratio,
            "created_at": utcnow(),
        }
        return self.store.create_numeraire(row)

    async def evaluate_circuit(self, data: TradingCircuitEvaluationCreate) -> dict[str, Any]:
        moves = [_d(edge.local_price_move) for edge in data.edges]
        charges = [_d(edge.charge) for edge in data.edges]
        holonomy = sum(moves, Decimal("0"))
        total_cost = sum(charges, Decimal("0"))
        net = holonomy - total_cost
        exact = holonomy == 0
        profitable = net > 0
        per_edge_charge = min(charges)
        upper_bound = -(Decimal(len(data.edges)) * per_edge_charge)
        evaluation_id = str(uuid.uuid4())
        edges_payload = [
            {"edge_id": edge.edge_id, "local_price_move": _s(edge.local_price_move), "charge": _s(edge.charge)}
            for edge in data.edges
        ]
        receipt = await self._integrate_analysis(
            analysis_id=evaluation_id,
            authored_by=data.authored_by,
            form_label="classical trading circuit",
            exact_text=(
                f"Circuit {evaluation_id} on {data.symbol}: price_holonomy={_s(holonomy)}, "
                f"friction={_s(total_cost)}, net={_s(net)}, exact={exact}."
            ),
            parent_event_ids=[],
            relation_hints=["classical_roundTrip", "price holonomy", "global token", "profit_needs_nonexact"],
            metadata={"edges": edges_payload, **data.metadata},
        )
        row = {
            "id": evaluation_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "symbol": data.symbol,
            "edges": edges_payload,
            "circuit_length": len(data.edges),
            "price_holonomy": _s(holonomy),
            "total_cost": _s(total_cost),
            "net_flow": _s(net),
            "exact_price_field": exact,
            "global_token_exists": exact,
            "exact_round_trip_eq_neg_cost": (not exact) or net == -total_cost,
            "per_edge_charge": _s(per_edge_charge),
            "exact_round_trip_upper_bound": _s(upper_bound),
            "bound_holds": (not exact) or net <= upper_bound,
            "profitable": profitable,
            "profitable_iff_price_exceeds_cost": profitable == (holonomy > total_cost),
            "profit_needs_arbitrage": (not profitable) or holonomy > 0,
            "profit_needs_nonexact": (not profitable) or not exact,
            "metadata": {**data.metadata, "tolerance": _s(data.tolerance)},
            "created_at": utcnow(),
        }
        return self.store.create_circuit(row)

    async def evaluate_pnl(self, data: PnLEvaluationCreate) -> dict[str, Any]:
        position = _d(data.position)
        start, end = _d(data.start_mark), _d(data.end_mark)
        cost = _d(data.accumulated_cost)
        price_move = end - start
        pnl = position * price_move - cost
        returning = end == start
        returning_pnl = -cost if returning else None
        positive_condition = position * price_move > cost
        evaluation_id = str(uuid.uuid4())
        receipt = await self._integrate_analysis(
            analysis_id=evaluation_id,
            authored_by=data.authored_by,
            form_label="classical trading P&L path",
            exact_text=(
                f"P&L {evaluation_id} on {data.symbol}: position={_s(position)}, "
                f"price_move={_s(price_move)}, cost={_s(cost)}, pnl={_s(pnl)}."
            ),
            parent_event_ids=[],
            relation_hints=["pnl_const_position", "pnl_returning_market", "pnl_pos_iff"],
            metadata=data.metadata,
        )
        row = {
            "id": evaluation_id,
            "occurrence_id": receipt["occurrence_ids"][0],
            "integration_event_id": receipt["event_id"],
            "symbol": data.symbol,
            "position": _s(position),
            "start_mark": _s(start),
            "end_mark": _s(end),
            "price_move": _s(price_move),
            "accumulated_cost": _s(cost),
            "pnl": _s(pnl),
            "formula_holds": pnl == position * (end - start) - cost,
            "returning_market": returning,
            "returning_market_pnl": _s(returning_pnl),
            "returning_market_nonpositive": (not returning) or pnl <= 0,
            "positive": pnl > 0,
            "pnl_pos_iff_price_move_beats_cost": (pnl > 0) == positive_condition,
            "metadata": data.metadata,
            "created_at": utcnow(),
        }
        return self.store.create_pnl(row)

    async def _integrate_analysis(
        self,
        *,
        analysis_id: str,
        authored_by: str,
        form_label: str,
        exact_text: str,
        parent_event_ids: list[str],
        relation_hints: list[str],
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        receipt = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=exact_text,
                authored_by=authored_by,
                form_label=form_label,
                language_label="NRRF780 classical trading evaluation",
                source_id="trading-supernet",
                parent_event_ids=parent_event_ids,
                causal_predecessor_ids=parent_event_ids,
                capabilities=["classical value-flow evaluation", "source-reversible return"],
                constraints=["simulation only", "no automatic trade execution", "no financial advice"],
                relation_hints=["NRRF780", *relation_hints],
                affected_perspectives=[authored_by],
                evidence_status=EvidenceStatus.SIMULATED_UNDER_ASSUMPTIONS,
                adapter_label="trading",
                external_key=f"trading:analysis:{analysis_id}",
                metadata={**metadata, "trading_analysis_id": analysis_id, "truth_issued": False},
            )
        )
        self.runtime.supernet_integrator.transition(
            receipt["event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason="Trading analysis returned as a scoped simulation without issuing TRUE",
                actor_id=authored_by,
                returned_resource_ids=[analysis_id],
                successor_potential=[{"form_type": "trading-analysis", "form_id": analysis_id}],
                metadata={"nrrf780": True, "simulation_only": True, "truth_issued": False},
            ),
        )
        return receipt

    def projection(self, limit: int = 5000) -> dict[str, Any]:
        transactions = self.store.list_transactions(limit=limit)
        systems = self.store.list_systems(limit=limit)
        shifts = self.store.list_shifts(limit=limit)
        numeraires = self.store.list_numeraires(limit=limit)
        circuits = self.store.list_circuits(limit=limit)
        pnl = self.store.list_pnl(limit=limit)
        source_reverse_index: dict[str, list[str]] = {}
        for kind, items in (
            ("transaction", transactions), ("system", systems), ("shift", shifts),
            ("numeraire", numeraires), ("circuit", circuits), ("pnl", pnl),
        ):
            for item in items:
                source_reverse_index[f"trading:{kind}:{item['id']}"] = [item["occurrence_id"]]
        stats = self.store.stats()
        stats.update(
            {
                "strictly_negative_crossings": sum(
                    1 for item in transactions if item["evaluation"]["crossing_strictly_negative"]
                ),
                "profitable_circuits": sum(1 for item in circuits if item["profitable"]),
                "exact_circuits": sum(1 for item in circuits if item["exact_price_field"]),
                "simulation_only": True,
                "direct_market_execution": False,
            }
        )
        projection = TradingFieldProjection(
            generated_at=utcnow(), transactions=transactions, systems=systems,
            shifts=shifts, numeraires=numeraires, circuits=circuits, pnl=pnl,
            stats=stats, source_reverse_index=source_reverse_index,
        ).model_dump(mode="json")
        self.store.set_state("trading_field_projection", projection)
        return projection
