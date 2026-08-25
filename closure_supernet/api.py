from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Body, FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from .config import RuntimeConfig
from .integration_models import IntegrationCreate, IntegrationRecord, IntegrationRunResult
from .models import (
    AuthorDecision,
    Occurrence,
    OccurrenceCreate,
    RuleVersion,
    RuleVersionCreate,
    RuntimeCycleResult,
    RuntimeStatus,
)
from .runtime import ClosureSupernetRuntime
from .web import DASHBOARD_HTML


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    runtime = ClosureSupernetRuntime(config)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        if runtime.config.autonomy_enabled:
            await runtime.start()
        try:
            yield
        finally:
            await runtime.stop()
            runtime.close()

    app = FastAPI(
        title="Closure Supernet Runtime",
        version="0.2.0",
        description=(
            "Source-preserving autonomous runtime and digital integration fabric "
            "for configured translational unification"
        ),
        lifespan=lifespan,
    )
    app.state.runtime = runtime

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def dashboard() -> str:
        return DASHBOARD_HTML

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "runtime": runtime.status().model_dump(mode="json"),
            "database": str(runtime.config.database_path),
            "integration_protocol": "closure.supernet/v1",
            "zero_infinity_role": "reciprocal poles",
        }

    @app.post("/occurrences", response_model=Occurrence)
    async def create_occurrence(data: OccurrenceCreate) -> Occurrence:
        return Occurrence.model_validate(await runtime.ingest(data))

    @app.get("/occurrences", response_model=list[Occurrence])
    async def list_occurrences(
        limit: Annotated[int, Query(ge=1, le=5000)] = 500,
        offset: Annotated[int, Query(ge=0)] = 0,
    ) -> list[Occurrence]:
        return [
            Occurrence.model_validate(row)
            for row in runtime.store.list_occurrences(limit=limit, offset=offset)
        ]

    @app.get("/occurrences/{occurrence_id}", response_model=Occurrence)
    async def get_occurrence(occurrence_id: str) -> Occurrence:
        try:
            return Occurrence.model_validate(runtime.store.get_occurrence(occurrence_id))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/candidate-relations")
    async def candidate_relations(
        limit: Annotated[int, Query(ge=1, le=5000)] = 1000,
    ) -> list[dict[str, Any]]:
        return runtime.store.list_candidate_relations(limit)

    @app.get("/interpretations")
    async def interpretations(
        limit: Annotated[int, Query(ge=1, le=5000)] = 1000,
    ) -> list[dict[str, Any]]:
        return runtime.store.list_interpretations(limit)

    @app.get("/admissions")
    async def admissions(
        limit: Annotated[int, Query(ge=1, le=5000)] = 1000,
    ) -> list[dict[str, Any]]:
        return runtime.store.list_admissions(limit)

    @app.post("/interpretations/{interpretation_id}/author-decision")
    async def author_decision(interpretation_id: str, data: AuthorDecision) -> dict[str, Any]:
        try:
            runtime.store.get_interpretation(interpretation_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        rule_version = (
            f"author:{data.author_id}:{runtime.store.active_rule_version()}:"
            f"{interpretation_id}:{data.verdict}"
        )
        admission, _ = runtime.store.create_admission(
            interpretation_id,
            data.verdict,
            {
                "AUTHOR_DECISION": True,
                "SOURCE_REVERSIBLE": True,
                "REOPENING_AVAILABLE": True,
            },
            data.reason,
            rule_version,
            f"author:{data.author_id}",
        )
        runtime.projection.run()
        return admission

    @app.get("/open-seams")
    async def open_seams(
        limit: Annotated[int, Query(ge=1, le=5000)] = 1000,
    ) -> list[dict[str, Any]]:
        return runtime.store.list_open_seams(limit)

    @app.get("/projection")
    async def projection() -> dict[str, Any]:
        return runtime.black_mirror()

    @app.get("/events")
    async def events(
        after: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=5000)] = 500,
    ) -> list[dict[str, Any]]:
        return runtime.store.events_after(after, limit)

    @app.post("/rules", response_model=RuleVersion)
    async def create_rule(data: RuleVersionCreate) -> RuleVersion:
        return RuleVersion.model_validate(runtime.store.create_rule_version(data))

    @app.get("/rules", response_model=list[RuleVersion])
    async def rules() -> list[RuleVersion]:
        return [RuleVersion.model_validate(row) for row in runtime.store.list_rules()]

    @app.post("/rules/{rule_db_id}/activate", response_model=RuleVersion)
    async def activate_rule(rule_db_id: str) -> RuleVersion:
        try:
            return RuleVersion.model_validate(runtime.store.activate_rule(rule_db_id))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    # Static integration routes must be registered before /integrations/{id}.
    @app.get("/integrations/capabilities")
    async def integration_capabilities() -> dict[str, Any]:
        return runtime.integrations.capabilities().model_dump(mode="json")

    @app.get("/integrations/runs", response_model=list[IntegrationRunResult])
    async def integration_runs(
        limit: Annotated[int, Query(ge=1, le=5000)] = 500,
    ) -> list[IntegrationRunResult]:
        return [
            IntegrationRunResult.model_validate(row)
            for row in runtime.integration_store.list_runs(limit)
        ]

    @app.post("/integrations", response_model=IntegrationRecord)
    async def create_integration(data: IntegrationCreate) -> IntegrationRecord:
        try:
            return runtime.integrations.create(data)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/integrations", response_model=list[IntegrationRecord])
    async def integrations(enabled_only: bool = False) -> list[IntegrationRecord]:
        return [
            IntegrationRecord.model_validate(row)
            for row in runtime.integration_store.list_integrations(enabled_only=enabled_only)
        ]

    @app.get("/integrations/{integration_id}", response_model=IntegrationRecord)
    async def get_integration(integration_id: str) -> IntegrationRecord:
        try:
            return IntegrationRecord.model_validate(
                runtime.integration_store.get_integration(integration_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/integrations/{integration_id}/enable", response_model=IntegrationRecord)
    async def enable_integration(integration_id: str) -> IntegrationRecord:
        try:
            return IntegrationRecord.model_validate(
                runtime.integration_store.set_enabled(integration_id, True)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/integrations/{integration_id}/disable", response_model=IntegrationRecord)
    async def disable_integration(integration_id: str) -> IntegrationRecord:
        try:
            return IntegrationRecord.model_validate(
                runtime.integration_store.set_enabled(integration_id, False)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/integrations/{integration_id}/poll", response_model=list[IntegrationRunResult])
    async def poll_integration(integration_id: str) -> list[IntegrationRunResult]:
        try:
            return await runtime.integrations.poll_enabled(integration_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/integrations/{integration_id}/webhook")
    async def integration_webhook(integration_id: str, request: Request) -> dict[str, Any]:
        raw_body = await request.body()
        signature = request.headers.get("X-Closure-Signature")
        try:
            return await runtime.integrations.ingest_webhook(
                integration_id, raw_body, signature
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        except (ValueError, json.JSONDecodeError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/runtime/cycle", response_model=RuntimeCycleResult)
    async def runtime_cycle() -> RuntimeCycleResult:
        return await runtime.cycle()

    @app.post("/runtime/start", response_model=RuntimeStatus)
    async def runtime_start() -> RuntimeStatus:
        await runtime.start()
        return runtime.status()

    @app.post("/runtime/stop", response_model=RuntimeStatus)
    async def runtime_stop() -> RuntimeStatus:
        await runtime.stop()
        return runtime.status()

    @app.get("/runtime/status", response_model=RuntimeStatus)
    async def runtime_status() -> RuntimeStatus:
        return runtime.status()

    @app.post("/bootstrap")
    async def bootstrap(root: Annotated[str | None, Body()] = None) -> dict[str, int]:
        count = await runtime.bootstrap_markdown(
            None if root is None else runtime.config.bootstrap_root / root
        )
        return {"ingested": count}

    @app.websocket("/ws/events")
    async def websocket_events(websocket: WebSocket) -> None:
        await websocket.accept()
        after = 0
        try:
            while True:
                recent_events = runtime.store.events_after(after, 100)
                for event in recent_events:
                    after = max(after, int(event["seq"]))
                    await websocket.send_json(event)
                await asyncio.sleep(1)
        except WebSocketDisconnect:
            return

    return app


app = create_app()
