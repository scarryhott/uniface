from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from . import api_reopening as base_api
from .config import RuntimeConfig
from .resource_models import (
    LiveResourceStage,
    ProtocolReceipt,
    ProtocolReceiptCreate,
    Resource,
    ResourceCreate,
    ResourceEngagement,
    ResourceEngagementCreate,
    ResourceFieldProjection,
    ResourceReintegration,
    ResourceReturn,
    ResourceReturnCreate,
    ResourceTranslation,
    ResourceTranslationCreate,
    ResourceTranslationDecisionCreate,
)
from .resource_web import RESOURCE_NETWORK_HTML


def attach_resource_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "live_resource_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.live_resource_routes_attached = True
    app.version = "0.5.0"
    app.description += (
        "; includes an open-form, live, self-reintegrating resource continuum "
        "whose protocol verdicts remain separate from translational truth"
    )

    @app.get("/resources", response_class=HTMLResponse, include_in_schema=False)
    async def resource_interface() -> str:
        return RESOURCE_NETWORK_HTML

    @app.get("/network/resources/capabilities")
    async def resource_capabilities() -> dict[str, Any]:
        return runtime.resource_protocol.capabilities()

    @app.post("/network/resources", response_model=Resource)
    async def create_resource(data: ResourceCreate) -> Resource:
        try:
            return Resource.model_validate(
                await runtime.resource_protocol.create_resource(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/resources", response_model=list[Resource])
    async def list_resources(
        problem_id: str | None = None,
        created_by: str | None = None,
        limit: Annotated[int, Query(ge=1, le=20_000)] = 10_000,
    ) -> list[Resource]:
        return [
            Resource.model_validate(row)
            for row in runtime.resource_store.list_resources(
                problem_id=problem_id, created_by=created_by, limit=limit
            )
        ]

    @app.get("/network/resources/{resource_id}", response_model=Resource)
    async def get_resource(resource_id: str) -> Resource:
        try:
            return Resource.model_validate(runtime.resource_store.get_resource(resource_id))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/network/resource-engagements", response_model=ResourceEngagement)
    async def create_resource_engagement(
        data: ResourceEngagementCreate,
    ) -> ResourceEngagement:
        try:
            return ResourceEngagement.model_validate(
                await runtime.resource_protocol.create_engagement(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/resource-engagements", response_model=list[ResourceEngagement])
    async def list_resource_engagements(
        resource_id: str | None = None,
        limit: Annotated[int, Query(ge=1, le=20_000)] = 10_000,
    ) -> list[ResourceEngagement]:
        return [
            ResourceEngagement.model_validate(row)
            for row in runtime.resource_store.list_engagements(
                resource_id=resource_id, limit=limit
            )
        ]

    @app.post("/network/resource-translations", response_model=ResourceTranslation)
    async def create_resource_translation(
        data: ResourceTranslationCreate,
    ) -> ResourceTranslation:
        try:
            return ResourceTranslation.model_validate(
                await runtime.resource_protocol.create_translation(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/resource-translations", response_model=list[ResourceTranslation])
    async def list_resource_translations(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 10_000,
    ) -> list[ResourceTranslation]:
        return [
            ResourceTranslation.model_validate(row)
            for row in runtime.resource_store.list_translations(limit)
        ]

    @app.post(
        "/network/resource-translations/{translation_id}/decision",
        response_model=ResourceTranslation,
    )
    async def decide_resource_translation(
        translation_id: str, data: ResourceTranslationDecisionCreate
    ) -> ResourceTranslation:
        try:
            return ResourceTranslation.model_validate(
                runtime.resource_protocol.decide_translation(translation_id, data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/network/resource-returns", response_model=ResourceReturn)
    async def create_resource_return(data: ResourceReturnCreate) -> ResourceReturn:
        try:
            return ResourceReturn.model_validate(
                await runtime.resource_protocol.create_return(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/resource-returns", response_model=list[ResourceReturn])
    async def list_resource_returns(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 10_000,
    ) -> list[ResourceReturn]:
        return [
            ResourceReturn.model_validate(row)
            for row in runtime.resource_store.list_returns(limit)
        ]

    @app.get(
        "/network/resource-reintegrations", response_model=list[ResourceReintegration]
    )
    async def list_resource_reintegrations(
        status: str | None = None,
        limit: Annotated[int, Query(ge=1, le=20_000)] = 10_000,
    ) -> list[ResourceReintegration]:
        return [
            ResourceReintegration.model_validate(row)
            for row in runtime.resource_store.list_reintegrations(
                status=status, limit=limit
            )
        ]

    @app.post("/network/resource-reintegrate")
    async def reintegrate_resources() -> dict[str, Any]:
        reintegrated = await runtime.resource_protocol.reintegrate_pending(
            runtime.config.resource_reintegrations_per_cycle
        )
        stage, created_new = runtime.resource_protocol.integrate_live_stage(
            trigger="public-resource-reintegration"
        )
        return {
            "reintegrated": reintegrated,
            "stage": stage,
            "created_new": created_new,
            "field": runtime.resource_protocol.projection(),
        }

    @app.post("/network/resource-protocol-receipts", response_model=ProtocolReceipt)
    async def create_resource_protocol_receipt(
        data: ProtocolReceiptCreate,
    ) -> ProtocolReceipt:
        try:
            return ProtocolReceipt.model_validate(
                await runtime.resource_protocol.create_protocol_receipt(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get(
        "/network/resource-protocol-receipts", response_model=list[ProtocolReceipt]
    )
    async def list_resource_protocol_receipts(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 10_000,
    ) -> list[ProtocolReceipt]:
        return [
            ProtocolReceipt.model_validate(row)
            for row in runtime.resource_store.list_protocol_receipts(limit)
        ]

    @app.post("/network/resource-live/integrate")
    async def integrate_resource_live_stage() -> dict[str, Any]:
        stage, created_new = runtime.resource_protocol.integrate_live_stage(
            trigger="public-live-integration"
        )
        return {
            "stage": LiveResourceStage.model_validate(stage),
            "created_new": created_new,
            "batch_limit_signature": runtime.resource_protocol.projection()["stats"][
                "batch_limit_signature"
            ],
        }

    @app.get("/network/resource-live/stages", response_model=list[LiveResourceStage])
    async def list_resource_live_stages(
        limit: Annotated[int, Query(ge=1, le=10_000)] = 1000,
    ) -> list[LiveResourceStage]:
        return [
            LiveResourceStage.model_validate(row)
            for row in runtime.resource_store.list_stages(limit)
        ]

    @app.get("/network/resource-field", response_model=ResourceFieldProjection)
    async def resource_field() -> ResourceFieldProjection:
        return ResourceFieldProjection.model_validate(
            runtime.resource_protocol.projection()
        )

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_resource_routes(base_api.create_app(config))


app = attach_resource_routes(base_api.app)
