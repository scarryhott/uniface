from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .living_store import LivingNetworkStore
from .models import EvidenceStatus, RelationType, Verdict
from .reopening_store import ReopeningStore
from .store import EventStore
from .translation_models import (
    RelativeFormRef,
    TranslationCompositionCreate,
    TranslationEventCreate,
    TranslationKind,
    TranslationRole,
    TranslationState,
    TranslationStateCreate,
)
from .translation_store import TranslationStore


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _form(
    form_type: str,
    form_id: str,
    role: TranslationRole,
    *,
    occurrence_id: str | None = None,
    label: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> RelativeFormRef:
    return RelativeFormRef(
        form_type=form_type,
        form_id=form_id,
        occurrence_id=occurrence_id,
        role=role,
        label=label,
        metadata=metadata or {},
    )


class TranslationFieldManager:
    """Canonical live translation field.

    HTTP, webhooks, SQLite rows, public problems, interactions, reopening
    families and projections are transports or relative forms. This manager
    records the source-reversible translations that make those forms mutually
    meaningful, carries their interpretation/admission/return history, and
    keeps every return reopenable.
    """

    agent_name = "translation-field-agent"

    def __init__(
        self,
        event_store: EventStore,
        translation_store: TranslationStore,
        living_store: LivingNetworkStore,
        reopening_store: ReopeningStore,
    ):
        self.event_store = event_store
        self.store = translation_store
        self.living_store = living_store
        self.reopening_store = reopening_store

    def capabilities(self) -> dict[str, Any]:
        return {
            "closure_reading": "translational truth through interaction",
            "canonical_live_primitive": "TranslationEvent",
            "protocol_is_transport_only": True,
            "source_immutable": True,
            "translation_state_append_only": True,
            "return_is_nonterminal": True,
            "automatic_global_truth": False,
            "turing_complete_assumed": False,
            "derived_forms": [
                "candidate relation",
                "interpretation",
                "admission",
                "problem",
                "note",
                "interaction / solution",
                "collective action",
                "returned consequence",
                "ordered reading",
                "reopening family",
                "residue round",
                "moral connection",
                "Black Mirror projection",
            ],
        }

    def create(self, data: TranslationEventCreate) -> dict[str, Any]:
        self._validate(data)
        data.transport = {
            "protocol_is_transport_only": True,
            **data.transport,
        }
        translation, created = self.store.create_translation(data)
        if created:
            self.event_store.append_event(
                "TRANSLATION_EVENT_CREATED",
                "translation_event",
                translation["id"],
                {
                    "kind": translation["kind"],
                    "relation_type": translation["relation_type"],
                    "exact_source_ids": translation["exact_source_ids"],
                    "external_key": translation["external_key"],
                    "protocol_is_transport_only": True,
                },
            )
        return translation

    def transition(
        self, translation_id: str, data: TranslationStateCreate
    ) -> dict[str, Any]:
        state, created = self.store.append_state(translation_id, data)
        if created:
            self.event_store.append_event(
                "TRANSLATION_STATE_APPENDED",
                "translation_event",
                translation_id,
                {
                    "state_id": state["id"],
                    "state": state["state"],
                    "verdict": state["verdict"],
                    "reason": state["reason"],
                    "nonterminal": True,
                },
            )
        return self.store.get_translation(translation_id)

    def compose(self, data: TranslationCompositionCreate) -> dict[str, Any]:
        predecessors = [
            self.store.get_translation(item)
            for item in data.predecessor_translation_ids
        ]
        exact_sources = list(
            dict.fromkeys(
                source
                for translation in predecessors
                for source in translation["exact_source_ids"]
            )
        )
        participant_ids = list(
            dict.fromkeys(
                participant
                for translation in predecessors
                for participant in translation["participant_ids"]
            )
        )
        perspectives = list(
            dict.fromkeys(
                perspective
                for translation in predecessors
                for perspective in translation["participating_perspective_ids"]
            )
        )
        traces = list(
            dict.fromkeys(
                trace
                for translation in predecessors
                for trace in translation["interaction_trace_ids"]
            )
        )
        preserves = list(
            dict.fromkeys(
                item for translation in predecessors for item in translation["preserves"]
            )
        )
        transforms = list(
            dict.fromkeys(
                item for translation in predecessors for item in translation["transforms"]
            )
        )
        untranslated = list(
            dict.fromkeys(
                item
                for translation in predecessors
                for item in translation["untranslated"]
            )
        )
        created = self.create(
            TranslationEventCreate(
                kind=TranslationKind.COMPOSED,
                exact_source_ids=exact_sources,
                source_forms=predecessors[0]["source_forms"],
                target_forms=predecessors[-1]["target_forms"],
                participant_ids=participant_ids,
                participating_perspective_ids=perspectives,
                interaction_trace_ids=traces,
                relation_type=data.relation_type,
                preserves=preserves,
                transforms=transforms,
                untranslated=untranslated,
                affected_perspectives=list(
                    dict.fromkeys(
                        item
                        for translation in predecessors
                        for item in translation["affected_perspectives"]
                    )
                ),
                frame_and_scope=data.frame_and_scope,
                admission_scope="composition remains relative to predecessor admissions",
                predecessor_translation_ids=data.predecessor_translation_ids,
                successor_potential=predecessors[-1]["successor_potential"],
                evidence_status=EvidenceStatus.INTERPRETED_RELATION,
                generated_by=data.generated_by,
                transport={"composition": True},
                metadata={
                    **data.metadata,
                    "composition_preserves_history": True,
                },
            )
        )
        return self.transition(
            created["id"],
            TranslationStateCreate(
                state=TranslationState.INTERPRETED,
                verdict=Verdict.OPEN,
                reason="Composed translation is explicit but inherits unresolved predecessor scope",
                actor_id=data.generated_by,
                metadata={"predecessors": data.predecessor_translation_ids},
            ),
        )

    def reconcile(self) -> dict[str, int]:
        counts = {
            "candidate_relations": self._reconcile_candidate_relations(),
            "living_interactions": self._reconcile_living_interactions(),
            "collective_actions": self._reconcile_collective_actions(),
            "action_returns": self._reconcile_action_returns(),
            "order_effects": self._reconcile_order_effects(),
            "residue_rounds": self._reconcile_residue_rounds(),
        }
        counts["total_created"] = sum(counts.values())
        self.store.set_state("last_reconciliation", {"at": utcnow(), **counts})
        return counts

    def projection(self) -> dict[str, Any]:
        translations = self.store.list_translations(limit=100_000)
        edges: list[dict[str, Any]] = []
        derived_views: dict[str, list[str]] = {}
        source_reverse_index: dict[str, list[str]] = {}
        open_ids: list[str] = []
        returned_ids: list[str] = []
        reopened_ids: list[str] = []

        for translation in translations:
            translation_id = translation["id"]
            source_reverse_index[translation_id] = translation["exact_source_ids"]
            if translation["current_verdict"] == Verdict.OPEN:
                open_ids.append(translation_id)
            if translation["current_state"] == TranslationState.RETURNED:
                returned_ids.append(translation_id)
            if translation["current_state"] == TranslationState.REOPENED:
                reopened_ids.append(translation_id)

            for predecessor in translation["predecessor_translation_ids"]:
                edges.append(
                    {
                        "source": predecessor,
                        "target": translation_id,
                        "relation": "COMPOSES_INTO",
                    }
                )
            for form in translation["source_forms"] + translation["target_forms"]:
                key = f"{form['form_type']}:{form['form_id']}"
                derived_views.setdefault(key, []).append(translation_id)
                if form.get("occurrence_id"):
                    source_reverse_index.setdefault(key, []).append(form["occurrence_id"])
            for source in translation["source_forms"]:
                for target in translation["target_forms"]:
                    edges.append(
                        {
                            "source": f"{source['form_type']}:{source['form_id']}",
                            "target": f"{target['form_type']}:{target['form_id']}",
                            "translation_id": translation_id,
                            "relation": translation["relation_type"],
                            "state": translation["current_state"],
                            "verdict": translation["current_verdict"],
                        }
                    )

        stats = self.store.stats()
        stats.update(
            {
                "open_translations": len(open_ids),
                "returned_translations": len(returned_ids),
                "reopened_translations": len(reopened_ids),
                "protocol_is_transport_only": True,
                "terminal_closure_available": False,
            }
        )
        projection = {
            "generated_at": utcnow(),
            "translations": translations,
            "edges": edges,
            "open_translations": open_ids,
            "returned_translations": returned_ids,
            "reopened_translations": reopened_ids,
            "derived_views": derived_views,
            "stats": stats,
            "source_reverse_index": {
                key: list(dict.fromkeys(value))
                for key, value in source_reverse_index.items()
            },
            "protocol_is_transport_only": True,
            "closure_reading": "translational truth through interaction",
        }
        self.store.set_state("translation_field_projection", projection)
        return projection

    def _validate(self, data: TranslationEventCreate) -> None:
        for occurrence_id in data.exact_source_ids:
            self.event_store.get_occurrence(occurrence_id)
        for form in data.source_forms + data.target_forms + data.successor_potential:
            if form.occurrence_id is not None:
                self.event_store.get_occurrence(form.occurrence_id)
        for predecessor in data.predecessor_translation_ids:
            self.store.get_translation(predecessor)

    @staticmethod
    def _kind_for_relation(relation_type: str) -> TranslationKind:
        if relation_type == RelationType.FRAME_TRANSLATION:
            return TranslationKind.FRAME_TRANSLATION
        if relation_type == RelationType.FORMALIZES:
            return TranslationKind.FORMALIZATION
        if relation_type == RelationType.MORAL_CONSEQUENCE:
            return TranslationKind.ACTION_CONSEQUENCE
        return TranslationKind.SOURCE_RELATION

    def _reconcile_candidate_relations(self) -> int:
        created = 0
        interpretations = self.event_store.list_interpretations(limit=100_000)
        by_candidate: dict[str, list[dict[str, Any]]] = {}
        for item in interpretations:
            by_candidate.setdefault(item["candidate_relation_id"], []).append(item)
        admissions = self.event_store.list_admissions(limit=100_000)
        by_interpretation: dict[str, list[dict[str, Any]]] = {}
        for item in admissions:
            by_interpretation.setdefault(item["interpretation_id"], []).append(item)

        for candidate in self.event_store.list_candidate_relations(limit=100_000):
            external_key = f"candidate_relation:{candidate['id']}"
            existing = self.store.get_by_external_key(external_key)
            if existing is None:
                source = self.event_store.get_occurrence(candidate["source_occurrence"])
                target = self.event_store.get_occurrence(candidate["target_occurrence"])
                existing = self.create(
                    TranslationEventCreate(
                        kind=self._kind_for_relation(candidate["relation_type"]),
                        exact_source_ids=[source["id"], target["id"]],
                        source_forms=[
                            _form(
                                "occurrence",
                                source["id"],
                                TranslationRole.SOURCE,
                                occurrence_id=source["id"],
                                label=source.get("source_context"),
                            )
                        ],
                        target_forms=[
                            _form(
                                "occurrence",
                                target["id"],
                                TranslationRole.TARGET,
                                occurrence_id=target["id"],
                                label=target.get("source_context"),
                            )
                        ],
                        relation_type=candidate["relation_type"],
                        preserves=["both exact source occurrences", "candidate provenance"],
                        transforms=["two isolated presentations become an explicit relation candidate"],
                        untranslated=["whether the relation is admissible remains unresolved"],
                        frame_and_scope="candidate relation proposed inside the canonical source field",
                        admission_scope="no admission inherited from semantic proximity",
                        evidence_status=EvidenceStatus.MODEL_SUGGESTED_RELATION,
                        generated_by=candidate["proposed_by"],
                        external_key=external_key,
                        transport={"legacy_view": "candidate_relation"},
                        metadata={"candidate_relation_id": candidate["id"]},
                    )
                )
                created += 1

            for interpretation in sorted(
                by_candidate.get(candidate["id"], []), key=lambda item: item["created_at"]
            ):
                self.transition(
                    existing["id"],
                    TranslationStateCreate(
                        state=TranslationState.INTERPRETED,
                        verdict=Verdict.OPEN,
                        reason="A source-reversible interpretation witness configured the relation",
                        actor_id=interpretation["generated_by"],
                        interpretation_id=interpretation["id"],
                        metadata={
                            "preserved_structure": interpretation["preserved_structure"],
                            "transformed_structure": interpretation["transformed_structure"],
                            "omitted_or_hidden_structure": interpretation[
                                "omitted_or_hidden_structure"
                            ],
                            "frame_and_scope": interpretation["frame_and_scope"],
                            "reopening": interpretation["reopening"],
                        },
                    ),
                )
                for admission in sorted(
                    by_interpretation.get(interpretation["id"], []),
                    key=lambda item: item["created_at"],
                ):
                    verdict = Verdict(admission["verdict"])
                    state = (
                        TranslationState.REJECTED
                        if verdict == Verdict.FALSE
                        else TranslationState.ADMITTED
                    )
                    self.transition(
                        existing["id"],
                        TranslationStateCreate(
                            state=state,
                            verdict=verdict,
                            reason=admission["reason"],
                            actor_id=admission["decided_by"],
                            interpretation_id=interpretation["id"],
                            admission_id=admission["id"],
                            metadata={
                                "checks": admission["checks"],
                                "rule_version": admission["rule_version"],
                                "relative_admission_not_terminal": True,
                            },
                        ),
                    )
        return created

    def _reconcile_living_interactions(self) -> int:
        created = 0
        for interaction in self.living_store.list_interactions(limit=100_000):
            external_key = f"living_interaction:{interaction['id']}"
            if self.store.get_by_external_key(external_key) is not None:
                continue
            problem = self.living_store.get_problem(interaction["from_problem_id"])
            target_problem = self.living_store.get_problem(interaction["to_problem_id"])
            kind = (
                TranslationKind.NOTE_LOOP_STEP
                if interaction["kind"] == "NOTE"
                else TranslationKind.PROBLEM_INTERACTION
            )
            translation = self.create(
                TranslationEventCreate(
                    kind=kind,
                    exact_source_ids=[interaction["occurrence_id"], problem["occurrence_id"]],
                    source_forms=[
                        _form(
                            "problem",
                            problem["id"],
                            TranslationRole.SOURCE,
                            occurrence_id=problem["occurrence_id"],
                            label=problem["title"],
                        ),
                        _form(
                            "interaction",
                            interaction["id"],
                            TranslationRole.SOURCE,
                            occurrence_id=interaction["occurrence_id"],
                            label=interaction["kind"],
                        ),
                    ],
                    target_forms=[
                        _form(
                            "problem",
                            target_problem["id"],
                            TranslationRole.TARGET,
                            occurrence_id=target_problem["occurrence_id"],
                            label=target_problem["title"],
                        ),
                        _form(
                            "solution_receipt",
                            interaction["solution_receipt_id"],
                            TranslationRole.RETURN,
                        ),
                    ],
                    participant_ids=[interaction["author_id"]],
                    participating_perspective_ids=[
                        item
                        for item in (
                            interaction["source_perspective_id"],
                            interaction["target_perspective_id"],
                        )
                        if item
                    ],
                    interaction_trace_ids=[interaction["id"]],
                    relation_type=f"LIVING_{interaction['kind']}",
                    preserves=interaction["preserves"]
                    or ["problem reality", "exact interaction occurrence"],
                    transforms=interaction["transforms"]
                    or ["the problem solution space gains one interaction"],
                    untranslated=interaction["omits"],
                    affected_perspectives=interaction["affected_perspectives"],
                    frame_and_scope="living problem interaction; solution is its returned form",
                    admission_scope="solution receipt remains OPEN unless later admitted",
                    successor_potential=[
                        _form(
                            "problem",
                            target_problem["id"],
                            TranslationRole.SUCCESSOR_POTENTIAL,
                            occurrence_id=target_problem["occurrence_id"],
                        )
                    ],
                    evidence_status=EvidenceStatus.ORIGINAL_NOTE,
                    generated_by=interaction["author_id"],
                    external_key=external_key,
                    transport={"legacy_view": "living_interaction"},
                    metadata={"solution_is_interaction": True},
                )
            )
            self.transition(
                translation["id"],
                TranslationStateCreate(
                    state=TranslationState.INTERPRETED,
                    verdict=Verdict.OPEN,
                    reason="The interaction constitutes a solution relation without exhausting discretion",
                    actor_id=interaction["author_id"],
                    returned_form=_form(
                        "solution_receipt",
                        interaction["solution_receipt_id"],
                        TranslationRole.RETURN,
                    ),
                ),
            )
            created += 1
        return created

    def _reconcile_collective_actions(self) -> int:
        created = 0
        for action in self.living_store.list_actions(limit=100_000):
            external_key = f"collective_action:{action['id']}"
            if self.store.get_by_external_key(external_key) is not None:
                continue
            problem = self.living_store.get_problem(action["problem_id"])
            self.create(
                TranslationEventCreate(
                    kind=TranslationKind.COLLECTIVE_ACTION,
                    exact_source_ids=[action["occurrence_id"], problem["occurrence_id"]],
                    source_forms=[
                        _form(
                            "problem",
                            problem["id"],
                            TranslationRole.SOURCE,
                            occurrence_id=problem["occurrence_id"],
                            label=problem["title"],
                        )
                    ],
                    target_forms=[
                        _form(
                            "collective_action",
                            action["id"],
                            TranslationRole.TARGET,
                            occurrence_id=action["occurrence_id"],
                            label=action["title"],
                        )
                    ],
                    participant_ids=action["participant_ids"],
                    interaction_trace_ids=[],
                    relation_type="COLLECTIVE_ACTION_FROM_PROBLEM",
                    preserves=["problem source", "action intent", "participant authorship"],
                    transforms=["shared interpretation becomes coordinated action"],
                    untranslated=action["open_assumptions"],
                    affected_perspectives=action["affected_perspectives"],
                    frame_and_scope="collective action as a relative form of problem interaction",
                    admission_scope="action does not self-certify truth or moral worth",
                    successor_potential=[
                        _form(
                            "collective_action",
                            action["id"],
                            TranslationRole.SUCCESSOR_POTENTIAL,
                            occurrence_id=action["occurrence_id"],
                        )
                    ],
                    evidence_status=EvidenceStatus.SOCIOECONOMIC_PROPOSAL,
                    generated_by=action["created_by"],
                    external_key=external_key,
                    transport={"legacy_view": "collective_action"},
                )
            )
            created += 1
        return created

    def _reconcile_action_returns(self) -> int:
        created = 0
        for returned in self.living_store.list_action_returns(limit=100_000):
            external_key = f"action_return:{returned['id']}"
            if self.store.get_by_external_key(external_key) is not None:
                continue
            action = self.living_store.get_action(returned["action_id"])
            problem = self.living_store.get_problem(action["problem_id"])
            predecessor = self.store.get_by_external_key(f"collective_action:{action['id']}")
            translation = self.create(
                TranslationEventCreate(
                    kind=TranslationKind.ACTION_CONSEQUENCE,
                    exact_source_ids=[
                        returned["occurrence_id"],
                        action["occurrence_id"],
                        problem["occurrence_id"],
                    ],
                    source_forms=[
                        _form(
                            "collective_action",
                            action["id"],
                            TranslationRole.SOURCE,
                            occurrence_id=action["occurrence_id"],
                            label=action["title"],
                        ),
                        _form(
                            "action_return",
                            returned["id"],
                            TranslationRole.RETURN,
                            occurrence_id=returned["occurrence_id"],
                        ),
                    ],
                    target_forms=[
                        _form(
                            "problem",
                            problem["id"],
                            TranslationRole.TARGET,
                            occurrence_id=problem["occurrence_id"],
                            label=problem["title"],
                        )
                    ],
                    participant_ids=[returned["authored_by"]],
                    affected_perspectives=returned["affected_perspectives"],
                    relation_type="RETURNED_CONSEQUENCE_REINTEGRATES_PROBLEM",
                    preserves=["action intent", "exact consequence", "problem source"],
                    transforms=["the problem field now includes what collective action caused"],
                    untranslated=["whether the consequence settles or further reopens discretion"],
                    frame_and_scope="returned consequence translated back into its originating problem",
                    admission_scope="return remains OPEN until participant-relative interpretation",
                    predecessor_translation_ids=([] if predecessor is None else [predecessor["id"]]),
                    successor_potential=[
                        _form(
                            "problem",
                            problem["id"],
                            TranslationRole.SUCCESSOR_POTENTIAL,
                            occurrence_id=problem["occurrence_id"],
                        )
                    ],
                    evidence_status=EvidenceStatus.MORAL_CONSEQUENCE,
                    generated_by=returned["authored_by"],
                    external_key=external_key,
                    transport={"legacy_view": "action_return"},
                    metadata={"return_is_nonterminal": True},
                )
            )
            self.transition(
                translation["id"],
                TranslationStateCreate(
                    state=TranslationState.RETURNED,
                    verdict=Verdict.OPEN,
                    reason="The consequence returned to the problem without terminally resolving it",
                    actor_id=returned["authored_by"],
                    returned_form=_form(
                        "action_return",
                        returned["id"],
                        TranslationRole.RETURN,
                        occurrence_id=returned["occurrence_id"],
                    ),
                ),
            )
            self.transition(
                translation["id"],
                TranslationStateCreate(
                    state=TranslationState.REOPENED,
                    verdict=Verdict.OPEN,
                    reason="Returned consequence becomes successor problem potential",
                    actor_id=self.agent_name,
                    metadata={"successor_problem_id": problem["id"]},
                ),
            )
            created += 1
        return created

    def _reconcile_order_effects(self) -> int:
        created = 0
        for assessment in self.reopening_store.list_order_assessments(limit=100_000):
            external_key = f"order_assessment:{assessment['id']}"
            if self.store.get_by_external_key(external_key) is not None:
                continue
            left = self.reopening_store.get_ordered_reading(
                assessment["left_reading_id"]
            )
            right = self.reopening_store.get_ordered_reading(
                assessment["right_reading_id"]
            )
            meaning_change = assessment["effect"] == "MEANING_CHANGING"
            translation = self.create(
                TranslationEventCreate(
                    kind=(
                        TranslationKind.ORDER_EFFECT
                        if meaning_change
                        else TranslationKind.FRAME_TRANSLATION
                    ),
                    exact_source_ids=[left["occurrence_id"], right["occurrence_id"]],
                    source_forms=[
                        _form(
                            "ordered_reading",
                            left["id"],
                            TranslationRole.SOURCE,
                            occurrence_id=left["occurrence_id"],
                        )
                    ],
                    target_forms=[
                        _form(
                            "ordered_reading",
                            right["id"],
                            TranslationRole.TARGET,
                            occurrence_id=right["occurrence_id"],
                        )
                    ],
                    participant_ids=[left["participant_id"], right["participant_id"]],
                    relation_type=assessment["effect"],
                    preserves=["the same assumption membership"]
                    if assessment["same_content"]
                    else ["source-reversible reading occurrences"],
                    transforms=["dependency order"],
                    untranslated=(
                        ["meaning differs under the reordered dependency path"]
                        if meaning_change
                        else []
                    ),
                    frame_and_scope="dependency-sensitive comparison of held assumptions",
                    admission_scope="order effect is a runtime classification, not global identity",
                    evidence_status=EvidenceStatus.INTERPRETED_RELATION,
                    generated_by=self.agent_name,
                    external_key=external_key,
                    transport={"legacy_view": "order_assessment"},
                    metadata={"assessment_id": assessment["id"]},
                )
            )
            self.transition(
                translation["id"],
                TranslationStateCreate(
                    state=TranslationState.INTERPRETED,
                    verdict=Verdict.OPEN,
                    reason=assessment["rationale"],
                    actor_id=self.agent_name,
                    metadata={"effect": assessment["effect"]},
                ),
            )
            created += 1
        return created

    def _reconcile_residue_rounds(self) -> int:
        created = 0
        for round_data in self.reopening_store.list_rounds(limit=100_000):
            external_key = f"residue_round:{round_data['id']}"
            if self.store.get_by_external_key(external_key) is not None:
                continue
            input_ids = round_data["input_assumption_ids"]
            residue_ids = round_data["remaining_star_ids"]
            exact_ids = list(dict.fromkeys(input_ids + residue_ids))
            if not exact_ids:
                continue
            previous = (
                None
                if round_data["previous_round_id"] is None
                else self.store.get_by_external_key(
                    f"residue_round:{round_data['previous_round_id']}"
                )
            )
            translation = self.create(
                TranslationEventCreate(
                    kind=TranslationKind.RESIDUE_RETURN,
                    exact_source_ids=exact_ids,
                    source_forms=[
                        _form(
                            "occurrence",
                            occurrence_id,
                            TranslationRole.SOURCE,
                            occurrence_id=occurrence_id,
                            label="round assumption",
                        )
                        for occurrence_id in input_ids
                    ],
                    target_forms=[
                        _form(
                            "occurrence",
                            occurrence_id,
                            TranslationRole.RETURN,
                            occurrence_id=occurrence_id,
                            label="remainingStar residue",
                        )
                        for occurrence_id in residue_ids
                    ],
                    relation_type="ADMISSIBLE_FAMILY_TO_REMAINING_STAR",
                    preserves=["all exact assumptions", "every generated reopening", "closure rules"],
                    transforms=["family of closed readings becomes their shared residue"],
                    untranslated=["finite executable chart is not a universal final core"],
                    frame_and_scope="finite explicit implication closure under one reopening family",
                    admission_scope="software-tested return under supplied rules",
                    predecessor_translation_ids=([] if previous is None else [previous["id"]]),
                    successor_potential=[
                        _form(
                            "occurrence",
                            occurrence_id,
                            TranslationRole.SUCCESSOR_POTENTIAL,
                            occurrence_id=occurrence_id,
                        )
                        for occurrence_id in residue_ids
                    ],
                    evidence_status=EvidenceStatus.SIMULATED_UNDER_ASSUMPTIONS,
                    generated_by=self.agent_name,
                    external_key=external_key,
                    transport={"legacy_view": "residue_round"},
                    metadata={
                        "round_id": round_data["id"],
                        "process_id": round_data["process_id"],
                        "strictly_reopened": round_data["strictly_reopened"],
                        "closed": round_data["closed"],
                        "final_core_state_available": False,
                    },
                )
            )
            self.transition(
                translation["id"],
                TranslationStateCreate(
                    state=TranslationState.RETURNED,
                    verdict=Verdict.TRUE if round_data["closed"] else Verdict.OPEN,
                    reason=(
                        "The explicit residue is closed under the supplied finite chart and returns as next-round potential"
                        if round_data["closed"]
                        else "The executable residue did not verify closedness and remains OPEN"
                    ),
                    actor_id=self.agent_name,
                    metadata={"finite_scope_only": True},
                ),
            )
            if round_data["strictly_reopened"]:
                self.transition(
                    translation["id"],
                    TranslationStateCreate(
                        state=TranslationState.REOPENED,
                        verdict=Verdict.OPEN,
                        reason="The returned residue strictly reopens into a further assumption body",
                        actor_id=self.agent_name,
                    ),
                )
            created += 1
        return created
