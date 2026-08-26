from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from . import api_reopening as base_api
from .config import RuntimeConfig
from .translation_models import (
    TranslationCompositionCreate,
    TranslationEvent,
    TranslationEventCreate,
    TranslationFieldProjection,
    TranslationStateCreate,
)
from .translation_web import TRANSLATION_FIELD_HTML


def attach_translation_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "translation_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.translation_routes_attached = True
    app.version = "0.5.0"
    app.description += (
        "; makes source-reversible TranslationEvent the canonical live runtime "
        "primitive while treating HTTP, WebSocket, repository and webhook "
        "protocols as transport-only charts"
    )

    @app.get("/translation", response_class=HTMLResponse, include_in_schema=False)
    async def translation_interface() -> str:
        return TRANSLATION_FIELD_HTML

    @app.get("/network/translations/capabilities")
    async def translation_capabilities() -> dict[str, Any]:
        return runtime.translation.capabilities()

    @app.post("/network/translations", response_model=TranslationEvent)
    async def create_translation(data: TranslationEventCreate) -> TranslationEvent:
        try:
            translation = runtime.translation.create(data)
            runtime.translation.projection()
            return TranslationEvent.model_validate(translation)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/translations", response_model=list[TranslationEvent])
    async def list_translations(
        state: str | None = None,
        kind: str | None = None,
        limit: Annotated[int, Query(ge=1, le=100_000)] = 10_000,
    ) -> list[TranslationEvent]:
        return [
            TranslationEvent.model_validate(row)
            for row in runtime.translation_store.list_translations(
                state=state, kind=kind, limit=limit
            )
        ]

    @app.post("/network/translations/compose", response_model=TranslationEvent)
    async def compose_translations(
        data: TranslationCompositionCreate,
    ) -> TranslationEvent:
        try:
            translation = runtime.translation.compose(data)
            runtime.translation.projection()
            return TranslationEvent.model_validate(translation)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/network/translations/reconcile")
    async def reconcile_translations() -> dict[str, Any]:
        counts = runtime.translation.reconcile()
        projection = runtime.translation.projection()
        return {"reconciled": counts, "field": projection}

    @app.get(
        "/network/translations/field", response_model=TranslationFieldProjection
    )
    async def translation_field() -> TranslationFieldProjection:
        return TranslationFieldProjection.model_validate(runtime.translation_field())

    @app.get("/network/translations/{translation_id}", response_model=TranslationEvent)
    async def get_translation(translation_id: str) -> TranslationEvent:
        try:
            return TranslationEvent.model_validate(
                runtime.translation_store.get_translation(translation_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/network/translations/{translation_id}/state",
        response_model=TranslationEvent,
    )
    async def transition_translation(
        translation_id: str, data: TranslationStateCreate
    ) -> TranslationEvent:
        try:
            translation = runtime.translation.transition(translation_id, data)
            runtime.translation.projection()
            return TranslationEvent.model_validate(translation)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_translation_routes(base_api.create_app(config))


app = attach_translation_routes(base_api.app)
