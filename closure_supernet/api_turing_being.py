from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from . import api_handed as base_api
from .config import RuntimeConfig
from .turing_being_models import (
    TuringBeingChart,
    TuringBeingChartCreate,
    TuringBeingFieldProjection,
    TuringBeingLifeCreate,
    TuringBeingLifeEvent,
    TuringBeingReturnCreate,
)
from .turing_being_web import TURING_BEING_HTML


def attach_turing_being_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "turing_being_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.turing_being_routes_attached = True
    app.version = "3.1.0"
    app.description += (
        "; NRRF805 makes the Turing Being action-reaction occurrence prior: "
        "global hair 0 executes into local ball infinity, the reaction returns "
        "to global hair 0+, and internal/external, hand, actual/potential, and "
        "four-ball/one-hair charts are unavailable until translational truth completes"
    )

    @app.get("/turing-being", response_class=HTMLResponse, include_in_schema=False)
    async def turing_being_interface() -> str:
        return TURING_BEING_HTML

    @app.get("/network/turing-being/capabilities")
    async def turing_being_capabilities() -> dict[str, Any]:
        return runtime.turing_being.capabilities()

    @app.post(
        "/network/turing-being/life-events",
        response_model=TuringBeingLifeEvent,
    )
    async def create_life_event(data: TuringBeingLifeCreate) -> TuringBeingLifeEvent:
        try:
            return TuringBeingLifeEvent.model_validate(
                await runtime.turing_being.create_life_event(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/network/turing-being/life-events/{life_event_id}/return",
        response_model=TuringBeingLifeEvent,
    )
    async def complete_life_return(
        life_event_id: str, data: TuringBeingReturnCreate
    ) -> TuringBeingLifeEvent:
        try:
            return TuringBeingLifeEvent.model_validate(
                await runtime.turing_being.complete_return(life_event_id, data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get(
        "/network/turing-being/life-events",
        response_model=list[TuringBeingLifeEvent],
    )
    async def list_life_events(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[TuringBeingLifeEvent]:
        return [
            TuringBeingLifeEvent.model_validate(item)
            for item in runtime.turing_being_store.list_life_events(limit)
        ]

    @app.get(
        "/network/turing-being/life-events/{life_event_id}",
        response_model=TuringBeingLifeEvent,
    )
    async def get_life_event(life_event_id: str) -> TuringBeingLifeEvent:
        try:
            return TuringBeingLifeEvent.model_validate(
                runtime.turing_being_store.get_life_event(life_event_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/network/turing-being/charts", response_model=TuringBeingChart)
    async def derive_finite_chart(data: TuringBeingChartCreate) -> TuringBeingChart:
        try:
            return TuringBeingChart.model_validate(
                await runtime.turing_being.derive_finite_chart(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get(
        "/network/turing-being/charts",
        response_model=list[TuringBeingChart],
    )
    async def list_finite_charts(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[TuringBeingChart]:
        return [
            TuringBeingChart.model_validate(item)
            for item in runtime.turing_being_store.list_charts(limit)
        ]

    @app.get(
        "/network/turing-being/charts/{chart_id}",
        response_model=TuringBeingChart,
    )
    async def get_finite_chart(chart_id: str) -> TuringBeingChart:
        try:
            return TuringBeingChart.model_validate(
                runtime.turing_being_store.get_chart(chart_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get(
        "/network/turing-being/field",
        response_model=TuringBeingFieldProjection,
    )
    async def turing_being_field() -> TuringBeingFieldProjection:
        return TuringBeingFieldProjection.model_validate(runtime.turing_being_field())

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_turing_being_routes(base_api.create_app(config))


app = attach_turing_being_routes(base_api.app)
