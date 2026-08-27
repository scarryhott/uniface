from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from . import api_inversion as base_api
from .completion_models import (
    CompletionExtensionCreate,
    CompletionFieldProjection,
    CompletionMap,
    CompletionMapComposeCreate,
    CompletionMapCreate,
    CompletionSystem,
    CompletionSystemCreate,
    ReachWitness,
)
from .completion_web import COMPLETION_HTML
from .config import RuntimeConfig
from .unify_closure_models import (
    ClosurePresentationCreate,
    ReturnClosureCreate,
    ReturnClosureMapCreate,
    TwoReturnClosureCreate,
)
from .unify_closure_web import UNIFY_CLOSURE_HTML


def attach_completion_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "completion_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.completion_routes_attached = True
    app.version = "3.0.0"
    app.description += (
        "; NRRF798/799 remain the one generative completion engine, and NRRF802 "
        "is its deterministic-return interface: Closure step, unique invariant "
        "factorization, functorial closure maps, unique closure presentations, "
        "and Closure₂ are all carried by the existing completion store"
    )

    @app.get("/completion", response_class=HTMLResponse, include_in_schema=False)
    async def completion_interface() -> str:
        return COMPLETION_HTML

    @app.get("/unify-closure", response_class=HTMLResponse, include_in_schema=False)
    async def unify_closure_interface() -> str:
        return UNIFY_CLOSURE_HTML

    @app.get("/network/completion/capabilities")
    async def completion_capabilities() -> dict[str, Any]:
        return {
            **runtime.completion.capabilities(),
            "unified_closure": runtime.unify_closure.capabilities(),
        }

    @app.get("/network/completion/closure-capabilities")
    async def unified_closure_capabilities() -> dict[str, Any]:
        return runtime.unify_closure.capabilities()

    @app.post("/network/completion/closures", response_model=CompletionSystem)
    async def create_return_closure(data: ReturnClosureCreate) -> CompletionSystem:
        try:
            return CompletionSystem.model_validate(
                await runtime.unify_closure.create_return_closure(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/network/completion/closures/two-return",
        response_model=CompletionSystem,
    )
    async def create_two_return_closure(
        data: TwoReturnClosureCreate,
    ) -> CompletionSystem:
        try:
            return CompletionSystem.model_validate(
                await runtime.unify_closure.create_two_return_closure(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/network/completion/closures/maps", response_model=CompletionMap)
    async def create_return_closure_map(
        data: ReturnClosureMapCreate,
    ) -> CompletionMap:
        try:
            return CompletionMap.model_validate(
                await runtime.unify_closure.create_map(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/network/completion/closures/presentations")
    async def create_closure_presentation(
        data: ClosurePresentationCreate,
    ) -> dict[str, Any]:
        try:
            return await runtime.unify_closure.create_presentation_witness(data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/completion/closure-instances")
    async def canonical_closure_instances() -> dict[str, Any]:
        return runtime.unify_closure.projection()["canonical_instances"]

    @app.get("/network/completion/unified-field")
    async def unified_closure_field() -> dict[str, Any]:
        return runtime.unified_closure_field()

    @app.post("/network/completion/systems", response_model=CompletionSystem)
    async def create_completion_system(data: CompletionSystemCreate) -> CompletionSystem:
        if not runtime.config.translational_completion_enabled:
            raise HTTPException(status_code=503, detail="translational completion is disabled")
        try:
            return CompletionSystem.model_validate(
                await runtime.completion.create_system(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/supernet/events/{event_id}/complete",
        response_model=CompletionSystem,
    )
    async def complete_from_event(
        event_id: str, data: CompletionSystemCreate
    ) -> CompletionSystem:
        if data.source_event_id is not None and data.source_event_id != event_id:
            raise HTTPException(
                status_code=400,
                detail="source_event_id must match the event path parameter",
            )
        data.source_event_id = event_id
        try:
            return CompletionSystem.model_validate(
                await runtime.completion.create_system(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/network/completion/systems/{system_id}/extend",
        response_model=CompletionSystem,
    )
    async def extend_completion_system(
        system_id: str, data: CompletionExtensionCreate
    ) -> CompletionSystem:
        try:
            return CompletionSystem.model_validate(
                await runtime.completion.extend_system(system_id, data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/completion/systems", response_model=list[CompletionSystem])
    async def list_completion_systems(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[CompletionSystem]:
        return [
            CompletionSystem.model_validate(item)
            for item in runtime.completion_store.list_systems(limit)
        ]

    @app.get(
        "/network/completion/systems/{system_id}",
        response_model=CompletionSystem,
    )
    async def get_completion_system(system_id: str) -> CompletionSystem:
        try:
            return CompletionSystem.model_validate(
                runtime.completion_store.get_system(system_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get(
        "/network/completion/systems/{system_id}/witness",
        response_model=ReachWitness,
    )
    async def completion_witness(
        system_id: str,
        source: Annotated[str, Query(min_length=1)],
        target: Annotated[str, Query(min_length=1)],
    ) -> ReachWitness:
        try:
            return ReachWitness.model_validate(
                runtime.completion.reach_witness(system_id, source, target)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/network/completion/maps", response_model=CompletionMap)
    async def create_completion_map(data: CompletionMapCreate) -> CompletionMap:
        try:
            return CompletionMap.model_validate(await runtime.completion.create_map(data))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/network/completion/maps/compose", response_model=CompletionMap)
    async def compose_completion_maps(
        data: CompletionMapComposeCreate,
    ) -> CompletionMap:
        try:
            return CompletionMap.model_validate(
                await runtime.completion.compose_maps(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/completion/maps", response_model=list[CompletionMap])
    async def list_completion_maps(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[CompletionMap]:
        return [
            CompletionMap.model_validate(item)
            for item in runtime.completion_store.list_maps(limit)
        ]

    @app.get(
        "/network/completion/maps/{map_id}", response_model=CompletionMap
    )
    async def get_completion_map(map_id: str) -> CompletionMap:
        try:
            return CompletionMap.model_validate(runtime.completion_store.get_map(map_id))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get(
        "/network/completion/field",
        response_model=CompletionFieldProjection,
    )
    async def completion_field() -> CompletionFieldProjection:
        return CompletionFieldProjection.model_validate(runtime.completion_field())

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_completion_routes(base_api.create_app(config))


app = attach_completion_routes(base_api.app)
