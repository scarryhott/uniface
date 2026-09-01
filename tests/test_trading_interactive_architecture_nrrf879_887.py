from closure_supernet.trading_interactive_architecture_nrrf879_887 import derive_interactive_trading_architecture


def test_compatibility_surface_is_continuous_not_staged():
    trading = {
        "symbol": "BTC/USD",
        "quote_projections": [{"status": "WITNESSED", "best_bid": "100", "best_ask": "101"}],
        "temporal_closures": [],
        "trading_projection_field": {"returned_natural_forms": []},
        "translational_truth_partition": {},
    }
    result = derive_interactive_trading_architecture(trading_receipt=trading)
    assert result["status"] == "WITNESSED"
    assert result["observation_and_trading_are_translation_equal_readings"] is True
    assert result["stage_gate_present"] is False
    assert result["separate_observation_pipeline_present"] is False
    assert result["open_queue_present"] is False
    assert "stages" not in result


def test_compatibility_surface_keeps_open_as_current_boundary_only():
    trading = {
        "symbol": "BTC/USD",
        "quote_projections": [{"status": "WITNESSED", "best_bid": "100", "best_ask": "101"}],
        "temporal_closures": [],
        "trading_projection_field": {"returned_natural_forms": []},
        "translational_truth_partition": {},
    }
    result = derive_interactive_trading_architecture(trading_receipt=trading)
    assert result["open_boundary"]["is_current_boundary_only"] is True
    assert result["open_boundary"]["accumulates_prior_open_failures"] is False
    assert result["open_count_is_progress_metric"] is False
