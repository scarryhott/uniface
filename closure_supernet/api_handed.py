from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from . import api_completion as base_api
from .config import RuntimeConfig
from .handed_models import (
    HandedLifeFieldProjection,
    HandedLifeRecord,
    HandedLifeSystem,
    HandedLifeSystemCreate,
    HandedMotionCreate,
    HumanRelationCreate,
)
from .handed_web import HANDED_LIFE_HTML


def attach_handed_life_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "handed_life_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.handed_life_routes_attached = True
    app.version = "2.9.0"
    app.description += (
        "; NRRF800 is live as a handed temporal-closure lens: the four-phase "
        "ball step generates one hair class, ball and inverse-hair returns are "
        "typed separately, self-limit is hand inversion at fixed phase, and "
        "submitted human relations are read without absolute standing"
    )

    @app.get("/handed-life", response_class=HTMLResponse, include_in_schema=False)
    async def handed_life_interface() -> str:
        return HANDED_LIFE_HTML

    @app.get("/network/handed-life/capabilities")
    async def handed_life_capabilities() -> dict[str, Any]:
        return runtime.handed_life.capabilities()

    @app.post("/network/handed-life/systems", response_model=HandedLifeSystem)
    async def create_handed_life_system(
        data: HandedLifeSystemCreate,
    ) -> HandedLifeSystem:
        try:
            return HandedLifeSystem.model_validate(
                await runtime.handed_life.create_system(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/supernet/events/{event_id}/handed-life",
        response_model=HandedLifeSystem,
    )
    async def create_handed_life_from_event(
        event_id: str, data: HandedLifeSystemCreate
    ) -> HandedLifeSystem:
        if data.source_event_id is not None and data.source_event_id != event_id:
            raise HTTPException(
                status_code=400,
                detail="source_event_id must match the event path parameter",
            )
        data.source_event_id = event_id
        try:
            return HandedLifeSystem.model_validate(
                await runtime.handed_life.create_system(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/handed-life/systems", response_model=list[HandedLifeSystem])
    async def list_handed_life_systems(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[HandedLifeSystem]:
        return [
            HandedLifeSystem.model_validate(item)
            for item in runtime.handed_life_store.list_systems(limit)
        ]

    @app.get(
        "/network/handed-life/systems/{system_id}",
        response_model=HandedLifeSystem,
    )
    async def get_handed_life_system(system_id: str) -> HandedLifeSystem:
        try:
            return HandedLifeSystem.model_validate(
                runtime.handed_life_store.get_system(system_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/network/handed-life/traces", response_model=HandedLifeRecord)
    async def create_handed_life_trace(data: HandedMotionCreate) -> HandedLifeRecord:
        try:
            return HandedLifeRecord.model_validate(
                await runtime.handed_life.create_motion(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/network/handed-life/human-relations",
        response_model=HandedLifeRecord,
    )
    async def create_human_relation(
        data: HumanRelationCreate,
    ) -> HandedLifeRecord:
        try:
            return HandedLifeRecord.model_validate(
                await runtime.handed_life.create_human_relation(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/handed-life/records", response_model=list[HandedLifeRecord])
    async def list_handed_life_records(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[HandedLifeRecord]:
        return [
            HandedLifeRecord.model_validate(item)
            for item in runtime.handed_life_store.list_records(limit)
        ]

    @app.get(
        "/network/handed-life/records/{record_id}",
        response_model=HandedLifeRecord,
    )
    async def get_handed_life_record(record_id: str) -> HandedLifeRecord:
        try:
            return HandedLifeRecord.model_validate(
                runtime.handed_life_store.get_record(record_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get(
        "/network/handed-life/field",
        response_model=HandedLifeFieldProjection,
    )
    async def handed_life_field() -> HandedLifeFieldProjection:
        return HandedLifeFieldProjection.model_validate(runtime.handed_life_field())

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_handed_life_routes(base_api.create_app(config))


app = attach_handed_life_routes(base_api.app)
