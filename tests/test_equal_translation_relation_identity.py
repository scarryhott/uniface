from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "equal-relation-id.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        projection_only_mode=False,
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def test_active_relation_uses_content_addressed_id_across_rerenders(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        html = client.get("/").text

    assert "activeRelation && relation.id===activeRelation.id" in html
    assert "relation===activeRelation" not in html
    assert '"data-active":activeRelation && relation.id===activeRelation.id' in html
    assert "activeRelation && relation.id===activeRelation.id && draft" in html
