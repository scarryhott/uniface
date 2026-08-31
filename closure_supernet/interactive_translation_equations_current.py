from __future__ import annotations

"""Current closure runtime: full atlas relative to current translational truth.

The versioned natural-form atlas is the semantic carrier; trading is a
projection. NRRF874 natural selection is the set-valued OPEN boundary of the
current-relative atlas plus returned hair/ball freedom frontiers. Selection is
support-inert; only returned truth recloses and can widen support.

External truth enters through one verified source-return boundary. Before any
market relation or external atlas translation reaches closure, its exact
semantic source payload must carry a trusted Ed25519 witness. Caller booleans,
ids, hair, size, authentication, and cost-completeness claims have no semantic
authority. Signed source events are consumed once across supplied history so
replay cannot increase fidelity, horizon, discovery, or actionability.
"""

import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS, audit_translational_continuity
from .current_closure_relative_natural_form_atlas import derive_current_closure_relative_atlas
from .interactive_translation_equations import (
    resolve_legacy_equation,
    resolve_reopening_equation,
    resolve_resource_equation,
    resolve_rule_chart_equation,
    resolve_trading_equation as resolve_legacy_trading_equation,
)
from .trading_natural_form_closure import PROTOCOL as TRADING_PROTOCOL, resolve_open_sensor_trading_closure
from .trading_open_boundary_natural_selection import derive_open_boundary_natural_selection
from .trading_relative_hair_horizon_ball_size import derive_preaction_relative_coordinates
from .trading_source_return_truth import (
    PROTOCOL as SOURCE_WITNESS_PROTOCOL,
    verify_atlas_translation_sources,
    verify_trading_feedback,
    verify_trading_history,
)
from .trading_translational_truth_partition import derive_translational_truth_partition
from .trading_unified_natural_form_field import derive_unified_natural_form_field

PROTOCOL = "closure.supernet/interactive-translation-equations-current-relative-full-atlas-verified-source-nrrf874-v13"


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def _sensor_feedback(
    *,
    sensor_feedback: Sequence[Mapping[str, Any]],
    returned_equations: Sequence[Mapping[str, Any]],
    hair_equations: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    supplied = [v for v in (sensor_feedback, returned_equations, hair_equations) if v]
    if len(supplied) > 1:
        raise ValueError("Supply exactly one of sensor_feedback, returned_equations, or hair_equations")
    return list(supplied[0]) if supplied else []


def _atlas_boundary_adapter(relative_atlas: Mapping[str, Any]) -> dict[str, Any]:
    forms: list[dict[str, Any]] = []
    for index, raw in enumerate(relative_atlas.get("action_projections", [])):
        action = dict(raw)
        if action.get("status") != OPEN_STATUS or action.get("requires_return") is not True:
            continue
        family_id = action.get("family_id")
        kind = (
            f"OPEN_ATLAS_FAMILY_TRANSLATION:{family_id}"
            if action.get("kind") == "RETURN_SOURCE_PRESERVING_ATLAS_TRANSLATION"
            else f"OPEN_CURRENT_RELATIVE_ATLAS_FORM:{action.get('kind')}:{index}"
        )
        forms.append({
            "form_id": action.get("projection_id") or action.get("boundary_id") or f"atlas-open-{index}",
            "kind": kind,
            "status": OPEN_STATUS,
            "closure_id": action.get("closure_id") or action.get("current_tt_id"),
            "source_token": action.get("source_token"),
            "target_token": action.get("target_token"),
            "family_id": family_id,
            "action_projection": action,
        })
    return {"open_natural_forms": forms}


def _formal_fixture_audit(count: int, *, kind: str) -> dict[str, Any]:
    return {
        "protocol": SOURCE_WITNESS_PROTOCOL,
        "status": WITNESSED_STATUS if count else OPEN_STATUS,
        "input_count": count,
        "verified_count": 0,
        "open_count": 0,
        "formal_fixture_count": count,
        "kind": kind,
        "formal_fixture_mode": True,
        "external_source_truth_condition_satisfied": False,
        "semantic_scope": "FORMAL_OR_SYNTHETIC_FIXTURE_ONLY",
        "caller_flags_are_not_external_truth_witnesses": True,
    }


def _verify_current_inputs(
    *,
    observer_id: str | None,
    feedback: Sequence[Mapping[str, Any]],
    history: Sequence[Sequence[Mapping[str, Any]]],
    atlas_translation_sources: Sequence[Mapping[str, Any]],
    source_truth_mode: str,
) -> tuple[list[dict[str, Any]], list[list[dict[str, Any]]], list[dict[str, Any]], dict[str, Any]]:
    mode = str(source_truth_mode or "VERIFIED").upper()
    if mode not in {"VERIFIED", "FORMAL_FIXTURE"}:
        raise ValueError("source_truth_mode must be VERIFIED or FORMAL_FIXTURE")

    if mode == "FORMAL_FIXTURE":
        verified_history = [[dict(row) for row in frame] for frame in history]
        verified_feedback = list(verified_history[-1]) if verified_history else [dict(row) for row in feedback]
        verified_atlas = [dict(row) for row in atlas_translation_sources]
        return verified_feedback, verified_history, verified_atlas, {
            "protocol": SOURCE_WITNESS_PROTOCOL,
            "mode": mode,
            "feedback": _formal_fixture_audit(len(verified_feedback), kind="TRADING_RELATION_RETURN"),
            "history_frames": [
                _formal_fixture_audit(len(frame), kind="TRADING_RELATION_RETURN")
                for frame in verified_history
            ],
            "atlas_translations": _formal_fixture_audit(len(verified_atlas), kind="ATLAS_TRANSLATION_RETURN"),
            "truth_requires_verified_source_witness_for_external_inputs": True,
            "formal_fixture_mode_is_not_externally_admissible": True,
        }

    verified_history, history_audits = verify_trading_history(
        observer_id=observer_id,
        history=history,
    )
    if verified_history:
        verified_feedback = list(verified_history[-1])
        feedback_audit = history_audits[-1]
    else:
        verified_feedback, feedback_audit = verify_trading_feedback(
            observer_id=observer_id,
            feedback=feedback,
        )

    verified_atlas, atlas_audit = verify_atlas_translation_sources(
        observer_id=observer_id,
        sources=atlas_translation_sources,
    )
    return verified_feedback, verified_history, verified_atlas, {
        "protocol": SOURCE_WITNESS_PROTOCOL,
        "mode": mode,
        "feedback": feedback_audit,
        "history_frames": history_audits,
        "atlas_translations": atlas_audit,
        "truth_requires_verified_source_witness_for_external_inputs": True,
        "unsigned_or_untrusted_return_remains_open": True,
        "duplicate_source_event_replay_remains_open": True,
        "caller_returned_flag_authors_truth": False,
        "caller_source_ids_author_truth": False,
        "caller_return_id_authors_geometry": False,
        "caller_authenticated_flag_authors_execution": False,
        "caller_cost_complete_flag_authors_execution": False,
        "caller_size_authors_action": False,
        "caller_hair_authors_truth": False,
        "verified_external_return_uses_canonical_hair_presentation": True,
    }


def resolve_trading_equation(
    *,
    observer_id: str | None = None,
    sensor_feedback: Sequence[Mapping[str, Any]] = (),
    returned_equations: Sequence[Mapping[str, Any]] = (),
    hair_equations: Sequence[Mapping[str, Any]] = (),
    sensor_history: Sequence[Sequence[Mapping[str, Any]]] = (),
    atlas_translation_sources: Sequence[Mapping[str, Any]] = (),
    source_truth_mode: str = "VERIFIED",
    max_returns: int | None = None,
    proposals: Sequence[Mapping[str, Any]] = (),
    receipts: Sequence[Mapping[str, Any]] = (),
    minimum_receipts: int = 1,
    max_forms: int | None = None,
) -> dict[str, Any]:
    feedback = _sensor_feedback(
        sensor_feedback=sensor_feedback,
        returned_equations=returned_equations,
        hair_equations=hair_equations,
    )
    if sensor_history and feedback:
        raise ValueError("Supply sensor_history or one current sensor feedback surface, not both")
    raw_history = [[dict(row) for row in frame] for frame in sensor_history]

    current_feedback, history, verified_atlas_sources, source_truth_audit = _verify_current_inputs(
        observer_id=observer_id,
        feedback=feedback,
        history=raw_history,
        atlas_translation_sources=atlas_translation_sources,
        source_truth_mode=source_truth_mode,
    )

    natural = resolve_open_sensor_trading_closure(
        observer_id=observer_id,
        sensor_feedback=current_feedback,
        max_returns=max_returns,
    )
    truth_partition = (
        derive_translational_truth_partition(
            observer_id=observer_id,
            sensor_history=history,
            max_returns_per_frame=max_returns,
        )
        if history else None
    )
    coordinates = derive_preaction_relative_coordinates(
        observer_id=observer_id,
        natural_closure=natural,
        current_feedback=current_feedback,
        sensor_history=history,
        max_returns=max_returns,
    )
    trading_projection = derive_unified_natural_form_field(
        natural_closure=natural,
        preaction_coordinates=coordinates.get("by_closure_id", {}),
    )
    relative_atlas = derive_current_closure_relative_atlas(
        observer_id=observer_id,
        natural_closure=natural,
        preaction_coordinates=coordinates.get("by_closure_id", {}),
        trading_projection_field=trading_projection,
        additional_translation_sources=verified_atlas_sources,
    )
    open_boundary_selection = derive_open_boundary_natural_selection(
        natural_form_field=_atlas_boundary_adapter(relative_atlas),
        preaction_relative_coordinates=coordinates,
        translational_truth_partition=truth_partition,
    )

    relative_atlas["returned_natural_forms"] = list(trading_projection.get("returned_natural_forms", []))
    relative_atlas["returned_natural_form_count"] = trading_projection.get("returned_natural_form_count", 0)
    relative_atlas["profitable_returned_natural_forms"] = list(trading_projection.get("profitable_returned_natural_forms", []))
    relative_atlas["compatibility_trading_readouts_only"] = True
    relative_atlas["open_boundary_natural_selection"] = open_boundary_selection
    relative_atlas["learning_interactions"] = list(open_boundary_selection.get("boundary_interactions", []))
    relative_atlas["learning_interaction_count"] = open_boundary_selection.get("boundary_interaction_count", 0)
    relative_atlas["boundary_driven_learning"] = open_boundary_selection.get("boundary_driven") is True
    relative_atlas["source_truth_audit"] = source_truth_audit

    current_profit = any(f.get("orientation") == "PROFITABLE" for f in natural.get("natural_forms", []))
    learned_profit = truth_partition.get("learned_profit") is True if truth_partition is not None else current_profit

    body = dict(natural)
    body.update({
        "protocol": PROTOCOL,
        "natural_trading_protocol": TRADING_PROTOCOL,
        "source_witness_protocol": SOURCE_WITNESS_PROTOCOL,
        "source_truth_mode": str(source_truth_mode).upper(),
        "source_truth_audit": source_truth_audit,
        "closure_continuation": None,
        "translational_truth_partition": truth_partition,
        "translational_truth_learning": truth_partition,
        "preaction_relative_coordinates": coordinates,
        "current_closure_relative_atlas": relative_atlas,
        "natural_form_field": relative_atlas,
        "natural_form_selection": relative_atlas,
        "trading_projection_field": trading_projection,
        "open_boundary_natural_selection": open_boundary_selection,
        "selected_interactions": list(relative_atlas.get("action_projections", [])),
        "learning_interactions": list(open_boundary_selection.get("boundary_interactions", [])),
        "current_profit_truth_witnessed": current_profit,
        "learned_profit": learned_profit,
    })

    if proposals or receipts:
        legacy = resolve_legacy_trading_equation(
            proposals=proposals,
            receipts=receipts,
            minimum_receipts=minimum_receipts,
            max_forms=max_forms,
        )
        body["legacy_route_receipt_projection"] = {
            **legacy,
            "semantic_authority": False,
            "may_gate_interaction": False,
            "may_widen_truth": False,
            "may_feed_back_into_closure": False,
            "compatibility_status": legacy.get("status"),
        }
        body["forms"] = [
            {**dict(r), "semantic_authority": False, "gate_open_authors_truth": False}
            for r in legacy.get("forms", [])
        ]
        body["proposals"] = list(legacy.get("proposals", []))
        body["unmatched_or_open_receipts"] = list(legacy.get("unmatched_or_open_receipts", []))
    else:
        body["legacy_route_receipt_projection"] = None
        body["forms"] = []
        body["proposals"] = []
        body["unmatched_or_open_receipts"] = []

    body.update({
        "status": natural["status"],
        "translational_truth_alone": True,
        "source_return_truth_condition_enforced": str(source_truth_mode).upper() == "VERIFIED",
        "truth_requires_verified_source_witness": True,
        "unsigned_or_untrusted_return_remains_open": True,
        "duplicate_source_event_replay_remains_open": True,
        "caller_returned_flag_authors_truth": False,
        "caller_source_ids_author_truth": False,
        "caller_return_id_authors_geometry": False,
        "caller_hair_authors_truth": False,
        "caller_authenticated_flag_authors_execution": False,
        "caller_cost_complete_flag_authors_execution": False,
        "caller_size_authors_action": False,
        "verified_external_return_uses_canonical_hair_presentation": True,
        "atlas_translation_source_requires_verified_witness": True,
        "nested_atlas_translations_verified_individually": True,
        "formal_fixture_mode_is_not_external_truth": True,
        "carrier_is_full_versioned_natural_form_atlas": True,
        "trading_specific_carrier": False,
        "trading_is_projection_family": True,
        "all_natural_form_families_preserved_when_open": True,
        "family_admissibility_requires_source_preserving_returned_translation": True,
        "local_global_relative_to_current_translational_truth": True,
        "local_global_are_not_fixed_ontological_levels": True,
        "recognition_equals_selection": True,
        "recognition_precedes_selection": False,
        "selection_precedes_recognition": False,
        "separate_selector_present": False,
        "selector_mode_present": False,
        "natural_form_selects_interaction": True,
        "selection_is_set_valued": True,
        "selection_is_not_filtering": True,
        "selection_authors_truth": False,
        "selection_moves_support": False,
        "only_return_can_change_support": True,
        "return_state_eq_close": True,
        "open_boundary_is_interaction_frontier": True,
        "open_boundary_drives_learning_selection": True,
        "open_boundary_includes_all_atlas_family_frontiers": True,
        "open_boundary_includes_hair_ball_freedom_frontiers": True,
        "truth_derived_selector": True,
        "selector_factors_through_translational_truth_classes": True,
        "selector_is_hair_blind": True,
        "runtime_smuggled_tie_breaker_present": False,
        "absolute_quoted_number_used_by_selector": False,
        "ball_selector_policy_present": False,
        "hair_resampling_can_widen_support": False,
        "new_truth_class_return_can_widen_support": True,
        "fairness_is_hypothesis_not_runtime_fact": True,
        "reachability_is_hypothesis_not_runtime_fact": True,
        "eventual_learning_is_conditional": True,
        "route_receipt_authors_truth": False,
        "completed_route_is_not_natural_form_primitive": True,
        "ask_to_immediately_succeeding_bid_is_definition": False,
        "only_open_sensor_return_recloses_trading": True,
        "open_sensor_all_closed_itineraries": True,
        "bfs_route_authors_truth": False,
        "undirected_connectivity_authors_ball": False,
        "directed_translation_fibres": True,
        "amplitude_is_negative_curvature_part": True,
        "ball_partition_max_gives_timing": True,
        "clock_duration_authors_timing": False,
        "normalized_closure_timing_equals_amplitude": True,
        "amplitude_timing_one_translation": True,
        "loop_timing_is_not_hold_horizon": True,
        "fixed_horizon_authors_truth": False,
        "fixed_horizon_present": False,
        "horizon_from_relative_hair_fidelity": True,
        "horizon_is_return_step_coordinate_not_wall_clock": True,
        "relative_ball_is_size": True,
        "size_is_relative_ball_bottleneck_capacity": True,
        "external_position_size_present": False,
        "external_position_size_authors_action": False,
        "horizon_and_size_derived_before_action": True,
        "selection_freedom_from_returned_fidelity": True,
        "selection_freedom_evolves_over_time_and_fidelity": True,
        "remaining_limits_are_open_selection_frontiers": True,
        "raw_quote_size_is_not_silently_relative_ball_size": True,
        "signal_trade_equal_relative_to_translation": True,
        "translational_truth_authors_relation_partition": True,
        "ball_equals_natural_form_truth_class": True,
        "hair_is_intra_truth_class_presentation": True,
        "predeclared_market_graph_authors_truth_partition": False,
        "relation_space_refines_from_returned_interaction": True,
        "distinct_natural_forms_are_not_declared_translations": True,
        "separate_dynamics_law_present": False,
        "inter_class_transition_model_present": False,
        "curvature_continuation_is_authoritative": False,
        "trend_model_present": False,
        "forecast_model_present": False,
        "similarity_tolerance_present": False,
        "profit_trajectory_present": False,
        "profit_trajectory_authors_trade": False,
        "history_length_authors_truth": False,
        "profit_learning_is_discovery_not_prediction": True,
        "positive_profit_requires_current_returned_truth": True,
        "positive_crossing_requires_current_execution_return": True,
        "all_open_forms_coexist": True,
        "local_open_cannot_block_relation_space_extension": True,
        "relation_space_extension_is_simultaneous_open_form": True,
        "profit_selection_requires_returned_positive_amplitude": True,
        "profit_is_natural_form_property_not_selection_rule": True,
        "action_occurs_after_unified_natural_form_field": True,
        "action_projection_authors_truth": False,
        "external_strategy_selector_present": False,
        "predeclared_candidate_graph_present": False,
        "configuration_authors_truth": False,
        "computation_bounds_author_truth": False,
        "existence_closed": False,
        "dialectic_continuation_status": OPEN_STATUS,
        "formal_correspondence": "NRRF874OpenBoundaryNaturalSelectionSupportWideningDerivedFromTranslationalTruth+VerifiedSourceReturnTruthCondition",
    })
    body["id"] = _digest("natural-trading-equation-current-relative-full-atlas-verified-source-nrrf874", body)
    return body


def resolve_closure_equations(payload: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "protocol": PROTOCOL,
        "equation": (
            "VerifySource(return); NaturalForm(Q,o)=Rel_(Q,o)(VersionedNaturalFormAtlas); "
            "Recognize=Select; H=HairFidelity; Size=RelativeBall; "
            "NaturalSelect(S)=OpenBoundary(Rel_Q(N_all)); "
            "S_(t+1)=Close(S_t+VerifiedReturnedTruth); "
            "Q_(t+1)=Close(Q_t+Translate(observer,verified_returned_interaction))"
        ),
        "translational_truth_alone": True,
        "truth_requires_verified_source_witness": True,
        "duplicate_source_event_replay_remains_open": True,
        "caller_returned_flag_authors_truth": False,
        "caller_source_ids_author_truth": False,
        "caller_return_id_authors_geometry": False,
        "caller_hair_authors_truth": False,
        "formal_fixture_mode_is_not_externally_admissible": True,
        "carrier_is_full_versioned_natural_form_atlas": True,
        "trading_specific_carrier": False,
        "local_global_relative_to_current_translational_truth": True,
        "recognition_equals_selection": True,
        "separate_selector_present": False,
        "natural_form_selects_interaction": True,
        "selection_authors_truth": False,
        "selection_moves_support": False,
        "only_return_can_change_support": True,
        "open_boundary_drives_learning_selection": True,
        "truth_derived_selector": True,
        "selector_is_hair_blind": True,
        "horizon_from_relative_hair_fidelity": True,
        "relative_ball_is_size": True,
        "horizon_and_size_derived_before_action": True,
        "selection_freedom_from_returned_fidelity": True,
        "fixed_horizon_present": False,
        "external_position_size_present": False,
        "action_occurs_after_unified_natural_form_field": True,
        "proposal_status": OPEN_STATUS,
        "only_returned_interaction_recloses": True,
        "separate_dynamics_law_present": False,
        "configuration_authors_truth": False,
        "computation_bounds_author_truth": False,
        "fairness_is_hypothesis_not_runtime_fact": True,
        "reachability_is_hypothesis_not_runtime_fact": True,
        "existence_closed": False,
        "dialectic_continuation_status": OPEN_STATUS,
    }
    if payload.get("reopening") is not None:
        result["reopening"] = resolve_reopening_equation(**dict(payload["reopening"]))
    if payload.get("rule_charts") is not None:
        result["rule_charts"] = resolve_rule_chart_equation(**dict(payload["rule_charts"]))
    if payload.get("trading") is not None:
        trading_payload = dict(payload["trading"])
        requested_mode = str(trading_payload.pop("source_truth_mode", "VERIFIED")).upper()
        if requested_mode != "VERIFIED":
            raise ValueError("external closure-equation trading requests require VERIFIED source truth")
        trading_payload["source_truth_mode"] = "VERIFIED"
        result["trading"] = resolve_trading_equation(**trading_payload)
    if payload.get("resources") is not None:
        result["resources"] = resolve_resource_equation(**dict(payload["resources"]))
    if payload.get("legacy") is not None:
        result["legacy"] = resolve_legacy_equation(**dict(payload["legacy"]))
    subsystems = [
        v for k, v in result.items()
        if k in {"reopening", "rule_charts", "trading", "resources", "legacy"}
    ]
    result["status"] = (
        WITNESSED_STATUS
        if subsystems and all(r.get("status") == WITNESSED_STATUS for r in subsystems)
        else OPEN_STATUS
    )
    target = dict(result)
    target.pop("continuity_audit", None)
    result["continuity_audit"] = audit_translational_continuity(target)
    result["id"] = _digest("closure-equations-current-relative-full-atlas-verified-source-nrrf874", result)
    return result


__all__ = [
    "PROTOCOL",
    "resolve_closure_equations",
    "resolve_legacy_equation",
    "resolve_reopening_equation",
    "resolve_resource_equation",
    "resolve_rule_chart_equation",
    "resolve_trading_equation",
]
