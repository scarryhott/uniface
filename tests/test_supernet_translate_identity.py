from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.supernet_closure_form import TRANSLATE_OPERATOR
from closure_supernet.supernet_closure_runtime import TRANSLATION_ENDPOINT


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "supernet-translate.db",
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


def _continuing_return_path(full: dict) -> tuple[dict, dict]:
    interactions = {
        row["path_id"]: row for row in full["supernet_closure_form"]["interactions"]
    }
    for path in full["relative_natural_form_potential_gate"]["paths"]:
        row = interactions.get(path["id"])
        if (
            row
            and row["ai_token_phase"] == "AI_CONTINUING"
            and path.get("action") == "OPEN_RETURN_EXTENSION"
        ):
            return path, row
    raise AssertionError("fixture has no continuing returned-interaction path")


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


def test_browser_and_runtime_publish_one_translate_operator(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        caps = client.get("/supernet/interface/capabilities").json()
        html = client.get("/supernet").text
        full = _gate(client)

    assert caps["translation_operator"] == TRANSLATE_OPERATOR
    assert caps["interaction_endpoint"] == TRANSLATION_ENDPOINT
    assert caps["interaction_relations"] == [TRANSLATE_OPERATOR]
    assert caps["single_transition_operator"] is True
    assert caps["browser_transition_is_runtime_transition"] is True
    assert caps["state_transition_is_visual_transition"] is True
    assert caps["separate_navigation_operator"] is False
    assert caps["separate_return_operator"] is False
    assert full["translation_operator"] == TRANSLATE_OPERATOR
    assert full["supernet_closure_form"]["translation_operator"] == TRANSLATE_OPERATOR
    assert "async function translateClosureForm" in html
    assert "translationMatches(translation,source,next,path)" in html
    assert "/supernet/interface/projections/${encodeURIComponent(source.id)}/translate" in html
    assert "flowTranslation(next,path,translation)" in html
    assert "async function navigateRelation(path)" not in html
    assert "async function submitReturn()" not in html


def test_continuing_visual_motion_is_the_same_runtime_translation(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        source = _gate(client)
        path, interaction = _continuing_return_path(source)
        endpoint = TRANSLATION_ENDPOINT.replace("{contract_id}", source["id"])
        response = client.post(endpoint, json=_payload(source, path, interaction))

    assert response.status_code == 200, response.text
    body = response.json()
    successor = body["supernet_potential_gate"]
    translation = body["translation"]
    assert body["translated"] is True
    assert body["operator"] == TRANSLATE_OPERATOR
    assert successor["id"] == source["id"]
    assert translation["source_gate_id"] == source["id"]
    assert translation["target_gate_id"] == source["id"]
    assert translation["source_closure_form_id"] == source["supernet_closure_form_id"]
    assert translation["target_closure_form_id"] == source["supernet_closure_form_id"]
    assert translation["source_interaction_id"] == interaction["id"]
    assert translation["source_ai_token_phase"] == "AI_CONTINUING"
    assert translation["runtime_state_change_is_this_translation"] is True
    assert translation["browser_trajectory_is_this_translation"] is True
    assert translation["semantic_transition_is_visual_transition"] is True
    assert translation["separate_navigation_operator"] is False
    assert translation["separate_return_operator"] is False


def test_returned_determination_uses_the_same_translate_operator(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        source = _gate(client)
        path, interaction = _continuing_return_path(source)
        endpoint = TRANSLATION_ENDPOINT.replace("{contract_id}", source["id"])
        response = client.post(
            endpoint,
            json=_payload(source, path, interaction, "one returned Supernet translation"),
        )

    assert response.status_code == 200, response.text
    body = response.json()
    successor = body["supernet_potential_gate"]
    translation = body["translation"]
    assert body["operator"] == TRANSLATE_OPERATOR
    assert successor["id"] == translation["target_gate_id"]
    assert successor["supernet_closure_form_id"] == translation["target_closure_form_id"]
    assert translation["source_gate_id"] == source["id"]
    assert translation["source_closure_form_id"] == source["supernet_closure_form_id"]
    assert translation["source_interaction_id"] == interaction["id"]
    assert translation["source_ai_token_phase"] == "AI_CONTINUING"
    assert translation["runtime_state_change_is_this_translation"] is True
    assert translation["browser_trajectory_is_this_translation"] is True
    assert translation["semantic_transition_is_visual_transition"] is True
