from __future__ import annotations

from closure_supernet.nrrf843_ui_mirror import derive_nrrf843_ui_receipt
from closure_supernet.translational_truth_axiometry import derive_closure


def test_missing_visualization_stays_open_and_admits_no_natural_form() -> None:
    derivation = derive_closure(
        [
            {"id": "a", "state": {"perspective_id": "authored-metadata"}},
            {"id": "b", "state": {"perspective_id": "other-metadata"}},
        ]
    )

    assert derivation.status == "OPEN_NO_PERSPECTIVE_READING"
    assert derivation.supernet_open is True
    assert derivation.perspective_visual_mirror.perspective_ids == ()
    assert derivation.perspective_visual_mirror.truth_ready is False
    assert derivation.visual_truth_closure.truth_issued is False
    assert derivation.natural_forms == ()

    receipt = derive_nrrf843_ui_receipt(
        truth_derivation=derivation.to_dict()
    )
    assert receipt["status"] == "OPEN_NO_PERSPECTIVE"
    assert receipt["ui_family"]["readings"] == {}
    assert receipt["claims"]["truth_issued"] is False


def test_changing_actual_visualization_kernel_changes_closure() -> None:
    merged = derive_closure(
        ["a", "b"],
        perspective_readings={"p": {"a": "one-form", "b": "one-form"}},
    )
    separated = derive_closure(
        ["a", "b"],
        perspective_readings={"p": {"a": "left", "b": "right"}},
    )

    assert merged.status == separated.status == "WITNESSED"
    assert merged.equivalence_closure.classes == (("a", "b"),)
    assert separated.equivalence_closure.classes == (("a",), ("b",))
    assert merged.vis_closure(["a"]) == ("a", "b")
    assert separated.vis_closure(["a"]) == ("a",)


def test_relative_truth_cannot_override_the_visualization_kernel() -> None:
    proposed_equality = {
        "id": "proposal:a-b",
        "source": "a",
        "target": "b",
        "verdict": "TRUE",
        "compatible": True,
        "visual_equation": {
            "id": "equation:a-b",
            "source": "a",
            "target": "b",
            "equation": "display(a) = display(b)",
            "deterministic": True,
        },
    }
    derivation = derive_closure(
        ["a", "b"],
        [proposed_equality],
        perspective_readings={"p": {"a": "left", "b": "right"}},
    )

    assert derivation.equivalence_closure.classes == (("a",), ("b",))
    assert derivation.truth_evaluations[0].reason == (
        "cross_translation_rejected_by_visualization_kernel"
    )
    assert derivation.truth_evaluations[0].closure_admitted is False


def test_independent_translation_is_required_between_perspectives() -> None:
    readings = {
        "local": {"a": "violet", "b": "violet"},
        "global": {"a": "unity", "b": "unity"},
    }
    untranslated = derive_closure(
        ["a", "b"],
        perspective_readings=readings,
    )
    translated = derive_closure(
        ["a", "b"],
        perspective_readings=readings,
        perspective_translations=(
            {
                "id": "return:local-global",
                "source": "local",
                "target": "global",
                "display_translation": {"violet": "unity"},
                "witnessed": True,
                "source_return_ids": ["return:local-global"],
            },
        ),
    )

    assert untranslated.status == "OPEN_UNTRANSLATED_PERSPECTIVES"
    assert untranslated.supernet_open is True
    assert untranslated.natural_forms == ()
    untranslated_receipt = derive_nrrf843_ui_receipt(
        truth_derivation=untranslated.to_dict()
    )
    assert untranslated_receipt["status"] == (
        "OPEN_UNTRANSLATED_PERSPECTIVES"
    )
    assert untranslated_receipt["translational_mirror"]["translations"] == []
    assert translated.status == "WITNESSED"
    assert translated.supernet_open is False
    assert translated.equivalence_closure.classes == (("a", "b"),)

    receipt = derive_nrrf843_ui_receipt(
        truth_derivation=translated.to_dict()
    )
    assert receipt["status"] == "WITNESSED"
    assert receipt["translational_mirror"]["witnessed"] is True
    assert receipt["translational_mirror"]["translations"][0][
        "id"
    ] == "return:local-global"
