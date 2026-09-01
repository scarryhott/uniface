from __future__ import annotations

"""Published Supernet runtime with visual identity from equal interactions.

NRRF882 determines the returned semantic translation geometry. This layer adds
NRRF883's one-layer UI/AI/token reading: visual identification is emitted only
from the same NaturalForm-family × MazeCell quotient through which the active
user interaction and token interaction both factor.
"""

from . import full_supernet_projection_runtime_v3 as _v3
from .equal_user_token_visual_identification import (
    derive_full_supernet_gate_contract,
    validate_full_supernet_gate_contract,
)
from .equal_user_token_visual_interface import POTENTIAL_GATE_SUPERNET_HTML


def create_app(config=None):
    # v3 derives its current gate through module-global functions, so replacing
    # those globals strengthens the same route/runtime without parallel state.
    _v3.derive_full_supernet_gate_contract = derive_full_supernet_gate_contract
    _v3.validate_full_supernet_gate_contract = validate_full_supernet_gate_contract
    _v3.POTENTIAL_GATE_SUPERNET_HTML = POTENTIAL_GATE_SUPERNET_HTML
    return _v3.create_app(config)


INTERACTION_ENDPOINT = _v3.INTERACTION_ENDPOINT
MinimalProjectionRuntime = _v3.MinimalProjectionRuntime
NAVIGATE = _v3.NAVIGATE
PerspectivalNavigationRequest = _v3.PerspectivalNavigationRequest
PotentialGateReturnRequest = _v3.PotentialGateReturnRequest
RETURN = _v3.RETURN
TranslationalReturnRequest = _v3.TranslationalReturnRequest
derive_local_projection_commitment = _v3.derive_local_projection_commitment

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
