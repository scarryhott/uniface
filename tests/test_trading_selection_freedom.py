from __future__ import annotations

from closure_supernet.interactive_translation_equations_current import resolve_trading_equation
from closure_supernet.trading_natural_form_closure import resolve_open_sensor_trading_closure
from closure_supernet.trading_relative_hair_horizon_ball_size import (
    derive_relative_ball_size,
    derive_relative_hair_horizon,
    derive_selection_freedom,
)


def returned(
    return_id: str,
    source: str,
    target: str,
    value: str,
    *,
    hair_delta: str = "0",
    relative_size: str = "3",
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
        "relative_size": relative_size,
        "relative_size_unit": "risk-unit",
    }


def hair_equivalent_frames() -> list[list[dict[str, object]]]:
    return [
        [
            returned("ab0", "A", "B", "-3", relative_size="5"),
            returned("ba0", "B", "A", "2", relative_size="3"),
        ],
        [
            returned("ab1", "A", "B", "2", hair_delta="5", relative_size="5"),
            returned("ba1", "B", "A", "-3", hair_delta="-5", relative_size="3"),
        ],
        [
            returned("ab2", "A", "B", "-2", hair_delta="1", relative_size="5"),
            returned("ba2", "B", "A", "1", hair_delta="-1", relative_size="3"),
        ],
    ]


def profitable_form(frame: list[dict[str, object]]) -> dict[str, object]:
    closure = resolve_open_sensor_trading_closure(observer_id="o", sensor_feedback=frame)
    return next(
        form for form in closure["natural_forms"] if form["orientation"] == "PROFITABLE"
    )


def test_selection_freedom_is_joint_hair_ball_region_with_open_frontier() -> None:
    history = hair_equivalent_frames()
    form = profitable_form(history[-1])
    freedom = derive_selection_freedom(
        current_form=form,
        observer_id="o",
        current_feedback=history[-1],
        sensor_history=history,
    )

    assert freedom["status"] == "WITNESSED"
    assert freedom["temporal_freedom"]["upper_inclusive_return_steps"] == 2
    assert freedom["ball_freedom"]["upper_inclusive"] == "3"
    assert freedom["ball_freedom"]["unit"] == "risk-unit"
    assert freedom["executable_region_witnessed"] is True
    assert freedom["temporal_freedom"]["frontier"]["status"] == "OPEN"
    assert freedom["temporal_freedom"]["frontier"]["next_return_step"] == 3
    assert freedom["ball_freedom"]["frontier"]["status"] == "OPEN"
    assert freedom["unwitnessed_boundary_remains_open"] is True
    assert freedom["external_limit_authors_selection"] is False
    assert freedom["configured_threshold_authors_selection"] is False


def test_exact_fidelity_break_resolves_temporal_boundary_without_threshold() -> None:
    history = hair_equivalent_frames()
    prior_frame = history[1]
    prior_form = profitable_form(prior_frame)
    history[-1] = [
        returned("ab2", "A", "B", "-1", relative_size="5"),
        returned("ba2", "B", "A", "2", relative_size="3"),
    ]
    horizon = derive_relative_hair_horizon(
        current_form=prior_form,
        observer_id="o",
        sensor_history=history,
    )
    size = derive_relative_ball_size(
        current_form=prior_form,
        current_feedback=prior_frame,
    )
    freedom = derive_selection_freedom(
        current_form=prior_form,
        observer_id="o",
        current_feedback=prior_frame,
        sensor_history=history,
        relative_hair_horizon=horizon,
        relative_ball_size=size,
    )

    assert horizon["horizon_return_steps"] == 0
    assert freedom["status"] == "WITNESSED"
    assert freedom["executable_region_witnessed"] is False
    frontier = freedom["temporal_freedom"]["frontier"]
    assert frontier["status"] == "WITNESSED"
    assert frontier["kind"] == "EXACT_RELATIVE_HAIR_FIDELITY_BREAK"
    assert frontier["next_return_step"] == 1
    assert frontier["boundary_is_empirically_identified"] is True


def test_selection_freedom_expands_only_when_returned_evidence_expands() -> None:
    history = hair_equivalent_frames()
    form = profitable_form(history[-1])
    freedom = derive_selection_freedom(
        current_form=form,
        observer_id="o",
        current_feedback=history[-1],
        sensor_history=history,
    )

    assert freedom["evolution"]["status"] == "WITNESSED"
    assert freedom["evolution"]["state"] == "EXPANDED"
    assert freedom["evolution"]["temporal_change"] == "EXPANDED"
    assert freedom["evolution"]["ball_change"] == "STABLE"
    assert freedom["evolution"]["returned_evidence_caused_change"] is True
    assert freedom["evolution"]["external_limit_caused_change"] is False


def test_missing_fidelity_never_gets_replaced_by_configured_limit() -> None:
    frame = hair_equivalent_frames()[0]
    form = profitable_form(frame)
    freedom = derive_selection_freedom(
        current_form=form,
        observer_id="o",
        current_feedback=frame,
        sensor_history=(),
    )

    assert freedom["status"] == "OPEN"
    assert freedom["temporal_freedom"]["status"] == "OPEN"
    assert freedom["temporal_freedom"]["upper_inclusive_return_steps"] is None
    assert freedom["executable_region_witnessed"] is False
    assert freedom["missing_evidence_widens_selection"] is False
    assert freedom["external_limit_authors_selection"] is False


def test_runtime_preaction_bundle_carries_closed_selection_freedom() -> None:
    history = hair_equivalent_frames()
    receipt = resolve_trading_equation(observer_id="o", sensor_history=history)
    profitable = next(
        row
        for row in receipt["natural_form_field"]["returned_natural_forms"]
        if row["orientation"] == "PROFITABLE"
    )
    closure_id = profitable["closure_id"]
    coordinates = receipt["preaction_relative_coordinates"]["by_closure_id"][closure_id]
    freedom = coordinates["selection_freedom"]

    assert receipt["preaction_relative_coordinates"]["selection_freedom_from_returned_fidelity"] is True
    assert receipt["preaction_relative_coordinates"]["remaining_limits_are_open_selection_frontiers"] is True
    assert freedom["status"] == "WITNESSED"
    assert freedom["executable_region_witnessed"] is True
    assert coordinates["derived_before_action"] is True
