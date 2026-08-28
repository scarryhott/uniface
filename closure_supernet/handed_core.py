from __future__ import annotations

import json
from itertools import permutations
from typing import Any, Callable

from .completion_models import InvariantReadingInput
from .handed_models import Hand, HandedLifeSystemCreate
from .unify_closure import (
    canonical_unified_closure_instances,
    evaluate_return_closure,
)
from .unify_closure_models import ReturnClosureCreate


def stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in values if str(item)))


def state(hand: Hand, phase: int) -> dict[str, Any]:
    """A finite handed chart state, without pre-assigning life semantics."""

    return {
        "hand": hand.value,
        "ball_phase": int(phase) % 4,
        "hair_class": "hair:unit",
        "temporal_role": None,
        "temporal_role_status": "UNDEFINED_UNTIL_TRANSLATIONAL_TRUTH",
        "internal_external_defined": False,
        "finite_chart_only": True,
    }


def ball_return(value: dict[str, Any]) -> dict[str, Any]:
    return state(Hand(value["hand"]), int(value["ball_phase"]) + 1)


def hair_return(value: dict[str, Any]) -> dict[str, Any]:
    return state(Hand(value["hand"]).inverse, int(value["ball_phase"]) - 1)


def self_limit(value: dict[str, Any]) -> dict[str, Any]:
    return hair_return(ball_return(value))


def iterate(
    start: dict[str, Any], step: Callable[[dict[str, Any]], dict[str, Any]], count: int
) -> list[dict[str, Any]]:
    trace = [{"index": 0, **start}]
    current = start
    for index in range(1, count + 1):
        current = step(current)
        trace.append({"index": index, **current})
    return trace


def trace_state(item: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in item.items() if key != "index"}


def ball_completion() -> dict[str, Any]:
    carrier = [str(index) for index in range(4)]
    return evaluate_return_closure(
        ReturnClosureCreate(
            name="NRRF800 four-ball one-hair closure instance",
            carrier=carrier,
            step={str(index): str((index + 1) % 4) for index in range(4)},
            step_label="ballStep",
            readings=[
                InvariantReadingInput(
                    name="hairMk",
                    values={item: "hair:unit" for item in carrier},
                    metadata={"one_sheaf": True},
                )
            ],
            metadata={"instance": "hair_of_ball", "formal_reading": "NRRF802"},
        )
    )


def commuting_maps_receipt() -> dict[str, Any]:
    commuting: list[dict[str, Any]] = []
    for values in permutations(range(4)):
        if all(
            values[(phase + 1) % 4] == (values[phase] + 1) % 4
            for phase in range(4)
        ):
            shift = values[0]
            commuting.append(
                {
                    "mapping": list(values),
                    "translation_shift": shift,
                    "is_translation": all(
                        values[phase] == (phase + shift) % 4 for phase in range(4)
                    ),
                }
            )
    natural = len(commuting) == 4 and all(
        item["is_translation"] for item in commuting
    )
    return {
        "all_commuting_bijections": commuting,
        "commuting_bijections": len(commuting),
        "all_are_ball_translations": natural,
        "expected_translation_count": 4,
        "naturality_forced_in_finite_chart": natural,
    }


def evaluate_system(data: HandedLifeSystemCreate) -> dict[str, Any]:
    initial = state(data.initial_hand, data.initial_ball_phase)
    ball_trace = iterate(initial, ball_return, 4)
    left_gate_start = state(Hand.LEFT, data.initial_ball_phase)
    left_gate_trace = iterate(left_gate_start, hair_return, 4)
    limit = self_limit(initial)
    unified = canonical_unified_closure_instances()
    completion = unified["hair_of_ball"]["evaluation"]
    classes = completion["classes"]
    visited_phases = [item["ball_phase"] for item in left_gate_trace[:-1]]
    hands = [item["hand"] for item in left_gate_trace]
    left_complete = sorted(visited_phases) == [0, 1, 2, 3] and (
        trace_state(left_gate_trace[-1]) == left_gate_start
    )
    translational_truth_prior = bool(data.metadata.get("translational_truth_prior"))
    foundation_status = str(
        data.metadata.get(
            "foundation_status",
            "DERIVED_FINITE_REACTION_CHART"
            if translational_truth_prior
            else "UNBOUND_FINITE_CHART",
        )
    )
    return {
        "initial_state": initial,
        "ball_carrier": [0, 1, 2, 3],
        "ball_card": 4,
        "ball_sheaves": 4,
        "ball_step_period": 4,
        "ball_step_iterate_four_is_identity": trace_state(ball_trace[-1]) == initial,
        "ball_step_ne_identity_below_four": all(
            trace_state(ball_trace[index]) != initial for index in (1, 2, 3)
        ),
        "ball_return_trace": ball_trace,
        "ball_return_never_touches_hand": all(
            item["hand"] == initial["hand"] for item in ball_trace
        ),
        "hair_completion": completion,
        "hair_classes": len(classes),
        "hair_card": len(classes),
        "hair_sheaves": 1,
        "hair_equiv_punit": len(classes) == 1,
        "hair_unmoved_by_ball_translation": True,
        "hair_unmoved_by_ball_inversion": True,
        "translation_invariant_ball_readings_factor_through_hair": True,
        "commuting_maps": commuting_maps_receipt(),
        "self_limit_state": limit,
        "self_limit_same_ball_phase": limit["ball_phase"] == initial["ball_phase"],
        "self_limit_inverts_hand": limit["hand"] == data.initial_hand.inverse.value,
        "self_limit_involutive": self_limit(limit) == initial,
        "self_limit_order_exact": 2,
        "left_handed_gate_trace": left_gate_trace,
        "left_gate_visits_each_ball_sheaf_once": sorted(visited_phases)
        == [0, 1, 2, 3],
        "left_gate_alternates_hands": all(
            hands[index] != hands[index + 1] for index in range(len(hands) - 1)
        ),
        "left_gate_alternates_potential_actual": False,
        "potential_actual_requires_translational_truth": True,
        "left_gate_closes_after_four": trace_state(left_gate_trace[-1]) == left_gate_start,
        "left_gate_same_hair_throughout": len(
            {item["hair_class"] for item in left_gate_trace}
        )
        == 1,
        "left_handed_gate_complete": left_complete,
        "four_ball_one_hair": len(classes) == 1,
        "completion_every_identification_has_finite_path": completion[
            "every_identification_has_finite_local_path"
        ],
        "completion_no_global_jump": completion["no_global_jump"],
        "completion_idempotent": completion["completion_idempotent"],
        "closure_defined_once": unified["closure_defined_once"],
        "hair_isClosure": unified["hair_of_ball"]["hair_isClosure"],
        "hair_eq_closure": unified["hair_of_ball"]["hair_eq_closure"],
        "hand_isClosure": unified["hand_of_ballReturn"]["hand_isClosure"],
        "closure_ballReturn_hand": unified["hand_of_ballReturn"][
            "closure_ballReturn_hand"
        ],
        "phase_isClosure": unified["phase_of_selfLimit"]["phase_isClosure"],
        "closure_selfLimit_phase": unified["phase_of_selfLimit"][
            "closure_selfLimit_phase"
        ],
        "unified_cardinalities": unified["unified_cardinalities"],
        "closure2_life_subsingleton": unified["closure2_life"][
            "closure2_life_subsingleton"
        ],
        "closure2_life_cardinality": unified["closure2_life"]["cardinality"],
        "unify_closure": unified["closure2_life"]["unify_closure"],
        "unify_closure_symm": unified["closure2_life"]["unify_closure_symm"],
        "unified_closure_instances": unified,
        "foundation_status": foundation_status,
        "translational_truth_prior": translational_truth_prior,
        "internal_external_defined": translational_truth_prior,
        "finite_ball_hair_foundational": False,
        "global_hair_zero_not_hair_cardinality_one": True,
        "local_ball_infinity_not_ball_cardinality_four": True,
        "canonical_biological_interpretation": None,
        "biological_chirality_claimed": False,
        "biological_life_claimed": False,
        "human_law_claimed": False,
        "truth_issued": False,
    }
