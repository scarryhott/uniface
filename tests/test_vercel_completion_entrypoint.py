from __future__ import annotations

import importlib


def test_vercel_asgi_serves_the_latest_completion_integrated_app(monkeypatch) -> None:
    monkeypatch.setenv("CLOSURE_AUTONOMY_ENABLED", "false")
    module = importlib.import_module("asgi")
    routes = {getattr(route, "path", None) for route in module.app.routes}
    assert "/network/inversion/capabilities" in routes
    assert "/network/completion/capabilities" in routes
    assert "/network/completion/systems" in routes
    assert "/completion" in routes
    assert module.app.version == "2.8.0"
