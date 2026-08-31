from __future__ import annotations

"""Atlas-preserving Supernet interaction closure.

This module wraps the previous observer-observed translation kernel without
changing its proved/runtime closure conditions.  The correction is ontological:
the previously emitted ball/physical topology is one chart projection inside a
versioned natural-form atlas, not the container or replacement for every
historical natural form.
"""

import hashlib
import json
from typing import Any

from . import interaction_closure_legacy as _legacy
from .closure_continuity import audit_translational_continuity
from .natural_form_atlas import (
    derive_glued_ui_subatlas,
    derive_versioned_natural_form_atlas,
    validate_versioned_natural_form_atlas,
)

PROTOCOL = _legacy.PROTOCOL
SCHEMA = _legacy.SCHEMA


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


def derive_interaction_closure(
    *,
    truth_derivation: dict[str, Any],
    nrrf843_ui: dict[str, Any],
    nrrf842_journey: dict[str, Any],
    coordination: dict[str, Any],
    ai_translation: dict[str, Any],
    tokenomic: dict[str, Any],
    visual_network: dict[str, Any],
    black_mirror: dict[str, Any],
    network_return: dict[str, Any],
) -> dict[str, Any]:
    """Derive one closure plus the versioned atlas it inhabits.

    Equality remains authored only by the legacy source-preserving interactive
    translation kernel.  The atlas never upgrades resemblance, shared names, or
    historical lineage into equality.  Cross-form identification is WITNESSED
    only when a returned translation explicitly preserves source, closure, and
    return; otherwise the relation remains OPEN.
    """

    body = _legacy.derive_interaction_closure(
        truth_derivation=truth_derivation,
        nrrf843_ui=nrrf843_ui,
        nrrf842_journey=nrrf842_journey,
        coordination=coordination,
        ai_translation=ai_translation,
        tokenomic=tokenomic,
        visual_network=visual_network,
        black_mirror=black_mirror,
        network_return=network_return,
    )
    legacy_interaction_closure_id = body.get("id")
    interactive_translation = body.get("interactive_translation") or {}
    topology = body.get("black_mirror_physical_topology") or {}
    atlas = derive_versioned_natural_form_atlas(
        truth_derivation=truth_derivation,
        interactive_translation=interactive_translation,
        active_perspective_id=topology.get("active_perspective_id"),
        active_reading=topology.get("projection_reading") or {},
        additional_translation_sources=(
            nrrf843_ui,
            nrrf842_journey,
            coordination,
            ai_translation,
            tokenomic,
            black_mirror,
            network_return,
        ),
    )
    atlas_validation = validate_versioned_natural_form_atlas(atlas)
    glued = derive_glued_ui_subatlas(atlas)

    body["natural_form_atlas"] = atlas
    body["natural_form_atlas_validation"] = atlas_validation
    body["glued_ui_subatlas"] = glued

    physical_topology = dict(body.get("black_mirror_physical_topology") or {})
    physical_topology.update(
        {
            "atlas_id": atlas["id"],
            "atlas_chart_role": "CURRENT_BALL_LIGHT_CONE_PROJECTION",
            "is_one_natural_form_chart": True,
            "is_master_ontology": False,
            "historical_forms_replaced_by_ball": False,
        }
    )
    body["black_mirror_physical_topology"] = physical_topology

    constraint = dict(body.get("unification_constraint") or {})
    constraint.update(
        {
            "natural_form_atlas_valid": atlas_validation["valid"],
            "natural_forms_flattened_into_synonyms": False,
            "cross_form_equality_requires_returned_translation": True,
            "open_cross_form_relations_preserved": True,
            "closure_ball_is_master_container": False,
        }
    )
    body["unification_constraint"] = constraint

    claims = dict(body.get("claims") or {})
    claims.update(
        {
            "closure_ball_is_master_container": False,
            "historical_natural_forms_collapsed": False,
            "visual_resemblance_witnesses_cross_form_equality": False,
            "shared_name_witnesses_cross_form_equality": False,
            "atlas_is_empirical_truth_claim": False,
        }
    )
    body["claims"] = claims

    body["continuity_self_audit"] = audit_translational_continuity(body)
    body["id"] = _digest(
        "interaction-closure-atlas",
        {
            "legacy_interaction_closure_id": legacy_interaction_closure_id,
            "translational_truth_id": body.get("translational_truth_id"),
            "interactive_translation_id": interactive_translation.get("id"),
            "natural_form_atlas_id": atlas["id"],
            "glued_ui_subatlas_id": glued["id"],
            "continuity_self_audit": body["continuity_self_audit"]["status"],
        },
    )
    return body


__all__ = ["PROTOCOL", "SCHEMA", "derive_interaction_closure"]
