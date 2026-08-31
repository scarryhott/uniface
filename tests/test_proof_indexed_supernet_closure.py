from copy import deepcopy

from closure_supernet.closure_only_interface import CLOSURE_ONLY_SUPERNET_HTML
from closure_supernet.closure_ui_contract import (
    derive_open_ui_contract,
    validate_ui_contract,
)
from closure_supernet.formal_proof_index import (
    REQUIRED_CORE_MODULES,
    derive_formal_proof_index,
    validate_formal_proof_index,
)
from closure_supernet.natural_form_atlas import derive_versioned_natural_form_atlas
from closure_supernet.supernet_closure_certificate import (
    derive_supernet_closure_certificate,
    validate_supernet_closure_certificate,
)


def empty_atlas(**kwargs):
    return derive_versioned_natural_form_atlas(
        truth_derivation={},
        interactive_translation={},
        active_perspective_id="perspective:test",
        active_reading={},
        **kwargs,
    )


def test_known_forms_and_formal_core_close_without_archive_gate():
    atlas = empty_atlas()
    proof_index = derive_formal_proof_index(atlas)
    certificate = derive_supernet_closure_certificate(
        atlas=atlas,
        formal_proof_index=proof_index,
    )

    assert proof_index["proof_index_closed"] is True
    assert proof_index["required_core_modules_present"] is True
    assert set(REQUIRED_CORE_MODULES).issubset(
        {proof["module"] for proof in proof_index["proofs"]}
    )
    assert proof_index["unresolved_chart_names"] == []
    assert all(
        proof["cross_form_equality_authored"] is False
        and proof["source_verified_by_runtime"] is False
        for proof in proof_index["proofs"]
    )

    assert certificate["status"] == "WITNESSED"
    assert certificate["supernet_closed"] is True
    assert certificate["missing_known_chart_ids"] == []
    assert certificate["missing_known_families"] == []
    assert certificate["archive_audit_required_for_supernet_closure"] is False
    assert certificate["archive_audit_is_diagnostic_only"] is True
    assert certificate["open_relations_are_part_of_closure"] is True
    assert certificate["open_relation_breaks_supernet_closure"] is False
    assert certificate["existence_closed"] is False
    assert certificate["dialectic_continuation_status"] == "OPEN"
    assert all(certificate["checks"].values())
    assert validate_formal_proof_index(proof_index, atlas=atlas)["valid"] is True
    assert validate_supernet_closure_certificate(
        certificate,
        atlas=atlas,
        formal_proof_index=proof_index,
    )["valid"] is True


def test_open_cross_form_translation_is_inside_closure_not_missing():
    atlas = empty_atlas(
        additional_translation_sources=(
            {
                "atlas_translations": [
                    {
                        "source_chart_id": "nf:triangle-time:v1",
                        "target_chart_id": "nf:checker-grid:v1",
                        "returned": False,
                        "source_preserved": False,
                        "closure_commutes": False,
                        "return_preserved": False,
                        "source_return_ids": [],
                    }
                ]
            },
        )
    )
    proof_index = derive_formal_proof_index(atlas)
    certificate = derive_supernet_closure_certificate(
        atlas=atlas,
        formal_proof_index=proof_index,
    )

    assert certificate["supernet_closed"] is True
    assert certificate["relation_witnesses"]["open_translation_ids"]
    assert certificate["relation_witnesses"][
        "open_relations_executing_as_equality"
    ] == []
    assert certificate["checks"]["every_unwitnessed_relation_remains_open"] is True


def test_returned_cross_form_translation_remains_the_runtime_equality_authority():
    atlas = empty_atlas(
        additional_translation_sources=(
            {
                "atlas_translations": [
                    {
                        "source_chart_id": "nf:triangle-time:v1",
                        "target_chart_id": "nf:checker-grid:v1",
                        "returned": True,
                        "source_preserved": True,
                        "closure_commutes": True,
                        "return_preserved": True,
                        "source_return_ids": ["return:triangle-checker"],
                        "return_witness_id": "witness:triangle-checker",
                    }
                ]
            },
        )
    )
    proof_index = derive_formal_proof_index(atlas)
    certificate = derive_supernet_closure_certificate(
        atlas=atlas,
        formal_proof_index=proof_index,
    )

    assert certificate["supernet_closed"] is True
    assert certificate["relation_witnesses"]["witnessed_nonidentity_translation_ids"]
    assert certificate["relation_witnesses"][
        "invalid_witnessed_translation_ids"
    ] == []
    assert certificate["checks"][
        "every_asserted_nonidentity_equality_return_witnessed"
    ] is True


def test_removing_a_known_form_opens_the_supernet_certificate():
    atlas = empty_atlas()
    atlas = deepcopy(atlas)
    atlas["charts"] = [
        chart for chart in atlas["charts"] if chart["id"] != "nf:triangle-time:v1"
    ]
    proof_index = derive_formal_proof_index(atlas)
    certificate = derive_supernet_closure_certificate(
        atlas=atlas,
        formal_proof_index=proof_index,
    )

    assert certificate["supernet_closed"] is False
    assert "nf:triangle-time:v1" in certificate["missing_known_chart_ids"]
    assert certificate["checks"]["all_known_natural_forms_retained"] is False


def test_open_ui_is_architecturally_closed_while_relation_remains_open():
    contract = derive_open_ui_contract(perspective_id="perspective:test")
    validation = validate_ui_contract(contract)

    assert contract["status"] == "OPEN_SOURCE_BOUNDARY"
    assert contract["supernet_closure_certificate"]["supernet_closed"] is True
    assert contract["supernet_closure_certificate"][
        "complete_does_not_mean_every_open_relation_resolved"
    ] is True
    assert contract["formal_proof_index"]["proof_index_closed"] is True
    assert contract["atlas_semantics"]["archive_audit_gates_supernet_closure"] is False
    assert validation["valid"] is True
    assert validation["supernet_closed"] is True
    assert validation["formal_proof_index_valid"] is True
    assert validation["supernet_closure_certificate_valid"] is True


def test_browser_requires_the_proof_indexed_closure_certificate():
    page = CLOSURE_ONLY_SUPERNET_HTML
    assert "SUPERNET-FORMAL-PROOF-INDEX" in page
    assert "SUPERNET-PROOF-INDEXED-CLOSURE" in page
    assert "archive_audit_required_for_supernet_closure" in page
    assert "open_relations_are_part_of_closure" in page
    assert "formalProofIndexId" in page
    assert "supernetClosureCertificateId" in page
    assert "supernetClosed" in page
