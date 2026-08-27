from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from . import api_selection as base_api
from .config import RuntimeConfig
from .inversion_models import (
    DemonConstructionCreate,
    EntanglementConstructionCreate,
    HairConstruction,
    InversionFieldProjection,
    LocalRelation,
    LocalRelationCreate,
    SingularityConstructionCreate,
    SuperpositionConstructionCreate,
)
from .inversion_web import INVERSION_HTML


def attach_inversion_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "inversion_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.inversion_routes_attached = True
    app.version = "2.7.0"
    app.description += (
        "; NRRF795/796 are live as a representation-free self-limit lens: "
        "the relation yields -transpose inversion, scale/hair/neutral sectors, "
        "one normalized hair channel and scoped construction returns without "
        "selecting a representation or issuing physical truth"
    )

    @app.get("/self-limit", response_class=HTMLResponse, include_in_schema=False)
    async def self_limit_interface() -> str:
        return INVERSION_HTML

    @app.get("/network/inversion/capabilities")
    async def inversion_capabilities() -> dict[str, Any]:
        return runtime.inversion.capabilities()

    @app.post("/network/inversion/relations", response_model=LocalRelation)
    async def create_relation(data: LocalRelationCreate) -> LocalRelation:
        if not runtime.config.inversion_self_limit_enabled:
            raise HTTPException(status_code=503, detail="inversion/self-limit lens is disabled")
        try:
            return LocalRelation.model_validate(await runtime.inversion.create_relation(data))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/supernet/events/{event_id}/self-limit",
        response_model=LocalRelation,
    )
    async def self_limit_from_event(
        event_id: str, data: LocalRelationCreate
    ) -> LocalRelation:
        if data.source_event_id is not None and data.source_event_id != event_id:
            raise HTTPException(
                status_code=400,
                detail="source_event_id must match the event path parameter",
            )
        data.source_event_id = event_id
        try:
            return LocalRelation.model_validate(await runtime.inversion.create_relation(data))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/inversion/relations", response_model=list[LocalRelation])
    async def list_relations(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[LocalRelation]:
        return [
            LocalRelation.model_validate(item)
            for item in runtime.inversion_store.list_relations(limit)
        ]

    @app.get(
        "/network/inversion/relations/{relation_id}",
        response_model=LocalRelation,
    )
    async def get_relation(relation_id: str) -> LocalRelation:
        try:
            return LocalRelation.model_validate(
                runtime.inversion_store.get_relation(relation_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/network/inversion/constructions/entanglement",
        response_model=HairConstruction,
    )
    async def create_entanglement(
        data: EntanglementConstructionCreate,
    ) -> HairConstruction:
        try:
            return HairConstruction.model_validate(
                await runtime.inversion.create_entanglement(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/network/inversion/constructions/superposition",
        response_model=HairConstruction,
    )
    async def create_superposition(
        data: SuperpositionConstructionCreate,
    ) -> HairConstruction:
        try:
            return HairConstruction.model_validate(
                await runtime.inversion.create_superposition(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/network/inversion/constructions/singularity",
        response_model=HairConstruction,
    )
    async def create_singularity(
        data: SingularityConstructionCreate,
    ) -> HairConstruction:
        try:
            return HairConstruction.model_validate(
                await runtime.inversion.create_singularity(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/network/inversion/constructions/demon",
        response_model=HairConstruction,
    )
    async def create_demon(data: DemonConstructionCreate) -> HairConstruction:
        try:
            return HairConstruction.model_validate(
                await runtime.inversion.create_demon(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get(
        "/network/inversion/constructions",
        response_model=list[HairConstruction],
    )
    async def list_constructions(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[HairConstruction]:
        return [
            HairConstruction.model_validate(item)
            for item in runtime.inversion_store.list_constructions(limit)
        ]

    @app.get(
        "/network/inversion/constructions/{construction_id}",
        response_model=HairConstruction,
    )
    async def get_construction(construction_id: str) -> HairConstruction:
        try:
            return HairConstruction.model_validate(
                runtime.inversion_store.get_construction(construction_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get(
        "/network/inversion/field",
        response_model=InversionFieldProjection,
    )
    async def inversion_field() -> InversionFieldProjection:
        return InversionFieldProjection.model_validate(runtime.inversion_field())

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_inversion_routes(base_api.create_app(config))


app = attach_inversion_routes(base_api.app)
