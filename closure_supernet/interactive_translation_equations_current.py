from __future__ import annotations

"""Current closure-equation runtime with NRRF870 natural trading closure.

Trading truth is the open-sensor feedback hair equation: returned interaction is
read through the complete finite closed-itinerary geometry, normalized to its
unique closure, then read as unitary curvature. Available amplitude is the
negative curvature part; semantic timing is the normalized ball-partition max
and therefore equals amplitude. Signal and trade are equal relative readings of
the same completed-route translation.

Historical route proposals, successor-quote rules, graph traversal order, clock
duration, and continuation trends remain non-authoritative projections.
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
from .trading_closure_continuation import resolve_trading_closure_continuation
from .trading_natural_form_closure import (
    PROTOCOL as TRADING_PROTOCOL,
    resolve_open_sensor_trading_closure,
)

PROTOCOL = "closure.supernet/interactive-translation-equations-natural-trading-v4-nrrf870"


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
    """Resolve trading only from returned open-sensor translation closure."""

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
    continuation = (
        resolve_trading_closure_continuation(
            observer_id=observer_id,
            sensor_history=history,
            max_returns_per_frame=max_returns,
        )
        if history
        else None
    )

    body = dict(natural)
    body["protocol"] = PROTOCOL
    body["natural_trading_protocol"] = TRADING_PROTOCOL
    body["closure_continuation"] = continuation

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
            "curvature_continuation_is_relative_projection": True,
            "history_length_authors_truth": False,
            "profit_trajectory_authors_trade": False,
            "positive_crossing_requires_current_execution_return": True,
            "configuration_authors_truth": False,
            "computation_bounds_author_truth": False,
            "existence_closed": False,
            "dialectic_continuation_status": OPEN_STATUS,
        }
    )
    body["id"] = _digest("natural-trading-equation-nrrf870", body)
    return body


def resolve_closure_equations(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Resolve supplied subsystems through one returned-translation law."""

    result: dict[str, Any] = {
        "protocol": PROTOCOL,
        "equation": (
            "Q_(t+1)=Close(Q_t + Translate(observer_t, returned_interaction_t))"
        ),
        "proposal_status": OPEN_STATUS,
        "only_returned_interaction_recloses": True,
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
    result["id"] = _digest("closure-equations-natural-trading-nrrf870", result)
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
