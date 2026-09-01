from __future__ import annotations

"""Published full-gate runtime with NRRF882 translation supervision.

The public route set remains unchanged.  This module only changes how the
full potential gate is derived: returned semantic market valuations are joined
to their canonical event-perspective provenance, and that exact translation
geometry becomes the shared AI/token supervision and perspectival-navigation
relation.
"""

from typing import Any, Mapping

from . import full_supernet_projection_runtime as _runtime
from .potential_gate_unified_interface import POTENTIAL_GATE_SUPERNET_HTML
from .translation_supervisory_full_gate import (
    derive_full_supernet_gate_contract,
    set_source_perspective_registry,
    update_source_perspective_registry,
    validate_full_supernet_gate_contract,
)


def _provenance(runtime: Any) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in runtime.ledger.list_returns():
        event_id = str(item.get("id") or "")
        perspective_id = str(item.get("perspective_id") or "")
        if event_id and perspective_id:
            result[event_id] = perspective_id
    return result


def _current_gate(
    runtime: Any,
    *,
    perspective_id: str,
    focus_event_id: str | None,
    navigation_context: Mapping[str, Any] | None,
) -> dict[str, Any]:
    provenance = _provenance(runtime)
    set_source_perspective_registry(provenance)
    closure_contract = runtime.project(
        perspective_id=perspective_id,
        focus_event_id=focus_event_id,
    )
    return derive_full_supernet_gate_contract(
        closure_contract,
        navigation_context=navigation_context,
        source_perspective_by_event=provenance,
    )


def _patch_runtime_instance(runtime: Any) -> None:
    original_append_return = runtime.append_return

    def append_return_with_provenance(*, contract: Mapping[str, Any], request: Any):
        response, replayed = original_append_return(
            contract=contract,
            request=request,
        )
        event_id = str(response.get("focus_event_id") or "")
        perspective_id = str(getattr(request, "perspective_id", "") or "")
        if event_id and perspective_id:
            update_source_perspective_registry({event_id: perspective_id})
        return response, replayed

    runtime.append_return = append_return_with_provenance  # type: ignore[method-assign]


def create_app(config: Any | None = None):
    # create_app resolves these globals when installing its route closures.
    _runtime.POTENTIAL_GATE_SUPERNET_HTML = POTENTIAL_GATE_SUPERNET_HTML
    _runtime.derive_full_supernet_gate_contract = derive_full_supernet_gate_contract
    _runtime.validate_full_supernet_gate_contract = validate_full_supernet_gate_contract
    _runtime._current_gate = _current_gate
    set_source_perspective_registry({})
    app = _runtime.create_app(config)
    _patch_runtime_instance(app.state.runtime)
    return app


INTERACTION_ENDPOINT = _runtime.INTERACTION_ENDPOINT
MinimalProjectionRuntime = _runtime.MinimalProjectionRuntime
NAVIGATE = _runtime.NAVIGATE
PerspectivalNavigationRequest = _runtime.PerspectivalNavigationRequest
PotentialGateReturnRequest = _runtime.PotentialGateReturnRequest
RETURN = _runtime.RETURN
TranslationalReturnRequest = _runtime.TranslationalReturnRequest
derive_local_projection_commitment = _runtime.derive_local_projection_commitment

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
