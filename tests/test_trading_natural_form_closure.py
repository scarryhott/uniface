from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient

from closure_supernet.api_interactive_translation import create_app
from closure_supernet.interactive_translation_equations_current import (
    resolve_trading_equation,
)
from closure_supernet.trading_natural_form_closure import (
    resolve_open_sensor_trading_closure,
)


def _returned(
    return_id: str,
    source: str,
    target: str,
    value: str,
    *,
    hair_delta: str = "0",
    timestamp: str | None = None,
    authenticated: bool = True,
    cost_complete: bool = True,
) -> dict[str, object]:
    return {
        "id": return_id,
        "source": source,
        "target": target,
        "value": value,
        "hair_delta": hair_delta,
        "source_ids": [f"source:{return_id}"],
        "returned": True,
        "authenticated": authenticated,
        "cost_complete": cost_complete,
        "timestamp": timestamp,
    }


def test_successor_quote_pair_is_not_a_natural_trading_closure() -> None:
    receipt = resolve_open_sensor_trading_closure(
        observer_id="trader",
        sensor_feedback=[
            _returned("q0", "USD", "BTC", "10"),
            _returned("q1", "USD", "BTC", "11"),
        ],
    )

    assert receipt["status"] == "OPEN"
    assert receipt["natural_forms"] == []
    assert receipt["ask_to_immediately_succeeding_bid_is_definition"] is False
    assert receipt["successor_observation_authors_closure"] is False
    assert receipt["fixed_horizon"] is None


def test_unitary_curvature_and_ball_maze_co_derive_amplitude_and_timing() -> None:
    receipt = resolve_open_sensor_trading_closure(
        observer_id="trader",
        sensor_feedback=[
            _returned(
                "usd-btc",
                "USD",
                "BTC",
                "10",
                hair_delta="2",
                timestamp="2026-08-30T10:00:00Z",
            ),
            _returned(
                "btc-eth",
                "BTC",
                "ETH",
                "4",
                hair_delta="1",
                timestamp="2026-08-30T10:00:05Z",
            ),
            _returned(
                "eth-usd",
                "ETH",
                "USD",
                "-12",
                hair_delta="-3",
                timestamp="2026-08-30T10:00:08Z",
            ),
        ],
    )

    assert receipt["status"] == "WITNESSED"
    assert receipt["witnessed_natural_form_count"] == 1
    form = receipt["natural_forms"][0]
    assert form["unitary_curvature"] == "2"
    assert form["amplitude"] == "2"
    assert form["natural_profit"] == "-2"
    assert form["hair_sum"] == "0"
    assert form["hair_closes_on_return"] is True

    assert form["timing"]["maze_steps"] == 3
    assert form["timing"]["support_start_index"] == 0
    assert form["timing"]["support_end_index"] == 2
    assert form["timing"]["duration_seconds"] == "8.0"
    assert form["timing"]["fixed_horizon"] is None

    assert form["amplitude_timing_translation_equal"] is True
    assert form["signal_trade_translation_equal"] is True
    assert (
        form["amplitude_projection"]["translation_id"]
        == form["timing"]["translation_id"]
        == form["signal_projection"]["translation_id"]
        == form["trade_projection"]["translation_id"]
    )
    assert form["signal_precedes_trade_semantically"] is False
    assert form["trade_precedes_signal_semantically"] is False


def test_hair_translation_changes_local_values_not_natural_curvature() -> None:
    base = [
        _returned("ab", "A", "B", "8"),
        _returned("bc", "B", "C", "3"),
        _returned("ca", "C", "A", "-9"),
    ]
    translated = [
        _returned("ab", "A", "B", "10", hair_delta="2"),
        _returned("bc", "B", "C", "7", hair_delta="4"),
        _returned("ca", "C", "A", "-15", hair_delta="-6"),
    ]

    left = resolve_open_sensor_trading_closure(
        observer_id="o",
        sensor_feedback=base,
    )
    right = resolve_open_sensor_trading_closure(
        observer_id="o",
        sensor_feedback=translated,
    )

    left_form = left["natural_forms"][0]
    right_form = right["natural_forms"][0]
    assert (
        left["sensor_returns"][0]["relation_value"]
        != right["sensor_returns"][0]["relation_value"]
    )
    assert left_form["relation_sum"] == right_form["relation_sum"] == "2"
    assert left_form["unitary_curvature"] == right_form["unitary_curvature"] == "2"
    assert left_form["natural_profit"] == right_form["natural_profit"] == "-2"
    assert left_form["closure_id"] == right_form["closure_id"]
    assert right_form["hair_sum"] == "0"


def test_ball_partition_maze_not_adjacency_supplies_timing() -> None:
    receipt = resolve_open_sensor_trading_closure(
        observer_id="o",
        sensor_feedback=[
            _returned("ab", "A", "B", "1"),
            _returned("xy", "X", "Y", "5"),
            _returned("bc", "B", "C", "2"),
            _returned("ca", "C", "A", "-4"),
        ],
    )

    assert receipt["status"] == "WITNESSED"
    form = receipt["natural_forms"][0]
    assert set(form["return_ids"]) == {"ab", "bc", "ca"}
    assert "xy" not in form["return_ids"]
    assert form["timing"]["maze_steps"] == 3
    assert form["timing"]["support_start_index"] == 0
    assert form["timing"]["support_end_index"] == 3
    assert len(receipt["ball_partition"]) == 2


def test_trade_execution_remains_open_when_cost_return_is_incomplete() -> None:
    receipt = resolve_open_sensor_trading_closure(
        observer_id="o",
        sensor_feedback=[
            _returned("ab", "A", "B", "-2", cost_complete=False),
            _returned("ba", "B", "A", "1", cost_complete=False),
        ],
    )

    form = receipt["natural_forms"][0]
    assert form["natural_profit"] == "1"
    assert form["orientation"] == "PROFITABLE"
    assert form["signal_trade_translation_equal"] is True
    assert form["trade_projection"]["execution_return_status"] == "OPEN"
    assert form["trade_projection"]["admissible"] is False


def test_route_receipt_compatibility_cannot_close_current_trading_runtime() -> None:
    receipt = resolve_trading_equation(
        receipts=[
            {
                "relation": ["USD", "BTC", "USD"],
                "id": "legacy-fill",
                "authenticated": True,
                "closed_relation": True,
                "realized_profit": "100",
            }
        ]
    )

    assert receipt["status"] == "OPEN"
    assert receipt["natural_forms"] == []
    legacy = receipt["legacy_route_receipt_projection"]
    assert legacy["compatibility_status"] == "WITNESSED"
    assert legacy["semantic_authority"] is False
    assert legacy["may_gate_interaction"] is False
    assert receipt["forms"][0]["gate_open"] is True
    assert receipt["forms"][0]["gate_open_authors_truth"] is False


def test_computation_limit_leaves_open_sensor_continuation_open() -> None:
    receipt = resolve_open_sensor_trading_closure(
        observer_id="o",
        sensor_feedback=[
            _returned("ab", "A", "B", "1"),
            _returned("ba", "B", "A", "-1"),
        ],
        max_returns=1,
    )

    assert receipt["status"] == "OPEN"
    assert receipt["natural_forms"] == []
    assert receipt["boundary_receipt"]["status"] == "OPEN"
    assert receipt["boundary_receipt"]["limit_is_semantic"] is False


def test_research_api_runs_natural_trading_closure_without_mutation(tmp_path) -> None:
    app = create_app(
        SimpleNamespace(database_path=tmp_path / "natural-trading-closure.db")
    )
    with TestClient(app) as client:
        before = client.get("/supernet/interface").json()["closure_ui_contract"]
        capabilities = client.get(
            "/supernet/closure-equations/capabilities"
        ).json()
        assert capabilities["successor_quote_loop_authors_truth"] is False
        assert capabilities["amplitude_timing_one_translation"] is True
        assert capabilities["signal_trade_one_translation"] is True

        response = client.post(
            "/supernet/closure-equations/resolve",
            json={
                "trading": {
                    "observer_id": "trader",
                    "sensor_feedback": [
                        _returned("ab", "A", "B", "-2"),
                        _returned("ba", "B", "A", "1"),
                    ],
                }
            },
        )
        assert response.status_code == 200
        trading = response.json()["trading"]
        assert trading["status"] == "WITNESSED"
        assert trading["natural_forms"][0]["natural_profit"] == "1"
        assert trading["natural_forms"][0]["signal_trade_translation_equal"] is True

        after = client.get("/supernet/interface").json()["closure_ui_contract"]
        assert after["id"] == before["id"]
