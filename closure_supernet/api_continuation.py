from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from . import api_turing_being as base_api
from .config import RuntimeConfig
from .continuation_models import (
    ContinuationFieldProjection,
    ContinuationMap,
    ContinuationMapCreate,
    ContinuationSystem,
    ContinuationSystemCreate,
    GeometryWitness,
    RuleWitness,
)
from .continuation_web import CONTINUATION_HTML


def attach_continuation_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "continuation_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.continuation_routes_attached = True
    app.version = "3.2.0"
    app.description += (
        "; NRRF807 keeps rule and geometry as two non-collapsing readings of one "
        "natural continuation: rule is directed forward range, geometry is its "
        "generated equality fold, and geometry never fabricates a missing rule witness"
    )

    @app.get("/continuation", response_class=HTMLResponse, include_in_schema=False)
    async def continuation_interface() -> str:
        return CONTINUATION_HTML

    @app.get("/network/continuations/capabilities")
    async def continuation_capabilities() -> dict[str, Any]:
        return runtime.continuation.capabilities()

    @app.post(
        "/network/continuations/systems",
        response_model=ContinuationSystem,
    )
    async def create_continuation_system(
        data: ContinuationSystemCreate,
    ) -> ContinuationSystem:
        try:
            return ContinuationSystem.model_validate(
                await runtime.continuation.create_system(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/network/turing-being/life-events/{life_event_id}/continuation",
        response_model=ContinuationSystem,
    )
    async def continue_turing_being_life(
        life_event_id: str,
        data: ContinuationSystemCreate,
    ) -> ContinuationSystem:
        if (
            data.turing_being_life_event_id is not None
            and data.turing_being_life_event_id != life_event_id
        ):
            raise HTTPException(
                status_code=400,
                detail="turing_being_life_event_id must match the path parameter",
            )
        data.turing_being_life_event_id = life_event_id
        try:
            return ContinuationSystem.model_validate(
                await runtime.continuation.create_system(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get(
        "/network/continuations/systems",
        response_model=list[ContinuationSystem],
    )
    async def list_continuation_systems(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[ContinuationSystem]:
        return [
            ContinuationSystem.model_validate(item)
            for item in runtime.continuation_store.list_systems(limit)
        ]

    @app.get(
        "/network/continuations/systems/{system_id}",
        response_model=ContinuationSystem,
    )
    async def get_continuation_system(system_id: str) -> ContinuationSystem:
        try:
            return ContinuationSystem.model_validate(
                runtime.continuation_store.get_system(system_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/network/continuations/systems/{system_id}/continuation")
    async def continuation_prefix(
        system_id: str,
        origin: str | None = None,
        steps: Annotated[int | None, Query(ge=0, le=20_000)] = None,
    ) -> dict[str, Any]:
        try:
            return runtime.continuation.continuation_prefix(
                system_id,
                origin=origin,
                steps=steps,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get(
        "/network/continuations/systems/{system_id}/rule",
        response_model=RuleWitness,
    )
    async def rule_witness(
        system_id: str,
        source: Annotated[str, Query(min_length=1)],
        target: Annotated[str, Query(min_length=1)],
    ) -> RuleWitness:
        try:
            return RuleWitness.model_validate(
                runtime.continuation.rule_witness(system_id, source, target)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get(
        "/network/continuations/systems/{system_id}/geometry",
        response_model=GeometryWitness,
    )
    async def geometry_witness(
        system_id: str,
        source: Annotated[str, Query(min_length=1)],
        target: Annotated[str, Query(min_length=1)],
    ) -> GeometryWitness:
        try:
            return GeometryWitness.model_validate(
                runtime.continuation.geometry_witness(system_id, source, target)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/network/continuations/maps",
        response_model=ContinuationMap,
    )
    async def create_continuation_map(
        data: ContinuationMapCreate,
    ) -> ContinuationMap:
        try:
            return ContinuationMap.model_validate(
                await runtime.continuation.create_map(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get(
        "/network/continuations/maps",
        response_model=list[ContinuationMap],
    )
    async def list_continuation_maps(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[ContinuationMap]:
        return [
            ContinuationMap.model_validate(item)
            for item in runtime.continuation_store.list_maps(limit)
        ]

    @app.get(
        "/network/continuations/maps/{map_id}",
        response_model=ContinuationMap,
    )
    async def get_continuation_map(map_id: str) -> ContinuationMap:
        try:
            return ContinuationMap.model_validate(
                runtime.continuation_store.get_map(map_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get(
        "/network/continuations/field",
        response_model=ContinuationFieldProjection,
    )
    async def continuation_field() -> ContinuationFieldProjection:
        return ContinuationFieldProjection.model_validate(runtime.continuation_field())

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_continuation_routes(base_api.create_app(config))


app = attach_continuation_routes(base_api.app)
