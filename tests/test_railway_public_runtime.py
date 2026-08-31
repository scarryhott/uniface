from __future__ import annotations

from pathlib import Path

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig


ROOT = Path(__file__).resolve().parents[1]
RAILWAY = ROOT / "railway.toml"
DOCKERFILE = ROOT / "Dockerfile"


def test_railway_publishes_only_the_translational_projection(tmp_path: Path) -> None:
    contract = RAILWAY.read_text(encoding="utf-8")
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    assert 'builder = "DOCKERFILE"' in contract
    assert 'dockerfilePath = "Dockerfile"' in contract
    assert "RUN pip install --no-cache-dir ." in dockerfile
    assert "CLOSURE_ENVIRONMENT=production" in dockerfile
    assert "CLOSURE_PROJECTION_ONLY_MODE=true" in dockerfile
    assert 'healthcheckPath = "/supernet/interface/capabilities"' in contract

    app = create_app(
        RuntimeConfig(
            database_path=tmp_path / "railway.db",
            inbox_dir=tmp_path / "inbox",
            backup_dir=tmp_path / "backups",
            autonomy_enabled=False,
            environment="production",
            projection_only_mode=True,
            trusted_hosts=("testserver", "localhost", "127.0.0.1"),
        )
    )
    assert {str(route.path) for route in app.routes} == {
        "/",
        "/supernet",
        "/natural-interface",
        "/supernet/interface",
        "/supernet/interface/capabilities",
        "/supernet/interface/projections/{contract_id}/return",
        "/livez",
        "/readyz",
    }
    assert app.version == "3.19.0"
