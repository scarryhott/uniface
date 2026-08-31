from __future__ import annotations

"""Unified pre-action natural-form field for trading closure.

Recognition and selection are not separate semantic stages.  The returned
closure and every still-OPEN boundary are assembled into one natural-form field
before any action projection exists:

    Recognize(Q) = Select(Q) = NaturalFormField(Q)

Returned closed forms and OPEN forms are therefore relative members of the same
pre-action closure object.  No mode switch, ranking, forecast, tolerance, or
profit-first policy may suppress one member of the field.  In particular a
persistent local OPEN boundary cannot block relation-space extension.

Action is a later projection of this already-unified field.  Action projections
never author truth; only a source-preserving returned interaction may reclose the
field and change translational truth.
"""

import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

PROTOCOL = "closure.supernet/trading-unified-natural-form-field-v1"


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
        "requires_return": requires_return,
        "requires_source_preserving_return": requires_return,
        "expected_value": None,
        "predicted_profit": None,
        "may_author_truth": False,
        "semantic_authority": False,
        "automatic_order_submission": False,
    }


def _returned_forms(closure: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in closure.get("natural_forms", []):
        form = dict(raw)
        closure_id = str(form.get("closure_id") or "")
        form_id = closure_id or _digest("returned-natural-form", form)
        trade = dict(form.get("trade_projection") or {})
        profitable = (
            form.get("status") == WITNESSED_STATUS
            and form.get("orientation") == "PROFITABLE"
        )
        execution_witnessed = trade.get("execution_return_status") == WITNESSED_STATUS
        action: dict[str, Any] | None = None
        if profitable:
            if execution_witnessed and trade.get("admissible") is True:
                action = _action_projection(
                    kind="PROJECT_RETURNED_PROFIT_NATURAL_FORM",
                    form_id=form_id,
                    status=WITNESSED_STATUS,
                    closure_id=closure_id or None,
                    natural_profit=form.get("natural_profit"),
                    amplitude=form.get("amplitude"),
                    requires_return=False,
                )
            else:
                action = _action_projection(
                    kind="RETURN_PROFIT_EXECUTION_EVIDENCE",
                    form_id=form_id,
                    status=OPEN_STATUS,
                    closure_id=closure_id or None,
                    natural_profit=form.get("natural_profit"),
                    amplitude=form.get("amplitude"),
                    requires_return=True,
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
) -> dict[str, Any]:
    """Derive recognition and selection as one pre-action natural-form field."""

    closure = dict(natural_closure)
    returned = _returned_forms(closure)
    repairs = _repair_forms(closure)
    closure_boundaries = _closure_boundary_forms(closure)

    # The global OPEN relation form is simultaneous with local OPEN forms.  It is
    # not a fallback branch.  This prevents persistent local OPEN relations from
    # starving support widening and removes the selector-mode architecture.
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
            "Recognize(Q)=Select(Q)=NaturalFormField(Q)="
            "ReturnedNaturalForms(Q) union OPENNaturalForms(Q); "
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
        "action_occurs_after_unified_natural_form_field": True,
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
