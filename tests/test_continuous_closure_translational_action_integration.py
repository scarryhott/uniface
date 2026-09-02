from closure_supernet.trading_continuous_unified_closure_nrrf879_887 import derive_continuous_unified_closure


def _form(form_id, truth_id, q, horizon, size):
    return {
        "form_id": form_id,
        "closure_id": form_id,
        "closure_truth_id": truth_id,
        "closure_number": q,
        "return_ids": [f"r-{form_id}"],
        "returned_truth_member": True,
        "selected": True,
        "status": "WITNESSED",
        "unitary_curvature": "0",
        "natural_profit": "0",
        "orientation": "FLAT",
        "relative_hair_horizon": {
            "status": "WITNESSED",
            "horizon_return_steps": horizon,
        },
        "relative_ball_size": {
            "status": "WITNESSED",
            "relative_ball_size": size,
            "relative_ball_size_unit": "USD-notional",
        },
    }


def test_continuous_closure_derives_action_as_same_current_translational_truth():
    forms = [
        _form("a1", "TA", "-1", 5, "8"),
        _form("b1", "TB", "1", 5, "8"),
        _form("a2", "TA", "-1", 5, "8"),
        _form("b2", "TB", "1", 5, "8"),
    ]
    trading = {
        "symbol": "BTC/USD",
        "quote_projections": [{"source_event_id": "q1", "best_bid": "100", "best_ask": "101"}],
        "temporal_closures": [],
        "trading_projection_field": {"returned_natural_forms": forms},
        "translational_truth_partition": {"class_count": 2},
        "sensor_returns": [
            {"return_id": "r-a1", "natural_form_value": "0"},
            {"return_id": "r-b1", "natural_form_value": "0"},
            {"return_id": "r-a2", "natural_form_value": "0"},
            {"return_id": "r-b2", "natural_form_value": "0"},
        ],
    }
    result = derive_continuous_unified_closure(trading_receipt=trading)
    action = result["translational_truth_action_field"]
    assert result["action_equation"] == "Delta_i=(P_t q_t)_i-q_(t,i)"
    assert result["action_is_unique_relative_slide_not_prediction"] is True
    assert action["status"] == "WITNESSED"
    assert action["action_count"] == 2
    deltas = sorted(row["unique_slide_amount"] for row in action["actions"])
    assert deltas == ["-2", "2"]
    assert all(row["relative_hair_horizon_return_steps"] == 5 for row in action["actions"])
    assert all(row["relative_ball_size"] == "8" for row in action["actions"])
    assert action["profit_authors_action"] is False
    assert action["forecast_authors_action"] is False
    assert action["family_selection_authors_action"] is False
    kinds = [row["kind"] for row in result["derived_relative_readings"]]
    assert "TRANSLATIONAL_TRUTH_ACTION_FIELD" in kinds
    assert result["derived_readings_do_not_increment_revision"] is True
