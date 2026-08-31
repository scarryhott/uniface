from __future__ import annotations

"""Published projection with one closure-equation translation endpoint.

The endpoint is a pure relative reading. It does not append events, execute a
trade, select a universal reopening mode, or alter the latent UI closure.
"""

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

from .interactive_translation_equations import (
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


def create_app(config: Any | None = None) -> FastAPI:
    app = create_projection_app(config)

    @app.get("/supernet/closure-equations/capabilities")
    async def closure_equation_capabilities() -> dict[str, Any]:
        return {
            "protocol": PROTOCOL,
            "equation": "Q_(t+1)=Close(Q_t + returned_interaction_t)",
            "subsystems": [
                "reopening",
                "participant_rule_charts",
                "trading_forms",
                "resource_reintegration",
                "legacy_compatibility",
            ],
            "proposal_status": "OPEN",
            "only_returned_interaction_recloses": True,
            "mode_enum_authors_truth": False,
            "fixed_horizon_authors_truth": False,
            "queue_limit_authors_truth": False,
            "legacy_runtime_can_gate": False,
            "mutation": False,
            "truth_issued": False,
            "existence_closed": False,
            "dialectic_continuation": "OPEN",
        }

    @app.post("/supernet/closure-equations/resolve")
    async def resolve_equations(data: ClosureEquationRequest) -> dict[str, Any]:
        return resolve_closure_equations(data.model_dump(exclude_none=True))

    return app


app = create_app()


__all__ = ["ClosureEquationRequest", "app", "create_app"]
