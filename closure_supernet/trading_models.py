from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class ExecutionMode(StrEnum):
    SELECTOR_QUOTE = "SELECTOR_QUOTE"
    EXPLICIT = "EXPLICIT"


class TradeSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class ClassicalTransactionCreate(BaseModel):
    symbol: str = Field(min_length=1, max_length=80)
    signed_size: Decimal
    bid: Decimal
    ask: Decimal
    fill: Decimal | None = None
    mark: Decimal
    fee: Decimal = Decimal("0")
    execution_mode: ExecutionMode = ExecutionMode.SELECTOR_QUOTE
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    perspective_id: str | None = None
    problem_id: str | None = None
    currency: str = Field(default="USD", min_length=1, max_length=32)
    external_key: str | None = Field(default=None, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_layers(self) -> "ClassicalTransactionCreate":
        if self.signed_size == 0:
            raise ValueError("signed_size must be non-zero")
        if self.bid > self.ask:
            raise ValueError("bid must be less than or equal to ask")
        if self.fee < 0:
            raise ValueError("fee must be non-negative")
        selected = self.ask if self.signed_size > 0 else self.bid
        if self.execution_mode == ExecutionMode.SELECTOR_QUOTE:
            if self.fill is not None and self.fill != selected:
                raise ValueError(
                    "SELECTOR_QUOTE execution is rigid: buy fills at ask and sell fills at bid"
                )
            self.fill = selected
        elif self.fill is None:
            raise ValueError("EXPLICIT execution requires fill")
        return self


class TransactionEvaluation(BaseModel):
    side: TradeSide
    six_layers: dict[str, str]
    layer_identity: str
    layers_complete: bool = True
    drop_fill_not_complete: bool = True
    drop_fill_witness: dict[str, str]
    mid: str
    spread: str
    selected_fill: str
    execution_rigid: bool
    slippage: str
    inf_cost: str
    cash_flow: str
    inventory_value: str
    net_flow: str
    identity_residual: str
    net_eq_neg_cost: bool
    cost_layer_redundant: bool = True
    local_not_recoverable_from_cost: bool = True
    flow_shift_invariant: bool
    fill_shift_invariant: bool
    crossing_at_quote_and_mid: bool
    crossing_expected_cost: str | None = None
    crossing_strictly_negative: bool
    flow_cost_ratio: str | None = None
    truth_issued: bool = False


class ClassicalTransaction(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    symbol: str
    signed_size: str
    bid: str
    ask: str
    fill: str
    mark: str
    fee: str
    execution_mode: ExecutionMode
    currency: str
    authored_by: str
    perspective_id: str | None
    problem_id: str | None
    evaluation: TransactionEvaluation
    metadata: dict[str, Any]
    created_at: str


class TradingSystemEvaluationCreate(BaseModel):
    transaction_ids: list[str] = Field(min_length=1)
    authored_by: str = Field(default="participant", min_length=1)
    label: str = Field(default="classical trading system", min_length=1, max_length=240)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def unique_transactions(self) -> "TradingSystemEvaluationCreate":
        self.transaction_ids = list(dict.fromkeys(self.transaction_ids))
        if not self.transaction_ids:
            raise ValueError("at least one transaction is required")
        return self


class TradingSystemEvaluation(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    transaction_ids: list[str]
    total_cost: str
    total_net: str
    identity_residual: str
    sys_net_eq_neg_sys_cost: bool
    all_costs_nonnegative: bool
    any_cost_positive: bool
    nonpositive_when_charged: bool
    strictly_negative_once_charged: bool
    flow_cost_ratio: str | None
    metadata: dict[str, Any]
    created_at: str


class PriceShiftEvaluationCreate(BaseModel):
    transaction_id: str = Field(min_length=1)
    shift: Decimal
    authored_by: str = Field(default="participant", min_length=1)


class PriceShiftEvaluation(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    transaction_id: str
    shift: str
    original_fill: str
    shifted_fill: str
    original_cost: str
    shifted_cost: str
    original_flow: str
    shifted_flow: str
    flow_shift_invariant: bool
    cost_shift_invariant: bool
    local_price_layer_changed: bool
    created_at: str


class NumeraireEvaluationCreate(BaseModel):
    transaction_id: str = Field(min_length=1)
    scale: Decimal
    authored_by: str = Field(default="participant", min_length=1)

    @model_validator(mode="after")
    def positive_scale(self) -> "NumeraireEvaluationCreate":
        if self.scale <= 0:
            raise ValueError("numeraire scale must be positive")
        return self


class NumeraireEvaluation(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    transaction_id: str
    scale: str
    original_cost: str
    scaled_cost: str
    original_flow: str
    scaled_flow: str
    cost_scales: bool
    flow_scales: bool
    original_ratio: str | None
    scaled_ratio: str | None
    flow_cost_ratio_invariant: bool
    created_at: str


class CircuitEdgeCreate(BaseModel):
    edge_id: str = Field(min_length=1, max_length=240)
    local_price_move: Decimal
    charge: Decimal = Decimal("0")

    @model_validator(mode="after")
    def nonnegative_charge(self) -> "CircuitEdgeCreate":
        if self.charge < 0:
            raise ValueError("circuit charge must be non-negative")
        return self


class TradingCircuitEvaluationCreate(BaseModel):
    symbol: str = Field(min_length=1, max_length=80)
    edges: list[CircuitEdgeCreate] = Field(min_length=1)
    authored_by: str = Field(default="participant", min_length=1)
    tolerance: Decimal = Decimal("0")
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def nonnegative_tolerance(self) -> "TradingCircuitEvaluationCreate":
        if self.tolerance < 0:
            raise ValueError("tolerance must be non-negative")
        return self


class TradingCircuitEvaluation(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    symbol: str
    edges: list[dict[str, str]]
    circuit_length: int
    price_holonomy: str
    total_cost: str
    net_flow: str
    exact_price_field: bool
    global_token_exists: bool
    exact_round_trip_eq_neg_cost: bool
    per_edge_charge: str
    exact_round_trip_upper_bound: str
    bound_holds: bool
    profitable: bool
    profitable_iff_price_exceeds_cost: bool
    profit_needs_arbitrage: bool
    profit_needs_nonexact: bool
    metadata: dict[str, Any]
    created_at: str


class PnLEvaluationCreate(BaseModel):
    symbol: str = Field(min_length=1, max_length=80)
    position: Decimal
    start_mark: Decimal
    end_mark: Decimal
    accumulated_cost: Decimal = Decimal("0")
    authored_by: str = Field(default="participant", min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def nonnegative_cost(self) -> "PnLEvaluationCreate":
        if self.accumulated_cost < 0:
            raise ValueError("accumulated_cost must be non-negative")
        return self


class PnLEvaluation(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    symbol: str
    position: str
    start_mark: str
    end_mark: str
    price_move: str
    accumulated_cost: str
    pnl: str
    formula_holds: bool
    returning_market: bool
    returning_market_pnl: str | None
    returning_market_nonpositive: bool
    positive: bool
    pnl_pos_iff_price_move_beats_cost: bool
    metadata: dict[str, Any]
    created_at: str


class ExecutionSelectionCreate(BaseModel):
    signed_size: Decimal
    bid: Decimal
    ask: Decimal

    @model_validator(mode="after")
    def validate_quote(self) -> "ExecutionSelectionCreate":
        if self.signed_size == 0:
            raise ValueError("signed_size must be non-zero")
        if self.bid > self.ask:
            raise ValueError("bid must be less than or equal to ask")
        return self


class ExecutionSelection(BaseModel):
    side: TradeSide
    selected_fill: str
    admissible_fills: list[str]
    rigid: bool = True
    natural_form_unique: bool = True
    truth_issued: bool = False


class TradingFieldProjection(BaseModel):
    generated_at: str
    transactions: list[ClassicalTransaction]
    systems: list[TradingSystemEvaluation]
    shifts: list[PriceShiftEvaluation]
    numeraires: list[NumeraireEvaluation]
    circuits: list[TradingCircuitEvaluation]
    pnl: list[PnLEvaluation]
    stats: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
    canonical_runtime_operation: str = "integrate"
    adapter_label: str = "trading"
    simulation_only: bool = True
    direct_market_execution: bool = False
    brokerage_connected: bool = False
    automatic_order_submission: bool = False
    determination_issues_truth: bool = False
