from __future__ import annotations

from closure_supernet.interactive_translation_equations_current import (
    resolve_trading_equation,
)
from closure_supernet.trading_closure_continuation import (
    resolve_trading_closure_continuation,
)


def _returned(return_id: str, source: str, target: str, value: str) -> dict[str, object]:
    return {
        "id": return_id,
        "source": source,
        "target": target,
        "value": value,
        "hair_delta": "0",
        "source_ids": [f"source:{return_id}"],
        "returned": True,
        "authenticated": True,
        "cost_complete": True,
    }


def _frame(prefix: str, close_value: str) -> list[dict[str, object]]:
    return [
        _returned(f"{prefix}-ab", "A", "B", "2"),
        _returned(f"{prefix}-bc", "B", "C", "1"),
        _returned(f"{prefix}-ca", "C", "A", close_value),
    ]


def test_same_directed_continuum_reads_motion_toward_profit_without_authorship() -> None:
    receipt = resolve_trading_closure_continuation(
        observer_id="o",
        sensor_history=[
            _frame("f0", "-1"),  # curvature 2, profit -2
            _frame("f1", "-2"),  # curvature 1, profit -1
        ],
    )

    assert receipt["status"] == "WITNESSED"
    assert receipt["continuum_count"] == 1
    track = receipt["continua"][0]
    assert track["latest_movement"] == "TOWARD_PROFIT"
    assert track["latest_natural_profit"] == "-1"
    assert track["transitions"][0]["profit_delta"] == "1"
    assert track["trajectory_authors_truth"] is False
    assert track["fixed_horizon"] is None


def test_positive_crossing_does_not_author_execution() -> None:
    receipt = resolve_trading_closure_continuation(
        observer_id="o",
        sensor_history=[
            _frame("f0", "-2"),   # profit -1
            _frame("f1", "-4"),   # curvature -1, profit +1
        ],
    )

    track = receipt["continua"][0]
    transition = track["transitions"][0]
    assert transition["crossed_positive_natural_profit"] is True
    assert receipt["positive_crossing_authors_trade"] is False
    assert transition["current_trade_admissible"] is True


def test_reversed_relation_orientation_is_a_distinct_continuum() -> None:
    forward = _frame("fwd", "-1")
    reverse = [
        _returned("rev-ac", "A", "C", "1"),
        _returned("rev-cb", "C", "B", "1"),
        _returned("rev-ba", "B", "A", "-1"),
    ]
    receipt = resolve_trading_closure_continuation(
        observer_id="o",
        sensor_history=[forward, reverse],
    )

    assert receipt["continuum_count"] == 2
    assert all(len(track["transitions"]) == 0 for track in receipt["continua"])


def test_exact_duplicate_sensor_state_adds_no_semantic_history() -> None:
    frame = _frame("same", "-1")
    receipt = resolve_trading_closure_continuation(
        observer_id="o",
        sensor_history=[frame, frame],
    )

    assert receipt["frames"][1]["status"] == "OPEN"
    assert receipt["frames"][1]["duplicate_return_state"] is True
    assert receipt["frames"][1]["authors_truth"] is False
    assert len(receipt["continua"][0]["readings"]) == 1


def test_current_runtime_demotes_historical_continuation_to_non_authoritative_code() -> None:
    receipt = resolve_trading_equation(
        observer_id="o",
        source_truth_mode="FORMAL_FIXTURE",
        sensor_history=[
            _frame("f0", "-1"),
            _frame("f1", "-2"),
        ],
    )

    assert receipt["status"] == "WITNESSED"
    assert receipt["closure_continuation"] is None
    assert receipt["translational_truth_alone"] is True
    assert receipt["separate_dynamics_law_present"] is False
    assert receipt["inter_class_transition_model_present"] is False
    assert receipt["curvature_continuation_is_authoritative"] is False
    assert receipt["history_length_authors_truth"] is False
    assert receipt["profit_trajectory_present"] is False
    assert receipt["profit_trajectory_authors_trade"] is False
    assert receipt["fixed_horizon"] is None
