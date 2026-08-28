from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from . import api_proof_completion as base_api
from .config import RuntimeConfig
from .natural_interface_models import NaturalInterfaceAdmissionCreate
from .natural_interface_web import NATURAL_SUPERNET_HTML
from .supernet_models import ResourceEnvelope


def attach_natural_interface_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "natural_interface_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.natural_interface_routes_attached = True
    app.version = "3.5.0"
    app.description += (
        "; the primary Black Mirror interaction now executes the existing closure "
        "pipeline synchronously: exact occurrence → UnderstandingAgent → InterpretationAgent "
        "→ AdmissionPolicy → TranslationField → NRRF790 natural selection → next natural "
        "chart. Background autonomy can remain disabled; Sense is caused by the human or "
        "agent interaction itself. The UI still selects no canonical pixel layout and Sense "
        "does not issue truth merely by producing a relation."
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
        return {
            **runtime.natural_interface.capabilities(),
            "live_sense": runtime.live_sense.capabilities(),
        }

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

    @app.post("/supernet/sense")
    async def sensed_offer(data: ResourceEnvelope) -> dict[str, Any]:
        try:
            return await runtime.live_sense.offer(data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/events/{event_id}/sense-interact")
    async def sensed_interaction(
        event_id: str, data: ResourceEnvelope
    ) -> dict[str, Any]:
        try:
            return await runtime.live_sense.interact(event_id, data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/events/{event_id}/sense")
    async def sense_existing_event(event_id: str) -> dict[str, Any]:
        try:
            return await runtime.live_sense.sense_event(event_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    # The natural Black Mirror already posts to these canonical paths.  Register
    # interaction-time Sense handlers ahead of the transport-only handlers that
    # were attached by api_supernet, while keeping those underlying APIs intact
    # for compatibility and subsystem use.
    @app.post("/supernet/integrate", include_in_schema=False)
    async def natural_surface_integrate(data: ResourceEnvelope) -> dict[str, Any]:
        return await sensed_offer(data)

    app.router.routes.insert(0, app.router.routes.pop())

    @app.post(
        "/supernet/events/{event_id}/interact",
        include_in_schema=False,
    )
    async def natural_surface_interact(
        event_id: str, data: ResourceEnvelope
    ) -> dict[str, Any]:
        return await sensed_interaction(event_id, data)

    app.router.routes.insert(0, app.router.routes.pop())

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_natural_interface_routes(base_api.create_app(config))


app = attach_natural_interface_routes(base_api.app)
