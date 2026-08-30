from __future__ import annotations

from closure_supernet.nrrf843_ui_mirror import derive_nrrf843_ui_receipt
from closure_supernet.translational_truth_axiometry import derive_closure


def admitted_truth(source: str, target: str) -> dict:
    return {
        "id": f"truth:{source}-{target}",
        "source": source,
        "target": target,
        "verdict": "TRUE",
        "visual_equation": {
            "id": f"equation:{source}-{target}",
            "source": source,
            "target": target,
            "equation": f"display({source}) = display({target})",
            "deterministic": True,
            "source_return_ids": [f"return:{source}", f"return:{target}"],
        },
        "compatible": {"witnessed": True},
        "closure_explicit": {"witnessed": True},
    }


def mirrored_derivation() -> dict:
    return derive_closure(
        [
            {
                "id": "garden-intent",
                "state": {
                    "perspective_id": "harry",
                    "exact_visual_form": "I want to start a community garden",
                },
                "source_return_ids": ["return:intent"],
            },
            {
                "id": "garden-project",
                "state": {
                    "perspective_id": "maya",
                    "exact_visual_form": "River Street community garden",
                },
                "source_return_ids": ["return:project"],
            },
            {
                "id": "tool-library",
                "state": {
                    "perspective_id": "steward",
                    "exact_visual_form": "neighbourhood tool library",
                },
                "source_return_ids": ["return:tools"],
            },
        ],
        [admitted_truth("garden-intent", "garden-project")],
    ).to_dict()


def test_ui_projection_itself_recomputes_nrrf840_closure() -> None:
    receipt = derive_nrrf843_ui_receipt(
        truth_derivation=mirrored_derivation()
    )

    assert receipt["status"] == "WITNESSED"
    assert receipt["supernet_open"] is False
    family = receipt["ui_family"]
    assert family["reading_source"] == "UI_VISUAL_METAPHOR_EQVGEN_FIBRES"
    assert family["external_closure_assumed"] is False
    assert family["external_truth_assumed"] is False
    assert set(family["perspective_ids"]) == {"harry", "maya", "steward"}

    mirror = receipt["translational_mirror"]
    assert mirror["witnessed"] is True
    assert mirror["translates_same_truth"] is True
    assert mirror["continuum_same_truth"] is True
    assert mirror["privileged_perspective_required"] is False
    assert all(
        item["faithful"]
        and item["same_truth"]
        and item["merges_states"] is False
        and item["splits_states"] is False
        for item in mirror["translations"]
    )

    closure = receipt["ui_closure"]
    assert closure["formula"] == "uiClosure(r,A) = r⁻¹(r(A))"
    assert closure["closure_falls_out_from_ui_projection"] is True
    assert closure["projection_closure_matches_nrrf840"] is True
    assert closure["external_closure_used"] is False
    assert all(closure["properties"].values())
    assert closure["same_carrier_different_closure_witness"][
        "different_closure"
    ] is True
    assert receipt["truth_constraint_location"]["located"] is True


def test_non_mirror_ui_keeps_supernet_open_without_fallback() -> None:
    derivation = mirrored_derivation()
    states = [item["id"] for item in derivation["visual_existence"]["forms"]]
    receipt = derive_nrrf843_ui_receipt(
        truth_derivation=derivation,
        perspective_readings={
            "identity-view": {state: state for state in states},
            "blind-view": {state: "one" for state in states},
        },
    )

    assert receipt["status"] == "OPEN_NON_MIRROR_UI"
    assert receipt["supernet_open"] is True
    assert receipt["translational_mirror"]["witnessed"] is False
    assert receipt["truth_constraint_location"]["located"] is False
    assert receipt["truth_constraint_location"]["outside_truth_constraint"] is None
    assert receipt["claims"]["outside_semantic_ontology"] is False


def test_no_perspective_has_no_distinction_and_supernet_is_open() -> None:
    derivation = derive_closure(["a", "b"], []).to_dict()
    receipt = derive_nrrf843_ui_receipt(truth_derivation=derivation)

    assert receipt["status"] == "OPEN_NO_PERSPECTIVE"
    assert receipt["supernet_open"] is True
    assert receipt["ui_family"]["perspective_ids"] == []
    boundary = receipt["no_perspective_boundary"]
    assert boundary["no_perspectives_no_distinction"] is True
    assert len(set(boundary["joint_reading"].values())) == 1
    assert boundary["distinguishable_pairs"] == []


def test_thought_is_eqvgen_of_displayed_metaphor() -> None:
    receipt = derive_nrrf843_ui_receipt(
        truth_derivation=mirrored_derivation()
    )
    thought = receipt["thought"]

    assert thought["construction"] == "RELATION_EQVGEN_OF_VISUAL_METAPHOR"
    assert thought["contains_metaphor"] is True
    assert thought["reflexive"] is True
    assert thought["symmetric"] is True
    assert thought["transitive"] is True
    assert thought["least_closed_relation_computed"] is True
    assert thought["adds_relations_genuinely"] is True
    assert thought["thought_equals_visualization_equality"] is True
    assert thought["one_thought_across_perspectives"] is True


def test_valuation_is_admissible_exactly_when_it_factors_through_ui() -> None:
    derivation = mirrored_derivation()
    equal_price = derive_nrrf843_ui_receipt(
        truth_derivation=derivation,
        valuation_by_state={
            "garden-intent": 12,
            "garden-project": 12,
            "tool-library": 5,
        },
    )["valuation"]
    assert equal_price["status"] == "ADMISSIBLE"
    assert equal_price["admissible"] is True
    assert equal_price["perspective_independent_under_mirror"] is True
    assert equal_price["price_issued"] is False

    split_price_receipt = derive_nrrf843_ui_receipt(
        truth_derivation=derivation,
        valuation_by_state={
            "garden-intent": 12,
            "garden-project": 13,
            "tool-library": 5,
        },
    )
    assert split_price_receipt["valuation"]["status"] == (
        "REJECTED_BY_UI_TRUTH"
    )
    assert split_price_receipt["valuation"]["admissible"] is False
    assert split_price_receipt["unpriced_example"]["admissible"] is False


def test_blind_mirror_and_resolution_are_independent() -> None:
    derivation = derive_closure(
        [
            {"id": "a", "state": {"perspective_id": "p"}},
            {"id": "b", "state": {"perspective_id": "q"}},
        ],
        [admitted_truth("a", "b")],
    ).to_dict()
    receipt = derive_nrrf843_ui_receipt(truth_derivation=derivation)

    assert receipt["translational_mirror"]["witnessed"] is True
    assert receipt["resolution"]["nontrivial_or_singleton"] is False
    assert receipt["resolution"]["mirror_and_resolution_are_independent"] is True
    assert receipt["resolution"]["blind_ui_can_be_mirror"] is True
    assert receipt["resolution"]["blind_ui_constrains_nothing_nontrivial"] is True
