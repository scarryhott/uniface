from __future__ import annotations

from closure_supernet.closure_only_interface import CLOSURE_ONLY_SUPERNET_HTML
from closure_supernet.closure_ui_contract import derive_open_ui_contract, validate_ui_contract
from closure_supernet.natural_form_atlas import (
    HAIR_VERSIONS,
    derive_versioned_natural_form_atlas,
    historical_charts,
    validate_versioned_natural_form_atlas,
)


def _atlas(**overrides):
    arguments = {
        "truth_derivation": {},
        "interactive_translation": {},
        "active_perspective_id": "perspective:test",
        "active_reading": {},
    }
    arguments.update(overrides)
    return derive_versioned_natural_form_atlas(**arguments)


def test_historical_atlas_retains_forms_without_ball_reduction():
    atlas = _atlas()
    validation = validate_versioned_natural_form_atlas(atlas)

    assert validation["valid"] is True
    assert atlas["closure_ball_is_one_chart"] is True
    assert atlas["closure_ball_is_master_container"] is False
    assert atlas["visual_resemblance_can_witness_equality"] is False
    assert atlas["shared_name_can_witness_equality"] is False
    assert atlas["forms_may_disappear_without_returned_translation"] is False

    names = {chart["name"] for chart in atlas["charts"]}
    for required in {
        "0↔infinity interbound",
        "triangle time",
        "Mobius strip",
        "fractal hypotenuse",
        "closure ball",
        "mirror ellipse",
        "sheaf",
        "unitary curvature",
        "Black Mirror",
        "Slearn",
        "token as returned curvature",
        "QG loop",
    }:
        assert required in names


def test_hair_semantic_lineage_is_versioned_and_not_silently_equal():
    atlas = _atlas()
    hair = sorted(
        (chart for chart in atlas["charts"] if chart["name"] == "hair"),
        key=lambda chart: chart["version"],
    )
    assert len(hair) == len(HAIR_VERSIONS)
    assert [chart["version"] for chart in hair] == [1, 2, 3, 4, 5]
    assert len({chart["semantic_role"] for chart in hair}) == 5

    lineage = [
        relation
        for relation in atlas["translations"]
        if relation["kind"] == "HISTORICAL_SEMANTIC_LINEAGE"
    ]
    assert lineage
    assert all(relation["status"] == "OPEN" for relation in lineage)
    assert all(relation["source_return_ids"] == [] for relation in lineage)


def test_cross_form_translation_requires_source_preserving_return():
    source = "nf:hair:v1"
    target = "nf:hair:v2"
    open_atlas = _atlas(
        truth_derivation={
            "atlas_translations": [
                {
                    "source_chart_id": source,
                    "target_chart_id": target,
                    "returned": False,
                    "source_preserved": False,
                    "closure_commutes": False,
                    "return_preserved": False,
                }
            ]
        }
    )
    open_relation = next(
        relation
        for relation in open_atlas["translations"]
        if relation["kind"] == "EXPLICIT_ATLAS_TRANSLATION"
    )
    assert open_relation["status"] == "OPEN"

    witnessed = _atlas(
        truth_derivation={
            "atlas_translations": [
                {
                    "source_chart_id": source,
                    "target_chart_id": target,
                    "returned": True,
                    "source_preserved": True,
                    "closure_commutes": True,
                    "return_preserved": True,
                    "source_return_ids": ["return:hair-lineage"],
                }
            ]
        }
    )
    witnessed_relation = next(
        relation
        for relation in witnessed["translations"]
        if relation["kind"] == "EXPLICIT_ATLAS_TRANSLATION"
    )
    assert witnessed_relation["status"] == "WITNESSED"
    assert witnessed_relation["source_return_ids"] == ["return:hair-lineage"]
    assert validate_versioned_natural_form_atlas(witnessed)["valid"] is True


def test_runtime_forms_are_compatible_subatlas_without_absorbing_history():
    atlas = _atlas(
        truth_derivation={
            "natural_forms": [
                {"id": "nf-a", "members": ["a"]},
                {"id": "nf-b", "members": ["b"]},
            ]
        },
        active_reading={"a": "display-a", "b": "display-b"},
        interactive_translation={
            "interactions": [
                {
                    "id": "a-to-b",
                    "observed_source_id": "a",
                    "observed_target_id": "b",
                    "translation_relation_witnessed": False,
                    "closure_preserved_after_translation": False,
                    "source_return_ids": ["return:a", "return:b"],
                }
            ]
        },
    )
    compatible = set(atlas["compatible_subatlas"]["chart_ids"])
    assert compatible == {"runtime-nf:nf-a", "runtime-nf:nf-b"}
    assert "nf:closure-ball:v1" not in compatible
    relation = next(
        relation
        for relation in atlas["translations"]
        if relation.get("source_state_id") == "a"
        and relation.get("target_state_id") == "b"
    )
    assert relation["status"] == "OPEN"
    assert relation["id"] in atlas["compatible_subatlas"][
        "open_boundary_translation_ids"
    ]


def test_open_interface_is_atlas_glue_not_empty_ontology():
    contract = derive_open_ui_contract(perspective_id="perspective:atlas")
    assert contract["status"] != "WITNESSED"
    assert contract["natural_form_atlas"]["historical_chart_count"] == len(
        historical_charts()
    )
    assert contract["natural_form_atlas"]["compatible_subatlas"]["chart_ids"] == []
    assert contract["glued_ui_subatlas"]["single_final_form_selected"] is False
    assert contract["atlas_semantics"]["closure_ball_is_master_container"] is False
    validation = validate_ui_contract(contract)
    assert validation["valid"] is True, validation
    assert validation["interface_is_glued_versioned_subatlas"] is True


def test_browser_independently_checks_atlas_and_edges_transport_views():
    assert "async function atlasContractMatches(contract)" in CLOSURE_ONLY_SUPERNET_HTML
    assert "naturalFormAtlasId" in CLOSURE_ONLY_SUPERNET_HTML
    assert 'data-view-transport\": \"ONGOING_VIEW_TRANSPORT\"' in CLOSURE_ONLY_SUPERNET_HTML
    assert 'data-view-transport\": \"OPEN_VIEW_TRANSPORT\"' in CLOSURE_ONLY_SUPERNET_HTML
    assert "await atlasContractMatches(contract)" in CLOSURE_ONLY_SUPERNET_HTML
