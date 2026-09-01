from __future__ import annotations

"""Published full-gate runtime with one unified Supernet interaction route."""

from . import full_supernet_projection_runtime as _base
from .potential_gate_unified_interface import POTENTIAL_GATE_SUPERNET_HTML

# ``create_app`` resolves this module global when it installs the three surface
# aliases, so patch the full-gate runtime before constructing the application.
_base.POTENTIAL_GATE_SUPERNET_HTML = POTENTIAL_GATE_SUPERNET_HTML

INTERACTION_ENDPOINT = _base.INTERACTION_ENDPOINT
MinimalProjectionRuntime = _base.MinimalProjectionRuntime
NAVIGATE = _base.NAVIGATE
PerspectivalNavigationRequest = _base.PerspectivalNavigationRequest
PotentialGateReturnRequest = _base.PotentialGateReturnRequest
RETURN = _base.RETURN
TranslationalReturnRequest = _base.TranslationalReturnRequest
create_app = _base.create_app
derive_local_projection_commitment = _base.derive_local_projection_commitment

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
