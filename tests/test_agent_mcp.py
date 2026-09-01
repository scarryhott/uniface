from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.supernet_closure_form import TRANSLATE_OPERATOR


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "agent-mcp.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def test_agent_mcp_is_transport_over_the_published_closure_runtime(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        response = client.get("/supernet/agent/capabilities")
        assert response.status_code == 200
        caps = response.json()
        assert caps["endpoint"] == "/mcp"
        assert caps["tool_only"] is True
        assert caps["same_runtime"] is True
        assert caps["published_semantic_carrier"] == "SUPERNET_CLOSURE_FORM"
        assert caps["translation_operator"] == TRANSLATE_OPERATOR
        assert caps["agent_interaction_is_supernet_translate"] is True
        assert caps["self_runtime_is_closure_form_reading"] is True
        assert caps["separate_agent_mutation_authority"] is False
        assert caps["admin_privilege"] is False
        assert caps["truth_privilege"] is False
        assert "/mcp" in {getattr(route, "path", None) for route in app.routes}


def test_agent_self_reading_is_not_a_second_truth_authority(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        first = client.get(
            "/supernet/agent/self", params={"perspective_id": "openai-agent"}
        )
        second = client.get(
            "/supernet/agent/self", params={"perspective_id": "openai-agent"}
        )
        assert first.status_code == 200
        assert second.status_code == 200
        a = first.json()
        b = second.json()

    assert a == b
    assert a["published_semantic_carrier"] == "SUPERNET_CLOSURE_FORM"
    assert a["translation_operator"] == TRANSLATE_OPERATOR
    assert a["runtime_identity_is_translational_truth"] is True
    assert a["self_runtime_is_closure_form_reading"] is True
    assert a["self_observation_authors_truth"] is False
    assert a["separate_self_runtime_authority"] is False
