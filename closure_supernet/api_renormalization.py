from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from . import api_trading as base_api
from .config import RuntimeConfig
from .renormalization_models import (
    RegularizedFamily,
    RegularizedFamilyCreate,
    RegularizedFamilyExtend,
    RenormalizationFieldProjection,
    RenormalizationScheme,
    RenormalizationSchemeCreate,
)
from .renormalization_web import RENORMALIZATION_HTML


def attach_renormalization_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "renormalization_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.renormalization_routes_attached = True
    app.version = "2.2.0"
    app.description += (
        "; NRRF781 is live as a scheme-free relative-closure lens: submitted "
        "cutoff families are checked for a common divergent component, rigid "
        "pairwise differences are determined without issuing TRUE, and "
        "renormalization schemes remain noncanonical charts"
    )

    @app.get("/renormalization", response_class=HTMLResponse, include_in_schema=False)
    async def renormalization_interface() -> str:
        return RENORMALIZATION_HTML

    @app.get("/network/renormalization/capabilities")
    async def renormalization_capabilities() -> dict[str, Any]:
        return runtime.renormalization.capabilities()

    @app.post(
        "/network/renormalization/families", response_model=RegularizedFamily
    )
    async def create_family(data: RegularizedFamilyCreate) -> RegularizedFamily:
        if not runtime.config.renormalization_enabled:
            raise HTTPException(status_code=503, detail="renormalization lens is disabled")
        try:
            return RegularizedFamily.model_validate(
                await runtime.renormalization.create_family(data)
            )
        except (KeyError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get(
        "/network/renormalization/families", response_model=list[RegularizedFamily]
    )
    async def list_families(
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[RegularizedFamily]:
        return [
            RegularizedFamily.model_validate(item)
            for item in runtime.renormalization_store.list_families(limit)
        ]

    @app.get(
        "/network/renormalization/families/{family_id}",
        response_model=RegularizedFamily,
    )
    async def get_family(family_id: str) -> RegularizedFamily:
        try:
            return RegularizedFamily.model_validate(
                runtime.renormalization_store.get_family(family_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/network/renormalization/families/{family_id}/extend",
        response_model=RegularizedFamily,
    )
    async def extend_family(
        family_id: str, data: RegularizedFamilyExtend
    ) -> RegularizedFamily:
        try:
            return RegularizedFamily.model_validate(
                await runtime.renormalization.extend_family(family_id, data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/network/renormalization/families/{family_id}/closure")
    async def get_relative_closure(family_id: str) -> dict[str, Any]:
        try:
            return runtime.renormalization.closure(family_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/network/renormalization/families/{family_id}/schemes",
        response_model=RenormalizationScheme,
    )
    async def create_scheme(
        family_id: str, data: RenormalizationSchemeCreate
    ) -> RenormalizationScheme:
        try:
            return RenormalizationScheme.model_validate(
                await runtime.renormalization.create_scheme(family_id, data)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get(
        "/network/renormalization/schemes",
        response_model=list[RenormalizationScheme],
    )
    async def list_schemes(
        family_id: str | None = None,
        limit: Annotated[int, Query(ge=1, le=20_000)] = 5000,
    ) -> list[RenormalizationScheme]:
        return [
            RenormalizationScheme.model_validate(item)
            for item in runtime.renormalization_store.list_schemes(
                limit=limit, family_id=family_id
            )
        ]

    @app.get(
        "/network/renormalization/field",
        response_model=RenormalizationFieldProjection,
    )
    async def renormalization_field() -> RenormalizationFieldProjection:
        return RenormalizationFieldProjection.model_validate(
            runtime.renormalization_field()
        )

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_renormalization_routes(base_api.create_app(config))


app = attach_renormalization_routes(base_api.app)
