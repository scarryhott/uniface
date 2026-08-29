from __future__ import annotations

import hashlib
import json
from typing import Any, TYPE_CHECKING

from .axiometry import operator_keys
from .models import Verdict
from .natural_interface import NaturalInterfaceManager
from .natural_interface_models import NaturalChartKind
from .nrrf825 import closure_level_receipt
from .selection_models import SelectionReadingCreate
from .supernet_models import ResourceEnvelope
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

    def capabilities(self) -> dict[str, Any]:
        return {
            "interaction_time_sense": True,
            "uses_existing_understanding_agent": True,
            "uses_existing_interpretation_provider": True,
            "uses_existing_admission_policy": True,
            "uses_existing_translation_field": True,
            "uses_existing_nrrf790_selector": True,
            "derives_nrrf825_equality_level": True,
            "unified_visual_translational_closure": True,
            "black_mirror_slearn_ai_tokenomic_one_receipt": True,
            "slearn_memory_changes_candidate_priority": True,
            "tokenomic_units_are_equality_classes": True,
            "visual_network_drives_next_operation": True,
            "level_derived_from_admitted_returns": True,
            "projective_zero_infinity_fold": "tan((π/2)·collapse)",
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
            field_events=self.runtime.supernet_store.list_events(limit=200_000),
        )
        visual_signature = hashlib.sha256(
            _stable(
                {
                    "source_event_id": event_id,
                    "current_stage": current_event["current_stage"],
                    "current_verdict": current_event["current_verdict"],
                    "relations": relation_receipts,
                    "closure_level_id": closure_level["level_id"],
                    "selection": (selection_reading or {}).get("evaluation"),
                    "slearn_memory": learned_relation_memory(
                        prior_visual_receipts
                    ),
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
