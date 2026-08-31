from __future__ import annotations

"""Proof-indexed atlas-aware closure UI contract.

The finite renderer remains the existing closure/naturality evaluator. This
wrapper changes the semantic carrier to the complete versioned natural-form
atlas and seals every projection with the formal Lean proof index, the local
natural-form freedom field, the canonical interactive equality-closure
natural-form solver, and the final Supernet closure certificate. OPEN remains a
valid unresolved relation inside closure; it is not a missing subsystem or a
reason to invent a final form.
"""

from typing import Any, Mapping

from . import closure_ui_contract_legacy as _legacy
from .formal_proof_index import (
    derive_formal_proof_index,
    validate_formal_proof_index,
)
from .interactive_natural_form_solver import (
    derive_interactive_natural_form_solver,
    validate_interactive_natural_form_solver,
)
from .local_natural_form_freedom import (
    derive_local_natural_form_freedom,
    validate_local_natural_form_freedom,
)
from .natural_form_atlas import (
    UI_PROTOCOL as ATLAS_UI_PROTOCOL,
    derive_glued_ui_subatlas,
    derive_versioned_natural_form_atlas,
    validate_versioned_natural_form_atlas,
)
from .supernet_closure_certificate import (
    derive_supernet_closure_certificate,
    validate_supernet_closure_certificate,
)

PROTOCOL = _legacy.PROTOCOL
SCHEMA = _legacy.SCHEMA
BUILDER_VERSION = _legacy.BUILDER_VERSION
OPEN_STATUS = _legacy.OPEN_STATUS
BLOCKED_STATUS = _legacy.BLOCKED_STATUS
WITNESSED_STATUS = _legacy.WITNESSED_STATUS
RETURN_ENDPOINT_TEMPLATE = _legacy.RETURN_ENDPOINT_TEMPLATE
EXECUTION_ENDPOINT_TEMPLATE = _legacy.EXECUTION_ENDPOINT_TEMPLATE


def _empty_atlas(*, perspective_id: str | None) -> dict[str, Any]:
    return derive_versioned_natural_form_atlas(
        truth_derivation={},
        interactive_translation={},
        active_perspective_id=perspective_id,
        active_reading={},
    )


def _seal_with_atlas(
    contract: Mapping[str, Any],
    *,
    atlas: Mapping[str, Any],
) -> dict[str, Any]:
    body = dict(contract)
    for key in (
        "id",
        "formal_proof_index",
        "local_natural_form_freedom",
        "interactive_natural_form_solver",
        "supernet_closure_certificate",
    ):
        body.pop(key, None)
    body["natural_form_atlas"] = dict(atlas)
    body["glued_ui_subatlas"] = derive_glued_ui_subatlas(atlas)
    proof_index = derive_formal_proof_index(atlas)
    local_field = derive_local_natural_form_freedom(atlas)
    body["formal_proof_index"] = proof_index
    body["local_natural_form_freedom"] = local_field
    solver = derive_interactive_natural_form_solver(
        body,
        atlas=atlas,
        local_field=local_field,
    )
    body["interactive_natural_form_solver"] = solver
    body["atlas_semantics"] = {
        "ui_is_locally_glued_atlas": True,
        "edge_is_ongoing_view_transport": True,
        "natural_form_selector_returns_compatible_subatlas": True,
        "single_final_form_selected": False,
        "closure_ball_is_master_container": False,
        "historical_form_meaning_may_be_replaced_without_return": False,
        "cross_form_equality_requires_source_preserving_return": True,
        "open_cross_form_relations_remain_navigable": True,
        "formal_proof_index_required": True,
        "local_natural_form_freedom_required": True,
        "interactive_natural_form_solver_required": True,
        "natural_forms_derived_from_interactive_equality_closure": True,
        "natural_form_is_posthoc_visual_template": False,
        "named_geometry_templates_present": False,
        "family_name_authors_geometry": False,
        "rendering_can_witness_equality": False,
        "all_retained_families_are_local_interaction_proposals": True,
        "selection_authors_truth": False,
        "fidelity_is_exact_return_partition_profile": True,
        "future_resolution_guaranteed": False,
        "archive_audit_gates_supernet_closure": False,
        "open_relation_breaks_supernet_closure": False,
        "atlas_ui_protocol": ATLAS_UI_PROTOCOL,
        "truth_issued": False,
    }
    certificate = derive_supernet_closure_certificate(
        atlas=atlas,
        formal_proof_index=proof_index,
        ui_contract=body,
    )
    body["supernet_closure_certificate"] = certificate
    body["id"] = _legacy._digest("translational-visualization", body)
    return body


def derive_open_ui_contract(*, perspective_id: str | None = None) -> dict[str, Any]:
    contract = _legacy.derive_open_ui_contract(perspective_id=perspective_id)
    return _seal_with_atlas(
        contract,
        atlas=_empty_atlas(
            perspective_id=str(contract.get("perspective_id") or "") or None
        ),
    )


def derive_closure_ui_contract(
    *,
    truth_derivation: dict[str, Any],
    nrrf843_ui: dict[str, Any],
    nrrf842_journey: dict[str, Any],
    interaction_closure: dict[str, Any],
    coordination: dict[str, Any],
    visual_network: dict[str, Any],
    source_occurrences: list[dict[str, Any]],
    focus_event: dict[str, Any],
    field_event_seq: int | None = None,
) -> dict[str, Any]:
    contract = _legacy.derive_closure_ui_contract(
        truth_derivation=truth_derivation,
        nrrf843_ui=nrrf843_ui,
        nrrf842_journey=nrrf842_journey,
        interaction_closure=interaction_closure,
        coordination=coordination,
        visual_network=visual_network,
        source_occurrences=source_occurrences,
        focus_event=focus_event,
        field_event_seq=field_event_seq,
    )
    atlas = interaction_closure.get("natural_form_atlas")
    if not isinstance(atlas, Mapping):
        topology = interaction_closure.get("black_mirror_physical_topology") or {}
        atlas = derive_versioned_natural_form_atlas(
            truth_derivation=truth_derivation,
            interactive_translation=interaction_closure.get("interactive_translation") or {},
            active_perspective_id=contract.get("perspective_id"),
            active_reading=(topology.get("projection_reading") or {})
            if isinstance(topology, Mapping)
            else {},
            additional_translation_sources=(nrrf843_ui, nrrf842_journey, coordination),
        )
    return _seal_with_atlas(contract, atlas=atlas)


def attach_perspective_closure(
    contract: Mapping[str, Any],
    *,
    perspective_closure: Mapping[str, Any],
    continuation_index: int,
    continuation_lineage_ids=(),
) -> dict[str, Any]:
    updated = _legacy.attach_perspective_closure(
        contract,
        perspective_closure=perspective_closure,
        continuation_index=continuation_index,
        continuation_lineage_ids=continuation_lineage_ids,
    )
    atlas = updated.get("natural_form_atlas")
    if isinstance(atlas, Mapping):
        return _seal_with_atlas(updated, atlas=atlas)
    return updated


def validate_ui_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    legacy = dict(_legacy.validate_ui_contract(contract))
    atlas = contract.get("natural_form_atlas")
    atlas_validation = (
        validate_versioned_natural_form_atlas(atlas)
        if isinstance(atlas, Mapping)
        else {"valid": False, "errors": ["atlas:missing"]}
    )
    expected_glue = (
        derive_glued_ui_subatlas(atlas) if isinstance(atlas, Mapping) else None
    )
    glue_matches = bool(
        expected_glue is not None and contract.get("glued_ui_subatlas") == expected_glue
    )
    semantics = contract.get("atlas_semantics")
    semantics_valid = bool(
        isinstance(semantics, Mapping)
        and semantics.get("ui_is_locally_glued_atlas") is True
        and semantics.get("edge_is_ongoing_view_transport") is True
        and semantics.get("natural_form_selector_returns_compatible_subatlas") is True
        and semantics.get("single_final_form_selected") is False
        and semantics.get("closure_ball_is_master_container") is False
        and semantics.get("historical_form_meaning_may_be_replaced_without_return")
        is False
        and semantics.get("cross_form_equality_requires_source_preserving_return")
        is True
        and semantics.get("open_cross_form_relations_remain_navigable") is True
        and semantics.get("formal_proof_index_required") is True
        and semantics.get("local_natural_form_freedom_required") is True
        and semantics.get("interactive_natural_form_solver_required") is True
        and semantics.get("natural_forms_derived_from_interactive_equality_closure")
        is True
        and semantics.get("natural_form_is_posthoc_visual_template") is False
        and semantics.get("named_geometry_templates_present") is False
        and semantics.get("family_name_authors_geometry") is False
        and semantics.get("rendering_can_witness_equality") is False
        and semantics.get("all_retained_families_are_local_interaction_proposals")
        is True
        and semantics.get("selection_authors_truth") is False
        and semantics.get("fidelity_is_exact_return_partition_profile") is True
        and semantics.get("future_resolution_guaranteed") is False
        and semantics.get("archive_audit_gates_supernet_closure") is False
        and semantics.get("open_relation_breaks_supernet_closure") is False
        and semantics.get("truth_issued") is False
    )

    proof_index = contract.get("formal_proof_index")
    proof_validation = (
        validate_formal_proof_index(proof_index, atlas=atlas)
        if isinstance(proof_index, Mapping) and isinstance(atlas, Mapping)
        else {"valid": False, "errors": ["formal-proof-index:missing"]}
    )
    local_field = contract.get("local_natural_form_freedom")
    local_field_validation = (
        validate_local_natural_form_freedom(local_field, atlas=atlas)
        if isinstance(local_field, Mapping) and isinstance(atlas, Mapping)
        else {"valid": False, "errors": ["local-natural-form-freedom:missing"]}
    )
    solver = contract.get("interactive_natural_form_solver")
    solver_validation = (
        validate_interactive_natural_form_solver(
            solver,
            contract=contract,
            atlas=atlas,
            local_field=local_field,
        )
        if isinstance(solver, Mapping)
        and isinstance(atlas, Mapping)
        and isinstance(local_field, Mapping)
        else {"valid": False, "errors": ["interactive-natural-form-solver:missing"]}
    )
    certificate = contract.get("supernet_closure_certificate")
    certificate_validation = (
        validate_supernet_closure_certificate(
            certificate,
            atlas=atlas,
            formal_proof_index=proof_index,
            ui_contract=contract,
        )
        if isinstance(certificate, Mapping)
        and isinstance(atlas, Mapping)
        and isinstance(proof_index, Mapping)
        and isinstance(local_field, Mapping)
        and isinstance(solver, Mapping)
        else {"valid": False, "errors": ["supernet-closure:missing"]}
    )

    atlas_errors = list(atlas_validation.get("errors", []))
    if not glue_matches:
        atlas_errors.append("atlas-ui:glue-mismatch")
    if not semantics_valid:
        atlas_errors.append("atlas-ui:semantics")
    atlas_errors.extend(proof_validation.get("errors", []))
    atlas_errors.extend(local_field_validation.get("errors", []))
    atlas_errors.extend(solver_validation.get("errors", []))
    atlas_errors.extend(certificate_validation.get("errors", []))

    legacy["natural_form_atlas_valid"] = bool(atlas_validation.get("valid"))
    legacy["glued_ui_subatlas_matches_atlas"] = glue_matches
    legacy["formal_proof_index_valid"] = bool(proof_validation.get("valid"))
    legacy["local_natural_form_freedom_valid"] = bool(
        local_field_validation.get("valid")
    )
    legacy["interactive_natural_form_solver_valid"] = bool(
        solver_validation.get("valid")
    )
    legacy["natural_form_is_interactive_interface_equality_closure"] = bool(
        solver_validation.get(
            "natural_form_is_interactive_interface_equality_closure"
        )
    )
    legacy["rendering_can_witness_equality"] = False
    legacy["all_retained_families_locally_admissible_as_proposals"] = bool(
        local_field_validation.get(
            "all_retained_families_locally_admissible_as_proposals"
        )
    )
    legacy["future_resolution_guaranteed"] = False
    legacy["supernet_closure_certificate_valid"] = bool(
        certificate_validation.get("valid")
    )
    legacy["supernet_closed"] = bool(
        isinstance(certificate, Mapping) and certificate.get("supernet_closed") is True
    )
    legacy["interface_is_glued_versioned_subatlas"] = bool(
        atlas_validation.get("valid")
        and glue_matches
        and semantics_valid
        and proof_validation.get("valid")
        and local_field_validation.get("valid")
        and solver_validation.get("valid")
        and certificate_validation.get("valid")
    )
    legacy["closure_ball_is_master_container"] = False
    legacy["cross_form_equality_requires_source_preserving_return"] = True
    legacy["archive_audit_gates_supernet_closure"] = False
    legacy["open_relations_are_part_of_closure"] = True
    legacy["atlas_errors"] = atlas_errors
    legacy["valid"] = bool(
        legacy.get("valid")
        and atlas_validation.get("valid")
        and glue_matches
        and semantics_valid
        and proof_validation.get("valid")
        and local_field_validation.get("valid")
        and solver_validation.get("valid")
        and certificate_validation.get("valid")
    )
    return legacy


def __getattr__(name: str) -> Any:
    return getattr(_legacy, name)


__all__ = sorted(
    set(getattr(_legacy, "__all__", ()))
    | {
        "PROTOCOL",
        "SCHEMA",
        "BUILDER_VERSION",
        "OPEN_STATUS",
        "BLOCKED_STATUS",
        "WITNESSED_STATUS",
        "RETURN_ENDPOINT_TEMPLATE",
        "EXECUTION_ENDPOINT_TEMPLATE",
        "attach_perspective_closure",
        "derive_closure_ui_contract",
        "derive_open_ui_contract",
        "validate_ui_contract",
    }
)
