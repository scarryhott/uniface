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
    assert result["realized_profit_projection"]["realized_net_profit_quote"] == "0"
    assert result["realized_profit_projection"]["new_realized_profit_delta_quote"] == "0"
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


def _closed_trade(closure_id, net_profit, *, cost_complete=True):
    return {
        "temporal_closure_id": closure_id,
        "source_event_ids": [f"source-{closure_id}"],
        "cost_complete": cost_complete,
        "net_profit_status": "WITNESSED" if cost_complete else "OPEN",
        "net_profit_quote": str(net_profit) if cost_complete else None,
    }


def test_observations_advance_continuous_revision_without_changing_realized_profit():
    first = derive_continuous_unified_closure(
        trading_receipt={
            "symbol": "BTC/USD",
            "quote_projections": [{"source_event_id": "q1", "best_bid": "100", "best_ask": "101"}],
            "trading_projection_field": {"returned_natural_forms": []},
            "translational_truth_partition": {},
            "temporal_closures": [],
        }
    )
    second = derive_continuous_unified_closure(
        trading_receipt={
            "symbol": "BTC/USD",
            "quote_projections": [{"source_event_id": "q2", "best_bid": "102", "best_ask": "103"}],
            "trading_projection_field": {"returned_natural_forms": []},
            "translational_truth_partition": {},
            "temporal_closures": [],
        },
        prior_state=first,
    )
    assert second["current_revision"] == first["current_revision"] + 1
    assert second["realized_profit_projection"]["realized_net_profit_quote"] == "0"
    assert second["realized_profit_projection"]["new_realized_profit_delta_quote"] == "0"
    assert second["realized_profit_projection"]["observation_can_change_current_closure_without_changing_realized_profit"] is True


def test_realized_profit_is_incremental_projection_of_new_closed_returns():
    start = derive_continuous_unified_closure(
        trading_receipt={
            "symbol": "BTC/USD",
            "quote_projections": [{"source_event_id": "q1", "best_bid": "100", "best_ask": "101"}],
            "temporal_closures": [_closed_trade("c1", "5")],
            "trading_projection_field": {"returned_natural_forms": []},
            "translational_truth_partition": {},
        }
    )
    assert start["realized_profit_projection"]["realized_net_profit_quote"] == "5"
    assert start["realized_profit_projection"]["new_realized_profit_delta_quote"] == "5"

    quote_only = derive_continuous_unified_closure(
        trading_receipt={
            "symbol": "BTC/USD",
            "quote_projections": [{"source_event_id": "q2", "best_bid": "104", "best_ask": "105"}],
            "temporal_closures": [],
            "trading_projection_field": {"returned_natural_forms": []},
            "translational_truth_partition": {},
        },
        prior_state=start,
    )
    assert quote_only["realized_profit_projection"]["realized_net_profit_quote"] == "5"
    assert quote_only["realized_profit_projection"]["new_realized_profit_delta_quote"] == "0"

    loss_return = derive_continuous_unified_closure(
        trading_receipt={
            "symbol": "BTC/USD",
            "temporal_closures": [_closed_trade("c2", "-2")],
            "trading_projection_field": {"returned_natural_forms": []},
            "translational_truth_partition": {},
        },
        prior_state=quote_only,
    )
    assert loss_return["realized_profit_projection"]["realized_net_profit_quote"] == "3"
    assert loss_return["realized_profit_projection"]["new_realized_profit_delta_quote"] == "-2"
    assert loss_return["realized_profit_projection"]["realized_profit_changes_only_on_new_cost_complete_temporal_closure"] is True


def test_replayed_closed_return_does_not_double_count_profit():
    first = derive_continuous_unified_closure(
        trading_receipt={
            "symbol": "BTC/USD",
            "temporal_closures": [_closed_trade("c1", "4")],
            "trading_projection_field": {"returned_natural_forms": []},
            "translational_truth_partition": {},
        }
    )
    replay = derive_continuous_unified_closure(
        trading_receipt={
            "symbol": "BTC/USD",
            "temporal_closures": [_closed_trade("c1", "4")],
            "trading_projection_field": {"returned_natural_forms": []},
            "translational_truth_partition": {},
        },
        prior_state=first,
    )
    assert replay["realized_profit_projection"]["realized_net_profit_quote"] == "4"
    assert replay["realized_profit_projection"]["new_realized_profit_delta_quote"] == "0"
    assert replay["realized_profit_projection"]["realized_profit_projection_count"] == 1


def test_missing_fee_keeps_profit_projection_open_until_same_relation_resolves():
    open_profit = derive_continuous_unified_closure(
        trading_receipt={
            "symbol": "BTC/USD",
            "temporal_closures": [_closed_trade("c1", "0", cost_complete=False)],
            "trading_projection_field": {"returned_natural_forms": []},
            "translational_truth_partition": {},
        }
    )
    assert open_profit["realized_profit_projection"]["status"] == "OPEN"
    assert open_profit["realized_profit_projection"]["realized_net_profit_quote"] == "0"
    assert "c1" in open_profit["realized_profit_projection"]["open_net_profit_temporal_closure_ids"]

    resolved = derive_continuous_unified_closure(
        trading_receipt={
            "symbol": "BTC/USD",
            "temporal_closures": [_closed_trade("c1", "1.25", cost_complete=True)],
            "trading_projection_field": {"returned_natural_forms": []},
            "translational_truth_partition": {},
        },
        prior_state=open_profit,
    )
    assert resolved["realized_profit_projection"]["status"] == "WITNESSED"
    assert resolved["realized_profit_projection"]["realized_net_profit_quote"] == "1.25"
    assert resolved["realized_profit_projection"]["new_realized_profit_delta_quote"] == "1.25"
    assert resolved["realized_profit_projection"]["open_net_profit_temporal_closure_ids"] == []
