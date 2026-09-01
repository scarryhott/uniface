from __future__ import annotations

"""Continuous translation-field reading of the published Supernet closure.

Returned source events remain discrete semantic control points.  They do not
name separate visual worlds.  The browser carries one continuing translation
field through those control points; interpolation is presentation-only and may
never author truth, Seen equality, natural-form membership, or return status.
"""

from copy import deepcopy
from typing import Any, Mapping, Sequence

from . import visualization_metaphor_closure as _nrrf885
from . import full_supernet_potential_gate as _base

PROTOCOL = "SUPERNET-CONTINUOUS-TRANSLATION-FIELD"
SCHEMA = "closure.supernet/continuous-translation-field-v1"

_DERIVE_PREDECESSOR = _nrrf885.derive_full_supernet_gate_contract
_VALIDATE_PREDECESSOR = _nrrf885.validate_full_supernet_gate_contract


def _rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [row for row in value if isinstance(row, Mapping)]


def derive_continuous_translation_field(full_gate: Mapping[str, Any]) -> dict[str, Any]:
    gate = full_gate.get("relative_natural_form_potential_gate")
    gate = gate if isinstance(gate, Mapping) else {}
    continuum = gate.get("continuing_translation_closure")
    continuum = continuum if isinstance(continuum, Mapping) else {}
    metaphor = gate.get("visualization_metaphor_closure")
    metaphor = metaphor if isinstance(metaphor, Mapping) else {}

    relations = []
    current_by_path = {
        str(row.get("path_id")): row
        for row in _rows(metaphor.get("currents"))
        if row.get("path_id")
    }
    for relation in _rows(continuum.get("relations")):
        path_id = str(relation.get("path_id") or "")
        current = current_by_path.get(path_id, {})
        row = {
            "path_id": path_id,
            "closure_state": relation.get("closure_state"),
            "returned": relation.get("returned") is True,
            "continuing": relation.get("continuing") is True,
            "visualization_current_id": current.get("id"),
            "fold_class_id": current.get("fold_class_id"),
            "rotation_class_id": current.get("rotation_class_id"),
            "crystal_ball_id": current.get("crystal_ball_id"),
            "semantic_control_point": relation.get("returned") is True,
            "continuous_between_control_points": True,
            "interpolation_authors_truth": False,
            "interpolation_authors_seen": False,
            "interpolation_authors_return": False,
        }
        row["id"] = _base._digest("continuous-translation-current", row)
        relations.append(row)

    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "control_point_id": full_gate.get("id"),
        "seen_id": metaphor.get("seen_id"),
        "metaphor_class_id": metaphor.get("metaphor_class_id"),
        "continuing_translation_closure_id": continuum.get("id"),
        "visualization_metaphor_closure_id": metaphor.get("id"),
        "currents": relations,
        "current_count": len(relations),
        "persistent_visual_carrier": True,
        "returned_revisions_are_control_points_not_visual_worlds": True,
        "semantic_time_is_returned_event_order": True,
        "visual_translation_is_continuous_between_returns": True,
        "hair_is_continuous_self_location_coordinate": True,
        "zoom_is_continuous_local_global_coordinate": True,
        "perspective_transport_is_continuous_field_transport": True,
        "return_deforms_same_field": True,
        "renderer_replaces_closure": False,
        "interpolation_authors_truth": False,
        "interpolation_authors_seen": False,
        "interpolation_authors_natural_form": False,
        "interpolation_authors_return": False,
        "truth_issued": False,
        "existence_closed": False,
    }
    body["id"] = _base._digest("continuous-translation-field", body)
    return body


def _attach(full_gate: Mapping[str, Any]) -> dict[str, Any]:
    full = deepcopy(dict(full_gate))
    field = derive_continuous_translation_field(full)
    gate = deepcopy(dict(full["relative_natural_form_potential_gate"]))
    gate["continuous_translation_field"] = field
    gate["continuous_translation_field_id"] = field["id"]
    gate["persistent_visual_carrier"] = True
    gate["returned_revisions_are_control_points_not_visual_worlds"] = True
    gate.pop("id", None)
    gate["id"] = _base._digest("relative-natural-form-potential-gate", gate)

    full.pop("id", None)
    full["relative_natural_form_potential_gate"] = gate
    full["continuous_translation_field_id"] = field["id"]
    full["persistent_visual_carrier"] = True
    full["returned_revisions_are_control_points_not_visual_worlds"] = True
    full["visual_translation_is_continuous_between_returns"] = True
    full["potential_gate_natural_form_solver"] = _base.derive_potential_gate_natural_form_solver(full)
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
    return _attach(predecessor)


def validate_full_supernet_gate_contract(full_gate: Mapping[str, Any]) -> dict[str, Any]:
    closure_contract = full_gate.get("closure_ui_contract")
    navigation_context = full_gate.get("navigation_context")
    provenance = full_gate.get("source_perspective_by_event")
    provenance = provenance if isinstance(provenance, Mapping) else {}
    if not isinstance(closure_contract, Mapping):
        return {"valid": False, "errors": ["continuous-field:closure-contract-missing"]}

    expected = derive_full_supernet_gate_contract(
        closure_contract,
        navigation_context=(navigation_context if isinstance(navigation_context, Mapping) else None),
        source_perspective_by_event=provenance,
    )
    errors: list[str] = []
    if dict(full_gate) != expected:
        errors.append("continuous-field:not-derived")

    predecessor = _DERIVE_PREDECESSOR(
        closure_contract,
        navigation_context=(navigation_context if isinstance(navigation_context, Mapping) else None),
        source_perspective_by_event=provenance,
    )
    predecessor_validation = _VALIDATE_PREDECESSOR(predecessor)
    if predecessor_validation.get("valid") is not True:
        errors.extend(predecessor_validation.get("errors", []))

    gate = expected.get("relative_natural_form_potential_gate")
    gate = gate if isinstance(gate, Mapping) else {}
    field = gate.get("continuous_translation_field")
    if not isinstance(field, Mapping):
        errors.append("continuous-field:missing")
    else:
        expected_field = derive_continuous_translation_field(predecessor)
        if dict(field) != expected_field:
            errors.append("continuous-field:field-not-derived")
        if field.get("persistent_visual_carrier") is not True:
            errors.append("continuous-field:carrier-not-persistent")
        if field.get("returned_revisions_are_control_points_not_visual_worlds") is not True:
            errors.append("continuous-field:revision-is-world")
        for row in _rows(field.get("currents")):
            if row.get("continuous_between_control_points") is not True:
                errors.append(f"continuous-field:current-discrete:{row.get('path_id')}")
            if row.get("interpolation_authors_truth") is not False:
                errors.append(f"continuous-field:interpolation-authority:{row.get('path_id')}")

    return {
        "valid": not errors,
        "errors": errors,
        "id": expected.get("id"),
        "continuous_translation_field_id": expected.get("continuous_translation_field_id"),
        "current_count": field.get("current_count", 0) if isinstance(field, Mapping) else 0,
    }


__all__ = [
    "PROTOCOL",
    "SCHEMA",
    "derive_continuous_translation_field",
    "derive_full_supernet_gate_contract",
    "validate_full_supernet_gate_contract",
]
