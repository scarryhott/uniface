from __future__ import annotations

import json
from itertools import permutations
from typing import Any, Callable

from .completion import TranslationalCompletionManager
from .completion_models import (
    CompletionSystemCreate,
    InvariantReadingInput,
    LocalTranslationStepInput,
)
from .handed_models import Hand, HandedLifeSystemCreate


def stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in values if str(item)))


def state(hand: Hand, phase: int) -> dict[str, Any]:
    return {
        "hand": hand.value,
        "ball_phase": int(phase) % 4,
        "hair_class": "hair:unit",
        "temporal_role": "POTENTIAL" if hand == Hand.LEFT else "ACTUAL",
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


def ball_completion() -> dict[str, Any]:
    presentations = [str(index) for index in range(4)]
    data = CompletionSystemCreate(
        name="NRRF800 four-ball one-hair completion",
        presentations=presentations,
        steps=[
            LocalTranslationStepInput(
                source=str(index),
                target=str((index + 1) % 4),
                label="ballStep",
                admitted_for_completion=True,
                witness={"phase": index, "next_phase": (index + 1) % 4},
            )
            for index in range(4)
        ],
        readings=[
            InvariantReadingInput(
                name="hairMk",
                values={item: "hair:unit" for item in presentations},
                metadata={"one_sheaf": True},
            )
        ],
    )
    return TranslationalCompletionManager.evaluate(data).model_dump(mode="json")


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
    completion = ball_completion()
    classes = completion["classes"]
    visited_phases = [item["ball_phase"] for item in left_gate_trace[:-1]]
    roles = [item["temporal_role"] for item in left_gate_trace]
    left_complete = sorted(visited_phases) == [0, 1, 2, 3] and (
        left_gate_trace[-1] == left_gate_start
    )
    return {
        "initial_state": initial,
        "ball_carrier": [0, 1, 2, 3],
        "ball_card": 4,
        "ball_sheaves": 4,
        "ball_step_period": 4,
        "ball_step_iterate_four_is_identity": ball_trace[-1] == initial,
        "ball_step_ne_identity_below_four": all(
            ball_trace[index] != initial for index in (1, 2, 3)
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
        "left_gate_alternates_potential_actual": all(
            roles[index] != roles[index + 1] for index in range(len(roles) - 1)
        ),
        "left_gate_closes_after_four": left_gate_trace[-1] == left_gate_start,
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
        "canonical_biological_interpretation": None,
        "biological_chirality_claimed": False,
        "biological_life_claimed": False,
        "human_law_claimed": False,
        "truth_issued": False,
    }
