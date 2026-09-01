from closure_supernet.trading_returned_family_kernel_nrrf887_attempt import (
    derive_candidate_fold_embedding,
    derive_returned_family_kernel,
)


def _families():
    return {
        "families": [
            {"family_id": "F-A", "closure_truth_id": "T-A", "member_ids": ["a1"]},
            {"family_id": "F-B", "closure_truth_id": "T-B", "member_ids": ["b1"]},
        ]
    }


def test_returned_history_derives_exact_stochastic_kernel_without_profit_or_forecast():
    field = {
        "returned_natural_forms": [
            {"form_id": "a1", "closure_truth_id": "T-A", "returned_truth_member": True},
            {"form_id": "b1", "closure_truth_id": "T-B", "returned_truth_member": True},
            {"form_id": "a2", "closure_truth_id": "T-A", "returned_truth_member": True},
            {"form_id": "b2", "closure_truth_id": "T-B", "returned_truth_member": True},
        ]
    }
    receipt = derive_returned_family_kernel(
        translation_family_receipt=_families(),
        natural_form_field=field,
    )
    assert receipt["status"] == "WITNESSED"
    kernel = receipt["returned_diffusion_kernel"]
    assert kernel["locality_ids"] == ["F-A", "F-B"]
    assert kernel["matrix"] == [["0", "1"], ["1", "0"]]
    assert kernel["uses_future_profit"] is False
    assert kernel["uses_expected_profit"] is False
    assert kernel["uses_forecast"] is False
    assert receipt["profit_authors_kernel"] is False
    assert receipt["absence_of_outgoing_evidence_creates_self_loop"] is False


def test_missing_outgoing_return_evidence_stays_open_instead_of_inventing_self_loop():
    field = {
        "returned_natural_forms": [
            {"form_id": "a1", "closure_truth_id": "T-A", "returned_truth_member": True},
            {"form_id": "b1", "closure_truth_id": "T-B", "returned_truth_member": True},
        ]
    }
    receipt = derive_returned_family_kernel(
        translation_family_receipt=_families(),
        natural_form_field=field,
    )
    assert receipt["status"] == "OPEN"
    assert receipt["returned_diffusion_kernel"] is None
    assert receipt["families_without_returned_outgoing_transition"] == ["F-B"]


def test_candidate_q_is_exact_family_probe_but_never_authoritative():
    families = {
        "families": [
            {"family_id": "F-A", "closure_truth_id": "T-A", "member_ids": ["a1"]},
        ]
    }
    field = {
        "returned_natural_forms": [
            {
                "form_id": "a1",
                "closure_truth_id": "T-A",
                "returned_truth_member": True,
                "return_ids": ["e1", "e2"],
                "unitary_curvature": "1/2",
            }
        ]
    }
    closure = {
        "sensor_returns": [
            {"return_id": "e1", "natural_form_value": "1"},
            {"return_id": "e2", "natural_form_value": "-1/2"},
        ]
    }
    receipt = derive_candidate_fold_embedding(
        translation_family_receipt=families,
        natural_form_field=field,
        natural_closure=closure,
    )
    assert receipt["status"] == "OPEN"
    row = receipt["candidate_families"][0]
    assert row["candidate_is_family_constant"] is True
    assert row["family_closure_number_candidate"] == "1/3"
    member = row["members"][0]
    assert member["curvature_extension_candidate"] == "1/2"
    assert member["total_variation_rotation_candidate"] == "3/2"
    assert member["inside_unit_interval"] is True
    assert receipt["candidate_feeds_authoritative_diffusion"] is False
    assert receipt["nrrf887_slide_translation_law_proved_for_embedding"] is False
    assert receipt["nrrf887_hodge_inversion_law_proved_for_embedding"] is False
    assert receipt["profit_used_as_input"] is False


def test_candidate_q_rejects_nonconstant_family_embedding():
    families = {
        "families": [
            {"family_id": "F-A", "closure_truth_id": "T-A", "member_ids": ["a1", "a2"]},
        ]
    }
    field = {
        "returned_natural_forms": [
            {"form_id": "a1", "closure_truth_id": "T-A", "returned_truth_member": True,
             "return_ids": ["e1", "e2"], "unitary_curvature": "1/2"},
            {"form_id": "a2", "closure_truth_id": "T-A", "returned_truth_member": True,
             "return_ids": ["e3", "e4"], "unitary_curvature": "1/2"},
        ]
    }
    closure = {
        "sensor_returns": [
            {"return_id": "e1", "natural_form_value": "1"},
            {"return_id": "e2", "natural_form_value": "-1/2"},
            {"return_id": "e3", "natural_form_value": "3/4"},
            {"return_id": "e4", "natural_form_value": "-1/4"},
        ]
    }
    receipt = derive_candidate_fold_embedding(
        translation_family_receipt=families,
        natural_form_field=field,
        natural_closure=closure,
    )
    row = receipt["candidate_families"][0]
    assert row["candidate_is_family_constant"] is False
    assert row["family_closure_number_candidate"] is None
    assert row["semantic_status"] == "OPEN"
