from __future__ import annotations

"""Opt-in projection adapter for pure closure-equation translation.

Production continues to expose only the one projection/return relation. This
adapter may be instantiated for research, tests or local inspection. Its extra
routes are pure readings: they append no event, execute no trade, select no
universal reopening mode and never alter the latent UI closure.

The module-level research app is a separately constructed projection runtime.
Importing this module therefore cannot widen an already-imported production app
object through FastAPI route aliasing.
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
                "Q_(t+1)=Close(Q_t + "
                "Translate(observer_t, returned_interaction_t))"
            ),
            "subsystems": [
                "reopening",
                "participant_rule_charts",
                "open_sensor_trading_closure",
                "resource_reintegration",
                "legacy_compatibility",
            ],
            "proposal_status": "OPEN",
            "only_returned_interaction_recloses": True,
            "mode_enum_authors_truth": False,
            "fixed_horizon_authors_truth": False,
            "successor_quote_loop_authors_truth": False,
            "route_receipt_authors_truth": False,
            "unitary_curvature_gives_amplitude": True,
            "ball_partition_maze_gives_timing": True,
            "amplitude_timing_one_translation": True,
            "signal_trade_one_translation": True,
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


# This is intentionally not minimal_projection_runtime.app. It is an isolated
# opt-in application object with its own projection runtime and route table.
app = create_app()


__all__ = [
    "ClosureEquationRequest",
    "app",
    "attach_closure_equations",
    "create_app",
]
