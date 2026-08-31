from __future__ import annotations

from closure_supernet.formal_proof_index import PROOF_BUNDLES
from closure_supernet.interactive_translation_equations_current import resolve_trading_equation
from closure_supernet.trading_natural_form_closure import resolve_open_sensor_trading_closure
from closure_supernet.trading_open_boundary_natural_selection import (
    derive_open_boundary_natural_selection,
)
from closure_supernet.trading_relative_hair_horizon_ball_size import (
    derive_preaction_relative_coordinates,
)
from closure_supernet.trading_translational_truth_partition import (
    derive_translational_truth_partition,
)
from closure_supernet.trading_unified_natural_form_field import (
    derive_unified_natural_form_field,
)


def returned(
    return_id: str,
    source: str,
    target: str,
    value: str,
    *,
    hair_delta: str = "0",
    relative_size: str = "3",
    quoted_number: str | None = None,
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
        "relative_size": relative_size,
        "relative_size_unit": "risk-unit",
    }
    if quoted_number is not None:
        row["absolute_quote"] = quoted_number
    return row


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


def derive_selection(
    history: list[list[dict[str, object]]],
) -> dict[str, object]:
    current = history[-1]
    natural = resolve_open_sensor_trading_closure(
        observer_id="o",
        sensor_feedback=current,
    )
    coordinates = derive_preaction_relative_coordinates(
        observer_id="o",
        natural_closure=natural,
        current_feedback=current,
        sensor_history=history,
    )
    field = derive_unified_natural_form_field(
        natural_closure=natural,
        preaction_coordinates=coordinates["by_closure_id"],
    )
    partition = derive_translational_truth_partition(
        observer_id="o",
        sensor_history=history,
    )
    return derive_open_boundary_natural_selection(
        natural_form_field=field,
        preaction_relative_coordinates=coordinates,
        translational_truth_partition=partition,
    )


def test_open_boundary_unifies_relation_hair_and_ball_frontiers() -> None:
    selection = derive_selection(hair_equivalent_frames())
    axes = {row["axis"] for row in selection["open_boundary"]}

    assert selection["boundary_driven"] is True
    assert selection["natural_select_is_set_valued"] is True
    assert {"RELATION_SPACE", "TEMPORAL_HAIR", "RELATIVE_BALL"} <= axes
    assert selection["boundary_interaction_count"] == selection["open_boundary_count"]
    assert all(row["status"] == "OPEN" for row in selection["open_boundary"])
    assert all(row["selection_authors_truth"] is False for row in selection["open_boundary"])
    assert all(row["support_delta_on_selection"] == 0 for row in selection["open_boundary"])


def test_selection_names_boundary_but_does_not_move_support() -> None:
    selection = derive_selection(hair_equivalent_frames())

    assert selection["selection_authors_truth"] is False
    assert selection["selection_moves_support"] is False
    assert selection["support_delta_on_selection"] == 0
    assert selection["only_return_can_change_support"] is True
    assert selection["return_state_eq_close"] is True


def test_return_in_support_is_hair_and_support_stays_fixed() -> None:
    selection = derive_selection(hair_equivalent_frames())
    support = selection["support_evolution"]
    events = support["events"]

    assert support["strict_extension_count"] == 1
    assert support["hair_resampling_count"] == 2
    assert support["support_class_count"] == 1
    assert events[0]["classification"] == "RETURN_OUTSIDE_SUPPORT_EXTENDS"
    assert events[0]["strict_support_extension"] is True
    assert events[1]["classification"] == "RETURN_IN_SUPPORT_IS_HAIR"
    assert events[1]["support_fixed"] is True
    assert events[2]["classification"] == "RETURN_IN_SUPPORT_IS_HAIR"
    assert events[2]["support_fixed"] is True
    assert support["hair_resampling_widens_support"] is False


def test_return_outside_support_strictly_widens_and_can_discover_profit() -> None:
    history = hair_equivalent_frames()[:2]
    history.append(
        [
            returned("ab2", "A", "B", "-4", relative_size="5"),
            returned("ba2", "B", "A", "2", relative_size="3"),
        ]
    )
    selection = derive_selection(history)
    support = selection["support_evolution"]

    assert support["support_class_count"] == 2
    assert support["strict_extension_count"] == 2
    assert support["profitable_class_discovery_count"] >= 1
    assert support["return_outside_support_strictly_extends"] is True
    assert support["profitability_is_truth_class_property"] is True
    assert selection["new_truth_class_return_can_widen_support"] is True


def test_hair_represented_world_has_same_truth_derived_boundary_support() -> None:
    left = [
        returned("ab0", "A", "B", "-3", relative_size="5", quoted_number="100"),
        returned("ba0", "B", "A", "2", relative_size="3", quoted_number="101"),
    ]
    right = [
        returned(
            "ab1",
            "A",
            "B",
            "2",
            hair_delta="5",
            relative_size="5",
            quoted_number="999999",
        ),
        returned(
            "ba1",
            "B",
            "A",
            "-3",
            hair_delta="-5",
            relative_size="3",
            quoted_number="-999999",
        ),
    ]

    left_selection = derive_selection([left])
    right_selection = derive_selection([right])
    left_ids = {row["boundary_id"] for row in left_selection["open_boundary"]}
    right_ids = {row["boundary_id"] for row in right_selection["open_boundary"]}

    assert left_ids == right_ids
    assert left_selection["truth_derived_selector"] is True
    assert left_selection["factors_through_translational_truth_classes"] is True
    assert left_selection["hair_blind_selector_contract"] is True
    assert left_selection["absolute_quoted_number_used_by_selector"] is False
    assert left_selection["ball_selector_policy_present"] is False
    assert left_selection["runtime_smuggled_tie_breaker_present"] is False


def test_runtime_integrates_nrrf874_without_replacing_execution_projection() -> None:
    receipt = resolve_trading_equation(
        observer_id="o",
        sensor_history=hair_equivalent_frames(),
    )
    selection = receipt["open_boundary_natural_selection"]

    assert receipt["formal_correspondence"].startswith("NRRF874")
    assert receipt["open_boundary_drives_learning_selection"] is True
    assert receipt["truth_derived_selector"] is True
    assert receipt["selector_is_hair_blind"] is True
    assert receipt["selection_moves_support"] is False
    assert receipt["only_return_can_change_support"] is True
    assert receipt["learning_interactions"] == selection["boundary_interactions"]
    assert receipt["selected_interactions"] == receipt["natural_form_field"]["action_projections"]
    assert receipt["natural_form_field"]["learning_interactions"] == receipt["learning_interactions"]
    assert selection["automatic_order_submission"] is False


def test_fairness_and_reachability_remain_explicit_hypotheses() -> None:
    selection = derive_selection(hair_equivalent_frames())

    assert selection["eventual_learning_is_conditional"] is True
    assert selection["fairness_is_hypothesis_not_runtime_fact"] is True
    assert selection["reachability_is_hypothesis_not_runtime_fact"] is True
    assert selection["fairness_claimed"] is False
    assert selection["market_reachability_claimed"] is False
    assert selection["profit_prediction_used_by_selector"] is False


def test_reported_nrrf874_theorem_family_is_proof_indexed() -> None:
    bundle = next(
        row
        for row in PROOF_BUNDLES
        if row["module"]
        == "NRRF874OpenBoundaryNaturalSelectionSupportWideningDerivedFromTranslationalTruth"
    )
    theorem_names = set(bundle["theorem_names"])

    assert "select_authors_no_truth" in theorem_names
    assert "return_outside_support_extends" in theorem_names
    assert "truthDerived_iff_factors" in theorem_names
    assert "fair_selector_is_closure_complete" in theorem_names
    assert "open_boundary_natural_selection_closes_the_support_gap" in theorem_names
    assert bundle["proof_kind"] == "OPEN_BOUNDARY_TRUTH_DERIVED_SELECTION_SUPPORT_WIDENING"
