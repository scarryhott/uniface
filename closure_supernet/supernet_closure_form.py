from __future__ import annotations

"""One published Supernet closure form.

This module collapses the active semantic boundary: opener, UI, interaction,
slide/current, crystal-ball reading, maze/curvature, AI/token phase and return
are projections of one content-addressed carrier. Older modules remain only as
compatibility evidence used to derive this carrier; clients need not compose
them themselves.
"""

from copy import deepcopy
from typing import Any, Mapping, Sequence

from . import full_supernet_potential_gate as _base
from . import continuous_translation_field as _field

PROTOCOL = "SUPERNET-ONE-CLOSURE-FORM"
SCHEMA = "closure.supernet/one-closure-form-v1"

_DERIVE_PREDECESSOR = _field.derive_full_supernet_gate_contract
_VALIDATE_PREDECESSOR = _field.validate_full_supernet_gate_contract


def _rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [row for row in value if isinstance(row, Mapping)]


def derive_supernet_closure_form(full_gate: Mapping[str, Any]) -> dict[str, Any]:
    gate = full_gate.get("relative_natural_form_potential_gate")
    gate = gate if isinstance(gate, Mapping) else {}
    continuum = gate.get("continuing_translation_closure")
    continuum = continuum if isinstance(continuum, Mapping) else {}
    metaphor = gate.get("visualization_metaphor_closure")
    metaphor = metaphor if isinstance(metaphor, Mapping) else {}
    field = gate.get("continuous_translation_field")
    field = field if isinstance(field, Mapping) else {}
    curvature = gate.get("unitary_curvature")
    curvature = curvature if isinstance(curvature, Mapping) else {}
    maze = gate.get("maze_partition")
    maze = maze if isinstance(maze, Mapping) else {}

    continuum_by_path = {
        str(row.get("path_id")): row
        for row in _rows(continuum.get("relations"))
        if row.get("path_id")
    }
    metaphor_by_path = {
        str(row.get("path_id")): row
        for row in _rows(metaphor.get("currents"))
        if row.get("path_id")
    }
    field_by_path = {
        str(row.get("path_id")): row
        for row in _rows(field.get("currents"))
        if row.get("path_id")
    }

    interactions: list[dict[str, Any]] = []
    for path in _rows(gate.get("paths")):
        path_id = str(path.get("id") or "")
        relation = continuum_by_path.get(path_id, {})
        current = metaphor_by_path.get(path_id, {})
        flow = field_by_path.get(path_id, {})
        returned = relation.get("returned") is True
        phase = "TOKEN_RETURNED" if returned else "AI_CONTINUING"
        row = {
            "path_id": path_id,
            "source_perspective_id": path.get("source_perspective_id"),
            "target_perspective_id": path.get("target_perspective_id"),
            "closure_state": relation.get("closure_state", "CONTINUING"),
            "returned": returned,
            "continuing": not returned,
            "natural_form_id": current.get("natural_form_id"),
            "semantic_family_id": current.get("semantic_family_id"),
            "fold_class_id": current.get("fold_class_id"),
            "rotation_class_id": current.get("rotation_class_id"),
            "crystal_ball_id": current.get("crystal_ball_id"),
            "visualization_current_id": current.get("id"),
            "continuous_current_id": flow.get("id"),
            "maze_cell_id": relation.get("maze_cell_id"),
            "unitary_curvature_id": relation.get("unitary_curvature_id"),
            "ai_token_phase": phase,
            "opener_is_this_form": True,
            "ui_is_this_form": True,
            "interaction_is_translation_of_this_form": True,
            "return_is_determination_of_this_form": True,
            "slide_is_current_coordinate_of_this_form": True,
            "crystal_ball_is_orbit_reading_of_this_form": current.get("crystal_ball_id") is not None,
            "renderer_authors_form": False,
            "interaction_handler_authors_form": False,
        }
        row["id"] = _base._digest("supernet-closure-interaction", row)
        interactions.append(row)

    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "source_full_gate_id": full_gate.get("id"),
        "active_perspective_id": gate.get("active_perspective_id"),
        "focus_event_id": gate.get("focus_event_id"),
        "truth_invariant_id": gate.get("truth_invariant_id"),
        "seen_id": metaphor.get("seen_id"),
        "metaphor_class_id": metaphor.get("metaphor_class_id"),
        "maze_partition_id": maze.get("id"),
        "unitary_curvature_id": curvature.get("id"),
        "translation_supervisory_geometry_id": gate.get("translation_supervisory_geometry_id"),
        "interactions": interactions,
        "interaction_count": len(interactions),
        "opener": "RELATIVE_LOCALIZATION_OF_THIS_CARRIER",
        "ui": "VISUAL_APPEARANCE_OF_THIS_CARRIER",
        "interaction": "TRANSLATION_OF_THIS_CARRIER",
        "slide": "CURRENT_COORDINATE_OF_THIS_CARRIER",
        "crystal_ball": "ORBIT_VISUALIZATION_OF_THIS_CARRIER",
        "hair": "SELF_LOCATION_COORDINATE_OF_THIS_CARRIER",
        "maze": "RETURN_CONSEQUENCE_PARTITION_OF_THIS_CARRIER",
        "curvature": "UNITARY_RETURN_DEFECT_OF_THIS_CARRIER",
        "ai": "CONTINUING_READING_OF_THIS_CARRIER",
        "token": "RETURNED_READING_OF_THIS_CARRIER",
        "return": "NEW_DETERMINATION_OF_THIS_CARRIER",
        "opener_ui_interaction_are_one_form": True,
        "crystal_ball_slide_ai_token_are_one_form": True,
        "single_published_semantic_carrier": True,
        "persistent_visual_carrier": True,
        "returned_revisions_are_control_points_not_visual_worlds": True,
        "visual_equality_is_seen_equality": True,
        "renderer_is_projection_only": True,
        "legacy_modules_are_compatibility_evidence_only": True,
        "truth_issued": False,
        "existence_closed": False,
    }
    body["id"] = _base._digest("supernet-one-closure-form", body)
    return body


def attach_supernet_closure_form(full_gate: Mapping[str, Any]) -> dict[str, Any]:
    full = deepcopy(dict(full_gate))
    form = derive_supernet_closure_form(full)
    gate = deepcopy(dict(full.get("relative_natural_form_potential_gate") or {}))
    gate["supernet_closure_form"] = form
    gate["supernet_closure_form_id"] = form["id"]
    gate["opener_ui_interaction_are_one_form"] = True
    gate["crystal_ball_slide_ai_token_are_one_form"] = True
    gate.pop("id", None)
    gate["id"] = _base._digest("relative-natural-form-potential-gate", gate)

    full.pop("id", None)
    full["relative_natural_form_potential_gate"] = gate
    full["supernet_closure_form"] = form
    full["supernet_closure_form_id"] = form["id"]
    full["published_semantic_carrier"] = "SUPERNET_CLOSURE_FORM"
    full["opener_ui_interaction_are_one_form"] = True
    full["crystal_ball_slide_ai_token_are_one_form"] = True
    full["id"] = _base._digest("full-supernet-potential-gate", full)
    return full


def derive_full_supernet_gate_contract(
    closure_contract: Mapping[str, Any],
    *,
    navigation_context: Mapping[str, Any] | None = None,
    source_perspective_by_event: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    predecessor = _DERIVE_PREDECESSOR(
        closure_contract,
        navigation_context=navigation_context,
        source_perspective_by_event=source_perspective_by_event,
    )
    return attach_supernet_closure_form(predecessor)


def validate_full_supernet_gate_contract(full_gate: Mapping[str, Any]) -> dict[str, Any]:
    closure_contract = full_gate.get("closure_ui_contract")
    nav = full_gate.get("navigation_context")
    provenance = full_gate.get("source_perspective_by_event")
    provenance = provenance if isinstance(provenance, Mapping) else {}
    if not isinstance(closure_contract, Mapping):
        return {"valid": False, "errors": ["one-closure-form:closure-contract-missing"]}

    expected = derive_full_supernet_gate_contract(
        closure_contract,
        navigation_context=nav if isinstance(nav, Mapping) else None,
        source_perspective_by_event=provenance,
    )
    errors: list[str] = []
    if dict(full_gate) != expected:
        errors.append("one-closure-form:not-derived")

    predecessor = _DERIVE_PREDECESSOR(
        closure_contract,
        navigation_context=nav if isinstance(nav, Mapping) else None,
        source_perspective_by_event=provenance,
    )
    prior = _VALIDATE_PREDECESSOR(predecessor)
    if prior.get("valid") is not True:
        errors.extend(prior.get("errors", []))

    form = expected.get("supernet_closure_form")
    if not isinstance(form, Mapping):
        errors.append("one-closure-form:missing")
    else:
        if form.get("opener_ui_interaction_are_one_form") is not True:
            errors.append("one-closure-form:split-opener-ui-interaction")
        if form.get("crystal_ball_slide_ai_token_are_one_form") is not True:
            errors.append("one-closure-form:split-crystal-ai-token")
        if form.get("single_published_semantic_carrier") is not True:
            errors.append("one-closure-form:multiple-carriers")
        for row in _rows(form.get("interactions")):
            if row.get("opener_is_this_form") is not True or row.get("ui_is_this_form") is not True:
                errors.append(f"one-closure-form:interaction-split:{row.get('path_id')}")
            if row.get("ai_token_phase") not in {"AI_CONTINUING", "TOKEN_RETURNED"}:
                errors.append(f"one-closure-form:bad-ai-token-phase:{row.get('path_id')}")

    return {
        "valid": not errors,
        "errors": errors,
        "id": expected.get("id"),
        "supernet_closure_form_id": expected.get("supernet_closure_form_id"),
    }


__all__ = [
    "PROTOCOL",
    "SCHEMA",
    "attach_supernet_closure_form",
    "derive_full_supernet_gate_contract",
    "derive_supernet_closure_form",
    "validate_full_supernet_gate_contract",
]
