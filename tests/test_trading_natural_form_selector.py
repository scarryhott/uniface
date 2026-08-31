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


def _select(feedback: list[dict[str, object]]) -> dict[str, object]:
    natural = resolve_open_sensor_trading_closure(
        observer_id="o",
        sensor_feedback=feedback,
    )
    return derive_natural_form_selection(natural_closure=natural)


def test_open_relation_frontier_selects_missing_return_that_would_close_path() -> None:
    selection = _select([_returned("ab", "A", "B", "1")])

    assert selection["status"] == "OPEN"
    assert selection["selection_mode"] == "OPEN_CLOSURE_FRONTIER"
    assert selection["profitable_natural_form_count"] == 0
    selected = selection["selected_interactions"]
    assert len(selected) == 1
    assert selected[0]["kind"] == "RETURN_CLOSURE_COMPLETING_RELATION"
    assert selected[0]["source_token"] == "B"
    assert selected[0]["target_token"] == "A"
    assert selected[0]["would_close_witnessed_directed_path"] is True
    assert selected[0]["predicted_profit"] is None
    assert selected[0]["may_author_truth"] is False


def test_returned_profitable_natural_form_selects_itself() -> None:
    selection = _select(
        [
            _returned("ab", "A", "B", "1"),
            _returned("ba", "B", "A", "-2"),
        ]
    )

    assert selection["status"] == "WITNESSED"
    assert selection["selection_mode"] == "PROFIT_NATURAL_FORM_CLASS"
    assert selection["profitable_natural_form_count"] == 1
    chosen = selection["selected_interactions"][0]
    assert chosen["kind"] == "WITNESSED_PROFIT_NATURAL_FORM"
    assert chosen["natural_profit"] == "1"
    assert chosen["amplitude"] == "1"
    assert chosen["trade_admissible"] is True
    assert chosen["automatic_order_submission"] is False
    assert chosen["may_author_truth"] is False


def test_profitable_closure_with_open_execution_selects_execution_return_boundary() -> None:
    selection = _select(
        [
            _returned("ab", "A", "B", "1", cost_complete=False),
            _returned("ba", "B", "A", "-2", cost_complete=False),
        ]
    )

    assert selection["selection_mode"] == "PROFIT_NATURAL_FORM_CLASS"
    chosen = selection["selected_interactions"][0]
    assert chosen["kind"] == "RETURN_PROFIT_EXECUTION_EVIDENCE"
    assert chosen["status"] == "OPEN"
    assert chosen["natural_profit"] == "1"
    assert chosen["requires_return"] is True
    assert chosen["trade_admissible"] is False


def test_costly_saturated_known_space_opens_relation_space_extension() -> None:
    selection = _select(
        [
            _returned("ab", "A", "B", "1"),
            _returned("ba", "B", "A", "1"),
        ]
    )

    assert selection["selection_mode"] == "OPEN_RELATION_SPACE_EXTENSION"
    assert selection["profitable_natural_form_count"] == 0
    assert selection["closure_completing_frontier"] == []
    chosen = selection["selected_interactions"][0]
    assert chosen["kind"] == "RETURN_NEW_SOURCE_PRESERVING_RELATION"
    assert chosen["source_token"] is None
    assert chosen["target_token"] is None
    assert chosen["predicted_profit"] is None
    assert chosen["predeclared_candidate_graph_required"] is False


def test_invalid_return_is_selected_for_source_preserving_repair() -> None:
    selection = _select(
        [
            _returned("ab", "A", "B", "1", source_ids=False),
        ]
    )

    assert selection["selection_mode"] == "OPEN_CLOSURE_FRONTIER"
    chosen = selection["selected_interactions"][0]
    assert chosen["kind"] == "RETURN_SOURCE_PRESERVED_RELATION"
    assert chosen["source_token"] == "A"
    assert chosen["target_token"] == "B"
    assert chosen["requires_source_preserving_return"] is True


def test_hair_translations_select_same_profitable_closure_truth() -> None:
    left = _select(
        [
            _returned("ab0", "A", "B", "-3"),
            _returned("ba0", "B", "A", "2"),
        ]
    )
    right = _select(
        [
            _returned("ab1", "A", "B", "2", hair_delta="5"),
            _returned("ba1", "B", "A", "-3", hair_delta="-5"),
        ]
    )

    left_choice = left["selected_interactions"][0]
    right_choice = right["selected_interactions"][0]
    assert left_choice["closure_id"] == right_choice["closure_id"]
    assert left_choice["natural_profit"] == right_choice["natural_profit"] == "1"
    assert left_choice["kind"] == right_choice["kind"] == "WITNESSED_PROFIT_NATURAL_FORM"


def test_current_runtime_exposes_natural_form_selection_without_truth_authorship() -> None:
    receipt = resolve_trading_equation(
        observer_id="o",
        sensor_feedback=[_returned("ab", "A", "B", "1")],
    )

    assert receipt["natural_form_selects_interaction"] is True
    assert receipt["selection_is_set_valued"] is True
    assert receipt["selection_authors_truth"] is False
    assert receipt["external_strategy_selector_present"] is False
    assert receipt["predeclared_candidate_graph_present"] is False
    assert receipt["natural_form_selection"]["selection_mode"] == "OPEN_CLOSURE_FRONTIER"
    assert receipt["selected_interactions"] == receipt["natural_form_selection"]["selected_interactions"]


def test_selector_closes_interactively_when_selected_boundary_returns() -> None:
    first = resolve_trading_equation(
        observer_id="o",
        sensor_feedback=[_returned("ab", "A", "B", "1")],
    )
    request = first["selected_interactions"][0]
    assert request["source_token"] == "B"
    assert request["target_token"] == "A"

    second = resolve_trading_equation(
        observer_id="o",
        sensor_feedback=[
            _returned("ab2", "A", "B", "1"),
            _returned("ba2", "B", "A", "-2"),
        ],
    )

    assert second["status"] == "WITNESSED"
    assert second["current_profit_truth_witnessed"] is True
    assert second["natural_form_selection"]["selection_mode"] == "PROFIT_NATURAL_FORM_CLASS"
    chosen = second["selected_interactions"][0]
    assert chosen["kind"] == "WITNESSED_PROFIT_NATURAL_FORM"
    assert chosen["natural_profit"] == "1"
