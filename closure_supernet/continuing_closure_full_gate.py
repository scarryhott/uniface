from __future__ import annotations

"""Full Supernet gate with continuation, not OPEN, as the published ontology."""

from typing import Any, Mapping

from . import equal_user_token_visual_identification as _v4_gate
from .continuing_translation_closure import (
    attach_continuing_translation_closure,
    derive_continuing_translation_closure,
)
from .translation_supervisory_full_gate import source_perspective_registry

PROTOCOL = "SUPERNET-CONTINUING-CLOSURE-FULL-GATE"
SCHEMA = "closure.supernet/continuing-closure-full-gate-v1"


def derive_full_supernet_gate_contract(
    closure_contract: Mapping[str, Any],
    *,
    navigation_context: Mapping[str, Any] | None = None,
    source_perspective_by_event: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    predecessor = _v4_gate.derive_full_supernet_gate_contract(
        closure_contract,
        navigation_context=navigation_context,
        source_perspective_by_event=(
            source_perspective_registry()
            if source_perspective_by_event is None
            else source_perspective_by_event
        ),
    )
    full = attach_continuing_translation_closure(predecessor)
    full.pop("id", None)
    full["protocol"] = PROTOCOL
    full["schema"] = SCHEMA
    full["legacy_status_vocabulary_is_compatibility_only"] = True
    full["published_relation_states"] = ["RETURNED", "CONTINUING"]
    full["nonreturned_does_not_mean_outside_closure"] = True
    full["id"] = _v4_gate._base._digest("full-supernet-potential-gate", full)
    return full


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
            "errors": ["continuing-closure-full-gate:closure-contract-missing"],
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
        errors.append("continuing-closure-full-gate:not-derived")

    predecessor = _v4_gate.derive_full_supernet_gate_contract(
        closure_contract,
        navigation_context=(
            navigation_context if isinstance(navigation_context, Mapping) else None
        ),
        source_perspective_by_event=provenance,
    )
    predecessor_validation = _v4_gate.validate_full_supernet_gate_contract(predecessor)
    if predecessor_validation.get("valid") is not True:
        errors.extend(predecessor_validation.get("errors", []))

    gate = expected.get("relative_natural_form_potential_gate")
    gate = gate if isinstance(gate, Mapping) else {}
    continuum = gate.get("continuing_translation_closure")
    if not isinstance(continuum, Mapping):
        errors.append("continuing-closure-full-gate:continuum-missing")
    else:
        expected_continuum = derive_continuing_translation_closure(predecessor)
        if dict(continuum) != expected_continuum:
            errors.append("continuing-closure-full-gate:continuum-not-derived")
        if continuum.get("continuation_is_inside_closure") is not True:
            errors.append("continuing-closure-full-gate:continuation-outside")
        if continuum.get("returned_is_determination_not_membership") is not True:
            errors.append("continuing-closure-full-gate:return-membership-confusion")
        relation_ids = {
            str(row.get("id"))
            for row in continuum.get("relations", [])
            if isinstance(row, Mapping) and row.get("id")
        }
        partition_ids = set(continuum.get("returned_relation_ids", [])) | set(
            continuum.get("continuing_relation_ids", [])
        )
        if relation_ids != partition_ids:
            errors.append("continuing-closure-full-gate:relation-partition-incomplete")
        if set(continuum.get("returned_relation_ids", [])) & set(
            continuum.get("continuing_relation_ids", [])
        ):
            errors.append("continuing-closure-full-gate:relation-state-overlap")

    if expected.get("published_relation_states") != ["RETURNED", "CONTINUING"]:
        errors.append("continuing-closure-full-gate:published-status-regression")
    if expected.get("legacy_status_vocabulary_is_compatibility_only") is not True:
        errors.append("continuing-closure-full-gate:legacy-status-authority")
    return {
        "valid": not errors,
        "errors": errors,
        "id": expected.get("id"),
        "continuing_translation_closure_id": expected.get(
            "continuing_translation_closure_id"
        ),
        "returned_relation_count": (
            continuum.get("returned_relation_count", 0)
            if isinstance(continuum, Mapping)
            else 0
        ),
        "continuing_relation_count": (
            continuum.get("continuing_relation_count", 0)
            if isinstance(continuum, Mapping)
            else 0
        ),
    }


__all__ = [
    "PROTOCOL",
    "SCHEMA",
    "derive_full_supernet_gate_contract",
    "validate_full_supernet_gate_contract",
]
