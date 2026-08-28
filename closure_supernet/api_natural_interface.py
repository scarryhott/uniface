from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from . import api_proof_completion as base_api
from .config import RuntimeConfig
from .natural_interface_models import NaturalInterfaceAdmissionCreate
from .natural_interface_web import NATURAL_SUPERNET_HTML


def attach_natural_interface_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "natural_interface_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.natural_interface_routes_attached = True
    app.version = "3.4.0"
    app.description += (
        "; the primary Black Mirror surface is now selected from current closure "
        "receipts: exact source point, open selector, Turing Being 0↔∞, rule/geometry "
        "continuation, proof/completion/balance, return ball–hair, or shared architecture. "
        "The selector chooses the least sufficient chart kind, preserves every source "
        "and proof fibre, gates semantic layers behind their receipts, and returns every "
        "interaction through the canonical Supernet integrator without selecting a "
        "canonical pixel layout or issuing truth"
    )

    @app.get(
        "/natural-interface",
        response_class=HTMLResponse,
        include_in_schema=False,
    )
    async def natural_interface_page() -> str:
        return NATURAL_SUPERNET_HTML

    @app.get("/supernet/interface/capabilities")
    async def natural_interface_capabilities() -> dict[str, Any]:
        return runtime.natural_interface.capabilities()

    @app.get("/supernet/interface")
    async def natural_interface_receipt(
        focus_event_id: str | None = None,
        perspective_id: str | None = None,
    ) -> dict[str, Any]:
        try:
            return runtime.natural_interface.select(
                focus_event_id=focus_event_id,
                perspective_id=perspective_id,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/interface/admissions")
    async def admit_natural_interface(
        data: NaturalInterfaceAdmissionCreate,
    ) -> dict[str, Any]:
        try:
            return await runtime.natural_interface.admit(data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_natural_interface_routes(base_api.create_app(config))


app = attach_natural_interface_routes(base_api.app)
