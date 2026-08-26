from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any, Awaitable, Callable

from .models import OccurrenceCreate, Verdict
from .supernet_models import (
    IntegrationLens,
    IntegrationReceipt,
    IntegrationStage,
    IntegrationStateCreate,
    ResourceEnvelope,
)
from .supernet_store import SupernetIntegrationStore


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _stable_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


RawIngest = Callable[[OccurrenceCreate], Awaitable[dict[str, Any]]]


class SupernetIntegrator:
    """The one semantic state transition of Closure Supernet.

    Domain managers may maintain materialized compatibility views. They do not
    advance the canonical living field. Only an append-only integration receipt
    followed by ``commit_stage`` creates the next Supernet field stage.
    """

    def __init__(
        self,
        config: Any,
        occurrence_store: Any,
        translation_store: Any,
        integration_store: SupernetIntegrationStore,
        raw_ingest: RawIngest,
    ):
        self.config = config
        self.occurrence_store = occurrence_store
        self.translation_store = translation_store
        self.store = integration_store
        self.raw_ingest = raw_ingest

    def capabilities(self) -> dict[str, Any]:
        return {
            "canonical_runtime_operation": "integrate",
            "one_continuous_field": True,
            "subsystems_are_lenses": True,
            "source_append_only": True,
            "open_resource_forms": True,
            "finite_resource_registry": False,
            "canonical_language": None,
            "determination_requires_rigidity_receipt": True,
            "determination_issues_truth": False,
            "protocol_is_transport_only": True,
            "replayable": True,
            "nonterminal": True,
            "lenses": [item.value for item in IntegrationLens],
        }

    async def integrate(self, envelope: ResourceEnvelope) -> dict[str, Any]:
        if envelope.external_key:
            existing = self.store.get_by_external_key(envelope.external_key)
            if existing is not None:
                return self._receipt(
                    existing,
                    self._ensure_stage("idempotent-replay", existing["id"]),
                )

        occurrence_data = OccurrenceCreate(
            exact_text=envelope.exact_text,
            source_id=envelope.source_id,
            source_location=envelope.source_location,
            source_context=envelope.source_context,
            evidence_status=envelope.evidence_status,
            metadata={
                **envelope.metadata,
                "supernet_integrator": True,
                "authored_by": envelope.authored_by,
                "form_label": envelope.form_label,
                "language_label": envelope.language_label,
                "perspective_id": envelope.perspective_id,
                "problem_id": envelope.problem_id,
                "action_id": envelope.action_id,
                "visibility": envelope.visibility,
                "capabilities": envelope.capabilities,
                "constraints": envelope.constraints,
                "relation_hints": envelope.relation_hints,
                "causal_predecessor_ids": envelope.causal_predecessor_ids,
                "parent_event_ids": envelope.parent_event_ids,
                "affected_perspectives": envelope.affected_perspectives,
                "adapter_label": envelope.adapter_label,
            },
        )
        occurrence = await self.raw_ingest(occurrence_data)
        event, _created = self.integrate_existing_occurrence(
            occurrence,
            envelope=envelope,
            external_key=envelope.external_key or f"occurrence:{occurrence['id']}",
        )
        stage = self.commit_stage(
            trigger=f"integrate:{envelope.form_label}",
            trigger_event_id=event["id"],
        )
        return self._receipt(event, stage, occurrence=occurrence)

    def integrate_existing_occurrence(
        self,
        occurrence: dict[str, Any],
        *,
        envelope: ResourceEnvelope | None = None,
        external_key: str | None = None,
    ) -> tuple[dict[str, Any], bool]:
        metadata = dict(occurrence.get("metadata") or {})
        if envelope is None:
            envelope = ResourceEnvelope(
                exact_text=occurrence["exact_text"],
                authored_by=str(
                    metadata.get("authored_by")
                    or metadata.get("created_by")
                    or metadata.get("author_id")
                    or occurrence.get("source_id")
                    or "source"
                ),
                form_label=str(
                    metadata.get("form_label")
                    or occurrence.get("source_id")
                    or "source"
                ),
                language_label=metadata.get("language_label"),
                source_id=str(occurrence.get("source_id") or "source"),
                source_location=occurrence.get("source_location"),
                source_context=occurrence.get("source_context"),
                perspective_id=metadata.get("perspective_id"),
                problem_id=metadata.get("problem_id"),
                action_id=metadata.get("action_id"),
                visibility=str(metadata.get("visibility") or "PUBLIC"),
                capabilities=list(metadata.get("capabilities") or []),
                constraints=list(metadata.get("constraints") or []),
                relation_hints=list(metadata.get("relation_hints") or []),
                causal_predecessor_ids=list(
                    metadata.get("causal_predecessor_ids") or []
                ),
                parent_event_ids=list(metadata.get("parent_event_ids") or []),
                affected_perspectives=list(
                    metadata.get("affected_perspectives") or []
                ),
                evidence_status=occurrence.get(
                    "evidence_status", "ORIGINAL_NOTE"
                ),
                adapter_label=metadata.get("adapter_label"),
                external_key=external_key,
                metadata=metadata,
            )

        relation_hints = list(envelope.relation_hints)
        relation_hints.extend(
            str(item) for item in occurrence.get("exact_symbols", [])
        )
        relation_hints.extend(
            str(item.get("operator", item.get("kind", "")))
            for item in occurrence.get("operator_path", [])
            if isinstance(item, dict)
        )
        relation_hints = [
            item for item in dict.fromkeys(relation_hints) if item
        ]
        event, created = self.store.create_event(
            {
                "external_key": external_key
                or envelope.external_key
                or f"occurrence:{occurrence['id']}",
                "exact_source_ids": [occurrence["id"]],
                "authored_by": envelope.authored_by,
                "perspective_id": envelope.perspective_id,
                "problem_id": envelope.problem_id,
                "action_id": envelope.action_id,
                "form_label": envelope.form_label,
                "language_label": envelope.language_label,
                "visibility": envelope.visibility,
                "capabilities": envelope.capabilities,
                "constraints": envelope.constraints,
                "relation_hints": relation_hints,
                "causal_predecessor_ids": envelope.causal_predecessor_ids,
                "parent_event_ids": envelope.parent_event_ids,
                "affected_perspectives": envelope.affected_perspectives,
                "evidence_status": str(envelope.evidence_status),
                "adapter_label": envelope.adapter_label
                or self._infer_adapter(envelope.form_label, metadata),
                "metadata": {
                    **metadata,
                    "occurrence_checksum": occurrence.get("checksum"),
                    "source_id": occurrence.get("source_id"),
                    "source_context": occurrence.get("source_context"),
                    "source_location": occurrence.get("source_location"),
                    "exact_symbols": occurrence.get("exact_symbols", []),
                    "operator_path": occurrence.get("operator_path", []),
                    "canonical_runtime_operation": "integrate",
                },
            }
        )
        if created:
            self.store.append_state(
                event["id"],
                IntegrationStateCreate(
                    stage=IntegrationStage.RELATION_SENSED,
                    verdict=Verdict.OPEN,
                    reason=(
                        "The resource is related to the current field without "
                        "automatic admission"
                    ),
                    actor_id=envelope.authored_by,
                    metadata={
                        "relation_hints": relation_hints,
                        "truth_issued": False,
                    },
                ),
            )
        return self.store.get_event(event["id"]), created

    def reconcile_occurrences(self, limit: int = 100_000) -> int:
        created = 0
        for occurrence in self.occurrence_store.list_occurrences(
            limit=limit, offset=0
        ):
            _event, was_created = self.integrate_existing_occurrence(
                occurrence,
                external_key=f"occurrence:{occurrence['id']}",
            )
            created += int(was_created)
        return created

    def reconcile_translations(self, limit: int = 100_000) -> int:
        changed = 0
        stage_map = {
            "PROPOSED": (IntegrationStage.RELATION_SENSED, Verdict.OPEN),
            "INTERPRETED": (IntegrationStage.RELATION_SENSED, Verdict.OPEN),
            "ADMITTED": (IntegrationStage.ADMITTED, Verdict.TRUE),
            "RETURNED": (IntegrationStage.RETURNED, Verdict.TRUE),
            "REOPENED": (IntegrationStage.REOPENED, Verdict.OPEN),
            "REJECTED": (IntegrationStage.REJECTED, Verdict.FALSE),
        }
        for translation in self.translation_store.list_translations(
            limit=limit
        ):
            external_key = f"translation:{translation['id']}"
            event = self.store.get_by_external_key(external_key)
            if event is None:
                source_ids = list(
                    dict.fromkeys(translation.get("exact_source_ids", []))
                )
                event, _ = self.store.create_event(
                    {
                        "external_key": external_key,
                        "exact_source_ids": source_ids,
                        "authored_by": translation.get(
                            "generated_by", "translation"
                        ),
                        "perspective_id": None,
                        "problem_id": None,
                        "action_id": None,
                        "form_label": "translation",
                        "language_label": None,
                        "visibility": "PUBLIC",
                        "capabilities": [
                            "directed relational transformation"
                        ],
                        "constraints": list(
                            translation.get("untranslated", [])
                        ),
                        "relation_hints": [
                            translation.get(
                                "relation_type", "OPEN_RELATION"
                            )
                        ],
                        "causal_predecessor_ids": list(
                            translation.get(
                                "predecessor_translation_ids", []
                            )
                        ),
                        "parent_event_ids": [],
                        "affected_perspectives": list(
                            translation.get("affected_perspectives", [])
                        ),
                        "evidence_status": translation.get(
                            "evidence_status", "INTERPRETED_RELATION"
                        ),
                        "adapter_label": "translation",
                        "metadata": {
                            "canonical_translation_id": translation["id"],
                            "source_forms": translation.get(
                                "source_forms", []
                            ),
                            "target_forms": translation.get(
                                "target_forms", []
                            ),
                            "preserves": translation.get("preserves", []),
                            "transforms": translation.get("transforms", []),
                            "untranslated": translation.get(
                                "untranslated", []
                            ),
                            "frame_and_scope": translation.get(
                                "frame_and_scope"
                            ),
                            "admission_scope": translation.get(
                                "admission_scope"
                            ),
                            "transport": translation.get("transport", {}),
                            "protocol_is_transport_only": True,
                        },
                    }
                )
                changed += 1
            desired_stage, desired_verdict = stage_map.get(
                str(translation.get("current_state")),
                (IntegrationStage.RELATION_SENSED, Verdict.OPEN),
            )
            current = self.store.get_event(event["id"])
            if (
                current["current_stage"] != str(desired_stage)
                or current["current_verdict"] != str(desired_verdict)
            ):
                self.store.append_state(
                    event["id"],
                    IntegrationStateCreate(
                        stage=desired_stage,
                        verdict=desired_verdict,
                        reason=(
                            "Canonical directed TranslationEvent reconciled "
                            "into the one Supernet field"
                        ),
                        actor_id=str(
                            translation.get("generated_by", "translation")
                        ),
                        returned_resource_ids=(
                            [translation["id"]]
                            if desired_stage == IntegrationStage.RETURNED
                            else []
                        ),
                        successor_potential=list(
                            translation.get("successor_potential", [])
                        ),
                        metadata={
                            "translation_state": translation.get(
                                "current_state"
                            ),
                            "translation_verdict": translation.get(
                                "current_verdict"
                            ),
                            "truth_issued_by_determination": False,
                        },
                    ),
                )
                changed += 1
        return changed

    def reconcile(self, limit: int = 100_000) -> dict[str, int]:
        sources = self.reconcile_occurrences(limit)
        translations = self.reconcile_translations(limit)
        return {
            "sources": sources,
            "translations": translations,
            "total": sources + translations,
        }

    def transition(
        self, event_id: str, data: IntegrationStateCreate
    ) -> dict[str, Any]:
        state, _ = self.store.append_state(event_id, data)
        stage = self.commit_stage(
            trigger=f"event-state:{data.stage}",
            trigger_event_id=event_id,
        )
        return {
            "event": self.store.get_event(event_id),
            "state": state,
            "field_stage": stage,
        }

    def determine(
        self,
        event_id: str,
        *,
        actor_id: str,
        rigidity_scope: list[str],
        rigidity_receipt: dict[str, Any],
        determined_form: dict[str, Any],
        unitary_path_partition: dict[str, Any] | None = None,
        reason: str = "Rigid relation leaves one natural form standing",
    ) -> dict[str, Any]:
        return self.transition(
            event_id,
            IntegrationStateCreate(
                stage=IntegrationStage.DETERMINED,
                verdict=Verdict.OPEN,
                reason=reason,
                actor_id=actor_id,
                rigidity_scope=rigidity_scope,
                rigidity_receipt=rigidity_receipt,
                determined_form=determined_form,
                unitary_path_partition=unitary_path_partition,
                metadata={
                    "translation_event_filled": True,
                    "truth_issued": False,
                    "selector_depends_on_relation": True,
                },
            ),
        )

    def commit_stage(
        self, *, trigger: str, trigger_event_id: str | None = None
    ) -> dict[str, Any]:
        events = self.store.list_events(limit=200_000)
        source_reverse_index = {
            f"integration:{item['id']}": list(item["exact_source_ids"])
            for item in events
        }
        history_payload = [
            {
                "seq": item["seq"],
                "id": item["id"],
                "stage": item["current_stage"],
                "verdict": item["current_verdict"],
            }
            for item in events
        ]
        admitted_relations = sorted(
            (
                str(
                    item["metadata"].get(
                        "canonical_translation_id", item["id"]
                    )
                ),
                item["current_stage"],
                item["current_verdict"],
            )
            for item in events
            if item["current_verdict"] == str(Verdict.TRUE)
        )
        determinations = sorted(
            (
                item["id"],
                _stable_hash(
                    next(
                        (
                            state.get("determined_form")
                            for state in reversed(item["state_history"])
                            if state.get("determined_form") is not None
                        ),
                        None,
                    )
                ),
            )
            for item in events
            if any(
                state.get("determined_form") is not None
                for state in item["state_history"]
            )
        )
        limit_payload = {
            "exact_sources": sorted(
                {
                    source
                    for item in events
                    for source in item["exact_source_ids"]
                }
            ),
            "admitted_relations": admitted_relations,
            "determinations": determinations,
            "canonical_language": None,
        }
        counts = {
            stage.value: sum(
                1
                for item in events
                if item["current_stage"] == stage.value
            )
            for stage in IntegrationStage
        }
        lens_counts = self._lens_counts(events)
        return self.store.create_field_stage(
            {
                "trigger": trigger,
                "trigger_event_id": trigger_event_id,
                "event_ids": [item["id"] for item in events],
                "history_signature": _stable_hash(history_payload),
                "limit_signature": _stable_hash(limit_payload),
                "event_count": len(events),
                "open_count": sum(
                    1
                    for item in events
                    if item["current_verdict"] == str(Verdict.OPEN)
                ),
                "admitted_count": counts[IntegrationStage.ADMITTED.value],
                "determined_count": counts[
                    IntegrationStage.DETERMINED.value
                ],
                "returned_count": counts[IntegrationStage.RETURNED.value],
                "reopened_count": counts[IntegrationStage.REOPENED.value],
                "summary": {
                    "stage_counts": counts,
                    "lens_counts": lens_counts,
                    "subsystems_are_lenses": True,
                    "canonical_runtime_operation": "integrate",
                    "truth_issued_by_determination": False,
                    "protocol_is_transport_only": True,
                },
                "source_reverse_index": source_reverse_index,
            }
        )

    def projection(
        self, lens: IntegrationLens | str = IntegrationLens.ALL
    ) -> dict[str, Any]:
        lens = IntegrationLens(lens)
        all_events = self.store.list_events(limit=200_000)
        events = (
            all_events
            if lens == IntegrationLens.ALL
            else [
                item
                for item in all_events
                if self._lens(item) == lens.value
            ]
        )
        edges: list[dict[str, Any]] = []
        for event in events:
            for parent in event["parent_event_ids"]:
                edges.append(
                    {
                        "source": parent,
                        "target": event["id"],
                        "kind": "interaction",
                        "verdict": event["current_verdict"],
                    }
                )
            for predecessor in event["causal_predecessor_ids"]:
                edges.append(
                    {
                        "source": predecessor,
                        "target": event["id"],
                        "kind": "causal-predecessor",
                        "verdict": event["current_verdict"],
                    }
                )
            if event["metadata"].get("canonical_translation_id"):
                for source_id in event["exact_source_ids"]:
                    edges.append(
                        {
                            "source": f"occurrence:{source_id}",
                            "target": event["id"],
                            "kind": event["relation_hints"][0]
                            if event["relation_hints"]
                            else "translation",
                            "verdict": event["current_verdict"],
                        }
                    )
        stats = self.store.stats()
        stats.update(
            {
                "visible_events": len(events),
                "all_events": len(all_events),
                "open_events": sum(
                    1
                    for item in all_events
                    if item["current_verdict"] == str(Verdict.OPEN)
                ),
                "determined_events": sum(
                    1
                    for item in all_events
                    if any(
                        state.get("determined_form") is not None
                        for state in item["state_history"]
                    )
                ),
                "returned_events": sum(
                    1
                    for item in all_events
                    if item["current_stage"]
                    == str(IntegrationStage.RETURNED)
                ),
            }
        )
        projection = {
            "generated_at": utcnow(),
            "events": events,
            "edges": edges,
            "current_stage": self.store.current_stage(),
            "stages": self.store.list_stages(limit=1000),
            "lens": lens.value,
            "lens_counts": self._lens_counts(all_events),
            "stats": stats,
            "source_reverse_index": {
                f"integration:{item['id']}": list(
                    item["exact_source_ids"]
                )
                for item in events
            },
            "canonical_runtime_operation": "integrate",
            "subsystems_are_lenses": True,
            "canonical_language": None,
            "protocol_is_transport_only": True,
            "truth_issued_by_determination": False,
        }
        self.store.set_state("supernet_field_projection", projection)
        return projection

    def _receipt(
        self,
        event: dict[str, Any],
        stage: dict[str, Any],
        *,
        occurrence: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        current = self.store.get_event(event["id"])
        latest = current["state_history"][-1]
        result = IntegrationReceipt(
            event_id=current["id"],
            occurrence_ids=list(current["exact_source_ids"]),
            current_stage=current["current_stage"],
            current_verdict=current["current_verdict"],
            field_stage_id=stage["id"],
            field_stage_index=stage["stage_index"],
            history_signature=stage["history_signature"],
            limit_signature=stage["limit_signature"],
            returned_resource_ids=list(
                latest.get("returned_resource_ids") or []
            ),
            successor_potential=list(
                latest.get("successor_potential") or []
            ),
            source_reverse_index={
                f"integration:{current['id']}": list(
                    current["exact_source_ids"]
                )
            },
        ).model_dump(mode="json")
        if occurrence is not None:
            result["occurrence"] = occurrence
        return result

    def _ensure_stage(
        self, trigger: str, event_id: str | None = None
    ) -> dict[str, Any]:
        stage = self.store.current_stage()
        return (
            stage
            if stage is not None
            else self.commit_stage(
                trigger=trigger, trigger_event_id=event_id
            )
        )

    @staticmethod
    def _infer_adapter(
        form_label: str, metadata: dict[str, Any]
    ) -> str:
        explicit = metadata.get("adapter_label")
        if explicit:
            return str(explicit)
        text = " ".join(
            [
                form_label,
                str(metadata.get("source_kind", "")),
                str(metadata.get("kind", "")),
                str(metadata.get("living_form", "")),
                str(metadata.get("resource_form_label", "")),
            ]
        ).lower()
        for candidate in (
            "hardware",
            "problem",
            "resource",
            "translation",
            "reopening",
            "action",
            "equality",
            "agent",
            "selector",
        ):
            if candidate in text:
                return candidate
        return "source"

    def _lens(self, event: dict[str, Any]) -> str:
        adapter = str(event.get("adapter_label") or "").lower()
        valid = {
            item.value
            for item in IntegrationLens
            if item != IntegrationLens.ALL
        }
        if adapter in valid:
            return adapter
        return self._infer_adapter(
            event.get("form_label", "source"),
            event.get("metadata", {}),
        )

    def _lens_counts(
        self, events: list[dict[str, Any]]
    ) -> dict[str, int]:
        counts = {item.value: 0 for item in IntegrationLens}
        counts[IntegrationLens.ALL.value] = len(events)
        for event in events:
            lens = self._lens(event)
            counts[lens] = counts.get(lens, 0) + 1
        return counts
