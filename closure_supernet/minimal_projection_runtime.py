from __future__ import annotations

"""Minimal executable Supernet: return ledger -> UI reading -> closure -> UI.

No domain manager, classifier, product ontology, action enum, recommendation
layer, token gate, or alternate interface is instantiated here.  The active
perspective visualization is the only reading from which equality and natural
forms are derived.  Returning a new source through a focused fibre gives it
that fibre's visual value; otherwise its exact source is its initial value.
"""

import asyncio
import hashlib
import json
import os
import sqlite3
import uuid
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .closure_only_interface import CLOSURE_ONLY_SUPERNET_HTML
from .closure_ui_contract import (
    OPEN_STATUS,
    RETURN_ENDPOINT_TEMPLATE,
    WITNESSED_STATUS,
    derive_closure_ui_contract,
    derive_open_ui_contract,
    validate_ui_contract,
)
from .interaction_closure import derive_interaction_closure
from .nrrf843_ui_mirror import derive_nrrf843_ui_receipt
from .translational_truth_axiometry import derive_closure


VERSION = "3.18.0"


class TranslationalReturnRequest(BaseModel):
    """The sole network mutation; it contains no domain or action selector."""

    model_config = ConfigDict(extra="forbid")

    return_relation_id: str = Field(min_length=1, max_length=500)
    perspective_id: str = Field(min_length=1, max_length=500)
    focus_event_id: str | None = Field(default=None, max_length=500)
    exact_source_return: str = Field(min_length=1, max_length=20_000)

    @field_validator("exact_source_return")
    @classmethod
    def source_is_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("A translational return may not be blank")
        return value


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()}"


def _utcnow() -> str:
    return datetime.now(UTC).isoformat()


class TranslationalReturnLedger:
    """Append-only physical/source boundary for the minimal runtime."""

    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(path)) as connection:
            connection.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS translational_returns (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    id TEXT NOT NULL UNIQUE,
                    perspective_id TEXT NOT NULL,
                    exact_source TEXT NOT NULL,
                    visual_value TEXT NOT NULL,
                    parent_return_id TEXT,
                    prior_projection_id TEXT NOT NULL,
                    return_relation_id TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS translational_executions (
                    fingerprint TEXT PRIMARY KEY,
                    response_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            connection.commit()

    def list_returns(self) -> list[dict[str, Any]]:
        with closing(sqlite3.connect(self.path)) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT * FROM translational_returns ORDER BY seq"
            ).fetchall()
        return [dict(row) for row in rows]

    def append(
        self,
        *,
        perspective_id: str,
        exact_source: str,
        visual_value: str,
        parent_return_id: str | None,
        prior_projection_id: str,
        return_relation_id: str,
    ) -> dict[str, Any]:
        return_id = f"return:{uuid.uuid4()}"
        created_at = _utcnow()
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute(
                """
                INSERT INTO translational_returns (
                    id, perspective_id, exact_source, visual_value,
                    parent_return_id, prior_projection_id,
                    return_relation_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    return_id,
                    perspective_id,
                    exact_source,
                    visual_value,
                    parent_return_id,
                    prior_projection_id,
                    return_relation_id,
                    created_at,
                ),
            )
            connection.commit()
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT * FROM translational_returns WHERE id = ?",
                (return_id,),
            ).fetchone()
        if row is None:  # pragma: no cover - sqlite insert invariant
            raise RuntimeError("return append lost its row")
        return dict(row)

    def replay(self, fingerprint: str) -> dict[str, Any] | None:
        with closing(sqlite3.connect(self.path)) as connection:
            row = connection.execute(
                "SELECT response_json FROM translational_executions WHERE fingerprint = ?",
                (fingerprint,),
            ).fetchone()
        return json.loads(row[0]) if row else None

    def complete(self, fingerprint: str, response: dict[str, Any]) -> None:
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute(
                """
                INSERT INTO translational_executions (
                    fingerprint, response_json, created_at
                ) VALUES (?, ?, ?)
                """,
                (fingerprint, _stable(response), _utcnow()),
            )
            connection.commit()


class MinimalProjectionRuntime:
    def __init__(self, database_path: Path):
        self.ledger = TranslationalReturnLedger(database_path)
        self.lock = asyncio.Lock()

    def project(
        self,
        *,
        perspective_id: str,
        focus_event_id: str | None = None,
    ) -> dict[str, Any]:
        returns = self.ledger.list_returns()
        if not returns:
            return derive_open_ui_contract(perspective_id=perspective_id)
        by_id = {str(item["id"]): item for item in returns}
        focus = by_id.get(str(focus_event_id or "")) or returns[-1]
        reading = {str(item["id"]): str(item["visual_value"]) for item in returns}
        visual_forms = [
            {
                "id": item["id"],
                "state": {
                    "perspective_id": perspective_id,
                    "source_perspective_id": item["perspective_id"],
                    "exact_visual_form": item["exact_source"],
                    "active_perspective_visual_value": reading[item["id"]],
                },
                "existence_provenance": [item["id"]],
                "source_return_ids": [item["id"]],
            }
            for item in returns
        ]
        truth = derive_closure(
            visual_forms,
            perspective_readings={perspective_id: reading},
        )
        truth_dict = truth.to_dict()
        ui = derive_nrrf843_ui_receipt(truth_derivation=truth_dict)
        journey = {
            "chosen_perspective": {
                "perspective_id": perspective_id,
                "chosen": True,
                "status": "CHOSEN",
                "choice_source": "ACTIVE_TRANSLATIONAL_VISUALIZATION",
            },
            "closed_state": {"visual_closure_id": truth.visual_truth_closure.id},
        }
        nodes = [
            {
                "id": item["id"],
                "occurrence_id": item["id"],
                "perspective_id": item["perspective_id"],
                "exact_text": item["exact_source"],
            }
            for item in returns
        ]
        edges = [
            {
                "id": _digest(
                    "translation-return",
                    {
                        "source": item["parent_return_id"],
                        "target": item["id"],
                        "visual_value": item["visual_value"],
                    },
                ),
                "source": item["parent_return_id"],
                "target": item["id"],
            }
            for item in returns
            if item["parent_return_id"] in by_id
        ]
        visual_network = {"nodes": nodes, "edges": edges}
        interaction = derive_interaction_closure(
            truth_derivation=truth_dict,
            nrrf843_ui=ui,
            nrrf842_journey=journey,
            coordination={},
            ai_translation={},
            tokenomic={},
            visual_network=visual_network,
            black_mirror={"physical_sensor_attached": False},
            network_return={},
        )
        contract = derive_closure_ui_contract(
            truth_derivation=truth_dict,
            nrrf843_ui=ui,
            nrrf842_journey=journey,
            interaction_closure=interaction,
            coordination={},
            visual_network=visual_network,
            source_occurrences=[],
            focus_event={
                "id": focus["id"],
                "perspective_id": perspective_id,
                "authored_by": perspective_id,
            },
            field_event_seq=int(returns[-1]["seq"]),
        )
        if not validate_ui_contract(contract)["valid"]:
            raise RuntimeError("derived projection failed its own exact relation audit")
        return contract

    @staticmethod
    def execution_fingerprint(
        contract_id: str,
        request: TranslationalReturnRequest,
    ) -> str:
        return _digest(
            "return-execution",
            {
                "contract": contract_id,
                "relation": request.return_relation_id,
                "perspective": request.perspective_id,
                "focus": request.focus_event_id,
                "source": request.exact_source_return,
            },
        )

    def append_return(
        self,
        *,
        contract: dict[str, Any],
        request: TranslationalReturnRequest,
    ) -> tuple[dict[str, Any], bool]:
        fingerprint = self.execution_fingerprint(contract["id"], request)
        replay = self.ledger.replay(fingerprint)
        if replay is not None:
            return replay, True
        relation = contract.get("return_relation") or {}
        focus_state_id = str(relation.get("focus_state_id") or "")
        visual_value = str(
            contract.get("projection", {}).get("reading", {}).get(focus_state_id)
            or request.exact_source_return
        )
        returned = self.ledger.append(
            perspective_id=request.perspective_id,
            exact_source=request.exact_source_return,
            visual_value=visual_value,
            parent_return_id=(focus_state_id or None),
            prior_projection_id=contract["id"],
            return_relation_id=request.return_relation_id,
        )
        successor = self.project(
            perspective_id=request.perspective_id,
            focus_event_id=returned["id"],
        )
        response = {
            "status": "RETURNED",
            "returned": True,
            "replayed": False,
            "execution_fingerprint": fingerprint,
            "prior_contract_id": contract["id"],
            "return_relation_id": request.return_relation_id,
            "focus_event_id": returned["id"],
            "closure_ui_contract": successor,
            "truth_issued": False,
        }
        self.ledger.complete(fingerprint, response)
        return response, False


def _database_path(config: Any | None) -> Path:
    configured = getattr(config, "database_path", None)
    return Path(configured or os.getenv("CLOSURE_DB_PATH", "runtime_data/closure_supernet.db"))


def create_app(config: Any | None = None) -> FastAPI:
    app = FastAPI(
        title="Closure Supernet",
        version=VERSION,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    runtime = MinimalProjectionRuntime(_database_path(config))
    app.state.runtime = runtime

    @app.get("/", response_class=HTMLResponse)
    @app.get("/supernet", response_class=HTMLResponse)
    @app.get("/natural-interface", response_class=HTMLResponse)
    async def surface() -> str:
        return CLOSURE_ONLY_SUPERNET_HTML

    @app.get("/supernet/interface/capabilities")
    async def capabilities() -> dict[str, Any]:
        return {
            "protocol": "closure.supernet/translational-visualization-v2",
            "surface": "ACTIVE_PERSPECTIVE_TRANSLATIONAL_VISUALIZATION",
            "input": "FULL_SURFACE_SOURCE_RETURN",
            "mutation_relations": ["SOURCE_PRESERVING_TRANSLATIONAL_RETURN"],
            "parallel_ui_routes": False,
            "parallel_mutation_routes": False,
            "truth_source": "PERSPECTIVE_VISUALIZATION_KERNEL",
        }

    @app.get("/supernet/interface")
    async def projection(
        perspective_id: str = "perspective",
        focus_event_id: str | None = None,
    ) -> dict[str, Any]:
        return {
            "closure_ui_contract": runtime.project(
                perspective_id=perspective_id,
                focus_event_id=focus_event_id,
            )
        }

    @app.post("/supernet/interface/projections/{contract_id}/return")
    async def append_return(
        contract_id: str,
        data: TranslationalReturnRequest,
    ) -> Any:
        async with runtime.lock:
            fingerprint = runtime.execution_fingerprint(contract_id, data)
            replay = runtime.ledger.replay(fingerprint)
            if replay is not None:
                return {**replay, "replayed": True}
            current = runtime.project(
                perspective_id=data.perspective_id,
                focus_event_id=data.focus_event_id,
            )
            if current["id"] != contract_id:
                return JSONResponse(
                    status_code=409,
                    content={
                        "status": "STALE_CONTRACT",
                        "returned": False,
                        "closure_ui_contract": current,
                    },
                )
            validation = validate_ui_contract(current)
            relation = current.get("return_relation") or {}
            if not validation["valid"]:
                raise HTTPException(400, "The active projection is invalid")
            if current["status"] not in {OPEN_STATUS, WITNESSED_STATUS}:
                raise HTTPException(400, "The active truth constraint admits no return")
            if relation.get("id") != data.return_relation_id:
                raise HTTPException(400, "The return is not the active projection relation")
            if current.get("perspective_id") != data.perspective_id:
                raise HTTPException(400, "The return is not in the active perspective")
            if current.get("focus_event_id") != data.focus_event_id:
                raise HTTPException(400, "The return is not at the active closure focus")
            response, replayed = runtime.append_return(contract=current, request=data)
            if replayed:
                response = {**response, "replayed": True}
            return response

    @app.get("/livez")
    async def live() -> dict[str, str]:
        return {"status": "live"}

    @app.get("/readyz")
    async def ready() -> dict[str, str]:
        runtime.ledger.list_returns()
        return {"status": "ready"}

    return app


app = create_app()


__all__ = ["MinimalProjectionRuntime", "TranslationalReturnLedger", "app", "create_app"]
