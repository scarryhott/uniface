from __future__ import annotations

"""Atlas-aware closure UI contract.

The previous contract remains the finite closure renderer and verification
kernel. This wrapper changes the semantic carrier: the rendered ball/fibre
projection is a locally compatible chart inside a versioned natural-form atlas.
The UI receipt therefore carries the glued compatible sub-atlas and preserves
OPEN chart translations without promoting historical resemblance to equality.
"""

from typing import Any, Mapping

from . import closure_ui_contract_legacy as _legacy
from .natural_form_atlas import (
    UI_PROTOCOL as ATLAS_UI_PROTOCOL,
    derive_glued_ui_subatlas,
    derive_versioned_natural_form_atlas,
    validate_versioned_natural_form_atlas,
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
    body.pop("id", None)
    body["natural_form_atlas"] = dict(atlas)
    body["glued_ui_subatlas"] = derive_glued_ui_subatlas(atlas)
    body["atlas_semantics"] = {
        "ui_is_locally_glued_atlas": True,
        "edge_is_ongoing_view_transport": True,
        "natural_form_selector_returns_compatible_subatlas": True,
        "single_final_form_selected": False,
        "closure_ball_is_master_container": False,
        "historical_form_meaning_may_be_replaced_without_return": False,
        "cross_form_equality_requires_source_preserving_return": True,
        "open_cross_form_relations_remain_navigable": True,
        "atlas_ui_protocol": ATLAS_UI_PROTOCOL,
        "truth_issued": False,
    }
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
        and semantics.get("truth_issued") is False
    )
    atlas_errors = list(atlas_validation.get("errors", []))
    if not glue_matches:
        atlas_errors.append("atlas-ui:glue-mismatch")
    if not semantics_valid:
        atlas_errors.append("atlas-ui:semantics")
    legacy["natural_form_atlas_valid"] = bool(atlas_validation.get("valid"))
    legacy["glued_ui_subatlas_matches_atlas"] = glue_matches
    legacy["interface_is_glued_versioned_subatlas"] = bool(
        atlas_validation.get("valid") and glue_matches and semantics_valid
    )
    legacy["closure_ball_is_master_container"] = False
    legacy["cross_form_equality_requires_source_preserving_return"] = True
    legacy["atlas_errors"] = atlas_errors
    legacy["valid"] = bool(
        legacy.get("valid")
        and atlas_validation.get("valid")
        and glue_matches
        and semantics_valid
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
