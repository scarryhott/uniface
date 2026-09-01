from __future__ import annotations

"""Published Supernet runtime with NRRF885 Seen/metaphor visualization."""

from typing import Any

from . import full_supernet_projection_runtime_v5 as _v5
from . import continuing_closure_full_gate as _continuing_gate_module
from .visualization_metaphor_closure import (
    derive_full_supernet_gate_contract,
    validate_full_supernet_gate_contract,
)
from .visualization_metaphor_interface import POTENTIAL_GATE_SUPERNET_HTML


def _replace_capabilities(app: Any) -> None:
    original = None
    kept = []
    for route in app.router.routes:
        if getattr(route, "path", None) == "/supernet/interface/capabilities":
            original = route.endpoint
        else:
            kept.append(route)
    app.router.routes[:] = kept
    if original is None:
        raise RuntimeError("Supernet capabilities route is missing")

    @app.get("/supernet/interface/capabilities")
    async def capabilities() -> dict[str, Any]:
        base = dict(await original())
        base.update(
            {
                "visualization_semantics": "NRRF885_SEEN_METAPHOR_EQUALITY",
                "visual_equality": "SEEN_ID_EQUALITY",
                "proof_by_visualization": "METAPHOR_EQUALITY",
                "visual_invariant_scope": "FACTORS_THROUGH_SEEN",
                "translation_truth_family": (
                    "VISUALIZATION_OF_NATURAL_FORMS_SELECTED_IN_CLOSURE"
                ),
                "current": "STRUCTURAL_TRANSLATION_ORBIT_READING",
                "crystal_ball": "LOCAL_ROTATION_CLASS_VISUALIZATION_CHART",
                "crystal_ball_is_master_supernet_ontology": False,
                "labels_author_visual_equality": False,
                "renderer_coordinates_author_visual_equality": False,
                "hair_authors_visual_equality": False,
                "zoom_authors_visual_equality": False,
                "runtime_reproves_nrrf885": False,
                "analytic_tan_limit_claimed": False,
                "truth_issued": False,
                "existence_closed": False,
            }
        )
        return base


def create_app(config=None):
    # v5 installs its module globals into the single published route. Replacing
    # those globals strengthens that route without creating parallel state.
    _v5.derive_full_supernet_gate_contract = derive_full_supernet_gate_contract
    _v5.validate_full_supernet_gate_contract = validate_full_supernet_gate_contract
    _v5.POTENTIAL_GATE_SUPERNET_HTML = POTENTIAL_GATE_SUPERNET_HTML

    # The NRRF885 bridge freezes the exact continuing-closure predecessor at
    # import time, so exposing the stronger validator at the v5 compatibility
    # boundary cannot recurse.
    _continuing_gate_module.validate_full_supernet_gate_contract = (
        validate_full_supernet_gate_contract
    )
    app = _v5.create_app(config)
    _replace_capabilities(app)
    return app


INTERACTION_ENDPOINT = _v5.INTERACTION_ENDPOINT
MinimalProjectionRuntime = _v5.MinimalProjectionRuntime
NAVIGATE = _v5.NAVIGATE
PerspectivalNavigationRequest = _v5.PerspectivalNavigationRequest
PotentialGateReturnRequest = _v5.PotentialGateReturnRequest
RETURN = _v5.RETURN
TranslationalReturnRequest = _v5.TranslationalReturnRequest
derive_local_projection_commitment = _v5.derive_local_projection_commitment

app = create_app()

__all__ = [
    "INTERACTION_ENDPOINT",
    "MinimalProjectionRuntime",
    "NAVIGATE",
    "PerspectivalNavigationRequest",
    "PotentialGateReturnRequest",
    "RETURN",
    "TranslationalReturnRequest",
    "app",
    "create_app",
    "derive_local_projection_commitment",
]
