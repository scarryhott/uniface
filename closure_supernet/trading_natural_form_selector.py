from __future__ import annotations

"""Natural-form interaction selector derived only from translational truth.

The selector never authors truth.  It reads one already-resolved NRRF870 trading
closure and exposes which interactions are naturally selectable next.

Selection is set-valued rather than heuristic:
* any currently returned profitable natural form is itself in the profit class;
* if profitable closure exists but execution evidence is OPEN, request only the
  missing execution return for that closure truth;
* otherwise expose every missing directed relation whose return would close an
  already witnessed directed path;
* if the known relation space is closure-saturated but still has no profitable
  truth, expose one generic relation-space-extension boundary.

No forecast, tolerance, score, fixed horizon, predeclared candidate graph or
route nomination may choose what is true.  A selected OPEN interaction can only
ask the environment for a source-preserving return; the next truth is whatever
that returned interaction actually closes to.
"""

import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

PROTOCOL = "closure.supernet/trading-natural-form-open-selector-v1"


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


def _closure_completing_boundaries(
    closure: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Missing one-edge returns that would close some witnessed directed path.

    No path is selected or scored.  The semantic test is only existential:
    missing u->v is on the OPEN frontier iff a witnessed path v=>u already
    exists, because its returned edge would create at least one closed itinerary.
    """

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
            body = {"source_token": source, "target_token": target}
            rows.append(
                {
                    "interaction_id": _digest("open-closure-relation", body),
                    "kind": "RETURN_CLOSURE_COMPLETING_RELATION",
                    "status": OPEN_STATUS,
                    "source_token": source,
                    "target_token": target,
                    "would_close_witnessed_directed_path": True,
                    "expected_value": None,
                    "predicted_profit": None,
                    "requires_source_preserving_return": True,
                    "requires_return": True,
                    "may_author_truth": False,
                    "semantic_authority": False,
                    "route_nomination": False,
                }
            )
    return rows


def _repair_boundaries(closure: Mapping[str, Any]) -> list[dict[str, Any]]:
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
        body = {
            "source_token": source,
            "target_token": target,
            "open_reason": row.get("parse_error") or "SOURCE_PRESERVATION_INCOMPLETE",
        }
        rows.append(
            {
                "interaction_id": _digest("open-return-repair", body),
                "kind": "RETURN_SOURCE_PRESERVED_RELATION",
                "status": OPEN_STATUS,
                "source_token": source,
                "target_token": target,
                "open_reason": body["open_reason"],
                "expected_value": None,
                "predicted_profit": None,
                "requires_source_preserving_return": True,
                "requires_return": True,
                "may_author_truth": False,
                "semantic_authority": False,
            }
        )
    return rows


def _profitable_truth_forms(closure: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in closure.get("natural_forms", []):
        form = dict(raw)
        if form.get("status") != WITNESSED_STATUS:
            continue
        if form.get("orientation") != "PROFITABLE":
            continue
        trade = dict(form.get("trade_projection") or {})
        execution_witnessed = trade.get("execution_return_status") == WITNESSED_STATUS
        admissible = trade.get("admissible") is True
        closure_id = str(form.get("closure_id") or "")
        body = {
            "closure_id": closure_id,
            "ball_id": form.get("ball_id"),
            "unitary_curvature": form.get("unitary_curvature"),
            "natural_profit": form.get("natural_profit"),
        }
        rows.append(
            {
                "interaction_id": _digest("profit-natural-form", body),
                "kind": (
                    "WITNESSED_PROFIT_NATURAL_FORM"
                    if admissible and execution_witnessed
                    else "RETURN_PROFIT_EXECUTION_EVIDENCE"
                ),
                "status": WITNESSED_STATUS if admissible and execution_witnessed else OPEN_STATUS,
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
                "timing": form.get("timing"),
                "execution_return_status": trade.get("execution_return_status"),
                "trade_admissible": admissible,
                "requires_return": not execution_witnessed,
                "requires_source_preserving_return": not execution_witnessed,
                "may_author_truth": False,
                "semantic_authority": False,
                "automatic_order_submission": False,
            }
        )
    return rows


def derive_natural_form_selection(
    *,
    natural_closure: Mapping[str, Any],
) -> dict[str, Any]:
    """Select the next interaction frontier from translational truth alone."""

    closure = dict(natural_closure)
    profitable = _profitable_truth_forms(closure)
    repairs = _repair_boundaries(closure)
    relation_frontier = _closure_completing_boundaries(closure)

    selected: list[dict[str, Any]]
    mode: str
    if profitable:
        selected = profitable
        mode = "PROFIT_NATURAL_FORM_CLASS"
    else:
        selected = [*repairs, *relation_frontier]
        mode = "OPEN_CLOSURE_FRONTIER"

    widening_boundary: dict[str, Any] | None = None
    if not profitable and not selected:
        relation_coordinates = list(closure.get("relation_coordinates", []))
        if relation_coordinates or closure.get("status") == WITNESSED_STATUS:
            widening_body = {
                "relation_coordinates": relation_coordinates,
                "natural_form_count": len(closure.get("natural_forms", [])),
            }
            widening_boundary = {
                "interaction_id": _digest("open-relation-space-extension", widening_body),
                "kind": "RETURN_NEW_SOURCE_PRESERVING_RELATION",
                "status": OPEN_STATUS,
                "source_token": None,
                "target_token": None,
                "open_reason": "KNOWN_RETURNED_RELATION_SPACE_HAS_NO_PROFITABLE_NATURAL_FORM",
                "expected_value": None,
                "predicted_profit": None,
                "requires_return": True,
                "requires_source_preserving_return": True,
                "may_author_truth": False,
                "semantic_authority": False,
                "predeclared_candidate_graph_required": False,
            }
            selected = [widening_boundary]
            mode = "OPEN_RELATION_SPACE_EXTENSION"

    selection_status = (
        WITNESSED_STATUS
        if selected and all(row.get("status") == WITNESSED_STATUS for row in selected)
        else OPEN_STATUS
    )

    return {
        "protocol": PROTOCOL,
        "equation": (
            "NaturalSelect(Q)=ProfitNaturalForms(Q) if returned profitable forms "
            "exist; otherwise OPENBoundary(Q)"
        ),
        "status": selection_status,
        "selection_mode": mode,
        "selected_interactions": selected,
        "selected_interaction_count": len(selected),
        "profitable_natural_forms": profitable,
        "profitable_natural_form_count": len(profitable),
        "open_return_repairs": repairs,
        "closure_completing_frontier": relation_frontier,
        "relation_space_extension_boundary": widening_boundary,
        "natural_form_selects_interaction": True,
        "selection_is_set_valued": True,
        "selection_authors_truth": False,
        "only_returned_interaction_recloses_truth": True,
        "open_boundary_is_interaction_frontier": True,
        "profit_selection_requires_returned_positive_amplitude": True,
        "profit_is_property_of_returned_truth_not_forecast": True,
        "external_strategy_selector_present": False,
        "predeclared_candidate_graph_present": False,
        "trend_model_present": False,
        "forecast_model_present": False,
        "similarity_tolerance_present": False,
        "automatic_order_submission": False,
        "continuation_status": OPEN_STATUS,
        "id": _digest(
            "trading-natural-form-selection",
            {
                "closure_id": closure.get("id"),
                "mode": mode,
                "selected": selected,
            },
        ),
    }


__all__ = ["PROTOCOL", "derive_natural_form_selection"]
