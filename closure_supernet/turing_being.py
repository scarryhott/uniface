from __future__ import annotations

import json
import uuid
from typing import Any, TYPE_CHECKING

from .handed_models import HandedLifeSystemCreate
from .models import EvidenceStatus, Verdict
from .supernet_models import IntegrationStage, IntegrationStateCreate, ResourceEnvelope
from .turing_being_models import (
    LifeActionWitness,
    LifeReactionWitness,
    TuringBeingChartCreate,
    TuringBeingLifeCreate,
    TuringBeingReturnCreate,
)
from .turing_being_store import TuringBeingStore, utcnow

if TYPE_CHECKING:
    from .runtime import ClosureSupernetRuntime


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in values if str(item)))


def _truth_receipt(
    action: LifeActionWitness,
    reaction: LifeReactionWitness | None,
) -> dict[str, Any]:
    action_admitted = action.admitted and action.source_preserved
    reaction_present = reaction is not None
    reaction_admitted = bool(
        reaction is not None
        and reaction.admitted
        and reaction.source_preserved
        and reaction.returned_to_global_hair
    )
    complete = action_admitted and reaction_admitted
    return {
        "complete": complete,
        "action_present": True,
        "action_admitted": action_admitted,
        "reaction_present": reaction_present,
        "reaction_admitted": reaction_admitted,
        "source_preserved_across_action": action.source_preserved,
        "source_preserved_across_reaction": (
            None if reaction is None else reaction.source_preserved
        ),
        "returned_to_global_hair_zero_plus": (
            False if reaction is None else reaction.returned_to_global_hair
        ),
        "global_hair_zero_is_executor_pole": True,
        "local_ball_infinity_is_reactor_pole": True,
        "global_hair_zero_is_not_a_cardinality_claim": True,
        "local_ball_infinity_is_not_a_cardinality_claim": True,
        "internal_external_prior_to_translational_truth": False,
        "hand_prior_to_translational_truth": False,
        "actual_potential_prior_to_translational_truth": False,
        "finite_ball_hair_chart_prior_to_translational_truth": False,
        "truth_issued": False,
    }


def _derived_relations(receipt: dict[str, Any]) -> dict[str, Any]:
    if not receipt["complete"]:
        return {
            "internal_external_defined": False,
            "internal": None,
            "external": None,
            "hand_defined": False,
            "hand": None,
            "actual_potential_defined": False,
            "action": None,
            "potential": None,
            "actual": None,
            "continuation": None,
            "finite_chart_available": False,
            "reason": "translational truth has not yet completed the action-reaction return",
        }
    return {
        "internal_external_defined": True,
        "internal": {
            "reading": "LOCAL_BALL_INFINITY_REACTOR_RELATIVE",
            "defined_after_translational_truth": True,
            "not_an_absolute_inside": True,
        },
        "external": {
            "reading": "GLOBAL_HAIR_ZERO_EXECUTOR_RELATIVE",
            "defined_after_translational_truth": True,
            "not_an_absolute_outside": True,
        },
        "hand_defined": True,
        "hand": {
            "reading": "RELATIVE_ORIENTATION_OF_COMPLETED_ACTION_REACTION",
            "left_right_chart_selected": False,
            "defined_after_translational_truth": True,
        },
        "actual_potential_defined": True,
        "action": "GLOBAL_HAIR_ZERO_EXECUTES_TOWARD_LOCAL_BALL_INFINITY",
        "potential": "LOCAL_BALL_INFINITY_REMAINS_OPEN_TO_ADMISSIBLE_REACTION",
        "actual": "ONE_LOCAL_BALL_REACTION_HAS_RETURNED",
        "continuation": "RETURNED_GLOBAL_HAIR_ZERO_PLUS_REOPENS_AS_NEXT_EXECUTOR",
        "finite_chart_available": True,
        "finite_chart_foundational": False,
    }


class TuringBeingManager:
    """NRRF805: life action/reaction first; relative readings only after TT."""

    def __init__(self, runtime: "ClosureSupernetRuntime", store: TuringBeingStore):
        self.runtime = runtime
        self.store = store

    def capabilities(self) -> dict[str, Any]:
        return {
            "formal_readings": ["NRRF799", "NRRF800", "NRRF802", "NRRF805"],
            "canonical_runtime_operation": "integrate",
            "primitive": "global hair 0 executor → local ball ∞ reactor → returned global hair 0+",
            "global_hair_zero_role": "EXECUTOR",
            "local_ball_infinity_role": "REACTOR",
            "zero_and_infinity_are_axiometric_poles_not_cardinalities": True,
            "internal_external_prior_to_translational_truth": False,
            "hand_prior_to_translational_truth": False,
            "actual_potential_prior_to_translational_truth": False,
            "finite_ball_hair_chart_prior_to_translational_truth": False,
            "four_ball_one_hair_is_derived_chart": True,
            "action_only_event_may_remain_open": True,
            "reaction_return_completes_translational_truth": True,
            "turing_complete_assumed": False,
            "halting_is_local_return_reading": True,
            "continuation_is_reopened_global_hair_reading": True,
            "runtime_is_formal_proof": False,
            "truth_issued": False,
        }

    def _source_context(
        self, source_event_id: str | None, source_ids: list[str]
    ) -> tuple[list[str], list[str]]:
        exact_sources = list(source_ids)
        parents: list[str] = []
        if source_event_id is not None:
            event = self.runtime.supernet_store.get_event(source_event_id)
            exact_sources.extend(event["exact_source_ids"])
            parents.append(source_event_id)
        return _unique(exact_sources), parents

    def _poles(self, data: TuringBeingLifeCreate) -> tuple[dict[str, Any], dict[str, Any]]:
        return (
            {
                "pole": "0",
                "name": "GLOBAL_HAIR_ZERO",
                "role": "EXECUTOR",
                "exact_source": data.global_hair_executor,
                "cardinality": None,
                "not_external_prior_to_truth": True,
            },
            {
                "pole": "∞",
                "name": "LOCAL_BALL_INFINITY",
                "role": "REACTOR",
                "exact_source": data.local_ball_reactor,
                "cardinality": None,
                "not_internal_prior_to_truth": True,
            },
        )

    async def create_life_event(self, data: TuringBeingLifeCreate) -> dict[str, Any]:
        life_event_id = str(uuid.uuid4())
        source_ids, parents = self._source_context(data.source_event_id, data.source_ids)
        global_hair_zero, local_ball_infinity = self._poles(data)
        receipt = _truth_receipt(data.action, data.reaction)
        derived = _derived_relations(receipt)
        integration = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=_stable(
                    {
                        "NRRF805": "translational truth prior to internal/external",
                        "name": data.name,
                        "global_hair_zero": global_hair_zero,
                        "action": data.action.model_dump(mode="json"),
                        "local_ball_infinity": local_ball_infinity,
                        "reaction": (
                            None
                            if data.reaction is None
                            else data.reaction.model_dump(mode="json")
                        ),
                        "translational_truth_receipt": receipt,
                    }
                ),
                authored_by=data.authored_by,
                form_label="Turing Being of Life action-potential occurrence",
                language_label="NRRF805 translational-truth-prior life loop",
                source_id="turing-being-life-supernet",
                perspective_id=data.perspective_id,
                problem_id=data.problem_id,
                capabilities=[
                    "preserve global hair 0 as executor pole",
                    "preserve local ball infinity as reactor pole",
                    "complete action through reaction return",
                    "derive relative readings only after translational truth",
                ],
                constraints=[
                    "zero and infinity are poles, not finite cardinalities",
                    "internal and external are undefined before translational truth",
                    "hand and actual/potential are undefined before translational truth",
                    "four-ball one-hair is downstream finite chart",
                    "Turing completeness is not assumed",
                    "determination does not issue TRUE",
                ],
                relation_hints=[
                    "NRRF805",
                    "Turing Being of Life",
                    "global hair 0 executor",
                    "local ball infinity reactor",
                    "translational truth prior internal external",
                ],
                causal_predecessor_ids=parents,
                parent_event_ids=parents,
                affected_perspectives=data.affected_perspectives or [data.authored_by],
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="turing_being",
                external_key=f"turing-being:life:{life_event_id}",
                metadata={
                    **data.metadata,
                    "life_event_id": life_event_id,
                    "formal_readings": ["NRRF799", "NRRF800", "NRRF802", "NRRF805"],
                    "translational_truth_complete": receipt["complete"],
                    "internal_external_defined": derived["internal_external_defined"],
                    "finite_ball_hair_foundational": False,
                    "runtime_is_formal_proof": False,
                    "truth_issued": False,
                },
            )
        )
        now = utcnow()
        stored = self.store.create_life_event(
            {
                "id": life_event_id,
                "occurrence_id": integration["occurrence_ids"][0],
                "integration_event_id": integration["event_id"],
                "reaction_event_id": None,
                "name": data.name,
                "authored_by": data.authored_by,
                "global_hair_zero": global_hair_zero,
                "local_ball_infinity": local_ball_infinity,
                "action": data.action.model_dump(mode="json"),
                "reaction": (
                    None if data.reaction is None else data.reaction.model_dump(mode="json")
                ),
                "translational_truth_receipt": receipt,
                "derived_relations": derived,
                "affected_perspectives": data.affected_perspectives,
                "untranslated_residue": data.untranslated_residue,
                "reopening_potential": data.reopening_potential,
                "source_event_id": data.source_event_id,
                "perspective_id": data.perspective_id,
                "problem_id": data.problem_id,
                "source_ids": source_ids,
                "metadata": {
                    **data.metadata,
                    "finite_ball_hair_foundational": False,
                    "truth_issued": False,
                },
                "created_at": now,
                "updated_at": now,
            }
        )
        if receipt["complete"]:
            self._complete_canonical_event(stored)
        self.projection()
        return self.store.get_life_event(life_event_id)

    def _complete_canonical_event(self, life_event: dict[str, Any]) -> None:
        event = self.runtime.supernet_store.get_event(life_event["integration_event_id"])
        if any(item["stage"] == "DETERMINED" for item in event["state_history"]):
            return
        receipt = life_event["translational_truth_receipt"]
        derived = life_event["derived_relations"]
        self.runtime.supernet_integrator.determine(
            life_event["integration_event_id"],
            actor_id=life_event["authored_by"],
            rigidity_scope=[
                "global hair zero executor pole",
                "local ball infinity reactor pole",
                "source-preserving action and reaction return",
                "translational truth prior to relative readings",
            ],
            rigidity_receipt={
                **receipt,
                "internal_external_derived_after_truth": True,
                "finite_chart_selected": False,
                "canonical_representative_selected": False,
            },
            determined_form={
                "life_event_id": life_event["id"],
                "global_hair_zero": life_event["global_hair_zero"],
                "local_ball_infinity": life_event["local_ball_infinity"],
                "derived_relations": derived,
                "canonical_internal": None,
                "canonical_external": None,
                "canonical_hand": None,
                "canonical_finite_chart": None,
            },
            unitary_path_partition={
                "path": [
                    "global hair 0 executor",
                    "life action",
                    "local ball infinity reactor",
                    "reaction return",
                    "returned global hair 0+",
                    "reopening",
                ],
                "local_halt": "one returned local ball reaction",
                "global_continuation": "returned hair reopens as next executor",
            },
            reason=(
                "The action-reaction return completes translational truth; only now "
                "are internal/external and other relative readings available"
            ),
        )
        self.runtime.supernet_integrator.transition(
            life_event["integration_event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason="The returned global hair 0+ reopens as the next executing potential",
                actor_id=life_event["authored_by"],
                returned_resource_ids=[life_event["id"]],
                successor_potential=(
                    life_event["reopening_potential"]
                    or [
                        {
                            "kind": "Turing Being life continuation",
                            "life_event_id": life_event["id"],
                            "executor": "GLOBAL_HAIR_ZERO_PLUS",
                        }
                    ]
                ),
                metadata={
                    "translational_truth_complete": True,
                    "internal_external_defined_after_truth": True,
                    "finite_ball_hair_foundational": False,
                    "truth_issued": False,
                },
            ),
        )

    async def complete_return(
        self, life_event_id: str, data: TuringBeingReturnCreate
    ) -> dict[str, Any]:
        life_event = self.store.get_life_event(life_event_id)
        if life_event["translational_truth_receipt"].get("complete") is True:
            raise ValueError("life event already has a completed translational return")
        source_ids, parents = self._source_context(data.source_event_id, data.source_ids)
        parents.append(life_event["integration_event_id"])
        reaction_integration = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=_stable(
                    {
                        "NRRF805": "reaction returns local ball infinity to global hair zero plus",
                        "life_event_id": life_event_id,
                        "reaction": data.reaction.model_dump(mode="json"),
                    }
                ),
                authored_by=data.authored_by,
                form_label="Turing Being of Life reaction return",
                language_label="NRRF805 reaction-to-continuation",
                source_id="turing-being-life-supernet",
                capabilities=["return the local reactor into global continuation"],
                constraints=["does not define internal/external before the completed return"],
                relation_hints=["NRRF805", "reaction return", "global hair zero plus"],
                causal_predecessor_ids=_unique(parents),
                parent_event_ids=_unique(parents),
                affected_perspectives=life_event["affected_perspectives"],
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="turing_being",
                external_key=f"turing-being:reaction:{life_event_id}:{uuid.uuid4()}",
                metadata={
                    **data.metadata,
                    "life_event_id": life_event_id,
                    "truth_issued": False,
                },
            )
        )
        action = LifeActionWitness.model_validate(life_event["action"])
        receipt = _truth_receipt(action, data.reaction)
        derived = _derived_relations(receipt)
        residue = (
            life_event["untranslated_residue"]
            if data.untranslated_residue is None
            else data.untranslated_residue
        )
        reopening = (
            life_event["reopening_potential"]
            if data.reopening_potential is None
            else data.reopening_potential
        )
        merged_sources = _unique(
            life_event["source_ids"]
            + source_ids
            + reaction_integration["occurrence_ids"]
        )
        updated = self.store.complete_return(
            life_event_id,
            reaction_event_id=reaction_integration["event_id"],
            reaction=data.reaction.model_dump(mode="json"),
            receipt=receipt,
            derived_relations=derived,
            untranslated_residue=residue,
            reopening_potential=reopening,
            source_ids=merged_sources,
            metadata={
                **life_event["metadata"],
                **data.metadata,
                "translational_truth_complete": receipt["complete"],
                "truth_issued": False,
            },
        )
        self.runtime.supernet_integrator.transition(
            reaction_integration["event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason="The reaction occurrence returns into its parent life loop",
                actor_id=data.authored_by,
                returned_resource_ids=[life_event_id],
                metadata={"truth_issued": False},
            ),
        )
        if receipt["complete"]:
            self._complete_canonical_event(updated)
        self.projection()
        return self.store.get_life_event(life_event_id)

    async def derive_finite_chart(self, data: TuringBeingChartCreate) -> dict[str, Any]:
        life_event = self.store.get_life_event(data.life_event_id)
        if life_event["translational_truth_receipt"].get("complete") is not True:
            raise ValueError(
                "finite ball-hair, hand and actual/potential charts require completed translational truth"
            )
        chart_id = str(uuid.uuid4())
        system = await self.runtime.handed_life.create_system(
            HandedLifeSystemCreate(
                name=data.name,
                authored_by=data.authored_by,
                initial_hand=data.action_hand_chart,
                initial_ball_phase=data.initial_ball_phase,
                source_event_id=life_event["integration_event_id"],
                perspective_id=life_event.get("perspective_id"),
                problem_id=life_event.get("problem_id"),
                source_ids=_unique(life_event["source_ids"] + data.source_ids),
                metadata={
                    **data.metadata,
                    "derived_from_turing_being_life_event_id": data.life_event_id,
                    "foundation_status": "DERIVED_FINITE_REACTION_CHART",
                    "translational_truth_prior": True,
                    "action_hand_chart": data.action_hand_chart.value,
                    "reaction_hand_chart": data.reaction_hand_chart.value,
                    "global_hair_zero_not_hair_cardinality_one": True,
                    "local_ball_infinity_not_ball_cardinality_four": True,
                    "finite_ball_hair_foundational": False,
                    "truth_issued": False,
                },
            )
        )
        chart = {
            "kind": "DERIVED_FINITE_REACTION_CHART",
            "translational_truth_prior": True,
            "life_event_id": data.life_event_id,
            "global_hair_zero": life_event["global_hair_zero"],
            "local_ball_infinity": life_event["local_ball_infinity"],
            "internal_external": life_event["derived_relations"],
            "action_hand_chart": data.action_hand_chart.value,
            "reaction_hand_chart": data.reaction_hand_chart.value,
            "ball_chart_cardinality": 4,
            "hair_chart_cardinality": 1,
            "global_hair_zero_not_hair_cardinality_one": True,
            "local_ball_infinity_not_ball_cardinality_four": True,
            "handed_system_evaluation": system["evaluation"],
            "truth_issued": False,
        }
        stored = self.store.create_chart(
            {
                "id": chart_id,
                "life_event_id": data.life_event_id,
                "handed_system_id": system["id"],
                "integration_event_id": system["integration_event_id"],
                "chart": chart,
                "source_ids": _unique(life_event["source_ids"] + system["source_ids"]),
                "metadata": {
                    **data.metadata,
                    "foundation_status": "DERIVED_FINITE_REACTION_CHART",
                    "truth_issued": False,
                },
                "created_at": utcnow(),
            }
        )
        self.projection()
        return stored

    def projection(self) -> dict[str, Any]:
        life_events = self.store.list_life_events(limit=20_000)
        charts = self.store.list_charts(limit=20_000)
        projection = {
            "generated_at": utcnow(),
            "life_events": life_events,
            "charts": charts,
            "stats": self.store.stats(),
            "source_reverse_index": {
                **{
                    f"turing-being:{item['id']}": list(item["source_ids"])
                    for item in life_events
                },
                **{
                    f"turing-being-chart:{item['id']}": list(item["source_ids"])
                    for item in charts
                },
            },
            "formal_readings": ["NRRF799", "NRRF800", "NRRF802", "NRRF805"],
            "canonical_runtime_operation": "integrate",
            "primitive": "global hair 0 executor → local ball ∞ reactor → returned global hair 0+",
            "internal_external_prior_to_translational_truth": False,
            "finite_ball_hair_foundational": False,
            "truth_issued": False,
        }
        self.store.set_state("turing_being_field_projection", projection)
        return projection
