from __future__ import annotations

"""Atlas-preserving, proof-indexed Supernet interaction closure.

The observer-observed translation kernel remains authoritative for runtime
cross-form equality.  The versioned atlas preserves every known historical
natural form without flattening it, while the formal proof index records the
Lean-proved chart families and invariants that constrain the same translation.
OPEN relations remain inside closure rather than counting as missing truth.
"""

import hashlib
import json
from typing import Any

from . import interaction_closure_legacy as _legacy
from .closure_continuity import audit_translational_continuity
from .formal_proof_index import derive_formal_proof_index
from .natural_form_atlas import (
    derive_glued_ui_subatlas,
    derive_versioned_natural_form_atlas,
    validate_versioned_natural_form_atlas,
)
from .supernet_closure_certificate import derive_supernet_closure_certificate

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
    """Derive one runtime closure inside the complete proof-indexed atlas."""

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
    proof_index = derive_formal_proof_index(atlas)

    body["natural_form_atlas"] = atlas
    body["natural_form_atlas_validation"] = atlas_validation
    body["glued_ui_subatlas"] = glued
    body["formal_proof_index"] = proof_index

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
            "formal_proof_index_closed": proof_index["proof_index_closed"],
            "archive_audit_gates_supernet_closure": False,
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
            "lean_source_verified_by_runtime": False,
            "runtime_reproves_lean": False,
        }
    )
    body["claims"] = claims

    # Audit first so the closure certificate can bind the current continuity
    # status.  The certificate contains no forbidden external-authority flag, so
    # the second audit below must remain the same status.
    body["continuity_self_audit"] = audit_translational_continuity(body)
    certificate = derive_supernet_closure_certificate(
        atlas=atlas,
        formal_proof_index=proof_index,
        interaction_closure=body,
    )
    body["supernet_closure_certificate"] = certificate

    constraint["proof_indexed_supernet_closed"] = certificate["supernet_closed"]
    body["unification_constraint"] = constraint
    claims["supernet_closed_by_proof_indexed_translation"] = certificate[
        "supernet_closed"
    ]
    body["claims"] = claims
    final_audit = audit_translational_continuity(body)
    if final_audit["status"] != body["continuity_self_audit"]["status"]:
        raise RuntimeError("proof-indexed closure changed translational continuity")
    body["continuity_self_audit"] = final_audit

    body["id"] = _digest(
        "interaction-closure-atlas",
        {
            "legacy_interaction_closure_id": legacy_interaction_closure_id,
            "translational_truth_id": body.get("translational_truth_id"),
            "interactive_translation_id": interactive_translation.get("id"),
            "natural_form_atlas_id": atlas["id"],
            "glued_ui_subatlas_id": glued["id"],
            "formal_proof_index_id": proof_index["id"],
            "supernet_closure_certificate_id": certificate["id"],
            "continuity_self_audit": body["continuity_self_audit"]["status"],
        },
    )
    return body


__all__ = ["PROTOCOL", "SCHEMA", "derive_interaction_closure"]
