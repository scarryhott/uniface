from closure_supernet.alpaca_nrrf879_881_live import AlpacaNRRF879881Runtime


class FakeAdapter:
    def resolve_once(self):
        returned = {
            "form_id": "form-a",
            "kind": "RETURNED_CLOSED_NATURAL_FORM",
            "status": "WITNESSED",
            "closure_truth_id": "truth-a",
            "directed_relation_signature": ["USD", "BTC", "USD"],
            "unitary_curvature": "-1",
            "natural_profit": "1",
            "orientation": "PROFITABLE",
            "returned_truth_member": True,
            "selected": True,
        }
        trading = {
            "status": "WITNESSED",
            "symbol": "BTC/USD",
            "empirical_arena_is_one_market_through_time": True,
            "temporal_order_authors_relation": True,
            "closure_derives_inventory_return": True,
            "instantaneous_ask_bid_cycle_authors_trade": False,
            "successor_bid_authors_exit": False,
            "multi_asset_cycle_required": False,
            "adapter_authors_temporal_closure": False,
            "fees_must_return_for_net_profit": True,
            "relative_hair_horizon_from_returned_history": True,
            "relative_ball_size_from_returned_execution": True,
            "automatic_order_submission": False,
            "fill_derivation_audit": {
                "incremental_fill_is_derived_from_returned_cumulative_state": True,
                "fifo_matching_used": False,
                "lifo_matching_used": False,
                "cost_basis_selector_present": False,
            },
            "temporal_closure_audit": {
                "current_relative_inventory": "0",
                "current_inventory_status": "WITNESSED",
                "temporal_closure_is_inventory_state_return": True,
            },
            "temporal_closures": [],
            "current_temporal_closure": None,
            "quote_projections": [],
            "translational_truth_partition": {"class_count": 1},
            "open_boundary_natural_selection": {"boundary_interaction_count": 0},
            "current_closure_relative_atlas": {"truth_class_count": 1},
            "natural_form_field": {},
            "trading_projection_field": {"returned_natural_forms": [returned]},
            "selected_interactions": [],
        }
        return {"protocol": "fake", "status": "WITNESSED", "trading": trading}


def test_live_runtime_exposes_nrrf884_886_translation_family_without_novelty_gate():
    receipt = AlpacaNRRF879881Runtime(FakeAdapter()).resolve_once()
    family = receipt["nrrf884_886_translation_families"]

    assert receipt["status"] == "WITNESSED"
    assert family["family_count"] == 1
    assert family["families"][0]["closure_truth_id"] == "truth-a"
    assert receipt["family_is_relative_visualization_of_selected_natural_forms"] is True
    assert receipt["new_tt_class_means_trade"] is False
    assert receipt["same_tt_class_means_do_not_trade"] is False
    assert receipt["fixed_price_subset_is_maximally_unified"] is False
    assert receipt["profitability_authors_family_membership"] is False
    assert receipt["automatic_order_submission"] is False
