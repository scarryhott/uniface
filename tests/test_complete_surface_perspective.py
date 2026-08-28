from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_natural_interface import create_app
from closure_supernet.config import RuntimeConfig


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "complete-perspective.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def test_primary_surface_reselects_by_perspective_and_preserves_sheaf_region(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        left = client.post(
            "/supernet/interface/offer",
            json={
                "exact_text": "Local learning perspective.",
                "authored_by": "person-a",
                "perspective_id": "person-a",
                "form_label": "learning",
                "sheaf": "SLEARN_PERSPECTIVE",
            },
        ).json()
        right = client.post(
            "/supernet/interface/offer",
            json={
                "exact_text": "Open second-brain memory.",
                "authored_by": "person-b",
                "perspective_id": "person-b",
                "form_label": "memory",
                "sheaf": "AGI_SECOND_BRAIN",
            },
        ).json()

        left_ui = client.get(
            "/supernet/interface", params={"perspective_id": "person-a"}
        ).json()
        assert left_ui["focus_event"]["id"] == left["event_id"]
        assert left_ui["natural_chart"]["eight_sheaf"] == "SLEARN_PERSPECTIVE"
        assert left_ui["natural_chart"]["ball_hair_region"] == "LOCAL BALL"

        right_ui = client.get(
            "/supernet/interface", params={"perspective_id": "person-b"}
        ).json()
        assert right_ui["focus_event"]["id"] == right["event_id"]
        assert right_ui["natural_chart"]["eight_sheaf"] == "AGI_SECOND_BRAIN"
        assert right_ui["natural_chart"]["ball_hair_region"] == "GLOBAL HAIR"

        page = client.get("/").text
        assert "params.set('perspective_id',p)" in page
        assert "Return sensed as successor potential" in page
        assert "Reopening re-sensed in the living field" in page
