from __future__ import annotations

import asyncio
from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from . import api_hardware as base_api
from .config import RuntimeConfig
from .supernet_models import IntegrationLens, IntegrationStateCreate, ResourceEnvelope
from .supernet_web import SUPERNET_HTML
from .topology_models import (
    CollectiveTraceCreate,
    EventRelationCreate,
    EventReopenCreate,
    EventReturnCreate,
    RigidificationCreate,
    TopologyMode,
)


def attach_supernet_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "unified_supernet_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.unified_supernet_routes_attached = True
    app.version = "2.0.0"
    app.description += (
        "; the canonical runtime operation is one continuous integrate transition; "
        "the primary interface is a zoomable topology where source, problem, "
        "resource, translation, selector, reopening, action, agent, equality, "
        "collective architecture and bounded hardware are direct-manipulation "
        "lenses over the same append-only field"
    )

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def unified_supernet_root() -> str:
        return SUPERNET_HTML

    app.router.routes.insert(0, app.router.routes.pop())

    @app.get("/supernet", response_class=HTMLResponse, include_in_schema=False)
    async def unified_supernet_interface() -> str:
        return SUPERNET_HTML

    @app.get("/supernet/capabilities")
    async def supernet_capabilities() -> dict[str, Any]:
        return {
            **runtime.supernet_integrator.capabilities(),
            "continuous_interface": runtime.topology.capabilities(),
        }

    @app.post("/supernet/integrate")
    async def integrate_resource(data: ResourceEnvelope) -> dict[str, Any]:
        try:
            return await runtime.integrate_resource(data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/events/{event_id}/interact")
    async def interact_with_event(event_id: str, data: ResourceEnvelope) -> dict[str, Any]:
        try:
            return await runtime.interact_with_event(event_id, data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/relations")
    async def create_event_relation(data: EventRelationCreate) -> dict[str, Any]:
        try:
            return await runtime.topology.create_relation(data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/collective-traces")
    async def create_collective_trace(data: CollectiveTraceCreate) -> dict[str, Any]:
        try:
            return await runtime.topology.create_collective_trace(data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/events/{event_id}/rigidify")
    async def rigidify_event(event_id: str, data: RigidificationCreate) -> dict[str, Any]:
        try:
            return runtime.topology.rigidify(event_id, data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/events/{event_id}/return")
    async def return_event(event_id: str, data: EventReturnCreate) -> dict[str, Any]:
        try:
            return await runtime.topology.return_event(event_id, data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/events/{event_id}/reopen")
    async def reopen_event(event_id: str, data: EventReopenCreate) -> dict[str, Any]:
        try:
            return runtime.topology.reopen(event_id, data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/supernet/events")
    async def list_supernet_events(
        after: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=20_000)] = 1000,
    ) -> list[dict[str, Any]]:
        return runtime.supernet_store.events_after(after, limit)

    @app.get("/supernet/events/{event_id}")
    async def get_supernet_event(event_id: str) -> dict[str, Any]:
        try:
            return runtime.supernet_store.get_event(event_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/supernet/events/{event_id}/context")
    async def get_supernet_event_context(
        event_id: str,
        depth: Annotated[int, Query(ge=0, le=6)] = 2,
    ) -> dict[str, Any]:
        try:
            return runtime.topology.event_context(event_id, depth)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/admin/supernet/events/{event_id}/state")
    async def transition_supernet_event(event_id: str, data: IntegrationStateCreate) -> dict[str, Any]:
        try:
            return runtime.supernet_integrator.transition(event_id, data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/supernet/stages")
    async def list_supernet_stages(
        limit: Annotated[int, Query(ge=1, le=10_000)] = 1000,
    ) -> list[dict[str, Any]]:
        return runtime.supernet_store.list_stages(limit)

    @app.get("/supernet/field")
    async def supernet_field() -> dict[str, Any]:
        return runtime.supernet_field()

    @app.get("/supernet/project")
    async def supernet_project(lens: IntegrationLens = IntegrationLens.ALL) -> dict[str, Any]:
        return runtime.supernet_field(lens)

    @app.get("/supernet/topology/capabilities")
    async def topology_capabilities() -> dict[str, Any]:
        return runtime.topology.capabilities()

    @app.get("/supernet/topology")
    async def supernet_topology(
        mode: TopologyMode = TopologyMode.FIELD,
        lens: IntegrationLens = IntegrationLens.ALL,
        focus_event_id: str | None = None,
    ) -> dict[str, Any]:
        return runtime.topology.projection(
            mode=mode,
            lens=lens,
            focus_event_id=focus_event_id,
        )

    @app.post("/admin/supernet/reconcile")
    async def reconcile_supernet() -> dict[str, Any]:
        reconciled = runtime.supernet_integrator.reconcile()
        stage = runtime.supernet_integrator.commit_stage(trigger="admin-reconcile")
        return {
            "reconciled": reconciled,
            "field_stage": stage,
            "field": runtime.supernet_field(),
        }

    @app.post("/admin/supernet/stage")
    async def commit_supernet_stage() -> dict[str, Any]:
        return runtime.supernet_integrator.commit_stage(trigger="admin-stage")

    @app.websocket("/supernet/stream")
    async def supernet_stream(websocket: WebSocket) -> None:
        await websocket.accept()
        after = 0
        try:
            while True:
                events = runtime.supernet_store.events_after(after, 250)
                for event in events:
                    after = max(after, int(event["seq"]))
                    await websocket.send_json(event)
                await asyncio.sleep(1)
        except WebSocketDisconnect:
            return

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_supernet_routes(base_api.create_app(config))


app = attach_supernet_routes(base_api.app)
