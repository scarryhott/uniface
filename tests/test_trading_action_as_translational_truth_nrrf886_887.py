from closure_supernet.trading_action_as_translational_truth_nrrf886_887 import derive_translational_truth_action_field


def _family(fid, truth, q, horizon=3, size="10", unit="USD-notional"):
    member = {
        "form_id": f"{fid}-m1",
        "closure_truth_id": truth,
        "closure_number": q,
        "returned_truth_member": True,
        "selected": True,
        "relative_hair_horizon": {
            "status": "WITNESSED",
            "horizon_return_steps": horizon,
        },
        "relative_ball_size": {
            "status": "WITNESSED",
            "relative_ball_size": size,
            "relative_ball_size_unit": unit,
        },
    }
    return {
        "family_id": fid,
        "closure_truth_id": truth,
        "members": [member],
    }


def _diffusion(rows):
    return {
        "status": "WITNESSED",
        "closure_number_coordinates": [
            {"family_id": fid, "closure_number": q0} for fid, q0, _ in rows
        ],
        "diffused_readings": [
            {"family_id": fid, "before_closure_number": q0, "diffused_closure_number": q1}
            for fid, q0, q1 in rows
        ],
    }


def test_unique_slide_is_the_translational_action_field_without_profit_selector():
    families = {
        "families": [
            _family("A", "TA", "-1", horizon=4, size="12"),
            _family("B", "TB", "1", horizon=4, size="12"),
        ]
    }
    diffusion = _diffusion([
        ("A", "-1", "0"),
        ("B", "1", "0"),
    ])
    result = derive_translational_truth_action_field(
        translation_family_receipt=families,
        diffusion_receipt=diffusion,
    )
    by_id = {row["family_id"]: row for row in result["actions"]}
    assert result["status"] == "WITNESSED"
    assert result["equation"] == "Delta_i=(P_t q_t)_i-q_(t,i)"
    assert by_id["A"]["unique_slide_amount"] == "1"
    assert by_id["A"]["closure_number_orientation"] == "POSITIVE_SLIDE"
    assert by_id["B"]["unique_slide_amount"] == "-1"
    assert by_id["B"]["closure_number_orientation"] == "NEGATIVE_SLIDE"
    assert by_id["A"]["relative_hair_horizon_return_steps"] == 4
    assert by_id["A"]["relative_ball_size"] == "12"
    assert result["action_field_is_whole_translation_family_field"] is True
    assert result["profit_authors_action"] is False
    assert result["forecast_authors_action"] is False
    assert result["family_selection_authors_action"] is False


def test_common_slide_does_not_change_action_translation():
    families = {"families": [_family("A", "TA", "-1")]}
    base = derive_translational_truth_action_field(
        translation_family_receipt=families,
        diffusion_receipt=_diffusion([("A", "-1", "1/2")]),
    )
    shifted = derive_translational_truth_action_field(
        translation_family_receipt=families,
        diffusion_receipt=_diffusion([("A", "2", "7/2")]),
    )
    assert base["actions"][0]["unique_slide_amount"] == "3/2"
    assert shifted["actions"][0]["unique_slide_amount"] == "3/2"
    assert base["global_slide_equivariance"].startswith("Delta(q+c*1)")


def test_family_horizon_disagreement_stays_open_instead_of_selecting_one():
    family = _family("A", "TA", "0")
    second = dict(family["members"][0])
    second["form_id"] = "A-m2"
    second["relative_hair_horizon"] = {"status": "WITNESSED", "horizon_return_steps": 7}
    family["members"].append(second)
    result = derive_translational_truth_action_field(
        translation_family_receipt={"families": [family]},
        diffusion_receipt=_diffusion([("A", "0", "1/2")]),
    )
    action = result["actions"][0]
    assert action["status"] == "OPEN"
    assert "RELATIVE_HAIR_HORIZON_NOT_FAMILY_INVARIANT" in action["unresolved_coordinates"]
    assert action["action_selector_used"] is False


def test_family_ball_size_disagreement_stays_open_instead_of_min_or_max_selection():
    family = _family("A", "TA", "0", size="10")
    second = dict(family["members"][0])
    second["form_id"] = "A-m2"
    second["relative_ball_size"] = {
        "status": "WITNESSED",
        "relative_ball_size": "20",
        "relative_ball_size_unit": "USD-notional",
    }
    family["members"].append(second)
    result = derive_translational_truth_action_field(
        translation_family_receipt={"families": [family]},
        diffusion_receipt=_diffusion([("A", "0", "1/2")]),
    )
    action = result["actions"][0]
    assert action["status"] == "OPEN"
    assert "RELATIVE_BALL_SIZE_NOT_FAMILY_INVARIANT" in action["unresolved_coordinates"]
    assert action["relative_ball_size"] is None


def test_identity_slide_is_noop_and_needs_no_buy_sell_bridge():
    result = derive_translational_truth_action_field(
        translation_family_receipt={"families": [_family("A", "TA", "1/3")]},
        diffusion_receipt=_diffusion([("A", "1/3", "1/3")]),
    )
    action = result["actions"][0]
    assert action["kind"] == "IDENTITY_TRANSLATION_NOOP"
    assert action["unique_slide_amount"] == "0"
    assert action["market_side_status"] == "WITNESSED"
    assert action["market_side"] is None


def test_nonzero_slide_does_not_invent_buy_or_sell():
    result = derive_translational_truth_action_field(
        translation_family_receipt={"families": [_family("A", "TA", "0")]},
        diffusion_receipt=_diffusion([("A", "0", "1")]),
    )
    action = result["actions"][0]
    assert action["status"] == "WITNESSED"
    assert action["closure_number_orientation"] == "POSITIVE_SLIDE"
    assert action["market_side"] is None
    assert action["market_side_status"] == "OPEN"
    assert result["market_side_bridge_complete"] is False
    assert action["profit_used_to_derive_action"] is False
