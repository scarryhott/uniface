from __future__ import annotations

"""Published runtime wrapper for the closure-ball-derived Supernet surface.

The existing projection runtime remains the sole persistent mutation and truth
boundary.  This wrapper adds no ledger and no parallel action endpoint.  It
replaces only the presentation route, derives one closure ball from the active
validated contract, and exposes the exact same source-preserving return route.
"""

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .closure_ball_interface import CLOSURE_BALL_SUPERNET_HTML
from .closure_ball_projection import (
    PROTOCOL as CLOSURE_BALL_PROTOCOL,
    derive_closure_ball_projection,
    validate_closure_ball_projection,
)
from .minimal_projection_runtime import (
    app as projection_app,
    create_app as create_projection_app,
)


_SURFACE_PATHS = {"/", "/supernet", "/natural-interface"}


def _remove_prior_surface_routes(app: FastAPI) -> None:
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if not (
            getattr(route, "path", None) in _SURFACE_PATHS
            and "GET" in (getattr(route, "methods", None) or set())
        )
    ]


def _install_closure_ball_surface(app: FastAPI) -> FastAPI:
    if getattr(app.state, "closure_ball_surface_installed", False):
        return app

    _remove_prior_surface_routes(app)

    async def surface() -> HTMLResponse:
        return HTMLResponse(
            CLOSURE_BALL_SUPERNET_HTML,
            headers={
                "Cache-Control": "no-store, max-age=0",
                "X-Supernet-Interface": CLOSURE_BALL_PROTOCOL,
            },
        )

    for path in sorted(_SURFACE_PATHS):
        app.add_api_route(
            path,
            surface,
            methods=["GET"],
            response_class=HTMLResponse,
            include_in_schema=False,
            name=f"closure_ball_surface_{path.strip('/').replace('/', '_') or 'root'}",
        )

    async def closure_ball_projection(
        perspective_id: str = "perspective",
        focus_event_id: str | None = None,
    ) -> dict[str, Any]:
        contract = app.state.runtime.project(
            perspective_id=perspective_id,
            focus_event_id=focus_event_id,
        )
        closure_ball = derive_closure_ball_projection(contract)
        validation = validate_closure_ball_projection(contract, closure_ball)
        if not validation["valid"]:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "OPEN_CLOSURE_BALL_DERIVATION",
                    "errors": validation["errors"],
                    "truth_issued": False,
                },
            )
        return {
            "protocol": CLOSURE_BALL_PROTOCOL,
            "closure_ball": closure_ball,
            "closure_ui_contract": contract,
            "validation": validation,
            "parallel_truth_runtime_present": False,
            "parallel_mutation_route_present": False,
            "truth_issued": False,
            "currency_issued": False,
        }

    async def closure_ball_capabilities() -> dict[str, Any]:
        return {
            "protocol": CLOSURE_BALL_PROTOCOL,
            "semantic_primitive": "ONE_CLOSURE_BALL_INTERACTION_EVENT",
            "interface": "RELATIVE_PROJECTION_OF_CLOSURE_BALL",
            "actions": "CLOSURE_BALL_HAIR_ONLY",
            "maze_partition": "CLOSURE_EQUALITY_KERNEL",
            "event_equality": (
                "UI(event)=AI(event)=Token(event)=Closure(event) "
                "modulo perspective translation"
            ),
            "mutation_routes": [
                "/supernet/interface/projections/{contract_id}/return"
            ],
            "parallel_mutation_routes": False,
            "open_paths_navigable": True,
            "open_paths_execute_as_equality": False,
            "numeric_curvature_invented": False,
            "truth_issued": False,
            "currency_issued": False,
        }

    app.add_api_route(
        "/supernet/ball",
        closure_ball_projection,
        methods=["GET"],
        include_in_schema=False,
        name="closure_ball_projection",
    )
    app.add_api_route(
        "/supernet/ball/capabilities",
        closure_ball_capabilities,
        methods=["GET"],
        include_in_schema=False,
        name="closure_ball_capabilities",
    )
    app.state.closure_ball_surface_installed = True
    app.state.closure_ball_protocol = CLOSURE_BALL_PROTOCOL
    return app


def create_app(config: Any | None = None) -> FastAPI:
    return _install_closure_ball_surface(create_projection_app(config))


app = _install_closure_ball_surface(projection_app)


__all__ = ["app", "create_app"]
