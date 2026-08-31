from __future__ import annotations

from closure_supernet.closure_continuity import (
    OPEN_STATUS,
    WITNESSED_STATUS,
    audit_translational_continuity,
    finite_horn_closure,
)
from closure_supernet.interaction_closure import derive_interaction_closure


def _truth():
    return {
        "id": "truth:1",
        "visual_truth_closure": {"id": "visual:1"},
        "status": "OPEN",
        "supernet_open": True,
        "natural_forms": [
            {"id": "form:a", "members": ["a", "b"]},
            {"id": "form:c", "members": ["c"]},
        ],
    }


def _ui(reading, *, labels=("display:ab", "display:c")):
    return {
        "id": "ui:1",
        "status": "OPEN",
        "closure_derivation_id": "truth:1",
        "visual_closure_id": "visual:1",
        "ui_family": {
            "perspective_ids": ["p"],
            "readings": {
                "p": {
                    "a": labels[0],
                    "b": labels[0] if reading == "equal" else "display:b",
                    "c": labels[1],
                }
            },
        },
        "truth_constraint_location": {"located": False},
        "ui_closure": {"closure_falls_out_from_ui_projection": False},
    }


def _journey(*, chosen=True):
    return {
        "chosen_perspective": {
            "perspective_id": "p" if chosen else None,
            "status": "CHOSEN" if chosen else "OPEN",
            "chosen": chosen,
            "choice_source": "EVENT_PERSPECTIVE" if chosen else "OPEN",
        }
    }


def _derive(ui, journey, **compatibility):
    return derive_interaction_closure(
        truth_derivation=_truth(),
        nrrf843_ui=ui,
        nrrf842_journey=journey,
        coordination=compatibility.get("coordination", {}),
        ai_translation=compatibility.get("ai_translation", {}),
        tokenomic=compatibility.get("tokenomic", {}),
        visual_network={"nodes": [], "edges": []},
        black_mirror={},
        network_return=compatibility.get("network_return", {}),
    )


def test_source_choice_without_returned_interaction_remains_open():
    result = _derive(_ui("equal"), _journey())
    assert result["status"] == OPEN_STATUS
    assert result["translational_continuity"]["translational_truth_witnessed"] is False
    assert result["unification_constraint"]["stored_status_flags_used_as_evidence"] is False
    assert result["existence_closed"] is False
    assert result["dialectic_continuation_status"] == OPEN_STATUS


def test_singleton_perspective_is_not_selected_without_return():
    result = _derive(_ui("equal"), _journey(chosen=False))
    assert result["status"] == OPEN_STATUS
    assert result["perspective_selection"]["active_perspective_id"] is None
    assert result["perspective_selection"]["fallback_selection_used"] is False


def test_stored_closure_claim_cannot_hide_partition_mismatch():
    ui = _ui("different")
    ui["status"] = "WITNESSED"
    ui["truth_constraint_location"]["located"] = True
    ui["ui_closure"]["closure_falls_out_from_ui_projection"] = True
    result = _derive(ui, _journey())
    assert result["status"] == OPEN_STATUS
    assert result["projection_equivalence"]["partition_equal"] is False


def test_display_relabeling_preserves_translational_truth_id():
    left = _derive(_ui("equal", labels=("x", "y")), _journey())
    right = _derive(_ui("equal", labels=("other-x", "other-y")), _journey())
    assert left["translational_truth_id"] == right["translational_truth_id"]
    assert left["id"] == right["id"]


def test_parallel_compatibility_products_cannot_author_interaction_truth():
    left = _derive(_ui("equal"), _journey())
    right = _derive(
        _ui("equal"),
        _journey(),
        coordination={"status": "REJECTED", "arbitrary": 1},
        ai_translation={"status": "WITNESSED", "arbitrary": 2},
        tokenomic={"status": "CLOSED", "arbitrary": 3},
        network_return={"status": "FAILED", "arbitrary": 4},
    )
    assert left["status"] == right["status"] == OPEN_STATUS
    assert left["translational_truth_id"] == right["translational_truth_id"]
    assert all(
        receipt["semantic_authority"] is False
        for receipt in right["relative_readings"].values()
    )


def test_finite_relative_closure_witnesses_fixed_point_but_not_existence():
    receipt = finite_horn_closure(
        ["a"],
        [
            {"premise_occurrence_ids": ["a"], "conclusion_occurrence_id": "b"},
            {"premise_occurrence_ids": ["b"], "conclusion_occurrence_id": "c"},
        ],
    )
    assert receipt["status"] == WITNESSED_STATUS
    assert receipt["members"] == ["a", "b", "c"]
    assert receipt["rule_chart_is_universal_truth"] is False
    assert receipt["existence_closed"] is False
    assert receipt["continuation_status"] == OPEN_STATUS


def test_exhausted_computation_bound_is_open_not_false_or_closed():
    receipt = finite_horn_closure(
        ["a"],
        [
            {"premise_occurrence_ids": ["b"], "conclusion_occurrence_id": "c"},
            {"premise_occurrence_ids": ["a"], "conclusion_occurrence_id": "b"},
        ],
        max_iterations=1,
    )
    assert receipt["status"] == OPEN_STATUS
    assert receipt["fixed_point_witnessed"] is False
    assert receipt["boundary_receipt"]["truth_issued"] is False
    assert receipt["boundary_receipt"]["limit_is_semantic"] is False


def test_structural_audit_keeps_forbidden_authorship_open():
    audit = audit_translational_continuity(
        {
            "configuration_authors_truth": True,
            "return_relation": {"operation_enum": ["BUY", "SELL"]},
            "nested": {"existence_closed": True},
        }
    )
    assert audit["status"] == OPEN_STATUS
    assert audit["violation_count"] == 3


def test_interaction_receipt_passes_its_own_continuity_audit():
    result = _derive(_ui("equal"), _journey())
    assert result["continuity_self_audit"]["status"] == WITNESSED_STATUS
    assert result["continuity_self_audit"]["violation_count"] == 0
