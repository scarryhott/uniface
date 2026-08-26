from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import api_equality as base_api
from .backup import create_backup, list_backups, prune_backups
from .config import RuntimeConfig
from .production import Authenticator, ProductionSecurityMiddleware
from .production_web import PRODUCTION_HTML


class LoginRequest(BaseModel):
    api_key: str = Field(min_length=1)


class BackupRequest(BaseModel):
    label: str = Field(default="manual", min_length=1, max_length=80)


def attach_production(app: FastAPI) -> FastAPI:
    if getattr(app.state, "production_routes_attached", False):
        return app
    runtime = app.state.runtime
    config = runtime.config
    authenticator = Authenticator(config)
    app.state.production_routes_attached = True
    app.state.authenticator = authenticator
    app.version = "0.8.0"
    app.description += (
        "; production integration adds authenticated public sessions, role-scoped "
        "writes, realtime access control, readiness, durable backups, audit events, "
        "CORS/trusted-host boundaries, and deployment health semantics"
    )

    origins = list(config.cors_origins)
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=[
                "Authorization",
                "Content-Type",
                "X-Closure-API-Key",
                "X-Request-ID",
                "X-Closure-Signature",
            ],
            expose_headers=["X-Request-ID"],
        )
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=list(config.trusted_hosts) or ["*"],
    )
    app.add_middleware(
        ProductionSecurityMiddleware,
        config=config,
        event_store=runtime.store,
        authenticator=authenticator,
    )

    @app.get("/production", response_class=HTMLResponse, include_in_schema=False)
    async def production_entry() -> str:
        return PRODUCTION_HTML

    @app.post("/auth/login")
    async def login(data: LoginRequest, response: Response) -> dict[str, Any]:
        principal = authenticator.authenticate_api_key(data.api_key)
        if principal is None:
            raise HTTPException(status_code=401, detail="invalid API key")
        try:
            token = authenticator.issue_session(principal)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        response.set_cookie(
            "closure_session",
            token,
            max_age=int(config.session_ttl_seconds),
            httponly=True,
            secure=config.environment == "production",
            samesite="lax",
            path="/",
        )
        return {"principal": principal.to_public_dict(), "session": "created"}

    @app.post("/auth/logout")
    async def logout(response: Response) -> dict[str, str]:
        response.delete_cookie("closure_session", path="/")
        return {"session": "cleared"}

    @app.get("/auth/session")
    async def session(request: Request) -> dict[str, Any]:
        return {
            "principal": getattr(request.state, "principal", None),
            "environment": config.environment,
            "service_role": config.service_role,
        }

    @app.get("/livez")
    async def livez() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/readyz")
    async def readyz() -> Response:
        auth_ready, auth_problems = authenticator.readiness()
        problems = list(auth_problems)
        if config.environment == "production" and config.public_development_mode:
            problems.append("public development mode is enabled")
        try:
            runtime.store.get_state("cycle_count", 0)
            config.database_path.parent.mkdir(parents=True, exist_ok=True)
            probe = config.database_path.parent / ".closure-ready"
            probe.write_text("ready", encoding="utf-8")
            probe.unlink(missing_ok=True)
        except Exception as exc:
            problems.append(f"database path is not writable: {type(exc).__name__}: {exc}")
        body = {
            "status": "ready" if not problems else "not-ready",
            "environment": config.environment,
            "service_role": config.service_role,
            "auth_mode": config.auth_mode,
            "auth_ready": auth_ready,
            "problems": problems,
            "database": str(config.database_path),
            "commit": os.getenv("RAILWAY_GIT_COMMIT_SHA") or os.getenv("GIT_COMMIT_SHA"),
        }
        from fastapi.responses import JSONResponse

        return JSONResponse(body, status_code=200 if not problems else 503)

    @app.get("/admin/production")
    async def production_status() -> dict[str, Any]:
        auth_ready, auth_problems = authenticator.readiness()
        return {
            "environment": config.environment,
            "service_role": config.service_role,
            "auth_mode": config.auth_mode,
            "auth_ready": auth_ready,
            "auth_problems": auth_problems,
            "allow_anonymous_read": config.allow_anonymous_read,
            "allow_anonymous_write": config.allow_anonymous_write,
            "allow_self_registration": config.allow_self_registration,
            "public_only_mode": config.public_only_mode,
            "trusted_hosts": list(config.trusted_hosts),
            "cors_origins": list(config.cors_origins),
            "database": str(config.database_path),
            "backup_dir": str(config.backup_dir),
            "runtime": runtime.status().model_dump(mode="json"),
        }

    @app.post("/admin/backups")
    async def backup(data: BackupRequest) -> dict[str, Any]:
        manifest = create_backup(config.database_path, config.backup_dir, label=data.label)
        removed = prune_backups(config.backup_dir, keep=config.backup_keep)
        runtime.store.append_event(
            "PRODUCTION_BACKUP_CREATED",
            "backup",
            Path(manifest["backup"]).name,
            {**manifest, "pruned": removed},
        )
        return {**manifest, "pruned": removed}

    @app.get("/admin/backups")
    async def backups() -> list[dict[str, Any]]:
        return list_backups(config.backup_dir, limit=config.backup_keep)

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    config = config or RuntimeConfig()
    if config.service_role == "web":
        config.autonomy_enabled = False
    return attach_production(base_api.create_app(config))


app = create_app()
