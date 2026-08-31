from __future__ import annotations

from closure_supernet.interactive_translation_equations_current import resolve_trading_equation
from closure_supernet.trading_translational_truth_partition import derive_translational_truth_partition


def _returned(
    return_id: str,
    source: str,
    target: str,
    value: str,
    *,
    hair_delta: str = "0",
) -> dict[str, object]:
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
    result = derive_translational_truth_partition(observer_id="o", sensor_history=[base, translated])

    assert result["status"] == "WITNESSED"
    assert result["translational_truth_alone"] is True
    assert result["class_count"] == 1
    truth = result["classes"][0]
    assert truth["member_count"] == 2
    assert truth["hair_orbit_member_count"] == 2
    assert truth["interaction_witness_count"] == 2
    assert truth["unitary_curvature"] == "-1"
    assert truth["natural_profit"] == "1"
    assert truth["profitable_truth_class"] is True
    assert truth["ball_equals_natural_form_class"] is True
    assert truth["hair_differences_do_not_split_truth"] is True
    assert result["learned_profit"] is True
    assert result["profitable_truth_class_count"] == 1
    events = result["learning_events"]
    assert events[0]["event"] == "NEW_TRANSLATIONAL_TRUTH_WITNESSED"
    assert events[1]["event"] == "SAME_TRANSLATIONAL_TRUTH_RETURNED"
    assert events[1]["hair_return_of_known_truth"] is True
    assert all(event["predicts_profit"] is False for event in events)


def test_changed_curvature_refines_truth_partition_without_dynamics_law() -> None:
    left = [_returned("ab0", "A", "B", "-3"), _returned("ba0", "B", "A", "2")]
    right = [_returned("ab1", "A", "B", "-4"), _returned("ba1", "B", "A", "2")]
    result = derive_translational_truth_partition(observer_id="o", sensor_history=[left, right])

    assert result["class_count"] == 2
    assert {row["unitary_curvature"] for row in result["classes"]} == {"-1", "-2"}
    assert result["relation_space_refines_from_returned_interaction"] is True
    assert result["distinct_natural_forms_are_not_declared_translations"] is True
    assert result["inter_class_dynamics_law_present"] is False
    assert result["trend_model_present"] is False
    assert result["forecast_model_present"] is False
    assert result["similarity_tolerance_present"] is False


def test_costly_truths_do_not_learn_profit_from_motion() -> None:
    costly0 = [_returned("ab0", "A", "B", "2"), _returned("ba0", "B", "A", "1")]
    costly1 = [_returned("ab1", "A", "B", "1"), _returned("ba1", "B", "A", "1")]
    result = derive_translational_truth_partition(observer_id="o", sensor_history=[costly0, costly1])

    assert result["class_count"] == 2
    assert result["learned_profit"] is False
    assert result["profitable_truth_class_count"] == 0
    assert result["profit_learning_is_discovery_not_prediction"] is True
    assert result["profit_trajectory_present"] is False
    assert all(row["profitable_truth_class"] is False for row in result["classes"])


def test_open_frame_does_not_invent_truth_class() -> None:
    closed = [_returned("ab", "A", "B", "-2"), _returned("ba", "B", "A", "1")]
    open_frame = [_returned("ab2", "A", "B", "-2")]
    result = derive_translational_truth_partition(observer_id="o", sensor_history=[closed, open_frame])

    assert result["class_count"] == 1
    assert result["witnessed_frame_count"] == 1
    assert result["open_frame_count"] == 1
    assert result["frame_boundaries_author_truth"] is False
    assert result["learning_events"][-1]["event"] == "OPEN_NO_TRANSLATIONAL_TRUTH"
    assert result["learning_events"][-1]["authors_truth"] is False


def test_current_runtime_uses_translational_truth_alone() -> None:
    base = [_returned("ab0", "A", "B", "-3"), _returned("ba0", "B", "A", "2")]
    translated = [
        _returned("ab1", "A", "B", "2", hair_delta="5"),
        _returned("ba1", "B", "A", "-3", hair_delta="-5"),
    ]

    receipt = resolve_trading_equation(
        observer_id="o",
        source_truth_mode="FORMAL_FIXTURE",
        sensor_history=[base, translated],
    )

    assert receipt["translational_truth_alone"] is True
    assert receipt["translational_truth_authors_relation_partition"] is True
    assert receipt["ball_equals_natural_form_truth_class"] is True
    assert receipt["hair_is_intra_truth_class_presentation"] is True
    assert receipt["predeclared_market_graph_authors_truth_partition"] is False
    assert receipt["separate_dynamics_law_present"] is False
    assert receipt["inter_class_transition_model_present"] is False
    assert receipt["trend_model_present"] is False
    assert receipt["forecast_model_present"] is False
    assert receipt["closure_continuation"] is None
    assert receipt["learned_profit"] is True
    assert receipt["formal_fixture_mode_is_not_external_truth"] is True

    partition = receipt["translational_truth_partition"]
    assert partition["class_count"] == 1
    assert partition["classes"][0]["member_count"] == 2
    assert receipt["translational_truth_learning"] == partition
