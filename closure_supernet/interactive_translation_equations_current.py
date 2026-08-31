from __future__ import annotations

"""Current closure-equation runtime using translational truth alone.

Trading truth is the NRRF870 open-sensor feedback hair equation. Returned
interaction is read through complete closed-itinerary geometry, normalized to
its unique closure, and quotiented by translational truth. There is no second
trajectory, trend, tolerance, forecast, or inter-class dynamics law.

The natural-form selector is also a pure reading of translational truth. It may
select what interaction to OPEN next, but it cannot select what the return will
mean. Profitable returned natural forms select themselves; otherwise OPEN exposes
the minimal return-generated closure frontier, or a generic relation-space
extension when the known returned space is saturated.
"""

import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import (
    OPEN_STATUS,
    WITNESSED_STATUS,
    audit_translational_continuity,
)
from .interactive_translation_equations import (
    resolve_legacy_equation,
    resolve_reopening_equation,
    resolve_resource_equation,
    resolve_rule_chart_equation,
    resolve_trading_equation as resolve_legacy_trading_equation,
)
from .trading_natural_form_closure import (
    PROTOCOL as TRADING_PROTOCOL,
    resolve_open_sensor_trading_closure,
)
from .trading_natural_form_selector import derive_natural_form_selection
from .trading_translational_truth_partition import (
    derive_translational_truth_partition,
)

PROTOCOL = "closure.supernet/interactive-translation-equations-trading-natural-form-selector-v7"


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def _sensor_feedback(
    *,
    sensor_feedback: Sequence[Mapping[str, Any]],
    returned_equations: Sequence[Mapping[str, Any]],
    hair_equations: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    supplied = [
        values
        for values in (sensor_feedback, returned_equations, hair_equations)
        if values
    ]
    if len(supplied) > 1:
        raise ValueError(
            "Supply exactly one of sensor_feedback, returned_equations, or hair_equations"
        )
    return list(supplied[0]) if supplied else []


def resolve_trading_equation(
    *,
    observer_id: str | None = None,
    sensor_feedback: Sequence[Mapping[str, Any]] = (),
    returned_equations: Sequence[Mapping[str, Any]] = (),
    hair_equations: Sequence[Mapping[str, Any]] = (),
    sensor_history: Sequence[Sequence[Mapping[str, Any]]] = (),
    max_returns: int | None = None,
    proposals: Sequence[Mapping[str, Any]] = (),
    receipts: Sequence[Mapping[str, Any]] = (),
    minimum_receipts: int = 1,
    max_forms: int | None = None,
) -> dict[str, Any]:
    """Resolve truth, then derive its natural-form interaction frontier."""

    feedback = _sensor_feedback(
        sensor_feedback=sensor_feedback,
        returned_equations=returned_equations,
        hair_equations=hair_equations,
    )
    if sensor_history and feedback:
        raise ValueError(
            "Supply sensor_history or one current sensor feedback surface, not both"
        )

    history = [[dict(row) for row in frame] for frame in sensor_history]
    current_feedback: list[Mapping[str, Any]] = (
        list(history[-1]) if history else list(feedback)
    )
    natural = resolve_open_sensor_trading_closure(
        observer_id=observer_id,
        sensor_feedback=current_feedback,
        max_returns=max_returns,
    )
    truth_partition = (
        derive_translational_truth_partition(
            observer_id=observer_id,
            sensor_history=history,
            max_returns_per_frame=max_returns,
        )
        if history
        else None
    )
    natural_selection = derive_natural_form_selection(natural_closure=natural)

    current_profit_truth_witnessed = any(
        form.get("orientation") == "PROFITABLE"
        for form in natural.get("natural_forms", [])
    )
    learned_profit = (
        truth_partition.get("learned_profit") is True
        if truth_partition is not None
        else current_profit_truth_witnessed
    )

    body = dict(natural)
    body["protocol"] = PROTOCOL
    body["natural_trading_protocol"] = TRADING_PROTOCOL
    # Historical continuation remains compatibility-only. Current dynamics are
    # returned interaction -> truth -> natural-form OPEN selection -> return.
    body["closure_continuation"] = None
    body["translational_truth_partition"] = truth_partition
    body["translational_truth_learning"] = truth_partition
    body["natural_form_selection"] = natural_selection
    body["selected_interactions"] = list(
        natural_selection.get("selected_interactions", [])
    )
    body["current_profit_truth_witnessed"] = current_profit_truth_witnessed
    body["learned_profit"] = learned_profit

    if proposals or receipts:
        legacy = resolve_legacy_trading_equation(
            proposals=proposals,
            receipts=receipts,
            minimum_receipts=minimum_receipts,
            max_forms=max_forms,
        )
        compatibility = {
            **legacy,
            "semantic_authority": False,
            "may_gate_interaction": False,
            "may_widen_truth": False,
            "may_feed_back_into_closure": False,
            "compatibility_status": legacy.get("status"),
        }
        body["legacy_route_receipt_projection"] = compatibility
        body["forms"] = [
            {
                **dict(row),
                "semantic_authority": False,
                "gate_open_authors_truth": False,
            }
            for row in legacy.get("forms", [])
        ]
        body["proposals"] = list(legacy.get("proposals", []))
        body["unmatched_or_open_receipts"] = list(
            legacy.get("unmatched_or_open_receipts", [])
        )
    else:
        body["legacy_route_receipt_projection"] = None
        body["forms"] = []
        body["proposals"] = []
        body["unmatched_or_open_receipts"] = []

    body.update(
        {
            "status": natural["status"],
            "translational_truth_alone": True,
            "route_receipt_authors_truth": False,
            "completed_route_is_not_natural_form_primitive": True,
            "ask_to_immediately_succeeding_bid_is_definition": False,
            "only_open_sensor_return_recloses_trading": True,
            "open_sensor_all_closed_itineraries": True,
            "bfs_route_authors_truth": False,
            "undirected_connectivity_authors_ball": False,
            "directed_translation_fibres": True,
            "amplitude_is_negative_curvature_part": True,
            "ball_partition_max_gives_timing": True,
            "clock_duration_authors_timing": False,
            "normalized_closure_timing_equals_amplitude": True,
            "signal_trade_equal_relative_to_translation": True,
            "translational_truth_authors_relation_partition": True,
            "ball_equals_natural_form_truth_class": True,
            "hair_is_intra_truth_class_presentation": True,
            "predeclared_market_graph_authors_truth_partition": False,
            "relation_space_refines_from_returned_interaction": True,
            "distinct_natural_forms_are_not_declared_translations": True,
            "separate_dynamics_law_present": False,
            "inter_class_transition_model_present": False,
            "curvature_continuation_is_authoritative": False,
            "trend_model_present": False,
            "forecast_model_present": False,
            "similarity_tolerance_present": False,
            "profit_trajectory_present": False,
            "history_length_authors_truth": False,
            "profit_trajectory_authors_trade": False,
            "profit_learning_is_discovery_not_prediction": True,
            "positive_profit_requires_current_returned_truth": True,
            "positive_crossing_requires_current_execution_return": True,
            "natural_form_selects_interaction": True,
            "selection_is_set_valued": True,
            "selection_authors_truth": False,
            "open_boundary_is_interaction_frontier": True,
            "profit_selection_requires_returned_positive_amplitude": True,
            "external_strategy_selector_present": False,
            "predeclared_candidate_graph_present": False,
            "configuration_authors_truth": False,
            "computation_bounds_author_truth": False,
            "existence_closed": False,
            "dialectic_continuation_status": OPEN_STATUS,
        }
    )
    body["id"] = _digest("natural-trading-equation-natural-form-selector", body)
    return body


def resolve_closure_equations(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Resolve supplied subsystems through one returned translational truth law."""

    result: dict[str, Any] = {
        "protocol": PROTOCOL,
        "equation": (
            "Q_(t+1)=Close(Q_t + Translate(observer_t, returned_interaction_t)); "
            "NaturalSelect(Q_t)=ProfitNaturalForms(Q_t) or OPENBoundary(Q_t)"
        ),
        "translational_truth_alone": True,
        "natural_form_selects_interaction": True,
        "selection_authors_truth": False,
        "proposal_status": OPEN_STATUS,
        "only_returned_interaction_recloses": True,
        "separate_dynamics_law_present": False,
        "configuration_authors_truth": False,
        "computation_bounds_author_truth": False,
        "existence_closed": False,
        "dialectic_continuation_status": OPEN_STATUS,
    }

    if payload.get("reopening") is not None:
        result["reopening"] = resolve_reopening_equation(
            **dict(payload["reopening"])
        )
    if payload.get("rule_charts") is not None:
        result["rule_charts"] = resolve_rule_chart_equation(
            **dict(payload["rule_charts"])
        )
    if payload.get("trading") is not None:
        result["trading"] = resolve_trading_equation(**dict(payload["trading"]))
    if payload.get("resources") is not None:
        result["resources"] = resolve_resource_equation(
            **dict(payload["resources"])
        )
    if payload.get("legacy") is not None:
        result["legacy"] = resolve_legacy_equation(**dict(payload["legacy"]))

    subsystem_rows = [
        value
        for key, value in result.items()
        if key in {"reopening", "rule_charts", "trading", "resources", "legacy"}
    ]
    result["status"] = (
        WITNESSED_STATUS
        if subsystem_rows
        and all(row.get("status") == WITNESSED_STATUS for row in subsystem_rows)
        else OPEN_STATUS
    )
    audit_target = dict(result)
    audit_target.pop("continuity_audit", None)
    result["continuity_audit"] = audit_translational_continuity(audit_target)
    result["id"] = _digest("closure-equations-natural-form-selector", result)
    return result


__all__ = [
    "PROTOCOL",
    "resolve_closure_equations",
    "resolve_legacy_equation",
    "resolve_reopening_equation",
    "resolve_resource_equation",
    "resolve_rule_chart_equation",
    "resolve_trading_equation",
]
