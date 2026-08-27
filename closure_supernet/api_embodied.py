from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from . import api_framework as base_api
from .config import RuntimeConfig
from .embodied_models import (
    EmbodiedField,
    EmbodiedFieldCreate,
    EmbodiedFieldProjection,
    EmbodiedLoopSensor,
    EmbodiedLoopSensorCreate,
    EmbodiedRelation,
    EmbodiedRelationCreate,
    EmbodiedSection,
    EmbodiedSectionCreate,
)
from .embodied_web import EMBODIED_HTML


def attach_embodied_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "embodied_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.embodied_routes_attached = True
    app.version = "2.5.0"
    app.description += (
        "; the embodied eight-sheaf layer reads human interaction, Slearn, "
        "Black Mirror sensing, tokenomic AI, resources, AGI memory, first-person "
        "reports, and unknown hypotheses as one local-ball/global-hair field. "
        "Its non-scalar reciprocal-translation profile is not a physical force, "
        "emotion classifier, or resource score"
    )

    @app.get("/embodied", response_class=HTMLResponse, include_in_schema=False)
    async def embodied_interface() -> str:
        return EMBODIED_HTML

    @app.get("/network/embodied/capabilities")
    async def embodied_capabilities() -> dict[str, Any]:
        return runtime.embodied.capabilities()

    @app.post("/network/embodied/sections", response_model=EmbodiedSection)
    async def create_section(data: EmbodiedSectionCreate) -> EmbodiedSection:
        if not runtime.config.embodied_supernet_enabled:
            raise HTTPException(status_code=503, detail="embodied Supernet is disabled")
        try:
            return EmbodiedSection.model_validate(await runtime.embodied.create_section(data))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/embodied/sections", response_model=list[EmbodiedSection])
    async def list_sections(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[EmbodiedSection]:
        return [
            EmbodiedSection.model_validate(item)
            for item in runtime.embodied_store.list_sections(limit)
        ]

    @app.get("/network/embodied/sections/{section_id}", response_model=EmbodiedSection)
    async def get_section(section_id: str) -> EmbodiedSection:
        try:
            return EmbodiedSection.model_validate(runtime.embodied_store.get_section(section_id))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/network/embodied/relations", response_model=EmbodiedRelation)
    async def create_relation(data: EmbodiedRelationCreate) -> EmbodiedRelation:
        if not runtime.config.embodied_supernet_enabled:
            raise HTTPException(status_code=503, detail="embodied Supernet is disabled")
        try:
            return EmbodiedRelation.model_validate(await runtime.embodied.create_relation(data))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/embodied/relations", response_model=list[EmbodiedRelation])
    async def list_relations(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[EmbodiedRelation]:
        return [
            EmbodiedRelation.model_validate(item)
            for item in runtime.embodied_store.list_relations(limit)
        ]

    @app.get("/network/embodied/relations/{relation_id}", response_model=EmbodiedRelation)
    async def get_relation(relation_id: str) -> EmbodiedRelation:
        try:
            return EmbodiedRelation.model_validate(runtime.embodied_store.get_relation(relation_id))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/network/embodied/fields", response_model=EmbodiedField)
    async def create_field(data: EmbodiedFieldCreate) -> EmbodiedField:
        if not runtime.config.embodied_supernet_enabled:
            raise HTTPException(status_code=503, detail="embodied Supernet is disabled")
        try:
            return EmbodiedField.model_validate(await runtime.embodied.create_field(data))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/embodied/fields", response_model=list[EmbodiedField])
    async def list_fields(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[EmbodiedField]:
        return [
            EmbodiedField.model_validate(item)
            for item in runtime.embodied_store.list_fields(limit)
        ]

    @app.get("/network/embodied/fields/{field_id}", response_model=EmbodiedField)
    async def get_field(field_id: str) -> EmbodiedField:
        try:
            return EmbodiedField.model_validate(runtime.embodied_store.get_field(field_id))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/network/embodied/sensors", response_model=EmbodiedLoopSensor)
    async def create_sensor_read(data: EmbodiedLoopSensorCreate) -> EmbodiedLoopSensor:
        if not runtime.config.embodied_supernet_enabled:
            raise HTTPException(status_code=503, detail="embodied Supernet is disabled")
        try:
            return EmbodiedLoopSensor.model_validate(await runtime.embodied.create_sensor_read(data))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/embodied/sensors", response_model=list[EmbodiedLoopSensor])
    async def list_sensor_reads(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[EmbodiedLoopSensor]:
        return [
            EmbodiedLoopSensor.model_validate(item)
            for item in runtime.embodied_store.list_sensor_reads(limit)
        ]

    @app.get("/network/embodied/sensors/{read_id}", response_model=EmbodiedLoopSensor)
    async def get_sensor_read(read_id: str) -> EmbodiedLoopSensor:
        try:
            return EmbodiedLoopSensor.model_validate(runtime.embodied_store.get_sensor_read(read_id))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/network/embodied/field", response_model=EmbodiedFieldProjection)
    async def embodied_field() -> EmbodiedFieldProjection:
        return EmbodiedFieldProjection.model_validate(runtime.embodied_field())

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_embodied_routes(base_api.create_app(config))


app = attach_embodied_routes(base_api.app)
