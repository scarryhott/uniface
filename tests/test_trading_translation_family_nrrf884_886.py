from closure_supernet.trading_translation_family_nrrf884_886 import derive_translation_families


def returned(form_id, truth_id, profit, orientation, *, signature=("A", "B")):
    return {
        "form_id": form_id,
        "kind": "RETURNED_CLOSED_NATURAL_FORM",
        "status": "WITNESSED",
        "closure_truth_id": truth_id,
        "directed_relation_signature": list(signature),
        "unitary_curvature": str(-profit),
        "natural_profit": str(profit),
        "orientation": orientation,
        "returned_truth_member": True,
        "selected": True,
    }


def test_same_truth_presentations_form_one_family_and_all_remain_selected():
    field = {
        "returned_natural_forms": [
            returned("a", "truth-1", 1, "PROFITABLE"),
            returned("b", "truth-1", 1, "PROFITABLE"),
        ]
    }
    receipt = derive_translation_families(natural_form_field=field)

    assert receipt["family_count"] == 1
    family = receipt["families"][0]
    assert family["member_count"] == 2
    assert family["all_members_selected"] is True
    assert family["family_wide_selection"] is True
    assert family["same_class_return_remains_family_member"] is True
    assert receipt["same_tt_class_means_do_not_trade"] is False


def test_support_novelty_is_not_family_membership_or_selection_rule():
    field = {
        "returned_natural_forms": [
            returned("old-return", "truth-1", -1, "COSTLY"),
            returned("new-return", "truth-2", 2, "PROFITABLE"),
        ]
    }
    receipt = derive_translation_families(
        natural_form_field=field,
        translational_truth_partition={"class_count": 2, "learned_profit": True},
    )

    assert receipt["family_count"] == 2
    assert receipt["family_is_support_novelty"] is False
    assert receipt["new_tt_class_means_trade"] is False
    assert receipt["same_tt_class_means_do_not_trade"] is False
    assert receipt["support_novelty_is_learning_coordinate_only"] is True


def test_profitability_does_not_define_translation_family():
    field = {
        "returned_natural_forms": [
            returned("costly", "cost-truth", -3, "COSTLY"),
            returned("profitable", "profit-truth", 4, "PROFITABLE"),
        ]
    }
    receipt = derive_translation_families(natural_form_field=field)

    assert receipt["family_count"] == 2
    assert receipt["profitability_is_property_not_family_definition"] is True
    for family in receipt["families"]:
        assert family["profitability_authors_membership"] is False
        assert family["profitable_and_costly_are_possible_properties_of_truth"] is True


def test_fixed_price_no_profit_hypothesis_cannot_author_unity():
    field = {
        "returned_natural_forms": [returned("a", "truth-1", -1, "COSTLY")]
    }
    receipt = derive_translation_families(natural_form_field=field)

    assert receipt["fixed_price_subset_is_maximally_unified"] is False
    assert receipt["breaking_fixed_price_hypothesis_means_escape_from_closure"] is False
    assert receipt["fixed_price_no_profit_is_empirical_hypothesis_only"] is True
    family = receipt["families"][0]
    assert family["fixed_price_no_profit_hypothesis_required_for_membership"] is False
    assert family["fixed_price_no_profit_hypothesis_authors_unity"] is False


def test_family_centre_is_common_truth_reading_not_preferred_member():
    field = {
        "returned_natural_forms": [
            returned("z-member", "truth-1", 5, "PROFITABLE", signature=("X", "Y")),
            returned("a-member", "truth-1", 5, "PROFITABLE", signature=("X", "Y")),
        ]
    }
    family = derive_translation_families(natural_form_field=field)["families"][0]

    assert family["member_ids"] == ["a-member", "z-member"]
    assert family["natural_form_centre"]["closure_truth_id"] == "truth-1"
    assert family["natural_form_centre"]["natural_profit"] == "5"
    assert family["crystal_ball_current"]["centre_is_family_invariant_not_member_choice"] is True


def test_missing_truth_identity_stays_open_instead_of_guessing_family():
    bad = returned("a", "", 1, "PROFITABLE")
    receipt = derive_translation_families(natural_form_field={"returned_natural_forms": [bad]})

    assert receipt["status"] == "OPEN"
    assert receipt["unresolved_member_count"] == 1
    assert receipt["family_count"] == 0
