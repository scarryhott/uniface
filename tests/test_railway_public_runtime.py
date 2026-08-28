from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAILWAY = ROOT / "railway.toml"
DOCKERFILE = ROOT / "Dockerfile"
ASGI_ENTRY = ROOT / "asgi.py"


def test_railway_runs_the_natural_interface_application(monkeypatch) -> None:
    contract = RAILWAY.read_text(encoding="utf-8")
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    assert 'builder = "DOCKERFILE"' in contract
    assert 'dockerfilePath = "Dockerfile"' in contract
    assert "RUN pip install --no-cache-dir ." in dockerfile
    assert (
        "/usr/local/bin/closure-supernet --db /data/closure_supernet.db serve"
        in contract
    )
    assert "/app/.venv/bin/python" not in contract
    assert "--port $PORT" not in contract
    assert 'healthcheckPath = "/supernet/interface/capabilities"' in contract
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
    assert "/network/turing-being/life-events/{life_event_id}/return" in routes
    assert "/network/turing-being/charts" in routes
    assert "/continuation" in routes
    assert "/network/continuations/capabilities" in routes
    assert "/network/continuations/systems" in routes
    assert "/network/continuations/maps" in routes
    assert "/network/continuations/field" in routes
    assert "/proof-completion" in routes
    assert "/network/proofs/capabilities" in routes
    assert "/network/proofs/systems" in routes
    assert "/network/proofs/receipts" in routes
    assert "/network/proofs/field" in routes
    assert "/natural-interface" in routes
    assert "/supernet/interface/capabilities" in routes
    assert "/supernet/interface" in routes
    assert "/supernet/interface/admissions" in routes
    assert "/supernet/interface/offer" in routes
    assert "/supernet/interface/selections" in routes
    assert "/supernet/interface/collective" in routes
    assert "/supernet/sense" in routes
    assert "/supernet/events/{event_id}/sense-interact" in routes
    assert "/supernet/events/{event_id}/sense" in routes
    assert "/supernet/classic" in routes
    assert module.app.version == "3.6.0"
