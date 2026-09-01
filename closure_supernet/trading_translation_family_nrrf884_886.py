from __future__ import annotations

"""NRRF884–886 trading-family projection.

A trading closure family is not support novelty and it is not a market-regime
predicate.  It is the structural visualization of returned natural-form
presentations that name one translational truth.  Runtime membership is therefore
derived from the already-computed ``closure_truth_id``; the projection does not
invent a new equality relation.

The module deliberately keeps three notions separate:

* family membership: equal translational truth / one natural form;
* support novelty: whether that truth class has been returned before;
* empirical profitability/no-profit hypotheses: properties of returned market
  geometry, never definitions of family unity.

This is a runtime correspondence layer for NRRF884/885/886.  Python does not
execute or re-prove the Lean kernel.
"""

import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

PROTOCOL = "closure.supernet/trading-translation-family-nrrf884-886-v1"
FORMAL_MODULES = (
    "NRRF884",
    "NRRF885ProofByVisualizationMetaphorEqualityCompleteRelationsAndTheCurrentsOfTheSlideAsVisualizationCrystalBalls",
    "NRRF886EqualityIsLocalMinimumAndGlobalMaximumToNaturalFormsOfAClosureFamilyAndTheUnfoldingFieldOfRelativePairs",
)


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def _common_value(rows: Sequence[Mapping[str, Any]], key: str) -> Any:
    values = [_stable(row.get(key)) for row in rows]
    if not values or any(value != values[0] for value in values[1:]):
        return None
    return rows[0].get(key)


def _family(rows: Sequence[Mapping[str, Any]], truth_id: str) -> dict[str, Any]:
    members = [dict(row) for row in rows]
    member_ids = sorted(str(row.get("form_id") or "") for row in members)
    common_signature = _common_value(members, "directed_relation_signature")
    common_curvature = _common_value(members, "unitary_curvature")
    common_profit = _common_value(members, "natural_profit")
    common_orientation = _common_value(members, "orientation")

    # The centre is an invariant family reading, not one arbitrarily preferred
    # presentation.  It contains only data common to every returned member.
    centre = {
        "closure_truth_id": truth_id,
        "directed_relation_signature": common_signature,
        "unitary_curvature": common_curvature,
        "natural_profit": common_profit,
        "orientation": common_orientation,
    }
    family_id = _digest(
        "translation-truth-family",
        {"closure_truth_id": truth_id, "member_ids": member_ids},
    )
    return {
        "family_id": family_id,
        "closure_truth_id": truth_id,
        "status": WITNESSED_STATUS,
        "members": members,
        "member_ids": member_ids,
        "member_count": len(members),
        "visualization": {
            "kind": "RELATIVE_VISUALIZATION_OF_SELECTED_NATURAL_FORMS",
            "member_ids": member_ids,
            "labels_author_truth": False,
            "presentation_multiplicity_authors_truth": False,
            "metaphor_equality_reading": "SAME_SEEN_TRANSLATIONAL_TRUTH",
        },
        "crystal_ball_current": {
            "kind": "TRANSLATION_FAMILY_CURRENT",
            "family_id": family_id,
            "natural_form_centre": centre,
            "centre_is_family_invariant_not_member_choice": True,
        },
        "natural_form_centre": centre,
        "all_members_selected": all(row.get("selected") is True for row in members),
        "family_wide_selection": True,
        "selection_is_family_visualization": True,
        "support_novelty_required_for_membership": False,
        "support_novelty_authors_selection": False,
        "same_class_return_remains_family_member": True,
        "fixed_price_no_profit_hypothesis_required_for_membership": False,
        "fixed_price_no_profit_hypothesis_authors_unity": False,
        "profitability_authors_membership": False,
        "profitable_and_costly_are_possible_properties_of_truth": True,
        "local_global_are_relative_readings_of_one_family": True,
        "family_name_authors_truth": False,
        "runtime_reproves_lean": False,
    }


def derive_translation_families(
    *,
    natural_form_field: Mapping[str, Any],
    translational_truth_partition: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Group returned presentations by the truth identity already derived upstream."""

    returned = [
        dict(row)
        for row in natural_form_field.get("returned_natural_forms", [])
        if row.get("returned_truth_member") is True
    ]
    by_truth: dict[str, list[dict[str, Any]]] = {}
    unresolved: list[dict[str, Any]] = []
    for row in returned:
        truth_id = str(row.get("closure_truth_id") or "")
        if not truth_id:
            unresolved.append(row)
            continue
        by_truth.setdefault(truth_id, []).append(row)

    families = [_family(rows, truth_id) for truth_id, rows in sorted(by_truth.items())]
    all_member_ids = {
        member_id
        for family in families
        for member_id in family["member_ids"]
    }
    returned_ids = {str(row.get("form_id") or "") for row in returned if row.get("form_id")}
    partition = dict(translational_truth_partition or {})

    body = {
        "protocol": PROTOCOL,
        "formal_modules": list(FORMAL_MODULES),
        "status": WITNESSED_STATUS if returned and not unresolved else OPEN_STATUS,
        "families": families,
        "family_count": len(families),
        "returned_member_count": len(returned),
        "unresolved_member_count": len(unresolved),
        "every_returned_member_visualized_once": bool(returned) and all_member_ids == returned_ids,
        "family_definition": "ONE_TRANSLATIONAL_TRUTH_RELATIVE_VISUALIZATION",
        "family_is_relative_visualization_of_selected_natural_forms": True,
        "family_is_support_novelty": False,
        "new_tt_class_means_trade": False,
        "same_tt_class_means_do_not_trade": False,
        "support_novelty_is_learning_coordinate_only": True,
        "fixed_price_subset_is_maximally_unified": False,
        "breaking_fixed_price_hypothesis_means_escape_from_closure": False,
        "fixed_price_no_profit_is_empirical_hypothesis_only": True,
        "profitability_is_property_not_family_definition": True,
        "local_global_are_relative_extrema_readings": True,
        "relative_pairs_share_one_unfolding_field": True,
        "translational_truth_partition_present": bool(partition),
        "lean_kernel_executed_by_runtime": False,
        "runtime_reproves_lean": False,
    }
    body["id"] = _digest("trading-translation-family-nrrf884-886", body)
    return body


__all__ = ["FORMAL_MODULES", "PROTOCOL", "derive_translation_families"]
