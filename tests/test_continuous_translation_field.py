from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.continuous_translation_field import (
    validate_full_supernet_gate_contract,
)


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "continuous-translation.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        projection_only_mode=False,
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def _gate(client: TestClient, perspective: str = "perspective") -> dict:
    response = client.get(
        "/supernet/interface",
        params={"perspective_id": perspective, "potential_gate": True},
    )
    assert response.status_code == 200, response.text
    return response.json()["supernet_potential_gate"]


def test_gate_publishes_one_continuous_translation_field(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        full = _gate(client)
        capabilities = client.get("/supernet/interface/capabilities").json()

    assert validate_full_supernet_gate_contract(full)["valid"] is True
    gate = full["relative_natural_form_potential_gate"]
    field = gate["continuous_translation_field"]
    assert field["persistent_visual_carrier"] is True
    assert field["returned_revisions_are_control_points_not_visual_worlds"] is True
    assert field["visual_translation_is_continuous_between_returns"] is True
    assert field["return_deforms_same_field"] is True
    assert field["interpolation_authors_truth"] is False
    assert field["interpolation_authors_seen"] is False
    assert all(row["continuous_between_control_points"] is True for row in field["currents"])
    assert capabilities["visual_carrier"] == "PERSISTENT_CONTINUOUS_TRANSLATION_FIELD"
    assert capabilities["returned_revisions_are_visual_worlds"] is False
    assert capabilities["discrete_visual_instance"] is False


def test_browser_flows_between_returned_control_points(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        html = client.get("/supernet").text

    assert "continuous_translation_field" in html
    assert "flowTranslation(next,path)" in html
    assert "requestAnimationFrame(animateCurrentFlow)" in html
    assert 'data-persistent-visual-carrier' in html
    assert 'data-discrete-visual-instance' in html
    assert 'data-continuous-current-id' in html
    assert 'returned_revisions_are_control_points_not_visual_worlds' in html


def test_interpolation_is_explicitly_non_authoritative(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        full = _gate(client)

    field = full["relative_natural_form_potential_gate"]["continuous_translation_field"]
    assert field["interpolation_authors_truth"] is False
    assert field["interpolation_authors_seen"] is False
    assert field["interpolation_authors_natural_form"] is False
    assert field["interpolation_authors_return"] is False
    for current in field["currents"]:
        assert current["interpolation_authors_truth"] is False
        assert current["interpolation_authors_seen"] is False
        assert current["interpolation_authors_return"] is False
