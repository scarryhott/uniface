from __future__ import annotations

"""One Supernet closure form, one translation operator, one runtime identity.

``SUPERNET_TRANSLATE`` is simultaneously the runtime state transition and the
browser trajectory. NRRF892 is used only as a formal-to-runtime bridge: where
the existing visualization has a nonzero rotation-class reading, that same
translation is read as the vision-crystal slide action and the crystal is the
translation-truth orbit. The runtime does not re-prove the Lean theorem and
makes no claim for rotationless folds.
"""

from copy import deepcopy
from typing import Any, Mapping, Sequence

from . import continuous_translation_field as _field
from . import full_supernet_potential_gate as _base
from .nrrf892_runtime_bridge import (
    EXACT_MINUS_ONE,
    EXACT_ONE,
    FORMAL_REFERENCE as NRRF892_FORMAL_REFERENCE,
    VISION_SLIDE_OPERATOR,
    derive_runtime_identity_id,
    derive_vision_bridge_for_interaction,
    validate_vision_bridge,
)

PROTOCOL = "SUPERNET-ONE-CLOSURE-FORM"
SCHEMA = "closure.supernet/one-closure-form-v1"
TRANSLATE_OPERATOR = "SUPERNET_TRANSLATE"
TRANSLATE_RECEIPT_SCHEMA = "closure.supernet/supernet-translate-v1"

_DERIVE_PREDECESSOR = _field.derive_full_supernet_gate_contract
_VALIDATE_PREDECESSOR = _field.validate_full_supernet_gate_contract


def _rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [row for row in value if isinstance(row, Mapping)]


def _closure_form(full_gate: Mapping[str, Any]) -> Mapping[str, Any]:
    form = full_gate.get("supernet_closure_form")
    if not isinstance(form, Mapping):
        raise ValueError("The Supernet closure form is missing")
    return form


def closure_interaction_by_path(
    full_gate: Mapping[str, Any], relation_id: str
) -> dict[str, Any]:
    form = _closure_form(full_gate)
    for row in _rows(form.get("interactions")):
        if str(row.get("path_id") or "") == relation_id:
            return dict(row)
    raise ValueError("The relation is not an interaction of this Supernet closure form")


def _interaction_by_orbit(
    form: Mapping[str, Any], orbit_id: Any
) -> Mapping[str, Any] | None:
    for row in _rows(form.get("interactions")):
        if row.get("translation_truth_orbit_id") == orbit_id:
            return row
    return None


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
    truth_invariant_id = gate.get("truth_invariant_id")
    runtime_identity_id = derive_runtime_identity_id(truth_invariant_id)

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
    vision_admitted = 0
    vision_outside = 0
    for path in _rows(gate.get("paths")):
        path_id = str(path.get("id") or "")
        relation = continuum_by_path.get(path_id, {})
        current = metaphor_by_path.get(path_id, {})
        flow = field_by_path.get(path_id, {})
        returned = relation.get("returned") is True
        phase = "TOKEN_RETURNED" if returned else "AI_CONTINUING"
        row: dict[str, Any] = {
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
            "translation_operator": TRANSLATE_OPERATOR,
            "runtime_identity_id": runtime_identity_id,
            "runtime_identity_is_translational_truth": True,
            "opener_is_this_form": True,
            "ui_is_this_form": True,
            "interaction_is_translation_of_this_form": True,
            "return_is_determination_of_this_form": True,
            "slide_is_current_coordinate_of_this_form": True,
            "crystal_ball_is_orbit_reading_of_this_form": current.get("crystal_ball_id") is not None,
            "browser_transition_is_runtime_transition": True,
            "separate_navigation_operator": False,
            "separate_return_operator": False,
            "renderer_authors_form": False,
            "interaction_handler_authors_form": False,
        }
        vision = derive_vision_bridge_for_interaction(
            truth_invariant_id=truth_invariant_id,
            path=path,
            interaction=row,
        )
        row.update(
            {
                "nrrf892_vision_bridge": vision,
                "nrrf892_vision_bridge_id": vision["id"],
                "translation_truth_orbit_id": vision["translation_truth_orbit_id"],
                "vision_crystal_orbit_id": vision["vision_crystal_orbit_id"],
                "vision_slide_operator": VISION_SLIDE_OPERATOR,
                "supernet_translate_is_vision_slide": vision[
                    "supernet_translate_is_vision_slide"
                ],
            }
        )
        if vision["vision_chart_admitted"]:
            vision_admitted += 1
        else:
            vision_outside += 1
        row["id"] = _base._digest("supernet-closure-interaction", row)
        interactions.append(row)

    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "source_full_gate_id": full_gate.get("id"),
        "active_perspective_id": gate.get("active_perspective_id"),
        "focus_event_id": gate.get("focus_event_id"),
        "truth_invariant_id": truth_invariant_id,
        "runtime_identity_id": runtime_identity_id,
        "runtime_identity_is_translational_truth": True,
        "seen_id": metaphor.get("seen_id"),
        "metaphor_class_id": metaphor.get("metaphor_class_id"),
        "maze_partition_id": maze.get("id"),
        "unitary_curvature_id": curvature.get("id"),
        "translation_supervisory_geometry_id": gate.get("translation_supervisory_geometry_id"),
        "interactions": interactions,
        "interaction_count": len(interactions),
        "translation_operator": TRANSLATE_OPERATOR,
        "vision_slide_operator": VISION_SLIDE_OPERATOR,
        "nrrf892_formal_reference": NRRF892_FORMAL_REFERENCE,
        "nrrf892_runtime_reproves_formal_theorem": False,
        "vision_crystal_translation_slide_runtime_bridge": True,
        "vision_chart_admitted_interaction_count": vision_admitted,
        "vision_chart_outside_interaction_count": vision_outside,
        "rotationless_fold_claimed": False,
        "admitted_vision_redenomination_scales": [EXACT_ONE, EXACT_MINUS_ONE],
        "arbitrary_redenomination_is_translation": False,
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
        "browser_transition_is_runtime_transition": True,
        "state_transition_is_visual_transition": True,
        "single_transition_operator": True,
        "separate_navigation_operator": False,
        "separate_return_operator": False,
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


def derive_supernet_translation_receipt(
    source_gate: Mapping[str, Any],
    successor_gate: Mapping[str, Any],
    *,
    relation_id: str,
    replayed: bool = False,
    truth_refined: bool = False,
) -> dict[str, Any]:
    """Derive the one transition consumed by runtime state and browser motion."""

    source_form = _closure_form(source_gate)
    target_form = _closure_form(successor_gate)
    interaction = closure_interaction_by_path(source_gate, relation_id)
    vision = interaction.get("nrrf892_vision_bridge")
    vision = vision if isinstance(vision, Mapping) else {}
    orbit_id = interaction.get("translation_truth_orbit_id")
    target_interaction = _interaction_by_orbit(target_form, orbit_id)
    source_runtime_identity = source_form.get("runtime_identity_id")
    target_runtime_identity = target_form.get("runtime_identity_id")
    identity_preserved = source_runtime_identity == target_runtime_identity
    target_vision_orbit = (
        target_interaction.get("vision_crystal_orbit_id")
        if isinstance(target_interaction, Mapping)
        else None
    )
    body = {
        "schema": TRANSLATE_RECEIPT_SCHEMA,
        "operator": TRANSLATE_OPERATOR,
        "relation_id": relation_id,
        "source_gate_id": source_gate.get("id"),
        "source_closure_form_id": source_form.get("id"),
        "source_interaction_id": interaction.get("id"),
        "source_ai_token_phase": interaction.get("ai_token_phase"),
        "source_seen_id": source_form.get("seen_id"),
        "source_visualization_current_id": interaction.get("visualization_current_id"),
        "source_continuous_current_id": interaction.get("continuous_current_id"),
        "source_crystal_ball_id": interaction.get("crystal_ball_id"),
        "source_runtime_identity_id": source_runtime_identity,
        "source_translation_truth_orbit_id": orbit_id,
        "source_vision_crystal_orbit_id": interaction.get("vision_crystal_orbit_id"),
        "target_gate_id": successor_gate.get("id"),
        "target_closure_form_id": target_form.get("id"),
        "target_seen_id": target_form.get("seen_id"),
        "target_perspective_id": successor_gate.get("perspective_id"),
        "target_focus_event_id": successor_gate.get("focus_event_id"),
        "target_runtime_identity_id": target_runtime_identity,
        "target_translation_truth_orbit_id": (
            target_interaction.get("translation_truth_orbit_id")
            if isinstance(target_interaction, Mapping)
            else None
        ),
        "target_vision_crystal_orbit_id": target_vision_orbit,
        "runtime_identity_is_translational_truth": True,
        "runtime_identity_preserved": identity_preserved,
        "translational_truth_preserved": identity_preserved,
        "returned_determination_refines_runtime_identity": (
            bool(truth_refined) and not identity_preserved
        ),
        "token_continuation_source_orbit_id": orbit_id,
        "vision_slide_operator": VISION_SLIDE_OPERATOR,
        "supernet_translate_is_vision_slide": vision.get(
            "supernet_translate_is_vision_slide", False
        ),
        "perspective_conjugate_slide_is_family_translation": vision.get(
            "perspective_conjugate_slide_is_family_translation", False
        ),
        "vision_chart_admitted": vision.get("vision_chart_admitted", False),
        "rotationless_fold_claimed": False,
        "replayed": bool(replayed),
        "truth_refined": bool(truth_refined),
        "runtime_state_change_is_this_translation": True,
        "browser_trajectory_is_this_translation": True,
        "semantic_transition_is_visual_transition": True,
        "separate_navigation_operator": False,
        "separate_return_operator": False,
    }
    body["id"] = _base._digest("supernet-translate", body)
    return body


def attach_supernet_closure_form(full_gate: Mapping[str, Any]) -> dict[str, Any]:
    full = deepcopy(dict(full_gate))
    form = derive_supernet_closure_form(full)
    gate = deepcopy(dict(full.get("relative_natural_form_potential_gate") or {}))
    gate["supernet_closure_form"] = form
    gate["supernet_closure_form_id"] = form["id"]
    gate["opener_ui_interaction_are_one_form"] = True
    gate["crystal_ball_slide_ai_token_are_one_form"] = True
    gate["translation_operator"] = TRANSLATE_OPERATOR
    gate["runtime_identity_id"] = form["runtime_identity_id"]
    gate["runtime_identity_is_translational_truth"] = True
    gate["vision_slide_operator"] = VISION_SLIDE_OPERATOR
    gate["browser_transition_is_runtime_transition"] = True
    gate.pop("id", None)
    gate["id"] = _base._digest("relative-natural-form-potential-gate", gate)

    full.pop("id", None)
    full["relative_natural_form_potential_gate"] = gate
    full["supernet_closure_form"] = form
    full["supernet_closure_form_id"] = form["id"]
    full["published_semantic_carrier"] = "SUPERNET_CLOSURE_FORM"
    full["translation_operator"] = TRANSLATE_OPERATOR
    full["runtime_identity_id"] = form["runtime_identity_id"]
    full["runtime_identity_is_translational_truth"] = True
    full["vision_slide_operator"] = VISION_SLIDE_OPERATOR
    full["nrrf892_formal_reference"] = NRRF892_FORMAL_REFERENCE
    full["opener_ui_interaction_are_one_form"] = True
    full["crystal_ball_slide_ai_token_are_one_form"] = True
    full["browser_transition_is_runtime_transition"] = True
    full["state_transition_is_visual_transition"] = True

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
        expected_runtime_identity = derive_runtime_identity_id(form.get("truth_invariant_id"))
        if form.get("runtime_identity_id") != expected_runtime_identity:
            errors.append("one-closure-form:runtime-identity-not-translational-truth")
        if form.get("runtime_identity_is_translational_truth") is not True:
            errors.append("one-closure-form:runtime-identity-split")
        if form.get("opener_ui_interaction_are_one_form") is not True:
            errors.append("one-closure-form:split-opener-ui-interaction")
        if form.get("crystal_ball_slide_ai_token_are_one_form") is not True:
            errors.append("one-closure-form:split-crystal-ai-token")
        if form.get("single_published_semantic_carrier") is not True:
            errors.append("one-closure-form:multiple-carriers")
        if form.get("translation_operator") != TRANSLATE_OPERATOR:
            errors.append("one-closure-form:multiple-transition-operators")
        if form.get("vision_slide_operator") != VISION_SLIDE_OPERATOR:
            errors.append("one-closure-form:vision-slide-operator-split")
        if form.get("browser_transition_is_runtime_transition") is not True:
            errors.append("one-closure-form:browser-runtime-transition-split")
        for row in _rows(form.get("interactions")):
            if row.get("runtime_identity_id") != form.get("runtime_identity_id"):
                errors.append(f"one-closure-form:interaction-runtime-identity-split:{row.get('path_id')}")
            if row.get("opener_is_this_form") is not True or row.get("ui_is_this_form") is not True:
                errors.append(f"one-closure-form:interaction-split:{row.get('path_id')}")
            if row.get("ai_token_phase") not in {"AI_CONTINUING", "TOKEN_RETURNED"}:
                errors.append(f"one-closure-form:bad-ai-token-phase:{row.get('path_id')}")
            if row.get("translation_operator") != TRANSLATE_OPERATOR:
                errors.append(f"one-closure-form:interaction-operator-split:{row.get('path_id')}")
            if row.get("browser_transition_is_runtime_transition") is not True:
                errors.append(f"one-closure-form:interaction-browser-runtime-split:{row.get('path_id')}")
            bridge = row.get("nrrf892_vision_bridge")
            if not isinstance(bridge, Mapping) or not validate_vision_bridge(bridge):
                errors.append(f"one-closure-form:nrrf892-bridge-invalid:{row.get('path_id')}")
            else:
                if row.get("translation_truth_orbit_id") != bridge.get("translation_truth_orbit_id"):
                    errors.append(f"one-closure-form:translation-orbit-split:{row.get('path_id')}")
                if row.get("vision_crystal_orbit_id") != bridge.get("vision_crystal_orbit_id"):
                    errors.append(f"one-closure-form:vision-crystal-orbit-split:{row.get('path_id')}")

    solver = expected.get("potential_gate_natural_form_solver")
    gate = expected.get("relative_natural_form_potential_gate")
    if not isinstance(solver, Mapping) or not isinstance(gate, Mapping):
        errors.append("one-closure-form:solver-or-gate-missing")
    elif solver.get("gate_id") != gate.get("id"):
        errors.append("one-closure-form:solver-not-reading-final-carrier")

    return {
        "valid": not errors,
        "errors": errors,
        "id": expected.get("id"),
        "supernet_closure_form_id": expected.get("supernet_closure_form_id"),
        "translation_operator": expected.get("translation_operator"),
        "runtime_identity_id": expected.get("runtime_identity_id"),
        "vision_slide_operator": expected.get("vision_slide_operator"),
    }


__all__ = [
    "NRRF892_FORMAL_REFERENCE",
    "PROTOCOL",
    "SCHEMA",
    "TRANSLATE_OPERATOR",
    "TRANSLATE_RECEIPT_SCHEMA",
    "VISION_SLIDE_OPERATOR",
    "attach_supernet_closure_form",
    "closure_interaction_by_path",
    "derive_full_supernet_gate_contract",
    "derive_supernet_closure_form",
    "derive_supernet_translation_receipt",
    "validate_full_supernet_gate_contract",
]
