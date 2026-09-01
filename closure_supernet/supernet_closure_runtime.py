from __future__ import annotations

"""Single published Supernet closure-form runtime and transition operator.

Legacy storage/network mechanics remain available as compatibility evidence,
but the active browser and runtime both execute ``SUPERNET_TRANSLATE``. The
server emits one content-addressed translation receipt, and the browser uses
that exact receipt as its visible trajectory. Navigation and return are no
longer separate public interaction operators.
"""

from typing import Any, Mapping

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field

from . import full_supernet_projection_runtime_v7 as _legacy_runtime
from . import continuous_translation_field as _legacy_gate
from .supernet_closure_form import (
    TRANSLATE_OPERATOR,
    closure_interaction_by_path,
    derive_full_supernet_gate_contract,
    derive_supernet_translation_receipt,
    validate_full_supernet_gate_contract,
)
from .one_closure_form_interface import POTENTIAL_GATE_SUPERNET_HTML

TRANSLATION_ENDPOINT = "/supernet/interface/projections/{contract_id}/translate"
LEGACY_INTERACTION_ENDPOINT = _legacy_runtime.INTERACTION_ENDPOINT
INTERACTION_ENDPOINT = TRANSLATION_ENDPOINT


class SupernetTranslationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relation_id: str = Field(min_length=1, max_length=500)
    perspective_id: str = Field(min_length=1, max_length=500)
    focus_event_id: str | None = Field(default=None, max_length=500)
    navigation_context: dict[str, Any]
    source_closure_form_id: str = Field(min_length=1, max_length=500)
    source_interaction_id: str = Field(min_length=1, max_length=500)
    exact_source_return: str = Field(default="", max_length=20_000)
    local_perspective_hair_millidegrees: int = Field(
        default=0,
        ge=-180_000,
        le=180_000,
    )
    local_perspective_zoom_milli: int = Field(
        default=1000,
        ge=0,
        le=1_000_000,
    )


def _route_endpoint(app: Any, path: str, method: str) -> Any:
    for route in app.router.routes:
        methods = getattr(route, "methods", set()) or set()
        if getattr(route, "path", None) == path and method in methods:
            return route.endpoint
    raise RuntimeError(f"missing route: {method} {path}")


def _provenance(runtime: Any) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in runtime.ledger.list_returns():
        event_id = str(item.get("id") or "")
        perspective_id = str(item.get("perspective_id") or "")
        if event_id and perspective_id:
            result[event_id] = perspective_id
    return result


def _current_form_state(runtime: Any, data: SupernetTranslationRequest) -> dict[str, Any]:
    closure_contract = runtime.project(
        perspective_id=data.perspective_id,
        focus_event_id=data.focus_event_id,
    )
    return derive_full_supernet_gate_contract(
        closure_contract,
        navigation_context=data.navigation_context,
        source_perspective_by_event=_provenance(runtime),
    )


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
                "translation_operator": TRANSLATE_OPERATOR,
                "interaction_endpoint": TRANSLATION_ENDPOINT,
                "interaction_relations": [TRANSLATE_OPERATOR],
                "mutation_relations": [TRANSLATE_OPERATOR],
                "opener": "RELATIVE_LOCALIZATION_OF_CLOSURE_FORM",
                "ui": "VISUAL_APPEARANCE_OF_CLOSURE_FORM",
                "interaction": "SUPERNET_TRANSLATE",
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
                "browser_transition_is_runtime_transition": True,
                "state_transition_is_visual_transition": True,
                "single_transition_operator": True,
                "continuing_interaction_uses_same_translation_operator": True,
                "separate_navigation_operator": False,
                "separate_return_operator": False,
                "legacy_interaction_endpoint": LEGACY_INTERACTION_ENDPOINT,
                "legacy_interaction_endpoint_is_compatibility_only": True,
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
    runtime = app.state.runtime
    legacy_interact = _route_endpoint(app, LEGACY_INTERACTION_ENDPOINT, "POST")

    @app.post(TRANSLATION_ENDPOINT)
    async def translate(
        contract_id: str,
        data: SupernetTranslationRequest,
    ) -> dict[str, Any]:
        current = _current_form_state(runtime, data)
        if current.get("id") != contract_id:
            raise HTTPException(409, "The Supernet closure form has changed")
        validation = validate_full_supernet_gate_contract(current)
        if validation.get("valid") is not True:
            raise HTTPException(409, "The current Supernet closure form is not derived")

        form = current.get("supernet_closure_form")
        if not isinstance(form, Mapping) or form.get("id") != data.source_closure_form_id:
            raise HTTPException(409, "The source closure form is stale")
        try:
            interaction = closure_interaction_by_path(current, data.relation_id)
        except ValueError as error:
            raise HTTPException(409, str(error)) from error
        if interaction.get("id") != data.source_interaction_id:
            raise HTTPException(409, "The source interaction is stale")
        if interaction.get("translation_operator") != TRANSLATE_OPERATOR:
            raise HTTPException(409, "The relation is not a Supernet translation")

        phase = str(interaction.get("ai_token_phase") or "")
        shared = {
            "relation_id": data.relation_id,
            "perspective_id": data.perspective_id,
            "focus_event_id": data.focus_event_id,
            "navigation_context": data.navigation_context,
        }
        if phase == "TOKEN_RETURNED":
            result: Mapping[str, Any] = await legacy_interact(
                contract_id,
                {
                    **shared,
                    "interaction_kind": _legacy_runtime.NAVIGATE,
                },
            )
            successor = result.get("supernet_potential_gate")
        elif phase == "AI_CONTINUING":
            exact_source = data.exact_source_return.strip()
            if not exact_source:
                # A continuing slide is still an interaction of the same
                # closure form. It executes SUPERNET_TRANSLATE without adding a
                # returned determination, so the semantic successor is the same
                # carrier and the browser receives a canonical trajectory.
                result = {
                    "replayed": False,
                    "truth_refined": False,
                    "continuing": True,
                }
                successor = current
            else:
                result = await legacy_interact(
                    contract_id,
                    {
                        **shared,
                        "interaction_kind": _legacy_runtime.RETURN,
                        "exact_source_return": exact_source,
                        "local_perspective_hair_millidegrees": (
                            data.local_perspective_hair_millidegrees
                        ),
                        "local_perspective_zoom_milli": (
                            data.local_perspective_zoom_milli
                        ),
                    },
                )
                successor = result.get("supernet_potential_gate")
        else:
            raise HTTPException(409, "The interaction has no valid AI/token phase")

        if not isinstance(successor, Mapping):
            raise HTTPException(500, "Supernet translation returned no closure form")
        successor_validation = validate_full_supernet_gate_contract(successor)
        if successor_validation.get("valid") is not True:
            raise HTTPException(409, "The translated successor closure form is not derived")

        receipt = derive_supernet_translation_receipt(
            current,
            successor,
            relation_id=data.relation_id,
            replayed=bool(result.get("replayed")),
            truth_refined=bool(result.get("truth_refined")),
        )
        return {
            "status": "TRANSLATED",
            "translated": True,
            "operator": TRANSLATE_OPERATOR,
            "translation": receipt,
            "supernet_potential_gate": dict(successor),
        }

    app.state.supernet_translate = translate
    _replace_capabilities(app)
    return app


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
    "LEGACY_INTERACTION_ENDPOINT",
    "MinimalProjectionRuntime",
    "NAVIGATE",
    "PerspectivalNavigationRequest",
    "PotentialGateReturnRequest",
    "RETURN",
    "SupernetTranslationRequest",
    "TRANSLATION_ENDPOINT",
    "TranslationalReturnRequest",
    "app",
    "create_app",
    "derive_local_projection_commitment",
]
