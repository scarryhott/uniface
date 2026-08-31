from __future__ import annotations

"""Final non-collapse closure certificate for the executable Supernet.

Supernet closure is not the claim that every OPEN relation has been resolved or
that every historical chart has executable geometry.  It is the stronger
structural invariant requested by the natural-form atlas:

* every known/versioned natural form remains present;
* no historical distinction is silently identified;
* every asserted non-identity equality is return-witnessed;
* every unwitnessed relation remains OPEN;
* the formal Lean corpus is indexed against the same atlas without being
  re-proved or promoted into visual resemblance;
* the UI is the derived glue of the compatible sub-atlas.

The historical archive audit remains useful diagnostics but cannot gate this
closure certificate.
"""

import hashlib
import json
from typing import Any, Mapping

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS
from .formal_proof_index import (
    derive_formal_proof_index,
    validate_formal_proof_index,
)
from .natural_form_atlas import (
    HAIR_VERSIONS,
    derive_glued_ui_subatlas,
    historical_charts,
    validate_versioned_natural_form_atlas,
)

PROTOCOL = "SUPERNET-PROOF-INDEXED-CLOSURE"
SCHEMA = "closure.supernet/proof-indexed-closure-certificate-v1"


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


def _relation_witness_checks(atlas: Mapping[str, Any]) -> dict[str, Any]:
    witnessed_nonidentity: list[str] = []
    open_relations: list[str] = []
    invalid_witnesses: list[str] = []
    open_executing_as_equality: list[str] = []
    for raw in atlas.get("translations", []):
        if not isinstance(raw, Mapping):
            continue
        relation_id = str(raw.get("id") or "")
        kind = str(raw.get("kind") or "")
        status = raw.get("status")
        if kind == "IDENTITY":
            continue
        if status == WITNESSED_STATUS:
            witnessed_nonidentity.append(relation_id)
            source_ids = [
                str(item)
                for item in raw.get("source_return_ids", [])
                if item is not None and str(item)
            ]
            if not (
                source_ids
                and raw.get("source_preserved") is True
                and raw.get("closure_commutes") is True
                and raw.get("return_preserved") is True
            ):
                invalid_witnesses.append(relation_id)
        elif status == OPEN_STATUS:
            open_relations.append(relation_id)
            if raw.get("executes_as_equality") is True:
                open_executing_as_equality.append(relation_id)
    return {
        "witnessed_nonidentity_translation_ids": witnessed_nonidentity,
        "open_translation_ids": open_relations,
        "invalid_witnessed_translation_ids": invalid_witnesses,
        "open_relations_executing_as_equality": open_executing_as_equality,
        "every_asserted_nonidentity_equality_return_witnessed": not invalid_witnesses,
        "every_unwitnessed_relation_remains_open": not open_executing_as_equality,
    }


def _runtime_chart_checks(atlas: Mapping[str, Any]) -> dict[str, Any]:
    mapping = {
        str(key): str(value)
        for key, value in dict(atlas.get("runtime_state_to_chart", {})).items()
    }
    runtime_charts = [
        chart
        for chart in atlas.get("charts", [])
        if isinstance(chart, Mapping) and chart.get("runtime_generated") is True
    ]
    orphan_states: list[str] = []
    for chart in runtime_charts:
        chart_id = str(chart.get("id") or "")
        for state_id in chart.get("member_state_ids", []):
            state = str(state_id)
            if mapping.get(state) != chart_id:
                orphan_states.append(state)
    return {
        "runtime_chart_count": len(runtime_charts),
        "orphan_runtime_state_ids": sorted(set(orphan_states)),
        "every_runtime_state_has_one_atlas_chart": not orphan_states,
    }


def derive_supernet_closure_certificate(
    *,
    atlas: Mapping[str, Any],
    formal_proof_index: Mapping[str, Any] | None = None,
    ui_contract: Mapping[str, Any] | None = None,
    interaction_closure: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    atlas_validation = validate_versioned_natural_form_atlas(atlas)
    proof_index = (
        dict(formal_proof_index)
        if isinstance(formal_proof_index, Mapping)
        else derive_formal_proof_index(atlas)
    )
    proof_validation = validate_formal_proof_index(proof_index, atlas=atlas)

    expected_historical = historical_charts()
    expected_ids = {str(chart["id"]) for chart in expected_historical}
    actual_charts = [
        chart
        for chart in atlas.get("charts", [])
        if isinstance(chart, Mapping) and chart.get("id")
    ]
    actual_ids = {str(chart["id"]) for chart in actual_charts}
    missing_known_chart_ids = sorted(expected_ids - actual_ids)
    expected_families = {str(chart["family"]) for chart in expected_historical}
    actual_families = {str(chart.get("family") or "") for chart in actual_charts}
    missing_families = sorted(expected_families - actual_families)

    hair_ids = {
        str(chart["id"])
        for chart in actual_charts
        if chart.get("name") == "hair"
    }
    expected_hair_ids = {f"nf:hair:v{item['version']}" for item in HAIR_VERSIONS}
    hair_history_preserved = expected_hair_ids.issubset(hair_ids)

    relation_checks = _relation_witness_checks(atlas)
    runtime_checks = _runtime_chart_checks(atlas)
    expected_glue = derive_glued_ui_subatlas(atlas)

    ui_supplied = isinstance(ui_contract, Mapping)
    if ui_supplied:
        ui_atlas_matches = (
            isinstance(ui_contract.get("natural_form_atlas"), Mapping)
            and ui_contract["natural_form_atlas"].get("id") == atlas.get("id")
        )
        ui_glue_matches = ui_contract.get("glued_ui_subatlas") == expected_glue
        ui_single_final_form = bool(
            (ui_contract.get("atlas_semantics") or {}).get(
                "single_final_form_selected"
            )
        )
    else:
        ui_atlas_matches = True
        ui_glue_matches = True
        ui_single_final_form = False

    interaction_supplied = isinstance(interaction_closure, Mapping)
    if interaction_supplied:
        interaction_atlas_matches = bool(
            isinstance(interaction_closure.get("natural_form_atlas"), Mapping)
            and interaction_closure["natural_form_atlas"].get("id")
            == atlas.get("id")
        )
        continuity = interaction_closure.get("continuity_self_audit")
        continuity_clean = bool(
            not isinstance(continuity, Mapping)
            or continuity.get("status") == WITNESSED_STATUS
        )
    else:
        interaction_atlas_matches = True
        continuity_clean = True

    checks = {
        "versioned_atlas_valid": atlas_validation.get("valid") is True,
        "all_known_natural_forms_retained": not missing_known_chart_ids,
        "all_known_natural_form_families_retained": not missing_families,
        "hair_semantic_lineage_retained": hair_history_preserved,
        "closure_ball_is_not_master_container": (
            atlas.get("closure_ball_is_master_container") is False
        ),
        "visual_resemblance_cannot_author_equality": (
            atlas.get("visual_resemblance_can_witness_equality") is False
        ),
        "shared_name_cannot_author_equality": (
            atlas.get("shared_name_can_witness_equality") is False
        ),
        "every_asserted_nonidentity_equality_return_witnessed": relation_checks[
            "every_asserted_nonidentity_equality_return_witnessed"
        ],
        "every_unwitnessed_relation_remains_open": relation_checks[
            "every_unwitnessed_relation_remains_open"
        ],
        "every_runtime_state_has_one_atlas_chart": runtime_checks[
            "every_runtime_state_has_one_atlas_chart"
        ],
        "formal_proof_index_closed": proof_validation.get("valid") is True,
        "formal_proofs_do_not_flatten_forms": all(
            item.get("cross_form_equality_authored") is False
            for item in proof_index.get("proofs", [])
            if isinstance(item, Mapping)
        ),
        "compatible_ui_glue_derivable": expected_glue.get("atlas_id")
        == atlas.get("id"),
        "ui_uses_same_atlas": ui_atlas_matches,
        "ui_is_exact_compatible_glue": ui_glue_matches,
        "ui_does_not_select_single_final_form": not ui_single_final_form,
        "interaction_uses_same_atlas": interaction_atlas_matches,
        "interaction_continuity_audit_clean": continuity_clean,
        "archive_audit_is_not_semantic_authority": True,
    }
    supernet_closed = all(checks.values())

    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "status": WITNESSED_STATUS if supernet_closed else OPEN_STATUS,
        "supernet_closed": supernet_closed,
        "closure_equation": (
            "SupernetCompleteAt(t) = retained(versioned natural forms) AND "
            "noSilentCollapse AND witnessed(asserted equalities) AND "
            "OPEN(unwitnessed relations) AND proofIndexed(formal core) AND "
            "UI=Glue(compatible subatlas)"
        ),
        "atlas_id": atlas.get("id"),
        "formal_proof_index_id": proof_index.get("id"),
        "glued_subatlas_id": expected_glue.get("id"),
        "checks": checks,
        "missing_known_chart_ids": missing_known_chart_ids,
        "missing_known_families": missing_families,
        "relation_witnesses": relation_checks,
        "runtime_chart_closure": runtime_checks,
        "known_form_authority": "VERSIONED_REMEMBERED_NATURAL_FORM_ATLAS",
        "formal_authority": "INDEXED_MACHINE_CHECKED_LEAN_CORPUS",
        "runtime_equality_authority": "SOURCE_PRESERVING_RETURNED_TRANSLATION",
        "unwitnessed_relation_authority": OPEN_STATUS,
        "archive_audit_required_for_supernet_closure": False,
        "archive_audit_is_diagnostic_only": True,
        "registered_historical_chart_must_be_executable_to_remain_in_atlas": False,
        "open_relation_breaks_supernet_closure": False,
        "open_relations_are_part_of_closure": True,
        "complete_does_not_mean_every_open_relation_resolved": True,
        "formal_proof_source_verified_by_runtime": False,
        "runtime_reproves_lean": False,
        "existence_closed": False,
        "dialectic_continuation_status": OPEN_STATUS,
        "truth_issued": False,
    }
    body["id"] = _digest("supernet-closure", body)
    return body


def validate_supernet_closure_certificate(
    certificate: Mapping[str, Any],
    *,
    atlas: Mapping[str, Any],
    formal_proof_index: Mapping[str, Any] | None = None,
    ui_contract: Mapping[str, Any] | None = None,
    interaction_closure: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    expected = derive_supernet_closure_certificate(
        atlas=atlas,
        formal_proof_index=formal_proof_index,
        ui_contract=ui_contract,
        interaction_closure=interaction_closure,
    )
    errors: list[str] = []
    if dict(certificate) != expected:
        errors.append("supernet-closure:not-derived")
    if expected.get("supernet_closed") is not True:
        errors.append("supernet-closure:open")
    return {
        "valid": not errors,
        "errors": errors,
        "supernet_closed": expected.get("supernet_closed") is True,
        "status": expected.get("status"),
        "archive_audit_required": False,
        "open_relations_are_part_of_closure": True,
    }


__all__ = [
    "PROTOCOL",
    "SCHEMA",
    "derive_supernet_closure_certificate",
    "validate_supernet_closure_certificate",
]
