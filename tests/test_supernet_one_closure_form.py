from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.supernet_closure_form import validate_full_supernet_gate_contract


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "one-closure-form.db",
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


def test_published_supernet_has_one_semantic_carrier(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        full = _gate(client)
        caps = client.get("/supernet/interface/capabilities").json()

    assert validate_full_supernet_gate_contract(full)["valid"] is True
    form = full["supernet_closure_form"]
    assert full["published_semantic_carrier"] == "SUPERNET_CLOSURE_FORM"
    assert form["single_published_semantic_carrier"] is True
    assert form["opener_ui_interaction_are_one_form"] is True
    assert form["crystal_ball_slide_ai_token_are_one_form"] is True
    assert form["legacy_modules_are_compatibility_evidence_only"] is True
    assert caps["published_semantic_carrier"] == "SUPERNET_CLOSURE_FORM"
    assert caps["opener_ui_interaction_are_one_form"] is True
    assert caps["crystal_ball_slide_ai_token_are_one_form"] is True


def test_every_visible_interaction_is_a_projection_of_same_form(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        full = _gate(client)
        html = client.get("/supernet").text

    form = full["supernet_closure_form"]
    assert len(form["interactions"]) == len(
        full["relative_natural_form_potential_gate"]["paths"]
    )
    for row in form["interactions"]:
        assert row["opener_is_this_form"] is True
        assert row["ui_is_this_form"] is True
        assert row["interaction_is_translation_of_this_form"] is True
        assert row["return_is_determination_of_this_form"] is True
        assert row["slide_is_current_coordinate_of_this_form"] is True
        assert row["ai_token_phase"] in {"AI_CONTINUING", "TOKEN_RETURNED"}
        assert row["renderer_authors_form"] is False
        assert row["interaction_handler_authors_form"] is False

    assert "SUPERNET_CLOSURE_FORM" in html
    assert "closureInteraction(active,path)" in html
    assert "data-supernet-closure-form-id" in html
    assert "data-opener-ui-interaction-one-form" in html
    assert "data-crystal-ball-slide-ai-token-one-form" in html
