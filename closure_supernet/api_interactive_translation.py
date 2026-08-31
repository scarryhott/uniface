from __future__ import annotations

"""Opt-in projection adapter for pure closure-equation translation.

Production continues to expose only the one projection/return relation. This
adapter may be instantiated for research, tests or local inspection. Its extra
routes are pure readings: they append no event, select no universal reopening
mode and never alter the latent UI closure.

The trading capability surface reports one unified pre-action natural-form
field. Relative-hair fidelity derives horizon, the relative ball derives size,
NRRF873 gives the joint selection-freedom frontier, and NRRF874 derives learning
selection from that OPEN boundary plus unresolved relation-space forms. Only a
returned interaction can change truth support.
"""

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

from .interactive_translation_equations_current import (
    PROTOCOL,
    resolve_closure_equations,
)
from .minimal_projection_runtime import create_app as create_projection_app


class ClosureEquationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reopening: dict[str, Any] | None = None
    rule_charts: dict[str, Any] | None = None
    trading: dict[str, Any] | None = None
    resources: dict[str, Any] | None = None
    legacy: dict[str, Any] | None = None


def attach_closure_equations(app: FastAPI) -> FastAPI:
    @app.get("/supernet/closure-equations/capabilities")
    async def closure_equation_capabilities() -> dict[str, Any]:
        return {
            "protocol": PROTOCOL,
            "equation": (
                "Recognize(Q_t)=Select(Q_t)=NaturalFormField(Q_t); "
                "H=HairFidelity; Size=RelativeBall; "
                "F_(t+1)=Close(F_t + ReturnedFidelity_t); "
                "NaturalSelect(S_t)=OpenBoundary(S_t); "
                "S_(t+1)=Close(S_t + ReturnedTruth_(t+1)); "
                "Q_(t+1)=Close(Q_t + Translate(observer_t, returned_interaction_t))"
            ),
            "subsystems": [
                "reopening",
                "participant_rule_charts",
                "open_sensor_trading_closure",
                "unified_natural_form_field",
                "relative_hair_horizon_ball_size",
                "returned_fidelity_selection_freedom",
                "open_boundary_natural_selection_nrrf874",
                "resource_reintegration",
                "legacy_compatibility",
            ],
            "proposal_status": "OPEN",
            "only_returned_interaction_recloses": True,
            "mode_enum_authors_truth": False,
            "fixed_horizon_authors_truth": False,
            "fixed_horizon_present": False,
            "horizon_from_relative_hair_fidelity": True,
            "horizon_is_return_step_coordinate_not_wall_clock": True,
            "relative_ball_is_size": True,
            "size_is_relative_ball_bottleneck_capacity": True,
            "external_position_size_present": False,
            "horizon_and_size_derived_before_action": True,
            "selection_freedom_from_returned_fidelity": True,
            "selection_freedom_evolves_over_time_and_fidelity": True,
            "remaining_limits_are_open_selection_frontiers": True,
            "unwitnessed_boundary_remains_open": True,
            "open_frontier_can_be_resolved_by_later_return": True,
            "external_limit_authors_selection": False,
            "configured_threshold_authors_selection": False,
            "missing_evidence_widens_selection": False,
            "open_boundary_drives_learning_selection": True,
            "open_boundary_includes_hair_ball_freedom_frontiers": True,
            "open_boundary_includes_relation_space_frontiers": True,
            "selection_moves_support": False,
            "only_return_can_change_support": True,
            "return_state_eq_close": True,
            "truth_derived_selector": True,
            "selector_factors_through_translational_truth_classes": True,
            "selector_is_hair_blind": True,
            "runtime_smuggled_tie_breaker_present": False,
            "absolute_quoted_number_used_by_selector": False,
            "ball_selector_policy_present": False,
            "hair_resampling_can_widen_support": False,
            "new_truth_class_return_can_widen_support": True,
            "eventual_learning_is_conditional": True,
            "fairness_is_hypothesis_not_runtime_fact": True,
            "reachability_is_hypothesis_not_runtime_fact": True,
            "raw_quote_size_is_not_silently_relative_ball_size": True,
            "successor_quote_loop_authors_truth": False,
            "route_receipt_authors_truth": False,
            "open_sensor_all_closed_itineraries": True,
            "simple_cycles_determine_finite_geometry": True,
            "bfs_route_authors_truth": False,
            "undirected_connectivity_authors_ball": False,
            "directed_translation_fibres": True,
            "feedback_hair_equation_unique_normalized_closure": True,
            "unitary_curvature_gives_amplitude": True,
            "amplitude_is_negative_curvature_part": True,
            "ball_partition_maze_gives_timing": True,
            "ball_partition_max_gives_timing": True,
            "clock_duration_authors_timing": False,
            "normalized_closure_timing_equals_amplitude": True,
            "loop_timing_is_not_hold_horizon": True,
            "amplitude_timing_one_translation": True,
            "signal_trade_one_translation": True,
            "signal_trade_same_round_trip_value": True,
            "translational_truth_alone": True,
            "recognition_equals_selection": True,
            "recognition_precedes_selection": False,
            "selection_precedes_recognition": False,
            "separate_selector_present": False,
            "selector_mode_present": False,
            "natural_form_selects_interaction": True,
            "selection_is_set_valued": True,
            "selection_is_not_filtering": True,
            "selection_authors_truth": False,
            "open_boundary_is_interaction_frontier": True,
            "all_open_forms_coexist": True,
            "local_open_cannot_block_relation_space_extension": True,
            "relation_space_extension_is_simultaneous_open_form": True,
            "profit_selection_requires_returned_positive_amplitude": True,
            "profit_is_natural_form_property_not_selection_rule": True,
            "action_occurs_after_unified_natural_form_field": True,
            "action_projection_authors_truth": False,
            "external_strategy_selector_present": False,
            "predeclared_candidate_graph_present": False,
            "automatic_order_submission": False,
            "queue_limit_authors_truth": False,
            "legacy_runtime_can_gate": False,
            "formal_correspondence": (
                "NRRF874OpenBoundaryNaturalSelectionSupportWideningDerivedFromTranslationalTruth"
            ),
            "mutation": False,
            "truth_issued": False,
            "existence_closed": False,
            "dialectic_continuation": "OPEN",
            "published_production_surface": False,
        }

    @app.post("/supernet/closure-equations/resolve")
    async def resolve_equations(data: ClosureEquationRequest) -> dict[str, Any]:
        return resolve_closure_equations(data.model_dump(exclude_none=True))

    return app


def create_app(config: Any | None = None) -> FastAPI:
    return attach_closure_equations(create_projection_app(config))


app = create_app()


__all__ = [
    "ClosureEquationRequest",
    "app",
    "attach_closure_equations",
    "create_app",
]
