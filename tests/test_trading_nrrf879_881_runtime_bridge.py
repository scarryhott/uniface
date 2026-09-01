from __future__ import annotations

from closure_supernet.alpaca_nrrf879_881_live import AlpacaNRRF879881Runtime
from closure_supernet.trading_nrrf879_881_runtime_bridge import (
    ACTION_KINDS,
    FORMAL_MODULES,
    derive_nrrf879_881_runtime_bridge,
)


def temporal_receipt(*, smuggle: str | None = None):
    receipt = {
        "status": "WITNESSED",
        "symbol": "BTC/USD",
        "empirical_arena_is_one_market_through_time": True,
        "temporal_order_authors_relation": True,
        "closure_derives_inventory_return": True,
        "instantaneous_ask_bid_cycle_authors_trade": False,
        "successor_bid_authors_exit": False,
        "multi_asset_cycle_required": False,
        "adapter_authors_temporal_closure": False,
        "automatic_order_submission": False,
        "relative_hair_horizon_from_returned_history": True,
        "relative_ball_size_from_returned_execution": True,
        "fees_must_return_for_net_profit": True,
        "fill_derivation_audit": {
            "incremental_fill_is_derived_from_returned_cumulative_state": True,
            "fifo_matching_used": False,
            "lifo_matching_used": False,
            "cost_basis_selector_present": False,
        },
        "temporal_closure_audit": {
            "temporal_closure_is_inventory_state_return": True,
            "current_relative_inventory": "0",
            "current_inventory_status": "WITNESSED",
        },
        "temporal_closures": [
            {
                "temporal_closure_id": "t0",
                "relative_ball_size_quote": "125",
                "relative_ball_size_unit": "USD-notional",
            }
        ],
        "current_temporal_closure": {
            "temporal_closure_id": "t0",
            "relative_ball_size_quote": "125",
            "relative_ball_size_unit": "USD-notional",
        },
        "quote_projections": [
            {
                "kind": "CURRENT_SPREAD_FRICTION_PROJECTION",
                "best_bid": "100",
                "best_ask": "101",
                "authors_temporal_closure": False,
            }
        ],
        "translational_truth_partition": {"class_count": 1},
        "current_closure_relative_atlas": {"truth_class_count": 1},
        "natural_form_field": {"truth_class_count": 1},
        "open_boundary_natural_selection": {"boundary_interaction_count": 1},
        "selected_interactions": [
            {
                "kind": "RETURN_RELATIVE_HAIR_FIDELITY",
                "status": "OPEN",
                "requires_return": True,
            }
        ],
    }
    if smuggle == "fifo":
        receipt["fill_derivation_audit"]["fifo_matching_used"] = True
    if smuggle == "next_bid":
        receipt["successor_bid_authors_exit"] = True
    if smuggle == "auto":
        receipt["automatic_order_submission"] = True
    return receipt


def test_bridge_names_all_three_formal_modules_and_adds_no_semantics():
    bridge = derive_nrrf879_881_runtime_bridge(
        temporal_trading_receipt=temporal_receipt()
    )
    assert bridge["anti_smuggling_audit"]["valid"] is True
    assert bridge["formal_correspondence"]["formal_modules"] == list(FORMAL_MODULES)
    assert bridge["bridge_defines_new_closure_law"] is False
    assert bridge["bridge_defines_new_selector"] is False
    assert bridge["bridge_defines_new_profit_model"] is False


def test_environment_exposes_only_nrrf881_action_families_without_execution():
    bridge = derive_nrrf879_881_runtime_bridge(
        temporal_trading_receipt=temporal_receipt()
    )
    actions = bridge["selectable_action_space"]
    assert tuple(row["kind"] for row in actions) == ACTION_KINDS
    assert all(row["authors_truth"] is False for row in actions)
    assert all(row["automatic_execution"] is False for row in actions)
    limit = next(row for row in actions if row["kind"] == "LIMIT")
    assert limit["coordinates"] == ["side", "price", "quantity"]


def test_ui_radius_is_projection_of_returned_ball_and_drag_wheel_are_truth_inert():
    bridge = derive_nrrf879_881_runtime_bridge(
        temporal_trading_receipt=temporal_receipt()
    )
    ui = bridge["closure_ball_ui"]
    assert ui["closure_ball_radius"] == "125"
    assert ui["closure_ball_unit"] == "USD-notional"
    assert ui["drag_is_hair"] is True
    assert ui["wheel_is_local_global_scale"] is True
    assert ui["drag_authors_truth"] is False
    assert ui["wheel_authors_truth"] is False


def test_open_interaction_is_not_given_forecast_expected_profit_or_tie_breaker():
    bridge = derive_nrrf879_881_runtime_bridge(
        temporal_trading_receipt=temporal_receipt()
    )
    item = bridge["open_or_selected_interactions"][0]
    assert item["expected_profit"] is None
    assert item["forecast"] is None
    assert item["runtime_tie_breaker"] is None
    assert item["bridge_authors_selection"] is False


def test_smuggled_fifo_or_successor_bid_forces_bridge_open():
    for mode in ("fifo", "next_bid", "auto"):
        bridge = derive_nrrf879_881_runtime_bridge(
            temporal_trading_receipt=temporal_receipt(smuggle=mode)
        )
        assert bridge["anti_smuggling_audit"]["valid"] is False
        assert bridge["anti_smuggling_audit"]["status"] == "OPEN"
        assert bridge["anti_smuggling_audit"]["runtime_semantic_author_present"] is True


class FakeAdapter:
    def __init__(self, trading):
        self.trading = trading
    def resolve_once(self):
        return {"status": self.trading["status"], "trading": self.trading}


def test_live_wrapper_factors_alpaca_receipt_through_formal_bridge():
    runtime = AlpacaNRRF879881Runtime(FakeAdapter(temporal_receipt()))
    receipt = runtime.resolve_once()
    assert receipt["status"] == "WITNESSED"
    assert receipt["runtime_semantic_author_present"] is False
    assert receipt["nrrf879_881_runtime"]["formal_correspondence"]["nrrf879"][
        "inventory_return_is_derived"
    ] is True


def test_live_wrapper_fails_open_when_runtime_semantics_are_smuggled():
    runtime = AlpacaNRRF879881Runtime(FakeAdapter(temporal_receipt(smuggle="fifo")))
    receipt = runtime.resolve_once()
    assert receipt["status"] == "OPEN"
    assert receipt["runtime_semantic_author_present"] is True
