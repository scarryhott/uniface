from __future__ import annotations

from closure_supernet.api_agent import app as production_app
from closure_supernet.api_interactive_translation import app as research_app


def _paths(app) -> set[str]:
    return {route.path for route in app.routes}


def test_research_adapter_has_an_isolated_fastapi_object() -> None:
    assert research_app is not production_app

    production_paths = _paths(production_app)
    research_paths = _paths(research_app)

    assert "/supernet/interface" in production_paths
    assert "/supernet/interface/capabilities" in production_paths
    assert "/supernet/closure-equations/resolve" not in production_paths
    assert "/supernet/closure-equations/capabilities" not in production_paths

    assert "/supernet/interface" in research_paths
    assert "/supernet/interface/capabilities" in research_paths
    assert "/supernet/closure-equations/resolve" in research_paths
    assert "/supernet/closure-equations/capabilities" in research_paths
