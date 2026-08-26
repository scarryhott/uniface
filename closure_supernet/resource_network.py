from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any, Awaitable, Callable

from .config import RuntimeConfig
from .living_models import Visibility
from .living_store import LivingNetworkStore
from .models import OccurrenceCreate, RelationType, Verdict
from .resource_models import (
    ProtocolReceiptCreate,
    ResourceCreate,
    ResourceEngagementCreate,
    ResourceReturnCreate,
    ResourceTranslationCreate,
    ResourceTranslationDecisionCreate,
)
from .resource_store import ResourceStore
from .store import EventStore


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _stable_hash(value: Any) -> str:
    body = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


class LiveResourceProtocolManager:
    """Open-form, live, self-reintegrating resource translation field.

    The protocol transports and records resources, engagements and translations.
    It never treats its own receipt or handshake as translational truth. Natural
    components are generated only from currently admitted translations and are
    independent of resource labels, delivery order and any selected language.
    """

    agent_name = "live-resource-reintegration-agent"

    def __init__(
        self,
        config: RuntimeConfig,
        event_store: EventStore,
        living_store: LivingNetworkStore,
        resource_store: ResourceStore,
        ingest: Callable[[OccurrenceCreate], Awaitable[dict[str, Any]]],
    ):
        self.config = config
        self.event_store = event_store
        self.living_store = living_store
        self.store = resource_store
        self.ingest = ingest

    def capabilities(self) -> dict[str, Any]:
        return {
            "protocol": "closure.supernet/resource-v1",
            "protocol_is_closure": False,
            "protocol_is_translational_truth": False,
            "resource_forms_open": True,
            "finite_resource_registry": False,
            "canonical_language_selected": False,
            "language_labels_source_preserved": True,
            "engagement_drives_evolution": True,
            "returned_resources_self_reintegrate": True,
            "natural_unification_from_admitted_translations": True,
            "protocol_verdict_separate_from_truth": True,
            "delivery_order_preserved": True,
            "limit_signature_order_independent": True,
            "live_limit_matches_current_batch": True,
            "source_immutable": True,
            "continuum_nonterminal": True,
            "automatic_global_truth": False,
            "turing_complete_assumed": False,
        }

    def _participant(self, participant_id: str) -> dict[str, Any]:
        return self.living_store.get_participant(participant_id)

    def _validate_optional_refs(self, data: ResourceCreate) -> None:
        self._participant(data.created_by)
        if data.perspective_id:
            self.living_store.get_perspective(data.perspective_id)
        if data.problem_id:
            self.living_store.get_problem(data.problem_id)
        if data.action_id:
            self.living_store.get_action(data.action_id)
        if data.parent_resource_id:
            self.store.get_resource(data.parent_resource_id)

    async def create_resource(self, data: ResourceCreate) -> dict[str, Any]:
        self._validate_optional_refs(data)
        occurrence = await self.ingest(
            OccurrenceCreate(
                exact_text=data.exact_text,
                source_id=f"resource-participant:{data.created_by}",
                source_context=f"Open resource form: {data.form_label}",
                metadata={
                    **data.metadata,
                    "living_form": "RESOURCE",
                    "resource_form_label": data.form_label,
                    "language_label": data.language_label,
                    "resource_form_registry": False,
                    "canonical_language_selected": False,
                    "created_by": data.created_by,
                    "perspective_id": data.perspective_id,
                    "problem_id": data.problem_id,
                    "action_id": data.action_id,
                    "parent_resource_id": data.parent_resource_id,
                    "affected_perspectives": data.affected_perspectives,
                    "capabilities": data.capabilities,
                    "constraints": data.constraints,
                    "resource_is_relative_form": True,
                },
            )
        )
        resource = self.store.create_resource(data, occurrence["id"])
        self.event_store.append_event(
            "RESOURCE_FORM_CREATED",
            "resource",
            resource["id"],
            {
                "occurrence_id": occurrence["id"],
                "form_label": data.form_label,
                "language_label": data.language_label,
                "open_form": True,
            },
        )
        return resource

    async def create_engagement(
        self, data: ResourceEngagementCreate
    ) -> dict[str, Any]:
        resource = self.store.get_resource(data.resource_id)
        self._participant(data.actor_id)
        if data.perspective_id:
            self.living_store.get_perspective(data.perspective_id)
        if data.problem_id:
            self.living_store.get_problem(data.problem_id)
        occurrence = await self.ingest(
            OccurrenceCreate(
                exact_text=data.exact_text,
                source_id=f"resource-engagement:{data.actor_id}",
                source_context=(
                    f"Active engagement '{data.engagement_label}' with resource "
                    f"{data.resource_id}"
                ),
                metadata={
                    **data.metadata,
                    "living_form": "RESOURCE_ENGAGEMENT",
                    "resource_id": data.resource_id,
                    "source_resource_occurrence_id": resource["occurrence_id"],
                    "engagement_label": data.engagement_label,
                    "language_label": data.language_label,
                    "preserves": data.preserves,
                    "transforms": data.transforms,
                    "omits": data.omits,
                    "engagement_reopens_resource": True,
                },
            )
        )
        engagement = self.store.create_engagement(data, occurrence["id"])
        self.event_store.append_event(
            "RESOURCE_ENGAGEMENT_CREATED",
            "resource_engagement",
            engagement["id"],
            {
                "resource_id": data.resource_id,
                "occurrence_id": occurrence["id"],
                "engagement_label": data.engagement_label,
                "nonterminal": True,
            },
        )
        return engagement

    async def create_translation(
        self, data: ResourceTranslationCreate
    ) -> dict[str, Any]:
        source = self.store.get_resource(data.source_resource_id)
        target = self.store.get_resource(data.target_resource_id)
        self._participant(data.authored_by)
        occurrence = await self.ingest(
            OccurrenceCreate(
                exact_text=data.exact_text,
                source_id=f"resource-translation:{data.authored_by}",
                source_context=(
                    f"Resource translation {data.source_resource_id} -> "
                    f"{data.target_resource_id}"
                ),
                metadata={
                    **data.metadata,
                    "living_form": "RESOURCE_TRANSLATION",
                    "relation_label": data.relation_label,
                    "source_resource_id": data.source_resource_id,
                    "target_resource_id": data.target_resource_id,
                    "source_frame": data.source_frame,
                    "target_frame": data.target_frame,
                    "source_language": data.source_language,
                    "target_language": data.target_language,
                    "faithfulness": data.faithfulness,
                    "protocol_verdict": data.protocol_verdict,
                    "protocol_verdict_is_not_truth": True,
                    "preserved": data.preserved,
                    "transformed": data.transformed,
                    "omitted": data.omitted,
                    "canonical_language_selected": False,
                },
            )
        )
        values = list(data.faithfulness.values())
        retrieval_score = 0.5 if not values else max(0.0, min(1.0, sum(values) / len(values)))
        candidate, _created = self.event_store.create_candidate_relation(
            source["occurrence_id"],
            target["occurrence_id"],
            str(RelationType.FRAME_TRANSLATION),
            retrieval_score,
            (
                "An authored resource translation proposes that two open forms "
                "can read one another; protocol delivery is recorded separately "
                "and the relation remains OPEN until admitted"
            ),
            proposed_by=f"resource:{data.authored_by}",
        )
        translation = self.store.create_translation(
            data, occurrence["id"], candidate["id"]
        )
        self.event_store.create_open_seam(
            source["occurrence_id"],
            target["occurrence_id"],
            "Resource translation remains OPEN until relative admission; no wire verdict creates truth",
            metadata={
                "resource_translation_id": translation["id"],
                "protocol_verdict": data.protocol_verdict,
                "transport_label": data.transport_label,
                "language_pair": [data.source_language, data.target_language],
            },
        )
        self.event_store.append_event(
            "RESOURCE_TRANSLATION_PROPOSED",
            "resource_translation",
            translation["id"],
            {
                "candidate_relation_id": candidate["id"],
                "source_resource_id": data.source_resource_id,
                "target_resource_id": data.target_resource_id,
                "protocol_verdict": data.protocol_verdict,
                "truth_verdict": str(Verdict.OPEN),
            },
        )
        return translation

    def decide_translation(
        self, translation_id: str, data: ResourceTranslationDecisionCreate
    ) -> dict[str, Any]:
        self._participant(data.decided_by)
        translation = self.store.decide_translation(translation_id, data)
        self.event_store.append_event(
            "RESOURCE_TRANSLATION_DECIDED",
            "resource_translation",
            translation_id,
            {
                "verdict": str(data.verdict),
                "scope": data.scope,
                "decided_by": data.decided_by,
                "protocol_verdict": translation["protocol_verdict"],
                "protocol_verdict_is_not_truth": True,
            },
        )
        return translation

    async def create_protocol_receipt(
        self, data: ProtocolReceiptCreate
    ) -> dict[str, Any]:
        self.store.get_resource(data.resource_id)
        self._participant(data.recorded_by)
        occurrence = await self.ingest(
            OccurrenceCreate(
                exact_text=data.exact_receipt,
                source_id=f"resource-protocol:{data.recorded_by}",
                source_context=f"Protocol receipt via {data.transport_label}",
                metadata={
                    **data.metadata,
                    "living_form": "PROTOCOL_RECEIPT",
                    "resource_id": data.resource_id,
                    "transport_label": data.transport_label,
                    "wire_reference": data.wire_reference,
                    "protocol_verdict": data.protocol_verdict,
                    "protocol_verdict_is_not_translational_truth": True,
                },
            )
        )
        receipt = self.store.create_protocol_receipt(data, occurrence["id"])
        self.event_store.append_event(
            "RESOURCE_PROTOCOL_RECEIPT_RECORDED",
            "protocol_receipt",
            receipt["id"],
            {
                "resource_id": data.resource_id,
                "protocol_verdict": data.protocol_verdict,
                "truth_unchanged": True,
            },
        )
        return receipt

    async def create_return(self, data: ResourceReturnCreate) -> dict[str, Any]:
        engagement = self.store.get_engagement(data.engagement_id)
        source = self.store.get_resource(engagement["resource_id"])
        self._participant(data.authored_by)
        returned_resource = await self.create_resource(
            ResourceCreate(
                exact_text=data.exact_text,
                created_by=data.authored_by,
                form_label=data.form_label,
                language_label=data.language_label,
                perspective_id=engagement["perspective_id"],
                problem_id=engagement["problem_id"] or source["problem_id"],
                action_id=source["action_id"],
                parent_resource_id=source["id"],
                visibility=Visibility(engagement["visibility"]),
                affected_perspectives=sorted(
                    set(source["affected_perspectives"])
                    | set(engagement["affected_perspectives"])
                    | set(data.affected_perspectives)
                ),
                capabilities=data.capabilities,
                constraints=data.constraints,
                metadata={
                    **data.metadata,
                    "returned_from_engagement_id": data.engagement_id,
                    "return_is_new_resource_form": True,
                    "return_is_not_terminal": True,
                    "evidence_status": str(data.evidence_status),
                    "source_location": data.source_location,
                },
            )
        )
        returned = self.store.create_return(
            engagement_id=data.engagement_id,
            source_resource_id=source["id"],
            returned_resource_id=returned_resource["id"],
            occurrence_id=returned_resource["occurrence_id"],
            authored_by=data.authored_by,
            affected_perspectives=returned_resource["affected_perspectives"],
            evidence_status=str(data.evidence_status),
            metadata={
                **data.metadata,
                "source_resource_id": source["id"],
                "returned_resource_id": returned_resource["id"],
            },
        )
        self.event_store.append_event(
            "RESOURCE_RETURN_CREATED",
            "resource_return",
            returned["id"],
            {
                "engagement_id": data.engagement_id,
                "source_resource_id": source["id"],
                "returned_resource_id": returned_resource["id"],
                "reintegration_status": "PENDING",
            },
        )
        return returned

    async def reintegrate_pending(self, limit: int | None = None) -> int:
        limit = limit or self.config.resource_reintegrations_per_cycle
        created = 0
        for reintegration in self.store.list_reintegrations(
            status="PENDING", limit=limit
        ):
            source = self.store.get_resource(reintegration["source_resource_id"])
            target = self.store.get_resource(reintegration["returned_resource_id"])
            returned = self.store.get_return(reintegration["return_id"])
            translation = await self.create_translation(
                ResourceTranslationCreate(
                    source_resource_id=source["id"],
                    target_resource_id=target["id"],
                    authored_by=returned["authored_by"],
                    exact_text=(
                        "Active engagement returned this resource form to its source; "
                        "the relation is proposed for reintegration without erasing either occurrence."
                    ),
                    relation_label="self-reintegrating resource return",
                    source_frame=source["form_label"],
                    target_frame=target["form_label"],
                    source_language=source["language_label"],
                    target_language=target["language_label"],
                    preserved=[
                        "exact source resource occurrence",
                        "exact returned resource occurrence",
                        "authorship",
                        "engagement history",
                        "source reversibility",
                    ],
                    transformed=[
                        "the return becomes a new participant-relative resource form",
                        "future engagement may be conditioned by the returned consequence",
                    ],
                    omitted=[],
                    faithfulness={
                        "source_preservation": 1.0,
                        "authorship": 1.0,
                        "semantic_completion": 0.0,
                    },
                    affected_perspectives=reint reintegration["affected_perspectives"] if False else reintegration["affected_perspectives"],
                    protocol_verdict=None,
                    transport_label=None,
                    visibility=Visibility(target["visibility"]),
                    metadata={
                        "resource_reintegration_id": reintegration["id"],
                        "return_id": reintegration["return_id"],
                        "automatic_truth": False,
                    },
                )
            )
            completed = self.store.complete_reintegration(
                reintegration["id"],
                translation_id=translation["id"],
                candidate_relation_id=translation["candidate_relation_id"],
            )
            self.event_store.append_event(
                "RESOURCE_RETURN_REINTEGRATED",
                "resource_reintegration",
                completed["id"],
                {
                    "translation_id": translation["id"],
                    "status": completed["status"],
                    "truth_verdict": str(Verdict.OPEN),
                    "continuum_reopened": True,
                },
            )
            created += 1
        return created

    # ------------------------------------------------------------------
    # Natural unification and live stages
    # ------------------------------------------------------------------

    @staticmethod
    def _components(
        resources: list[dict[str, Any]],
        translations: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        parent = {row["id"]: row["id"] for row in resources}

        def find(value: str) -> str:
            while parent[value] != value:
                parent[value] = parent[parent[value]]
                value = parent[value]
            return value

        def union(left: str, right: str) -> None:
            a, b = find(left), find(right)
            if a != b:
                parent[max(a, b)] = min(a, b)

        for translation in translations:
            if translation["current_verdict"] == str(Verdict.TRUE):
                union(
                    translation["source_resource_id"],
                    translation["target_resource_id"],
                )

        grouped: dict[str, list[dict[str, Any]]] = {}
        for resource in resources:
            grouped.setdefault(find(resource["id"]), []).append(resource)

        components: list[dict[str, Any]] = []
        for index, members in enumerate(
            sorted(grouped.values(), key=lambda group: min(row["id"] for row in group))
        ):
            member_ids = sorted(row["id"] for row in members)
            components.append(
                {
                    "id": f"natural-component:{index}",
                    "resource_ids": member_ids,
                    "form_labels": sorted({row["form_label"] for row in members}),
                    "language_labels": sorted(
                        {row["language_label"] for row in members if row["language_label"]}
                    ),
                    "occurrence_ids": sorted(row["occurrence_id"] for row in members),
                    "canonical_form": None,
                    "canonical_language": None,
                    "generated_by": "currently admitted resource translations",
                }
            )
        return components

    @staticmethod
    def canonical_limit_signature(
        resources: list[dict[str, Any]], translations: list[dict[str, Any]]
    ) -> str:
        admitted_pairs = sorted(
            [
                sorted(
                    [
                        translation["source_resource_id"],
                        translation["target_resource_id"],
                    ]
                )
                for translation in translations
                if translation["current_verdict"] == str(Verdict.TRUE)
            ]
        )
        return _stable_hash(
            {
                "resource_occurrences": sorted(
                    resource["occurrence_id"] for resource in resources
                ),
                "admitted_translation_pairs": admitted_pairs,
            }
        )

    def integrate_live_stage(self, trigger: str = "manual") -> tuple[dict[str, Any], bool]:
        resources = self.store.list_resources(limit=100_000)
        engagements = self.store.list_engagements(limit=100_000)
        translations = self.store.list_translations(limit=100_000)
        returns = self.store.list_returns(limit=100_000)
        delivery_order = self.store.chronological_delivery_order()
        admitted = sorted(
            row["id"]
            for row in translations
            if row["current_verdict"] == str(Verdict.TRUE)
        )
        opened = sorted(
            row["id"]
            for row in translations
            if row["current_verdict"] == str(Verdict.OPEN)
        )
        rejected = sorted(
            row["id"]
            for row in translations
            if row["current_verdict"] == str(Verdict.FALSE)
        )
        components = self._components(resources, translations)
        limit_signature = self.canonical_limit_signature(resources, translations)
        stage_signature = _stable_hash(
            {
                "delivery_order": delivery_order,
                "translation_verdicts": sorted(
                    (row["id"], row["current_verdict"]) for row in translations
                ),
                "return_statuses": sorted(
                    (row["id"], row["reintegration_status"]) for row in returns
                ),
            }
        )
        latest = self.store.latest_stage()
        if latest and latest["stage_signature"] == stage_signature:
            return latest, False

        source_reverse_index: dict[str, list[str]] = {}
        for resource in resources:
            source_reverse_index[f"resource:{resource['id']}"] = [
                resource["occurrence_id"]
            ]
        for engagement in engagements:
            source_reverse_index[f"engagement:{engagement['id']}"] = [
                engagement["occurrence_id"],
                self.store.get_resource(engagement["resource_id"])["occurrence_id"],
            ]
        for translation in translations:
            source_reverse_index[f"resource-translation:{translation['id']}"] = [
                translation["occurrence_id"],
                self.store.get_resource(translation["source_resource_id"])[
                    "occurrence_id"
                ],
                self.store.get_resource(translation["target_resource_id"])[
                    "occurrence_id"
                ],
            ]
        for component in components:
            source_reverse_index[component["id"]] = component["occurrence_ids"]

        stage = self.store.create_stage(
            {
                "stage_index": 0 if latest is None else int(latest["stage_index"]) + 1,
                "previous_stage_id": None if latest is None else latest["id"],
                "trigger": trigger,
                "delivery_order": delivery_order,
                "resource_ids": sorted(row["id"] for row in resources),
                "engagement_ids": sorted(row["id"] for row in engagements),
                "translation_ids": sorted(row["id"] for row in translations),
                "admitted_translation_ids": admitted,
                "open_translation_ids": opened,
                "rejected_translation_ids": rejected,
                "natural_components": components,
                "stage_signature": stage_signature,
                "limit_signature": limit_signature,
                "complete_coverage": (
                    len(resources) == len(source_reverse_index.keys() & {f"resource:{r['id']}" for r in resources})
                ),
                "canonical_language": None,
                "source_reverse_index": source_reverse_index,
            }
        )
        self.event_store.append_event(
            "RESOURCE_LIVE_STAGE_INTEGRATED",
            "resource_live_stage",
            stage["id"],
            {
                "stage_index": stage["stage_index"],
                "limit_signature": limit_signature,
                "delivery_order_preserved": True,
                "canonical_language": None,
                "natural_components": len(components),
                "nonterminal": True,
            },
        )
        return stage, True

    def projection(self) -> dict[str, Any]:
        resources = self.store.list_resources(limit=100_000)
        engagements = self.store.list_engagements(limit=100_000)
        translations = self.store.list_translations(limit=100_000)
        returns = self.store.list_returns(limit=100_000)
        reintegrations = self.store.list_reintegrations(limit=100_000)
        receipts = self.store.list_protocol_receipts(limit=100_000)
        stages = self.store.list_stages(limit=10_000)
        current = stages[-1] if stages else None
        batch_signature = self.canonical_limit_signature(resources, translations)
        source_reverse_index: dict[str, list[str]] = {}
        for resource in resources:
            source_reverse_index[f"resource:{resource['id']}"] = [
                resource["occurrence_id"]
            ]
        if current:
            source_reverse_index.update(current["source_reverse_index"])
        stats = {
            **self.store.stats(),
            "natural_components": 0 if current is None else len(current["natural_components"]),
            "admitted_translations": 0 if current is None else len(current["admitted_translation_ids"]),
            "open_translations": 0 if current is None else len(current["open_translation_ids"]),
            "rejected_translations": 0 if current is None else len(current["rejected_translation_ids"]),
            "batch_limit_signature": batch_signature,
            "live_limit_matches_current_batch": (
                current is None or current["limit_signature"] == batch_signature
            ),
            "finite_resource_registry": False,
            "canonical_language_selected": False,
            "protocol_is_translational_truth": False,
            "protocol_verdict_is_truth": False,
            "natural_unification": True,
            "engagement_driven": True,
            "self_reintegrating": True,
            "complete_network_coverage": (
                True if current is None else current["complete_coverage"]
            ),
            "nonterminal": True,
            "turing_complete_assumed": False,
        }
        return {
            "generated_at": utcnow(),
            "resources": resources,
            "engagements": engagements,
            "translations": translations,
            "returns": returns,
            "reintegrations": reintegrations,
            "protocol_receipts": receipts,
            "stages": stages,
            "current_stage": current,
            "stats": stats,
            "source_reverse_index": source_reverse_index,
        }
