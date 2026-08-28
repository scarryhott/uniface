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
    assert "/network/completion/closures" in routes
    assert "/network/completion/closures/two-return" in routes
    assert "/network/completion/closures/maps" in routes
    assert "/network/completion/closure-instances" in routes
    assert "/network/completion/unified-field" in routes
    assert "/completion" in routes
    assert "/unify-closure" in routes
    assert "/network/handed-life/capabilities" in routes
    assert "/network/handed-life/systems" in routes
    assert "/network/handed-life/human-relations" in routes
    assert "/handed-life" in routes
    assert "/network/turing-being/capabilities" in routes
    assert "/network/turing-being/life-events" in routes
    assert "/network/turing-being/charts" in routes
    assert "/network/turing-being/field" in routes
    assert "/turing-being" in routes
    assert "/network/continuations/capabilities" in routes
    assert "/network/continuations/systems" in routes
    assert "/network/continuations/maps" in routes
    assert "/network/continuations/field" in routes
    assert "/continuation" in routes
    assert "/network/proofs/capabilities" in routes
    assert "/network/proofs/systems" in routes
    assert "/network/proofs/receipts" in routes
    assert "/network/proofs/canonical-qg" in routes
    assert "/network/proofs/field" in routes
    assert "/proof-completion" in routes
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
