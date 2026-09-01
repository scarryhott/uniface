from __future__ import annotations

"""Published Supernet runtime with one persistent continuous translation field."""

from typing import Any

from . import full_supernet_projection_runtime_v6 as _v6
from . import visualization_metaphor_closure as _metaphor_gate_module
from .continuous_translation_field import (
    derive_full_supernet_gate_contract,
    validate_full_supernet_gate_contract,
)
from .continuous_translation_interface import POTENTIAL_GATE_SUPERNET_HTML


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
                "visual_carrier": "PERSISTENT_CONTINUOUS_TRANSLATION_FIELD",
                "returned_revisions": "SEMANTIC_CONTROL_POINTS",
                "returned_revisions_are_visual_worlds": False,
                "continuous_between_returns": True,
                "navigation": "CONTINUOUS_FIELD_TRANSPORT",
                "hair": "CONTINUOUS_SELF_LOCATION_COORDINATE",
                "zoom": "CONTINUOUS_LOCAL_GLOBAL_COORDINATE",
                "return": "DEFORMATION_OF_THE_SAME_FIELD",
                "interpolation_authors_truth": False,
                "interpolation_authors_seen": False,
                "interpolation_authors_natural_form": False,
                "interpolation_authors_return": False,
                "discrete_visual_instance": False,
                "truth_issued": False,
                "existence_closed": False,
            }
        )
        return base


def create_app(config=None):
    # v6 already owns the single production route; replace only its derived
    # gate/validator/interface so there is still one semantic state and one UI.
    _v6.derive_full_supernet_gate_contract = derive_full_supernet_gate_contract
    _v6.validate_full_supernet_gate_contract = validate_full_supernet_gate_contract
    _v6.POTENTIAL_GATE_SUPERNET_HTML = POTENTIAL_GATE_SUPERNET_HTML

    # The continuous field module freezes the exact NRRF885 predecessor before
    # this compatibility alias is installed, avoiding recursive validation.
    _metaphor_gate_module.validate_full_supernet_gate_contract = (
        validate_full_supernet_gate_contract
    )
    app = _v6.create_app(config)
    _replace_capabilities(app)
    return app


INTERACTION_ENDPOINT = _v6.INTERACTION_ENDPOINT
MinimalProjectionRuntime = _v6.MinimalProjectionRuntime
NAVIGATE = _v6.NAVIGATE
PerspectivalNavigationRequest = _v6.PerspectivalNavigationRequest
PotentialGateReturnRequest = _v6.PotentialGateReturnRequest
RETURN = _v6.RETURN
TranslationalReturnRequest = _v6.TranslationalReturnRequest
derive_local_projection_commitment = _v6.derive_local_projection_commitment

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
