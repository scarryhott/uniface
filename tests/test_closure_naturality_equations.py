from __future__ import annotations

from copy import deepcopy

from closure_supernet.closure_naturality_equations import (
    FORMAL_MODULE,
    PROTOCOL,
    derive_closure_naturality_equations,
)


def finite_contract(*, one_fibre: bool = False) -> dict[str, object]:
    fibres = (
        [{"id": "f:0", "member_state_ids": ["s:0", "s:1"]}]
        if one_fibre
        else [
            {"id": "f:0", "member_state_ids": ["s:0"]},
            {"id": "f:1", "member_state_ids": ["s:1"]},
        ]
    )
    reading_a = {"s:0": "a:0", "s:1": "a:0" if one_fibre else "a:1"}
    reading_b = {"s:0": "b:0", "s:1": "b:0" if one_fibre else "b:1"}
    mapping = {"a:0": "b:0"}
    if not one_fibre:
        mapping["a:1"] = "b:1"
    return {
        "status": "WITNESSED",
        "perspective_id": "p:a",
        "interactive_translation_id": "interactive-translation:test",
        "continuation_lineage_ids": ["e:0", "e:1"],
        "projection": {
            "reading": reading_a,
            "states": [
                {"id": "s:0", "event_id": "e:0"},
                {"id": "s:1", "event_id": "e:1"},
            ],
            "equality_fibres": fibres,
        },
        "perspective_closure": {
            "readings": {"p:a": reading_a, "p:b": reading_b},
            "translations": [
                {
                    "id": "hair:a-b",
                    "source_perspective_id": "p:a",
                    "target_perspective_id": "p:b",
                    "display_translation": mapping,
                }
            ],
        },
    }


def test_finite_equations_derive_translation_naturality_and_strict_growth() -> None:
    equations = derive_closure_naturality_equations(finite_contract())

    assert equations["protocol"] == PROTOCOL
    assert equations["formal_module"] == FORMAL_MODULE
    assert equations["interactive_translation_id"] == (
        "interactive-translation:test"
    )
    assert all(equations["checks"].values())
    stages = equations["finite_instance"]["pull_growth_stages"]
    assert [stage["distinction_count"] for stage in stages] == [0, 1]
    assert [stage["strictly_grows"] for stage in stages] == [False, True]
    assert all(stage["naturality_square_commutes"] for stage in stages)
    assert stages[-1]["at_full_reach"] is True


def test_growth_need_not_be_strict_when_the_arena_adds_no_distinction() -> None:
    equations = derive_closure_naturality_equations(
        finite_contract(one_fibre=True)
    )

    assert equations["checks"]["finite_runtime_instance_checked"] is True
    assert equations["checks"]["strict_growth_witnessed"] is False
    assert [
        stage["distinction_count"]
        for stage in equations["finite_instance"]["pull_growth_stages"]
    ] == [0, 0]


def test_forged_hair_or_disconnected_family_fails_equation_derivation() -> None:
    forged = finite_contract()
    forged["perspective_closure"]["translations"][0][
        "display_translation"
    ]["a:0"] = "b:1"
    equations = derive_closure_naturality_equations(forged)
    assert equations["checks"]["all_translation_equations_hold"] is False
    assert equations["checks"]["translation_family_connected"] is False
    assert equations["checks"]["finite_runtime_instance_checked"] is False

    disconnected = deepcopy(finite_contract())
    disconnected["perspective_closure"]["translations"] = []
    equations = derive_closure_naturality_equations(disconnected)
    assert equations["checks"]["translation_family_connected"] is False
    assert equations["checks"]["closure_fibres_are_translation_classes"] is False
