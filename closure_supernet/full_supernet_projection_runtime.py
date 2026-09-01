from __future__ import annotations

"""Production runtime for the full relative natural-form potential gate.

The historical closure UI contract remains the finite witnessed/OPEN truth
constraint. This runtime places it inside the larger Supernet gate and exposes
one interaction endpoint whose two internal relations are truth-inert
perspectival navigation and source-preserving return. No parallel public UI or
mutation route is introduced.
"""

from typing import Any, Literal, Mapping

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from . import minimal_projection_runtime as _base
from .full_supernet_potential_gate import (
    OPEN_RETURN_EXTENSION,
    advance_navigation_context,
    derive_full_supernet_gate_contract,
    derive_navigation_context,
    validate_full_supernet_gate_contract,
)
from .potential_gate_interface import POTENTIAL_GATE_SUPERNET_HTML

NAVIGATE = "PERSPECTIVE_NAVIGATION"
RETURN = "POTENTIAL_GATE_RETURN"
INTERACTION_ENDPOINT = "/supernet/interface/projections/{contract_id}/return"


class PerspectivalNavigationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interaction_kind: Literal["PERSPECTIVE_NAVIGATION"]
    relation_id: str = Field(min_length=1, max_length=500)
    perspective_id: str = Field(min_length=1, max_length=500)
    focus_event_id: str | None = Field(default=None, max_length=500)
    navigation_context: dict[str, Any]


class PotentialGateReturnRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interaction_kind: Literal["POTENTIAL_GATE_RETURN"]
    relation_id: str = Field(min_length=1, max_length=500)
    perspective_id: str = Field(min_length=1, max_length=500)
    focus_event_id: str | None = Field(default=None, max_length=500)
    navigation_context: dict[str, Any]
    exact_source_return: str = Field(min_length=1, max_length=20_000)
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

    @field_validator("exact_source_return")
    @classmethod
    def source_is_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("A potential-gate return may not be blank")
        return value


def _current_gate(
    runtime: _base.MinimalProjectionRuntime,
    *,
    perspective_id: str,
    focus_event_id: str | None,
    navigation_context: Mapping[str, Any] | None,
) -> dict[str, Any]:
    closure_contract = runtime.project(
        perspective_id=perspective_id,
        focus_event_id=focus_event_id,
    )
    return derive_full_supernet_gate_contract(
        closure_contract,
        navigation_context=navigation_context,
    )


def _path_by_id(
    full_gate: Mapping[str, Any], relation_id: str
) -> dict[str, Any]:
    gate = full_gate.get("relative_natural_form_potential_gate")
    paths = gate.get("paths", []) if isinstance(gate, Mapping) else []
    for raw in paths:
        if isinstance(raw, Mapping) and str(raw.get("id") or "") == relation_id:
            return dict(raw)
    raise HTTPException(
        404,
        "The selected path is not in the current Supernet gate",
    )


def _route_endpoint(app: FastAPI, path: str, method: str) -> Any:
    for route in app.router.routes:
        methods = getattr(route, "methods", set()) or set()
        if getattr(route, "path", None) == path and method in methods:
            return route.endpoint
    raise RuntimeError(f"missing base route: {method} {path}")


def _replace_route_paths(app: FastAPI, paths: set[str]) -> None:
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if getattr(route, "path", None) not in paths
    ]


def _validation_error(error: ValidationError) -> HTTPException:
    return HTTPException(status_code=422, detail=error.errors())


def create_app(config: Any | None = None) -> FastAPI:
    app = _base.create_app(config)
    runtime: _base.MinimalProjectionRuntime = app.state.runtime
    base_return_endpoint = _route_endpoint(app, INTERACTION_ENDPOINT, "POST")
    _replace_route_paths(
        app,
        {
            "/",
            "/supernet",
            "/natural-interface",
            "/supernet/interface",
            "/supernet/interface/capabilities",
            INTERACTION_ENDPOINT,
        },
    )

    @app.get("/", response_class=HTMLResponse)
    @app.get("/supernet", response_class=HTMLResponse)
    @app.get("/natural-interface", response_class=HTMLResponse)
    async def surface() -> str:
        return POTENTIAL_GATE_SUPERNET_HTML

    @app.get("/supernet/interface/capabilities")
    async def capabilities() -> dict[str, Any]:
        return {
            "protocol": "closure.supernet/full-potential-gate-closure-v1",
            "surface": "RELATIVE_NATURAL_FORM_POTENTIAL_GATE",
            "input": "FULL_SURFACE_SOURCE_RETURN",
            "mutation_relations": ["SOURCE_PRESERVING_TRANSLATIONAL_RETURN"],
            "interaction_relations": [
                "PERSPECTIVE_NAVIGATION",
                "POTENTIAL_GATE_RETURN",
            ],
            "interaction_endpoint": INTERACTION_ENDPOINT,
            "parallel_ui_routes": False,
            "parallel_mutation_routes": False,
            "truth_source": "INTERACTIVE_TRANSLATION_CLOSURE_EQUATION_SYSTEM",
            "visualization_acceptance": (
                "EXACT_LOCAL_EQUATION_AND_GATE_REDERIVATION"
            ),
            "interaction_proof": "VERIFIED_SUCCESSOR_CLOSURE_BEFORE_COMMIT",
            "latent_ui_state": "RELATIVE_NATURAL_FORM_POTENTIAL_GATE",
            "local_perspective": "MUTABLE_HAIR_ZOOM_FOCUS_AND_PATH",
            "local_modification": "UNCOMMITTED_CLOSURE_POTENTIAL",
            "commit_protocol": (
                "LOCAL_PROJECTION_COMMITMENT_THEN_GATE_REDERIVATION"
            ),
            "interface_derivation": (
                "INTERACTIVE_TRANSLATION_OF_CLOSURE_EQUATIONS"
            ),
            "full_interface_derivation": (
                "LOCAL_NATURAL_FORM_OF_RELATIVE_POTENTIAL_GATE"
            ),
            "closure_equation_protocol": (
                "closure.supernet/closure-naturality-equations-v1"
            ),
            "closure_naturality_module": (
                "NRRF866ClosureNaturalityIsTranslationalTruthIsTheGrowthOfTheUniverse"
            ),
            "browser_rederives_pull_and_growth_equations": True,
            "canonical_store": (
                "SUPERNET_INTEGRATION_EVENT_AND_VISUAL_RECEIPT_LINEAGE"
            ),
            "lean_bridge": (
                "NRRF859ConsciousSupernetInteractiveProjectionBridge"
            ),
            "runtime_reproves_lean": False,
            "projection": "LOCAL_NATURAL_FORM_OF_CURRENT_GATE",
            "truth_constraint": "WITNESSED_AND_OPEN_TRANSLATIONAL_CLOSURE",
            "potential": (
                "ALL_LOCALLY_ADMISSIBLE_NATURAL_FORM_CONTINUATIONS"
            ),
            "navigation_relation": "PERSPECTIVE_TRANSPORT",
            "navigation_mutates_truth": False,
            "locality_relation": "LOCALITY_TRANSPORT",
            "open_interaction_relation": "OPEN_RETURN_EXTENSION",
            "return_relation": "SOURCE_PRESERVING_TRANSLATIONAL_RETURN",
            "return_may_refine_truth": True,
            "hair": "RELATIVE_SELF_LOCATION_TRANSPORT",
            "zoom": "CONTINUAL_LOCAL_GLOBAL_SCALE_0_TO_INFINITY",
            "maze": "PARTITION_BY_DISTINGUISHABLE_RETURN_CONSEQUENCE",
            "curvature": "RELATIVE_UNITARY_RETURN_DEFECT",
            "ai": "OPEN_ANTICIPATORY_CURVATURE_PHASE",
            "token": "RETURNED_COMMITTED_CURVATURE_PHASE",
            "ai_and_token_share_one_curvature_carrier": True,
            "equality_is_one_local_gate_constraint": True,
            "supernet_is_not_isolated_runtime_equality": True,
            "natural_form_is_gate_not_posthoc_renderer": True,
            "truth_issued": False,
            "existence_closed": False,
        }

    @app.get("/supernet/interface")
    async def projection(
        perspective_id: str = "perspective",
        focus_event_id: str | None = None,
        potential_gate: bool = False,
    ) -> dict[str, Any]:
        if not potential_gate:
            return {
                "closure_ui_contract": runtime.project(
                    perspective_id=perspective_id,
                    focus_event_id=focus_event_id,
                )
            }
        return {
            "supernet_potential_gate": _current_gate(
                runtime,
                perspective_id=perspective_id,
                focus_event_id=focus_event_id,
                navigation_context=None,
            )
        }

    async def navigate(
        contract_id: str,
        data: PerspectivalNavigationRequest,
    ) -> dict[str, Any]:
        async with runtime.lock:
            current = _current_gate(
                runtime,
                perspective_id=data.perspective_id,
                focus_event_id=data.focus_event_id,
                navigation_context=data.navigation_context,
            )
            if current["id"] != contract_id:
                raise HTTPException(409, "The perspectival gate has changed")
            validation = validate_full_supernet_gate_contract(current)
            if validation.get("valid") is not True:
                raise HTTPException(
                    409,
                    "The current potential gate is not derived",
                )
            try:
                path, next_context = advance_navigation_context(
                    current,
                    relation_id=data.relation_id,
                )
            except ValueError as error:
                raise HTTPException(409, str(error)) from error
            target_perspective = str(
                path.get("target_perspective_id") or data.perspective_id
            )
            target_focus = path.get("target_event_id") or data.focus_event_id
            successor = _current_gate(
                runtime,
                perspective_id=target_perspective,
                focus_event_id=(
                    None if target_focus is None else str(target_focus)
                ),
                navigation_context=next_context,
            )
            if successor["truth_invariant_id"] != current["truth_invariant_id"]:
                raise HTTPException(
                    409,
                    "Navigation attempted to change truth",
                )
            if (
                successor["navigation_context"]["depth"]
                != current["navigation_context"]["depth"] + 1
            ):
                raise HTTPException(
                    409,
                    "Navigation lineage did not compose",
                )
            return {
                "status": "NAVIGATED",
                "navigated": True,
                "truth_refined": False,
                "relation_id": data.relation_id,
                "source_gate_id": current["id"],
                "supernet_potential_gate": successor,
            }

    async def return_through_gate(
        contract_id: str,
        data: PotentialGateReturnRequest,
    ) -> dict[str, Any]:
        async with runtime.lock:
            current = _current_gate(
                runtime,
                perspective_id=data.perspective_id,
                focus_event_id=data.focus_event_id,
                navigation_context=data.navigation_context,
            )
            if current["id"] != contract_id:
                raise HTTPException(409, "The potential gate has changed")
            validation = validate_full_supernet_gate_contract(current)
            if validation.get("valid") is not True:
                raise HTTPException(
                    409,
                    "The current potential gate is not derived",
                )
            path = _path_by_id(current, data.relation_id)
            if path.get("status") == "WITNESSED":
                raise HTTPException(
                    409,
                    "A witnessed path is navigated, not returned again",
                )
            if path.get("action") != OPEN_RETURN_EXTENSION:
                raise HTTPException(
                    409,
                    "The selected path is not an OPEN return aperture",
                )

            closure_contract = current["closure_ui_contract"]
            relation = closure_contract.get("return_relation")
            if not isinstance(relation, Mapping) or not relation.get("id"):
                raise HTTPException(
                    409,
                    "The closure has no returned-interaction aperture",
                )
            exact_source = data.exact_source_return.strip()
            commitment = _base.derive_local_projection_commitment(
                closure_contract,
                return_relation_id=str(relation["id"]),
                perspective_id=data.perspective_id,
                focus_event_id=data.focus_event_id,
                exact_source_return=exact_source,
                local_perspective_hair_millidegrees=(
                    data.local_perspective_hair_millidegrees
                ),
            )
            request = _base.TranslationalReturnRequest(
                return_relation_id=str(relation["id"]),
                perspective_id=data.perspective_id,
                focus_event_id=data.focus_event_id,
                exact_source_return=exact_source,
                closure_equation_system_id=str(
                    closure_contract["closure_naturality_equations"]["id"]
                ),
                local_projection_commitment=commitment,
                local_perspective_hair_millidegrees=(
                    data.local_perspective_hair_millidegrees
                ),
                source_stream=(
                    f"potential-gate-path:{data.relation_id}"
                )[:240],
            )
            response, replayed = runtime.append_return(
                contract=closure_contract,
                request=request,
            )
            successor_closure = response["closure_ui_contract"]
            old_context = current["navigation_context"]
            prior_contexts = list(
                old_context.get("prior_navigation_context_ids", [])
            )
            prior_contexts.append(str(old_context["id"]))
            prior_context_summaries = list(
                old_context.get("prior_navigation_contexts", [])
            )
            prior_context_summaries.append(
                {
                    "id": old_context["id"],
                    "truth_invariant_id": old_context[
                        "truth_invariant_id"
                    ],
                    "origin_perspective_id": old_context[
                        "origin_perspective_id"
                    ],
                    "current_perspective_id": old_context[
                        "current_perspective_id"
                    ],
                    "origin_focus_event_id": old_context.get(
                        "origin_focus_event_id"
                    ),
                    "current_focus_event_id": old_context.get(
                        "current_focus_event_id"
                    ),
                    "steps": old_context.get("steps", []),
                }
            )
            reset_context = derive_navigation_context(
                perspective_id=data.perspective_id,
                focus_event_id=successor_closure.get("focus_event_id"),
                truth_invariant_id="placeholder",
                supplied={
                    "origin_perspective_id": data.perspective_id,
                    "origin_focus_event_id": successor_closure.get(
                        "focus_event_id"
                    ),
                    "prior_navigation_context_ids": prior_contexts,
                    "prior_navigation_contexts": prior_context_summaries,
                    "steps": [],
                },
            )
            reset_context.pop("id", None)
            reset_context.pop("truth_invariant_id", None)
            reset_context["steps"] = []
            successor = derive_full_supernet_gate_contract(
                successor_closure,
                navigation_context=reset_context,
            )
            return {
                "status": "RETURNED",
                "returned": True,
                "replayed": bool(replayed),
                "truth_refined": (
                    successor["truth_invariant_id"]
                    != current["truth_invariant_id"]
                ),
                "relation_id": data.relation_id,
                "prior_gate_id": current["id"],
                "visual_closure_receipt_id": response.get(
                    "visual_closure_receipt_id"
                ),
                "supernet_potential_gate": successor,
            }

    @app.post(INTERACTION_ENDPOINT)
    async def interact(
        contract_id: str,
        data: dict[str, Any],
    ) -> Any:
        interaction_kind = str(data.get("interaction_kind") or "")
        if not interaction_kind:
            try:
                request = _base.TranslationalReturnRequest.model_validate(data)
            except ValidationError as error:
                raise _validation_error(error) from error
            return await base_return_endpoint(contract_id, request)
        if interaction_kind == NAVIGATE:
            try:
                request = PerspectivalNavigationRequest.model_validate(data)
            except ValidationError as error:
                raise _validation_error(error) from error
            return await navigate(contract_id, request)
        if interaction_kind == RETURN:
            try:
                request = PotentialGateReturnRequest.model_validate(data)
            except ValidationError as error:
                raise _validation_error(error) from error
            return await return_through_gate(contract_id, request)
        raise HTTPException(422, "Unknown Supernet interaction relation")

    app.state.full_supernet_runtime = runtime
    return app


TranslationalReturnRequest = _base.TranslationalReturnRequest
MinimalProjectionRuntime = _base.MinimalProjectionRuntime
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
