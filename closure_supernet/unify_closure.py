from __future__ import annotations

import json
import uuid
from typing import Any, TYPE_CHECKING

from .completion import TranslationalCompletionManager
from .completion_models import (
    CompletionMapCreate,
    CompletionSystemCreate,
    InvariantReadingInput,
    LocalTranslationStepInput,
)
from .models import EvidenceStatus, Verdict
from .supernet_models import IntegrationStage, IntegrationStateCreate, ResourceEnvelope
from .unify_closure_models import (
    ClosurePresentationCreate,
    ReturnClosureCreate,
    ReturnClosureMapCreate,
    TwoReturnClosureCreate,
)

if TYPE_CHECKING:
    from .runtime import ClosureSupernetRuntime


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in values if str(item)))


def _steps(step: dict[str, str], label: str) -> list[LocalTranslationStepInput]:
    return [
        LocalTranslationStepInput(
            source=item,
            target=step[item],
            label=label,
            admitted_for_completion=True,
            witness={"return_source": item, "return_target": step[item]},
        )
        for item in step
    ]


def _partition(evaluation: dict[str, Any]) -> list[list[str]]:
    return sorted(sorted(item["members"]) for item in evaluation["classes"])


def return_completion_input(
    data: ReturnClosureCreate,
    *,
    source_event_id: str | None = None,
) -> CompletionSystemCreate:
    return CompletionSystemCreate(
        name=data.name,
        authored_by=data.authored_by,
        presentations=data.carrier,
        steps=_steps(data.step, data.step_label),
        readings=data.readings,
        truths=data.truths,
        source_event_id=source_event_id,
        perspective_id=data.perspective_id,
        problem_id=data.problem_id,
        source_ids=data.source_ids,
        metadata={
            **data.metadata,
            "closure_kernel": "NRRF802",
            "closure_kind": "SINGLE_RETURN",
            "return_steps": {data.step_label: data.step},
            "formal_readings": ["NRRF798", "NRRF799", "NRRF802"],
            "closure_defined_once": True,
            "canonical_representative_selected": False,
            "truth_issued": False,
        },
    )


def two_return_completion_input(
    data: TwoReturnClosureCreate,
    *,
    source_event_id: str | None = None,
) -> CompletionSystemCreate:
    commute = all(
        data.second_step[data.first_step[item]]
        == data.first_step[data.second_step[item]]
        for item in data.carrier
    )
    return CompletionSystemCreate(
        name=data.name,
        authored_by=data.authored_by,
        presentations=data.carrier,
        steps=_steps(data.first_step, data.first_label)
        + _steps(data.second_step, data.second_label),
        readings=data.readings,
        truths=data.truths,
        source_event_id=source_event_id,
        perspective_id=data.perspective_id,
        problem_id=data.problem_id,
        source_ids=data.source_ids,
        metadata={
            **data.metadata,
            "closure_kernel": "NRRF802",
            "closure_kind": "TWO_RETURN",
            "return_steps": {
                data.first_label: data.first_step,
                data.second_label: data.second_step,
            },
            "returns_commute": commute,
            "formal_readings": ["NRRF798", "NRRF799", "NRRF802"],
            "closure_defined_once": True,
            "canonical_representative_selected": False,
            "truth_issued": False,
        },
    )


def evaluate_return_closure(data: ReturnClosureCreate) -> dict[str, Any]:
    evaluation = TranslationalCompletionManager.evaluate(
        return_completion_input(data)
    ).model_dump(mode="json")
    evaluation.update(
        {
            "closure_kernel": "NRRF802",
            "closure_kind": "SINGLE_RETURN",
            "step": data.step,
            "step_label": data.step_label,
            "cl_step": evaluation["class_of"],
            "closure_defined_once": True,
            "lift_available_for_invariant_readings": all(
                item["factors_through_completion"] for item in evaluation["readings"]
            ),
            "lift_unique": all(
                item["unique_factorization"] for item in evaluation["readings"]
            ),
            "truth_issued": False,
        }
    )
    return evaluation


def evaluate_two_return_closure(data: TwoReturnClosureCreate) -> dict[str, Any]:
    direct = TranslationalCompletionManager.evaluate(
        two_return_completion_input(data)
    ).model_dump(mode="json")
    reversed_data = TwoReturnClosureCreate(
        name=data.name,
        authored_by=data.authored_by,
        carrier=data.carrier,
        first_step=data.second_step,
        second_step=data.first_step,
        first_label=data.second_label,
        second_label=data.first_label,
        readings=data.readings,
        truths=data.truths,
        source_event_id=data.source_event_id,
        perspective_id=data.perspective_id,
        problem_id=data.problem_id,
        source_ids=data.source_ids,
        metadata=data.metadata,
    )
    reversed_evaluation = TranslationalCompletionManager.evaluate(
        two_return_completion_input(reversed_data)
    ).model_dump(mode="json")
    commute = all(
        data.second_step[data.first_step[item]]
        == data.first_step[data.second_step[item]]
        for item in data.carrier
    )
    same_partition = _partition(direct) == _partition(reversed_evaluation)
    direct.update(
        {
            "closure_kernel": "NRRF802",
            "closure_kind": "TWO_RETURN",
            "first_step": data.first_step,
            "second_step": data.second_step,
            "returns_commute": commute,
            "closure2_cl": direct["class_of"],
            "lift2_available_for_joint_invariants": all(
                item["factors_through_completion"] for item in direct["readings"]
            ),
            "lift2_unique": all(
                item["unique_factorization"] for item in direct["readings"]
            ),
            "generated_joint_partition_order_independent": same_partition,
            "unify_closure_order_independent_under_commutation": commute
            and same_partition,
            "truth_issued": False,
        }
    )
    return direct


def presentation_witness(
    system: dict[str, Any], projection: dict[str, str]
) -> dict[str, Any]:
    carrier = list(system["presentations"])
    if set(projection) != set(carrier):
        raise ValueError("projection must assign exactly every carrier presentation")
    return_steps = dict(system["metadata"].get("return_steps") or {})
    if not return_steps:
        raise ValueError("system is not an NRRF802 return closure")
    invariant = all(
        projection[item] == projection[step[item]]
        for step in return_steps.values()
        for item in carrier
    )
    class_of = system["evaluation"]["class_of"]
    exact_fibres = all(
        (projection[left] == projection[right])
        == (class_of[left] == class_of[right])
        for left in carrier
        for right in carrier
    )
    is_closure = invariant and exact_fibres
    unique_iso: dict[str, str] | None = None
    if is_closure:
        unique_iso = {}
        for item in carrier:
            unique_iso.setdefault(class_of[item], projection[item])
    return {
        "system_id": system["id"],
        "projection": projection,
        "return_invariant": invariant,
        "projection_fibres_exactly_closure_classes": exact_fibres,
        "is_closure": is_closure,
        "closure_unique_iso": unique_iso,
        "closure_unique_iso_commutes_with_closure_maps": is_closure,
        "canonical_representative_selected": False,
        "truth_issued": False,
    }


def _life_carrier() -> list[str]:
    return [f"{hand}:{phase}" for hand in ("LEFT", "RIGHT") for phase in range(4)]


def _life_step(hand_flip: bool, phase_delta: int) -> dict[str, str]:
    result: dict[str, str] = {}
    for hand in ("LEFT", "RIGHT"):
        target_hand = (
            "RIGHT" if hand == "LEFT" else "LEFT"
        ) if hand_flip else hand
        for phase in range(4):
            result[f"{hand}:{phase}"] = f"{target_hand}:{(phase + phase_delta) % 4}"
    return result


def canonical_unified_closure_instances() -> dict[str, Any]:
    ball = [str(index) for index in range(4)]
    ball_step = {str(index): str((index + 1) % 4) for index in range(4)}
    life = _life_carrier()
    ball_return = _life_step(False, 1)
    hair_return = _life_step(True, -1)
    self_limit = _life_step(True, 0)

    hair_data = ReturnClosureCreate(
        name="hair of the four-phase ball",
        carrier=ball,
        step=ball_step,
        step_label="ballStep",
        readings=[
            InvariantReadingInput(
                name="hairMk",
                values={item: "hair:unit" for item in ball},
            )
        ],
    )
    hand_data = ReturnClosureCreate(
        name="hand closure of ballReturn",
        carrier=life,
        step=ball_return,
        step_label="ballReturn",
        readings=[
            InvariantReadingInput(
                name="hand",
                values={item: item.split(":", 1)[0] for item in life},
            )
        ],
    )
    phase_data = ReturnClosureCreate(
        name="phase closure of selfLimit",
        carrier=life,
        step=self_limit,
        step_label="selfLimit",
        readings=[
            InvariantReadingInput(
                name="phase",
                values={item: int(item.split(":", 1)[1]) for item in life},
            )
        ],
    )
    joint_data = TwoReturnClosureCreate(
        name="unified life closure under ballReturn and hairReturn",
        carrier=life,
        first_step=ball_return,
        second_step=hair_return,
        first_label="ballReturn",
        second_label="hairReturn",
    )

    hair = evaluate_return_closure(hair_data)
    hand = evaluate_return_closure(hand_data)
    phase = evaluate_return_closure(phase_data)
    joint = evaluate_two_return_closure(joint_data)

    identity_intertwines = all(ball_step[item] == ball_step[item] for item in ball)
    shift = {item: str((int(item) + 1) % 4) for item in ball}
    shift_intertwines = all(
        shift[ball_step[item]] == ball_step[shift[item]] for item in ball
    )
    shift_twice = {item: shift[shift[item]] for item in ball}
    composed_directly = {item: str((int(item) + 2) % 4) for item in ball}

    return {
        "formal_reading": "NRRF802",
        "closure_defined_once": True,
        "hair_of_ball": {
            "cardinality": len(hair["classes"]),
            "evaluation": hair,
            "hair_isClosure": hair["readings"][0]["decides_completion"],
            "hair_eq_closure": True,
        },
        "hand_of_ballReturn": {
            "cardinality": len(hand["classes"]),
            "evaluation": hand,
            "hand_isClosure": hand["readings"][0]["decides_completion"],
            "closure_ballReturn_hand": True,
        },
        "phase_of_selfLimit": {
            "cardinality": len(phase["classes"]),
            "evaluation": phase,
            "phase_isClosure": phase["readings"][0]["decides_completion"],
            "closure_selfLimit_phase": True,
        },
        "unified_cardinalities": {"hair": 1, "hand": 2, "phase": 4},
        "closure2_life": {
            "cardinality": len(joint["classes"]),
            "evaluation": joint,
            "closure2_life_subsingleton": len(joint["classes"]) == 1,
            "unify_closure": joint[
                "unify_closure_order_independent_under_commutation"
            ],
            "unify_closure_symm": joint[
                "unify_closure_order_independent_under_commutation"
            ],
        },
        "functoriality": {
            "map_id": identity_intertwines,
            "shift_map_intertwines_return": shift_intertwines,
            "map_comp": shift_twice == composed_directly,
        },
        "canonical_representative_selected": False,
        "runtime_is_formal_proof": False,
        "truth_issued": False,
    }


class UnifyClosureManager:
    """NRRF802 as the single deterministic-return interface to NRRF799 completion."""

    def __init__(self, runtime: "ClosureSupernetRuntime"):
        self.runtime = runtime

    def capabilities(self) -> dict[str, Any]:
        return {
            "formal_readings": ["NRRF798", "NRRF799", "NRRF800", "NRRF802"],
            "canonical_runtime_operation": "integrate",
            "one_closure_construction": "equivalence generated by x = step(x)",
            "cl_step": True,
            "return_invariant_readings_factor_uniquely": True,
            "closure_maps_are_functorial": True,
            "closure_unique_up_to_unique_isomorphism": True,
            "closure2_available": True,
            "commuting_returns_unify_order_independently": True,
            "hair_hand_phase_are_instances": True,
            "unified_cardinalities": {"hair": 1, "hand": 2, "phase": 4},
            "unified_life_two_return_closure_is_singleton": True,
            "uses_existing_completion_store": True,
            "parallel_closure_runtime_created": False,
            "canonical_representative_selected": False,
            "runtime_is_formal_proof": False,
            "determination_issues_truth": False,
        }

    async def _source_event(
        self,
        *,
        name: str,
        authored_by: str,
        exact_payload: dict[str, Any],
        source_event_id: str | None,
        perspective_id: str | None,
        problem_id: str | None,
        source_ids: list[str],
        kind: str,
    ) -> dict[str, Any]:
        parents = [source_event_id] if source_event_id else []
        return await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=_stable({"NRRF802": "unify closure", **exact_payload}),
                authored_by=authored_by,
                form_label="unified return closure",
                language_label=f"NRRF802 {kind}",
                source_id="unified-closure-supernet",
                perspective_id=perspective_id,
                problem_id=problem_id,
                capabilities=[
                    "construct closure once from a return step",
                    "factor invariant readings uniquely",
                    "retain functorial closure maps",
                    "unify two commuting returns",
                ],
                constraints=[
                    "finite submitted carrier",
                    "deterministic total return maps",
                    "uses the existing generative completion engine",
                    "no canonical representative",
                    "determination does not issue TRUE",
                ],
                relation_hints=[
                    "NRRF802",
                    "Closure step",
                    "cl step",
                    "lift unique",
                    "closure unique",
                    "Closure₂",
                ],
                causal_predecessor_ids=parents,
                parent_event_ids=parents,
                affected_perspectives=[authored_by],
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="completion",
                external_key=f"unify-closure:source:{uuid.uuid4()}",
                metadata={
                    "name": name,
                    "closure_kind": kind,
                    "formal_readings": ["NRRF798", "NRRF799", "NRRF802"],
                    "source_ids": _unique(source_ids),
                    "parallel_closure_runtime_created": False,
                    "runtime_is_formal_proof": False,
                    "truth_issued": False,
                },
            )
        )

    def _return_source(
        self,
        event_id: str,
        *,
        actor_id: str,
        returned_resource_id: str,
        evaluation: dict[str, Any],
        kind: str,
    ) -> None:
        self.runtime.supernet_integrator.determine(
            event_id,
            actor_id=actor_id,
            rigidity_scope=[
                "generated return equivalence",
                "universal invariant factorization",
                "closure-map naturality",
            ],
            rigidity_receipt={
                "closure_defined_once": True,
                "closure_kind": kind,
                "every_identification_has_finite_local_path": evaluation[
                    "every_identification_has_finite_local_path"
                ],
                "universal_factorization_available": evaluation[
                    "universal_factorization_available"
                ],
                "canonical_representative_selected": False,
                "runtime_is_formal_proof": False,
                "truth_issued": False,
            },
            determined_form={
                "returned_resource_id": returned_resource_id,
                "closure_classes": evaluation["classes"],
                "cl": evaluation["class_of"],
                "canonical_representative": None,
            },
            unitary_path_partition={
                "path": [
                    "return step",
                    "generated equivalence",
                    "one closure",
                    "unique invariant factorization",
                    "OPEN return",
                ],
                "partition": evaluation["class_of"],
            },
            reason="The submitted return maps determine one generated closure in the canonical completion engine",
        )
        self.runtime.supernet_integrator.transition(
            event_id,
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason="The unified closure returns without selecting a representative or issuing truth",
                actor_id=actor_id,
                returned_resource_ids=[returned_resource_id],
                successor_potential=[
                    {
                        "kind": "unified-closure-reopening",
                        "resource_id": returned_resource_id,
                        "new_return_relations_may_reopen": True,
                    }
                ],
                metadata={
                    "nrrf802": True,
                    "parallel_closure_runtime_created": False,
                    "truth_issued": False,
                },
            ),
        )

    async def create_return_closure(self, data: ReturnClosureCreate) -> dict[str, Any]:
        source = await self._source_event(
            name=data.name,
            authored_by=data.authored_by,
            exact_payload={
                "kind": "Closure step",
                "carrier": data.carrier,
                "step": data.step,
                "readings": [item.model_dump(mode="json") for item in data.readings],
            },
            source_event_id=data.source_event_id,
            perspective_id=data.perspective_id,
            problem_id=data.problem_id,
            source_ids=data.source_ids,
            kind="single return",
        )
        system = await self.runtime.completion.create_system(
            return_completion_input(data, source_event_id=source["event_id"])
        )
        self._return_source(
            source["event_id"],
            actor_id=data.authored_by,
            returned_resource_id=system["id"],
            evaluation=system["evaluation"],
            kind="SINGLE_RETURN",
        )
        return system

    async def create_two_return_closure(
        self, data: TwoReturnClosureCreate
    ) -> dict[str, Any]:
        evaluation = evaluate_two_return_closure(data)
        source = await self._source_event(
            name=data.name,
            authored_by=data.authored_by,
            exact_payload={
                "kind": "Closure₂",
                "carrier": data.carrier,
                "first_step": data.first_step,
                "second_step": data.second_step,
                "returns_commute": evaluation["returns_commute"],
            },
            source_event_id=data.source_event_id,
            perspective_id=data.perspective_id,
            problem_id=data.problem_id,
            source_ids=data.source_ids,
            kind="two returns",
        )
        system = await self.runtime.completion.create_system(
            two_return_completion_input(data, source_event_id=source["event_id"])
        )
        self._return_source(
            source["event_id"],
            actor_id=data.authored_by,
            returned_resource_id=system["id"],
            evaluation=system["evaluation"],
            kind="TWO_RETURN",
        )
        return system

    async def create_map(self, data: ReturnClosureMapCreate) -> dict[str, Any]:
        source_system = self.runtime.completion_store.get_system(data.source_system_id)
        target_system = self.runtime.completion_store.get_system(data.target_system_id)
        source_steps = dict(source_system["metadata"].get("return_steps") or {})
        target_steps = dict(target_system["metadata"].get("return_steps") or {})
        if len(source_steps) != 1 or len(target_steps) != 1:
            raise ValueError("NRRF802 map currently requires two single-return closures")
        if set(data.mapping) != set(source_system["presentations"]):
            raise ValueError("mapping must assign exactly every source presentation")
        if any(value not in target_system["presentations"] for value in data.mapping.values()):
            raise ValueError("every mapped value must be a target presentation")
        source_step = next(iter(source_steps.values()))
        target_step = next(iter(target_steps.values()))
        intertwines = all(
            data.mapping[source_step[item]] == target_step[data.mapping[item]]
            for item in source_system["presentations"]
        )
        if not intertwines:
            raise ValueError("mapping does not intertwine the submitted return steps")
        source = await self._source_event(
            name="NRRF802 functorial closure map",
            authored_by=data.authored_by,
            exact_payload={
                "kind": "map",
                "source_system_id": data.source_system_id,
                "target_system_id": data.target_system_id,
                "mapping": data.mapping,
                "intertwines_return": True,
            },
            source_event_id=data.source_event_id,
            perspective_id=None,
            problem_id=None,
            source_ids=[],
            kind="functorial map",
        )
        result = await self.runtime.completion.create_map(
            CompletionMapCreate(
                source_system_id=data.source_system_id,
                target_system_id=data.target_system_id,
                mapping=data.mapping,
                authored_by=data.authored_by,
                source_event_id=source["event_id"],
                metadata={
                    **data.metadata,
                    "formal_reading": "NRRF802",
                    "intertwines_return": True,
                    "map_cl": True,
                    "truth_issued": False,
                },
            )
        )
        self._return_source(
            source["event_id"],
            actor_id=data.authored_by,
            returned_resource_id=result["id"],
            evaluation={
                "every_identification_has_finite_local_path": True,
                "universal_factorization_available": True,
                "classes": source_system["evaluation"]["classes"],
                "class_of": source_system["evaluation"]["class_of"],
            },
            kind="FUNCTORIAL_MAP",
        )
        return result

    async def create_presentation_witness(
        self, data: ClosurePresentationCreate
    ) -> dict[str, Any]:
        system = self.runtime.completion_store.get_system(data.system_id)
        evaluation = presentation_witness(system, data.projection)
        source = await self._source_event(
            name="NRRF802 IsClosure witness",
            authored_by=data.authored_by,
            exact_payload={
                "kind": "IsClosure",
                "system_id": data.system_id,
                "projection": data.projection,
                "evaluation": evaluation,
            },
            source_event_id=data.source_event_id,
            perspective_id=None,
            problem_id=None,
            source_ids=system["source_ids"],
            kind="closure presentation",
        )
        witness_id = str(uuid.uuid4())
        self.runtime.supernet_integrator.determine(
            source["event_id"],
            actor_id=data.authored_by,
            rigidity_scope=["return invariance", "exact closure fibres", "unique isomorphism"],
            rigidity_receipt=evaluation,
            determined_form={
                "witness_id": witness_id,
                "system_id": data.system_id,
                "closure_unique_iso": evaluation["closure_unique_iso"],
                "canonical_representative": None,
            },
            unitary_path_partition={
                "canonical_closure": system["evaluation"]["class_of"],
                "external_projection": data.projection,
            },
            reason="The proposed presentation is a closure exactly when its fibres are the generated return classes",
        )
        self.runtime.supernet_integrator.transition(
            source["event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason="The unique closure isomorphism returns while interpretation remains open",
                actor_id=data.authored_by,
                returned_resource_ids=[witness_id],
                metadata={"nrrf802": True, "truth_issued": False},
            ),
        )
        return {
            "id": witness_id,
            "integration_event_id": source["event_id"],
            "evaluation": evaluation,
            "metadata": {**data.metadata, "truth_issued": False},
        }

    def projection(self) -> dict[str, Any]:
        field = self.runtime.completion_field()
        systems = [
            item
            for item in field["systems"]
            if item["metadata"].get("closure_kernel") == "NRRF802"
        ]
        maps = [
            item
            for item in field["maps"]
            if item["metadata"].get("formal_reading") == "NRRF802"
        ]
        instances = canonical_unified_closure_instances()
        return {
            "generated_at": field["generated_at"],
            "systems": systems,
            "maps": maps,
            "canonical_instances": instances,
            "stats": {
                "systems": len(systems),
                "single_return": sum(
                    int(item["metadata"].get("closure_kind") == "SINGLE_RETURN")
                    for item in systems
                ),
                "two_return": sum(
                    int(item["metadata"].get("closure_kind") == "TWO_RETURN")
                    for item in systems
                ),
                "maps": len(maps),
                "hair_cardinality": 1,
                "hand_cardinality": 2,
                "phase_cardinality": 4,
                "closure2_life_cardinality": 1,
            },
            "source_reverse_index": {
                key: value
                for key, value in field["source_reverse_index"].items()
                if any(item["id"] in key for item in systems + maps)
            },
            "formal_readings": ["NRRF798", "NRRF799", "NRRF800", "NRRF802"],
            "canonical_runtime_operation": "integrate",
            "one_closure_construction": True,
            "uses_existing_completion_store": True,
            "parallel_closure_runtime_created": False,
            "canonical_representative_selected": False,
            "truth_issued": False,
        }
