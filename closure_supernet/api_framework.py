from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from . import api_constructive as base_api
from .config import RuntimeConfig
from .framework_models import (
    FrameworkFieldProjection,
    NaturalSelectionArena,
    NaturalSelectionArenaCreate,
    TranslationalTruthFramework,
    TranslationalTruthFrameworkCreate,
    TruthSelectionBridge,
    TruthSelectionBridgeCreate,
)
from .framework_web import FRAMEWORK_HTML


def attach_framework_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "framework_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.framework_routes_attached = True
    app.version = "2.4.0"
    app.description += (
        "; NRRF784/785 are live as one orbit layer: natural selectors are fixed "
        "under level shifts and factor through level orbits, while classical and "
        "contextual frameworks share one partial translational truth and differ "
        "only by the existence of a global assignment"
    )

    @app.get("/frameworks", response_class=HTMLResponse, include_in_schema=False)
    async def framework_interface() -> str:
        return FRAMEWORK_HTML

    @app.get("/network/frameworks/capabilities")
    async def framework_capabilities() -> dict[str, Any]:
        return runtime.frameworks.capabilities()

    @app.post("/network/frameworks/naturality", response_model=NaturalSelectionArena)
    async def create_naturality(data: NaturalSelectionArenaCreate) -> NaturalSelectionArena:
        if not runtime.config.translational_frameworks_enabled:
            raise HTTPException(status_code=503, detail="framework lens is disabled")
        try:
            return NaturalSelectionArena.model_validate(await runtime.frameworks.create_arena(data))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/frameworks/naturality", response_model=list[NaturalSelectionArena])
    async def list_naturality(limit: Annotated[int, Query(ge=1, le=20_000)] = 5000) -> list[NaturalSelectionArena]:
        return [NaturalSelectionArena.model_validate(item) for item in runtime.framework_store.list_arenas(limit)]

    @app.get("/network/frameworks/naturality/{arena_id}", response_model=NaturalSelectionArena)
    async def get_naturality(arena_id: str) -> NaturalSelectionArena:
        try:
            return NaturalSelectionArena.model_validate(runtime.framework_store.get_arena(arena_id))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/network/frameworks/truth", response_model=TranslationalTruthFramework)
    async def create_truth_framework(data: TranslationalTruthFrameworkCreate) -> TranslationalTruthFramework:
        if not runtime.config.translational_frameworks_enabled:
            raise HTTPException(status_code=503, detail="framework lens is disabled")
        try:
            return TranslationalTruthFramework.model_validate(await runtime.frameworks.create_framework(data))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/frameworks/truth", response_model=list[TranslationalTruthFramework])
    async def list_truth_frameworks(limit: Annotated[int, Query(ge=1, le=20_000)] = 5000) -> list[TranslationalTruthFramework]:
        return [TranslationalTruthFramework.model_validate(item) for item in runtime.framework_store.list_frameworks(limit)]

    @app.get("/network/frameworks/truth/{framework_id}", response_model=TranslationalTruthFramework)
    async def get_truth_framework(framework_id: str) -> TranslationalTruthFramework:
        try:
            return TranslationalTruthFramework.model_validate(runtime.framework_store.get_framework(framework_id))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/network/frameworks/bridges", response_model=TruthSelectionBridge)
    async def create_bridge(data: TruthSelectionBridgeCreate) -> TruthSelectionBridge:
        if not runtime.config.translational_frameworks_enabled:
            raise HTTPException(status_code=503, detail="framework lens is disabled")
        try:
            return TruthSelectionBridge.model_validate(await runtime.frameworks.create_bridge(data))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/frameworks/bridges", response_model=list[TruthSelectionBridge])
    async def list_bridges(limit: Annotated[int, Query(ge=1, le=20_000)] = 5000) -> list[TruthSelectionBridge]:
        return [TruthSelectionBridge.model_validate(item) for item in runtime.framework_store.list_bridges(limit)]

    @app.get("/network/frameworks/bridges/{bridge_id}", response_model=TruthSelectionBridge)
    async def get_bridge(bridge_id: str) -> TruthSelectionBridge:
        try:
            return TruthSelectionBridge.model_validate(runtime.framework_store.get_bridge(bridge_id))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/network/frameworks/field", response_model=FrameworkFieldProjection)
    async def framework_field() -> FrameworkFieldProjection:
        return FrameworkFieldProjection.model_validate(runtime.framework_field())

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_framework_routes(base_api.create_app(config))


app = attach_framework_routes(base_api.app)
