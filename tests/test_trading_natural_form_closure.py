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


def test_cost_curvature_has_zero_available_amplitude_and_zero_closure_timing() -> None:
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
    assert form["natural_profit"] == "-2"
    assert form["amplitude"] == "0"
    assert form["available_amplitude"] == "0"
    assert form["timing"]["value"] == "0"
    assert form["amplitude_timing_numerically_identical"] is True
    assert form["hair_sum"] == "0"
    assert form["hair_closes_on_return"] is True
    assert form["timing"]["duration_seconds"] == "8.0"
    assert form["timing"]["clock_duration_authors_timing"] is False
    assert form["clock_duration_is_timing"] is False
    assert form["timing"]["fixed_horizon"] is None
    assert form["amplitude_timing_translation_equal"] is True
    assert form["signal_trade_translation_equal"] is True
    assert form["signal_trade_value_equal"] is True
    assert (
        form["amplitude_projection"]["translation_id"]
        == form["timing"]["translation_id"]
        == form["signal_projection"]["translation_id"]
        == form["trade_projection"]["translation_id"]
    )


def test_raw_ball_timing_moves_under_hair_but_closure_timing_does_not() -> None:
    base = [
        _returned("ab", "A", "B", "-3"),
        _returned("ba", "B", "A", "2"),
    ]
    translated = [
        _returned("ab", "A", "B", "2", hair_delta="5"),
        _returned("ba", "B", "A", "-3", hair_delta="-5"),
    ]

    left = resolve_open_sensor_trading_closure(observer_id="o", sensor_feedback=base)
    right = resolve_open_sensor_trading_closure(observer_id="o", sensor_feedback=translated)
    left_form = left["natural_forms"][0]
    right_form = right["natural_forms"][0]
    assert left_form["unitary_curvature"] == right_form["unitary_curvature"] == "-1"
    assert left_form["natural_profit"] == right_form["natural_profit"] == "1"
    assert left_form["amplitude"] == right_form["amplitude"] == "1"
    assert left_form["closure_id"] == right_form["closure_id"]
    assert left_form["raw_ball_partition"]["max"] == "3"
    assert right_form["raw_ball_partition"]["max"] == "1"
    assert left_form["raw_ball_partition"]["hair_invariant"] is False
    assert left_form["closure_ball_partition"]["max"] == "1"
    assert right_form["closure_ball_partition"]["max"] == "1"
    assert left_form["timing"]["value"] == right_form["timing"]["value"] == "1"
    assert left_form["timing"]["entry_leg_free_in_closure"] is True
    assert left_form["timing"]["return_attains_timing"] is True


def test_open_sensor_exposes_all_simple_cycles_not_one_bfs_route() -> None:
    receipt = resolve_open_sensor_trading_closure(
        observer_id="o",
        sensor_feedback=[
            _returned("ab", "A", "B", "1"),
            _returned("ba", "B", "A", "-2"),
            _returned("ac", "A", "C", "3"),
            _returned("ca", "C", "A", "-5"),
        ],
    )

    assert receipt["status"] == "WITNESSED"
    assert receipt["open_sensor_runs_all_closed_itineraries"] is True
    assert receipt["simple_cycles_determine_finite_closed_itinerary_geometry"] is True
    assert receipt["bfs_route_authors_truth"] is False
    assert len(receipt["natural_forms"]) == 2
    signatures = {
        tuple((row["source_token"], row["target_token"]) for row in form["directed_relation_signature"])
        for form in receipt["natural_forms"]
    }
    assert signatures == {
        (("A", "B"), ("B", "A")),
        (("A", "C"), ("C", "A")),
    }


def test_ball_partition_is_directed_closure_fibre_not_undirected_component() -> None:
    receipt = resolve_open_sensor_trading_closure(
        observer_id="o",
        sensor_feedback=[
            _returned("ab", "A", "B", "1"),
            _returned("cb", "C", "B", "1"),
        ],
    )
    assert receipt["status"] == "OPEN"
    assert receipt["natural_forms"] == []
    assert receipt["undirected_connectivity_authors_ball"] is False
    assert receipt["ball_partition_is_directed_translation_fibre"] is True
    assert sorted(ball["member_tokens"] for ball in receipt["ball_partition"]) == [["A"], ["B"], ["C"]]


def test_profitable_closure_has_amplitude_equal_ball_partition_max() -> None:
    receipt = resolve_open_sensor_trading_closure(
        observer_id="o",
        sensor_feedback=[_returned("ab", "A", "B", "-2"), _returned("ba", "B", "A", "1")],
    )
    form = receipt["natural_forms"][0]
    assert form["unitary_curvature"] == "-1"
    assert form["natural_profit"] == "1"
    assert form["amplitude"] == "1"
    assert form["raw_ball_partition"]["max"] == "2"
    assert form["closure_ball_partition"]["max"] == "1"
    assert form["timing"]["value"] == "1"
    assert form["amplitude_timing_numerically_identical"] is True
    assert form["signal_projection"]["value"] == "1"
    assert form["trade_projection"]["value"] == "1"
    assert form["signal_trade_value_equal"] is True


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
    assert form["amplitude"] == "1"
    assert form["orientation"] == "PROFITABLE"
    assert form["signal_trade_translation_equal"] is True
    assert form["trade_projection"]["execution_return_status"] == "OPEN"
    assert form["trade_projection"]["admissible"] is False


def test_route_receipt_compatibility_cannot_close_current_trading_runtime() -> None:
    receipt = resolve_trading_equation(
        receipts=[{
            "relation": ["USD", "BTC", "USD"],
            "id": "legacy-fill",
            "authenticated": True,
            "closed_relation": True,
            "realized_profit": "100",
        }]
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
        sensor_feedback=[_returned("ab", "A", "B", "1"), _returned("ba", "B", "A", "-1")],
        max_returns=1,
    )
    assert receipt["status"] == "OPEN"
    assert receipt["natural_forms"] == []
    assert receipt["boundary_receipt"]["status"] == "OPEN"
    assert receipt["boundary_receipt"]["limit_is_semantic"] is False


def test_research_api_exposes_verified_source_boundary_without_mutation(tmp_path) -> None:
    app = create_app(SimpleNamespace(database_path=tmp_path / "nrrf870.db"))
    with TestClient(app) as client:
        before = client.get("/supernet/interface").json()["closure_ui_contract"]
        capabilities = client.get("/supernet/closure-equations/capabilities").json()
        assert capabilities["truth_requires_verified_source_witness"] is True
        assert capabilities["unsigned_or_untrusted_return_remains_open"] is True
        assert capabilities["caller_returned_flag_authors_truth"] is False
        assert capabilities["successor_quote_loop_authors_truth"] is False
        assert capabilities["open_sensor_all_closed_itineraries"] is True
        assert capabilities["bfs_route_authors_truth"] is False
        assert capabilities["amplitude_is_negative_curvature_part"] is True
        assert capabilities["ball_partition_max_gives_timing"] is True
        assert capabilities["clock_duration_authors_timing"] is False
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
        assert trading["status"] == "OPEN"
        assert trading["natural_forms"] == []
        assert trading["source_truth_audit"]["feedback"]["verified_count"] == 0
        assert trading["source_truth_audit"]["feedback"]["open_count"] == 2

        after = client.get("/supernet/interface").json()["closure_ui_contract"]
        assert after["id"] == before["id"]
