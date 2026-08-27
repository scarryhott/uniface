from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASGI_ENTRY = ROOT / "asgi.py"


def test_vercel_asgi_serves_the_latest_completion_integrated_app(monkeypatch) -> None:
    monkeypatch.setenv("CLOSURE_AUTONOMY_ENABLED", "false")
    spec = importlib.util.spec_from_file_location("completion_asgi_test", ASGI_ENTRY)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    routes = {getattr(route, "path", None) for route in module.app.routes}
    assert "/network/inversion/capabilities" in routes
    assert "/network/completion/capabilities" in routes
    assert "/network/completion/systems" in routes
    assert "/completion" in routes
    assert module.app.version == "2.8.0"
