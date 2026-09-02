from closure_supernet.trading_ai_diffusion_nrrf887 import derive_nrrf887_diffusion


def _family(fid, truth, q=None, extension=None, rotation=None):
    member = {
        "form_id": f"form-{fid}",
        "closure_truth_id": truth,
        "returned_truth_member": True,
        "selected": True,
    }
    if q is not None:
        member["closure_number"] = q
    if extension is not None:
        member["extension"] = extension
    if rotation is not None:
        member["rotation"] = rotation
    return {
        "family_id": fid,
        "closure_truth_id": truth,
        "members": [member],
        "natural_form_centre": {},
    }


def _receipt(*families):
    return {"families": list(families), "family_count": len(families)}


def _kernel(ids, matrix, **extra):
    return {"returned": True, "locality_ids": list(ids), "matrix": matrix, **extra}


def test_exact_rational_diffusion_contracts_oscillation_and_stays_in_range():
    families = _receipt(_family("a", "ta", "-1"), _family("b", "tb", "1"))
    result = derive_nrrf887_diffusion(
        translation_family_receipt=families,
        returned_diffusion_kernel=_kernel(
            ["a", "b"],
            [["3/4", "1/4"], ["1/4", "3/4"]],
        ),
    )

    assert result["status"] == "WITNESSED"
    assert result["oscillation_before"] == "2"
    assert result["oscillation_after"] == "1"
    assert result["oscillation_nonincreasing"] is True
    assert [x["diffused_closure_number"] for x in result["diffused_readings"]] == ["-1/2", "1/2"]
    assert all(x["inside_returned_range"] for x in result["diffused_readings"])
    assert result["closure_preserved_if_all_local_closed"] is True


def test_consensus_is_relative_global_intent_when_returned_step_is_constant():
    families = _receipt(_family("a", "ta", "-1"), _family("b", "tb", "1"))
    result = derive_nrrf887_diffusion(
        translation_family_receipt=families,
        returned_diffusion_kernel=_kernel(
            ["a", "b"],
            [["1/2", "1/2"], ["1/2", "1/2"]],
        ),
    )

    assert result["global_intent"]["status"] == "WITNESSED"
    assert result["global_intent"]["closure_number"] == "0"
    assert result["global_intent"]["actual_limit_claimed"] is False


def test_constant_reading_is_fixed():
    families = _receipt(_family("a", "ta", "2/3"), _family("b", "tb", "2/3"))
    result = derive_nrrf887_diffusion(
        translation_family_receipt=families,
        returned_diffusion_kernel=_kernel(
            ["a", "b"],
            [["2/3", "1/3"], ["1/5", "4/5"]],
        ),
    )
    assert result["constant_reading_fixed"] is True
    assert [x["diffused_closure_number"] for x in result["diffused_readings"]] == ["2/3", "2/3"]


def test_translation_equivariance_holds_for_same_returned_kernel():
    kernel = _kernel(["a", "b"], [["3/4", "1/4"], ["1/4", "3/4"]])
    base = derive_nrrf887_diffusion(
        translation_family_receipt=_receipt(_family("a", "ta", "-1"), _family("b", "tb", "1")),
        returned_diffusion_kernel=kernel,
    )
    shifted = derive_nrrf887_diffusion(
        translation_family_receipt=_receipt(_family("a", "ta", "2"), _family("b", "tb", "4")),
        returned_diffusion_kernel=kernel,
    )
    assert [x["diffused_closure_number"] for x in base["diffused_readings"]] == ["-1/2", "1/2"]
    assert [x["diffused_closure_number"] for x in shifted["diffused_readings"]] == ["5/2", "7/2"]


def test_extension_per_rotation_is_exact_closure_number_coordinate():
    result = derive_nrrf887_diffusion(
        translation_family_receipt=_receipt(_family("a", "ta", extension="3", rotation="4")),
        returned_diffusion_kernel=_kernel(["a"], [["1"]]),
    )
    assert result["status"] == "WITNESSED"
    coordinate = result["closure_number_coordinates"][0]
    assert coordinate["closure_number"] == "3/4"
    assert coordinate["closure_number_provenance"] == "COMMON_RETURNED_MEMBER_CLOSURE_NUMBER"
    assert coordinate["ball_hair_closed"] is True


def test_missing_closure_number_or_kernel_remains_open():
    no_q = derive_nrrf887_diffusion(
        translation_family_receipt=_receipt(_family("a", "ta")),
        returned_diffusion_kernel=_kernel(["a"], [["1"]]),
    )
    assert no_q["status"] == "OPEN"
    assert no_q["unresolved_coordinate_family_ids"] == ["a"]

    no_kernel = derive_nrrf887_diffusion(
        translation_family_receipt=_receipt(_family("a", "ta", "1/2")),
        returned_diffusion_kernel=None,
    )
    assert no_kernel["status"] == "OPEN"
    assert "NO_RETURNED_DIFFUSION_KERNEL" in no_kernel["kernel_failures"]


def test_non_stochastic_or_profit_smuggling_kernel_fails_open():
    families = _receipt(_family("a", "ta", "0"), _family("b", "tb", "1"))
    bad_row = derive_nrrf887_diffusion(
        translation_family_receipt=families,
        returned_diffusion_kernel=_kernel(["a", "b"], [["1", "1"], ["0", "1"]]),
    )
    assert bad_row["status"] == "OPEN"
    assert "KERNEL_ROW_NOT_STOCHASTIC" in bad_row["kernel_failures"]

    profit_kernel = derive_nrrf887_diffusion(
        translation_family_receipt=families,
        returned_diffusion_kernel=_kernel(
            ["a", "b"], [["1", "0"], ["0", "1"]], uses_expected_profit=True
        ),
    )
    assert profit_kernel["status"] == "OPEN"
    assert "KERNEL_SMUGGLES_PROFIT_OR_FORECAST" in profit_kernel["kernel_failures"]
    assert profit_kernel["profit_authors_diffusion"] is False
