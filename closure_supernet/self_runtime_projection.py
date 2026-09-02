from __future__ import annotations

"""Read the runtime from inside the same Supernet closure form.

This endpoint has no mutation or truth authority. It derives the same published
closure form used by browser and agent translation and returns only its relative
self-reading.
"""

from typing import Any

from fastapi import FastAPI

from .nrrf892_runtime_bridge import VISION_SLIDE_OPERATOR
from .supernet_closure_form import TRANSLATE_OPERATOR, derive_full_supernet_gate_contract


def _provenance(runtime: Any) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in runtime.ledger.list_returns():
        event_id = str(item.get("id") or "")
        perspective_id = str(item.get("perspective_id") or "")
        if event_id and perspective_id:
            result[event_id] = perspective_id
    return result


def derive_self_runtime_reading(
    runtime: Any,
    *,
    perspective_id: str = "runtime:self",
    focus_event_id: str | None = None,
) -> dict[str, Any]:
    closure = runtime.project(
        perspective_id=perspective_id,
        focus_event_id=focus_event_id,
    )
    gate = derive_full_supernet_gate_contract(
        closure,
        source_perspective_by_event=_provenance(runtime),
    )
    form = gate["supernet_closure_form"]
    return {
        "published_semantic_carrier": "SUPERNET_CLOSURE_FORM",
        "closure_form_id": form["id"],
        "translation_operator": TRANSLATE_OPERATOR,
        "runtime_identity_id": form["runtime_identity_id"],
        "truth_invariant_id": form["truth_invariant_id"],
        "runtime_identity_is_translational_truth": True,
        "vision_slide_operator": VISION_SLIDE_OPERATOR,
        "self_runtime_is_closure_form_reading": True,
        "self_observation_authors_truth": False,
        "separate_self_runtime_authority": False,
    }


def attach_self_runtime_projection(app: FastAPI) -> FastAPI:
    runtime = app.state.runtime

    @app.get("/supernet/agent/self")
    async def self_runtime(
        perspective_id: str = "runtime:self",
        focus_event_id: str | None = None,
    ) -> dict[str, Any]:
        return derive_self_runtime_reading(
            runtime,
            perspective_id=perspective_id,
            focus_event_id=focus_event_id,
        )

    app.state.supernet_self_runtime_reading = derive_self_runtime_reading
    return app


__all__ = ["attach_self_runtime_projection", "derive_self_runtime_reading"]
