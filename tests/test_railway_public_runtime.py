from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAILWAY = ROOT / "railway.toml"
ASGI_ENTRY = ROOT / "asgi.py"


def test_railway_runs_the_complete_turing_being_application(monkeypatch) -> None:
    contract = RAILWAY.read_text(encoding="utf-8")
    assert 'builder = "NIXPACKS"' in contract
    assert "closure-supernet serve" in contract
    assert "CLOSURE_DB_PATH=/data/closure_supernet.db" in contract
    assert 'healthcheckPath = "/network/turing-being/capabilities"' in contract
    assert "--no-autonomy" in contract

    monkeypatch.setenv("CLOSURE_AUTONOMY_ENABLED", "false")
    spec = importlib.util.spec_from_file_location("railway_asgi_test", ASGI_ENTRY)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    routes = {getattr(route, "path", None) for route in module.app.routes}
    assert "/turing-being" in routes
    assert "/network/turing-being/capabilities" in routes
    assert "/network/turing-being/life-events" in routes
    assert "/network/turing-being/life-events/{event_id}/return" in routes
    assert "/network/turing-being/charts" in routes
    assert module.app.version == "3.1.0"
