from __future__ import annotations

"""Opt-in projection adapter for pure closure-equation translation.

Production continues to expose only the one projection/return relation. This
adapter may be instantiated for research, tests or local inspection. Its extra
routes are pure readings: they append no event, select no universal reopening
mode and never alter the latent UI closure.

The trading capability surface reports NRRF870 truth as one unified pre-action
natural-form field. Recognition and selection are identical; returned and OPEN
forms coexist; relative-hair fidelity derives horizon; the relative ball derives
size; and only a later returned interaction may reclose truth.
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
                "Q_(t+1)=Close(Q_t + Translate(observer_t, returned_interaction_t))"
            ),
            "subsystems": [
                "reopening",
                "participant_rule_charts",
                "open_sensor_trading_closure",
                "unified_natural_form_field",
                "relative_hair_horizon_ball_size",
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
