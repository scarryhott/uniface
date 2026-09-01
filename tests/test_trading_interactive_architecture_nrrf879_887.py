from closure_supernet.trading_interactive_architecture_nrrf879_887 import derive_interactive_trading_architecture


def _returned(form_id, truth_id, return_ids, q=None):
    row = {
        "form_id": form_id,
        "closure_id": form_id,
        "closure_truth_id": truth_id,
        "return_ids": return_ids,
        "unitary_curvature": "0",
        "natural_profit": "0",
        "orientation": "FLAT",
        "returned_truth_member": True,
        "selected": True,
        "status": "WITNESSED",
    }
    if q is not None:
        row["closure_number"] = q
    return row


def test_public_environment_without_account_return_stays_open():
    trading = {
        "symbol": "BTC/USD",
        "source_event_ids": [],
        "temporal_closures": [],
        "trading_projection_field": {"returned_natural_forms": []},
        "translational_truth_partition": {},
        "sensor_returns": [],
    }
    result = derive_interactive_trading_architecture(trading_receipt=trading)
    assert result["status"] == "OPEN"
    assert result["stages"][0]["status"] == "WITNESSED"
    assert result["stages"][1]["status"] == "OPEN"
    assert result["public_quote_or_trade_can_author_inventory_return"] is False
    assert result["interaction_projection"]["status"] == "OPEN"


def test_returned_families_and_kernel_do_not_bypass_missing_authoritative_q():
    a1 = _returned("a1", "TA", ["r1"])
    b1 = _returned("b1", "TB", ["r2"])
    a2 = _returned("a2", "TA", ["r3"])
    b2 = _returned("b2", "TB", ["r4"])
    trading = {
        "symbol": "BTC/USD",
        "source_event_ids": ["s1", "s2", "s3", "s4"],
        "temporal_closures": [{"id": "c1"}],
        "trading_projection_field": {"returned_natural_forms": [a1, b1, a2, b2]},
        "translational_truth_partition": {"class_count": 2},
        "sensor_returns": [
            {"return_id": "r1", "natural_form_value": "1"},
            {"return_id": "r2", "natural_form_value": "-1"},
            {"return_id": "r3", "natural_form_value": "1"},
            {"return_id": "r4", "natural_form_value": "-1"},
        ],
    }
    result = derive_interactive_trading_architecture(trading_receipt=trading)
    stages = {row["stage"]: row["status"] for row in result["stages"]}
    assert stages["VERIFIED_RETURN"] == "WITNESSED"
    assert stages["TEMPORAL_CLOSURE"] == "WITNESSED"
    assert stages["TRANSLATION_FAMILY"] == "WITNESSED"
    assert stages["RETURNED_KERNEL_P"] == "WITNESSED"
    assert stages["CLOSURE_NUMBER_Q"] == "OPEN"
    assert stages["AI_DIFFUSION_PQ"] == "OPEN"
    assert result["candidate_fold_embedding"]["candidate_q_authors_truth"] is False
    assert result["interaction_projection"]["status"] == "OPEN"


def test_even_witnessed_q_and_diffusion_leave_action_projection_open():
    a1 = _returned("a1", "TA", ["r1"], "-1")
    b1 = _returned("b1", "TB", ["r2"], "1")
    a2 = _returned("a2", "TA", ["r3"], "-1")
    b2 = _returned("b2", "TB", ["r4"], "1")
    trading = {
        "symbol": "BTC/USD",
        "source_event_ids": ["s1", "s2", "s3", "s4"],
        "temporal_closures": [{"id": "c1"}],
        "trading_projection_field": {"returned_natural_forms": [a1, b1, a2, b2]},
        "translational_truth_partition": {"class_count": 2},
        "sensor_returns": [
            {"return_id": "r1", "natural_form_value": "1"},
            {"return_id": "r2", "natural_form_value": "-1"},
            {"return_id": "r3", "natural_form_value": "1"},
            {"return_id": "r4", "natural_form_value": "-1"},
        ],
    }
    result = derive_interactive_trading_architecture(trading_receipt=trading)
    stages = {row["stage"]: row["status"] for row in result["stages"]}
    assert stages["CLOSURE_NUMBER_Q"] == "WITNESSED"
    assert stages["RETURNED_KERNEL_P"] == "WITNESSED"
    assert stages["AI_DIFFUSION_PQ"] == "WITNESSED"
    assert stages["INTERACTION_PROJECTION"] == "OPEN"
    assert result["interaction_projection"]["buy_or_sell_invented"] is False
    assert result["automatic_order_submission"] is False
