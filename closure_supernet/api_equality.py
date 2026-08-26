from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from . import api_resource as base_api
from .config import RuntimeConfig
from .equality_models import (
    EqualityChart,
    EqualityChartCreate,
    EqualityContext,
    EqualityContextCreate,
    EqualityContextReopenCreate,
    EqualityDecisionCreate,
    RelativeEqualityCreate,
    RelativeEqualityFieldProjection,
    RelativeEqualityWitness,
    ReturnCoherence,
    ReturnCoherenceCreate,
)
from .equality_web import RELATIVE_EQUALITY_HTML


def attach_relative_equality_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "relative_equality_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.relative_equality_routes_attached = True
    app.version = "0.7.0"
    app.description += (
        "; adds witness-valued, context-indexed relative equality over directed "
        "TranslationEvents, with explicit reverse and return coherence"
    )

    @app.get("/equality", response_class=HTMLResponse, include_in_schema=False)
    async def equality_interface() -> str:
        return RELATIVE_EQUALITY_HTML

    @app.get("/network/equality/capabilities")
    async def equality_capabilities() -> dict[str, Any]:
        return runtime.relative_equality.capabilities()

    @app.post("/network/equality/contexts", response_model=EqualityContext)
    async def create_equality_context(data: EqualityContextCreate) -> EqualityContext:
        try:
            return EqualityContext.model_validate(
                runtime.relative_equality.create_context(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/equality/contexts", response_model=list[EqualityContext])
    async def list_equality_contexts(
        limit: Annotated[int, Query(ge=1, le=100_000)] = 10_000,
    ) -> list[EqualityContext]:
        return [
            EqualityContext.model_validate(row)
            for row in runtime.relative_equality_store.list_contexts(limit)
        ]

    @app.get(
        "/network/equality/contexts/{context_id}", response_model=EqualityContext
    )
    async def get_equality_context(context_id: str) -> EqualityContext:
        try:
            return EqualityContext.model_validate(
                runtime.relative_equality_store.get_context(context_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/network/equality/contexts/{context_id}/reopen",
        response_model=EqualityContext,
    )
    async def reopen_equality_context(
        context_id: str, data: EqualityContextReopenCreate
    ) -> EqualityContext:
        try:
            return EqualityContext.model_validate(
                runtime.relative_equality.reopen_context(context_id, data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/network/equality/witnesses", response_model=RelativeEqualityWitness
    )
    async def create_equality_witness(
        data: RelativeEqualityCreate,
    ) -> RelativeEqualityWitness:
        try:
            return RelativeEqualityWitness.model_validate(
                runtime.relative_equality.create_witness(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get(
        "/network/equality/witnesses", response_model=list[RelativeEqualityWitness]
    )
    async def list_equality_witnesses(
        context_id: str | None = None,
        limit: Annotated[int, Query(ge=1, le=100_000)] = 10_000,
    ) -> list[RelativeEqualityWitness]:
        return [
            RelativeEqualityWitness.model_validate(
                runtime.relative_equality.evaluate_witness(row["id"])
            )
            for row in runtime.relative_equality_store.list_witnesses(
                context_id=context_id, limit=limit
            )
        ]

    @app.get(
        "/network/equality/witnesses/{witness_id}",
        response_model=RelativeEqualityWitness,
    )
    async def get_equality_witness(witness_id: str) -> RelativeEqualityWitness:
        try:
            return RelativeEqualityWitness.model_validate(
                runtime.relative_equality.evaluate_witness(witness_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/network/equality/witnesses/{witness_id}/decision",
        response_model=RelativeEqualityWitness,
    )
    async def decide_equality_witness(
        witness_id: str, data: EqualityDecisionCreate
    ) -> RelativeEqualityWitness:
        try:
            return RelativeEqualityWitness.model_validate(
                runtime.relative_equality.decide_witness(witness_id, data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post(
        "/network/equality/coherences", response_model=ReturnCoherence
    )
    async def create_return_coherence(
        data: ReturnCoherenceCreate,
    ) -> ReturnCoherence:
        try:
            return ReturnCoherence.model_validate(
                runtime.relative_equality.create_coherence(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get(
        "/network/equality/coherences", response_model=list[ReturnCoherence]
    )
    async def list_return_coherences(
        witness_id: str | None = None,
        limit: Annotated[int, Query(ge=1, le=100_000)] = 10_000,
    ) -> list[ReturnCoherence]:
        return [
            ReturnCoherence.model_validate(
                runtime.relative_equality.evaluate_coherence(row["id"])
            )
            for row in runtime.relative_equality_store.list_coherences(
                witness_id=witness_id, limit=limit
            )
        ]

    @app.post(
        "/network/equality/coherences/{coherence_id}/decision",
        response_model=ReturnCoherence,
    )
    async def decide_return_coherence(
        coherence_id: str, data: EqualityDecisionCreate
    ) -> ReturnCoherence:
        try:
            return ReturnCoherence.model_validate(
                runtime.relative_equality.decide_coherence(coherence_id, data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/network/equality/charts", response_model=EqualityChart)
    async def create_equality_chart(data: EqualityChartCreate) -> EqualityChart:
        try:
            return EqualityChart.model_validate(
                runtime.relative_equality.create_chart(data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/equality/charts", response_model=list[EqualityChart])
    async def list_equality_charts(
        context_id: str | None = None,
        limit: Annotated[int, Query(ge=1, le=100_000)] = 10_000,
    ) -> list[EqualityChart]:
        return [
            EqualityChart.model_validate(row)
            for row in runtime.relative_equality_store.list_charts(
                context_id=context_id, limit=limit
            )
        ]

    @app.post("/network/equality/reconcile")
    async def reconcile_relative_equality() -> dict[str, Any]:
        created = runtime.reconcile_relative_equalities()
        return {
            "created": created,
            "field": runtime.relative_equality.projection(),
        }

    @app.get(
        "/network/equality/field", response_model=RelativeEqualityFieldProjection
    )
    async def relative_equality_field() -> RelativeEqualityFieldProjection:
        return RelativeEqualityFieldProjection.model_validate(
            runtime.relative_equality_field()
        )

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_relative_equality_routes(base_api.create_app(config))


app = attach_relative_equality_routes(base_api.app)
