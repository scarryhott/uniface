from __future__ import annotations

from closure_supernet.interactive_translation_equations_current import resolve_trading_equation
from closure_supernet.trading_translational_truth_partition import derive_translational_truth_partition


def _returned(return_id: str, source: str, target: str, value: str, *, hair_delta: str = "0") -> dict[str, object]:
    return {
        "id": return_id,
        "source": source,
        "target": target,
        "value": value,
        "hair_delta": hair_delta,
        "source_ids": [f"source:{return_id}"],
        "returned": True,
        "authenticated": True,
        "cost_complete": True,
    }


def test_hair_translations_are_one_ball_truth_class() -> None:
    base = [_returned("ab0", "A", "B", "-3"), _returned("ba0", "B", "A", "2")]
    translated = [
        _returned("ab1", "A", "B", "2", hair_delta="5"),
        _returned("ba1", "B", "A", "-3", hair_delta="-5"),
    ]

    result = derive_translational_truth_partition(
        observer_id="o", sensor_history=[base, translated]
    )

    assert result["status"] == "WITNESSED"
    assert result["class_count"] == 1
    truth = result["classes"][0]
    assert truth["member_count"] == 2
    assert truth["hair_orbit_member_count"] == 2
    assert truth["interaction_witness_count"] == 2
    assert truth["unitary_curvature"] == "-1"
    assert truth["ball_equals_natural_form_class"] is True
    assert truth["hair_differences_do_not_split_truth"] is True


def test_changed_curvature_refines_truth_partition() -> None:
    left = [_returned("ab0", "A", "B", "-3"), _returned("ba0", "B", "A", "2")]
    right = [_returned("ab1", "A", "B", "-4"), _returned("ba1", "B", "A", "2")]

    result = derive_translational_truth_partition(
        observer_id="o", sensor_history=[left, right]
    )

    assert result["class_count"] == 2
    assert {row["unitary_curvature"] for row in result["classes"]} == {"-1", "-2"}
    assert result["relation_space_refines_from_returned_interaction"] is True


def test_open_frame_does_not_invent_truth_class() -> None:
    closed = [_returned("ab", "A", "B", "-2"), _returned("ba", "B", "A", "1")]
    open_frame = [_returned("ab2", "A", "B", "-2")]

    result = derive_translational_truth_partition(
        observer_id="o", sensor_history=[closed, open_frame]
    )

    assert result["class_count"] == 1
    assert result["witnessed_frame_count"] == 1
    assert result["open_frame_count"] == 1
    assert result["frame_boundaries_author_truth"] is False


def test_current_runtime_exposes_truth_relative_partition() -> None:
    base = [_returned("ab0", "A", "B", "-3"), _returned("ba0", "B", "A", "2")]
    translated = [
        _returned("ab1", "A", "B", "2", hair_delta="5"),
        _returned("ba1", "B", "A", "-3", hair_delta="-5"),
    ]

    receipt = resolve_trading_equation(observer_id="o", sensor_history=[base, translated])

    assert receipt["translational_truth_authors_relation_partition"] is True
    assert receipt["ball_equals_natural_form_truth_class"] is True
    assert receipt["hair_is_intra_truth_class_presentation"] is True
    assert receipt["predeclared_market_graph_authors_truth_partition"] is False
    partition = receipt["translational_truth_partition"]
    assert partition["class_count"] == 1
    assert partition["classes"][0]["member_count"] == 2
