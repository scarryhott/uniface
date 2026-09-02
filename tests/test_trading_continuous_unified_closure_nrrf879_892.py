from closure_supernet.trading_continuous_unified_closure_nrrf879_892 import derive_continuous_unified_closure


def _returned(form_id, truth_id, q, horizon=3, size="10"):
    return {
        "form_id": form_id,
        "closure_id": form_id,
        "closure_truth_id": truth_id,
        "closure_number": q,
        "returned_truth_member": True,
        "selected": True,
        "status": "WITNESSED",
        "relative_hair_horizon": {"status": "WITNESSED", "horizon_return_steps": horizon},
        "relative_ball_size": {
            "status": "WITNESSED",
            "relative_ball_size": size,
            "relative_ball_size_unit": "USD-notional",
        },
    }


def test_nrrf892_removes_only_the_representation_bridge_open_boundary():
    a = _returned("a", "TA", "-1")
    b = _returned("b", "TB", "1")
    trading = {
        "symbol": "BTC/USD",
        "quote_projections": [{"source_event_id": "q1", "best_bid": "100", "best_ask": "101"}],
        "trading_projection_field": {"returned_natural_forms": [a, b]},
        "translational_truth_partition": {"class_count": 2},
        "returned_diffusion_kernel": {
            "returned": True,
            "locality_ids": [
                "translation-truth-family:placeholder-a",
                "translation-truth-family:placeholder-b",
            ],
            "matrix": [["1/2", "1/2"], ["1/2", "1/2"]],
            "uses_future_profit": False,
            "uses_expected_profit": False,
            "uses_forecast": False,
        },
        "temporal_closures": [],
    }
    # Family ids are content-derived, so obtain them once then re-run with the exact ids.
    first = derive_continuous_unified_closure(trading_receipt={**trading, "returned_diffusion_kernel": None})
    ids = [row["family_id"] for row in first["translation_families"]["families"]]
    trading["returned_diffusion_kernel"] = {
        "returned": True,
        "locality_ids": ids,
        "matrix": [["1/2", "1/2"], ["1/2", "1/2"]],
        "uses_future_profit": False,
        "uses_expected_profit": False,
        "uses_forecast": False,
    }
    result = derive_continuous_unified_closure(trading_receipt=trading)
    rendering = result["nrrf892_vision_crystal_market_rendering"]
    sides = {row["market_side"] for row in rendering["renderings"]}
    assert rendering["status"] == "WITNESSED"
    assert sides == {"BUY", "SELL"}
    assert "CLOSURE_SLIDE_TO_CONCRETE_MARKET_SIDE_BRIDGE_OPEN" not in result["open_boundary"]["unresolved_relations"]
    assert result["market_side_is_relative_visualization_of_translational_slide"] is True
    assert result["market_side_is_separate_semantic_bridge"] is False
