from __future__ import annotations

"""Local natural-form freedom derived from the proof-indexed Supernet atlas.

Every retained natural-form family is locally admissible as a *proposal* for
interaction.  Only the currently compatible returned sub-atlas is witnessed at
this perspective.  All other families remain OPEN interaction possibilities;
selecting one never authors equality.

Fidelity is not a configured score.  It is the exact current return/partition
profile of the atlas.  Over successive source-preserving returns the content-
addressed local field may expand, contract, or transform.  A later return may
resolve an OPEN frontier, but future resolution is never guaranteed.
"""

import hashlib
import json
from typing import Any, Iterable, Mapping

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS
from .natural_form_atlas import STATIC_FAMILIES

PROTOCOL = "SUPERNET-LOCAL-NATURAL-FORM-FREEDOM"
SCHEMA = "closure.supernet/local-natural-form-freedom-v1"


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


def _unique(values: Iterable[Any]) -> list[str]:
    return list(
        dict.fromkeys(
            str(value)
            for value in values
            if value is not None and str(value)
        )
    )


def _rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, (list, tuple)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def derive_local_natural_form_freedom(
    atlas: Mapping[str, Any],
) -> dict[str, Any]:
    """Derive the complete local proposal field from one versioned atlas."""

    charts = [dict(row) for row in _rows(atlas.get("charts")) if row.get("id")]
    translations = [
        dict(row) for row in _rows(atlas.get("translations")) if row.get("id")
    ]
    chart_by_id = {str(chart["id"]): chart for chart in charts}

    compatible = atlas.get("compatible_subatlas")
    compatible = compatible if isinstance(compatible, Mapping) else {}
    compatible_ids = set(_unique(compatible.get("chart_ids", [])))
    open_boundary_ids = set(
        _unique(compatible.get("open_boundary_translation_ids", []))
    )
    relation_by_id = {
        str(relation["id"]): relation for relation in translations
    }

    open_boundary_chart_ids: set[str] = set()
    for relation_id in open_boundary_ids:
        relation = relation_by_id.get(relation_id)
        if relation is None or relation.get("status") != OPEN_STATUS:
            continue
        for key in ("source_chart_id", "target_chart_id"):
            chart_id = str(relation.get(key) or "")
            if chart_id in chart_by_id:
                open_boundary_chart_ids.add(chart_id)

    family_names = sorted(
        {
            str(chart.get("family") or "")
            for chart in charts
            if str(chart.get("family") or "")
        }
    )
    required_historical_families = sorted(STATIC_FAMILIES)

    family_rows: list[dict[str, Any]] = []
    witnessed_family_ids: list[str] = []
    open_family_ids: list[str] = []
    empirical_family_ids: list[str] = []

    for family in family_names:
        family_charts = [
            chart for chart in charts if str(chart.get("family") or "") == family
        ]
        family_chart_ids = sorted(str(chart["id"]) for chart in family_charts)
        compatible_chart_ids = sorted(
            chart_id for chart_id in family_chart_ids if chart_id in compatible_ids
        )
        boundary_chart_ids = sorted(
            chart_id
            for chart_id in family_chart_ids
            if chart_id in open_boundary_chart_ids
        )
        empirical_required = any(
            chart.get("empirical_return_required") is True for chart in family_charts
        )
        witnessed = bool(compatible_chart_ids)
        status = WITNESSED_STATUS if witnessed else OPEN_STATUS
        if witnessed:
            witnessed_family_ids.append(family)
        else:
            open_family_ids.append(family)
        if empirical_required:
            empirical_family_ids.append(family)

        family_rows.append(
            {
                "family": family,
                "status": status,
                "chart_ids": family_chart_ids,
                "compatible_chart_ids": compatible_chart_ids,
                "open_boundary_chart_ids": boundary_chart_ids,
                "local_admissibility": (
                    "CURRENT_RETURNED_COMPATIBLE_FAMILY"
                    if witnessed
                    else (
                        "OPEN_EMPIRICAL_RETURN_CANDIDATE"
                        if empirical_required
                        else "OPEN_SOURCE_PRESERVING_RETURN_CANDIDATE"
                    )
                ),
                "selectable_as_interaction_proposal": True,
                "selection_executes_as_equality": False,
                "return_required_to_change_truth": True,
                "empirical_return_required": empirical_required,
            }
        )

    witnessed_nonidentity = [
        relation
        for relation in translations
        if relation.get("kind") != "IDENTITY"
        and relation.get("status") == WITNESSED_STATUS
    ]
    open_relations = [
        relation
        for relation in translations
        if relation.get("kind") != "IDENTITY"
        and relation.get("status") == OPEN_STATUS
    ]
    runtime_charts = [
        chart for chart in charts if chart.get("runtime_generated") is True
    ]

    returned_source_ids = _unique(
        [
            source_id
            for chart in runtime_charts
            for source_id in chart.get("source_return_ids", [])
        ]
        + [
            source_id
            for relation in witnessed_nonidentity
            for source_id in relation.get("source_return_ids", [])
        ]
    )
    runtime_state_ids = sorted(
        {
            str(state_id)
            for chart in runtime_charts
            for state_id in chart.get("member_state_ids", [])
            if state_id is not None and str(state_id)
        }
    )

    fidelity_profile = {
        "kind": "EXACT_RETURN_PARTITION_PROFILE",
        "interaction_time_coordinate": len(returned_source_ids),
        "returned_source_count": len(returned_source_ids),
        "returned_source_ids": returned_source_ids,
        "runtime_state_count": len(runtime_state_ids),
        "runtime_chart_count": len(runtime_charts),
        "closure_distinction_count": len(runtime_charts),
        "witnessed_nonidentity_translation_count": len(witnessed_nonidentity),
        "open_nonidentity_translation_count": len(open_relations),
        "configured_threshold": None,
        "similarity_epsilon": None,
        "scalar_fidelity_score": None,
        "fidelity_authored_only_by_exact_returns": True,
    }

    missing_required_families = sorted(
        set(required_historical_families) - set(family_names)
    )
    selection_freedom = {
        "admissible_family_ids": family_names,
        "witnessed_family_ids": sorted(witnessed_family_ids),
        "open_family_ids": sorted(open_family_ids),
        "empirical_return_family_ids": sorted(empirical_family_ids),
        "open_translation_frontier_ids": sorted(
            str(relation["id"]) for relation in open_relations
        ),
        "selection_is_set_valued": True,
        "selection_filters_families": False,
        "developer_menu_authors_selection": False,
        "external_limit_authors_selection": False,
        "configured_threshold_authors_selection": False,
        "missing_evidence_widens_truth": False,
        "remaining_limits_are_open_selection_frontiers": True,
        "later_return_may_resolve_open_frontier": True,
        "later_return_may_expand_contract_or_transform_freedom": True,
        "future_resolution_guaranteed": False,
    }

    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "status": WITNESSED_STATUS if not missing_required_families else OPEN_STATUS,
        "atlas_id": atlas.get("id"),
        "active_perspective_id": atlas.get("active_perspective_id"),
        "families": family_rows,
        "local_constraint": {
            "kind": "ALL_RETAINED_FAMILIES_AS_LOCAL_INTERACTION_PROPOSALS",
            "required_historical_family_ids": required_historical_families,
            "missing_required_historical_family_ids": missing_required_families,
            "all_retained_families_locally_admissible_as_proposals": not missing_required_families,
            "only_compatible_subatlas_is_currently_witnessed": True,
            "unwitnessed_family_selection_authors_truth": False,
            "cross_form_equality_still_requires_returned_translation": True,
        },
        "fidelity_profile": fidelity_profile,
        "selection_freedom": selection_freedom,
        "evolution_law": (
            "F_(t+1)=Close(F_t + SourcePreservingReturnedFidelity_t); "
            "OPEN remains OPEN until discriminating return"
        ),
        "recognition_equals_selection": True,
        "interaction_precedes_return": True,
        "return_precedes_truth_refinement": True,
        "truth_issued": False,
        "existence_closed": False,
    }
    body["id"] = _digest("local-natural-form-freedom", body)
    return body


def validate_local_natural_form_freedom(
    field: Mapping[str, Any],
    *,
    atlas: Mapping[str, Any],
) -> dict[str, Any]:
    expected = derive_local_natural_form_freedom(atlas)
    errors: list[str] = []
    if dict(field) != expected:
        errors.append("local-natural-form-freedom:not-derived")
    local = expected.get("local_constraint") or {}
    freedom = expected.get("selection_freedom") or {}
    fidelity = expected.get("fidelity_profile") or {}
    if local.get("all_retained_families_locally_admissible_as_proposals") is not True:
        errors.append("local-natural-form-freedom:missing-family")
    if local.get("unwitnessed_family_selection_authors_truth") is not False:
        errors.append("local-natural-form-freedom:selection-authors-truth")
    if freedom.get("selection_is_set_valued") is not True:
        errors.append("local-natural-form-freedom:not-set-valued")
    if freedom.get("future_resolution_guaranteed") is not False:
        errors.append("local-natural-form-freedom:guaranteed-convergence")
    if fidelity.get("configured_threshold") is not None:
        errors.append("local-natural-form-freedom:configured-threshold")
    if fidelity.get("fidelity_authored_only_by_exact_returns") is not True:
        errors.append("local-natural-form-freedom:fidelity-authority")
    return {
        "valid": not errors,
        "errors": errors,
        "status": expected.get("status"),
        "family_count": len(expected.get("families", [])),
        "returned_source_count": fidelity.get("returned_source_count", 0),
        "all_retained_families_locally_admissible_as_proposals": (
            local.get("all_retained_families_locally_admissible_as_proposals") is True
        ),
        "future_resolution_guaranteed": False,
    }


__all__ = [
    "PROTOCOL",
    "SCHEMA",
    "derive_local_natural_form_freedom",
    "validate_local_natural_form_freedom",
]
