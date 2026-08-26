from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from . import api as base_api
from .config import RuntimeConfig
from .reopening_models import (
    MoralConnection,
    MoralConnectionCreate,
    OrderAssessment,
    OrderedReading,
    OrderedReadingCreate,
    ReopeningFamily,
    ReopeningFamilyCreate,
    ReopeningProcess,
    ReopeningProcessCreate,
    ResidueRound,
)
from .reopening_web import REOPENING_NETWORK_HTML


def attach_reopening_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "iterated_reopening_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.iterated_reopening_routes_attached = True
    app.version = "0.4.0"
    app.description += (
        "; includes NRRF768 admissible reopening families, dependency-order "
        "readings, iterated closed residues and residue-relative moral connection"
    )

    @app.get("/reopening", response_class=HTMLResponse, include_in_schema=False)
    async def reopening_interface() -> str:
        return REOPENING_NETWORK_HTML

    @app.get("/network/reopening/capabilities")
    async def reopening_capabilities() -> dict[str, Any]:
        return runtime.iterated_reopening.capabilities()

    @app.post("/network/reopening/families", response_model=ReopeningFamily)
    async def create_reopening_family(data: ReopeningFamilyCreate) -> ReopeningFamily:
        try:
            return ReopeningFamily.model_validate(
                runtime.iterated_reopening.create_family(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/reopening/families", response_model=list[ReopeningFamily])
    async def list_reopening_families(
        problem_id: str | None = None,
        limit: Annotated[int, Query(ge=1, le=10_000)] = 5000,
    ) -> list[ReopeningFamily]:
        return [
            ReopeningFamily.model_validate(row)
            for row in runtime.iterated_reopening_store.list_families(
                problem_id=problem_id, limit=limit
            )
        ]

    @app.get(
        "/network/reopening/families/{family_id}", response_model=ReopeningFamily
    )
    async def get_reopening_family(family_id: str) -> ReopeningFamily:
        try:
            return ReopeningFamily.model_validate(
                runtime.iterated_reopening_store.get_family(family_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/network/reopening/readings", response_model=OrderedReading)
    async def create_ordered_reading(data: OrderedReadingCreate) -> OrderedReading:
        try:
            return OrderedReading.model_validate(
                await runtime.iterated_reopening.create_ordered_reading(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/reopening/readings", response_model=list[OrderedReading])
    async def list_ordered_readings(
        problem_id: str | None = None,
        limit: Annotated[int, Query(ge=1, le=10_000)] = 5000,
    ) -> list[OrderedReading]:
        return [
            OrderedReading.model_validate(row)
            for row in runtime.iterated_reopening_store.list_ordered_readings(
                problem_id=problem_id, limit=limit
            )
        ]

    @app.get(
        "/network/reopening/order-assessments",
        response_model=list[OrderAssessment],
    )
    async def list_order_assessments(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 10_000,
    ) -> list[OrderAssessment]:
        return [
            OrderAssessment.model_validate(row)
            for row in runtime.iterated_reopening_store.list_order_assessments(limit)
        ]

    @app.post("/network/reopening/processes", response_model=ReopeningProcess)
    async def create_reopening_process(data: ReopeningProcessCreate) -> ReopeningProcess:
        try:
            return ReopeningProcess.model_validate(
                runtime.iterated_reopening.create_process(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/reopening/processes", response_model=list[ReopeningProcess])
    async def list_reopening_processes(
        active_only: bool = False,
        limit: Annotated[int, Query(ge=1, le=10_000)] = 5000,
    ) -> list[ReopeningProcess]:
        return [
            ReopeningProcess.model_validate(row)
            for row in runtime.iterated_reopening_store.list_processes(
                active_only=active_only, limit=limit
            )
        ]

    @app.post(
        "/network/reopening/processes/{process_id}/advance",
        response_model=ResidueRound | None,
    )
    async def advance_reopening_process(process_id: str) -> ResidueRound | None:
        try:
            row = runtime.iterated_reopening.advance_process(process_id)
            return None if row is None else ResidueRound.model_validate(row)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/network/reopening/advance")
    async def advance_all_reopening_processes() -> dict[str, Any]:
        count = runtime.iterated_reopening.advance_active_processes(
            runtime.config.reopening_processes_per_cycle
        )
        return {
            "advanced": count,
            "projection": runtime.iterated_reopening.projection(),
        }

    @app.get("/network/reopening/rounds", response_model=list[ResidueRound])
    async def list_residue_rounds(
        process_id: str | None = None,
        limit: Annotated[int, Query(ge=1, le=20_000)] = 10_000,
    ) -> list[ResidueRound]:
        return [
            ResidueRound.model_validate(row)
            for row in runtime.iterated_reopening_store.list_rounds(
                process_id=process_id, limit=limit
            )
        ]

    @app.post(
        "/network/reopening/moral-connections", response_model=MoralConnection
    )
    async def create_moral_connection(data: MoralConnectionCreate) -> MoralConnection:
        try:
            return MoralConnection.model_validate(
                runtime.iterated_reopening.create_moral_connection(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get(
        "/network/reopening/moral-connections",
        response_model=list[MoralConnection],
    )
    async def list_moral_connections(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 10_000,
    ) -> list[MoralConnection]:
        return [
            MoralConnection.model_validate(row)
            for row in runtime.iterated_reopening_store.list_moral_connections(limit)
        ]

    @app.get("/network/reopening/field")
    async def reopening_field() -> dict[str, Any]:
        return runtime.iterated_reopening.projection()

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_reopening_routes(base_api.create_app(config))


app = attach_reopening_routes(base_api.app)
