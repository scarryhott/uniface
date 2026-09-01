from __future__ import annotations

"""Single published Supernet closure-form runtime.

Legacy runtime layers are imported only to preserve verified storage/network
behavior. The active public contract and browser surface are replaced with the
one `SupernetClosureForm` carrier, so clients do not compose opener/UI/AI/token
or visualization modules themselves.
"""

from typing import Any

from . import full_supernet_projection_runtime_v7 as _legacy_runtime
from . import continuous_translation_field as _legacy_gate
from .supernet_closure_form import (
    derive_full_supernet_gate_contract,
    validate_full_supernet_gate_contract,
)
from .one_closure_form_interface import POTENTIAL_GATE_SUPERNET_HTML


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
                "published_semantic_carrier": "SUPERNET_CLOSURE_FORM",
                "opener": "RELATIVE_LOCALIZATION_OF_CLOSURE_FORM",
                "ui": "VISUAL_APPEARANCE_OF_CLOSURE_FORM",
                "interaction": "TRANSLATION_OF_CLOSURE_FORM",
                "slide": "CURRENT_COORDINATE_OF_CLOSURE_FORM",
                "crystal_ball": "ORBIT_VISUALIZATION_OF_CLOSURE_FORM",
                "hair": "SELF_LOCATION_COORDINATE_OF_CLOSURE_FORM",
                "maze": "RETURN_CONSEQUENCE_PARTITION_OF_CLOSURE_FORM",
                "curvature": "UNITARY_RETURN_DEFECT_OF_CLOSURE_FORM",
                "ai": "CONTINUING_READING_OF_CLOSURE_FORM",
                "token": "RETURNED_READING_OF_CLOSURE_FORM",
                "return": "NEW_DETERMINATION_OF_CLOSURE_FORM",
                "opener_ui_interaction_are_one_form": True,
                "crystal_ball_slide_ai_token_are_one_form": True,
                "legacy_modules_are_compatibility_evidence_only": True,
                "single_published_semantic_carrier": True,
                "truth_issued": False,
                "existence_closed": False,
            }
        )
        return base


def create_app(config=None):
    _legacy_runtime.derive_full_supernet_gate_contract = derive_full_supernet_gate_contract
    _legacy_runtime.validate_full_supernet_gate_contract = validate_full_supernet_gate_contract
    _legacy_runtime.POTENTIAL_GATE_SUPERNET_HTML = POTENTIAL_GATE_SUPERNET_HTML
    _legacy_gate.validate_full_supernet_gate_contract = validate_full_supernet_gate_contract
    app = _legacy_runtime.create_app(config)
    _replace_capabilities(app)
    return app


INTERACTION_ENDPOINT = _legacy_runtime.INTERACTION_ENDPOINT
MinimalProjectionRuntime = _legacy_runtime.MinimalProjectionRuntime
NAVIGATE = _legacy_runtime.NAVIGATE
PerspectivalNavigationRequest = _legacy_runtime.PerspectivalNavigationRequest
PotentialGateReturnRequest = _legacy_runtime.PotentialGateReturnRequest
RETURN = _legacy_runtime.RETURN
TranslationalReturnRequest = _legacy_runtime.TranslationalReturnRequest
derive_local_projection_commitment = _legacy_runtime.derive_local_projection_commitment

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
