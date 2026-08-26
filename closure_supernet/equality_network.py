from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any

from .equality_models import (
    CoherenceSide,
    EqualityChartCreate,
    EqualityContextCreate,
    EqualityContextReopenCreate,
    EqualityDecisionCreate,
    EqualityWitnessState,
    RelativeEqualityCreate,
    ReturnCoherenceCreate,
)
from .equality_store import RelativeEqualityStore
from .models import Verdict
from .store import EventStore
from .translation_models import RelativeFormRef
from .translation_store import TranslationStore


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _form_data(form: RelativeFormRef | dict[str, Any]) -> dict[str, Any]:
    return form if isinstance(form, dict) else form.model_dump(mode="json")


def _form_key(form: RelativeFormRef | dict[str, Any]) -> str:
    data = _form_data(form)
    return f"{data['form_type']}:{data['form_id']}"


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


class RelativeEqualityManager:
    """Witness-valued, context-indexed equality over TranslationEvents.

    A TranslationEvent is directed interaction. Relative equality is admitted
    only when a reverse translation exists, both directed translations are TRUE
    at their scopes, both return paths are explicitly judged coherent, and a
    participant admits the witness in one declared context. Reopening creates a
    successor context rather than rewriting an earlier judgment.
    """

    agent_name = "relative-equality-agent"

    def __init__(
        self,
        event_store: EventStore,
        translation_store: TranslationStore,
        equality_store: RelativeEqualityStore,
    ):
        self.event_store = event_store
        self.translation_store = translation_store
        self.store = equality_store

    def capabilities(self) -> dict[str, Any]:
        return {
            "closure_reading": "unity as coherent source-reversible relative equality",
            "directed_translation_precedes_equality": True,
            "witness_valued": True,
            "context_indexed": True,
            "reverse_required": True,
            "left_and_right_return_coherence_required": True,
            "explicit_participant_admission_required": True,
            "source_immutable": True,
            "successor_context_reopening": True,
            "multiple_natural_forms_one_component": True,
            "canonical_language_selected": False,
            "automatic_global_truth": False,
            "protocol_is_transport_only": True,
            "turing_complete_assumed": False,
            "closure_relations": [
                "source closure",
                "return closure",
                "composition closure",
                "frame closure",
                "choice closure",
                "reopening closure",
                "separation closure",
            ],
        }

    def create_context(self, data: EqualityContextCreate) -> dict[str, Any]:
        self._validate_sources(data.exact_source_ids)
        if data.predecessor_context_id:
            self.store.get_context(data.predecessor_context_id)
        if data.reopening_translation_id:
            translation = self.translation_store.get_translation(
                data.reopening_translation_id
            )
            self._require_source_closure(
                data.exact_source_ids, translation["exact_source_ids"]
            )
        context, created = self.store.create_context(data)
        if created:
            self.event_store.append_event(
                "EQUALITY_CONTEXT_CREATED",
                "equality_context",
                context["id"],
                {
                    "label": context["label"],
                    "predecessor_context_id": context["predecessor_context_id"],
                    "source_reversible": True,
                    "context_indexed": True,
                },
            )
        return context

    def create_witness(self, data: RelativeEqualityCreate) -> dict[str, Any]:
        self.store.get_context(data.context_id)
        self._validate_sources(data.exact_source_ids)
        forward = self.translation_store.get_translation(data.forward_translation_id)
        if not self._translation_matches(forward, data.left_form, data.right_form):
            raise ValueError(
                "Forward TranslationEvent does not carry the left form to the right form"
            )
        translations = [forward]
        if data.reverse_translation_id:
            reverse = self.translation_store.get_translation(data.reverse_translation_id)
            if not self._translation_matches(reverse, data.right_form, data.left_form):
                raise ValueError(
                    "Reverse TranslationEvent does not carry the right form back to the left form"
                )
            translations.append(reverse)
        required_sources = _unique(
            [source for item in translations for source in item["exact_source_ids"]]
        )
        self._require_source_closure(data.exact_source_ids, required_sources)
        witness, created = self.store.create_witness(data)
        if created:
            self.event_store.append_event(
                "RELATIVE_EQUALITY_WITNESS_CREATED",
                "relative_equality_witness",
                witness["id"],
                {
                    "context_id": witness["context_id"],
                    "left_form": _form_key(witness["left_form"]),
                    "right_form": _form_key(witness["right_form"]),
                    "reverse_present": witness["reverse_translation_id"] is not None,
                    "verdict": "OPEN",
                },
            )
        return self.evaluate_witness(witness["id"])

    def create_coherence(self, data: ReturnCoherenceCreate) -> dict[str, Any]:
        witness = self.store.get_witness(data.witness_id)
        if witness["reverse_translation_id"] is None:
            raise ValueError("Return coherence requires a reverse translation")
        self._validate_sources(data.exact_source_ids)
        path = [
            self.translation_store.get_translation(item)
            for item in data.path_translation_ids
        ]
        required_sources = _unique(
            [source for item in path for source in item["exact_source_ids"]]
        )
        self._require_source_closure(data.exact_source_ids, required_sources)

        if str(data.side) == str(CoherenceSide.LEFT):
            expected_start = witness["forward_translation_id"]
            expected_end = witness["reverse_translation_id"]
            expected_form = witness["left_form"]
        else:
            expected_start = witness["reverse_translation_id"]
            expected_end = witness["forward_translation_id"]
            expected_form = witness["right_form"]
        if data.path_translation_ids[0] != expected_start or data.path_translation_ids[-1] != expected_end:
            raise ValueError(
                "Return-coherence path must follow the witness forward/reverse order for its side"
            )
        if _form_key(data.return_form) != _form_key(expected_form):
            raise ValueError("Return-coherence form must be the selected side's original form")

        coherence, created = self.store.create_coherence(data)
        if created:
            self.event_store.append_event(
                "RETURN_COHERENCE_CREATED",
                "return_coherence",
                coherence["id"],
                {
                    "witness_id": coherence["witness_id"],
                    "side": coherence["side"],
                    "path_translation_ids": coherence["path_translation_ids"],
                    "verdict": "OPEN",
                },
            )
        return self.evaluate_coherence(coherence["id"])

    def decide_coherence(
        self, coherence_id: str, data: EqualityDecisionCreate
    ) -> dict[str, Any]:
        evaluated = self.evaluate_coherence(coherence_id)
        if data.verdict == Verdict.TRUE and not evaluated["path_admitted"]:
            raise ValueError(
                "A return-coherence path cannot be TRUE while one of its TranslationEvents is not currently TRUE"
            )
        decision = self.store.append_coherence_decision(coherence_id, data)
        self.event_store.append_event(
            "RETURN_COHERENCE_DECIDED",
            "return_coherence",
            coherence_id,
            {
                "decision_id": decision["id"],
                "verdict": decision["verdict"],
                "scope": decision["scope"],
            },
        )
        return self.evaluate_coherence(coherence_id)

    def decide_witness(
        self, witness_id: str, data: EqualityDecisionCreate
    ) -> dict[str, Any]:
        evaluated = self.evaluate_witness(witness_id)
        if data.verdict == Verdict.TRUE and not evaluated["eligible_for_true"]:
            raise ValueError(
                "TRUE relative equality requires admitted forward and reverse translations plus TRUE left and right return coherences"
            )
        decision = self.store.append_witness_decision(witness_id, data)
        self.event_store.append_event(
            "RELATIVE_EQUALITY_DECIDED",
            "relative_equality_witness",
            witness_id,
            {
                "decision_id": decision["id"],
                "verdict": decision["verdict"],
                "scope": decision["scope"],
                "context_relative": True,
            },
        )
        return self.evaluate_witness(witness_id)

    def create_chart(self, data: EqualityChartCreate) -> dict[str, Any]:
        self._validate_sources(data.exact_source_ids)
        if data.context_id:
            self.store.get_context(data.context_id)
        chart = self.store.create_chart(data)
        self.event_store.append_event(
            "RELATIVE_EQUALITY_CHART_CREATED",
            "equality_chart",
            chart["id"],
            {
                "name": chart["name"],
                "generator": chart["generator"],
                "inverse_reading": chart["inverse_reading"],
                "chart_is_not_foundation": True,
            },
        )
        return chart

    def reopen_context(
        self, context_id: str, data: EqualityContextReopenCreate
    ) -> dict[str, Any]:
        predecessor = self.store.get_context(context_id)
        translation = self.translation_store.get_translation(
            data.reopening_translation_id
        )
        self._validate_sources(data.exact_source_ids)
        required = _unique(
            predecessor["exact_source_ids"] + translation["exact_source_ids"]
        )
        self._require_source_closure(data.exact_source_ids, required)
        context = self.create_context(
            EqualityContextCreate(
                label=data.label,
                exact_source_ids=data.exact_source_ids,
                authored_by=data.authored_by,
                participant_ids=predecessor["participant_ids"],
                perspective_ids=predecessor["perspective_ids"],
                frame_and_scope=data.frame_and_scope,
                predecessor_context_id=context_id,
                reopening_translation_id=data.reopening_translation_id,
                metadata={
                    **data.metadata,
                    "prior_context_preserved": True,
                    "reopening_is_successor_context": True,
                },
            )
        )
        self.event_store.append_event(
            "EQUALITY_CONTEXT_REOPENED",
            "equality_context",
            context["id"],
            {
                "predecessor_context_id": context_id,
                "reopening_translation_id": data.reopening_translation_id,
                "prior_context_mutated": False,
            },
        )
        return context

    def evaluate_coherence(self, coherence_id: str) -> dict[str, Any]:
        coherence = self.store.get_coherence(coherence_id)
        decisions = self.store.list_coherence_decisions(coherence_id)
        translations = [
            self.translation_store.get_translation(item)
            for item in coherence["path_translation_ids"]
        ]
        path_admitted = all(
            item["current_verdict"] == str(Verdict.TRUE) for item in translations
        )
        latest = decisions[-1] if decisions else None
        if latest is None:
            verdict = Verdict.OPEN
            reason = "Return coherence remains OPEN until explicitly admitted"
        elif latest["verdict"] == str(Verdict.FALSE):
            verdict = Verdict.FALSE
            reason = latest["reason"]
        elif latest["verdict"] == str(Verdict.TRUE) and path_admitted:
            verdict = Verdict.TRUE
            reason = latest["reason"]
        elif latest["verdict"] == str(Verdict.TRUE):
            verdict = Verdict.OPEN
            reason = "Previously admitted coherence reopened because its translation path is no longer TRUE"
        else:
            verdict = Verdict.OPEN
            reason = latest["reason"]
        return {
            **coherence,
            "path_admitted": path_admitted,
            "current_verdict": str(verdict),
            "current_reason": reason,
            "decision_history": decisions,
        }

    def evaluate_witness(self, witness_id: str) -> dict[str, Any]:
        witness = self.store.get_witness(witness_id)
        decisions = self.store.list_witness_decisions(witness_id)
        forward = self.translation_store.get_translation(
            witness["forward_translation_id"]
        )
        forward_admitted = forward["current_verdict"] == str(Verdict.TRUE)
        reverse_admitted = False
        if witness["reverse_translation_id"]:
            reverse = self.translation_store.get_translation(
                witness["reverse_translation_id"]
            )
            reverse_admitted = reverse["current_verdict"] == str(Verdict.TRUE)
        reversible = forward_admitted and reverse_admitted

        coherences = [
            self.evaluate_coherence(item["id"])
            for item in self.store.list_coherences(witness_id)
        ]
        left = next(
            (item for item in coherences if item["side"] == str(CoherenceSide.LEFT)),
            None,
        )
        right = next(
            (item for item in coherences if item["side"] == str(CoherenceSide.RIGHT)),
            None,
        )
        coherent = (
            left is not None
            and right is not None
            and left["current_verdict"] == str(Verdict.TRUE)
            and right["current_verdict"] == str(Verdict.TRUE)
        )
        eligible = reversible and coherent
        latest = decisions[-1] if decisions else None

        if latest and latest["verdict"] == str(Verdict.FALSE):
            state = EqualityWitnessState.REJECTED
            verdict = Verdict.FALSE
            reason = latest["reason"]
        elif latest and latest["verdict"] == str(Verdict.TRUE) and eligible:
            state = EqualityWitnessState.ADMITTED
            verdict = Verdict.TRUE
            reason = latest["reason"]
        elif latest and latest["verdict"] == str(Verdict.TRUE):
            state = EqualityWitnessState.REOPENED
            verdict = Verdict.OPEN
            reason = (
                "The context-relative equality reopened because reversibility or return coherence is no longer admitted"
            )
        elif coherent:
            state = EqualityWitnessState.COHERENT
            verdict = Verdict.OPEN
            reason = "Reversible coherent witness awaits explicit context-relative admission"
        elif reversible:
            state = EqualityWitnessState.REVERSIBLE
            verdict = Verdict.OPEN
            reason = "Forward and reverse translations are admitted; return coherence remains OPEN"
        else:
            state = EqualityWitnessState.PROPOSED
            verdict = Verdict.OPEN
            reason = "Directed translation has not yet closed into a reversible equality witness"

        return {
            **witness,
            "current_state": str(state),
            "current_verdict": str(verdict),
            "current_reason": reason,
            "reversible": reversible,
            "coherent": coherent,
            "eligible_for_true": eligible,
            "left_coherence_id": None if left is None else left["id"],
            "right_coherence_id": None if right is None else right["id"],
            "decision_history": decisions,
        }

    def natural_components(self, context_id: str) -> list[dict[str, Any]]:
        self.store.get_context(context_id)
        witnesses = [
            self.evaluate_witness(item["id"])
            for item in self.store.list_witnesses(context_id)
        ]
        forms: dict[str, dict[str, Any]] = {}
        parent: dict[str, str] = {}

        def add(form: dict[str, Any]) -> str:
            key = _form_key(form)
            forms[key] = form
            parent.setdefault(key, key)
            return key

        def find(key: str) -> str:
            while parent[key] != key:
                parent[key] = parent[parent[key]]
                key = parent[key]
            return key

        def union(left: str, right: str) -> None:
            a, b = find(left), find(right)
            if a != b:
                parent[b] = a

        for witness in witnesses:
            left = add(witness["left_form"])
            right = add(witness["right_form"])
            if witness["current_verdict"] == str(Verdict.TRUE):
                union(left, right)

        groups: dict[str, list[str]] = {}
        for key in parent:
            groups.setdefault(find(key), []).append(key)

        components: list[dict[str, Any]] = []
        for members in groups.values():
            members = sorted(members)
            member_set = set(members)
            admitted_witnesses = [
                item
                for item in witnesses
                if item["current_verdict"] == str(Verdict.TRUE)
                and _form_key(item["left_form"]) in member_set
                and _form_key(item["right_form"]) in member_set
            ]
            sources = _unique(
                [source for item in admitted_witnesses for source in item["exact_source_ids"]]
            )
            member_forms = [forms[key] for key in members]
            form_labels = sorted(
                {
                    str(item.get("label") or item["form_type"])
                    for item in member_forms
                }
            )
            language_labels = sorted(
                {
                    str(item.get("metadata", {}).get("language_label"))
                    for item in member_forms
                    if item.get("metadata", {}).get("language_label") is not None
                }
            )
            digest = hashlib.sha256(
                (context_id + "|" + "|".join(members)).encode("utf-8")
            ).hexdigest()[:24]
            components.append(
                {
                    "id": f"relative-component:{digest}",
                    "context_id": context_id,
                    "member_forms": member_forms,
                    "witness_ids": [item["id"] for item in admitted_witnesses],
                    "exact_source_ids": sources,
                    "form_labels": form_labels,
                    "language_labels": language_labels,
                    "canonical_form": None,
                    "canonical_language": None,
                }
            )
        return components

    def reconcile_translation_pairs(
        self, translation_limit: int = 2000, pair_limit: int = 128
    ) -> int:
        translations = [
            item
            for item in self.translation_store.list_translations(
                limit=translation_limit
            )
            if item["current_verdict"] != str(Verdict.FALSE)
        ]
        created = 0
        for index, forward in enumerate(translations):
            if created >= pair_limit:
                break
            for reverse in translations[index + 1 :]:
                if created >= pair_limit:
                    break
                pair = self._reverse_pair(forward, reverse)
                if pair is None:
                    continue
                left_form, right_form = pair
                ordered_ids = sorted([forward["id"], reverse["id"]])
                key = ":".join(ordered_ids)
                exact_sources = _unique(
                    forward["exact_source_ids"] + reverse["exact_source_ids"]
                )
                context = self.create_context(
                    EqualityContextCreate(
                        label="Reversible TranslationEvent candidate context",
                        exact_source_ids=exact_sources,
                        authored_by=self.agent_name,
                        participant_ids=_unique(
                            forward["participant_ids"] + reverse["participant_ids"]
                        ),
                        perspective_ids=_unique(
                            forward["participating_perspective_ids"]
                            + reverse["participating_perspective_ids"]
                        ),
                        frame_and_scope=(
                            f"{forward['frame_and_scope']} ↔ {reverse['frame_and_scope']}"
                        ),
                        external_key=f"auto-equality-context:{key}",
                        metadata={
                            "automatic_candidate_only": True,
                            "no_automatic_truth": True,
                        },
                    )
                )
                existing = self.store.get_witness_by_external_key(
                    f"auto-relative-equality:{key}"
                )
                if existing is not None:
                    continue
                common_invariant = sorted(
                    set(forward["preserves"]) & set(reverse["preserves"])
                ) or ["source reversibility across the two directed translations"]
                self.create_witness(
                    RelativeEqualityCreate(
                        context_id=context["id"],
                        left_form=RelativeFormRef.model_validate(left_form),
                        right_form=RelativeFormRef.model_validate(right_form),
                        forward_translation_id=forward["id"],
                        reverse_translation_id=reverse["id"],
                        exact_source_ids=exact_sources,
                        invariant=common_invariant,
                        residue=_unique(
                            forward["untranslated"]
                            + reverse["untranslated"]
                            + ["left and right return coherence remain to be supplied"]
                        ),
                        authored_by=self.agent_name,
                        external_key=f"auto-relative-equality:{key}",
                        metadata={
                            "understanding_proposed_relation": True,
                            "participant_admission_required": True,
                        },
                    )
                )
                created += 1
        return created

    def projection(self, context_id: str | None = None) -> dict[str, Any]:
        contexts = self.store.list_contexts(limit=100_000)
        if context_id is not None:
            contexts = [item for item in contexts if item["id"] == context_id]
        context_ids = {item["id"] for item in contexts}
        witnesses = [
            self.evaluate_witness(item["id"])
            for item in self.store.list_witnesses(limit=100_000)
            if item["context_id"] in context_ids
        ]
        witness_ids = {item["id"] for item in witnesses}
        coherences = [
            self.evaluate_coherence(item["id"])
            for item in self.store.list_coherences(limit=100_000)
            if item["witness_id"] in witness_ids
        ]
        charts = [
            item
            for item in self.store.list_charts(limit=100_000)
            if item["context_id"] is None or item["context_id"] in context_ids
        ]
        components = [
            component
            for context in contexts
            for component in self.natural_components(context["id"])
        ]
        source_reverse_index: dict[str, list[str]] = {}
        for context in contexts:
            source_reverse_index[f"equality-context:{context['id']}"] = context[
                "exact_source_ids"
            ]
        for witness in witnesses:
            source_reverse_index[f"relative-equality:{witness['id']}"] = witness[
                "exact_source_ids"
            ]
        for coherence in coherences:
            source_reverse_index[f"return-coherence:{coherence['id']}"] = coherence[
                "exact_source_ids"
            ]
        for chart in charts:
            source_reverse_index[f"equality-chart:{chart['id']}"] = chart[
                "exact_source_ids"
            ]
        for component in components:
            source_reverse_index[component["id"]] = component["exact_source_ids"]

        stats = {
            **self.store.stats(),
            "admitted_equalities": sum(
                1 for item in witnesses if item["current_verdict"] == str(Verdict.TRUE)
            ),
            "open_equalities": sum(
                1 for item in witnesses if item["current_verdict"] == str(Verdict.OPEN)
            ),
            "rejected_equalities": sum(
                1 for item in witnesses if item["current_verdict"] == str(Verdict.FALSE)
            ),
            "reopened_equalities": sum(
                1
                for item in witnesses
                if item["current_state"] == str(EqualityWitnessState.REOPENED)
            ),
            "natural_components": len(components),
            "complete_current_coverage": all(
                source_reverse_index.get(f"relative-equality:{item['id']}")
                for item in witnesses
            ),
            "terminal_completion_claimed": False,
        }
        projection = {
            "generated_at": utcnow(),
            "contexts": contexts,
            "witnesses": witnesses,
            "coherences": coherences,
            "charts": charts,
            "natural_components": components,
            "stats": stats,
            "source_reverse_index": source_reverse_index,
            "closure_relations": self.capabilities()["closure_relations"],
            "context_indexed": True,
            "witness_valued": True,
            "directed_translation_precedes_equality": True,
            "automatic_global_truth": False,
            "canonical_language_selected": False,
            "protocol_is_transport_only": True,
        }
        self.store.set_state("relative_equality_projection", projection)
        return projection

    @staticmethod
    def _translation_matches(
        translation: dict[str, Any],
        source_form: RelativeFormRef | dict[str, Any],
        target_form: RelativeFormRef | dict[str, Any],
    ) -> bool:
        source_key = _form_key(source_form)
        target_key = _form_key(target_form)
        return source_key in {
            _form_key(item) for item in translation["source_forms"]
        } and target_key in {
            _form_key(item) for item in translation["target_forms"]
        }

    @staticmethod
    def _reverse_pair(
        forward: dict[str, Any], reverse: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any]] | None:
        for left in forward["source_forms"]:
            for right in forward["target_forms"]:
                if _form_key(left) == _form_key(right):
                    continue
                if _form_key(right) in {
                    _form_key(item) for item in reverse["source_forms"]
                } and _form_key(left) in {
                    _form_key(item) for item in reverse["target_forms"]
                }:
                    return left, right
        for left in reverse["source_forms"]:
            for right in reverse["target_forms"]:
                if _form_key(left) == _form_key(right):
                    continue
                if _form_key(right) in {
                    _form_key(item) for item in forward["source_forms"]
                } and _form_key(left) in {
                    _form_key(item) for item in forward["target_forms"]
                }:
                    return left, right
        return None

    def _validate_sources(self, source_ids: list[str]) -> None:
        for source_id in source_ids:
            self.event_store.get_occurrence(source_id)

    @staticmethod
    def _require_source_closure(
        supplied_source_ids: list[str], required_source_ids: list[str]
    ) -> None:
        missing = sorted(set(required_source_ids) - set(supplied_source_ids))
        if missing:
            raise ValueError(
                "Relative equality source closure is incomplete; missing exact sources: "
                + ", ".join(missing)
            )
