from __future__ import annotations

"""Runtime bridge for NRRF892 vision-crystal slide closure.

This module does not re-prove NRRF892. It turns the proved structural reading
into deterministic runtime metadata: runtime identity is the current
translational-truth class; each supported interaction is read as one vision
crystal translation orbit; and SUPERNET_TRANSLATE is the runtime slide action.
The NRRF892 chart boundary is preserved exactly as a runtime guard: only
interactions with a nonempty rotation-class reading are admitted to this bridge.
"""

from typing import Any, Mapping

from . import full_supernet_potential_gate as _base

PROTOCOL = "NRRF892-RUNTIME-BRIDGE"
SCHEMA = "closure.supernet/nrrf892-runtime-bridge-v1"
FORMAL_REFERENCE = "NRRF892VisionCrystalTranslationSlideIsClosedThroughTheFurtheredClosureFamily"
VISION_SLIDE_OPERATOR = "VISION_SLIDE_TRANS"
VISION_CHART_DOMAIN = "FINITE_PREDUAL_ROTATION_NONZERO"
VISION_CHART_OUTSIDE = "CONTINUING_OUTSIDE_NRRF892_VISION_CHART"

EXACT_ONE = {"num": 1, "den": 1}
EXACT_MINUS_ONE = {"num": -1, "den": 1}


def derive_runtime_identity_id(truth_invariant_id: Any) -> str:
    """Runtime identity is the content address of current translational truth."""

    return _base._digest(
        "runtime-translational-truth-identity",
        {"truth_invariant_id": truth_invariant_id},
    )


def derive_translation_truth_orbit_id(
    *,
    truth_invariant_id: Any,
    path: Mapping[str, Any],
    interaction: Mapping[str, Any],
) -> str:
    """Derive an interaction orbit without perspective/render coordinates."""

    witness = (
        path.get("translation_supervisory_relation_id")
        or path.get("relation_id")
        or tuple(sorted(str(v) for v in path.get("source_return_ids", []) if v))
        or path.get("id")
    )
    return _base._digest(
        "translation-truth-orbit",
        {
            "truth_invariant_id": truth_invariant_id,
            "semantic_family_id": interaction.get("semantic_family_id"),
            "relation_witness": witness,
        },
    )


def derive_vision_bridge_for_interaction(
    *,
    truth_invariant_id: Any,
    path: Mapping[str, Any],
    interaction: Mapping[str, Any],
) -> dict[str, Any]:
    """Read one Supernet interaction as an NRRF892 vision-slide orbit."""

    rotation_class_id = interaction.get("rotation_class_id")
    in_chart = bool(rotation_class_id)
    orbit_id = derive_translation_truth_orbit_id(
        truth_invariant_id=truth_invariant_id,
        path=path,
        interaction=interaction,
    )
    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "formal_reference": FORMAL_REFERENCE,
        "runtime_reproves_formal_theorem": False,
        "vision_chart_domain": VISION_CHART_DOMAIN if in_chart else VISION_CHART_OUTSIDE,
        "vision_chart_admitted": in_chart,
        "rotationless_fold_claimed": False,
        "runtime_identity_is_translational_truth": True,
        "translation_truth_orbit_id": orbit_id,
        "vision_crystal_orbit_id": orbit_id if in_chart else None,
        "vision_crystal_is_translation_orbit": in_chart,
        "vision_slide_operator": VISION_SLIDE_OPERATOR,
        "supernet_translate_is_vision_slide": in_chart,
        "slide_is_closure_family_member": in_chart,
        "slide_gravitational_ratio": EXACT_ONE if in_chart else None,
        "slide_group_identity_amount": {"num": 0, "den": 1} if in_chart else None,
        "slide_inverse_is_family_member": in_chart,
        "perspective_conjugate_slide_is_family_translation": in_chart,
        "crystal_action_is_simply_transitive_formal_reading": in_chart,
        "admitted_vision_redenomination_scales": [EXACT_ONE, EXACT_MINUS_ONE],
        "arbitrary_redenomination_is_translation": False,
        "crystal_ball_is_local_chart": True,
    }
    body["id"] = _base._digest("nrrf892-runtime-vision-bridge", body)
    return body


def validate_vision_bridge(bridge: Mapping[str, Any]) -> bool:
    if bridge.get("protocol") != PROTOCOL or bridge.get("schema") != SCHEMA:
        return False
    admitted = bridge.get("vision_chart_admitted") is True
    if admitted:
        if bridge.get("vision_crystal_orbit_id") != bridge.get("translation_truth_orbit_id"):
            return False
        if bridge.get("supernet_translate_is_vision_slide") is not True:
            return False
        if bridge.get("slide_is_closure_family_member") is not True:
            return False
        if bridge.get("slide_gravitational_ratio") != EXACT_ONE:
            return False
    else:
        if bridge.get("rotationless_fold_claimed") is not False:
            return False
        if bridge.get("vision_crystal_orbit_id") is not None:
            return False
    return True


__all__ = [
    "EXACT_MINUS_ONE",
    "EXACT_ONE",
    "FORMAL_REFERENCE",
    "PROTOCOL",
    "SCHEMA",
    "VISION_CHART_DOMAIN",
    "VISION_CHART_OUTSIDE",
    "VISION_SLIDE_OPERATOR",
    "derive_runtime_identity_id",
    "derive_translation_truth_orbit_id",
    "derive_vision_bridge_for_interaction",
    "validate_vision_bridge",
]
