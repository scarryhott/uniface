from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, TYPE_CHECKING

from .axiometry import operator_keys
from .closure_ui_contract import (
    BUILDER_VERSION as CLOSURE_UI_BUILDER_VERSION,
    SCHEMA as CLOSURE_UI_SCHEMA,
    derive_closure_ui_contract,
    derive_open_ui_contract,
)
from .interaction_closure import derive_interaction_closure
from .models import RelationType, Verdict
from .natural_interface import NaturalInterfaceManager
from .natural_interface_models import NaturalChartKind
from .nrrf825 import closure_level_receipt
from .nrrf837_continuum import SCHEMA as NRRF837_SCHEMA
from .nrrf837_continuum import UNITY_SELECTOR_VERSION
from .selection_models import SelectionReadingCreate
from .supernet_models import ResourceEnvelope
from .truth_constrained_runtime import derive_unified_truth_runtime
from .topology_models import TopologyMode
from .visual_closure import (
    build_visual_closure_receipt,
    learned_relation_memory,
)

if TYPE_CHECKING:
    from .runtime import ClosureSupernetRuntime


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in values if str(item)))


def _full_digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()}"


class LiveSenseManager:
    """Interaction-time orchestration of the already existing closure agents.

    No new semantic classifier lives here.  The manager runs the project's
    existing UnderstandingAgent classifier, InterpretationProvider,
    AdmissionPolicy, TranslationField reconciliation, NRRF790 selection, and
    NRRF825 equality-level closure immediately after a public interaction.
    Background autonomy may remain disabled: Sense is caused by the
    interaction itself.
    """

    def __init__(self, runtime: "ClosureSupernetRuntime"):
        self.runtime = runtime

    def _field_events_snapshot(
        self, *, batch_size: int = 50_000
    ) -> tuple[list[dict[str, Any]], int]:
        """Read the complete ordered field and its authoritative revision."""

        if batch_size < 1:
            raise ValueError("batch_size must be positive")
        events: list[dict[str, Any]] = []
        offset = 0
        while True:
            batch = self.runtime.supernet_store.list_events(
                limit=batch_size,
                offset=offset,
            )
            events.extend(batch)
            if len(batch) < batch_size:
                break
            offset += len(batch)
        return (
            events,
            self.runtime.supernet_store.latest_event_sequence(),
        )

    def _field_occurrences_snapshot(
        self, *, batch_size: int = 50_000
    ) -> list[dict[str, Any]]:
        """Read every source occurrence used by the visual field."""

        if batch_size < 1:
            raise ValueError("batch_size must be positive")
        occurrences: list[dict[str, Any]] = []
        offset = 0
        while True:
            batch = self.runtime.store.list_occurrences(
                limit=batch_size,
                offset=offset,
            )
            occurrences.extend(batch)
            if len(batch) < batch_size:
                break
            offset += len(batch)
        return occurrences

    def capabilities(self) -> dict[str, Any]:
        return {
            "interaction_time_sense": True,
            "uses_existing_understanding_agent": True,
            "uses_existing_interpretation_provider": True,
            "uses_existing_admission_policy": True,
            "uses_existing_translation_field": True,
            "uses_existing_nrrf790_selector": True,
            "derives_nrrf825_equality_level": True,
            "derives_nrrf837_continuum": True,
            "unified_visual_translational_closure": True,
            "black_mirror_slearn_ai_tokenomic_one_receipt": True,
            "slearn_memory_changes_candidate_priority": True,
            "slearn_memory_basis": "closure-admitted translational-truth witnesses only",
            "open_candidates_change_slearn_truth_memory": False,
            "tokenomic_units_are_equality_classes": True,
            "visual_network_drives_next_operation": True,
            "level_derived_from_admitted_returns": True,
            "projective_zero_infinity_fold": "tan((π/2)·collapse)",
            "projective_fold_requires_explicit_visual_axiometry_witness": True,
            "projective_fold_is_user_selected": False,
            "background_autonomy_required": False,
            "exact_source_preserved_before_sense": True,
            "open_relations_remain_open": True,
            "forced_isolation_automatic": False,
            "canonical_presentation": None,
            "truth_issued_by_sense": False,
        }

    def _understand_occurrence(self, occurrence_id: str) -> list[str]:
        source = self.runtime.store.get_occurrence(occurrence_id)
        learned = learned_relation_memory(
            self.runtime.supernet_store.list_visual_closure_receipts()
        )
        proposals: list[tuple[float, str, dict[str, Any], str]] = []
        for target in self.runtime.store.list_occurrences(limit=100_000):
            if target["id"] == source["id"]:
                continue
            relation_type, score, rationale = self.runtime.understanding._classify(
                source, target
            )
            if relation_type is None:
                continue
            proposals.append((score, str(relation_type), target, rationale))
        # SLEARN is operational here: previously admitted relation witnesses
        # determine candidate priority before raw semantic score.  No verdict or
        # truth is upgraded by memory, and exact sources remain unchanged.
        proposals.sort(
            key=lambda item: (
                -learned.get(item[1], 0),
                -item[0],
                item[2]["id"],
            )
        )
        candidate_ids: list[str] = []
        for score, relation_type, target, rationale in proposals[
            : self.runtime.config.max_candidates_per_occurrence
        ]:
            row, _created = self.runtime.store.create_candidate_relation(
                source["id"],
                target["id"],
                relation_type,
                score,
                rationale,
                proposed_by=self.runtime.understanding.name,
            )
            candidate_ids.append(row["id"])
        return _unique(candidate_ids)

    async def _interpret_candidate(self, candidate: dict[str, Any]) -> dict[str, Any]:
        existing = [
            row
            for row in self.runtime.store.list_interpretations(limit=100_000)
            if row["candidate_relation_id"] == candidate["id"]
        ]
        if existing:
            return max(existing, key=lambda row: row["created_at"])

        source = self.runtime.store.get_occurrence(candidate["source_occurrence"])
        target = self.runtime.store.get_occurrence(candidate["target_occurrence"])
        source_keys = operator_keys(source["operator_path"])
        target_keys = operator_keys(target["operator_path"])
        common_keys = sorted(set(source_keys) & set(target_keys))
        source_only = sorted(set(source_keys) - set(target_keys))
        target_only = sorted(set(target_keys) - set(source_keys))
        payload: dict[str, Any] = {
            "candidate_relation_id": candidate["id"],
            "source_operator_path": source["operator_path"],
            "target_operator_path": target["operator_path"],
            "preserved_structure": common_keys,
            "transformed_structure": [
                *(f"source-only:{key}" for key in source_only),
                *(f"target-only:{key}" for key in target_only),
            ],
            "omitted_or_hidden_structure": [
                "The exact source occurrences are not reconstructed from a projected relation",
                "Semantic or operator-path resemblance does not by itself prove identical meaning",
            ],
            "frame_and_scope": f"{candidate['relation_type']} proposed within the source-preserving axiometric index",
            "reverse_path": [source["id"], target["id"]],
            "affected_perspectives": sorted(
                {
                    str(source.get("metadata", {}).get("authored_by") or source["source_id"]),
                    str(target.get("metadata", {}).get("authored_by") or target["source_id"]),
                }
            ),
            "formal_scope": "No machine-checked equivalence is inferred unless an explicit FORMALIZES witness is attached",
            "empirical_scope": "No physical, social, or moral fact is inferred from formal or semantic similarity",
            "reopening": "Retain both occurrences and reopen the relation for author confirmation, proof, contradiction, or alternate interpretation",
            "generated_by": self.runtime.interpretation.name,
            "status": "INTERPRETED_RELATION",
        }
        provider_payload = await self.runtime.interpretation.provider.interpret(
            source, target, candidate
        )
        if provider_payload:
            for key in (
                "preserved_structure",
                "transformed_structure",
                "omitted_or_hidden_structure",
                "frame_and_scope",
                "affected_perspectives",
                "formal_scope",
                "empirical_scope",
                "reopening",
            ):
                if key in provider_payload and provider_payload[key]:
                    payload[key] = provider_payload[key]
            payload["generated_by"] = (
                f"{self.runtime.interpretation.name}+{self.runtime.interpretation.provider.name}"
            )
        row, _created = self.runtime.store.create_interpretation(
            payload, self.runtime.interpretation.engine_version
        )
        return row

    def _admit_interpretation(
        self,
        candidate: dict[str, Any],
        interpretation: dict[str, Any],
    ) -> dict[str, Any]:
        version = self.runtime.store.active_rule_version()
        existing = [
            row
            for row in self.runtime.store.list_admissions(limit=100_000)
            if row["interpretation_id"] == interpretation["id"]
            and row["rule_version"] == version
        ]
        if existing:
            return max(existing, key=lambda row: row["created_at"])
        source = self.runtime.store.get_occurrence(candidate["source_occurrence"])
        target = self.runtime.store.get_occurrence(candidate["target_occurrence"])
        result = self.runtime.admission.policy.evaluate(
            candidate, interpretation, source, target
        )
        row, _created = self.runtime.store.create_admission(
            interpretation["id"],
            result.verdict,
            result.checks,
            result.reason,
            version,
            self.runtime.admission.name,
        )
        return row

    def _candidate_rows(self, source_ids: set[str]) -> list[dict[str, Any]]:
        rows = [
            row
            for row in self.runtime.store.list_candidate_relations(limit=100_000)
            if row["source_occurrence"] in source_ids
            or row["target_occurrence"] in source_ids
        ]
        rows.sort(key=lambda row: (-float(row["score"]), row["id"]))
        return rows

    async def sense_event(self, event_id: str) -> dict[str, Any]:
        event = self.runtime.supernet_store.get_event(event_id)
        source_ids = set(event["exact_source_ids"])
        proposed: list[str] = []
        for occurrence_id in source_ids:
            proposed.extend(self._understand_occurrence(occurrence_id))

        candidates = self._candidate_rows(source_ids)
        interpretations: dict[str, dict[str, Any]] = {}
        admissions: dict[str, dict[str, Any]] = {}
        for candidate in candidates:
            interpretation = await self._interpret_candidate(candidate)
            interpretations[candidate["id"]] = interpretation
            admissions[candidate["id"]] = self._admit_interpretation(
                candidate, interpretation
            )

        # OPEN seams and moral-residue checks are the same agents used by the
        # autonomous cycle.  Running them here makes reopening interaction-time.
        reopened = self.runtime.reopening.run()
        moral_open = self.runtime.moral_audit.run()

        translation_reconciliation = (
            self.runtime.translation.reconcile()
            if self.runtime.config.translation_field_enabled
            else {"total_created": 0}
        )
        supernet_reconciliation = self.runtime.supernet_integrator.reconcile()
        stage = self.runtime.supernet_integrator.commit_stage(
            trigger=f"live-sense:{event_id}", trigger_event_id=event_id
        )

        translations = []
        candidate_ids = {row["id"] for row in candidates}
        for translation in self.runtime.translation_store.list_translations(
            limit=100_000
        ):
            candidate_id = translation.get("metadata", {}).get(
                "candidate_relation_id"
            )
            if candidate_id in candidate_ids:
                translations.append(translation)

        relation_receipts: list[dict[str, Any]] = []
        admissible_symbols: list[str] = []
        for candidate in candidates:
            admission = admissions.get(candidate["id"])
            verdict = str(admission["verdict"]) if admission else Verdict.OPEN.value
            if verdict != Verdict.FALSE.value:
                admissible_symbols.append(candidate["id"])
            admission_checks = dict((admission or {}).get("checks") or {})
            compatibility_keys = (
                "SOURCE_REVERSIBLE",
                "STATUS_EXPLICIT",
                "AFFECTED_PERSPECTIVES_RETAINED",
                "FORMAL_SCOPE_EXPLICIT",
                "EMPIRICAL_SCOPE_EXPLICIT",
                "REOPENING_AVAILABLE",
                "NO_TURING_COMPLETENESS_ASSUMPTION",
            )
            compatible = verdict == Verdict.TRUE.value and all(
                admission_checks.get(key) is True for key in compatibility_keys
            )
            deterministic_equation = verdict == Verdict.TRUE.value and str(
                candidate["relation_type"]
            ) in {
                RelationType.SAME_LITERAL_EQUATION.value,
                RelationType.SAME_OPERATOR_PATH.value,
            }
            relation_receipts.append(
                {
                    "candidate_relation_id": candidate["id"],
                    "relation_type": candidate["relation_type"],
                    "score": candidate["score"],
                    "rationale": candidate["rationale"],
                    "source_occurrence": candidate["source_occurrence"],
                    "target_occurrence": candidate["target_occurrence"],
                    "interpretation_id": interpretations.get(candidate["id"], {}).get(
                        "id"
                    ),
                    "admission_id": admission.get("id") if admission else None,
                    "verdict": verdict,
                    "admission_reason": admission.get("reason") if admission else None,
                    "source_return_ids": [
                        candidate["source_occurrence"],
                        candidate["target_occurrence"],
                    ],
                    "visual_equation": {
                        "id": f"visual-equation:{candidate['id']}",
                        "source": candidate["source_occurrence"],
                        "target": candidate["target_occurrence"],
                        "equation": candidate["relation_type"],
                        "deterministic": deterministic_equation,
                        "source_return_ids": [
                            candidate["source_occurrence"],
                            candidate["target_occurrence"],
                        ],
                    },
                    "compatible": {
                        "witnessed": compatible,
                        "basis": "AdmissionPolicy source-reversibility and scope checks",
                        "provenance": [
                            admission.get("id") if admission else None,
                            *[
                                key
                                for key in compatibility_keys
                                if admission_checks.get(key) is True
                            ],
                        ],
                    },
                    "closure_explicit": {
                        "witnessed": deterministic_equation,
                        "basis": (
                            "deterministic visual equation with exact endpoints"
                            if deterministic_equation
                            else "OPEN: no exact visual equation closes this relation"
                        ),
                        "provenance": [candidate["id"]],
                    },
                }
            )

        closure_level = closure_level_receipt(
            source_occurrence_ids=source_ids,
            relation_receipts=relation_receipts,
        )

        selection_reading = None
        if candidates:
            signature = hashlib.sha256(
                _stable(
                    [
                        (item["candidate_relation_id"], item["verdict"])
                        for item in relation_receipts
                    ]
                ).encode("utf-8")
            ).hexdigest()
            existing = [
                reading
                for reading in self.runtime.selection_store.list_readings()
                if reading.get("metadata", {}).get("live_sense_signature")
                == signature
                and reading.get("source_event_id") == event_id
            ]
            if existing:
                selection_reading = max(
                    existing, key=lambda reading: reading["created_at"]
                )
            else:
                selection_reading = await self.runtime.selection.create_reading(
                    SelectionReadingCreate(
                        name="Live Sense relational selection",
                        authored_by=event["authored_by"],
                        field_symbols=[row["id"] for row in candidates],
                        admissible_symbols=admissible_symbols,
                        source_event_id=event_id,
                        selection_scope="live Black Mirror interaction",
                        perspective_id=event.get("perspective_id")
                        or event["authored_by"],
                        problem_id=event.get("problem_id"),
                        source_ids=list(source_ids),
                        external_key=f"live-sense:{event_id}:{signature}",
                        metadata={
                            "live_sense": True,
                            "live_sense_signature": signature,
                            "relation_receipts": relation_receipts,
                            "formal_pipeline": [
                                "UnderstandingAgent",
                                "InterpretationAgent",
                                "AdmissionPolicy",
                                "TranslationField",
                                "NRRF790",
                                "NRRF825",
                            ],
                            "closure_level": closure_level,
                            "truth_issued": False,
                        },
                    )
                )

        prior_visual_receipts = (
            self.runtime.supernet_store.list_visual_closure_receipts()
        )
        commitment_proposals = (
            self.runtime.supernet_store.list_commitment_proposals(limit=100_000)
        )
        living_problems = self.runtime.living_store.list_problems(limit=100_000)
        living_actions = self.runtime.living_store.list_actions(limit=100_000)
        living_returns = self.runtime.living_store.list_action_returns(limit=100_000)
        field_occurrences = self._field_occurrences_snapshot()
        field_events, field_event_seq = self._field_events_snapshot()
        current_event = self.runtime.supernet_store.get_event(event_id)
        source_occurrences = [
            self.runtime.store.get_occurrence(occurrence_id)
            for occurrence_id in source_ids
        ]
        visual_payload = build_visual_closure_receipt(
            event=current_event,
            source_occurrences=source_occurrences,
            relation_receipts=relation_receipts,
            closure_level=closure_level,
            selection_reading=selection_reading,
            prior_receipts=prior_visual_receipts,
            field_events=field_events,
            field_occurrences=field_occurrences,
            commitment_proposals=commitment_proposals,
            living_problems=living_problems,
            living_actions=living_actions,
            living_returns=living_returns,
            field_event_seq=field_event_seq,
        )
        visual_signature = hashlib.sha256(
            _stable(
                {
                    "visual_closure_schema": NRRF837_SCHEMA,
                    "closure_ui_contract_schema": CLOSURE_UI_SCHEMA,
                    "closure_ui_contract_builder_version": (
                        CLOSURE_UI_BUILDER_VERSION
                    ),
                    "field_event_seq": field_event_seq,
                    "unity_selector_version": UNITY_SELECTOR_VERSION,
                    "source_event_id": event_id,
                    "current_stage": current_event["current_stage"],
                    "current_verdict": current_event["current_verdict"],
                    "relations": relation_receipts,
                    "closure_level_id": closure_level["level_id"],
                    "selection": (selection_reading or {}).get("evaluation"),
                    "slearn_memory": learned_relation_memory(
                        prior_visual_receipts
                    ),
                    "commitment_proposals": [
                        {
                            "id": proposal["id"],
                            "status": proposal["status"],
                            "title": proposal.get("title"),
                            "proposed_by": proposal.get("proposed_by"),
                            "exact_terms": proposal.get("exact_terms"),
                            "open_assumptions": proposal.get(
                                "open_assumptions", []
                            ),
                            "target_event_ids": proposal.get(
                                "target_event_ids", []
                            ),
                            "required_participant_ids": proposal.get(
                                "required_participant_ids", []
                            ),
                            "resource_conditions": proposal.get(
                                "resource_conditions", []
                            ),
                            "unity_selector_version": proposal.get(
                                "unity_selector_version",
                                UNITY_SELECTOR_VERSION,
                            ),
                            "decision_event_ids": [
                                item["decision_event_id"]
                                for item in proposal.get("decision_history", [])
                            ],
                        }
                        for proposal in commitment_proposals
                    ],
                    "living_return_ids": [
                        item["id"] for item in living_returns
                    ],
                }
            ).encode("utf-8")
        ).hexdigest()
        previous_for_event = (
            self.runtime.supernet_store.latest_visual_closure_receipt(event_id)
        )
        parent_receipt_ids = _unique(
            [
                previous_for_event.get("id") if previous_for_event else "",
                prior_visual_receipts[-1].get("id")
                if prior_visual_receipts
                else "",
            ]
        )
        visual_closure, visual_closure_created = (
            self.runtime.supernet_store.append_visual_closure_receipt(
                source_event_id=event_id,
                input_signature=visual_signature,
                parent_receipt_ids=parent_receipt_ids,
                receipt=visual_payload,
            )
        )

        return {
            "source_event_id": event_id,
            "source_occurrence_ids": list(source_ids),
            "candidate_relation_ids": [row["id"] for row in candidates],
            "new_candidate_ids": _unique(proposed),
            "relation_receipts": relation_receipts,
            "admissible_relation_ids": admissible_symbols,
            "selection_reading": selection_reading,
            "closure_level": closure_level,
            "visual_closure": visual_closure,
            "visual_closure_created": visual_closure_created,
            "translation_ids": [row["id"] for row in translations],
            "translation_reconciliation": translation_reconciliation,
            "supernet_reconciliation": supernet_reconciliation,
            "open_seams_created": reopened + moral_open,
            "field_stage_id": stage["id"],
            "formal_pipeline_reused": True,
            "background_autonomy_required": False,
            "canonical_presentation": None,
            "two_person_E2E": "OPEN",
            "truth_issued": False,
        }

    async def offer(self, data: ResourceEnvelope) -> dict[str, Any]:
        base = await self.runtime.integrate_resource(data)
        sense = await self.sense_event(base["event_id"])
        return {**base, "sense_receipt": sense, "focus_event_id": base["event_id"]}

    async def interact(self, parent_event_id: str, data: ResourceEnvelope) -> dict[str, Any]:
        base = await self.runtime.interact_with_event(parent_event_id, data)
        sense = await self.sense_event(base["event_id"])
        return {**base, "sense_receipt": sense, "focus_event_id": base["event_id"]}


class LiveNaturalInterfaceManager(NaturalInterfaceManager):
    """The Black Mirror reads the interaction's relation field, not an adapter tag."""

    def _focus_event(
        self,
        events: list[dict[str, Any]],
        focus_event_id: str | None,
        perspective_id: str | None,
    ) -> dict[str, Any] | None:
        if focus_event_id is not None:
            return super()._focus_event(events, focus_event_id, perspective_id)
        sensed_ids = self.runtime.supernet_store.visual_closure_event_ids()
        sensed = [event for event in events if event["id"] in sensed_ids]
        if perspective_id:
            relative = [
                event
                for event in sensed
                if event.get("authored_by") == perspective_id
                or perspective_id in event.get("affected_perspectives", [])
                or event.get("perspective_id") == perspective_id
            ]
            if relative:
                sensed = relative
            else:
                unsensed_relative = [
                    event
                    for event in events
                    if event.get("authored_by") == perspective_id
                    or perspective_id in event.get(
                        "affected_perspectives", []
                    )
                    or event.get("perspective_id") == perspective_id
                ]
                return (
                    max(
                        unsensed_relative,
                        key=lambda item: int(item["seq"]),
                    )
                    if unsensed_relative
                    else None
                )
        if sensed:
            return max(sensed, key=lambda item: int(item["seq"]))
        return super()._focus_event(events, focus_event_id, perspective_id)

    def _sense_context(self, event: dict[str, Any] | None) -> dict[str, Any] | None:
        if event is None or not hasattr(self.runtime, "selection_store"):
            return None
        matches = [
            reading
            for reading in self.runtime.selection_store.list_readings()
            if reading.get("source_event_id") == event["id"]
            and reading.get("metadata", {}).get("live_sense") is True
        ]
        if not matches:
            return None
        reading = max(matches, key=lambda item: item["created_at"])
        return {
            "reading": reading,
            "relations": reading.get("metadata", {}).get("relation_receipts", []),
            "closure_level": reading.get("metadata", {}).get("closure_level"),
            "visual_closure": self.runtime.supernet_store.latest_visual_closure_receipt(
                event["id"]
            ),
        }

    def _project_visual_for_perspective(
        self,
        visual: dict[str, Any],
        *,
        event: dict[str, Any],
        perspective_id: str | None,
    ) -> dict[str, Any]:
        """Recompute the UI/interaction projection for the requested witness.

        The persisted receipt contains the whole NRRF843 mirror family.  Its
        originally active projection is not reused for another participant:
        selection derives a new interaction closure and UI contract from that
        participant's witnessed reading without mutating the stored receipt.
        """

        if not perspective_id:
            return visual
        requested = str(perspective_id)
        nrrf843_ui = visual.get("nrrf843_ui") or {}
        perspectives = {
            str(item)
            for item in nrrf843_ui.get("ui_family", {}).get(
                "perspective_ids", []
            )
        }
        projected = deepcopy(visual)
        if requested not in perspectives:
            projected["selected_closure_ui_contract"] = derive_open_ui_contract(
                perspective_id=requested
            )
            projected["perspective_projection_status"] = (
                "OPEN_UNWITNESSED_PERSPECTIVE"
            )
            return projected

        journey = deepcopy(visual.get("nrrf842_journey") or {})
        chosen = dict(journey.get("chosen_perspective") or {})
        chosen.update(
            {
                "perspective_id": requested,
                "status": "CHOSEN",
                "chosen": True,
                "choice_source": "REQUESTED_NRRF843_PERSPECTIVE_READING",
                "free_choice_of_perspective": True,
            }
        )
        journey["chosen_perspective"] = chosen
        interaction = derive_interaction_closure(
            truth_derivation=visual["translational_truth_axiometry"],
            nrrf843_ui=nrrf843_ui,
            nrrf842_journey=journey,
            coordination=visual["coordination"],
            ai_translation=visual["ai_translation"],
            tokenomic=visual["tokenomic"],
            visual_network=visual["visual_network"],
            black_mirror=visual["black_mirror"],
            network_return=visual["network_return"],
        )
        source_occurrences = (
            visual.get("interface_natural_form", {})
            .get("render_state", {})
            .get("source_fibre", [])
        )
        contract = derive_closure_ui_contract(
            truth_derivation=visual["translational_truth_axiometry"],
            nrrf843_ui=nrrf843_ui,
            nrrf842_journey=journey,
            interaction_closure=interaction,
            coordination=visual["coordination"],
            visual_network=visual["visual_network"],
            source_occurrences=source_occurrences,
            focus_event=event,
            field_event_seq=visual.get("closure_ui_contract", {}).get(
                "field_event_seq"
            ),
        )
        unified = derive_unified_truth_runtime(
            truth_derivation=visual["translational_truth_axiometry"],
            nrrf843_ui=nrrf843_ui,
            nrrf842_journey=journey,
            interaction_closure=interaction,
            closure_ui_contract=contract,
            coordination=visual["coordination"],
            semantic_elements=visual.get("interface_natural_form", {}).get(
                "semantic_elements", []
            ),
            interface_actions=visual.get("interface_natural_form", {}).get(
                "actions", []
            ),
            slearn=visual["slearn"],
            ai_translation=visual["ai_translation"],
            tokenomic=visual["tokenomic"],
        )
        render_state = {
            "closure_derivation_id": contract.get("closure_derivation_id"),
            "visual_closure_id": contract.get("visual_closure_id"),
            "nrrf843_ui_id": contract.get("nrrf843_ui_id"),
            "interaction_closure_id": contract.get("interaction_closure_id"),
            "closure_ui_contract": contract,
            "projection": contract.get("projection", {}),
            "return_relation": contract.get("return_relation"),
        }
        interface_form = self._refactor_interface_natural_form(
            visual=visual,
            render_state=render_state,
        )
        projected["nrrf842_journey"] = journey
        projected["interaction_closure"] = interaction
        projected["closure_ui_contract"] = contract
        projected["unified_truth_runtime"] = unified
        projected["interface_natural_form"] = interface_form
        projected["perspective_projection_status"] = "WITNESSED"
        return projected

    def _refactor_interface_natural_form(
        self,
        *,
        visual: dict[str, Any],
        render_state: dict[str, Any],
    ) -> dict[str, Any]:
        """Re-run the quotient factorization for a perspective render state."""

        truth = visual["translational_truth_axiometry"]
        form_by_member = {
            str(member): str(form["id"])
            for form in truth.get("natural_forms", [])
            for member in form.get("members", [])
        }
        members = sorted(
            str(item["id"])
            for item in truth.get("visual_existence", {}).get("forms", [])
        )
        contract = render_state["closure_ui_contract"]
        projected = contract.get("projection", {})
        state_by_id = {
            str(item["id"]): item for item in projected.get("states", [])
        }
        payload_by_form: dict[str, dict[str, Any]] = {}
        for fibre in projected.get("equality_fibres", []):
            form_id = str(fibre["id"])
            fibre_members = set(
                str(item) for item in fibre.get("member_state_ids", [])
            )
            payload_by_form[form_id] = {
                "natural_form_id": form_id,
                "perspective_visual_value": {
                    "natural_form_id": form_id,
                    "member_state_ids": sorted(fibre_members),
                    "source_returns": [
                        {
                            "state_id": state_id,
                            "source_return_ids": state_by_id[state_id][
                                "source_return_ids"
                            ],
                            "source_trace": state_by_id[state_id][
                                "source_trace"
                            ],
                        }
                        for state_id in sorted(fibre_members)
                    ],
                    "translations": [
                        item
                        for item in projected.get("translations", [])
                        if item.get("source_state_id") in fibre_members
                        or item.get("target_state_id") in fibre_members
                    ],
                    "potentials": [
                        item
                        for item in projected.get("potentials", [])
                        if item.get("shared_natural_form_id") == form_id
                        or item.get("target_state_id") in fibre_members
                        or (
                            item.get("target_state_id") is None
                            and contract.get("return_relation", {}).get(
                                "parent_natural_form_id"
                            )
                            == form_id
                        )
                    ],
                    "relation_digest": projected.get(
                        "visualization", {}
                    ).get("relation_digest"),
                },
            }
        quotient = {
            form_id: payload_by_form[form_id]
            for form_id in sorted(payload_by_form)
        }
        projection = {
            member: payload_by_form[form_by_member[member]]
            for member in members
        }
        render_states = [
            {"member_id": member, **projection[member]}
            for member in members
        ]
        closure_id = str(truth["id"])
        factorization_id = _full_digest(
            "interface-factorization-witness",
            {
                "closure": closure_id,
                "quotient_render_state": quotient,
                "projection": projection,
            },
        )
        interface_id = _full_digest(
            "interface-natural-form",
            {
                "closure": closure_id,
                "quotient_render_state": quotient,
                "factorization": factorization_id,
            },
        )
        interface_form = deepcopy(visual["interface_natural_form"])
        interface_form.update(
            {
                "id": interface_id,
                "members": members,
                "render_states": render_states,
                "quotient_render_state": quotient,
                "closure_projection": projection,
                "factorization_provenance": [factorization_id],
                "render_state": render_state,
                "render_state_factorized": True,
                "factorization_is_per_equality_fibre": True,
                "constant_whole_scene_factorization": False,
                "semantic_elements": [],
                "actions": [],
            }
        )
        return interface_form

    def _select_chart(
        self,
        event: dict[str, Any] | None,
        *,
        proof: dict[str, Any] | None,
        continuation: dict[str, Any] | None,
        life: dict[str, Any] | None,
    ) -> dict[str, Any]:
        chart = super()._select_chart(
            event,
            proof=proof,
            continuation=continuation,
            life=life,
        )
        sense = self._sense_context(event)
        if sense is None:
            return chart
        evaluation = sense["reading"]["evaluation"]
        state = str(evaluation["state"])
        relation_layers = [
            f"{item['relation_type']} · {item['verdict']}"
            for item in sense["relations"][:6]
        ]
        closure_level = sense.get("closure_level") or closure_level_receipt(
            source_occurrence_ids=event.get("exact_source_ids", []),
            relation_receipts=sense["relations"],
        )
        chart.update(
            {
                "kind": NaturalChartKind.OPEN_SELECTOR.value,
                "topology_mode": TopologyMode.SELECTOR.value,
                "lens": "selector",
                "title": (
                    "Natural relation selected"
                    if evaluation.get("natural_selection")
                    else "Sense · open relational field"
                ),
                "axiometric_reading": (
                    "The interaction has been translated against the living field; the relation itself now determines whether one form stands or several remain OPEN."
                ),
                "required_layers": [
                    "exact occurrence",
                    "Sense",
                    "interpretation",
                    "truth admission",
                    f"NRRF825 level {closure_level['endpoint']}",
                    "0↔∞ projective return seam",
                    state,
                    *relation_layers,
                ],
                "selection_reason": (
                    "NRRF790 is applied to the interaction's actual candidate-relation field after interpretation and admission, rather than to a hand-authored chart label."
                ),
                "minimal_sufficient": True,
                "canonical_pixel_layout_selected": False,
            }
        )
        return chart

    def select(
        self,
        *,
        focus_event_id: str | None = None,
        perspective_id: str | None = None,
    ) -> dict[str, Any]:
        result = super().select(
            focus_event_id=focus_event_id, perspective_id=perspective_id
        )
        sense = self._sense_context(result.get("focus_event"))
        event = result.get("focus_event")
        closure_level = None
        if event is not None:
            stored_level = sense.get("closure_level") if sense is not None else None
            closure_level = stored_level or closure_level_receipt(
                source_occurrence_ids=(event or {}).get("exact_source_ids", []),
                relation_receipts=(sense or {}).get("relations", []),
            )
        result["closure_level"] = closure_level
        result["visual_closure"] = (
            sense.get("visual_closure")
            if sense is not None
            else (
                self.runtime.supernet_store.latest_visual_closure_receipt(
                    event["id"]
                )
                if event is not None
                else None
            )
        )
        if event is not None and result["visual_closure"] is not None:
            result["visual_closure"] = self._project_visual_for_perspective(
                result["visual_closure"],
                event=event,
                perspective_id=perspective_id,
            )
        visual = result["visual_closure"] or {}
        selected_contract = visual.get("selected_closure_ui_contract")
        if selected_contract is not None:
            # An unwitnessed requested perspective must not receive another
            # perspective's WITNESSED receipt alongside its OPEN contract.
            result["visual_closure"] = None
            result["closure_level"] = None
            visual = {}
            sense = None
        result["closure_ui_contract"] = selected_contract or visual.get(
            "closure_ui_contract"
        ) or derive_open_ui_contract(
            perspective_id=(
                perspective_id
                or (event or {}).get("perspective_id")
                or (event or {}).get("authored_by")
                or "participant"
            )
        )
        result["two_person_E2E"] = "OPEN"
        if sense is not None:
            result["sense_depth"] = {
                "selection_reading_id": sense["reading"]["id"],
                "selection_state": sense["reading"]["evaluation"]["state"],
                "natural_selection": sense["reading"]["evaluation"][
                    "natural_selection"
                ],
                "admissible_relations": sense["reading"]["admissible_symbols"],
                "relations": sense["relations"],
                "closure_level_id": closure_level["level_id"],
                "closure_level_endpoint": closure_level["endpoint"],
                "formal_pipeline_reused": True,
                "nrrf825_derived": True,
                "unified_visual_closure_receipt_id": (
                    sense.get("visual_closure") or {}
                ).get("id"),
                "all_desired_functions_in_occurrence": (
                    (sense.get("visual_closure") or {})
                    .get("operational_closure", {})
                    .get("all_desired_functions_in_this_occurrence", False)
                ),
                "projective_fold_is_user_selected": False,
                "two_person_E2E": "OPEN",
                "truth_issued": False,
            }
        return result
