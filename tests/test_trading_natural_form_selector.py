from __future__ import annotations

from closure_supernet.interactive_translation_equations_current import (
    resolve_trading_equation,
)
from closure_supernet.trading_natural_form_closure import (
    resolve_open_sensor_trading_closure,
)
from closure_supernet.trading_natural_form_selector import (
    derive_natural_form_selection,
)
from closure_supernet.trading_unified_natural_form_field import (
    derive_unified_natural_form_field,
)


def _returned(
    return_id: str,
    source: str,
    target: str,
    value: str,
    *,
    hair_delta: str = "0",
    authenticated: bool = True,
    cost_complete: bool = True,
    source_ids: bool = True,
) -> dict[str, object]:
    return {
        "id": return_id,
        "source": source,
        "target": target,
        "value": value,
        "hair_delta": hair_delta,
        "source_ids": [f"source:{return_id}"] if source_ids else [],
        "returned": True,
        "authenticated": authenticated,
        "cost_complete": cost_complete,
    }


def _field(feedback: list[dict[str, object]]) -> dict[str, object]:
    natural = resolve_open_sensor_trading_closure(
        observer_id="o",
        sensor_feedback=feedback,
    )
    return derive_unified_natural_form_field(natural_closure=natural)


def _kinds(field: dict[str, object]) -> set[str]:
    return {str(row["kind"]) for row in field["natural_form_field"]}


def _projection_kinds(field: dict[str, object]) -> set[str]:
    return {str(row["kind"]) for row in field["action_projections"]}


def test_recognition_and_selection_are_one_pre_action_field() -> None:
    field = _field([_returned("ab", "A", "B", "1")])

    assert field["recognition_equals_selection"] is True
    assert field["recognition_precedes_selection"] is False
    assert field["selection_precedes_recognition"] is False
    assert field["separate_selector_present"] is False
    assert field["selector_mode_present"] is False
    assert field["action_occurs_after_unified_natural_form_field"] is True
    assert all(
        row["recognized"] is True
        and row["selected"] is True
        and row["recognition_selection_same_form"] is True
        for row in field["natural_form_field"]
    )


def test_open_closure_form_and_relation_space_extension_coexist() -> None:
    field = _field([_returned("ab", "A", "B", "1")])

    assert _kinds(field) == {
        "OPEN_CLOSURE_COMPLETING_NATURAL_FORM",
        "OPEN_RELATION_SPACE_EXTENSION_NATURAL_FORM",
    }
    assert _projection_kinds(field) == {
        "RETURN_CLOSURE_COMPLETING_RELATION",
        "RETURN_NEW_SOURCE_PRESERVING_RELATION",
    }
    boundary = next(
        row
        for row in field["natural_form_field"]
        if row["kind"] == "OPEN_CLOSURE_COMPLETING_NATURAL_FORM"
    )
    assert boundary["source_token"] == "B"
    assert boundary["target_token"] == "A"
    assert boundary["action_projection"]["predicted_profit"] is None
    assert field["all_open_forms_coexist"] is True
    assert field["local_open_cannot_block_relation_space_extension"] is True


def test_deadlock_regression_local_open_does_not_starve_support_widening() -> None:
    # Costly U<->A plus A->B creates local missing returns B->A, B->U and U->B.
    # The old exclusive selector stopped widening here. The unified field must
    # retain the global relation-space extension form simultaneously.
    field = _field(
        [
            _returned("ua", "U", "A", "1"),
            _returned("au", "A", "U", "1"),
            _returned("ab", "A", "B", "0.4"),
        ]
    )

    kinds = _kinds(field)
    assert "RETURNED_CLOSED_NATURAL_FORM" in kinds
    assert "OPEN_CLOSURE_COMPLETING_NATURAL_FORM" in kinds
    assert "OPEN_RELATION_SPACE_EXTENSION_NATURAL_FORM" in kinds
    projections = _projection_kinds(field)
    assert "RETURN_CLOSURE_COMPLETING_RELATION" in projections
    assert "RETURN_NEW_SOURCE_PRESERVING_RELATION" in projections
    assert field["relation_space_extension_is_simultaneous_open_form"] is True


def test_profitable_returned_form_does_not_suppress_open_field() -> None:
    field = _field(
        [
            _returned("ab", "A", "B", "1"),
            _returned("ba", "B", "A", "-2"),
        ]
    )

    assert field["profitable_returned_natural_form_count"] == 1
    assert "RETURNED_CLOSED_NATURAL_FORM" in _kinds(field)
    assert "OPEN_RELATION_SPACE_EXTENSION_NATURAL_FORM" in _kinds(field)
    projections = _projection_kinds(field)
    assert "PROJECT_RETURNED_PROFIT_NATURAL_FORM" in projections
    assert "RETURN_NEW_SOURCE_PRESERVING_RELATION" in projections
    assert field["profit_is_natural_form_property_not_selection_rule"] is True
    assert field["selection_is_not_filtering"] is True


def test_open_execution_is_an_open_form_projection_of_same_returned_natural_form() -> None:
    field = _field(
        [
            _returned("ab", "A", "B", "1", cost_complete=False),
            _returned("ba", "B", "A", "-2", cost_complete=False),
        ]
    )

    returned = next(
        row
        for row in field["returned_natural_forms"]
        if row["orientation"] == "PROFITABLE"
    )
    projection = returned["action_projection"]
    assert projection["kind"] == "RETURN_PROFIT_EXECUTION_EVIDENCE"
    assert projection["status"] == "OPEN"
    assert projection["requires_return"] is True
    assert projection["may_author_truth"] is False


def test_invalid_source_return_and_global_open_form_coexist() -> None:
    field = _field(
        [_returned("ab", "A", "B", "1", source_ids=False)]
    )

    assert "OPEN_SOURCE_RETURN_NATURAL_FORM" in _kinds(field)
    assert "OPEN_RELATION_SPACE_EXTENSION_NATURAL_FORM" in _kinds(field)
    assert "RETURN_SOURCE_PRESERVED_RELATION" in _projection_kinds(field)
    assert "RETURN_NEW_SOURCE_PRESERVING_RELATION" in _projection_kinds(field)


def test_hair_translations_are_same_returned_natural_form_truth() -> None:
    left = _field(
        [
            _returned("ab0", "A", "B", "-3"),
            _returned("ba0", "B", "A", "2"),
        ]
    )
    right = _field(
        [
            _returned("ab1", "A", "B", "2", hair_delta="5"),
            _returned("ba1", "B", "A", "-3", hair_delta="-5"),
        ]
    )

    left_returned = left["returned_natural_forms"][0]
    right_returned = right["returned_natural_forms"][0]
    assert left_returned["closure_id"] == right_returned["closure_id"]
    assert left_returned["natural_profit"] == right_returned["natural_profit"] == "1"


def test_legacy_selector_import_is_only_alias_of_unified_field() -> None:
    natural = resolve_open_sensor_trading_closure(
        observer_id="o",
        sensor_feedback=[_returned("ab", "A", "B", "1")],
    )
    field = derive_unified_natural_form_field(natural_closure=natural)
    compatibility = derive_natural_form_selection(natural_closure=natural)

    assert compatibility["natural_form_field"] == field["natural_form_field"]
    assert compatibility["action_projections"] == field["action_projections"]
    assert compatibility["compatibility_selector_name_only"] is True
    assert compatibility["separate_selector_present"] is False


def test_current_runtime_exposes_same_object_as_recognition_and_selection() -> None:
    receipt = resolve_trading_equation(
        observer_id="o",
        sensor_feedback=[_returned("ab", "A", "B", "1")],
    )

    assert receipt["recognition_equals_selection"] is True
    assert receipt["separate_selector_present"] is False
    assert receipt["selector_mode_present"] is False
    assert receipt["selection_is_not_filtering"] is True
    assert receipt["natural_form_selection"] == receipt["natural_form_field"]
    assert receipt["selected_interactions"] == receipt["natural_form_field"]["action_projections"]
    assert "RETURN_NEW_SOURCE_PRESERVING_RELATION" in {
        row["kind"] for row in receipt["selected_interactions"]
    }
