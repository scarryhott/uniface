from __future__ import annotations

"""Canonical Supernet closure as one continuing family of translational truth.

The legacy runtime distinguishes ``WITNESSED`` from ``OPEN`` internally because
older contracts and proofs use that vocabulary. This module does not alter that
compatibility boundary. Instead it derives the published semantic object:

    Closure = all current translation relations
    Returned(relation) = the relation has a returned determination
    Continuing(relation) = the relation continues in the same closure

Nothing is outside closure. A non-returned relation is not an ontological gap;
it is a continuation of the same closure family. Return changes determination,
not membership in closure.
"""

from copy import deepcopy
from typing import Any, Mapping, Sequence

from .closure_continuity import WITNESSED_STATUS
from . import full_supernet_potential_gate as _base

PROTOCOL = "SUPERNET-CONTINUING-TRANSLATION-CLOSURE"
SCHEMA = "closure.supernet/continuing-translation-closure-v1"
RETURNED = "RETURNED"
CONTINUING = "CONTINUING"


def _rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _state_of(path: Mapping[str, Any]) -> str:
    return RETURNED if path.get("status") == WITNESSED_STATUS else CONTINUING


def _semantic_kind(path: Mapping[str, Any]) -> str:
    raw = str(path.get("kind") or "TRANSLATION")
    if "PERSPECTIVE" in raw:
        return "PERSPECTIVE_TRANSLATION"
    if "LOCAL" in raw:
        return "LOCALITY_TRANSLATION"
    if "RETURN" in raw:
        return "RETURN_CONTINUATION"
    if "POTENTIAL" in raw:
        return "TRANSLATION_CONTINUATION"
    return "TRANSLATION"


def _semantic_action(path: Mapping[str, Any]) -> str:
    raw = str(path.get("action") or "CONTINUE")
    if raw == "PERSPECTIVE_TRANSPORT":
        return "PERSPECTIVE_TRANSPORT"
    if raw == "LOCALITY_TRANSPORT":
        return "LOCALITY_TRANSPORT"
    return "CONTINUE_TO_RETURN"


def _relation(path: Mapping[str, Any]) -> dict[str, Any]:
    returned = _state_of(path) == RETURNED
    body = {
        "path_id": str(path.get("id") or ""),
        "source_perspective_id": str(path.get("source_perspective_id") or ""),
        "target_perspective_id": (
            None
            if path.get("target_perspective_id") is None
            else str(path.get("target_perspective_id"))
        ),
        "source_state_id": (
            None
            if path.get("source_state_id") is None
            else str(path.get("source_state_id"))
        ),
        "target_state_id": (
            None
            if path.get("target_state_id") is None
            else str(path.get("target_state_id"))
        ),
        "kind": _semantic_kind(path),
        "action": _semantic_action(path),
        "closure_state": RETURNED if returned else CONTINUING,
        "returned": returned,
        "continuing": not returned,
        "source_preserved": path.get("source_preserved") is True,
        "source_return_ids": sorted(
            {
                str(item)
                for item in path.get("source_return_ids", [])
                if item is not None and str(item)
            }
        ),
        "maze_cell_id": None,
        "unitary_curvature_id": None,
        "translation_supervisory_relation_id": path.get(
            "translation_supervisory_relation_id"
        ),
        "semantic_translation_determined": path.get(
            "semantic_translation_determined"
        ) is True,
        "translation_scale": path.get("translation_scale"),
        "shared_token_ids": list(path.get("shared_token_ids", [])),
        "membership_in_closure_is_unconditional": True,
        "return_changes_determination_not_membership": True,
        "selection_authors_membership": False,
        "rendering_authors_membership": False,
    }
    body["id"] = _base._digest("continuing-translation-relation", body)
    return body


def derive_continuing_translation_closure(
    full_gate: Mapping[str, Any],
) -> dict[str, Any]:
    gate = full_gate.get("relative_natural_form_potential_gate")
    gate = gate if isinstance(gate, Mapping) else {}
    maze = gate.get("maze_partition")
    maze = maze if isinstance(maze, Mapping) else {}
    curvature = gate.get("unitary_curvature")
    curvature = curvature if isinstance(curvature, Mapping) else {}

    maze_by_path: dict[str, str] = {}
    for cell in _rows(maze.get("classes")):
        cell_id = str(cell.get("id") or "")
        if not cell_id:
            continue
        for path_id in cell.get("path_ids", []):
            maze_by_path[str(path_id)] = cell_id

    curvature_by_path = {
        str(row.get("path_id")): str(row.get("unitary_curvature_id"))
        for row in _rows(curvature.get("path_curvatures"))
        if row.get("path_id") and row.get("unitary_curvature_id")
    }

    relations = [_relation(path) for path in _rows(gate.get("paths"))]
    for relation in relations:
        relation["maze_cell_id"] = maze_by_path.get(relation["path_id"])
        relation["unitary_curvature_id"] = curvature_by_path.get(
            relation["path_id"]
        )
        relation.pop("id", None)
        relation["id"] = _base._digest("continuing-translation-relation", relation)

    returned_ids = [row["id"] for row in relations if row["returned"]]
    continuing_ids = [row["id"] for row in relations if row["continuing"]]

    translation_geometry = gate.get("translation_supervisory_geometry")
    translation_geometry = (
        translation_geometry if isinstance(translation_geometry, Mapping) else {}
    )
    family_potentials = [dict(row) for row in _rows(gate.get("family_potentials"))]

    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "revision_basis": full_gate.get("id"),
        "active_perspective_id": gate.get("active_perspective_id"),
        "focus_event_id": gate.get("focus_event_id"),
        "truth_invariant_id": gate.get("truth_invariant_id"),
        "translation_supervisory_geometry_id": translation_geometry.get("id"),
        "maze_partition_id": maze.get("id"),
        "unitary_curvature_id": curvature.get("id"),
        "natural_form_atlas_id": gate.get("natural_form_atlas_id"),
        "relations": relations,
        "relation_count": len(relations),
        "returned_relation_ids": returned_ids,
        "continuing_relation_ids": continuing_ids,
        "returned_relation_count": len(returned_ids),
        "continuing_relation_count": len(continuing_ids),
        "natural_form_family_potentials": family_potentials,
        "closure_contains_every_current_translation": True,
        "continuation_is_inside_closure": True,
        "nonreturned_relation_is_continuation_not_nonclosure": True,
        "returned_is_determination_not_membership": True,
        "family_of_translation_truth_is_visualized_as_natural_form_selection": True,
        "navigation_moves_within_closure": True,
        "hair_moves_within_closure": True,
        "zoom_moves_within_closure": True,
        "return_refines_determination": True,
        "selection_authors_truth": False,
        "rendering_authors_truth": False,
        "truth_issued": False,
        "existence_closed": False,
    }
    body["id"] = _base._digest("continuing-translation-closure", body)
    return body


def attach_continuing_translation_closure(
    full_gate: Mapping[str, Any],
) -> dict[str, Any]:
    full = deepcopy(dict(full_gate))
    continuum = derive_continuing_translation_closure(full)
    gate = deepcopy(dict(full.get("relative_natural_form_potential_gate") or {}))
    gate["continuing_translation_closure"] = continuum
    gate["continuing_translation_closure_id"] = continuum["id"]
    gate["closure_is_continuation_of_all"] = True
    gate["closure_has_external_nonclosure_region"] = False
    gate["returned_and_continuing_are_states_inside_one_closure"] = True
    gate.pop("id", None)
    gate["id"] = _base._digest("relative-natural-form-potential-gate", gate)

    full.pop("id", None)
    full["relative_natural_form_potential_gate"] = gate
    full["continuing_translation_closure_id"] = continuum["id"]
    full["closure_is_continuation_of_all"] = True
    full["returned_and_continuing_are_states_inside_one_closure"] = True
    full["ui_visualizes_natural_forms_selected_in_translation_closure"] = True
    full["potential_gate_natural_form_solver"] = (
        _base.derive_potential_gate_natural_form_solver(full)
    )
    full["id"] = _base._digest("full-supernet-potential-gate", full)
    return full


def validate_continuing_translation_closure(
    full_gate: Mapping[str, Any],
) -> dict[str, Any]:
    gate = full_gate.get("relative_natural_form_potential_gate")
    if not isinstance(gate, Mapping):
        return {"valid": False, "errors": ["continuing-closure:gate-missing"]}
    continuum = gate.get("continuing_translation_closure")
    if not isinstance(continuum, Mapping):
        return {"valid": False, "errors": ["continuing-closure:missing"]}

    predecessor = deepcopy(dict(full_gate))
    predecessor_gate = deepcopy(dict(gate))
    for key in (
        "continuing_translation_closure",
        "continuing_translation_closure_id",
        "closure_is_continuation_of_all",
        "closure_has_external_nonclosure_region",
        "returned_and_continuing_are_states_inside_one_closure",
    ):
        predecessor_gate.pop(key, None)
    predecessor["relative_natural_form_potential_gate"] = predecessor_gate
    for key in (
        "continuing_translation_closure_id",
        "closure_is_continuation_of_all",
        "returned_and_continuing_are_states_inside_one_closure",
        "ui_visualizes_natural_forms_selected_in_translation_closure",
    ):
        predecessor.pop(key, None)
    expected = derive_continuing_translation_closure(predecessor)

    errors: list[str] = []
    comparable_actual = dict(continuum)
    comparable_expected = dict(expected)
    comparable_expected["revision_basis"] = comparable_actual.get("revision_basis")
    comparable_expected.pop("id", None)
    comparable_actual_id = comparable_actual.pop("id", None)
    expected_id = _base._digest("continuing-translation-closure", comparable_actual)
    if comparable_actual != comparable_expected:
        errors.append("continuing-closure:not-derived")
    if comparable_actual_id != expected_id:
        errors.append("continuing-closure:id-mismatch")
    if continuum.get("continuation_is_inside_closure") is not True:
        errors.append("continuing-closure:continuation-outside")
    if continuum.get("closure_contains_every_current_translation") is not True:
        errors.append("continuing-closure:relation-omission")
    for relation in _rows(continuum.get("relations")):
        returned = relation.get("returned") is True
        continuing = relation.get("continuing") is True
        state = relation.get("closure_state")
        if returned == continuing:
            errors.append(f"continuing-closure:state-overlap:{relation.get('id')}")
        if state not in {RETURNED, CONTINUING}:
            errors.append(f"continuing-closure:unknown-state:{relation.get('id')}")
        if returned and state != RETURNED:
            errors.append(f"continuing-closure:returned-state:{relation.get('id')}")
        if continuing and state != CONTINUING:
            errors.append(f"continuing-closure:continuing-state:{relation.get('id')}")
    return {
        "valid": not errors,
        "errors": errors,
        "id": continuum.get("id"),
        "relation_count": continuum.get("relation_count", 0),
        "returned_relation_count": continuum.get("returned_relation_count", 0),
        "continuing_relation_count": continuum.get("continuing_relation_count", 0),
    }


__all__ = [
    "CONTINUING",
    "PROTOCOL",
    "RETURNED",
    "SCHEMA",
    "attach_continuing_translation_closure",
    "derive_continuing_translation_closure",
    "validate_continuing_translation_closure",
]
