from __future__ import annotations

"""Executable closure field: canonical returns -> translated charts -> UI.

The published surface remains projection-only, but it no longer owns a private
return ledger. Exact returns enter the existing occurrence and integration
event stores, translated perspective readings are derived from one canonical
visual value, and the existing visual-receipt/execution tables carry lineage
and idempotency. Provenance is audited but never defines display equality.
"""

import asyncio
import hashlib
import json
import os
import sqlite3
from contextlib import asynccontextmanager, closing
from pathlib import Path
from typing import Any, AsyncIterator, Mapping

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .axiometry import extract_exact_symbols, extract_operator_path
from .closure_only_interface import CLOSURE_ONLY_SUPERNET_HTML
from .closure_ui_contract import (
    OPEN_STATUS,
    SCHEMA as CLOSURE_UI_SCHEMA,
    WITNESSED_STATUS,
    attach_perspective_closure,
    derive_closure_ui_contract,
    derive_open_ui_contract,
    validate_ui_contract,
)
from .interaction_closure import derive_interaction_closure
from .models import OccurrenceCreate, Verdict
from .nrrf843_ui_mirror import derive_nrrf843_ui_receipt
from .store import EventStore
from .supernet_models import IntegrationStage, IntegrationStateCreate
from .supernet_store import SupernetIntegrationStore
from .translational_truth_axiometry import derive_closure


VERSION = "3.22.0"
PROJECTION_RECEIPT_PROTOCOL = (
    "closure.supernet/conscious-interactive-projection-v1"
)


class TranslationalReturnRequest(BaseModel):
    """The sole mutation; client-authored truth and effect claims are forbidden."""

    model_config = ConfigDict(extra="forbid")

    return_relation_id: str = Field(min_length=1, max_length=500)
    perspective_id: str = Field(min_length=1, max_length=500)
    focus_event_id: str | None = Field(default=None, max_length=500)
    exact_source_return: str = Field(min_length=1, max_length=20_000)
    closure_equation_system_id: str = Field(min_length=25, max_length=128)
    local_projection_commitment: str = Field(min_length=25, max_length=128)
    local_perspective_hair_millidegrees: int = Field(
        default=0,
        ge=-180_000,
        le=180_000,
    )
    source_stream: str = Field(
        default="full-surface-interaction",
        min_length=1,
        max_length=240,
    )

    @field_validator("exact_source_return", "source_stream")
    @classmethod
    def source_is_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("A translational return field may not be blank")
        return value


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _digest(prefix: str, value: Any) -> str:
    content = hashlib.sha256(_stable(value).encode("utf-8")).hexdigest()
    return f"{prefix}:{content}"


def derive_local_projection_commitment(
    contract: Mapping[str, Any],
    *,
    return_relation_id: str,
    perspective_id: str,
    focus_event_id: str | None,
    exact_source_return: str,
    local_perspective_hair_millidegrees: int = 0,
) -> str:
    """Commit a browser-local amendment to its exact latent closure base."""

    body = {
        "contract_id": contract.get("id"),
        "closure_equation_system_id": (
            contract.get("closure_naturality_equations") or {}
        ).get("id"),
        "return_relation_id": return_relation_id,
        "perspective_id": perspective_id,
        "focus_event_id": focus_event_id,
        "exact_source_return": exact_source_return,
        "local_perspective_hair_millidegrees": (
            local_perspective_hair_millidegrees
        ),
        "reading_kernel": (contract.get("perspective_closure") or {}).get(
            "kernel", []
        ),
    }
    return "local-projection:" + hashlib.sha256(
        _stable(body).encode("utf-8")
    ).hexdigest()[:24]


def local_projection_commitment(
    contract: Mapping[str, Any],
    request: TranslationalReturnRequest,
) -> str:
    return derive_local_projection_commitment(
        contract,
        return_relation_id=request.return_relation_id,
        perspective_id=request.perspective_id,
        focus_event_id=request.focus_event_id,
        exact_source_return=request.exact_source_return,
        local_perspective_hair_millidegrees=(
            request.local_perspective_hair_millidegrees
        ),
    )


class TranslationalReturnLedger:
    """Compatibility facade over the canonical Supernet stores.

    The historical class name remains for callers, but no
    ``translational_returns`` or ``translational_executions`` table is created.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self.events = EventStore(self.path)
        self.supernet = SupernetIntegrationStore(self.path)
        self._migrate_legacy_returns()

    def close(self) -> None:
        self.supernet.close()
        self.events.close()

    def _migrate_legacy_returns(self) -> None:
        """Import a prior projection ledger once without deleting user data."""

        with closing(sqlite3.connect(self.path)) as connection:
            connection.row_factory = sqlite3.Row
            present = connection.execute(
                """SELECT 1 FROM sqlite_master
                WHERE type='table' AND name='translational_returns'"""
            ).fetchone()
            if present is None:
                return
            legacy_rows = connection.execute(
                "SELECT * FROM translational_returns ORDER BY seq"
            ).fetchall()

        translated_ids: dict[str, str] = {}
        for row in legacy_rows:
            legacy = dict(row)
            external_key = f"legacy-projection-return:{legacy['id']}"
            existing = self.supernet.get_by_external_key(external_key)
            if existing is not None:
                translated_ids[str(legacy["id"])] = str(existing["id"])
                continue
            occurrence = self._create_occurrence(
                exact_source=str(legacy["exact_source"]),
                source_stream="legacy",
                perspective_id=str(legacy["perspective_id"]),
                metadata={"legacy_projection_return_id": legacy["id"]},
            )
            legacy_parent = str(legacy.get("parent_return_id") or "")
            event, _ = self.supernet.create_event(
                {
                    "external_key": external_key,
                    "exact_source_ids": [occurrence["id"]],
                    "source_stream": "legacy",
                    "authored_by": str(legacy["perspective_id"]),
                    "perspective_id": str(legacy["perspective_id"]),
                    "form_label": "translational source return",
                    "visibility": "PUBLIC",
                    "parent_event_ids": (
                        [translated_ids[legacy_parent]]
                        if legacy_parent in translated_ids
                        else []
                    ),
                    "affected_perspectives": [str(legacy["perspective_id"])],
                    "metadata": {
                        "minimal_projection_return": True,
                        "legacy_projection_return_id": legacy["id"],
                        "canonical_visual_value": str(legacy["visual_value"]),
                        "prior_projection_id": legacy["prior_projection_id"],
                        "return_relation_id": legacy["return_relation_id"],
                    },
                }
            )
            self._register_closure(event["id"], source_stream="legacy")
            translated_ids[str(legacy["id"])] = str(event["id"])

    def _create_occurrence(
        self,
        *,
        exact_source: str,
        source_stream: str,
        perspective_id: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        operator_path = extract_operator_path(exact_source)
        return self.events.create_occurrence(
            OccurrenceCreate(
                exact_text=exact_source,
                source_id="closure-supernet-projection",
                source_stream=source_stream,
                source_location="full-surface-aperture",
                source_context=perspective_id,
                metadata=metadata,
            ),
            exact_symbols=extract_exact_symbols(exact_source, operator_path),
            operator_path=operator_path,
        )

    def _register_closure(self, event_id: str, *, source_stream: str) -> None:
        self.supernet.append_state(
            event_id,
            IntegrationStateCreate(
                stage=IntegrationStage.RELATION_SENSED,
                verdict=Verdict.OPEN,
                reason=(
                    "The exact return is registered in the translated closure "
                    "without issuing absolute truth"
                ),
                actor_id="closure-supernet-projection",
                metadata={
                    "closure_registering": True,
                    "source_stream": source_stream,
                    "truth_issued": False,
                },
            ),
        )

    def _exact_source(self, event: Mapping[str, Any]) -> str:
        exact_ids = [str(item) for item in event.get("exact_source_ids", [])]
        if not exact_ids:
            raise RuntimeError(
                f"event {event.get('id')} has no exact source occurrence"
            )
        exact_parts: list[str] = []
        missing: list[str] = []
        for occurrence_id in exact_ids:
            try:
                exact_parts.append(
                    str(self.events.get_occurrence(occurrence_id)["exact_text"])
                )
            except KeyError:
                missing.append(occurrence_id)
        if missing:
            raise RuntimeError(
                f"event {event.get('id')} lost exact source occurrences: "
                + ", ".join(missing)
            )
        return "\n".join(exact_parts)

    @staticmethod
    def _canonical_value(event: Mapping[str, Any]) -> str:
        metadata = event.get("metadata", {})
        if isinstance(metadata, Mapping) and metadata.get("canonical_visual_value"):
            return str(metadata["canonical_visual_value"])
        return _digest(
            "canonical-visual-value",
            {
                "event": event.get("id"),
                "exact_source_ids": event.get("exact_source_ids", []),
            },
        )

    def _return_from_event(self, event: Mapping[str, Any]) -> dict[str, Any]:
        """Decode one canonical integration event as a projection return."""

        parent_ids = [str(item) for item in event.get("parent_event_ids", [])]
        return {
            "seq": int(event["seq"]),
            "id": str(event["id"]),
            "perspective_id": str(
                event.get("perspective_id")
                or event.get("authored_by")
                or "participant"
            ),
            "exact_source": self._exact_source(event),
            "canonical_visual_value": self._canonical_value(event),
            "parent_return_id": parent_ids[-1] if parent_ids else None,
            "source_stream": str(event.get("source_stream") or "legacy"),
            "exact_source_ids": [
                str(item) for item in event.get("exact_source_ids", [])
            ],
            "metadata": dict(event.get("metadata") or {}),
            "created_at": event.get("created_at"),
        }

    def _existing_execution_occurrence(
        self,
        *,
        fingerprint: str,
        exact_source: str,
        source_stream: str,
        perspective_id: str,
    ) -> dict[str, Any] | None:
        """Find the occurrence written before a retried event append.

        Occurrence creation and integration-event creation live in existing,
        independently durable stores.  The execution fingerprint in occurrence
        metadata is therefore the recovery join when a fault lands between
        those two commits.
        """

        offset = 0
        page_size = 500
        while True:
            page = self.events.list_occurrences(
                limit=page_size,
                offset=offset,
            )
            for occurrence in page:
                metadata = occurrence.get("metadata") or {}
                if (
                    isinstance(metadata, Mapping)
                    and metadata.get("execution_fingerprint") == fingerprint
                ):
                    if (
                        occurrence.get("exact_text") != exact_source
                        or occurrence.get("source_stream") != source_stream
                        or occurrence.get("source_context") != perspective_id
                    ):
                        raise RuntimeError(
                            "the durable execution occurrence does not match "
                            "the exact retried request"
                        )
                    return occurrence
            if len(page) < page_size:
                return None
            offset += len(page)

    @staticmethod
    def _event_matches_execution(
        event: Mapping[str, Any],
        *,
        fingerprint: str,
        perspective_id: str,
        source_stream: str,
        canonical_visual_value: str,
        parent_return_id: str | None,
        prior_projection_id: str,
        return_relation_id: str,
        local_projection_commitment: str,
        closure_equation_system_id: str,
        local_perspective_hair_millidegrees: int,
    ) -> bool:
        metadata = event.get("metadata") or {}
        parent_ids = [str(item) for item in event.get("parent_event_ids", [])]
        expected_parents = [parent_return_id] if parent_return_id else []
        return bool(
            isinstance(metadata, Mapping)
            and metadata.get("execution_fingerprint") == fingerprint
            and metadata.get("prior_projection_id") == prior_projection_id
            and metadata.get("return_relation_id") == return_relation_id
            and metadata.get("local_projection_commitment")
            == local_projection_commitment
            and metadata.get("closure_equation_system_id")
            == closure_equation_system_id
            and metadata.get("local_perspective_hair_millidegrees")
            == local_perspective_hair_millidegrees
            and metadata.get("canonical_visual_value")
            == canonical_visual_value
            and str(event.get("perspective_id") or "") == perspective_id
            and str(event.get("source_stream") or "") == source_stream
            and parent_ids == expected_parents
        )

    def _ensure_closure_registered(
        self,
        event: Mapping[str, Any],
        *,
        source_stream: str,
    ) -> dict[str, Any]:
        history = event.get("state_history", [])
        registered = any(
            isinstance(state, Mapping)
            and state.get("stage") == str(IntegrationStage.RELATION_SENSED)
            and isinstance(state.get("metadata"), Mapping)
            and state["metadata"].get("closure_registering") is True
            for state in history
        )
        if not registered:
            self._register_closure(str(event["id"]), source_stream=source_stream)
            return self.supernet.get_event(str(event["id"]))
        return dict(event)

    def list_returns(self) -> list[dict[str, Any]]:
        returns: list[dict[str, Any]] = []
        offset = 0
        page_size = 1_000
        while True:
            page = self.supernet.list_events(
                limit=page_size,
                offset=offset,
            )
            for event in page:
                if str(event.get("visibility") or "PUBLIC") == "PUBLIC":
                    returns.append(self._return_from_event(event))
            if len(page) < page_size:
                break
            offset += len(page)
        return returns

    def append(
        self,
        *,
        fingerprint: str,
        perspective_id: str,
        exact_source: str,
        source_stream: str,
        canonical_visual_value: str,
        parent_return_id: str | None,
        prior_projection_id: str,
        return_relation_id: str,
        local_projection_commitment: str,
        closure_equation_system_id: str,
        local_perspective_hair_millidegrees: int,
    ) -> dict[str, Any]:
        external_key = f"projection-return:{fingerprint}"
        existing = self.supernet.get_by_external_key(external_key)
        if existing is not None:
            if not self._event_matches_execution(
                existing,
                fingerprint=fingerprint,
                perspective_id=perspective_id,
                source_stream=source_stream,
                canonical_visual_value=canonical_visual_value,
                parent_return_id=parent_return_id,
                prior_projection_id=prior_projection_id,
                return_relation_id=return_relation_id,
                local_projection_commitment=local_projection_commitment,
                closure_equation_system_id=closure_equation_system_id,
                local_perspective_hair_millidegrees=(
                    local_perspective_hair_millidegrees
                ),
            ):
                raise RuntimeError(
                    "the durable execution event does not match the exact "
                    "retried request"
                )
            event = self._ensure_closure_registered(
                existing,
                source_stream=source_stream,
            )
            returned = self._return_from_event(event)
            if returned["exact_source"] != exact_source:
                raise RuntimeError(
                    "the durable execution event lost the exact retried source"
                )
            return returned
        occurrence = self._existing_execution_occurrence(
            fingerprint=fingerprint,
            exact_source=exact_source,
            source_stream=source_stream,
            perspective_id=perspective_id,
        )
        if occurrence is None:
            occurrence = self._create_occurrence(
                exact_source=exact_source,
                source_stream=source_stream,
                perspective_id=perspective_id,
                metadata={
                    "execution_fingerprint": fingerprint,
                    "prior_projection_id": prior_projection_id,
                },
            )
        event, _ = self.supernet.create_event(
            {
                "external_key": external_key,
                "exact_source_ids": [occurrence["id"]],
                "source_stream": source_stream,
                "authored_by": perspective_id,
                "perspective_id": perspective_id,
                "form_label": "translational source return",
                "visibility": "PUBLIC",
                "parent_event_ids": (
                    [parent_return_id] if parent_return_id else []
                ),
                "affected_perspectives": [perspective_id],
                "metadata": {
                    "minimal_projection_return": True,
                    "canonical_visual_value": canonical_visual_value,
                    "prior_projection_id": prior_projection_id,
                    "return_relation_id": return_relation_id,
                    "local_projection_commitment": local_projection_commitment,
                    "closure_equation_system_id": closure_equation_system_id,
                    "local_perspective_hair_millidegrees": (
                        local_perspective_hair_millidegrees
                    ),
                    "execution_fingerprint": fingerprint,
                    "source_stream_is_equality_authority": False,
                },
            }
        )
        if not self._event_matches_execution(
            event,
            fingerprint=fingerprint,
            perspective_id=perspective_id,
            source_stream=source_stream,
            canonical_visual_value=canonical_visual_value,
            parent_return_id=parent_return_id,
            prior_projection_id=prior_projection_id,
            return_relation_id=return_relation_id,
            local_projection_commitment=local_projection_commitment,
            closure_equation_system_id=closure_equation_system_id,
            local_perspective_hair_millidegrees=(
                local_perspective_hair_millidegrees
            ),
        ):
            raise RuntimeError(
                "the recovered execution event does not match the exact request"
            )
        event = self._ensure_closure_registered(
            event,
            source_stream=source_stream,
        )
        return self._return_from_event(event)

    def replay(self, fingerprint: str) -> dict[str, Any] | None:
        execution = self.supernet.get_closure_ui_execution(fingerprint)
        if execution is None or execution.get("status") != "COMPLETED":
            return None
        response = execution.get("response")
        return dict(response) if isinstance(response, Mapping) else None

    def claim(
        self,
        *,
        fingerprint: str,
        contract_id: str,
        request: TranslationalReturnRequest,
    ) -> tuple[dict[str, Any], bool]:
        return self.supernet.claim_closure_ui_execution(
            fingerprint=fingerprint,
            contract_id=contract_id,
            action_id=request.return_relation_id,
            perspective_id=request.perspective_id,
            focus_event_id=request.focus_event_id,
            request_values=request.model_dump(),
        )

    def complete(self, fingerprint: str, response: dict[str, Any]) -> None:
        self.supernet.complete_closure_ui_execution(fingerprint, response)
        completed = self.supernet.get_closure_ui_execution(fingerprint)
        if (
            completed is None
            or completed.get("status") != "COMPLETED"
            or completed.get("response") != response
        ):
            raise RuntimeError("the closure return execution did not complete")


class MinimalProjectionRuntime:
    def __init__(self, database_path: Path):
        self.ledger = TranslationalReturnLedger(database_path)
        self.lock = asyncio.Lock()

    def close(self) -> None:
        self.ledger.close()

    @staticmethod
    def _chart_token(perspective_id: str, canonical_value: str) -> str:
        return _digest(
            "perspective-visual-value",
            {
                "perspective": perspective_id,
                "canonical": canonical_value,
            },
        )

    @classmethod
    def _perspective_family(
        cls,
        returns: list[dict[str, Any]],
        active_perspective: str,
    ) -> tuple[dict[str, dict[str, str]], list[dict[str, Any]]]:
        perspectives = sorted(
            {
                active_perspective,
                *(str(item["perspective_id"]) for item in returns),
            }
        )
        readings = {
            perspective: {
                str(item["id"]): cls._chart_token(
                    perspective,
                    str(item["canonical_visual_value"]),
                )
                for item in returns
            }
            for perspective in perspectives
        }
        translations: list[dict[str, Any]] = []
        if len(perspectives) > 1:
            anchor = perspectives[0]
            source_return_ids = [str(item["id"]) for item in returns]
            for target in perspectives[1:]:
                mapping = {
                    readings[anchor][str(item["id"])]: readings[target][
                        str(item["id"])
                    ]
                    for item in returns
                }
                translations.append(
                    {
                        "id": _digest(
                            "perspective-translation-witness",
                            {
                                "source": anchor,
                                "target": target,
                                "mapping": mapping,
                                "source_returns": source_return_ids,
                            },
                        ),
                        "source_perspective_id": anchor,
                        "target_perspective_id": target,
                        "display_translation": mapping,
                        "witnessed": True,
                        "source_return_ids": source_return_ids,
                    }
                )
        return readings, translations

    @staticmethod
    def _continuation_lineage(
        returns: list[dict[str, Any]],
        focus_event_id: str,
    ) -> list[str]:
        """Return the focused root-to-focus parent chain, rejecting breaks."""

        by_id = {str(item["id"]): item for item in returns}
        lineage: list[str] = []
        seen: set[str] = set()
        current_id: str | None = focus_event_id
        while current_id:
            if current_id in seen:
                raise RuntimeError(
                    "the focused continuation lineage contains a cycle"
                )
            current = by_id.get(current_id)
            if current is None:
                raise RuntimeError(
                    "the focused continuation lineage lost parent event "
                    f"{current_id}"
                )
            seen.add(current_id)
            lineage.append(current_id)
            parent = current.get("parent_return_id")
            current_id = str(parent) if parent else None
        lineage.reverse()
        return lineage

    @staticmethod
    def _execution_matches_request(
        execution: Mapping[str, Any],
        *,
        fingerprint: str,
        contract_id: str,
        request: TranslationalReturnRequest,
    ) -> bool:
        return bool(
            execution.get("fingerprint") == fingerprint
            and execution.get("contract_id") == contract_id
            and execution.get("action_id") == request.return_relation_id
            and execution.get("perspective_id") == request.perspective_id
            and execution.get("focus_event_id") == request.focus_event_id
            and execution.get("request_values") == request.model_dump()
        )

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
        readings, translation_inputs = self._perspective_family(
            returns,
            perspective_id,
        )
        visual_forms = [
            {
                "id": item["id"],
                "state": {
                    "source_perspective_id": item["perspective_id"],
                    "exact_visual_form": item["exact_source"],
                    "source_stream": item["source_stream"],
                    "canonical_visual_value": item["canonical_visual_value"],
                },
                "existence_provenance": item["exact_source_ids"] or [item["id"]],
                "source_return_ids": [item["id"]],
            }
            for item in returns
        ]
        truth = derive_closure(
            visual_forms,
            perspective_readings=readings,
            perspective_translations=translation_inputs,
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
                "source_stream": item["source_stream"],
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
                        "canonical_visual_value": item["canonical_visual_value"],
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
        continuation_lineage_ids = self._continuation_lineage(
            returns,
            str(focus["id"]),
        )
        contract = attach_perspective_closure(
            contract,
            perspective_closure=contract["perspective_closure"],
            continuation_index=len(continuation_lineage_ids),
            continuation_lineage_ids=continuation_lineage_ids,
        )
        validation = validate_ui_contract(contract)
        if not validation["valid"]:
            raise RuntimeError(
                "derived projection failed its exact relation audit: "
                + ", ".join(validation["errors"])
            )
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
                "source_stream": request.source_stream,
                "local_projection_commitment": (
                    request.local_projection_commitment
                ),
                "closure_equation_system_id": (
                    request.closure_equation_system_id
                ),
                "local_perspective_hair_millidegrees": (
                    request.local_perspective_hair_millidegrees
                ),
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
        execution, claimed = self.ledger.claim(
            fingerprint=fingerprint,
            contract_id=contract["id"],
            request=request,
        )
        resuming = not claimed
        if not claimed:
            if execution.get("status") == "COMPLETED" and isinstance(
                execution.get("response"), Mapping
            ):
                return dict(execution["response"]), True
            if execution.get("status") != "EXECUTING" or not (
                self._execution_matches_request(
                    execution,
                    fingerprint=fingerprint,
                    contract_id=str(contract["id"]),
                    request=request,
                )
            ):
                raise RuntimeError(
                    "the durable return execution does not match the retry"
                )

        relation = contract.get("return_relation") or {}
        focus_state_id = str(relation.get("focus_state_id") or "")
        by_id = {item["id"]: item for item in self.ledger.list_returns()}
        focus = by_id.get(focus_state_id)
        canonical_visual_value = (
            str(focus["canonical_visual_value"])
            if focus is not None
            else _digest(
                "canonical-visual-value",
                {"exact_source": request.exact_source_return},
            )
        )
        returned = self.ledger.append(
            fingerprint=fingerprint,
            perspective_id=request.perspective_id,
            exact_source=request.exact_source_return,
            source_stream=request.source_stream,
            canonical_visual_value=canonical_visual_value,
            parent_return_id=(focus_state_id or None),
            prior_projection_id=contract["id"],
            return_relation_id=request.return_relation_id,
            local_projection_commitment=request.local_projection_commitment,
            closure_equation_system_id=request.closure_equation_system_id,
            local_perspective_hair_millidegrees=(
                request.local_perspective_hair_millidegrees
            ),
        )
        successor = self.project(
            perspective_id=request.perspective_id,
            focus_event_id=returned["id"],
        )
        parent_receipt = (
            self.ledger.supernet.latest_visual_closure_receipt(focus_state_id)
            if focus_state_id
            else None
        )
        parent_receipt_ids = (
            [str(parent_receipt["id"])] if parent_receipt is not None else []
        )
        receipt_signature = _digest(
            "projection-receipt-input",
            {
                "execution": fingerprint,
                "contract": successor["id"],
                "source_stream": request.source_stream,
            },
        )
        receipt_body = {
            "protocol": PROJECTION_RECEIPT_PROTOCOL,
            "source_event_id": returned["id"],
            "source_provenance": {
                "source_stream": request.source_stream,
                "exact_source_ids": returned["exact_source_ids"],
                "source_stream_defines_equality": False,
                "source_stream_authorizes_external_effect": False,
                "local_projection_commitment": (
                    request.local_projection_commitment
                ),
                "closure_equation_system_id": (
                    request.closure_equation_system_id
                ),
                "local_perspective_hair_millidegrees": (
                    request.local_perspective_hair_millidegrees
                ),
                "local_hair_defines_equality": False,
            },
            "closure_ui_contract": successor,
            "perspective_closure": successor["perspective_closure"],
            "closure_process": successor["closure_process"],
            "truth_issued": False,
            "external_resource_admitted": False,
            "committed_local_projection": {
                "id": request.local_projection_commitment,
                "latent_contract_id": contract["id"],
                "closure_equation_system_id": (
                    request.closure_equation_system_id
                ),
                "perspective_id": request.perspective_id,
                "focus_event_id": request.focus_event_id,
                "hair_millidegrees": (
                    request.local_perspective_hair_millidegrees
                ),
                "closure_rederived": True,
            },
        }
        receipt, _ = self.ledger.supernet.append_visual_closure_receipt(
            source_event_id=str(returned["id"]),
            input_signature=receipt_signature,
            parent_receipt_ids=parent_receipt_ids,
            receipt=receipt_body,
        )
        if (
            receipt.get("input_signature") != receipt_signature
            or receipt.get("source_event_id") != returned["id"]
            or receipt.get("parent_receipt_ids") != parent_receipt_ids
            or any(receipt.get(key) != value for key, value in receipt_body.items())
        ):
            raise RuntimeError(
                "the durable visual receipt does not match the exact retry"
            )
        response = {
            "status": "RETURNED",
            "returned": True,
            "replayed": False,
            "execution_fingerprint": fingerprint,
            "prior_contract_id": contract["id"],
            "return_relation_id": request.return_relation_id,
            "focus_event_id": returned["id"],
            "visual_closure_receipt_id": receipt["id"],
            "closure_ui_contract": successor,
            "committed_local_projection": receipt_body[
                "committed_local_projection"
            ],
            "truth_issued": False,
            "external_resource_admitted": False,
        }
        self.ledger.complete(fingerprint, response)
        return response, resuming


def _database_path(config: Any | None) -> Path:
    configured = getattr(config, "database_path", None)
    return Path(
        configured
        or os.getenv("CLOSURE_DB_PATH", "runtime_data/closure_supernet.db")
    )


def create_app(config: Any | None = None) -> FastAPI:
    runtime = MinimalProjectionRuntime(_database_path(config))

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            runtime.close()

    app = FastAPI(
        title="Closure Supernet",
        version=VERSION,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )
    app.state.runtime = runtime

    @app.get("/", response_class=HTMLResponse)
    @app.get("/supernet", response_class=HTMLResponse)
    @app.get("/natural-interface", response_class=HTMLResponse)
    async def surface() -> str:
        return CLOSURE_ONLY_SUPERNET_HTML

    @app.get("/supernet/interface/capabilities")
    async def capabilities() -> dict[str, Any]:
        return {
            "protocol": CLOSURE_UI_SCHEMA,
            "surface": "ACTIVE_PERSPECTIVE_TRANSLATIONAL_VISUALIZATION",
            "input": "FULL_SURFACE_SOURCE_RETURN",
            "mutation_relations": ["SOURCE_PRESERVING_TRANSLATIONAL_RETURN"],
            "parallel_ui_routes": False,
            "parallel_mutation_routes": False,
            "truth_source": "INTERACTIVE_TRANSLATION_CLOSURE_EQUATION_SYSTEM",
            "visualization_acceptance": (
                "EXACT_LOCAL_EQUATION_AND_GEOMETRY_REDERIVATION"
            ),
            "interaction_proof": "VERIFIED_SUCCESSOR_CLOSURE_BEFORE_COMMIT",
            "latent_ui_state": "VERIFIED_CLOSURE_EQUATION_SYSTEM",
            "local_perspective": "MUTABLE_HAIR_AND_FOCUS",
            "local_modification": "UNCOMMITTED_CLOSURE_POTENTIAL",
            "commit_protocol": "LOCAL_PROJECTION_COMMITMENT_THEN_REDERIVATION",
            "interface_derivation": "INTERACTIVE_TRANSLATION_OF_CLOSURE_EQUATIONS",
            "closure_equation_protocol": (
                "closure.supernet/closure-naturality-equations-v1"
            ),
            "closure_naturality_module": (
                "NRRF866ClosureNaturalityIsTranslationalTruthIsTheGrowthOfTheUniverse"
            ),
            "browser_rederives_pull_and_growth_equations": True,
            "canonical_store": "SUPERNET_INTEGRATION_EVENT_AND_VISUAL_RECEIPT_LINEAGE",
            "lean_bridge": "NRRF859ConsciousSupernetInteractiveProjectionBridge",
            "declared_formal_continuation": (
                "NRRF862InteractiveTranslationRelativeUnityOfNaturalForms"
                "ArgumentFlowPolicePerspectiveTruthNoClosedExistence"
                "DialecticContinuation"
            ),
            "declared_formal_source_verified_by_runtime": False,
            "runtime_reproves_lean": False,
            "truth_issued": False,
            "consciousness_claimed": False,
            "external_resource_admitted": False,
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
            execution = runtime.ledger.supernet.get_closure_ui_execution(
                fingerprint
            )
            if execution is not None and execution.get("status") == "EXECUTING":
                if not runtime._execution_matches_request(
                    execution,
                    fingerprint=fingerprint,
                    contract_id=contract_id,
                    request=data,
                ):
                    raise HTTPException(
                        409,
                        "The durable execution does not match this exact retry",
                    )
                response, _resumed = runtime.append_return(
                    contract={
                        "id": contract_id,
                        "return_relation": {
                            "focus_state_id": data.focus_event_id,
                        },
                    },
                    request=data,
                )
                return {**response, "replayed": True}
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
                raise HTTPException(
                    400,
                    "The active truth constraint admits no return",
                )
            if relation.get("id") != data.return_relation_id:
                raise HTTPException(
                    400,
                    "The return is not the active projection relation",
                )
            if current.get("perspective_id") != data.perspective_id:
                raise HTTPException(
                    400,
                    "The return is not in the active perspective",
                )
            if current.get("focus_event_id") != data.focus_event_id:
                raise HTTPException(
                    400,
                    "The return is not at the active closure focus",
                )
            current_equation_id = current.get(
                "closure_naturality_equations", {}
            ).get("id")
            if current_equation_id != data.closure_equation_system_id:
                raise HTTPException(
                    400,
                    "The local projection is not based on the active closure equations",
                )
            expected_local_commitment = local_projection_commitment(
                current,
                data,
            )
            if data.local_projection_commitment != expected_local_commitment:
                raise HTTPException(
                    400,
                    "The local projection is not derived from the active closure",
                )
            response, replayed = runtime.append_return(
                contract=current,
                request=data,
            )
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


__all__ = [
    "MinimalProjectionRuntime",
    "TranslationalReturnLedger",
    "derive_local_projection_commitment",
    "local_projection_commitment",
    "app",
    "create_app",
]
