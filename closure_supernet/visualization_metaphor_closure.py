from __future__ import annotations

"""NRRF885 runtime bridge: visualization equality is equality of what is seen.

The formal theorem is not re-proved at runtime.  This module derives a finite
content-addressed `Seen` quotient from the already-verified continuing
translation closure.  Labels, SVG coordinates, hair, zoom and renderer choices
do not enter this quotient.

A structural visualization current is attached to each relation for which the
existing semantic interaction layer has identified a natural form.  Currents
with the same natural-form/rotation class share one structural crystal ball.
This is a runtime realization of the NRRF885 reading, not an analytic
reconstruction of tan(pi/2), Fourier or Chaitin-Kakeya mathematics.
"""

from copy import deepcopy
from typing import Any, Mapping, Sequence

from . import full_supernet_potential_gate as _base
from .continuing_closure_full_gate import (
    derive_full_supernet_gate_contract as derive_continuing_gate,
    validate_full_supernet_gate_contract as validate_continuing_gate,
)
from .translation_supervisory_full_gate import source_perspective_registry

PROTOCOL = "SUPERNET-NRRF885-VISUALIZATION-METAPHOR-CLOSURE"
SCHEMA = "closure.supernet/nrrf885-visualization-metaphor-closure-v1"
FORMAL_MODULE = (
    "NRRF885ProofByVisualizationMetaphorEqualityCompleteRelationsAndTheCurrentsOfTheSlideAsVisualizationCrystalBalls"
)
FORMAL_THEOREMS = (
    "currents_of_the_slide_are_visualization_crystal_balls",
    "metaphorEq_iff_seen_eq",
    "visInvariant_iff_factors_through_seen",
    "metaphor_equality_complete_relations",
    "family_of_translation_truth_is_visualization_of_natural_forms_selected_in_closure",
    "proof_by_visualization_is_metaphor_equality_complete_relations",
)


def _rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _visual_by_path(gate: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    identification = gate.get("equal_user_token_visual_identification")
    identification = identification if isinstance(identification, Mapping) else {}
    return {
        str(row.get("path_id")): row
        for row in _rows(identification.get("relations"))
        if row.get("path_id")
    }


def _continuum_by_path(gate: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    continuum = gate.get("continuing_translation_closure")
    continuum = continuum if isinstance(continuum, Mapping) else {}
    return {
        str(row.get("path_id")): row
        for row in _rows(continuum.get("relations"))
        if row.get("path_id")
    }


def _current(
    path_id: str,
    *,
    visual: Mapping[str, Any],
    continuum: Mapping[str, Any],
) -> dict[str, Any]:
    natural_form_id = (
        str(visual.get("natural_form_id"))
        if visual.get("natural_form_id")
        else None
    )
    semantic_family_id = (
        str(visual.get("semantic_family_id"))
        if visual.get("semantic_family_id")
        else None
    )
    maze_cell_id = (
        str(continuum.get("maze_cell_id"))
        if continuum.get("maze_cell_id")
        else None
    )
    curvature_id = (
        str(continuum.get("unitary_curvature_id"))
        if continuum.get("unitary_curvature_id")
        else None
    )

    # Runtime rotation classes are semantic natural-form classes.  No visual
    # coordinate, label, hair angle or zoom value is admitted here.
    rotation_class_id = (
        _base._digest(
            "visualization-rotation-class",
            {
                "natural_form_id": natural_form_id,
                "semantic_family_id": semantic_family_id,
            },
        )
        if natural_form_id
        else None
    )
    crystal_ball_id = (
        _base._digest(
            "visualization-crystal-ball",
            {"rotation_class_id": rotation_class_id},
        )
        if rotation_class_id
        else None
    )
    fold_class_id = (
        _base._digest(
            "visualization-fold-class",
            {
                "natural_form_id": natural_form_id,
                "rotation_class_id": rotation_class_id,
            },
        )
        if natural_form_id
        else None
    )

    body = {
        "path_id": path_id,
        "closure_state": continuum.get("closure_state"),
        "returned": continuum.get("returned") is True,
        "continuing": continuum.get("continuing") is True,
        "natural_form_id": natural_form_id,
        "semantic_family_id": semantic_family_id,
        "maze_cell_id": maze_cell_id,
        "unitary_curvature_id": curvature_id,
        "rotation_class_id": rotation_class_id,
        "fold_class_id": fold_class_id,
        "crystal_ball_id": crystal_ball_id,
        "current_defined": fold_class_id is not None,
        "current_is_translation_orbit_reading": fold_class_id is not None,
        "crystal_ball_is_rotation_class_reading": crystal_ball_id is not None,
        "labels_enter_seen": False,
        "renderer_coordinates_enter_seen": False,
        "hair_enters_seen": False,
        "zoom_enters_seen": False,
        "analytic_tan_limit_claimed": False,
        "formal_source_verified_by_runtime": False,
    }
    body["id"] = _base._digest("visualization-current", body)
    return body


def derive_visualization_metaphor_closure(
    full_gate: Mapping[str, Any],
) -> dict[str, Any]:
    gate = full_gate.get("relative_natural_form_potential_gate")
    gate = gate if isinstance(gate, Mapping) else {}
    visual_by_path = _visual_by_path(gate)
    continuum_by_path = _continuum_by_path(gate)

    currents: list[dict[str, Any]] = []
    for path_id in sorted(continuum_by_path):
        currents.append(
            _current(
                path_id,
                visual=visual_by_path.get(path_id, {}),
                continuum=continuum_by_path[path_id],
            )
        )

    seen_fold_class_ids = sorted(
        {
            str(row["fold_class_id"])
            for row in currents
            if row.get("fold_class_id")
        }
    )
    seen_body = {"fold_class_ids": seen_fold_class_ids}
    seen_id = _base._digest("visualization-seen", seen_body)
    metaphor_class_id = _base._digest(
        "visualization-metaphor-class",
        {"seen_id": seen_id},
    )

    balls_by_id: dict[str, dict[str, Any]] = {}
    for current in currents:
        ball_id = current.get("crystal_ball_id")
        if not ball_id:
            continue
        row = balls_by_id.setdefault(
            str(ball_id),
            {
                "id": str(ball_id),
                "rotation_class_id": current.get("rotation_class_id"),
                "natural_form_id": current.get("natural_form_id"),
                "current_ids": [],
                "path_ids": [],
            },
        )
        row["current_ids"].append(current["id"])
        row["path_ids"].append(current["path_id"])
    crystal_balls = []
    for ball in balls_by_id.values():
        ball["current_ids"] = sorted(set(ball["current_ids"]))
        ball["path_ids"] = sorted(set(ball["path_ids"]))
        ball["same_rotation_class_same_ball"] = True
        ball["renderer_geometry_authors_ball"] = False
        crystal_balls.append(ball)
    crystal_balls.sort(key=lambda row: row["id"])

    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "formal_module": FORMAL_MODULE,
        "formal_theorems": list(FORMAL_THEOREMS),
        "formal_source_verified_by_runtime": False,
        "runtime_reproves_lean": False,
        "continuing_translation_closure_id": gate.get(
            "continuing_translation_closure_id"
        ),
        "translation_supervisory_geometry_id": gate.get(
            "translation_supervisory_geometry_id"
        ),
        "currents": currents,
        "current_count": len(currents),
        "crystal_balls": crystal_balls,
        "crystal_ball_count": len(crystal_balls),
        "seen": seen_body,
        "seen_id": seen_id,
        "seen_fold_class_ids": seen_fold_class_ids,
        "metaphor_class_id": metaphor_class_id,
        "metaphor_equality_runtime_criterion": "SEEN_ID_EQUALITY",
        "visual_invariants_factor_through_seen": True,
        "metaphor_equality_complete_for_formal_visual_invariants": True,
        "family_of_translation_truth_visualizes_natural_form_selection": True,
        "labels_author_metaphor_equality": False,
        "renderer_coordinates_author_metaphor_equality": False,
        "hair_authors_metaphor_equality": False,
        "zoom_authors_metaphor_equality": False,
        "selection_authors_metaphor_equality": False,
        "crystal_ball_is_master_supernet_ontology": False,
        "crystal_ball_is_local_visualization_chart": True,
        "analytic_tan_limit_claimed": False,
        "truth_issued": False,
        "existence_closed": False,
    }
    body["id"] = _base._digest("visualization-metaphor-closure", body)
    return body


def attach_visualization_metaphor_closure(
    full_gate: Mapping[str, Any],
) -> dict[str, Any]:
    full = deepcopy(dict(full_gate))
    gate = deepcopy(dict(full.get("relative_natural_form_potential_gate") or {}))
    visualization = derive_visualization_metaphor_closure(full)
    gate["visualization_metaphor_closure"] = visualization
    gate["visualization_metaphor_closure_id"] = visualization["id"]
    gate["seen_id"] = visualization["seen_id"]
    gate["metaphor_class_id"] = visualization["metaphor_class_id"]
    gate["visual_equality_is_seen_equality"] = True
    gate["ui_is_visualization_of_translation_family_selection"] = True
    gate.pop("id", None)
    gate["id"] = _base._digest("relative-natural-form-potential-gate", gate)

    full.pop("id", None)
    full["relative_natural_form_potential_gate"] = gate
    full["visualization_metaphor_closure_id"] = visualization["id"]
    full["seen_id"] = visualization["seen_id"]
    full["metaphor_class_id"] = visualization["metaphor_class_id"]
    full["visual_equality_is_seen_equality"] = True
    full["proof_by_visualization_uses_metaphor_equality"] = True
    full["ui_is_visualization_of_translation_family_selection"] = True
    full["potential_gate_natural_form_solver"] = (
        _base.derive_potential_gate_natural_form_solver(full)
    )
    full["id"] = _base._digest("full-supernet-potential-gate", full)
    return full


def derive_full_supernet_gate_contract(
    closure_contract: Mapping[str, Any],
    *,
    navigation_context: Mapping[str, Any] | None = None,
    source_perspective_by_event: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    predecessor = derive_continuing_gate(
        closure_contract,
        navigation_context=navigation_context,
        source_perspective_by_event=(
            source_perspective_registry()
            if source_perspective_by_event is None
            else source_perspective_by_event
        ),
    )
    return attach_visualization_metaphor_closure(predecessor)


def validate_full_supernet_gate_contract(
    full_gate: Mapping[str, Any],
) -> dict[str, Any]:
    closure_contract = full_gate.get("closure_ui_contract")
    navigation_context = full_gate.get("navigation_context")
    provenance = full_gate.get("source_perspective_by_event")
    provenance = provenance if isinstance(provenance, Mapping) else {}
    if not isinstance(closure_contract, Mapping):
        return {
            "valid": False,
            "errors": ["visualization-metaphor:closure-contract-missing"],
        }

    expected = derive_full_supernet_gate_contract(
        closure_contract,
        navigation_context=(
            navigation_context if isinstance(navigation_context, Mapping) else None
        ),
        source_perspective_by_event=provenance,
    )
    errors: list[str] = []
    if dict(full_gate) != expected:
        errors.append("visualization-metaphor:not-derived")

    predecessor = derive_continuing_gate(
        closure_contract,
        navigation_context=(
            navigation_context if isinstance(navigation_context, Mapping) else None
        ),
        source_perspective_by_event=provenance,
    )
    predecessor_validation = validate_continuing_gate(predecessor)
    if predecessor_validation.get("valid") is not True:
        errors.extend(predecessor_validation.get("errors", []))

    gate = expected.get("relative_natural_form_potential_gate")
    gate = gate if isinstance(gate, Mapping) else {}
    visualization = gate.get("visualization_metaphor_closure")
    if not isinstance(visualization, Mapping):
        errors.append("visualization-metaphor:missing")
    else:
        if visualization.get("metaphor_equality_runtime_criterion") != "SEEN_ID_EQUALITY":
            errors.append("visualization-metaphor:wrong-equivalence")
        if visualization.get("visual_invariants_factor_through_seen") is not True:
            errors.append("visualization-metaphor:visual-invariant-leak")
        if visualization.get("labels_author_metaphor_equality") is not False:
            errors.append("visualization-metaphor:label-authority")
        if visualization.get("renderer_coordinates_author_metaphor_equality") is not False:
            errors.append("visualization-metaphor:renderer-authority")
        fold_ids = sorted(
            {
                str(row.get("fold_class_id"))
                for row in _rows(visualization.get("currents"))
                if row.get("fold_class_id")
            }
        )
        if fold_ids != list(visualization.get("seen_fold_class_ids", [])):
            errors.append("visualization-metaphor:seen-not-complete")
        expected_seen = _base._digest(
            "visualization-seen",
            {"fold_class_ids": fold_ids},
        )
        if visualization.get("seen_id") != expected_seen:
            errors.append("visualization-metaphor:seen-id-mismatch")
        for ball in _rows(visualization.get("crystal_balls")):
            expected_ball = _base._digest(
                "visualization-crystal-ball",
                {"rotation_class_id": ball.get("rotation_class_id")},
            )
            if ball.get("id") != expected_ball:
                errors.append("visualization-metaphor:crystal-ball-not-rotation-class")

    return {
        "valid": not errors,
        "errors": errors,
        "id": expected.get("id"),
        "visualization_metaphor_closure_id": expected.get(
            "visualization_metaphor_closure_id"
        ),
        "seen_id": expected.get("seen_id"),
        "metaphor_class_id": expected.get("metaphor_class_id"),
    }


__all__ = [
    "FORMAL_MODULE",
    "FORMAL_THEOREMS",
    "PROTOCOL",
    "SCHEMA",
    "attach_visualization_metaphor_closure",
    "derive_full_supernet_gate_contract",
    "derive_visualization_metaphor_closure",
    "validate_full_supernet_gate_contract",
]
