from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from . import api_renormalization as base_api
from .config import RuntimeConfig
from .constructive_models import (
    AxiometricForm,
    AxiometricFormCreate,
    ConstructiveFieldProjection,
    IdempotentTranslationCreate,
    TranslationChartCompareCreate,
    TranslationChartComparison,
    TranslationalClosure,
    TranslationalClosureCreate,
)
from .constructive_web import CONSTRUCTIVE_HTML


def attach_constructive_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "constructive_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.constructive_routes_attached = True
    app.version = "2.3.0"
    app.description += (
        "; NRRF783 is live as an explicit-witness constructive lens: an "
        "axiometric form carries its section as data, U2 is derived from U1, "
        "U3 is read through the defect, and translational closures use a "
        "participant-supplied base site rather than runtime choice"
    )

    @app.get("/constructive", response_class=HTMLResponse, include_in_schema=False)
    async def constructive_interface() -> str:
        return CONSTRUCTIVE_HTML

    @app.get("/network/constructive/capabilities")
    async def constructive_capabilities() -> dict[str, Any]:
        return runtime.constructive.capabilities()

    @app.post(
        "/network/constructive/forms/from-idempotent",
        response_model=AxiometricForm,
    )
    async def form_from_idempotent(
        data: IdempotentTranslationCreate,
    ) -> AxiometricForm:
        if not runtime.config.constructive_forms_enabled:
            raise HTTPException(status_code=503, detail="constructive lens is disabled")
        try:
            return AxiometricForm.model_validate(
                await runtime.constructive.create_from_idempotent(data)
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/network/constructive/forms", response_model=AxiometricForm)
    async def create_form(data: AxiometricFormCreate) -> AxiometricForm:
        if not runtime.config.constructive_forms_enabled:
            raise HTTPException(status_code=503, detail="constructive lens is disabled")
        try:
            return AxiometricForm.model_validate(
                await runtime.constructive.create_form(data)
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get(
        "/network/constructive/forms", response_model=list[AxiometricForm]
    )
    async def list_forms(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[AxiometricForm]:
        return [
            AxiometricForm.model_validate(item)
            for item in runtime.constructive_store.list_forms(limit)
        ]

    @app.get(
        "/network/constructive/forms/{form_id}", response_model=AxiometricForm
    )
    async def get_form(form_id: str) -> AxiometricForm:
        try:
            return AxiometricForm.model_validate(
                runtime.constructive_store.get_form(form_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/network/constructive/translations",
        response_model=TranslationalClosure,
    )
    async def create_translation(
        data: TranslationalClosureCreate,
    ) -> TranslationalClosure:
        if not runtime.config.constructive_forms_enabled:
            raise HTTPException(status_code=503, detail="constructive lens is disabled")
        try:
            return TranslationalClosure.model_validate(
                await runtime.constructive.create_translation(data)
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get(
        "/network/constructive/translations",
        response_model=list[TranslationalClosure],
    )
    async def list_translations(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[TranslationalClosure]:
        return [
            TranslationalClosure.model_validate(item)
            for item in runtime.constructive_store.list_translations(limit)
        ]

    @app.get(
        "/network/constructive/translations/{closure_id}",
        response_model=TranslationalClosure,
    )
    async def get_translation(closure_id: str) -> TranslationalClosure:
        try:
            return TranslationalClosure.model_validate(
                runtime.constructive_store.get_translation(closure_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/network/constructive/translations/{closure_id}/compare",
        response_model=TranslationChartComparison,
    )
    async def compare_translation(
        closure_id: str, data: TranslationChartCompareCreate
    ) -> TranslationChartComparison:
        try:
            return TranslationChartComparison.model_validate(
                await runtime.constructive.compare_chart(closure_id, data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get(
        "/network/constructive/comparisons",
        response_model=list[TranslationChartComparison],
    )
    async def list_comparisons(
        closure_id: str | None = None,
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[TranslationChartComparison]:
        return [
            TranslationChartComparison.model_validate(item)
            for item in runtime.constructive_store.list_comparisons(
                limit=limit, closure_id=closure_id
            )
        ]

    @app.get(
        "/network/constructive/field",
        response_model=ConstructiveFieldProjection,
    )
    async def constructive_field() -> ConstructiveFieldProjection:
        return ConstructiveFieldProjection.model_validate(
            runtime.constructive_field()
        )

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_constructive_routes(base_api.create_app(config))


app = attach_constructive_routes(base_api.app)
