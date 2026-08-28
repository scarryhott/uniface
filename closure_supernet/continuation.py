from __future__ import annotations

import json
import uuid
from typing import Any, TYPE_CHECKING

from .completion import TranslationalCompletionManager
from .completion_models import CompletionMapCreate, CompletionSystemCreate, LocalTranslationStepInput
from .continuation_models import (
    ContinuationMapCreate,
    ContinuationPoint,
    ContinuationSystemCreate,
    GeometryWitness,
    RuleWitness,
)
from .continuation_store import ContinuationStore, utcnow
from .models import EvidenceStatus, Verdict
from .supernet_models import IntegrationStage, IntegrationStateCreate, ResourceEnvelope

if TYPE_CHECKING:
    from .runtime import ClosureSupernetRuntime


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in values if str(item)))


def _iterate(step: dict[str, str], start: str, count: int) -> list[str]:
    path = [start]
    current = start
    for _index in range(count):
        current = step[current]
        path.append(current)
    return path


def _orbit_first(step: dict[str, str], start: str) -> tuple[list[str], dict[str, int], int]:
    sequence: list[str] = []
    first: dict[str, int] = {}
    current = start
    while current not in first:
        first[current] = len(sequence)
        sequence.append(current)
        current = step[current]
    return sequence, first, first[current]


def _rule_witness_data(
    step: dict[str, str], source: str, target: str
) -> RuleWitness:
    sequence, first, _cycle_start = _orbit_first(step, source)
    iterate = first.get(target)
    if iterate is None:
        return RuleWitness(
            source=source,
            target=target,
            related=False,
            iterate=None,
            path=[],
            exact_unfolded_path=False,
        )
    return RuleWitness(
        source=source,
        target=target,
        related=True,
        iterate=iterate,
        path=sequence[: iterate + 1],
        exact_unfolded_path=True,
    )


def _meeting_data(
    step: dict[str, str],
    class_of: dict[str, str],
    source: str,
    target: str,
) -> GeometryWitness:
    source_rule = _rule_witness_data(step, source, target)
    target_rule = _rule_witness_data(step, target, source)
    if class_of[source] != class_of[target]:
        return GeometryWitness(
            source=source,
            target=target,
            related=False,
            closure_class=None,
            meeting_value=None,
            source_iterate=None,
            target_iterate=None,
            source_path=[],
            target_path=[],
            continuations_meet=False,
            forward_rule_source_to_target=source_rule.related,
            forward_rule_target_to_source=target_rule.related,
            symmetry_added_by_geometry=False,
        )

    source_sequence, source_first, _source_cycle = _orbit_first(step, source)
    target_sequence, target_first, _target_cycle = _orbit_first(step, target)
    intersection = set(source_first).intersection(target_first)
    if not intersection:
        raise AssertionError("points in one finite functional component must have meeting continuations")
    meeting = min(
        intersection,
        key=lambda item: (
            source_first[item] + target_first[item],
            max(source_first[item], target_first[item]),
            item,
        ),
    )
    m = source_first[meeting]
    n = target_first[meeting]
    return GeometryWitness(
        source=source,
        target=target,
        related=True,
        closure_class=class_of[source],
        meeting_value=meeting,
        source_iterate=m,
        target_iterate=n,
        source_path=source_sequence[: m + 1],
        target_path=target_sequence[: n + 1],
        continuations_meet=True,
        forward_rule_source_to_target=source_rule.related,
        forward_rule_target_to_source=target_rule.related,
        symmetry_added_by_geometry=not source_rule.related,
    )


def _completion_input(
    data: ContinuationSystemCreate,
    *,
    source_event_id: str | None,
    source_ids: list[str] | None = None,
) -> CompletionSystemCreate:
    return CompletionSystemCreate(
        name=f"{data.name} — geometry fold",
        authored_by=data.authored_by,
        presentations=data.presentations,
        steps=[
            LocalTranslationStepInput(
                source=item,
                target=data.step[item],
                label=data.step_label,
                admitted_for_completion=True,
                witness={
                    "formal_reading": "NRRF807",
                    "rule_step": True,
                    "source": item,
                    "target": data.step[item],
                },
            )
            for item in data.presentations
        ],
        source_event_id=source_event_id,
        perspective_id=data.perspective_id,
        problem_id=data.problem_id,
        source_ids=_unique((source_ids or []) + data.source_ids),
        metadata={
            **data.metadata,
            "formal_readings": ["NRRF799", "NRRF802", "NRRF807"],
            "continuation_origin": data.origin,
            "rule_is_directed": True,
            "geometry_is_generated_equality": True,
            "geometry_must_not_fabricate_rule_witness": True,
            "truth_issued": False,
        },
    )


def evaluate_continuation(
    data: ContinuationSystemCreate,
    completion_system: dict[str, Any],
) -> dict[str, Any]:
    class_of = dict(completion_system["evaluation"]["class_of"])
    rule_relation: dict[str, list[str]] = {}
    geometry_relation: dict[str, list[str]] = {}
    rule_pairs: set[tuple[str, str]] = set()
    geometry_pairs: set[tuple[str, str]] = set()

    for source in data.presentations:
        sequence, _first, _cycle_start = _orbit_first(data.step, source)
        rule_relation[source] = sequence
        for target in sequence:
            rule_pairs.add((source, target))
        geometry_relation[source] = [
            target
            for target in data.presentations
            if class_of[target] == class_of[source]
        ]
        for target in geometry_relation[source]:
            geometry_pairs.add((source, target))

    rule_reflexive = all((item, item) in rule_pairs for item in data.presentations)
    rule_transitive = all(
        (left, right) not in rule_pairs
        or (right, third) not in rule_pairs
        or (left, third) in rule_pairs
        for left in data.presentations
        for right in data.presentations
        for third in data.presentations
    )
    rule_translate = all(
        (left, right) not in rule_pairs
        or (data.step[left], data.step[right]) in rule_pairs
        for left in data.presentations
        for right in data.presentations
    )
    geometry_reflexive = all((item, item) in geometry_pairs for item in data.presentations)
    geometry_symmetric = all(
        (right, left) in geometry_pairs for left, right in geometry_pairs
    )
    geometry_transitive = all(
        (left, right) not in geometry_pairs
        or (right, third) not in geometry_pairs
        or (left, third) in geometry_pairs
        for left in data.presentations
        for right in data.presentations
        for third in data.presentations
    )
    geometry_translate = all(
        (left, right) not in geometry_pairs
        or (data.step[left], data.step[right]) in geometry_pairs
        for left in data.presentations
        for right in data.presentations
    )
    rule_le_geometry = rule_pairs.issubset(geometry_pairs)
    rule_eq_geometry = rule_pairs == geometry_pairs
    rule_symmetric = all((right, left) in rule_pairs for left, right in rule_pairs)
    injective = len(set(data.step.values())) == len(data.presentations)

    meeting_receipts = [
        _meeting_data(data.step, class_of, left, right)
        for left in data.presentations
        for right in data.presentations
    ]
    geom_iff_meet = all(
        receipt.related == receipt.continuations_meet for receipt in meeting_receipts
    ) and all(
        receipt.related == ((receipt.source, receipt.target) in geometry_pairs)
        for receipt in meeting_receipts
    )

    prefix_path = _iterate(data.step, data.origin, data.continuation_horizon)
    continuation_prefix = [
        ContinuationPoint(
            index=index,
            presentation=presentation,
            closure_class=class_of[presentation],
        ).model_dump(mode="json")
        for index, presentation in enumerate(prefix_path)
    ]
    orbit_sequence, _origin_first, cycle_start = _orbit_first(data.step, data.origin)
    differences = [
        {
            "source": source,
            "target": target,
            "geometry_related": True,
            "rule_related": False,
        }
        for source, target in sorted(geometry_pairs.difference(rule_pairs))
    ]

    return {
        "finite_executable_chart": True,
        "step_is_input_not_selected_by_nrrf807": True,
        "real_world_step_admissibility": (
            "TRANSLATIONAL_TRUTH_PRIOR"
            if data.turing_being_life_event_id is not None
            else "OPEN"
        ),
        "origin": data.origin,
        "step": data.step,
        "step_label": data.step_label,
        "step_injective": injective,
        "rule_relation": rule_relation,
        "geometry_relation": geometry_relation,
        "closure_class_of": class_of,
        "rule_reflexive": rule_reflexive,
        "rule_transitive": rule_transitive,
        "rule_translate": rule_translate,
        "geometry_reflexive": geometry_reflexive,
        "geometry_symmetric": geometry_symmetric,
        "geometry_transitive": geometry_transitive,
        "geometry_translate": geometry_translate,
        "rule_le_geometry": rule_le_geometry,
        "geometry_eq_eqvgen_rule": True,
        "geom_iff_continuations_meet": geom_iff_meet,
        "rule_eq_geometry": rule_eq_geometry,
        "rule_symmetric": rule_symmetric,
        "rule_eq_geometry_iff_rule_symmetric": rule_eq_geometry == rule_symmetric,
        "finite_injective_rule_eq_geometry": (not injective) or rule_eq_geometry,
        "continuation_prefix": continuation_prefix,
        "continuation_unique": True,
        "free_pointed_translation_reading": True,
        "continuation_natural_under_morphisms": True,
        "cl_continuation_constant": len(
            {item["closure_class"] for item in continuation_prefix}
        )
        <= 1,
        "orbit_range": orbit_sequence,
        "rule_iff_range": True,
        "origin_cycle_start": cycle_start,
        "origin_eventually_periodic_in_finite_chart": True,
        "geometry_only_pairs": differences,
        "geometry_only_pair_count": len(differences),
        "geometry_does_not_supply_missing_rule_witness": True,
        "completion_system_id": completion_system["id"],
        "canonical_representative_selected": False,
        "runtime_is_formal_proof": False,
        "truth_issued": False,
    }


def preview_continuation(data: ContinuationSystemCreate) -> dict[str, Any]:
    completion_data = _completion_input(data, source_event_id=None)
    completion_evaluation = TranslationalCompletionManager.evaluate(completion_data)
    completion_system = {
        "id": "preview",
        "evaluation": completion_evaluation.model_dump(mode="json"),
    }
    return evaluate_continuation(data, completion_system)


def canonical_examples() -> dict[str, Any]:
    ball = ContinuationSystemCreate(
        name="four-phase ball",
        presentations=["0", "1", "2", "3"],
        step={"0": "1", "1": "2", "2": "3", "3": "0"},
        origin="0",
        step_label="ballStep",
        continuation_horizon=8,
    )
    branching = ContinuationSystemCreate(
        name="finite branching translation",
        presentations=["a", "b", "c"],
        step={"a": "b", "b": "b", "c": "b"},
        origin="a",
        step_label="branch-to-return",
        continuation_horizon=4,
    )
    ball_eval = preview_continuation(ball)
    branching_eval = preview_continuation(branching)
    return {
        "ball": {
            "rule_eq_geometry": ball_eval["rule_eq_geometry"],
            "finite_injective": ball_eval["step_injective"],
            "continuation": ball_eval["continuation_prefix"],
        },
        "finite_branching": {
            "rule_eq_geometry": branching_eval["rule_eq_geometry"],
            "geometry_only_pairs": branching_eval["geometry_only_pairs"],
            "a_c_meeting": _meeting_data(
                branching.step,
                branching_eval["closure_class_of"],
                "a",
                "c",
            ).model_dump(mode="json"),
        },
        "free_line_symbolic": {
            "carrier": "ℕ",
            "step": "succ",
            "rule": "≤",
            "geometry": "one fold point",
            "rule_eq_geometry": False,
            "runtime_exhausted_infinite_line": False,
        },
        "shift_pi_symbolic": {
            "carrier": "ℝ",
            "step": "x ↦ x + π",
            "geometry_relates": ["0", "-π"],
            "rule_reaches_backwards": False,
            "runtime_exhausted_infinite_line": False,
        },
        "truth_issued": False,
    }


class ContinuationManager:
    """NRRF807 as rule and geometry lenses of one stored natural continuation."""

    def __init__(self, runtime: "ClosureSupernetRuntime", store: ContinuationStore):
        self.runtime = runtime
        self.store = store

    def capabilities(self) -> dict[str, Any]:
        return {
            "formal_readings": ["NRRF799", "NRRF802", "NRRF805", "NRRF807"],
            "canonical_runtime_operation": "integrate",
            "rule_is_unfolded_forward_continuation": True,
            "geometry_is_closure_equality": True,
            "rule_le_geometry": True,
            "geometry_eq_eqvgen_rule": True,
            "geometry_iff_continuations_meet": True,
            "rule_eq_geometry_iff_rule_symmetric": True,
            "finite_injective_rule_eq_geometry": True,
            "continuation_is_unique_free_line_reading": True,
            "continuation_is_natural": True,
            "closure_constant_along_continuation": True,
            "rule_and_geometry_are_lenses": True,
            "geometry_does_not_fabricate_rule_witness": True,
            "linked_turing_being_requires_completed_translational_truth": True,
            "step_admissibility_derived_by_nrrf807": False,
            "runtime_is_formal_proof": False,
            "truth_issued": False,
        }

    def _source_context(
        self,
        data: ContinuationSystemCreate,
    ) -> tuple[list[str], list[str], dict[str, Any] | None]:
        source_ids = list(data.source_ids)
        parents: list[str] = []
        life_event: dict[str, Any] | None = None
        if data.source_event_id is not None:
            event = self.runtime.supernet_store.get_event(data.source_event_id)
            source_ids.extend(event["exact_source_ids"])
            parents.append(data.source_event_id)
        if data.turing_being_life_event_id is not None:
            life_event = self.runtime.turing_being_store.get_life_event(
                data.turing_being_life_event_id
            )
            if life_event["translational_truth_receipt"].get("complete") is not True:
                raise ValueError(
                    "a Turing Being continuation requires completed translational truth"
                )
            parents.append(life_event["integration_event_id"])
            if life_event.get("reaction_event_id"):
                parents.append(life_event["reaction_event_id"])
            source_ids.extend(life_event["source_ids"])
        return _unique(source_ids), _unique(parents), life_event

    async def create_system(self, data: ContinuationSystemCreate) -> dict[str, Any]:
        system_id = str(uuid.uuid4())
        source_ids, parents, life_event = self._source_context(data)
        source = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=_stable(
                    {
                        "NRRF807": "rule geometry equal relation natural continuation",
                        "name": data.name,
                        "presentations": data.presentations,
                        "step": data.step,
                        "origin": data.origin,
                        "turing_being_life_event_id": data.turing_being_life_event_id,
                    }
                ),
                authored_by=data.authored_by,
                form_label="natural translation continuation",
                language_label="NRRF807 rule/geometry continuation",
                source_id="natural-continuation-supernet",
                perspective_id=data.perspective_id,
                problem_id=data.problem_id,
                capabilities=[
                    "unfold one directed rule continuation",
                    "fold the same translation into geometry equality",
                    "retain explicit rule and meeting witnesses",
                    "transport continuation along translation morphisms",
                ],
                constraints=[
                    "the translation step is supplied rather than selected by NRRF807",
                    "geometry never fabricates a missing directed rule witness",
                    "infinite examples remain formal/symbolic rather than runtime-exhausted",
                    "determination does not issue TRUE",
                ],
                relation_hints=[
                    "NRRF807",
                    "RuleRel",
                    "GeomRel",
                    "natural continuation",
                    "free translation",
                    "continuations meet",
                ],
                causal_predecessor_ids=parents,
                parent_event_ids=parents,
                affected_perspectives=[data.authored_by],
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="continuation",
                external_key=f"continuation:source:{system_id}",
                metadata={
                    **data.metadata,
                    "continuation_system_id": system_id,
                    "formal_readings": ["NRRF799", "NRRF802", "NRRF805", "NRRF807"],
                    "turing_being_translational_truth_prior": life_event is not None,
                    "rule_and_geometry_are_lenses": True,
                    "truth_issued": False,
                },
            )
        )
        completion = await self.runtime.completion.create_system(
            _completion_input(
                data,
                source_event_id=source["event_id"],
                source_ids=source_ids,
            )
        )
        evaluation = evaluate_continuation(data, completion)
        row = {
            "id": system_id,
            "occurrence_id": source["occurrence_ids"][0],
            "integration_event_id": source["event_id"],
            "completion_system_id": completion["id"],
            "name": data.name,
            "authored_by": data.authored_by,
            "presentations": data.presentations,
            "step": data.step,
            "origin": data.origin,
            "step_label": data.step_label,
            "continuation_horizon": data.continuation_horizon,
            "turing_being_life_event_id": data.turing_being_life_event_id,
            "source_event_id": data.source_event_id,
            "perspective_id": data.perspective_id,
            "problem_id": data.problem_id,
            "source_ids": source_ids,
            "evaluation": evaluation,
            "metadata": {
                **data.metadata,
                "formal_reading": "NRRF807",
                "completion_system_id": completion["id"],
                "turing_being_translational_truth_prior": life_event is not None,
                "canonical_representative_selected": False,
                "truth_issued": False,
            },
            "created_at": utcnow(),
        }
        stored = self.store.create_system(row)
        self.runtime.supernet_integrator.determine(
            source["event_id"],
            actor_id=data.authored_by,
            rigidity_scope=[
                "unique continuation from the supplied origin",
                "directed rule range",
                "generated geometry equality",
                "explicit continuation meeting witnesses",
            ],
            rigidity_receipt={
                "continuation_unique": evaluation["continuation_unique"],
                "rule_le_geometry": evaluation["rule_le_geometry"],
                "geometry_eq_eqvgen_rule": evaluation["geometry_eq_eqvgen_rule"],
                "geom_iff_continuations_meet": evaluation[
                    "geom_iff_continuations_meet"
                ],
                "rule_eq_geometry": evaluation["rule_eq_geometry"],
                "geometry_does_not_supply_missing_rule_witness": True,
                "step_admissibility_derived_by_nrrf807": False,
                "truth_issued": False,
            },
            determined_form={
                "continuation_system_id": system_id,
                "completion_system_id": completion["id"],
                "origin": data.origin,
                "continuation_prefix": evaluation["continuation_prefix"],
                "rule_relation": evaluation["rule_relation"],
                "geometry_relation": evaluation["geometry_relation"],
                "canonical_representative": None,
            },
            unitary_path_partition={
                "path": [
                    "supplied translation step",
                    "unique natural continuation",
                    "directed rule range",
                    "geometry meeting fold",
                    "OPEN return and further continuation",
                ],
                "partition": evaluation["closure_class_of"],
            },
            reason=(
                "The rule and geometry are two non-collapsing readings of the "
                "same supplied translation continuation"
            ),
        )
        self.runtime.supernet_integrator.transition(
            source["event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason=(
                    "The present continuation prefix returns while the free line "
                    "remains open to its next translated stage"
                ),
                actor_id=data.authored_by,
                returned_resource_ids=[system_id, completion["id"]],
                successor_potential=[
                    {
                        "kind": "natural-continuation",
                        "continuation_system_id": system_id,
                        "next_index": data.continuation_horizon + 1,
                        "geometry_class": evaluation["closure_class_of"][data.origin],
                    }
                ],
                metadata={
                    "nrrf807": True,
                    "rule_direction_preserved": True,
                    "geometry_does_not_fabricate_rule_witness": True,
                    "truth_issued": False,
                },
            ),
        )
        self.projection()
        return self.store.get_system(stored["id"])

    def rule_witness(self, system_id: str, source: str, target: str) -> dict[str, Any]:
        system = self.store.get_system(system_id)
        if source not in system["presentations"] or target not in system["presentations"]:
            raise KeyError("source and target must belong to the continuation system")
        return _rule_witness_data(system["step"], source, target).model_dump(mode="json")

    def geometry_witness(
        self, system_id: str, source: str, target: str
    ) -> dict[str, Any]:
        system = self.store.get_system(system_id)
        if source not in system["presentations"] or target not in system["presentations"]:
            raise KeyError("source and target must belong to the continuation system")
        return _meeting_data(
            system["step"],
            system["evaluation"]["closure_class_of"],
            source,
            target,
        ).model_dump(mode="json")

    def continuation_prefix(
        self, system_id: str, origin: str | None = None, steps: int | None = None
    ) -> dict[str, Any]:
        system = self.store.get_system(system_id)
        start = system["origin"] if origin is None else origin
        if start not in system["presentations"]:
            raise KeyError("origin must belong to the continuation system")
        count = system["continuation_horizon"] if steps is None else steps
        if count < 0 or count > 20_000:
            raise ValueError("steps must be between 0 and 20000")
        class_of = system["evaluation"]["closure_class_of"]
        path = _iterate(system["step"], start, count)
        return {
            "system_id": system_id,
            "origin": start,
            "points": [
                ContinuationPoint(
                    index=index,
                    presentation=presentation,
                    closure_class=class_of[presentation],
                ).model_dump(mode="json")
                for index, presentation in enumerate(path)
            ],
            "unique": True,
            "closure_constant": len({class_of[item] for item in path}) <= 1,
            "nonterminal": True,
            "truth_issued": False,
        }

    async def create_map(self, data: ContinuationMapCreate) -> dict[str, Any]:
        source = self.store.get_system(data.source_system_id)
        target = self.store.get_system(data.target_system_id)
        if set(data.mapping) != set(source["presentations"]):
            raise ValueError("mapping must assign exactly every source presentation")
        if any(value not in target["presentations"] for value in data.mapping.values()):
            raise ValueError("every mapped value must be a target presentation")
        intertwines = all(
            data.mapping[source["step"][item]]
            == target["step"][data.mapping[item]]
            for item in source["presentations"]
        )
        if not intertwines:
            raise ValueError("mapping must commute with the translation steps")

        completion_map = await self.runtime.completion.create_map(
            CompletionMapCreate(
                source_system_id=source["completion_system_id"],
                target_system_id=target["completion_system_id"],
                mapping=data.mapping,
                authored_by=data.authored_by,
                source_event_id=data.source_event_id,
                metadata={
                    **data.metadata,
                    "formal_reading": "NRRF807",
                    "morphism_rule": True,
                    "morphism_geom": True,
                    "continuation_natural": True,
                    "truth_issued": False,
                },
            )
        )
        source_rule = source["evaluation"]["rule_relation"]
        target_rule = target["evaluation"]["rule_relation"]
        source_geom = source["evaluation"]["geometry_relation"]
        target_geom = target["evaluation"]["geometry_relation"]
        rule_preserved = all(
            data.mapping[right] in target_rule[data.mapping[left]]
            for left in source["presentations"]
            for right in source_rule[left]
        )
        geometry_preserved = all(
            data.mapping[right] in target_geom[data.mapping[left]]
            for left in source["presentations"]
            for right in source_geom[left]
        )
        verification_horizon = max(
            source["continuation_horizon"],
            target["continuation_horizon"],
            2 * len(source["presentations"]),
        )
        continuation_natural = all(
            data.mapping[_iterate(source["step"], item, index)[-1]]
            == _iterate(target["step"], data.mapping[item], index)[-1]
            for item in source["presentations"]
            for index in range(verification_horizon + 1)
        )
        evaluation = {
            "intertwines_translation": intertwines,
            "morphism_rule": rule_preserved,
            "morphism_geom": geometry_preserved,
            "continuation_natural": continuation_natural,
            "source_origin_maps_to": data.mapping[source["origin"]],
            "target_distinguished_origin": target["origin"],
            "pointed_origin_preserved": data.mapping[source["origin"]]
            == target["origin"],
            "completion_map_relation_preserving": completion_map[
                "relation_preserving"
            ],
            "completion_map_mk_commutes": completion_map["map_mk_commutes"],
            "geometry_does_not_fabricate_rule_witness": True,
            "truth_issued": False,
        }
        map_id = str(uuid.uuid4())
        stored = self.store.create_map(
            {
                "id": map_id,
                "occurrence_id": completion_map["occurrence_id"],
                "integration_event_id": completion_map["integration_event_id"],
                "completion_map_id": completion_map["id"],
                "source_system_id": data.source_system_id,
                "target_system_id": data.target_system_id,
                "mapping": data.mapping,
                "authored_by": data.authored_by,
                "source_event_id": data.source_event_id,
                "evaluation": evaluation,
                "metadata": {
                    **data.metadata,
                    "formal_reading": "NRRF807",
                    "truth_issued": False,
                },
                "created_at": utcnow(),
            }
        )
        self.projection()
        return stored

    def projection(self) -> dict[str, Any]:
        systems = self.store.list_systems(limit=20_000)
        maps = self.store.list_maps(limit=20_000)
        projection = {
            "generated_at": utcnow(),
            "systems": systems,
            "maps": maps,
            "stats": self.store.stats(),
            "canonical_examples": canonical_examples(),
            "source_reverse_index": {
                **{
                    f"continuation-system:{item['id']}": list(item["source_ids"])
                    for item in systems
                },
                **{
                    f"continuation-map:{item['id']}": []
                    for item in maps
                },
            },
            "formal_readings": ["NRRF799", "NRRF802", "NRRF805", "NRRF807"],
            "canonical_runtime_operation": "integrate",
            "rule_and_geometry_are_lenses": True,
            "rule_direction_preserved": True,
            "geometry_does_not_fabricate_rule_witness": True,
            "truth_issued": False,
        }
        self.store.set_state("continuation_field_projection", projection)
        return projection
