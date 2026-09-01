from closure_supernet.trading_vision_crystal_slide_nrrf892 import derive_nrrf892_market_rendering


def _action(fid, delta):
    return {
        "family_id": fid,
        "closure_truth_id": f"truth-{fid}",
        "status": "WITNESSED",
        "unique_slide_amount": str(delta),
    }


def test_positive_negative_zero_slides_render_in_signed_inventory_chart():
    result = derive_nrrf892_market_rendering(
        translational_action_field={
            "actions": [_action("A", 1), _action("B", -2), _action("C", 0)]
        },
        trading_receipt={"symbol": "BTC/USD"},
    )
    by_id = {row["family_id"]: row for row in result["renderings"]}
    assert result["status"] == "WITNESSED"
    assert by_id["A"]["market_side"] == "BUY"
    assert by_id["B"]["market_side"] == "SELL"
    assert by_id["C"]["market_side"] == "NOOP"
    assert by_id["A"]["market_side_is_canonical_chart_rendering_not_new_truth"] is True
    assert by_id["A"]["profit_used_to_render_market_side"] is False


def test_slide_is_rendered_as_nrrf892_horizontal_translation():
    result = derive_nrrf892_market_rendering(
        translational_action_field={"actions": [_action("A", "3/2")]},
        trading_receipt={"symbol": "BTC/USD"},
    )
    row = result["renderings"][0]
    assert row["vision_slide_vector"] == ["3/2", "0"]
    assert row["slide_is_closure_family_member"] is True
    assert row["slide_group_zero_comp_inverse"] is True
    assert row["vision_crystal_is_slide_orbit"] is True
    assert row["closure_family_conjugate_of_slide_is_translation"] is True


def test_non_single_market_chart_stays_open():
    result = derive_nrrf892_market_rendering(
        translational_action_field={"actions": [_action("A", 1)]},
        trading_receipt={"symbol": ""},
    )
    assert result["status"] == "OPEN"
    assert result["renderings"][0]["market_side"] is None
    assert "CANONICAL_SINGLE_MARKET_VISION_CHART_OPEN" in result["renderings"][0]["unresolved"]


def test_nrrf892_exact_vision_scale_boundary_is_exposed():
    result = derive_nrrf892_market_rendering(
        translational_action_field={"actions": [_action("A", 1)]},
        trading_receipt={"symbol": "BTC/USD"},
    )
    row = result["renderings"][0]
    assert row["allowed_vision_family_scales"] == ["1", "-1"]
    assert row["vision_scale_is_family_member_iff_scale_is_pm_one"] is True
    assert row["arbitrary_vision_redenomination_is_family_member"] is False
