from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query

from . import api_embodied as base_api
from .config import RuntimeConfig
from .selection_models import (
    SelectionFieldProjection,
    SelectionReading,
    SelectionReadingCreate,
)


def attach_selection_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "selection_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.selection_routes_attached = True
    app.version = "2.6.0"
    app.description += (
        "; NRRF790 is live as a selection-audit lens: complete readings yield "
        "natural selections, while selecting from a branching reading is "
        "recorded as forced isolation with removed alternatives and a symmetry witness"
    )

    @app.get("/network/selections/capabilities")
    async def selection_capabilities() -> dict[str, Any]:
        return runtime.selection.capabilities()

    @app.post("/network/selections/readings", response_model=SelectionReading)
    async def create_selection_reading(data: SelectionReadingCreate) -> SelectionReading:
        if not runtime.config.selection_audit_enabled:
            raise HTTPException(status_code=503, detail="selection audit is disabled")
        try:
            return SelectionReading.model_validate(
                await runtime.selection.create_reading(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/supernet/events/{event_id}/select",
        response_model=SelectionReading,
    )
    async def select_from_event(
        event_id: str, data: SelectionReadingCreate
    ) -> SelectionReading:
        if data.source_event_id is not None and data.source_event_id != event_id:
            raise HTTPException(
                status_code=400,
                detail="source_event_id must match the event path parameter",
            )
        data.source_event_id = event_id
        try:
            return SelectionReading.model_validate(
                await runtime.selection.create_reading(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/selections/readings", response_model=list[SelectionReading])
    async def list_selection_readings(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[SelectionReading]:
        return [
            SelectionReading.model_validate(item)
            for item in runtime.selection_store.list_readings(limit)
        ]

    @app.get(
        "/network/selections/readings/{reading_id}",
        response_model=SelectionReading,
    )
    async def get_selection_reading(reading_id: str) -> SelectionReading:
        try:
            return SelectionReading.model_validate(
                runtime.selection_store.get_reading(reading_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get(
        "/network/selections/field",
        response_model=SelectionFieldProjection,
    )
    async def selection_field() -> SelectionFieldProjection:
        return SelectionFieldProjection.model_validate(runtime.selection_field())

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_selection_routes(base_api.create_app(config))


app = attach_selection_routes(base_api.app)
