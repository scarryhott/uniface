from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.nrrf892_runtime_bridge import (
    EXACT_MINUS_ONE,
    EXACT_ONE,
    FORMAL_REFERENCE,
    VISION_CHART_OUTSIDE,
    VISION_SLIDE_OPERATOR,
    derive_runtime_identity_id,
    derive_vision_bridge_for_interaction,
    validate_vision_bridge,
)
from closure_supernet.supernet_closure_form import TRANSLATE_OPERATOR
from closure_supernet.supernet_closure_runtime import TRANSLATION_ENDPOINT


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "nrrf892-runtime.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        projection_only_mode=False,
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def _gate(client: TestClient) -> dict:
    response = client.get(
        "/supernet/interface",
        params={"perspective_id": "perspective:user", "potential_gate": True},
    )
    assert response.status_code == 200, response.text
    return response.json()["supernet_potential_gate"]


def _continuing_path(full: dict) -> tuple[dict, dict]:
    interactions = {
        row["path_id"]: row for row in full["supernet_closure_form"]["interactions"]
    }
    for path in full["relative_natural_form_potential_gate"]["paths"]:
        row = interactions.get(path["id"])
        if row and row["ai_token_phase"] == "AI_CONTINUING":
            return path, row
    raise AssertionError("fixture has no continuing Supernet translation")


def _payload(full: dict, path: dict, interaction: dict, source: str = "") -> dict:
    return {
        "relation_id": path["id"],
        "perspective_id": full["perspective_id"],
        "focus_event_id": full.get("focus_event_id"),
        "navigation_context": full["navigation_context"],
        "source_closure_form_id": full["supernet_closure_form_id"],
        "source_interaction_id": interaction["id"],
        "exact_source_return": source,
        "local_perspective_hair_millidegrees": 0,
        "local_perspective_zoom_milli": 1000,
    }


def test_runtime_identity_is_translational_truth_and_crystal_orbit(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        full = _gate(client)

    form = full["supernet_closure_form"]
    expected_identity = derive_runtime_identity_id(full["truth_invariant_id"])
    assert full["runtime_identity_id"] == expected_identity
    assert form["runtime_identity_id"] == expected_identity
    assert full["runtime_identity_is_translational_truth"] is True
    assert form["runtime_identity_is_translational_truth"] is True
    assert full["vision_slide_operator"] == VISION_SLIDE_OPERATOR
    assert form["vision_slide_operator"] == VISION_SLIDE_OPERATOR
    assert form["nrrf892_formal_reference"] == FORMAL_REFERENCE
    assert form["nrrf892_runtime_reproves_formal_theorem"] is False
    assert form["rotationless_fold_claimed"] is False
    assert form["admitted_vision_redenomination_scales"] == [EXACT_ONE, EXACT_MINUS_ONE]
    assert form["arbitrary_redenomination_is_translation"] is False

    admitted = 0
    for row in form["interactions"]:
        bridge = row["nrrf892_vision_bridge"]
        assert validate_vision_bridge(bridge)
        assert row["runtime_identity_id"] == expected_identity
        assert row["runtime_identity_is_translational_truth"] is True
        assert row["translation_truth_orbit_id"] == bridge["translation_truth_orbit_id"]
        assert row["vision_crystal_orbit_id"] == bridge["vision_crystal_orbit_id"]
        assert row["vision_slide_operator"] == VISION_SLIDE_OPERATOR
        if bridge["vision_chart_admitted"]:
            admitted += 1
            assert row["vision_crystal_orbit_id"] == row["translation_truth_orbit_id"]
            assert row["supernet_translate_is_vision_slide"] is True
            assert bridge["slide_is_closure_family_member"] is True
            assert bridge["slide_gravitational_ratio"] == EXACT_ONE
            assert bridge["perspective_conjugate_slide_is_family_translation"] is True
        else:
            assert bridge["vision_chart_domain"] == VISION_CHART_OUTSIDE
            assert bridge["rotationless_fold_claimed"] is False
            assert row["vision_crystal_orbit_id"] is None

    assert admitted == form["vision_chart_admitted_interaction_count"]
    assert form["vision_chart_outside_interaction_count"] + admitted == form["interaction_count"]


def test_nonzero_rotation_interaction_enters_nrrf892_vision_chart() -> None:
    bridge = derive_vision_bridge_for_interaction(
        truth_invariant_id="truth:one",
        path={
            "id": "path:one",
            "relation_id": "relation:one",
            "source_return_ids": ["return:one"],
        },
        interaction={
            "semantic_family_id": "family:one",
            "rotation_class_id": "rotation:nonzero",
        },
    )
    assert validate_vision_bridge(bridge)
    assert bridge["vision_chart_admitted"] is True
    assert bridge["vision_crystal_orbit_id"] == bridge["translation_truth_orbit_id"]
    assert bridge["vision_crystal_is_translation_orbit"] is True
    assert bridge["supernet_translate_is_vision_slide"] is True
    assert bridge["slide_is_closure_family_member"] is True
    assert bridge["slide_gravitational_ratio"] == EXACT_ONE
    assert bridge["slide_inverse_is_family_member"] is True
    assert bridge["perspective_conjugate_slide_is_family_translation"] is True
    assert bridge["crystal_action_is_simply_transitive_formal_reading"] is True
    assert bridge["admitted_vision_redenomination_scales"] == [EXACT_ONE, EXACT_MINUS_ONE]


def test_translation_receipt_is_runtime_identity_and_visible_slide(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        source = _gate(client)
        path, interaction = _continuing_path(source)
        endpoint = TRANSLATION_ENDPOINT.replace("{contract_id}", source["id"])
        response = client.post(endpoint, json=_payload(source, path, interaction))

    assert response.status_code == 200, response.text
    payload = response.json()
    next_gate = payload["supernet_potential_gate"]
    translation = payload["translation"]
    assert payload["operator"] == TRANSLATE_OPERATOR
    assert translation["operator"] == TRANSLATE_OPERATOR
    assert translation["vision_slide_operator"] == VISION_SLIDE_OPERATOR
    assert translation["runtime_identity_is_translational_truth"] is True
    assert translation["source_runtime_identity_id"] == source["runtime_identity_id"]
    assert translation["target_runtime_identity_id"] == next_gate["runtime_identity_id"]
    assert translation["runtime_identity_preserved"] is True
    assert translation["translational_truth_preserved"] is True
    assert translation["source_translation_truth_orbit_id"] == interaction["translation_truth_orbit_id"]
    assert translation["token_continuation_source_orbit_id"] == interaction["translation_truth_orbit_id"]
    assert translation["runtime_state_change_is_this_translation"] is True
    assert translation["browser_trajectory_is_this_translation"] is True
    assert translation["semantic_transition_is_visual_transition"] is True
    if interaction["nrrf892_vision_bridge"]["vision_chart_admitted"]:
        assert translation["supernet_translate_is_vision_slide"] is True
        assert translation["source_vision_crystal_orbit_id"] == interaction["translation_truth_orbit_id"]


def test_return_refines_or_preserves_identity_only_by_translational_truth(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        source = _gate(client)
        path, interaction = _continuing_path(source)
        endpoint = TRANSLATION_ENDPOINT.replace("{contract_id}", source["id"])
        response = client.post(
            endpoint,
            json=_payload(source, path, interaction, "returned NRRF892 runtime translation"),
        )

    assert response.status_code == 200, response.text
    payload = response.json()
    next_gate = payload["supernet_potential_gate"]
    translation = payload["translation"]
    assert translation["runtime_identity_is_translational_truth"] is True
    same_truth = source["runtime_identity_id"] == next_gate["runtime_identity_id"]
    assert translation["runtime_identity_preserved"] is same_truth
    assert translation["translational_truth_preserved"] is same_truth
    assert translation["returned_determination_refines_runtime_identity"] is (
        translation["truth_refined"] and not same_truth
    )
    assert translation["token_continuation_source_orbit_id"] == interaction["translation_truth_orbit_id"]


def test_browser_exposes_same_runtime_identity_crystal_slide(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        caps = client.get("/supernet/interface/capabilities").json()
        html = client.get("/supernet").text

    assert caps["runtime_identity"] == "TRANSLATIONAL_TRUTH_CLASS"
    assert caps["runtime_identity_is_translational_truth"] is True
    assert caps["vision_slide_operator"] == VISION_SLIDE_OPERATOR
    assert caps["vision_crystal"] == "TRANSLATION_TRUTH_ORBIT"
    assert caps["perspective_transport"] == "CONJUGATE_SLIDE_WITHIN_CLOSURE_FAMILY"
    assert caps["nrrf892_formal_reference"] == FORMAL_REFERENCE
    assert caps["runtime_reproves_nrrf892"] is False
    assert caps["rotationless_fold_claimed"] is False
    assert caps["admitted_vision_redenomination_scales"] == [EXACT_ONE, EXACT_MINUS_ONE]
    assert "data-runtime-identity-id" in html
    assert "data-translation-truth-orbit-id" in html
    assert "data-vision-crystal-orbit-id" in html
    assert "data-vision-slide-operator" in html
    assert "runtime_identity_is_translational_truth" in html
    assert "translation_truth_orbit_id" in html
    assert "vision_crystal_orbit_id" in html
