from __future__ import annotations

from itertools import combinations
from typing import Any, Awaitable, Callable, Iterable

from .config import RuntimeConfig
from .living_store import LivingNetworkStore
from .models import OccurrenceCreate, RelationType
from .reopening_models import (
    ClosureRuleSpec,
    MoralConnectionCreate,
    OrderEffect,
    OrderedReadingCreate,
    ReopeningFamilyCreate,
    ReopeningMode,
    ReopeningProcessCreate,
    ReopeningProcessState,
    ReopeningProjection,
    ReopeningVariantSpec,
    ResidueRoundState,
)
from .reopening_store import ReopeningStore, utcnow
from .store import EventStore


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


class IteratedReopeningManager:
    """Executable NRRF768 reading for the living public field.

    Families and closure rules are explicit authored data. The runtime computes
    a finite Horn-closure chart over exact occurrence identifiers; it does not
    infer a universal semantic closure and never labels finite stabilization as
    a final moral core.
    """

    agent_name = "iterated-reopening-agent"

    def __init__(
        self,
        config: RuntimeConfig,
        event_store: EventStore,
        living_store: LivingNetworkStore,
        reopening_store: ReopeningStore,
        ingest: Callable[[OccurrenceCreate], Awaitable[dict[str, Any]]],
    ):
        self.config = config
        self.event_store = event_store
        self.living_store = living_store
        self.store = reopening_store
        self.ingest = ingest

    def capabilities(self) -> dict[str, Any]:
        return {
            "protocol": "closure.supernet/reopening-v1",
            "formal_reading": "NRRF768IteratedReopeningAdmissibleFamiliesDependencyOrder",
            "forms": [
                "admissible_reopening_family",
                "explicit_closure_rule",
                "remaining_star_residue",
                "ordered_dependency_reading",
                "content_preserving_permutation",
                "meaning_changing_reorder",
                "iterated_residue_round",
                "residue_relative_moral_connection",
            ],
            "remaining_star": "intersection of explicit finite closure readings across a nonempty reopening family",
            "final_core_state_available": False,
            "finite_stability_label": str(
                ReopeningProcessState.STABLE_AT_CURRENT_FINITE_SCOPE
            ),
            "plurality_outside_residue_preserved": True,
            "automatic_global_truth": False,
            "turing_complete_assumed": False,
        }

    @staticmethod
    def _rule_dicts(
        rules: list[ClosureRuleSpec] | list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        result = []
        for rule in rules:
            result.append(
                rule.model_dump(mode="json")
                if isinstance(rule, ClosureRuleSpec)
                else dict(rule)
            )
        return result

    def closure(
        self,
        seed: Iterable[str],
        rules: list[ClosureRuleSpec] | list[dict[str, Any]],
    ) -> list[str]:
        """Least finite closure under explicit participant-supplied implications."""
        result = set(seed)
        rule_dicts = self._rule_dicts(rules)
        universe = set(result)
        for rule in rule_dicts:
            universe.update(rule.get("premise_occurrence_ids") or [])
            universe.add(str(rule["conclusion_occurrence_id"]))
        for _ in range(len(universe) + 1):
            changed = False
            for rule in rule_dicts:
                premises = set(rule.get("premise_occurrence_ids") or [])
                conclusion = str(rule["conclusion_occurrence_id"])
                if premises.issubset(result) and conclusion not in result:
                    result.add(conclusion)
                    changed = True
            if not changed:
                break
        return sorted(result)

    def _validate_occurrences(self, occurrence_ids: Iterable[str]) -> None:
        for occurrence_id in _unique(occurrence_ids):
            self.event_store.get_occurrence(occurrence_id)

    def _validate_rules(
        self, rules: list[ClosureRuleSpec] | list[dict[str, Any]]
    ) -> None:
        all_ids: list[str] = []
        for rule in self._rule_dicts(rules):
            all_ids.extend(rule.get("premise_occurrence_ids") or [])
            all_ids.append(str(rule["conclusion_occurrence_id"]))
        self._validate_occurrences(all_ids)

    def _variant_specs(
        self, data: ReopeningFamilyCreate
    ) -> list[ReopeningVariantSpec]:
        assumptions = list(data.assumption_occurrence_ids)
        if data.mode == ReopeningMode.TRIVIAL:
            return [
                ReopeningVariantSpec(
                    label="retain all assumptions", held_occurrence_ids=assumptions
                )
            ]
        if data.mode == ReopeningMode.SINGLE_REMOVAL:
            return [
                ReopeningVariantSpec(
                    label=f"remove {occurrence_id}",
                    held_occurrence_ids=[
                        item for item in assumptions if item != occurrence_id
                    ],
                    metadata={"suspended": [occurrence_id]},
                )
                for occurrence_id in assumptions
            ]
        if data.mode == ReopeningMode.JOINT_SUSPENSION:
            variants = []
            for index, suspended in enumerate(data.joint_suspensions):
                unknown = set(suspended) - set(assumptions)
                if unknown:
                    raise ValueError(
                        "Joint suspension references assumptions outside this family: "
                        + ", ".join(sorted(unknown))
                    )
                suspended_set = set(suspended)
                variants.append(
                    ReopeningVariantSpec(
                        label=f"joint suspension {index + 1}",
                        held_occurrence_ids=[
                            item for item in assumptions if item not in suspended_set
                        ],
                        metadata={"suspended": list(suspended)},
                    )
                )
            return variants
        if data.mode == ReopeningMode.POWERSET:
            if len(assumptions) > self.config.reopening_powerset_limit:
                raise ValueError(
                    f"POWERSET family is limited to {self.config.reopening_powerset_limit} assumptions"
                )
            subsets = [
                subset
                for size in range(len(assumptions) + 1)
                for subset in combinations(assumptions, size)
            ]
            return [
                ReopeningVariantSpec(
                    label=f"subset {index + 1}",
                    held_occurrence_ids=list(subset),
                )
                for index, subset in enumerate(subsets)
            ]
        return list(data.custom_variants)

    def create_family(self, data: ReopeningFamilyCreate) -> dict[str, Any]:
        self.living_store.get_problem(data.problem_id)
        self.living_store.get_participant(data.created_by)
        self._validate_occurrences(data.assumption_occurrence_ids)
        self._validate_rules(data.closure_rules)
        specs = self._variant_specs(data)
        if not specs:
            raise ValueError("A reopening family must remain nonempty")

        variants: list[dict[str, Any]] = []
        closure_sets: list[set[str]] = []
        for spec in specs:
            self._validate_occurrences(spec.held_occurrence_ids)
            closure_ids = self.closure(spec.held_occurrence_ids, data.closure_rules)
            closure_sets.append(set(closure_ids))
            variants.append(
                {
                    "label": spec.label,
                    "held_occurrence_ids": list(spec.held_occurrence_ids),
                    "closure_occurrence_ids": closure_ids,
                    "metadata": spec.metadata,
                }
            )

        remaining_star_ids = sorted(set.intersection(*closure_sets))
        closure_verified = (
            self.closure(remaining_star_ids, data.closure_rules)
            == remaining_star_ids
        )
        family = self.store.create_family(
            data,
            variants=variants,
            remaining_star_ids=remaining_star_ids,
            closure_verified=closure_verified,
        )
        self.event_store.append_event(
            "REOPENING_FAMILY_CREATED",
            "reopening_family",
            family["id"],
            {
                "problem_id": data.problem_id,
                "mode": str(data.mode),
                "variant_count": len(variants),
                "remaining_star_ids": remaining_star_ids,
                "remaining_star_closed": closure_verified,
            },
        )
        return family

    async def create_ordered_reading(
        self, data: OrderedReadingCreate
    ) -> dict[str, Any]:
        self.living_store.get_problem(data.problem_id)
        self.living_store.get_participant(data.participant_id)
        self._validate_occurrences(data.held_occurrence_ids)
        previous = self.store.list_ordered_readings(
            problem_id=data.problem_id, limit=100_000
        )
        occurrence = await self.ingest(
            OccurrenceCreate(
                exact_text=data.exact_text,
                source_id=f"living-participant:{data.participant_id}",
                source_context="Dependency-sensitive ordered cultural reading",
                metadata={
                    **data.metadata,
                    "living_form": "ORDERED_READING",
                    "problem_id": data.problem_id,
                    "participant_id": data.participant_id,
                    "held_occurrence_ids": data.held_occurrence_ids,
                    "dependency_edges": data.dependency_edges,
                    "meaning_key": data.meaning_key,
                    "order_is_not_assumed_semantically_free": True,
                },
            )
        )
        reading = self.store.create_ordered_reading(data, occurrence["id"])
        assessments = 0
        for other in previous:
            assessment, created = self._assess_pair(other, reading)
            assessments += int(created)
            if assessment["effect"] in {
                str(OrderEffect.CONTENT_PRESERVING),
                str(OrderEffect.MEANING_CHANGING),
            }:
                relation_type = (
                    RelationType.FRAME_TRANSLATION
                    if assessment["effect"]
                    == str(OrderEffect.CONTENT_PRESERVING)
                    else RelationType.OPEN_RELATION
                )
                self.event_store.create_candidate_relation(
                    other["occurrence_id"],
                    reading["occurrence_id"],
                    str(relation_type),
                    0.88
                    if relation_type == RelationType.FRAME_TRANSLATION
                    else 0.82,
                    assessment["rationale"],
                    proposed_by=self.agent_name,
                )
                if relation_type == RelationType.OPEN_RELATION:
                    self.event_store.create_open_seam(
                        other["occurrence_id"],
                        reading["occurrence_id"],
                        "The same assumptions acquire a meaning-changing dependency order",
                        metadata={"order_assessment_id": assessment["id"]},
                    )
        self.event_store.append_event(
            "ORDERED_READING_CREATED",
            "ordered_reading",
            reading["id"],
            {
                "problem_id": data.problem_id,
                "participant_id": data.participant_id,
                "occurrence_id": occurrence["id"],
                "assessments_created": assessments,
            },
        )
        return reading

    def _assess_pair(
        self, left: dict[str, Any], right: dict[str, Any]
    ) -> tuple[dict[str, Any], bool]:
        left_ids = list(left["held_occurrence_ids"])
        right_ids = list(right["held_occurrence_ids"])
        same_content = (
            set(left_ids) == set(right_ids) and len(left_ids) == len(right_ids)
        )
        order_changed = same_content and left_ids != right_ids
        if not same_content:
            effect = OrderEffect.NOT_COMPARABLE
            rationale = "The readings do not hold the same assumption content"
        elif not order_changed and left["meaning_key"] == right["meaning_key"]:
            effect = OrderEffect.SAME_READING
            rationale = "Content, order and declared meaning are the same"
        elif not order_changed:
            effect = OrderEffect.NOT_COMPARABLE
            rationale = (
                "Meaning differs without a dependency reorder, so the reorder "
                "dichotomy does not apply"
            )
        elif left["meaning_key"] == right["meaning_key"]:
            effect = OrderEffect.CONTENT_PRESERVING
            rationale = (
                "The same assumptions were permuted while the declared cultural "
                "reading was preserved"
            )
        else:
            effect = OrderEffect.MEANING_CHANGING
            rationale = (
                "The same assumptions were reordered and the declared cultural "
                "reading changed"
            )
        return self.store.create_order_assessment(
            left["id"],
            right["id"],
            same_content=same_content,
            order_changed=order_changed,
            effect=effect,
            rationale=rationale,
        )

    def create_process(self, data: ReopeningProcessCreate) -> dict[str, Any]:
        self.living_store.get_problem(data.problem_id)
        self.living_store.get_participant(data.created_by)
        if data.previous_process_id:
            self.store.get_process(data.previous_process_id)
        self._validate_occurrences(data.initial_assumption_ids)
        self._validate_rules(data.closure_rules)
        initial_closed_ids = self.closure(
            data.initial_assumption_ids, data.closure_rules
        )
        process = self.store.create_process(
            data, initial_closed_ids=initial_closed_ids
        )
        self.event_store.append_event(
            "REOPENING_PROCESS_CREATED",
            "reopening_process",
            process["id"],
            {
                "problem_id": data.problem_id,
                "mode": str(data.mode),
                "initial_closed_ids": initial_closed_ids,
                "max_rounds": data.max_rounds,
                "final_core_state_available": False,
            },
        )
        return process

    def advance_process(self, process_id: str) -> dict[str, Any] | None:
        process = self.store.get_process(process_id)
        if process["state"] != str(ReopeningProcessState.ACTIVE):
            return None
        latest = self.store.latest_round(process_id)
        round_index = 0 if latest is None else int(latest["round_index"]) + 1
        if round_index >= int(process["max_rounds"]):
            self.store.set_process_state(
                process_id, ReopeningProcessState.MAX_ROUNDS_REACHED
            )
            return None
        if latest is None:
            input_ids = list(
                process["metadata"].get("initial_closed_ids")
                or process["initial_assumption_ids"]
            )
            previous_round_id = None
        else:
            input_ids = list(latest["remaining_star_ids"])
            previous_round_id = latest["id"]
        if not input_ids:
            self.store.set_process_state(
                process_id,
                ReopeningProcessState.STABLE_AT_CURRENT_FINITE_SCOPE,
            )
            return None

        mode = ReopeningMode(process["mode"])
        input_set = set(input_ids)
        suspensions = [
            [item for item in suspension if item in input_set]
            for suspension in process["joint_suspensions"]
        ]
        if mode == ReopeningMode.JOINT_SUSPENSION:
            suspensions = [
                list(item)
                for item in dict.fromkeys(tuple(item) for item in suspensions)
            ]
            if not suspensions:
                suspensions = [[]]
        family = self.create_family(
            ReopeningFamilyCreate(
                problem_id=process["problem_id"],
                name=f"{process['name']} · round {round_index}",
                created_by=process["created_by"],
                assumption_occurrence_ids=input_ids,
                mode=mode,
                joint_suspensions=suspensions,
                closure_rules=process["closure_rules"],
                metadata={
                    "generated_by_process": process_id,
                    "round_index": round_index,
                    "previous_round_id": previous_round_id,
                },
            )
        )
        residue = list(family["remaining_star_ids"])
        strictly_reopened = set(residue) < set(input_ids)
        if not residue:
            round_state = ResidueRoundState.EMPTY_RESIDUE
            process_state = (
                ReopeningProcessState.STABLE_AT_CURRENT_FINITE_SCOPE
            )
        elif residue == input_ids:
            round_state = ResidueRoundState.STABLE_AT_CURRENT_FINITE_SCOPE
            process_state = (
                ReopeningProcessState.STABLE_AT_CURRENT_FINITE_SCOPE
            )
        else:
            round_state = ResidueRoundState.STRICTLY_REOPENED
            process_state = (
                ReopeningProcessState.MAX_ROUNDS_REACHED
                if round_index + 1 >= int(process["max_rounds"])
                else ReopeningProcessState.ACTIVE
            )
        residue_round = self.store.create_round(
            process_id=process_id,
            round_index=round_index,
            input_assumption_ids=input_ids,
            family_id=family["id"],
            remaining_star_ids=residue,
            closed=bool(family["closure_verified"]),
            strictly_reopened=strictly_reopened,
            state=round_state,
            previous_round_id=previous_round_id,
        )
        self.store.set_process_state(process_id, process_state)
        self.event_store.append_event(
            "REOPENING_ROUND_COMPLETED",
            "residue_round",
            residue_round["id"],
            {
                "process_id": process_id,
                "round_index": round_index,
                "input_assumption_ids": input_ids,
                "remaining_star_ids": residue,
                "remaining_star_closed": residue_round["closed"],
                "strictly_reopened": strictly_reopened,
                "process_state": str(process_state),
            },
        )
        return residue_round

    def advance_active_processes(self, limit: int | None = None) -> int:
        limit = limit or self.config.reopening_processes_per_cycle
        advanced = 0
        for process in self.store.list_processes(
            active_only=True, limit=limit
        ):
            advanced += int(self.advance_process(process["id"]) is not None)
        return advanced

    def create_moral_connection(
        self, data: MoralConnectionCreate
    ) -> dict[str, Any]:
        residue_round = self.store.get_round(data.round_id)
        self.living_store.get_participant(data.participant_a_id)
        self.living_store.get_participant(data.participant_b_id)
        self._validate_occurrences(data.understanding_a_ids)
        self._validate_occurrences(data.understanding_b_ids)
        residue = set(residue_round["remaining_star_ids"])
        understanding_a = set(data.understanding_a_ids)
        understanding_b = set(data.understanding_b_ids)
        agrees = residue.issubset(understanding_a) and residue.issubset(
            understanding_b
        )
        connection = self.store.create_moral_connection(
            data,
            residue_ids=sorted(residue),
            agrees_on_residue=agrees,
            plurality_a_ids=sorted(understanding_a - residue),
            plurality_b_ids=sorted(understanding_b - residue),
        )
        self.event_store.append_event(
            "RESIDUE_MORAL_CONNECTION_RECORDED",
            "moral_connection",
            connection["id"],
            {
                "round_id": data.round_id,
                "agrees_on_residue": agrees,
                "full_understandings_equal": understanding_a == understanding_b,
                "plurality_outside_residue_preserved": True,
            },
        )
        return connection

    def projection(self) -> dict[str, Any]:
        families = self.store.list_families(limit=100_000)
        readings = self.store.list_ordered_readings(limit=100_000)
        assessments = self.store.list_order_assessments(limit=100_000)
        processes = self.store.list_processes(limit=100_000)
        rounds = self.store.list_rounds(limit=100_000)
        connections = self.store.list_moral_connections(limit=100_000)
        source_reverse_index: dict[str, list[str]] = {}
        for family in families:
            source_reverse_index[f"family:{family['id']}"] = sorted(
                set(family["assumption_occurrence_ids"])
                | set(family["remaining_star_ids"])
                | {
                    item
                    for variant in family["variants"]
                    for item in variant["held_occurrence_ids"]
                }
            )
        for reading in readings:
            source_reverse_index[f"reading:{reading['id']}"] = [
                reading["occurrence_id"],
                *reading["held_occurrence_ids"],
            ]
        for residue_round in rounds:
            source_reverse_index[f"round:{residue_round['id']}"] = sorted(
                set(residue_round["input_assumption_ids"])
                | set(residue_round["remaining_star_ids"])
            )
        stats = {
            **self.store.stats(),
            "meaning_changing_reorders": sum(
                1
                for item in assessments
                if item["effect"] == str(OrderEffect.MEANING_CHANGING)
            ),
            "content_preserving_permutations": sum(
                1
                for item in assessments
                if item["effect"] == str(OrderEffect.CONTENT_PRESERVING)
            ),
            "connections_on_residue": sum(
                1 for item in connections if item["agrees_on_residue"]
            ),
            "final_core_state_available": False,
            "finite_scope_stability_only": True,
            "nonterminal": True,
        }
        projection = ReopeningProjection(
            generated_at=utcnow(),
            families=families,
            ordered_readings=readings,
            order_assessments=assessments,
            processes=processes,
            rounds=rounds,
            moral_connections=connections,
            stats=stats,
            source_reverse_index=source_reverse_index,
        ).model_dump(mode="json")
        self.store.set_state("iterated_reopening_projection", projection)
        return projection
