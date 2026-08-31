from __future__ import annotations

from closure_supernet.interactive_translation_equations_current import resolve_trading_equation
from closure_supernet.trading_natural_form_closure import resolve_open_sensor_trading_closure
from closure_supernet.trading_relative_hair_horizon_ball_size import (
    derive_preaction_relative_coordinates,
    derive_relative_ball_size,
    derive_relative_hair_horizon,
)


def returned(
    return_id: str,
    source: str,
    target: str,
    value: str,
    *,
    hair_delta: str = "0",
    relative_size: str | None = None,
    relative_size_unit: str | None = None,
) -> dict[str, object]:
    row: dict[str, object] = {
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
    if relative_size is not None:
        row["relative_size"] = relative_size
    if relative_size_unit is not None:
        row["relative_size_unit"] = relative_size_unit
    return row


def hair_equivalent_frames(*, include_size: bool = True) -> list[list[dict[str, object]]]:
    size = {"relative_size": "5", "relative_size_unit": "risk-unit"} if include_size else {}
    reverse_size = {"relative_size": "3", "relative_size_unit": "risk-unit"} if include_size else {}
    return [
        [
            returned("ab0", "A", "B", "-3", **size),
            returned("ba0", "B", "A", "2", **reverse_size),
        ],
        [
            returned("ab1", "A", "B", "2", hair_delta="5", **size),
            returned("ba1", "B", "A", "-3", hair_delta="-5", **reverse_size),
        ],
        [
            returned("ab2", "A", "B", "-2", hair_delta="1", **size),
            returned("ba2", "B", "A", "1", hair_delta="-1", **reverse_size),
        ],
    ]


def current_profitable_form(history: list[list[dict[str, object]]]) -> dict[str, object]:
    closure = resolve_open_sensor_trading_closure(
        observer_id="o",
        sensor_feedback=history[-1],
    )
    return next(
        form for form in closure["natural_forms"] if form["orientation"] == "PROFITABLE"
    )


def formal_runtime(**kwargs: object) -> dict[str, object]:
    return resolve_trading_equation(source_truth_mode="FORMAL_FIXTURE", **kwargs)


def test_exact_hair_fidelity_derives_return_step_horizon() -> None:
    history = hair_equivalent_frames()
    form = current_profitable_form(history)

    horizon = derive_relative_hair_horizon(
        current_form=form,
        observer_id="o",
        sensor_history=history,
    )

    assert horizon["status"] == "WITNESSED"
    assert horizon["relative_hair_fidelity"] == 1.0
    assert horizon["horizon_return_steps"] == 2
    assert horizon["fixed_horizon"] is None
    assert horizon["horizon_is_derived_from_relative_hair_fidelity"] is True
    assert horizon["similarity_tolerance_used"] is False


def test_hair_break_collapses_derived_horizon_without_tolerance() -> None:
    history = hair_equivalent_frames()
    history[-1] = [
        returned("ab2", "A", "B", "-1", relative_size="5", relative_size_unit="risk-unit"),
        returned("ba2", "B", "A", "2", relative_size="3", relative_size_unit="risk-unit"),
    ]
    prior_closure = resolve_open_sensor_trading_closure(
        observer_id="o",
        sensor_feedback=history[1],
    )
    form = next(
        item for item in prior_closure["natural_forms"] if item["orientation"] == "PROFITABLE"
    )
    horizon = derive_relative_hair_horizon(
        current_form=form,
        observer_id="o",
        sensor_history=history,
    )

    assert horizon["status"] == "WITNESSED"
    assert horizon["relative_hair_fidelity"] == 0.5
    assert horizon["horizon_return_steps"] == 0
    assert horizon["zero_horizon"] is True


def test_relative_ball_size_is_bottleneck_translated_capacity() -> None:
    history = hair_equivalent_frames()
    form = current_profitable_form(history)
    size = derive_relative_ball_size(
        current_form=form,
        current_feedback=history[-1],
    )

    assert size["status"] == "WITNESSED"
    assert size["relative_ball_size"] == "3"
    assert size["unit"] == "risk-unit"
    assert size["bottleneck_return_id"] == "ba2"
    assert size["size_is_relative_ball_bottleneck"] is True


def test_raw_quote_sizes_are_not_silently_position_size() -> None:
    frame = [
        {**returned("ab", "A", "B", "-3"), "bid_size": "5"},
        {**returned("ba", "B", "A", "2"), "ask_size": "3"},
    ]
    closure = resolve_open_sensor_trading_closure(observer_id="o", sensor_feedback=frame)
    form = next(item for item in closure["natural_forms"] if item["orientation"] == "PROFITABLE")
    size = derive_relative_ball_size(current_form=form, current_feedback=frame)

    assert size["status"] == "OPEN"
    assert size["relative_ball_size"] is None
    assert size["raw_quote_size_is_not_silently_a_relative_ball_size"] is True


def test_full_runtime_derives_horizon_and_size_before_profit_action() -> None:
    history = hair_equivalent_frames()
    receipt = formal_runtime(observer_id="o", sensor_history=history)

    assert receipt["fixed_horizon_present"] is False
    assert receipt["horizon_from_relative_hair_fidelity"] is True
    assert receipt["relative_ball_is_size"] is True
    assert receipt["external_position_size_present"] is False
    profitable = next(
        row
        for row in receipt["natural_form_field"]["returned_natural_forms"]
        if row["orientation"] == "PROFITABLE"
    )
    assert profitable["relative_hair_horizon"]["horizon_return_steps"] == 2
    assert profitable["relative_ball_size"]["relative_ball_size"] == "3"
    assert profitable["preaction_ready"] is True
    assert profitable["action_projection"]["kind"] == "PROJECT_RETURNED_PROFIT_NATURAL_FORM"
    assert profitable["action_projection"]["preaction_ready"] is True


def test_profit_truth_with_size_but_no_fidelity_history_stays_open_before_action() -> None:
    frame = hair_equivalent_frames()[0]
    receipt = formal_runtime(observer_id="o", sensor_feedback=frame)
    profitable = next(
        row
        for row in receipt["natural_form_field"]["returned_natural_forms"]
        if row["orientation"] == "PROFITABLE"
    )

    assert profitable["relative_ball_size"]["status"] == "WITNESSED"
    assert profitable["relative_hair_horizon"]["status"] == "OPEN"
    assert profitable["preaction_ready"] is False
    assert profitable["action_projection"]["kind"] == "RETURN_RELATIVE_HAIR_FIDELITY"


def test_profit_truth_with_fidelity_but_missing_ball_size_stays_open_before_action() -> None:
    history = hair_equivalent_frames(include_size=False)
    receipt = formal_runtime(observer_id="o", sensor_history=history)
    profitable = next(
        row
        for row in receipt["natural_form_field"]["returned_natural_forms"]
        if row["orientation"] == "PROFITABLE"
    )

    assert profitable["relative_hair_horizon"]["horizon_return_steps"] == 2
    assert profitable["relative_ball_size"]["status"] == "OPEN"
    assert profitable["preaction_ready"] is False
    assert profitable["action_projection"]["kind"] == "RETURN_RELATIVE_BALL_SIZE"


def test_preaction_coordinate_bundle_is_one_natural_form_reading() -> None:
    history = hair_equivalent_frames()
    closure = resolve_open_sensor_trading_closure(
        observer_id="o",
        sensor_feedback=history[-1],
    )
    bundle = derive_preaction_relative_coordinates(
        observer_id="o",
        natural_closure=closure,
        current_feedback=history[-1],
        sensor_history=history,
    )

    assert bundle["horizon_from_relative_hair_fidelity"] is True
    assert bundle["size_from_relative_ball"] is True
    assert bundle["fixed_horizon_present"] is False
    assert bundle["external_position_size_present"] is False
    assert bundle["derived_before_action"] is True
