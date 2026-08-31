from __future__ import annotations

"""NRRF874 runtime correspondence: OPEN-boundary natural selection.

This module does not add a predictive policy or a second selector. It derives the
learning-interaction support already implicit in translational truth:

    S_t                 = held translational-truth support
    d_OPEN(S_t)         = unresolved truth boundary
    NaturalSelect(S_t)  = the set of OPEN-boundary interactions
    S_(t+1)             = Close(S_t + returned truth)

Selection itself never changes support. A returned member of held support is a
hair re-presentation and leaves support fixed. A returned truth class outside
held support strictly widens the cumulative support. Profit is discovered only
when a returned truth class itself is profitable.

The runtime stays set-valued when several OPEN boundary interactions coexist.
Choosing one concrete member is deliberately left to any executor that factors
through the same truth classes; this layer introduces no absolute-value
selector, ranking, tolerance, forecast, or hidden tie-break policy.

NRRF873 horizon/ball frontiers and the unified field's relation-space OPEN forms
are promoted into one OPEN-boundary interaction support. Fairness and market
reachability remain hypotheses, not runtime claims.
"""

import hashlib
import json
from typing import Any, Mapping

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

PROTOCOL = "closure.supernet/trading-open-boundary-natural-selection-nrrf874-v1"


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


def _field_boundaries(natural_form_field: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in natural_form_field.get("open_natural_forms", []):
        form = dict(raw)
        projection = dict(form.get("action_projection") or {})
        if projection.get("status") != OPEN_STATUS or projection.get("requires_return") is not True:
            continue
        body = {
            "origin": "UNIFIED_NATURAL_FORM_FIELD",
            "form_kind": form.get("kind"),
            "source_token": form.get("source_token"),
            "target_token": form.get("target_token"),
            "closure_id": form.get("closure_id"),
            "projection_kind": projection.get("kind"),
        }
        rows.append(
            {
                "boundary_id": _digest("open-boundary", body),
                "status": OPEN_STATUS,
                "origin": body["origin"],
                "axis": "RELATION_SPACE",
                "form_id": form.get("form_id"),
                "form_kind": form.get("kind"),
                "closure_id": form.get("closure_id"),
                "source_token": form.get("source_token"),
                "target_token": form.get("target_token"),
                "interaction": projection,
                "truth_derived": True,
                "selection_authors_truth": False,
                "support_delta_on_selection": 0,
            }
        )
    return rows


def _freedom_boundaries(
    preaction_relative_coordinates: Mapping[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for closure_id, raw_coordinates in sorted(
        dict(preaction_relative_coordinates.get("by_closure_id", {})).items()
    ):
        coordinates = dict(raw_coordinates)
        freedom = dict(coordinates.get("selection_freedom") or {})
        for axis, field_name in (
            ("TEMPORAL_HAIR", "temporal_freedom"),
            ("RELATIVE_BALL", "ball_freedom"),
        ):
            axis_body = dict(freedom.get(field_name) or {})
            frontier = dict(axis_body.get("frontier") or {})
            if frontier.get("status") != OPEN_STATUS:
                continue
            boundary_body = {
                "origin": "NRRF873_SELECTION_FREEDOM",
                "axis": axis,
                "closure_id": closure_id,
                "closure_truth_id": freedom.get("closure_truth_id"),
                "kind": frontier.get("kind"),
                "next_return_step": frontier.get("next_return_step"),
                "current_upper_bound": frontier.get("current_upper_bound"),
                "unit": frontier.get("unit"),
            }
            interaction = {
                "kind": frontier.get("kind"),
                "status": OPEN_STATUS,
                "closure_id": closure_id,
                "axis": axis,
                "next_return_step": frontier.get("next_return_step"),
                "current_upper_bound": frontier.get("current_upper_bound"),
                "unit": frontier.get("unit"),
                "requires_return": True,
                "requires_source_preserving_return": True,
                "predicted_profit": None,
                "expected_value": None,
                "semantic_authority": False,
                "may_author_truth": False,
                "automatic_order_submission": False,
            }
            rows.append(
                {
                    "boundary_id": _digest("open-boundary", boundary_body),
                    "status": OPEN_STATUS,
                    "origin": boundary_body["origin"],
                    "axis": axis,
                    "form_id": None,
                    "form_kind": "OPEN_SELECTION_FREEDOM_FRONTIER",
                    "closure_id": closure_id,
                    "closure_truth_id": freedom.get("closure_truth_id"),
                    "source_token": None,
                    "target_token": None,
                    "interaction": interaction,
                    "truth_derived": True,
                    "selection_authors_truth": False,
                    "support_delta_on_selection": 0,
                }
            )
    return rows


def _support_evolution(
    translational_truth_partition: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if not translational_truth_partition:
        return {
            "status": OPEN_STATUS,
            "support_class_ids": [],
            "support_class_count": 0,
            "events": [],
            "strict_extension_count": 0,
            "hair_resampling_count": 0,
            "profitable_class_discovery_count": 0,
            "support_history_available": False,
            "support_is_monotone_under_return_closure": True,
        }

    support: set[str] = set()
    rows: list[dict[str, Any]] = []
    strict_extensions = 0
    hair_resamplings = 0
    profitable_discoveries = 0

    for raw in translational_truth_partition.get("learning_events", []):
        event = dict(raw)
        before = set(support)
        truth_class_id = event.get("truth_class_id")
        event_name = str(event.get("event") or "")
        if event_name == "NEW_TRANSLATIONAL_TRUTH_WITNESSED" and truth_class_id:
            support.add(str(truth_class_id))
            classification = "RETURN_OUTSIDE_SUPPORT_EXTENDS"
            strict_extensions += 1
            if event.get("profitable_truth_class") is True:
                profitable_discoveries += 1
        elif event_name == "SAME_TRANSLATIONAL_TRUTH_RETURNED" and truth_class_id:
            support.add(str(truth_class_id))
            classification = "RETURN_IN_SUPPORT_IS_HAIR"
            hair_resamplings += 1
        else:
            classification = "OPEN_OR_INERT_NO_SUPPORT_CHANGE"

        after = set(support)
        rows.append(
            {
                "frame_index": event.get("frame_index"),
                "form_index": event.get("form_index"),
                "status": event.get("status"),
                "truth_class_id": truth_class_id,
                "classification": classification,
                "support_before_count": len(before),
                "support_after_count": len(after),
                "strict_support_extension": len(after) > len(before),
                "support_fixed": after == before,
                "hair_return_of_known_truth": classification == "RETURN_IN_SUPPORT_IS_HAIR",
                "profitable_truth_class": event.get("profitable_truth_class") is True,
                "selection_authored_change": False,
                "returned_interaction_authored_change": len(after) > len(before),
            }
        )

    return {
        "status": WITNESSED_STATUS if support else OPEN_STATUS,
        "support_class_ids": sorted(support),
        "support_class_count": len(support),
        "events": rows,
        "strict_extension_count": strict_extensions,
        "hair_resampling_count": hair_resamplings,
        "profitable_class_discovery_count": profitable_discoveries,
        "support_history_available": True,
        "support_is_monotone_under_return_closure": True,
        "return_in_support_is_hair": True,
        "return_outside_support_strictly_extends": True,
        "profitability_is_truth_class_property": True,
        "hair_resampling_widens_support": False,
        "hair_resampling_discovers_new_profit_class": False,
    }


def derive_open_boundary_natural_selection(
    *,
    natural_form_field: Mapping[str, Any],
    preaction_relative_coordinates: Mapping[str, Any],
    translational_truth_partition: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive the set-valued NRRF874 selector support from translational truth."""

    boundaries_by_id: dict[str, dict[str, Any]] = {}
    for boundary in [
        *_field_boundaries(natural_form_field),
        *_freedom_boundaries(preaction_relative_coordinates),
    ]:
        boundaries_by_id[str(boundary["boundary_id"])] = boundary
    boundaries = [boundaries_by_id[key] for key in sorted(boundaries_by_id)]
    interactions = [dict(row["interaction"]) for row in boundaries]
    support = _support_evolution(translational_truth_partition)

    return {
        "protocol": PROTOCOL,
        "status": OPEN_STATUS if boundaries else support.get("status", OPEN_STATUS),
        "equation": (
            "OpenBoundary(S_t)=unresolved truth interactions; "
            "NaturalSelect(S_t)=OpenBoundary(S_t); "
            "S_(t+1)=Close(S_t + ReturnedTruth_(t+1))"
        ),
        "open_boundary": boundaries,
        "open_boundary_count": len(boundaries),
        "boundary_interactions": interactions,
        "boundary_interaction_count": len(interactions),
        "boundary_driven": bool(boundaries),
        "natural_select_is_set_valued": True,
        "runtime_smuggled_tie_breaker_present": False,
        "executor_may_choose_any_truth_derived_boundary_member": bool(boundaries),
        "selection_authors_truth": False,
        "selection_moves_support": False,
        "support_delta_on_selection": 0,
        "only_return_can_change_support": True,
        "return_state_eq_close": True,
        "support_evolution": support,
        "hair_exploration_is_truth_space_exploration": False,
        "hair_resampling_can_widen_support": False,
        "new_truth_class_return_can_widen_support": True,
        "open_boundary_is_support_widening_frontier": True,
        "truth_derived_selector": True,
        "factors_through_translational_truth_classes": True,
        "hair_blind_selector_contract": True,
        "absolute_quoted_number_used_by_selector": False,
        "ball_selector_policy_present": False,
        "ranking_policy_present": False,
        "forecast_policy_present": False,
        "similarity_tolerance_present": False,
        "profit_prediction_used_by_selector": False,
        "eventual_learning_is_conditional": True,
        "fairness_is_hypothesis_not_runtime_fact": True,
        "reachability_is_hypothesis_not_runtime_fact": True,
        "fairness_claimed": False,
        "market_reachability_claimed": False,
        "resampling_never_profits_requires_costly_support_world": True,
        "formal_correspondence": "NRRF874OpenBoundaryNaturalSelectionSupportWideningDerivedFromTranslationalTruth",
        "automatic_order_submission": False,
    }


__all__ = ["PROTOCOL", "derive_open_boundary_natural_selection"]
