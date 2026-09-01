from __future__ import annotations

"""Visual identification from equal user/token interactions.

This module is the runtime bridge for the NRRF883 reading that UI, trading,
AI curvature and token maze partition are one translational interaction layer.
A visual identity is never authored from proximity, family names, SVG geometry
or pointer selection. It exists exactly when the active user's admissible path
and the token's maze-cell reading factor through the same returned semantic
natural-form family and the same return-effect cell.

The resulting quotient key is therefore

    RelativeInteraction = SemanticNaturalFormFamily × MazeCell

and the visual identifier is only a deterministic presentation name for that
already-derived equality. OPEN semantic translations remain visible apertures
but do not receive a witnessed visual identity.
"""

from copy import deepcopy
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS
from . import full_supernet_potential_gate as _base
from .translation_supervisory_full_gate import (
    derive_full_supernet_gate_contract as derive_translation_gate,
    source_perspective_registry,
    validate_full_supernet_gate_contract as validate_translation_gate,
)

PROTOCOL = "SUPERNET-EQUAL-USER-TOKEN-VISUAL-IDENTIFICATION"
SCHEMA = "closure.supernet/equal-user-token-visual-identification-v1"
FORMAL_MODULE = (
    "NRRF883TradingAndUIAreOneLayerOfTheAITokenRelationUnitaryCurvatureAndMazePartition"
)
FORMAL_THEOREMS = (
    "relativeBall_eq_bottleneck_capacity",
    "ui_derived_from_closure_ball",
    "itinerary_feasible_iff_within_ball",
    "hair_and_zoom_author_no_truth",
    "only_a_verified_return_recloses",
    "ai_and_token_are_one_translational_interactive_truth_closure",
    "layer_is_one_translational_closure",
    "visualization_iff_factors_through_naturalForm",
    "visualBalls_are_semantic",
    "trading_and_ui_are_one_layer_of_the_ai_token_relation",
)


def _rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _family_by_perspective(geometry: Mapping[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for family in _rows(geometry.get("global_belief_families")):
        family_id = str(family.get("id") or "")
        if not family_id:
            continue
        for perspective in family.get("perspective_ids", []):
            perspective_id = str(perspective or "")
            if perspective_id:
                result[perspective_id] = family_id
    return result


def _valuation_natural_form_by_perspective(
    geometry: Mapping[str, Any],
) -> dict[str, str]:
    return {
        str(row.get("perspective_id")): str(row.get("natural_form_id"))
        for row in _rows(geometry.get("valuations"))
        if row.get("perspective_id") and row.get("natural_form_id")
    }


def _maze_cell_by_path(maze: Mapping[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for cell in _rows(maze.get("classes")):
        cell_id = str(cell.get("id") or "")
        if not cell_id:
            continue
        for path_id in cell.get("path_ids", []):
            key = str(path_id or "")
            if key:
                result[key] = cell_id
    return result


def _semantic_relation_by_id(geometry: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(row.get("id")): row
        for row in _rows(geometry.get("relations"))
        if row.get("id")
    }


def derive_equal_user_token_visual_identification(
    gate: Mapping[str, Any],
) -> dict[str, Any]:
    """Derive visual identities from one exact user/token interaction quotient."""

    geometry = gate.get("translation_supervisory_geometry")
    geometry = geometry if isinstance(geometry, Mapping) else {}
    maze = gate.get("maze_partition")
    maze = maze if isinstance(maze, Mapping) else {}
    active = str(gate.get("active_perspective_id") or "")

    family_by_perspective = _family_by_perspective(geometry)
    natural_form_by_perspective = _valuation_natural_form_by_perspective(geometry)
    cell_by_path = _maze_cell_by_path(maze)
    relation_by_id = _semantic_relation_by_id(geometry)

    active_family = family_by_perspective.get(active)
    active_natural_form = natural_form_by_perspective.get(active)
    rows: list[dict[str, Any]] = []

    for path in _rows(gate.get("paths")):
        path_id = str(path.get("id") or "")
        if not path_id:
            continue
        cell_id = cell_by_path.get(path_id)
        source = str(path.get("source_perspective_id") or active)
        target = str(path.get("target_perspective_id") or source)
        semantic_relation_id = str(
            path.get("translation_supervisory_relation_id") or ""
        )
        semantic_relation = relation_by_id.get(semantic_relation_id)
        semantic_controlled = bool(semantic_relation_id)

        source_family = family_by_perspective.get(source)
        target_family = family_by_perspective.get(target)
        source_nf = natural_form_by_perspective.get(source)
        target_nf = natural_form_by_perspective.get(target)

        if semantic_controlled:
            semantic_equal = bool(
                semantic_relation is not None
                and semantic_relation.get("status") == WITNESSED_STATUS
                and semantic_relation.get("unique_relative_translation") is True
                and source_family
                and source_family == target_family
            )
            semantic_family_id = source_family if semantic_equal else None
            natural_form_id = source_nf if semantic_equal else None
        else:
            # A local interaction can be visually identified relative to the
            # active returned semantic family. No semantic return means there is
            # no token-relative visual equality yet.
            semantic_equal = bool(
                active_family
                and active_natural_form
                and source == active
                and source_family == active_family
            )
            semantic_family_id = active_family if semantic_equal else None
            natural_form_id = active_natural_form if semantic_equal else None

        token_interaction_defined = bool(cell_id and semantic_family_id)
        user_interaction_defined = bool(
            token_interaction_defined
            and path.get("source_preserved") is True
            and str(path.get("source_perspective_id") or active) == active
        )

        quotient_body = (
            {
                "semantic_family_id": semantic_family_id,
                "natural_form_id": natural_form_id,
                "maze_cell_id": cell_id,
                "path_status": str(path.get("status") or OPEN_STATUS),
            }
            if token_interaction_defined
            else None
        )
        token_read_id = (
            _base._digest("token-interaction-read", quotient_body)
            if quotient_body is not None
            else None
        )
        user_read_id = (
            _base._digest("token-interaction-read", quotient_body)
            if user_interaction_defined and quotient_body is not None
            else None
        )
        equal_interaction = bool(
            user_read_id and token_read_id and user_read_id == token_read_id
        )
        witnessed_visual_identity = bool(
            equal_interaction
            and (
                not semantic_controlled
                or str(path.get("status") or OPEN_STATUS) == WITNESSED_STATUS
            )
        )
        visual_id = (
            _base._digest(
                "visual-interaction-identity",
                {
                    "interaction_read_id": user_read_id,
                    "semantic_family_id": semantic_family_id,
                    "maze_cell_id": cell_id,
                },
            )
            if witnessed_visual_identity
            else None
        )

        body = {
            "path_id": path_id,
            "path_status": str(path.get("status") or OPEN_STATUS),
            "source_perspective_id": source,
            "target_perspective_id": target,
            "semantic_translation_controlled": semantic_controlled,
            "semantic_translation_relation_id": semantic_relation_id or None,
            "semantic_translation_equal": semantic_equal,
            "semantic_family_id": semantic_family_id,
            "natural_form_id": natural_form_id,
            "source_natural_form_id": source_nf,
            "target_natural_form_id": target_nf,
            "maze_cell_id": cell_id,
            "user_interaction_read_id": user_read_id,
            "token_interaction_read_id": token_read_id,
            "equal_user_token_interaction": equal_interaction,
            "visually_identified": witnessed_visual_identity,
            "visual_identification_id": visual_id,
            "visual_identification_requires_equal_user_token_interaction": True,
            "visual_similarity_authors_identification": False,
            "renderer_authors_identification": False,
            "selection_authors_identification": False,
            "hair_authors_identification": False,
            "zoom_authors_identification": False,
            "only_returned_translation_can_create_semantic_equality": True,
        }
        body["id"] = _base._digest("user-token-visual-relation", body)
        rows.append(body)

    visually_identified = [
        row["visual_identification_id"]
        for row in rows
        if row.get("visual_identification_id")
    ]
    open_visual = [
        row["path_id"]
        for row in rows
        if not row.get("visually_identified")
    ]
    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "formal_module": FORMAL_MODULE,
        "formal_theorems": list(FORMAL_THEOREMS),
        "formal_source_verified_by_runtime": False,
        "runtime_reproves_lean": False,
        "active_perspective_id": active,
        "translation_supervisory_geometry_id": geometry.get("id"),
        "maze_partition_id": maze.get("id"),
        "active_semantic_family_id": active_family,
        "active_natural_form_id": active_natural_form,
        "relations": rows,
        "relation_count": len(rows),
        "visually_identified_ids": visually_identified,
        "visually_open_path_ids": open_visual,
        "visual_identification_count": len(visually_identified),
        "relative_interaction_quotient": "NATURAL_FORM_FAMILY_X_MAZE_CELL",
        "visual_identification_iff_equal_user_token_interaction": True,
        "user_interaction_and_token_interaction_share_one_quotient": True,
        "open_semantic_translation_remains_visually_open": True,
        "visualization_is_relative_to_user_and_token_interaction": True,
        "rendering_authors_truth": False,
        "rendering_authors_equality": False,
        "selection_authors_truth": False,
        "truth_issued": False,
    }
    body["id"] = _base._digest("equal-user-token-visual-identification", body)
    return body


def _attach_visual_identification(full_gate: Mapping[str, Any]) -> dict[str, Any]:
    full = deepcopy(dict(full_gate))
    gate = deepcopy(dict(full["relative_natural_form_potential_gate"]))
    identification = derive_equal_user_token_visual_identification(gate)
    gate["equal_user_token_visual_identification"] = identification
    gate["equal_user_token_visual_identification_id"] = identification["id"]
    gate["visual_identification_iff_equal_user_token_interaction"] = True
    gate["visualization_is_relative_to_user_and_token_interaction"] = True
    gate["renderer_can_create_visual_equality"] = False
    gate.pop("id", None)
    gate["id"] = _base._digest("relative-natural-form-potential-gate", gate)

    full.pop("id", None)
    full["relative_natural_form_potential_gate"] = gate
    full["equal_user_token_visual_identification_id"] = identification["id"]
    full["visual_identification_iff_equal_user_token_interaction"] = True
    full["ui_is_visual_reading_of_equal_user_token_interactions"] = True
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
    base = derive_translation_gate(
        closure_contract,
        navigation_context=navigation_context,
        source_perspective_by_event=(
            source_perspective_registry()
            if source_perspective_by_event is None
            else source_perspective_by_event
        ),
    )
    return _attach_visual_identification(base)


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
            "errors": ["equal-user-token-visual:closure-contract-missing"],
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
        errors.append("equal-user-token-visual:not-derived")
    # Validate the predecessor independently by removing only the new derived
    # visual layer and reconstructing the NRRF882 contract.
    predecessor = derive_translation_gate(
        closure_contract,
        navigation_context=(
            navigation_context if isinstance(navigation_context, Mapping) else None
        ),
        source_perspective_by_event=provenance,
    )
    predecessor_validation = validate_translation_gate(predecessor)
    if predecessor_validation.get("valid") is not True:
        errors.extend(predecessor_validation.get("errors", []))

    gate = expected["relative_natural_form_potential_gate"]
    identification = gate.get("equal_user_token_visual_identification")
    if not isinstance(identification, Mapping):
        errors.append("equal-user-token-visual:identification-missing")
    else:
        if identification.get("visual_identification_iff_equal_user_token_interaction") is not True:
            errors.append("equal-user-token-visual:not-iff")
        for row in _rows(identification.get("relations")):
            equal_interaction = row.get("equal_user_token_interaction") is True
            identified = row.get("visually_identified") is True
            semantic_controlled = row.get("semantic_translation_controlled") is True
            witnessed = row.get("path_status") == WITNESSED_STATUS
            expected_identified = bool(
                equal_interaction and (not semantic_controlled or witnessed)
            )
            if identified != expected_identified:
                errors.append(
                    f"equal-user-token-visual:relation-mismatch:{row.get('path_id')}"
                )
            if identified and not row.get("visual_identification_id"):
                errors.append(
                    f"equal-user-token-visual:identified-without-id:{row.get('path_id')}"
                )
            if row.get("renderer_authors_identification") is not False:
                errors.append("equal-user-token-visual:renderer-authority")
    if expected.get("ui_is_visual_reading_of_equal_user_token_interactions") is not True:
        errors.append("equal-user-token-visual:ui-split")
    return {
        "valid": not errors,
        "errors": errors,
        "id": expected.get("id"),
        "equal_user_token_visual_identification_id": expected.get(
            "equal_user_token_visual_identification_id"
        ),
        "visual_identification_count": (
            (identification or {}).get("visual_identification_count")
            if isinstance(identification, Mapping)
            else 0
        ),
    }


__all__ = [
    "FORMAL_MODULE",
    "FORMAL_THEOREMS",
    "PROTOCOL",
    "SCHEMA",
    "derive_equal_user_token_visual_identification",
    "derive_full_supernet_gate_contract",
    "validate_full_supernet_gate_contract",
]
