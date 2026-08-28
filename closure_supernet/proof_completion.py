from __future__ import annotations

import json
import uuid
from collections import deque
from itertools import product
from typing import Any, TYPE_CHECKING

from .completion_models import CompletionSystemCreate, LocalTranslationStepInput
from .models import EvidenceStatus, Verdict
from .proof_completion_models import (
    AdmissionCreate,
    AdmissionWitness,
    BalanceCreate,
    BalanceWitness,
    DerivationCreate,
    DerivationWitness,
    ProofReceiptKind,
    ProofSystemCreate,
)
from .proof_completion_store import ProofCompletionStore, utcnow
from .supernet_models import IntegrationStage, IntegrationStateCreate, ResourceEnvelope

if TYPE_CHECKING:
    from .runtime import ClosureSupernetRuntime


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in values if str(item)))


def _step_dict(step: LocalTranslationStepInput | dict[str, Any], index: int) -> dict[str, Any]:
    if isinstance(step, LocalTranslationStepInput):
        data = step.model_dump(mode="json")
    else:
        data = dict(step)
    data.setdefault("label", "admitted step")
    data.setdefault("admitted_for_completion", True)
    data.setdefault("witness", {})
    data["index"] = index
    return data


def _steps(steps: list[LocalTranslationStepInput] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [_step_dict(step, index) for index, step in enumerate(steps)]


def _admitted_steps(
    steps: list[LocalTranslationStepInput] | list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [step for step in _steps(steps) if step["admitted_for_completion"]]


def _adjacency(
    presentations: list[str],
    steps: list[LocalTranslationStepInput] | list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    result = {item: [] for item in presentations}
    for step in _admitted_steps(steps):
        result[step["source"]].append(step)
    return result


def shortest_derivation(
    presentations: list[str],
    steps: list[LocalTranslationStepInput] | list[dict[str, Any]],
    source: str,
    target: str,
) -> DerivationWitness:
    known = set(presentations)
    if source not in known or target not in known:
        raise KeyError("source and target must belong to the proof system")
    if source == target:
        return DerivationWitness(
            source=source,
            target=target,
            admitted=True,
            length=0,
            trace=[source],
            step_labels=[],
            step_indices=[],
            completion_proposition=True,
        )

    adjacency = _adjacency(presentations, steps)
    queue: deque[str] = deque([source])
    predecessor: dict[str, tuple[str, dict[str, Any]]] = {}
    seen = {source}
    while queue:
        current = queue.popleft()
        for step in adjacency[current]:
            nxt = step["target"]
            if nxt in seen:
                continue
            seen.add(nxt)
            predecessor[nxt] = (current, step)
            if nxt == target:
                queue.clear()
                break
            queue.append(nxt)

    if target not in seen:
        return DerivationWitness(
            source=source,
            target=target,
            admitted=False,
            length=None,
            trace=[],
            step_labels=[],
            step_indices=[],
            completion_proposition=False,
        )

    reversed_nodes = [target]
    reversed_steps: list[dict[str, Any]] = []
    current = target
    while current != source:
        previous, step = predecessor[current]
        reversed_steps.append(step)
        reversed_nodes.append(previous)
        current = previous
    trace = list(reversed(reversed_nodes))
    path_steps = list(reversed(reversed_steps))
    return DerivationWitness(
        source=source,
        target=target,
        admitted=True,
        length=len(path_steps),
        trace=trace,
        step_labels=[str(step["label"]) for step in path_steps],
        step_indices=[int(step["index"]) for step in path_steps],
        completion_proposition=True,
    )


def validate_derivation_path(
    presentations: list[str],
    steps: list[LocalTranslationStepInput] | list[dict[str, Any]],
    source: str,
    target: str,
    path: list[str],
) -> DerivationWitness:
    known = set(presentations)
    if not path or path[0] != source or path[-1] != target:
        raise ValueError("a supplied derivation path must begin at source and end at target")
    if any(item not in known for item in path):
        raise ValueError("every derivation path point must belong to the proof system")
    admitted = _admitted_steps(steps)
    labels: list[str] = []
    indices: list[int] = []
    for left, right in zip(path, path[1:]):
        witness = next(
            (
                step
                for step in admitted
                if step["source"] == left and step["target"] == right
            ),
            None,
        )
        if witness is None:
            raise ValueError(f"path edge {left!r} → {right!r} is not an admitted step")
        labels.append(str(witness["label"]))
        indices.append(int(witness["index"]))
    return DerivationWitness(
        source=source,
        target=target,
        admitted=True,
        length=len(path) - 1,
        trace=path,
        step_labels=labels,
        step_indices=indices,
        shortest=False,
        completion_proposition=True,
    )


def _all_shortest(
    presentations: list[str],
    steps: list[LocalTranslationStepInput] | list[dict[str, Any]],
) -> dict[str, dict[str, DerivationWitness]]:
    return {
        source: {
            target: shortest_derivation(presentations, steps, source, target)
            for target in presentations
        }
        for source in presentations
    }


def _relation_from_witnesses(
    presentations: list[str],
    witnesses: dict[str, dict[str, DerivationWitness]],
) -> tuple[dict[str, list[str]], set[tuple[str, str]]]:
    relation: dict[str, list[str]] = {}
    pairs: set[tuple[str, str]] = set()
    for source in presentations:
        related = [target for target in presentations if witnesses[source][target].admitted]
        relation[source] = related
        pairs.update((source, target) for target in related)
    return relation, pairs


def _equivalence_classes(
    presentations: list[str],
    related: set[tuple[str, str]],
    *,
    prefix: str,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    remaining = set(presentations)
    classes: list[dict[str, Any]] = []
    class_of: dict[str, str] = {}
    for anchor in presentations:
        if anchor not in remaining:
            continue
        members = [
            item
            for item in presentations
            if item in remaining
            and (anchor, item) in related
            and (item, anchor) in related
        ]
        class_id = f"{prefix}:{len(classes)}"
        for item in members:
            remaining.discard(item)
            class_of[item] = class_id
        classes.append(
            {
                "id": class_id,
                "representative": members[0],
                "members": members,
                "canonical_representative_selected": False,
            }
        )
    return classes, class_of


def _geometry_classes(
    presentations: list[str],
    steps: list[LocalTranslationStepInput] | list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, str], set[tuple[str, str]]]:
    neighbours = {item: set() for item in presentations}
    for step in _admitted_steps(steps):
        left = step["source"]
        right = step["target"]
        neighbours[left].add(right)
        neighbours[right].add(left)
    remaining = set(presentations)
    classes: list[dict[str, Any]] = []
    class_of: dict[str, str] = {}
    pairs: set[tuple[str, str]] = set()
    for anchor in presentations:
        if anchor not in remaining:
            continue
        stack = [anchor]
        members: list[str] = []
        remaining.remove(anchor)
        while stack:
            current = stack.pop()
            members.append(current)
            for nxt in neighbours[current]:
                if nxt in remaining:
                    remaining.remove(nxt)
                    stack.append(nxt)
        members.sort(key=presentations.index)
        class_id = f"geometry:{len(classes)}"
        for item in members:
            class_of[item] = class_id
        pairs.update(product(members, members))
        classes.append(
            {
                "id": class_id,
                "representative": members[0],
                "members": members,
                "canonical_representative_selected": False,
            }
        )
    return classes, class_of, pairs


def _admit_set(
    admits_relation: dict[str, list[str]], seeds: list[str]
) -> list[str]:
    admitted: set[str] = set()
    for seed in seeds:
        admitted.update(admits_relation[seed])
    order = list(admits_relation)
    return [item for item in order if item in admitted]


def admission_witness_from_evaluation(
    system: dict[str, Any], seeds: list[str]
) -> AdmissionWitness:
    known = set(system["presentations"])
    normalized = _unique(seeds)
    if not normalized or any(seed not in known for seed in normalized):
        raise KeyError("every admission seed must belong to the proof system")
    relation = system["evaluation"]["admits_relation"]
    admitted_set = _admit_set(relation, normalized)
    second = _admit_set(relation, admitted_set)
    return AdmissionWitness(
        seeds=normalized,
        admitted_set=admitted_set,
        extensive=set(normalized).issubset(admitted_set),
        monotone_by_union=True,
        idempotent=second == admitted_set,
        fixed_point=second == admitted_set,
        least_step_closed_superset=True,
    )


def _reading_receipts(
    data: ProofSystemCreate,
    admits_pairs: set[tuple[str, str]],
    balance_classes: list[dict[str, Any]],
    geometry_classes: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    admitted_steps = _admitted_steps(data.steps)

    def receipt(item: Any, *, truth: bool) -> dict[str, Any]:
        values = item.values
        step_invariant = all(
            values[step["source"]] == values[step["target"]]
            for step in admitted_steps
        )
        completion_invariant = all(
            values[left] == values[right] for left, right in admits_pairs
        )
        balance_constant = all(
            len({_stable(values[member]) for member in cls["members"]}) <= 1
            for cls in balance_classes
        )
        geometry_constant = all(
            len({_stable(values[member]) for member in cls["members"]}) <= 1
            for cls in geometry_classes
        )
        balance_values = (
            {
                cls["id"]: values[cls["members"][0]]
                for cls in balance_classes
            }
            if balance_constant
            else None
        )
        geometry_values = (
            {
                cls["id"]: values[cls["members"][0]]
                for cls in geometry_classes
            }
            if geometry_constant
            else None
        )
        return {
            "name": item.name,
            "kind": "truth" if truth else "reading",
            "unmoved_by_admitted_steps": step_invariant,
            "unmoved_by_completion": completion_invariant,
            "step_invariant_iff_completion_invariant": (
                step_invariant == completion_invariant
            ),
            "factors_through_balance": balance_constant,
            "factors_uniquely_through_meta_abstraction": (
                step_invariant and balance_constant
            ),
            "balance_values": balance_values,
            "factors_through_geometry": geometry_constant,
            "geometry_values": geometry_values,
            "metadata": item.metadata,
        }

    return (
        [receipt(item, truth=False) for item in data.readings],
        [receipt(item, truth=True) for item in data.truths],
    )


def evaluate_proof_system(
    data: ProofSystemCreate,
    *,
    geometry_completion_system: dict[str, Any] | None = None,
) -> dict[str, Any]:
    admitted_steps = _admitted_steps(data.steps)
    all_steps = _steps(data.steps)
    witnesses = _all_shortest(data.presentations, data.steps)
    admits_relation, admits_pairs = _relation_from_witnesses(
        data.presentations, witnesses
    )
    balance_pairs = {
        (left, right)
        for left, right in admits_pairs
        if (right, left) in admits_pairs
    }
    balance_classes, balance_class_of = _equivalence_classes(
        data.presentations,
        balance_pairs,
        prefix="balance",
    )
    computed_geometry_classes, computed_geometry_class_of, geometry_pairs = (
        _geometry_classes(data.presentations, data.steps)
    )
    if geometry_completion_system is not None:
        supplied = dict(geometry_completion_system["evaluation"]["class_of"])
        supplied_pairs = {
            (left, right)
            for left in data.presentations
            for right in data.presentations
            if supplied[left] == supplied[right]
        }
        geometry_matches_existing_completion = supplied_pairs == geometry_pairs
        geometry_class_of = supplied
        geometry_classes = geometry_completion_system["evaluation"]["classes"]
    else:
        geometry_matches_existing_completion = True
        geometry_class_of = computed_geometry_class_of
        geometry_classes = computed_geometry_classes

    readings, truths = _reading_receipts(
        data,
        admits_pairs,
        balance_classes,
        computed_geometry_classes,
    )
    max_shortest = max(
        (
            witness.length or 0
            for by_target in witnesses.values()
            for witness in by_target.values()
            if witness.admitted
        ),
        default=0,
    )
    n = len(data.presentations)
    proof_bound = max_shortest <= max(0, n - 1)
    completion_eq_proof = all(
        ((left, right) in admits_pairs) == witnesses[left][right].completion_proposition
        for left in data.presentations
        for right in data.presentations
    )
    admits_symmetric = all((right, left) in admits_pairs for left, right in admits_pairs)
    balance_le_geometry = balance_pairs.issubset(geometry_pairs)
    balance_eq_geometry = balance_pairs == geometry_pairs

    closure_idempotent_all = all(
        set(_admit_set(admits_relation, admits_relation[source]))
        == set(admits_relation[source])
        for source in data.presentations
    )
    fixed_point_count: int | None = None
    fixed_point_exhaustive = n <= 12
    if fixed_point_exhaustive:
        fixed_point_count = 0
        for mask in range(1 << n):
            seeds = [
                data.presentations[index]
                for index in range(n)
                if mask & (1 << index)
            ]
            closure = _admit_set(admits_relation, seeds)
            if set(closure) == set(seeds):
                fixed_point_count += 1

    outgoing: dict[str, int] = {item: 0 for item in data.presentations}
    for step in admitted_steps:
        outgoing[step["source"]] += 1
    deterministic_return = all(count == 1 for count in outgoing.values())

    return {
        "finite_executable_chart": True,
        "relation_is_admitted_steps": True,
        "presentations": data.presentations,
        "admitted_steps": admitted_steps,
        "unadmitted_steps": [
            step for step in all_steps if not step["admitted_for_completion"]
        ],
        "proof_is_data": True,
        "proof_trace_available": True,
        "proof_concatenation_available": True,
        "completion_is_proposition": True,
        "completion_eq_proof": completion_eq_proof,
        "completion_eq_nonempty_derivation": completion_eq_proof,
        "deriv_prop_ext": completion_eq_proof,
        "meta_abstraction_surjective": completion_eq_proof,
        "meta_abstraction_forgets": [
            "derivation identity",
            "length",
            "ordered intermediate readings",
            "step labels",
            "alternative proof paths",
        ],
        "canonical_derivation_selected": False,
        "admits_relation": admits_relation,
        "shortest_proof_lengths": {
            left: {
                right: witnesses[left][right].length
                for right in data.presentations
                if witnesses[left][right].admitted
            }
            for left in data.presentations
        },
        "known_shortest_derivations": len(admits_pairs),
        "finite_proof_search_halts": True,
        "short_proof_bound": max(0, n - 1),
        "max_shortest_proof_length": max_shortest,
        "all_admissions_have_short_proof": proof_bound,
        "admission_decidable": True,
        "truth_admission": {
            "extensive": all(item in admits_relation[item] for item in data.presentations),
            "monotone_by_union": True,
            "idempotent": closure_idempotent_all,
            "admitted_sets_are_fixed_points": True,
            "fixed_points_are_admitted_sets": True,
            "least_step_closed_superset": True,
            "admit_isLeast": True,
            "admit_gi": True,
            "runtime_exhaustive_fixed_point_check": fixed_point_exhaustive,
            "fixed_point_count": fixed_point_count,
        },
        "balance_is_mutual_admission": True,
        "balance_relation": {
            left: [
                right
                for right in data.presentations
                if (left, right) in balance_pairs
            ]
            for left in data.presentations
        },
        "balance_classes": balance_classes,
        "balance_class_of": balance_class_of,
        "completion_object": "quotient by relative balance",
        "completion_object_cardinality": len(balance_classes),
        "metaAbs_factorsUniquely": all(
            (not item["unmoved_by_admitted_steps"])
            or item["factors_uniquely_through_meta_abstraction"]
            for item in readings + truths
        ),
        "readings": readings,
        "truths": truths,
        "geometry_classes": geometry_classes,
        "geometry_class_of": geometry_class_of,
        "geometry_matches_existing_completion": geometry_matches_existing_completion,
        "balance_le_geometry": balance_le_geometry,
        "balance_eq_geometry": balance_eq_geometry,
        "balance_eq_geometry_when_return_closes": (
            (not admits_symmetric) or balance_eq_geometry
        ),
        "return_closes": admits_symmetric,
        "deterministic_return_relation": deterministic_return,
        "proof_is_counting_for_deterministic_return": deterministic_return,
        "geometry_does_not_replace_proof": True,
        "geometry_may_forget_direction_beyond_balance": not balance_eq_geometry,
        "proof_fibres_reopenable": True,
        "runtime_is_formal_proof": False,
        "truth_issued": False,
    }


def _geometry_input(
    data: ProofSystemCreate,
    *,
    source_event_id: str,
    source_ids: list[str],
) -> CompletionSystemCreate:
    return CompletionSystemCreate(
        name=f"{data.name} — generated geometry shadow",
        authored_by=data.authored_by,
        presentations=data.presentations,
        steps=data.steps,
        source_event_id=source_event_id,
        perspective_id=data.perspective_id,
        problem_id=data.problem_id,
        source_ids=source_ids,
        metadata={
            **data.metadata,
            "formal_readings": ["NRRF799", "NRRF807", "NRRF811"],
            "proof_system_geometry_shadow": True,
            "geometry_does_not_replace_proof": True,
            "truth_issued": False,
        },
    )


def _life_presentations() -> list[str]:
    return [f"{hand}:{phase}" for hand in ("LEFT", "RIGHT") for phase in range(4)]


def _life_steps() -> list[LocalTranslationStepInput]:
    result: list[LocalTranslationStepInput] = []
    for hand in ("LEFT", "RIGHT"):
        inverse = "RIGHT" if hand == "LEFT" else "LEFT"
        for phase in range(4):
            source = f"{hand}:{phase}"
            result.append(
                LocalTranslationStepInput(
                    source=source,
                    target=f"{hand}:{(phase + 1) % 4}",
                    label="ballReturn",
                    witness={"role": "reactor beat"},
                )
            )
            result.append(
                LocalTranslationStepInput(
                    source=source,
                    target=f"{inverse}:{(phase - 1) % 4}",
                    label="hairReturn",
                    witness={"role": "global hair return"},
                )
            )
    return result


def _beat_steps() -> list[LocalTranslationStepInput]:
    result: list[LocalTranslationStepInput] = []
    for hand in ("LEFT", "RIGHT"):
        inverse = "RIGHT" if hand == "LEFT" else "LEFT"
        for phase in range(4):
            result.append(
                LocalTranslationStepInput(
                    source=f"{hand}:{phase}",
                    target=f"{inverse}:{phase}",
                    label="selfLimit beat",
                    witness={"reactor_phase": phase},
                )
            )
    return result


def canonical_qg_evaluation() -> dict[str, Any]:
    presentations = _life_presentations()
    full_data = ProofSystemCreate(
        name="finite Turing being of life / QG reading",
        presentations=presentations,
        steps=_life_steps(),
        metadata={"formal_scope": "finite hand × ball return being"},
    )
    beat_data = ProofSystemCreate(
        name="reactor beat balance",
        presentations=presentations,
        steps=_beat_steps(),
        metadata={"formal_scope": "selfLimit beat only"},
    )
    full = evaluate_proof_system(full_data)
    beat = evaluate_proof_system(beat_data)
    qg_total = all(
        len(full["admits_relation"][item]) == len(presentations)
        for item in presentations
    )
    beat_decide_correct = all(
        (
            beat["balance_class_of"][left] == beat["balance_class_of"][right]
        )
        == (left.split(":", 1)[1] == right.split(":", 1)[1])
        for left in presentations
        for right in presentations
    )
    return {
        "formal_reading": "NRRF811",
        "scope": "finite hand × ball return being; not empirical gravitation",
        "qg_total": qg_total,
        "qg_shortProof": full["max_shortest_proof_length"] <= 5,
        "observed_max_shortest_proof_length": full["max_shortest_proof_length"],
        "theorem_bound": 5,
        "completion_single_point": len(full["balance_classes"]) == 1,
        "completion_object_cardinality": len(full["balance_classes"]),
        "every_admissible_reading_constant": len(full["geometry_classes"]) == 1,
        "beat_balance_iff_reactor": beat_decide_correct,
        "beat_balance_eq_geometry": beat["balance_eq_geometry"],
        "beatDecide_correct": beat_decide_correct,
        "admitted_example": {
            "left": "LEFT:0",
            "right": "RIGHT:0",
            "decision": beat_decide_correct
            and beat["balance_class_of"]["LEFT:0"]
            == beat["balance_class_of"]["RIGHT:0"],
        },
        "non_admitted_example": {
            "left": "LEFT:0",
            "right": "RIGHT:1",
            "decision": beat["balance_class_of"]["LEFT:0"]
            == beat["balance_class_of"]["RIGHT:1"],
        },
        "full_evaluation": full,
        "beat_evaluation": beat,
        "runtime_is_formal_proof": False,
        "truth_issued": False,
    }


class ProofCompletionManager:
    """NRRF811 as proof-bearing depth of completion, balance and Black Mirror."""

    def __init__(
        self,
        runtime: "ClosureSupernetRuntime",
        store: ProofCompletionStore,
    ):
        self.runtime = runtime
        self.store = store

    def capabilities(self) -> dict[str, Any]:
        return {
            "formal_readings": [
                "NRRF799",
                "NRRF802",
                "NRRF805",
                "NRRF807",
                "NRRF811",
            ],
            "canonical_runtime_operation": "integrate",
            "proof_is_finite_derivation_data": True,
            "completion_is_nonempty_proof": True,
            "completion_eq_proof": True,
            "meta_abstraction_forgets_path_not_conclusion": True,
            "truth_admission_is_closure_operator": True,
            "relative_balance_is_mutual_admission": True,
            "completion_object_is_balance_quotient": True,
            "invariant_readings_factor_through_meta_abstraction": True,
            "finite_proof_search_halts": True,
            "rule_is_admission_for_return_steps": True,
            "balance_equals_geometry_only_when_return_closes": True,
            "proof_fibre_reopenable_from_black_mirror": True,
            "canonical_derivation_selected": False,
            "geometry_does_not_replace_proof": True,
            "runtime_is_formal_proof": False,
            "determination_issues_truth": False,
        }

    def _source_context(
        self,
        data: ProofSystemCreate,
    ) -> tuple[list[str], list[str]]:
        source_ids = list(data.source_ids)
        parents: list[str] = []
        if data.source_event_id is not None:
            event = self.runtime.supernet_store.get_event(data.source_event_id)
            source_ids.extend(event["exact_source_ids"])
            parents.append(data.source_event_id)
        if data.continuation_system_id is not None:
            continuation = self.runtime.continuation_store.get_system(
                data.continuation_system_id
            )
            parents.append(continuation["integration_event_id"])
            source_ids.extend(continuation["source_ids"])
        if data.turing_being_life_event_id is not None:
            life = self.runtime.turing_being_store.get_life_event(
                data.turing_being_life_event_id
            )
            if life["translational_truth_receipt"].get("complete") is not True:
                raise ValueError(
                    "a Turing Being proof completion requires completed translational truth"
                )
            parents.append(life["integration_event_id"])
            if life.get("reaction_event_id"):
                parents.append(life["reaction_event_id"])
            source_ids.extend(life["source_ids"])
        return _unique(source_ids), _unique(parents)

    async def create_system(self, data: ProofSystemCreate) -> dict[str, Any]:
        system_id = str(uuid.uuid4())
        source_ids, parents = self._source_context(data)
        source = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=_stable(
                    {
                        "NRRF811": "completion equals proof by meta abstraction",
                        "name": data.name,
                        "presentations": data.presentations,
                        "admitted_steps": [
                            step.model_dump(mode="json") for step in data.steps
                        ],
                        "continuation_system_id": data.continuation_system_id,
                        "turing_being_life_event_id": data.turing_being_life_event_id,
                    }
                ),
                authored_by=data.authored_by,
                form_label="proof completion meta abstraction",
                language_label="NRRF811 proof/admission/balance",
                source_id="proof-completion-supernet",
                perspective_id=data.perspective_id,
                problem_id=data.problem_id,
                capabilities=[
                    "retain finite derivation data",
                    "abstract proof existence into admission",
                    "close admitted seed sets",
                    "form relative balance from reciprocal proof",
                    "reopen completion classes to proof fibres",
                ],
                constraints=[
                    "completion preserves proof existence but not proof identity",
                    "geometry does not replace directed proof",
                    "no canonical derivation is selected",
                    "determination does not issue TRUE",
                ],
                relation_hints=[
                    "NRRF811",
                    "Deriv",
                    "Admits",
                    "Balance",
                    "meta abstraction",
                    "truth admission",
                    "completion equals proof",
                ],
                causal_predecessor_ids=parents,
                parent_event_ids=parents,
                affected_perspectives=[data.authored_by],
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="proof",
                external_key=f"proof-completion:source:{system_id}",
                metadata={
                    **data.metadata,
                    "proof_system_id": system_id,
                    "formal_readings": [
                        "NRRF799",
                        "NRRF802",
                        "NRRF805",
                        "NRRF807",
                        "NRRF811",
                    ],
                    "completion_is_proof_truncation": True,
                    "canonical_derivation_selected": False,
                    "truth_issued": False,
                },
            )
        )

        geometry_completion: dict[str, Any] | None = None
        geometry_id = data.geometry_completion_system_id
        if geometry_id is not None:
            geometry_completion = self.runtime.completion_store.get_system(geometry_id)
        else:
            geometry_completion = await self.runtime.completion.create_system(
                _geometry_input(
                    data,
                    source_event_id=source["event_id"],
                    source_ids=source_ids,
                )
            )
            geometry_id = geometry_completion["id"]

        evaluation = evaluate_proof_system(
            data,
            geometry_completion_system=geometry_completion,
        )
        row = {
            "id": system_id,
            "occurrence_id": source["occurrence_ids"][0],
            "integration_event_id": source["event_id"],
            "name": data.name,
            "authored_by": data.authored_by,
            "presentations": data.presentations,
            "steps": [step.model_dump(mode="json") for step in data.steps],
            "readings": [item.model_dump(mode="json") for item in data.readings],
            "truths": [item.model_dump(mode="json") for item in data.truths],
            "continuation_system_id": data.continuation_system_id,
            "turing_being_life_event_id": data.turing_being_life_event_id,
            "geometry_completion_system_id": geometry_id,
            "source_event_id": data.source_event_id,
            "perspective_id": data.perspective_id,
            "problem_id": data.problem_id,
            "source_ids": source_ids,
            "evaluation": evaluation,
            "metadata": {
                **data.metadata,
                "formal_reading": "NRRF811",
                "geometry_completion_system_id": geometry_id,
                "completion_is_proof_truncation": True,
                "proof_fibres_reopenable": True,
                "canonical_derivation_selected": False,
                "truth_issued": False,
            },
            "created_at": utcnow(),
        }
        stored = self.store.create_system(row)
        self.runtime.supernet_integrator.determine(
            source["event_id"],
            actor_id=data.authored_by,
            rigidity_scope=[
                "finite admitted-step relation",
                "proof existence / completion equivalence",
                "truth-admission closure laws",
                "mutual-proof balance classes",
                "proof-preserving Black Mirror abstraction",
            ],
            rigidity_receipt={
                "completion_eq_proof": evaluation["completion_eq_proof"],
                "meta_abstraction_surjective": evaluation[
                    "meta_abstraction_surjective"
                ],
                "truth_admission_idempotent": evaluation["truth_admission"][
                    "idempotent"
                ],
                "all_admissions_have_short_proof": evaluation[
                    "all_admissions_have_short_proof"
                ],
                "balance_le_geometry": evaluation["balance_le_geometry"],
                "balance_eq_geometry": evaluation["balance_eq_geometry"],
                "geometry_does_not_replace_proof": True,
                "truth_issued": False,
            },
            determined_form={
                "proof_system_id": system_id,
                "admits_relation": evaluation["admits_relation"],
                "balance_classes": evaluation["balance_classes"],
                "geometry_completion_system_id": geometry_id,
                "known_derivations": evaluation["known_shortest_derivations"],
                "canonical_derivation": None,
            },
            unitary_path_partition={
                "path": [
                    "admitted step",
                    "finite derivation",
                    "proposition-level admission",
                    "reciprocal balance",
                    "meta abstraction quotient",
                    "OPEN proof-fibre reopening",
                ],
                "balance_partition": evaluation["balance_class_of"],
                "geometry_partition": evaluation["geometry_class_of"],
            },
            reason=(
                "Completion is the inhabited proposition of finite proof while "
                "the Supernet retains the proof-relevant fibre beneath it"
            ),
        )
        self.runtime.supernet_integrator.transition(
            source["event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason=(
                    "The meta abstraction returns while concrete derivations, "
                    "alternative proof paths and later admissions remain reopenable"
                ),
                actor_id=data.authored_by,
                returned_resource_ids=[system_id, geometry_id],
                successor_potential=[
                    {
                        "kind": "proof-fibre-reopening",
                        "proof_system_id": system_id,
                        "known_derivation_count": evaluation[
                            "known_shortest_derivations"
                        ],
                        "canonical_derivation": None,
                    }
                ],
                metadata={
                    "nrrf811": True,
                    "completion_is_proof_truncation": True,
                    "proof_fibres_reopenable": True,
                    "truth_issued": False,
                },
            ),
        )
        self.projection()
        return self.store.get_system(stored["id"])

    async def create_from_continuation(
        self,
        continuation_system: dict[str, Any],
    ) -> dict[str, Any]:
        existing = self.store.find_by_continuation(continuation_system["id"])
        if existing is not None:
            return existing
        data = ProofSystemCreate(
            name=f"{continuation_system['name']} — proof completion",
            authored_by=continuation_system["authored_by"],
            presentations=continuation_system["presentations"],
            steps=[
                LocalTranslationStepInput(
                    source=item,
                    target=continuation_system["step"][item],
                    label=continuation_system["step_label"],
                    witness={
                        "formal_reading": "NRRF811",
                        "continuation_system_id": continuation_system["id"],
                    },
                )
                for item in continuation_system["presentations"]
            ],
            continuation_system_id=continuation_system["id"],
            turing_being_life_event_id=continuation_system.get(
                "turing_being_life_event_id"
            ),
            geometry_completion_system_id=continuation_system[
                "completion_system_id"
            ],
            source_event_id=continuation_system["integration_event_id"],
            perspective_id=continuation_system.get("perspective_id"),
            problem_id=continuation_system.get("problem_id"),
            source_ids=continuation_system["source_ids"],
            metadata={
                "derived_from_continuation": True,
                "rule_is_admission": True,
                "return_proof_is_counting": True,
            },
        )
        return await self.create_system(data)

    async def create_from_turing_being(
        self,
        life_event_id: str,
        *,
        authored_by: str = "participant",
        source_event_id: str | None = None,
    ) -> dict[str, Any]:
        existing = self.store.find_by_turing_being(life_event_id)
        if existing is not None:
            return existing
        life = self.runtime.turing_being_store.get_life_event(life_event_id)
        if life["translational_truth_receipt"].get("complete") is not True:
            raise ValueError(
                "Turing Being proof completion requires completed translational truth"
            )
        return await self.create_system(
            ProofSystemCreate(
                name=f"{life['name']} — finite Turing being proof completion",
                authored_by=authored_by,
                presentations=_life_presentations(),
                steps=_life_steps(),
                turing_being_life_event_id=life_event_id,
                source_event_id=source_event_id or life["integration_event_id"],
                source_ids=life["source_ids"],
                metadata={
                    "qg_finite_being": True,
                    "physical_gravitation_claimed": False,
                    "formal_scope": "finite hand × ball return being",
                },
            )
        )

    def derivation_witness(
        self,
        system_id: str,
        source: str,
        target: str,
        *,
        path: list[str] | None = None,
    ) -> dict[str, Any]:
        system = self.store.get_system(system_id)
        witness = (
            shortest_derivation(
                system["presentations"], system["steps"], source, target
            )
            if path is None
            else validate_derivation_path(
                system["presentations"],
                system["steps"],
                source,
                target,
                path,
            )
        )
        result = witness.model_dump(mode="json")
        result.update(
            {
                "system_id": system_id,
                "meta_abstraction": witness.completion_proposition,
                "completion_eq_proof": True,
                "canonical_derivation": None,
                "proof_fibre_reopenable": True,
                "truth_issued": False,
            }
        )
        return result

    def admission_witness(self, system_id: str, seeds: list[str]) -> dict[str, Any]:
        system = self.store.get_system(system_id)
        result = admission_witness_from_evaluation(system, seeds).model_dump(
            mode="json"
        )
        result.update(
            {
                "system_id": system_id,
                "closure_operator": True,
                "admit_isLeast": True,
                "admit_gi": True,
                "truth_issued": False,
            }
        )
        return result

    def balance_witness(
        self,
        system_id: str,
        left: str,
        right: str,
    ) -> dict[str, Any]:
        system = self.store.get_system(system_id)
        forward = DerivationWitness.model_validate(
            self.derivation_witness(system_id, left, right)
        )
        reverse = DerivationWitness.model_validate(
            self.derivation_witness(system_id, right, left)
        )
        balanced = forward.admitted and reverse.admitted
        evaluation = system["evaluation"]
        geometry_related = (
            evaluation["geometry_class_of"][left]
            == evaluation["geometry_class_of"][right]
        )
        result = BalanceWitness(
            left=left,
            right=right,
            balanced=balanced,
            forward=forward,
            reverse=reverse,
            balance_class=(
                evaluation["balance_class_of"][left] if balanced else None
            ),
            geometry_related=geometry_related,
            balance_implies_geometry=(not balanced) or geometry_related,
            geometry_implies_balance=(not geometry_related) or balanced,
            closure_equality_under_closed_return=(
                (not evaluation["return_closes"])
                or (geometry_related == balanced)
            ),
        ).model_dump(mode="json")
        result.update(
            {
                "system_id": system_id,
                "meta_abstraction_object": "balance quotient",
                "geometry_does_not_replace_forward_or_reverse_proof": True,
                "truth_issued": False,
            }
        )
        return result

    async def _receipt_event(
        self,
        *,
        system: dict[str, Any],
        kind: ProofReceiptKind,
        authored_by: str,
        source_event_id: str | None,
        payload: dict[str, Any],
        evaluation: dict[str, Any],
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        receipt_id = str(uuid.uuid4())
        parents = [system["integration_event_id"]]
        source_ids = list(system["source_ids"])
        if source_event_id is not None:
            source_event = self.runtime.supernet_store.get_event(source_event_id)
            parents.append(source_event_id)
            source_ids.extend(source_event["exact_source_ids"])
        integrated = await self.runtime.integrate_resource(
            ResourceEnvelope(
                exact_text=_stable(
                    {
                        "NRRF811": kind.value,
                        "proof_system_id": system["id"],
                        "payload": payload,
                        "evaluation": evaluation,
                    }
                ),
                authored_by=authored_by,
                form_label=f"proof completion {kind.value.lower()}",
                language_label="NRRF811 proof fibre",
                source_id="proof-completion-supernet",
                capabilities=[
                    "reopen completion to concrete proof data",
                    "retain directed trace and reciprocal balance separately",
                ],
                constraints=[
                    "one proof witness is not declared canonical",
                    "geometry cannot substitute for proof",
                    "determination does not issue TRUE",
                ],
                relation_hints=["NRRF811", kind.value, "proof fibre"],
                causal_predecessor_ids=_unique(parents),
                parent_event_ids=_unique(parents),
                affected_perspectives=[authored_by],
                evidence_status=EvidenceStatus.FORMALLY_PROVED_UNDER_READING,
                adapter_label="proof",
                external_key=f"proof-completion:receipt:{receipt_id}",
                metadata={
                    **metadata,
                    "proof_receipt_id": receipt_id,
                    "proof_system_id": system["id"],
                    "kind": kind.value,
                    "truth_issued": False,
                },
            )
        )
        row = self.store.create_receipt(
            {
                "id": receipt_id,
                "occurrence_id": integrated["occurrence_ids"][0],
                "integration_event_id": integrated["event_id"],
                "system_id": system["id"],
                "kind": kind.value,
                "authored_by": authored_by,
                "source_event_id": source_event_id,
                "payload": payload,
                "evaluation": evaluation,
                "source_ids": _unique(source_ids),
                "metadata": {
                    **metadata,
                    "canonical_derivation_selected": False,
                    "truth_issued": False,
                },
                "created_at": utcnow(),
            }
        )
        is_determined = (
            (kind == ProofReceiptKind.DERIVATION and evaluation.get("admitted") is True)
            or (kind == ProofReceiptKind.BALANCE and evaluation.get("balanced") is True)
            or kind == ProofReceiptKind.ADMISSION
        )
        if is_determined:
            self.runtime.supernet_integrator.determine(
                integrated["event_id"],
                actor_id=authored_by,
                rigidity_scope=[kind.value, "finite proof witness"],
                rigidity_receipt={
                    "kind": kind.value,
                    "evaluation": evaluation,
                    "canonical_derivation_selected": False,
                    "truth_issued": False,
                },
                determined_form={
                    "proof_receipt_id": receipt_id,
                    "proof_system_id": system["id"],
                    "evaluation": evaluation,
                    "canonical_derivation": None,
                },
                unitary_path_partition={
                    "kind": kind.value,
                    "trace": evaluation.get("trace")
                    or evaluation.get("forward", {}).get("trace")
                    or evaluation.get("admitted_set", []),
                },
                reason="The finite proof receipt is checked under the submitted admission relation",
            )
        self.runtime.supernet_integrator.transition(
            integrated["event_id"],
            IntegrationStateCreate(
                stage=IntegrationStage.RETURNED,
                verdict=Verdict.OPEN,
                reason="The proof receipt returns while its abstraction and alternative proof fibre remain open",
                actor_id=authored_by,
                returned_resource_ids=[receipt_id],
                successor_potential=[
                    {
                        "kind": "proof-fibre-continuation",
                        "proof_system_id": system["id"],
                        "receipt_id": receipt_id,
                    }
                ],
                metadata={"nrrf811": True, "truth_issued": False},
            ),
        )
        self.projection()
        return row

    async def create_derivation(
        self,
        system_id: str,
        data: DerivationCreate,
    ) -> dict[str, Any]:
        system = self.store.get_system(system_id)
        evaluation = self.derivation_witness(
            system_id,
            data.source,
            data.target,
            path=data.path,
        )
        return await self._receipt_event(
            system=system,
            kind=ProofReceiptKind.DERIVATION,
            authored_by=data.authored_by,
            source_event_id=data.source_event_id,
            payload=data.model_dump(mode="json"),
            evaluation=evaluation,
            metadata=data.metadata,
        )

    async def create_admission(
        self,
        system_id: str,
        data: AdmissionCreate,
    ) -> dict[str, Any]:
        system = self.store.get_system(system_id)
        evaluation = self.admission_witness(system_id, data.seeds)
        return await self._receipt_event(
            system=system,
            kind=ProofReceiptKind.ADMISSION,
            authored_by=data.authored_by,
            source_event_id=data.source_event_id,
            payload=data.model_dump(mode="json"),
            evaluation=evaluation,
            metadata=data.metadata,
        )

    async def create_balance(
        self,
        system_id: str,
        data: BalanceCreate,
    ) -> dict[str, Any]:
        system = self.store.get_system(system_id)
        evaluation = self.balance_witness(system_id, data.left, data.right)
        return await self._receipt_event(
            system=system,
            kind=ProofReceiptKind.BALANCE,
            authored_by=data.authored_by,
            source_event_id=data.source_event_id,
            payload=data.model_dump(mode="json"),
            evaluation=evaluation,
            metadata=data.metadata,
        )

    def projection(self) -> dict[str, Any]:
        systems = self.store.list_systems(limit=20_000)
        receipts = self.store.list_receipts(limit=20_000)
        projection = {
            "generated_at": utcnow(),
            "systems": systems,
            "receipts": receipts,
            "stats": self.store.stats(),
            "canonical_qg": canonical_qg_evaluation(),
            "source_reverse_index": {
                **{
                    f"proof-system:{item['id']}": list(item["source_ids"])
                    for item in systems
                },
                **{
                    f"proof-receipt:{item['id']}": list(item["source_ids"])
                    for item in receipts
                },
            },
            "formal_readings": [
                "NRRF799",
                "NRRF802",
                "NRRF805",
                "NRRF807",
                "NRRF811",
            ],
            "canonical_runtime_operation": "integrate",
            "completion_is_proof_truncation": True,
            "proof_fibres_remain_reopenable": True,
            "balance_is_mutual_admission": True,
            "geometry_does_not_replace_proof": True,
            "canonical_derivation_selected": False,
            "truth_issued": False,
        }
        self.store.set_state("proof_completion_field_projection", projection)
        return projection
