from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.nrrf892_runtime_bridge import VISION_SLIDE_OPERATOR
from closure_supernet.supernet_closure_form import TRANSLATE_OPERATOR
from closure_supernet.supernet_closure_runtime import TRANSLATION_ENDPOINT


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "agent-self-runtime-closure.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def _gate(client: TestClient, perspective: str = "openai-agent") -> dict:
    response = client.get(
        "/supernet/interface",
        params={"perspective_id": perspective, "potential_gate": True},
    )
    assert response.status_code == 200, response.text
    return response.json()["supernet_potential_gate"]


def _continuing(gate: dict) -> dict:
    for row in gate["supernet_closure_form"]["interactions"]:
        if row["ai_token_phase"] == "AI_CONTINUING":
            return row
    raise AssertionError("fixture has no continuing translation")


def test_agent_surface_is_one_closure_transition_not_parallel_runtime(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        caps = client.get("/supernet/agent/capabilities")
        assert caps.status_code == 200
        payload = caps.json()
        self_reading = client.get(
            "/supernet/agent/self", params={"perspective_id": "openai-agent"}
        )
        assert self_reading.status_code == 200
        self_payload = self_reading.json()

    assert payload["same_runtime"] is True
    assert payload["published_semantic_carrier"] == "SUPERNET_CLOSURE_FORM"
    assert payload["translation_operator"] == TRANSLATE_OPERATOR
    assert payload["runtime_identity"] == "TRANSLATIONAL_TRUTH_CLASS"
    assert payload["runtime_identity_is_translational_truth"] is True
    assert payload["agent_interaction_is_supernet_translate"] is True
    assert payload["self_runtime_is_closure_form_reading"] is True
    assert payload["separate_agent_mutation_authority"] is False
    assert payload["vision_slide_operator"] == VISION_SLIDE_OPERATOR
    assert self_payload["published_semantic_carrier"] == "SUPERNET_CLOSURE_FORM"
    assert self_payload["translation_operator"] == TRANSLATE_OPERATOR
    assert self_payload["runtime_identity_is_translational_truth"] is True
    assert self_payload["self_observation_authors_truth"] is False


def test_agent_and_self_runtime_share_the_exact_published_translation(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    runtime = app.state.runtime
    exact = "Agent interaction returns into the same self runtime closure form."

    with TestClient(app) as client:
        source = _gate(client)
        before = client.get(
            "/supernet/agent/self", params={"perspective_id": "openai-agent"}
        ).json()
        interaction = _continuing(source)
        endpoint = TRANSLATION_ENDPOINT.replace("{contract_id}", source["id"])
        response = client.post(
            endpoint,
            json={
                "relation_id": interaction["path_id"],
                "perspective_id": source["perspective_id"],
                "focus_event_id": source.get("focus_event_id"),
                "navigation_context": source["navigation_context"],
                "source_closure_form_id": source["supernet_closure_form_id"],
                "source_interaction_id": interaction["id"],
                "exact_source_return": exact,
                "local_perspective_hair_millidegrees": 0,
                "local_perspective_zoom_milli": 1000,
            },
        )
        assert response.status_code == 200, response.text
        result = response.json()
        target = result["supernet_potential_gate"]
        after = client.get(
            "/supernet/agent/self",
            params={
                "perspective_id": "openai-agent",
                "focus_event_id": target.get("focus_event_id"),
            },
        ).json()

    translation = result["translation"]
    assert result["operator"] == TRANSLATE_OPERATOR
    assert translation["operator"] == TRANSLATE_OPERATOR
    assert translation["runtime_state_change_is_this_translation"] is True
    assert translation["browser_trajectory_is_this_translation"] is True
    assert translation["runtime_identity_is_translational_truth"] is True
    assert translation["source_runtime_identity_id"] == before["runtime_identity_id"]
    assert translation["target_runtime_identity_id"] == after["runtime_identity_id"]
    assert after["closure_form_id"] == target["supernet_closure_form_id"]
    assert after["self_observation_authors_truth"] is False
    assert runtime.ledger.list_returns()[-1]["exact_source"] == exact
    runtime.close()
