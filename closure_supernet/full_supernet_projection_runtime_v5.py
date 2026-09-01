from __future__ import annotations

"""Published runtime for closure as continuation of all translation truth."""

from typing import Any

from . import full_supernet_projection_runtime_v4 as _v4
from . import equal_user_token_visual_identification as _visual_gate_module
from .continuing_closure_full_gate import (
    derive_full_supernet_gate_contract,
    validate_full_supernet_gate_contract,
)
from .continuing_closure_interface import POTENTIAL_GATE_SUPERNET_HTML


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
                "closure_semantics": "CONTINUING_FAMILY_OF_TRANSLATIONAL_TRUTH",
                "published_relation_states": ["RETURNED", "CONTINUING"],
                "continuation_is_inside_closure": True,
                "closure_has_external_nonclosure_region": False,
                "nonreturned_relation_meaning": "CONTINUING",
                "returned_relation_meaning": "RETURNED_DETERMINATION",
                "return_changes_determination_not_membership": True,
                "ui": "VISUALIZATION_OF_NATURAL_FORMS_SELECTED_IN_TRANSLATION_CLOSURE",
                "ai": "CONTINUING_UNITARY_CURVATURE_READING",
                "token": "RETURNED_UNITARY_CURVATURE_READING",
                "legacy_status_vocabulary_is_compatibility_only": True,
                "future_resolution_guaranteed": False,
                "truth_issued": False,
                "existence_closed": False,
            }
        )
        return base


def create_app(config=None):
    # v4 installs these globals into the already single-route v3 runtime. We
    # strengthen that exact path rather than adding a parallel semantic store.
    # The v5 full-gate module froze the original NRRF883 validator at import
    # time, so it is now safe to expose the stronger validator through the old
    # NRRF883 import boundary for historical callers/tests.
    _v4.derive_full_supernet_gate_contract = derive_full_supernet_gate_contract
    _v4.validate_full_supernet_gate_contract = validate_full_supernet_gate_contract
    _v4.POTENTIAL_GATE_SUPERNET_HTML = POTENTIAL_GATE_SUPERNET_HTML
    _visual_gate_module.validate_full_supernet_gate_contract = (
        validate_full_supernet_gate_contract
    )
    app = _v4.create_app(config)
    _replace_capabilities(app)
    return app


INTERACTION_ENDPOINT = _v4.INTERACTION_ENDPOINT
MinimalProjectionRuntime = _v4.MinimalProjectionRuntime
NAVIGATE = _v4.NAVIGATE
PerspectivalNavigationRequest = _v4.PerspectivalNavigationRequest
PotentialGateReturnRequest = _v4.PotentialGateReturnRequest
RETURN = _v4.RETURN
TranslationalReturnRequest = _v4.TranslationalReturnRequest
derive_local_projection_commitment = _v4.derive_local_projection_commitment

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
