from closure_supernet.trading_continuous_unified_closure_nrrf879_887 import derive_continuous_unified_closure


def test_quote_observation_is_same_current_closure_not_presemantic_environment():
    trading = {
        "symbol": "BTC/USD",
        "quote_projections": [{"status": "WITNESSED", "best_bid": "100", "best_ask": "101"}],
        "trading_projection_field": {"returned_natural_forms": []},
        "translational_truth_partition": {},
        "temporal_closures": [],
    }
    result = derive_continuous_unified_closure(trading_receipt=trading)
    assert result["status"] == "WITNESSED"
    assert result["observation_and_trading_are_translation_equal_readings"] is True
    assert result["observation_is_not_presemantic_environment"] is True
    assert result["completed_temporal_trade_count"] == 0
    assert result["quote_can_update_current_closure_without_realizing_pnl"] is True
    assert result["stage_gate_present"] is False
    assert result["separate_observation_pipeline_present"] is False


def test_open_is_recomputed_current_boundary_not_accumulated_history():
    prior = {
        "current_revision": 7,
        "returned_readings": [{"kind": "QUOTE_OBSERVATION", "reading": {"x": 1}}],
        "open_boundary": {
            "status": "OPEN",
            "unresolved_relations": ["STALE_OLD_OPEN_REASON"],
        },
    }
    trading = {
        "symbol": "BTC/USD",
        "quote_projections": [{"status": "WITNESSED", "best_bid": "102", "best_ask": "103"}],
        "trading_projection_field": {"returned_natural_forms": []},
        "translational_truth_partition": {},
        "temporal_closures": [],
    }
    result = derive_continuous_unified_closure(trading_receipt=trading, prior_state=prior)
    assert result["current_revision"] == 8
    assert "STALE_OLD_OPEN_REASON" not in result["open_boundary"]["unresolved_relations"]
    assert result["open_boundary"]["is_current_boundary_only"] is True
    assert result["open_boundary"]["accumulates_prior_open_failures"] is False
    assert result["open_queue_present"] is False
    assert result["open_count_is_progress_metric"] is False


def test_completed_trade_is_projection_inside_same_continuous_current():
    trading = {
        "symbol": "BTC/USD",
        "quote_projections": [{"status": "WITNESSED", "best_bid": "100", "best_ask": "101"}],
        "fill_increments": [{"side": "buy", "base_quantity": "0.1"}],
        "temporal_closures": [{"closure_id": "c1", "natural_profit": "1"}],
        "trading_projection_field": {"returned_natural_forms": []},
        "translational_truth_partition": {},
    }
    result = derive_continuous_unified_closure(trading_receipt=trading)
    kinds = [row["kind"] for row in result["returned_readings"]]
    assert "QUOTE_OBSERVATION" in kinds
    assert "FILL_RETURN" in kinds
    assert "TEMPORAL_TRADE_CLOSURE" in kinds
    assert result["completed_temporal_trade_count"] == 1
    assert result["completed_trade_is_projection_not_truth_start"] is True
    assert result["only_returned_interaction_changes_current_closure"] is True
