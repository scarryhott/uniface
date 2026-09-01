from __future__ import annotations

from closure_supernet.alpaca_nrrf879_881_live import AlpacaNRRF879881Runtime
from closure_supernet.trading_nrrf879_881_runtime_bridge import ACTION_KINDS, FORMAL_MODULES, derive_nrrf879_881_runtime_bridge


def receipt(smuggle=None):
    r = {
        "status": "WITNESSED", "symbol": "BTC/USD",
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
        "fill_derivation_audit": {"incremental_fill_is_derived_from_returned_cumulative_state": True, "fifo_matching_used": False, "lifo_matching_used": False, "cost_basis_selector_present": False},
        "temporal_closure_audit": {"temporal_closure_is_inventory_state_return": True, "current_relative_inventory": "0", "current_inventory_status": "WITNESSED"},
        "temporal_closures": [{"relative_ball_size_quote": "125", "relative_ball_size_unit": "USD-notional"}],
        "current_temporal_closure": {"relative_ball_size_quote": "125", "relative_ball_size_unit": "USD-notional"},
        "quote_projections": [{"best_bid": "100", "best_ask": "101", "authors_temporal_closure": False}],
        "translational_truth_partition": {"class_count": 1},
        "current_closure_relative_atlas": {"truth_class_count": 1},
        "natural_form_field": {"truth_class_count": 1},
        "open_boundary_natural_selection": {"boundary_interaction_count": 1},
        "selected_interactions": [{"kind": "RETURN_RELATIVE_HAIR_FIDELITY", "status": "OPEN", "requires_return": True}],
    }
    if smuggle == "fifo": r["fill_derivation_audit"]["fifo_matching_used"] = True
    if smuggle == "next": r["successor_bid_authors_exit"] = True
    if smuggle == "auto": r["automatic_order_submission"] = True
    return r


def test_bridge_is_projection_of_formal_stack_not_new_semantics():
    b = derive_nrrf879_881_runtime_bridge(temporal_trading_receipt=receipt())
    assert b["anti_smuggling_audit"]["valid"] is True
    assert b["formal_correspondence"]["formal_modules"] == list(FORMAL_MODULES)
    assert b["bridge_defines_new_closure_law"] is False
    assert b["bridge_defines_new_selector"] is False
    assert b["bridge_defines_new_profit_model"] is False
    assert b["formal_correspondence"]["lean_kernel_executed_by_runtime"] is False


def test_environment_action_space_is_selectable_but_truth_inert():
    b = derive_nrrf879_881_runtime_bridge(temporal_trading_receipt=receipt())
    actions = b["selectable_action_space"]
    assert tuple(x["kind"] for x in actions) == ACTION_KINDS
    assert all(x["authors_truth"] is False for x in actions)
    assert all(x["automatic_execution"] is False for x in actions)
    assert next(x for x in actions if x["kind"] == "LIMIT")["coordinates"] == ["side", "price", "quantity"]


def test_closure_ball_ui_is_returned_ball_projection():
    ui = derive_nrrf879_881_runtime_bridge(temporal_trading_receipt=receipt())["closure_ball_ui"]
    assert ui["closure_ball_radius"] == "125"
    assert ui["drag_is_hair"] is True and ui["drag_authors_truth"] is False
    assert ui["wheel_is_local_global_scale"] is True and ui["wheel_authors_truth"] is False


def test_bridge_fails_open_on_runtime_semantic_smuggling():
    for mode in ("fifo", "next", "auto"):
        b = derive_nrrf879_881_runtime_bridge(temporal_trading_receipt=receipt(mode))
        assert b["anti_smuggling_audit"]["valid"] is False
        assert b["anti_smuggling_audit"]["status"] == "OPEN"


class FakeAdapter:
    def __init__(self, r): self.r = r
    def resolve_once(self): return {"status": self.r["status"], "trading": self.r}


def test_live_entrypoint_factors_source_receipt_through_bridge():
    out = AlpacaNRRF879881Runtime(FakeAdapter(receipt())).resolve_once()
    assert out["status"] == "WITNESSED"
    assert out["runtime_semantic_author_present"] is False


def test_live_entrypoint_forces_open_if_runtime_smuggles_selector():
    out = AlpacaNRRF879881Runtime(FakeAdapter(receipt("fifo"))).resolve_once()
    assert out["status"] == "OPEN"
    assert out["runtime_semantic_author_present"] is True
