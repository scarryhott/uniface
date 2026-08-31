from __future__ import annotations

"""Unified pre-action natural-form field for trading closure.

Recognition and selection are not separate semantic stages. The returned
closure and every still-OPEN boundary are assembled into one natural-form field
before any action projection exists:

    Recognize(Q) = Select(Q) = NaturalFormField(Q)

Each returned form also carries its two relative action coordinates before an
action can become executable:

    Horizon(N) <- fidelity of the selected relative hair to later executable
                  translational truth;
    Size(N)    <- translated bottleneck capacity of the relative ball.

No externally fixed semantic horizon or externally authored position size is
introduced. If either coordinate is not returned/derivable, the action remains
OPEN. Returned closed forms and OPEN forms still coexist; no mode switch,
ranking, forecast, tolerance, or profit-first policy may suppress the field.
"""

import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

PROTOCOL = "closure.supernet/trading-unified-natural-form-field-v2-relative-horizon-size"


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


def _witnessed_edges(closure: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in closure.get("sensor_returns", []):
        row = dict(raw)
        if row.get("status") != WITNESSED_STATUS:
            continue
        source = row.get("source_token")
        target = row.get("target_token")
        if not source or not target:
            continue
        rows.append(row)
    return rows


def _adjacency(edges: Sequence[Mapping[str, Any]]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for edge in edges:
        source = str(edge["source_token"])
        target = str(edge["target_token"])
        result.setdefault(source, set()).add(target)
        result.setdefault(target, set())
    return result


def _reachable(adjacency: Mapping[str, set[str]], source: str, target: str) -> bool:
    if source == target:
        return True
    seen = {source}
    stack = [source]
    while stack:
        current = stack.pop()
        for neighbor in adjacency.get(current, set()):
            if neighbor == target:
                return True
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return False


def _action_projection(
    *,
    kind: str,
    form_id: str,
    status: str,
    source_token: str | None = None,
    target_token: str | None = None,
    closure_id: str | None = None,
    natural_profit: Any = None,
    amplitude: Any = None,
    requires_return: bool,
    relative_hair_horizon: Mapping[str, Any] | None = None,
    relative_ball_size: Mapping[str, Any] | None = None,
    preaction_ready: bool | None = None,
) -> dict[str, Any]:
    return {
        "projection_id": _digest(
            "natural-form-action-projection",
            {
                "form_id": form_id,
                "kind": kind,
                "source_token": source_token,
                "target_token": target_token,
                "closure_id": closure_id,
            },
        ),
        "kind": kind,
        "status": status,
        "form_id": form_id,
        "source_token": source_token,
        "target_token": target_token,
        "closure_id": closure_id,
        "natural_profit": natural_profit,
        "amplitude": amplitude,
        "relative_hair_horizon": dict(relative_hair_horizon or {}),
        "relative_ball_size": dict(relative_ball_size or {}),
        "preaction_ready": preaction_ready,
        "horizon_is_relative_hair_fidelity": True,
        "size_is_relative_ball": True,
        "fixed_horizon": None,
        "externally_authored_size": None,
        "requires_return": requires_return,
        "requires_source_preserving_return": requires_return,
        "expected_value": None,
        "predicted_profit": None,
        "may_author_truth": False,
        "semantic_authority": False,
        "automatic_order_submission": False,
    }


def _returned_forms(
    closure: Mapping[str, Any],
    preaction_coordinates: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in closure.get("natural_forms", []):
        form = dict(raw)
        closure_id = str(form.get("closure_id") or "")
        form_id = closure_id or _digest("returned-natural-form", form)
        coordinates = dict(preaction_coordinates.get(closure_id, {}))
        horizon = dict(coordinates.get("relative_hair_horizon") or {})
        ball_size = dict(coordinates.get("relative_ball_size") or {})
        trade = dict(form.get("trade_projection") or {})
        profitable = (
            form.get("status") == WITNESSED_STATUS
            and form.get("orientation") == "PROFITABLE"
        )
        execution_witnessed = trade.get("execution_return_status") == WITNESSED_STATUS
        horizon_witnessed = horizon.get("status") == WITNESSED_STATUS
        horizon_steps = horizon.get("horizon_return_steps")
        horizon_positive = bool(
            horizon_witnessed and horizon_steps is not None and int(horizon_steps) > 0
        )
        size_witnessed = ball_size.get("status") == WITNESSED_STATUS
        size_value = ball_size.get("relative_ball_size")
        size_positive = False
        if size_witnessed and size_value is not None:
            try:
                size_positive = float(size_value) > 0
            except (TypeError, ValueError):
                size_positive = False
        preaction_ready = bool(
            execution_witnessed
            and trade.get("admissible") is True
            and horizon_positive
            and size_positive
        )

        action: dict[str, Any] | None = None
        if profitable:
            if not execution_witnessed:
                action = _action_projection(
                    kind="RETURN_PROFIT_EXECUTION_EVIDENCE",
                    form_id=form_id,
                    status=OPEN_STATUS,
                    closure_id=closure_id or None,
                    natural_profit=form.get("natural_profit"),
                    amplitude=form.get("amplitude"),
                    requires_return=True,
                    relative_hair_horizon=horizon,
                    relative_ball_size=ball_size,
                    preaction_ready=False,
                )
            elif not horizon_witnessed:
                action = _action_projection(
                    kind="RETURN_RELATIVE_HAIR_FIDELITY",
                    form_id=form_id,
                    status=OPEN_STATUS,
                    closure_id=closure_id or None,
                    natural_profit=form.get("natural_profit"),
                    amplitude=form.get("amplitude"),
                    requires_return=True,
                    relative_hair_horizon=horizon,
                    relative_ball_size=ball_size,
                    preaction_ready=False,
                )
            elif not horizon_positive:
                action = _action_projection(
                    kind="ZERO_HAIR_FIDELITY_HORIZON_NO_ACTION",
                    form_id=form_id,
                    status=WITNESSED_STATUS,
                    closure_id=closure_id or None,
                    natural_profit=form.get("natural_profit"),
                    amplitude=form.get("amplitude"),
                    requires_return=False,
                    relative_hair_horizon=horizon,
                    relative_ball_size=ball_size,
                    preaction_ready=False,
                )
            elif not size_witnessed:
                action = _action_projection(
                    kind="RETURN_RELATIVE_BALL_SIZE",
                    form_id=form_id,
                    status=OPEN_STATUS,
                    closure_id=closure_id or None,
                    natural_profit=form.get("natural_profit"),
                    amplitude=form.get("amplitude"),
                    requires_return=True,
                    relative_hair_horizon=horizon,
                    relative_ball_size=ball_size,
                    preaction_ready=False,
                )
            elif not size_positive:
                action = _action_projection(
                    kind="ZERO_RELATIVE_BALL_SIZE_NO_ACTION",
                    form_id=form_id,
                    status=WITNESSED_STATUS,
                    closure_id=closure_id or None,
                    natural_profit=form.get("natural_profit"),
                    amplitude=form.get("amplitude"),
                    requires_return=False,
                    relative_hair_horizon=horizon,
                    relative_ball_size=ball_size,
                    preaction_ready=False,
                )
            else:
                action = _action_projection(
                    kind="PROJECT_RETURNED_PROFIT_NATURAL_FORM",
                    form_id=form_id,
                    status=WITNESSED_STATUS,
                    closure_id=closure_id or None,
                    natural_profit=form.get("natural_profit"),
                    amplitude=form.get("amplitude"),
                    requires_return=False,
                    relative_hair_horizon=horizon,
                    relative_ball_size=ball_size,
                    preaction_ready=preaction_ready,
                )

        rows.append(
            {
                "form_id": form_id,
                "kind": "RETURNED_CLOSED_NATURAL_FORM",
                "status": form.get("status"),
                "closure_id": closure_id or None,
                "closure_truth_id": form.get("closure_truth_id"),
                "ball_id": form.get("ball_id"),
                "return_ids": list(form.get("return_ids", [])),
                "directed_relation_signature": list(
                    form.get("directed_relation_signature", [])
                ),
                "unitary_curvature": form.get("unitary_curvature"),
                "natural_profit": form.get("natural_profit"),
                "amplitude": form.get("amplitude"),
                "orientation": form.get("orientation"),
                "relative_hair_horizon": horizon,
                "relative_ball_size": ball_size,
                "horizon_from_relative_hair_fidelity": True,
                "size_from_relative_ball": True,
                "preaction_ready": preaction_ready,
                "returned_truth_member": True,
                "open_boundary_member": False,
                "recognized": True,
                "selected": True,
                "recognition_selection_same_form": True,
                "action_projection": action,
                "may_author_truth": False,
            }
        )
    return rows


def _repair_forms(closure: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for raw in closure.get("sensor_returns", []):
        row = dict(raw)
        if row.get("status") != OPEN_STATUS:
            continue
        source = str(row.get("source_token") or "")
        target = str(row.get("target_token") or "")
        if not source or not target or source == target:
            continue
        key = (source, target)
        if key in seen:
            continue
        seen.add(key)
        form_id = _digest(
            "open-source-return-natural-form",
            {
                "source_token": source,
                "target_token": target,
                "reason": row.get("parse_error") or "SOURCE_PRESERVATION_INCOMPLETE",
            },
        )
        rows.append(
            {
                "form_id": form_id,
                "kind": "OPEN_SOURCE_RETURN_NATURAL_FORM",
                "status": OPEN_STATUS,
                "source_token": source,
                "target_token": target,
                "returned_truth_member": False,
                "open_boundary_member": True,
                "recognized": True,
                "selected": True,
                "recognition_selection_same_form": True,
                "action_projection": _action_projection(
                    kind="RETURN_SOURCE_PRESERVED_RELATION",
                    form_id=form_id,
                    status=OPEN_STATUS,
                    source_token=source,
                    target_token=target,
                    requires_return=True,
                ),
                "may_author_truth": False,
            }
        )
    return rows


def _closure_boundary_forms(closure: Mapping[str, Any]) -> list[dict[str, Any]]:
    edges = _witnessed_edges(closure)
    adjacency = _adjacency(edges)
    nodes = sorted(adjacency)
    witnessed_pairs = {
        (str(edge["source_token"]), str(edge["target_token"]))
        for edge in edges
    }
    rows: list[dict[str, Any]] = []
    for source in nodes:
        for target in nodes:
            if source == target or (source, target) in witnessed_pairs:
                continue
            if not _reachable(adjacency, target, source):
                continue
            form_id = _digest(
                "open-closure-completing-natural-form",
                {"source_token": source, "target_token": target},
            )
            rows.append(
                {
                    "form_id": form_id,
                    "kind": "OPEN_CLOSURE_COMPLETING_NATURAL_FORM",
                    "status": OPEN_STATUS,
                    "source_token": source,
                    "target_token": target,
                    "would_close_witnessed_directed_path": True,
                    "returned_truth_member": False,
                    "open_boundary_member": True,
                    "recognized": True,
                    "selected": True,
                    "recognition_selection_same_form": True,
                    "action_projection": _action_projection(
                        kind="RETURN_CLOSURE_COMPLETING_RELATION",
                        form_id=form_id,
                        status=OPEN_STATUS,
                        source_token=source,
                        target_token=target,
                        requires_return=True,
                    ),
                    "may_author_truth": False,
                }
            )
    return rows


def _relation_space_extension_form(closure: Mapping[str, Any]) -> dict[str, Any]:
    relation_coordinates = list(closure.get("relation_coordinates", []))
    form_id = _digest(
        "open-relation-space-extension-natural-form",
        {
            "relation_coordinates": relation_coordinates,
            "natural_form_count": len(closure.get("natural_forms", [])),
        },
    )
    return {
        "form_id": form_id,
        "kind": "OPEN_RELATION_SPACE_EXTENSION_NATURAL_FORM",
        "status": OPEN_STATUS,
        "source_token": None,
        "target_token": None,
        "open_reason": "EXISTENCE_AND_RELATION_SPACE_REMAIN_OPEN",
        "returned_truth_member": False,
        "open_boundary_member": True,
        "recognized": True,
        "selected": True,
        "recognition_selection_same_form": True,
        "predeclared_candidate_graph_required": False,
        "action_projection": _action_projection(
            kind="RETURN_NEW_SOURCE_PRESERVING_RELATION",
            form_id=form_id,
            status=OPEN_STATUS,
            requires_return=True,
        ),
        "may_author_truth": False,
    }


def derive_unified_natural_form_field(
    *,
    natural_closure: Mapping[str, Any],
    preaction_coordinates: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Derive recognition, selection, horizon, and size before action."""

    closure = dict(natural_closure)
    coordinates = dict(preaction_coordinates or {})
    returned = _returned_forms(closure, coordinates)
    repairs = _repair_forms(closure)
    closure_boundaries = _closure_boundary_forms(closure)

    extension = _relation_space_extension_form(closure)
    forms = [*returned, *repairs, *closure_boundaries, extension]
    action_projections = [
        dict(form["action_projection"])
        for form in forms
        if form.get("action_projection") is not None
    ]
    profitable_returned = [
        form
        for form in returned
        if form.get("orientation") == "PROFITABLE"
        and form.get("status") == WITNESSED_STATUS
    ]

    return {
        "protocol": PROTOCOL,
        "equation": (
            "Recognize(Q)=Select(Q)=NaturalFormField(Q); "
            "H(N)=HairFidelity(N); Size(N)=RelativeBall(N); "
            "Action is only a later projection"
        ),
        "status": (
            WITNESSED_STATUS
            if returned and all(form.get("status") == WITNESSED_STATUS for form in returned)
            else OPEN_STATUS
        ),
        "natural_form_field": forms,
        "natural_form_count": len(forms),
        "returned_natural_forms": returned,
        "returned_natural_form_count": len(returned),
        "open_natural_forms": [form for form in forms if form.get("open_boundary_member")],
        "open_natural_form_count": sum(
            1 for form in forms if form.get("open_boundary_member")
        ),
        "profitable_returned_natural_forms": profitable_returned,
        "profitable_returned_natural_form_count": len(profitable_returned),
        "action_projections": action_projections,
        "action_projection_count": len(action_projections),
        "recognition_equals_selection": True,
        "recognition_precedes_selection": False,
        "selection_precedes_recognition": False,
        "separate_selector_present": False,
        "selector_mode_present": False,
        "selection_is_not_filtering": True,
        "all_open_forms_coexist": True,
        "local_open_cannot_block_relation_space_extension": True,
        "relation_space_extension_is_simultaneous_open_form": True,
        "profit_is_natural_form_property_not_selection_rule": True,
        "horizon_from_relative_hair_fidelity": True,
        "relative_ball_is_size": True,
        "fixed_horizon_present": False,
        "external_position_size_present": False,
        "action_occurs_after_unified_natural_form_field": True,
        "horizon_and_size_derived_before_action": True,
        "action_projection_authors_truth": False,
        "only_returned_interaction_recloses_truth": True,
        "forecast_model_present": False,
        "trend_model_present": False,
        "similarity_tolerance_present": False,
        "predeclared_candidate_graph_present": False,
        "automatic_order_submission": False,
        "continuation_status": OPEN_STATUS,
        "id": _digest(
            "trading-unified-natural-form-field",
            {
                "closure_id": closure.get("id"),
                "forms": forms,
            },
        ),
    }


__all__ = ["PROTOCOL", "derive_unified_natural_form_field"]
