from __future__ import annotations

"""Opt-in research adapter for current closure equations.

The full versioned natural-form atlas is the carrier relative to current TT.
Trading and NRRF873 coordinates are projections; NRRF874 learning selection is
the set-valued OPEN boundary of that relative atlas. No route mutates truth and
no automatic order submission is exposed.
"""

from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict
from .interactive_translation_equations_current import PROTOCOL, resolve_closure_equations
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
                "NaturalForm(Q,o)=Rel_(Q,o)(VersionedNaturalFormAtlas); "
                "Recognize=Select; H=HairFidelity; Size=RelativeBall; "
                "NaturalSelect(S)=OpenBoundary(Rel_Q(N_all)); "
                "S_(t+1)=Close(S_t+ReturnedTruth); "
                "Q_(t+1)=Close(Q_t+Translate(observer,returned_interaction))"
            ),
            "subsystems": [
                "reopening", "participant_rule_charts", "open_sensor_trading_closure",
                "current_closure_relative_full_natural_form_atlas", "trading_projection_field",
                "relative_hair_horizon_ball_size", "returned_fidelity_selection_freedom",
                "open_boundary_natural_selection_nrrf874", "resource_reintegration",
                "legacy_compatibility",
            ],
            "proposal_status": "OPEN",
            "only_returned_interaction_recloses": True,
            "carrier_is_full_versioned_natural_form_atlas": True,
            "trading_specific_carrier": False,
            "trading_is_projection_family": True,
            "all_natural_form_families_preserved_when_open": True,
            "family_admissibility_requires_source_preserving_returned_translation": True,
            "local_global_relative_to_current_translational_truth": True,
            "local_global_are_not_fixed_ontological_levels": True,
            "local_means_one_returned_atlas_translation": True,
            "global_means_transitive_returned_compatibility": True,
            "open_means_no_returned_family_translation": True,
            "recognition_equals_selection": True,
            "separate_selector_present": False,
            "selection_is_set_valued": True,
            "selection_authors_truth": False,
            "selection_moves_support": False,
            "only_return_can_change_support": True,
            "open_boundary_drives_learning_selection": True,
            "open_boundary_includes_all_atlas_family_frontiers": True,
            "open_boundary_includes_hair_ball_freedom_frontiers": True,
            "truth_derived_selector": True,
            "selector_factors_through_translational_truth_classes": True,
            "selector_is_hair_blind": True,
            "runtime_smuggled_tie_breaker_present": False,
            "absolute_quoted_number_used_by_selector": False,
            "hair_resampling_can_widen_support": False,
            "new_truth_class_return_can_widen_support": True,
            "eventual_learning_is_conditional": True,
            "fairness_is_hypothesis_not_runtime_fact": True,
            "reachability_is_hypothesis_not_runtime_fact": True,
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
            "missing_evidence_widens_selection": False,
            "raw_quote_size_is_not_silently_relative_ball_size": True,
            "successor_quote_loop_authors_truth": False,
            "route_receipt_authors_truth": False,
            "open_sensor_all_closed_itineraries": True,
            "bfs_route_authors_truth": False,
            "undirected_connectivity_authors_ball": False,
            "directed_translation_fibres": True,
            "feedback_hair_equation_unique_normalized_closure": True,
            "unitary_curvature_gives_amplitude": True,
            "amplitude_is_negative_curvature_part": True,
            "ball_partition_max_gives_timing": True,
            "clock_duration_authors_timing": False,
            "normalized_closure_timing_equals_amplitude": True,
            "loop_timing_is_not_hold_horizon": True,
            "profit_is_natural_form_property_not_selection_rule": True,
            "action_projection_authors_truth": False,
            "external_strategy_selector_present": False,
            "predeclared_candidate_graph_present": False,
            "automatic_order_submission": False,
            "formal_correspondence": "NRRF874OpenBoundaryNaturalSelectionSupportWideningDerivedFromTranslationalTruth",
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
__all__ = ["ClosureEquationRequest", "app", "attach_closure_equations", "create_app"]
