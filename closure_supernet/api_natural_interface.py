from __future__ import annotations

import asyncio
import hashlib
from functools import wraps
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse

from . import api_proof_completion as base_api
from .closure_only_interface import CLOSURE_ONLY_SUPERNET_HTML
from .closure_ui_contract import (
    OPEN_STATUS as CLOSURE_UI_OPEN_STATUS,
    SCHEMA as CLOSURE_UI_SCHEMA,
    WITNESSED_STATUS as CLOSURE_UI_WITNESSED_STATUS,
    derive_open_ui_contract,
    validate_ui_contract,
)
from .complete_interface_models import (
    AuthorshipRole,
    ClosureUIExecutionRequest,
    CompleteInterfaceCollective,
    CompleteInterfaceCommitmentDecision,
    CompleteInterfaceCommitmentProposal,
    CompleteInterfaceCommitmentReturn,
    CompleteInterfaceOffer,
    CompleteInterfaceSelection,
)
from .config import RuntimeConfig
from .interaction_closure import SCHEMA as INTERACTION_CLOSURE_SCHEMA
from .living_models import (
    ActionReturnCreate,
    ActionState,
    ActionStateChange,
    CollectiveActionCreate,
    ParticipantCreate,
    PerspectiveCreate,
    ProblemCreate,
    Visibility,
)
from .natural_interface_models import NaturalInterfaceAdmissionCreate
from .nrrf837_continuum import SCHEMA as NRRF837_SCHEMA
from .nrrf837_continuum import UNITY_SELECTOR_VERSION
from .nrrf837_continuum import canonical_hash
from .nrrf842_journey import SCHEMA as NRRF842_SCHEMA
from .nrrf843_ui_mirror import SCHEMA as NRRF843_SCHEMA
from .selection_models import SelectionReadingCreate
from .supernet_models import IntegrationLens, ResourceEnvelope
from .topology_models import CollectiveTraceCreate
from .translational_truth_axiometry import SCHEMA as AXIOMETRY_SCHEMA
from .truth_constrained_runtime import SCHEMA as UNIFIED_TRUTH_RUNTIME_SCHEMA


def attach_natural_interface_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "natural_interface_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.natural_interface_routes_attached = True
    proposal_creation_lock = asyncio.Lock()
    closure_mutation_lock = asyncio.Lock()
    contract_execution_lock = asyncio.Lock()

    @app.middleware("http")
    async def serialize_closure_mutations(
        request: Request,
        call_next: Any,
    ) -> Any:
        """Keep revalidation and every HTTP mutation in one process-local order."""

        if request.method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
            async with closure_mutation_lock:
                return await call_next(request)
        return await call_next(request)
    app.version = "3.18.0"
    app.description = (
        "One active-perspective translational visualization. Exact returns induce "
        "the equality fibres, closure, natural forms, visible relation and next return."
    )

    def _event_for_occurrence(occurrence_id: str) -> dict[str, Any]:
        event = runtime.supernet_store.get_by_external_key(
            f"occurrence:{occurrence_id}"
        )
        if event is None:
            runtime.supernet_integrator.reconcile_occurrences()
            event = runtime.supernet_store.get_by_external_key(
                f"occurrence:{occurrence_id}"
            )
        if event is None:
            raise KeyError(f"No Supernet event preserves occurrence {occurrence_id}")
        return event

    def _participant_for_handle(handle: str) -> dict[str, Any]:
        normalized = handle.strip()
        for participant in runtime.living_store.list_participants(limit=20_000):
            metadata = participant.get("metadata", {})
            if metadata.get("supernet_handle") == normalized:
                return participant
            if participant.get("display_name") == normalized:
                return participant
        return runtime.living.create_participant(
            ParticipantCreate(
                display_name=normalized,
                metadata={
                    "supernet_handle": normalized,
                    "identity_assurance": "DEVELOPMENT_ATTESTATION",
                },
            )
        )

    def _problem_for_intent(event: dict[str, Any]) -> dict[str, Any]:
        occurrence_ids = set(event.get("exact_source_ids", []))
        for problem in runtime.living_store.list_problems(limit=20_000):
            if problem.get("occurrence_id") in occurrence_ids:
                return problem
        raise ValueError(
            "The intent has no living problem receipt; create it through /supernet/interface/intents"
        )

    def _perspective_for_handle(
        participant: dict[str, Any], label: str | None
    ) -> dict[str, Any] | None:
        if not label:
            return None
        for perspective in runtime.living_store.list_perspectives(limit=20_000):
            if (
                perspective.get("participant_id") == participant["id"]
                and perspective.get("label") == label
            ):
                return perspective
        return runtime.living.create_perspective(
            PerspectiveCreate(
                participant_id=participant["id"],
                label=label,
                description="Local Supernet coordination perspective",
                visibility=Visibility.PUBLIC,
                metadata={
                    "supernet_perspective_handle": label,
                    "identity_assurance": "DEVELOPMENT_ATTESTATION",
                },
            )
        )

    def _proposal_view(proposal_id: str) -> dict[str, Any]:
        proposal = runtime.supernet_store.get_commitment_proposal(proposal_id)
        consent_status = str(proposal.get("status") or "PROPOSED")
        def expose_decision(item: dict[str, Any]) -> dict[str, Any]:
            return {
                **item,
                "authorship_role": item.get("metadata", {}).get(
                    "authorship_role", "HUMAN"
                ),
                "authored_by": item.get("metadata", {}).get(
                    "authored_by", item.get("participant_id")
                ),
            }

        proposal = {
            **proposal,
            "decisions": [
                expose_decision(item) for item in proposal.get("decisions", [])
            ],
            "decision_history": [
                expose_decision(item)
                for item in proposal.get("decision_history", [])
            ],
            "coordination_settled": consent_status == "ACCEPTED",
            "monetary_settled": False,
            "legally_binding": False,
            "settled": False,
            "settled_deprecated": True,
            "non_transferable": True,
            "identity_assurance": "DEVELOPMENT_ATTESTATION",
            "consent_status": consent_status,
        }
        action_id = proposal.get("action_id")
        returned = (
            runtime.living_store.list_action_returns(
                action_id=action_id, limit=20_000
            )
            if action_id
            else []
        )
        latest_return_at = max(
            (str(item.get("created_at") or "") for item in returned),
            default=None,
        )
        unanimous_acceptance_at = proposal.get("unanimous_acceptance_at")
        return_follows_current_acceptance = bool(
            latest_return_at
            and unanimous_acceptance_at
            and latest_return_at >= str(unanimous_acceptance_at)
        )
        proposal = {
            **proposal,
            "latest_return_at": latest_return_at,
            "return_follows_current_acceptance": return_follows_current_acceptance,
        }
        if (
            returned
            and consent_status == "ACCEPTED"
            and return_follows_current_acceptance
        ):
            proposal = {
                **proposal,
                "status_before_return": consent_status,
                "status": "RETURNED",
                "closure_phase": "RETURN",
                "return_ids": [item["id"] for item in returned],
            }
        elif returned:
            if consent_status == "ACCEPTED":
                closure_phase = "ACT"
            elif consent_status == "PARTIAL":
                closure_phase = "COMMIT"
            elif consent_status in {"REJECTED", "WITHDRAWN"}:
                closure_phase = "REOPENED"
            else:
                closure_phase = "AGREE"
            proposal = {
                **proposal,
                "closure_phase": closure_phase,
                "return_ids": [item["id"] for item in returned],
                "historical_return_present": True,
            }
        return proposal

    async def _coordination_for_event(event_id: str) -> dict[str, Any] | None:
        interface = runtime.natural_interface.select(focus_event_id=event_id)
        visual = interface.get("visual_closure")
        if visual is not None and not _is_current_nrrf837_visual(visual):
            visual = await _upgrade_visual_if_stale(event_id, visual)
        return (visual or {}).get("coordination")

    def _is_current_nrrf837_visual(receipt: dict[str, Any] | None) -> bool:
        coordination = (receipt or {}).get("coordination") or {}
        continuum = coordination.get("nrrf837_continuum") or coordination.get(
            "continuum"
        ) or {}
        axiometry = (receipt or {}).get("translational_truth_axiometry") or {}
        interface = (receipt or {}).get("interface_natural_form") or {}
        journey = (receipt or {}).get("nrrf842_journey") or {}
        nrrf843_ui = (receipt or {}).get("nrrf843_ui") or {}
        interaction_closure = (receipt or {}).get("interaction_closure") or {}
        unified_runtime = (receipt or {}).get("unified_truth_runtime") or {}
        closure_ui_contract = (receipt or {}).get("closure_ui_contract") or {}
        closure_ui_validation = validate_ui_contract(closure_ui_contract)
        renderer = interface.get("renderer_contract") or {}
        return bool(
            continuum.get("schema") == NRRF837_SCHEMA
            and axiometry.get("schema") == AXIOMETRY_SCHEMA
            and journey.get("schema") == NRRF842_SCHEMA
            and nrrf843_ui.get("schema") == NRRF843_SCHEMA
            and nrrf843_ui.get("status") == "WITNESSED"
            and interaction_closure.get("schema") == INTERACTION_CLOSURE_SCHEMA
            and interaction_closure.get("status") == "WITNESSED"
            and interaction_closure.get("supernet_interaction_closed") is True
            and unified_runtime.get("schema") == UNIFIED_TRUTH_RUNTIME_SCHEMA
            and unified_runtime.get("status") == "WITNESSED"
            and closure_ui_contract.get("schema") == CLOSURE_UI_SCHEMA
            and closure_ui_contract.get("status")
            == CLOSURE_UI_WITNESSED_STATUS
            and closure_ui_validation["valid"]
            and closure_ui_contract.get("field_event_seq")
            == runtime.supernet_store.latest_event_sequence()
            and interface.get("closure_internal") is True
            and interface.get("admitted") is True
            and interface.get("render_state_factorized") is True
            and renderer.get("role") == "TRANSPORT_ONLY"
        )

    async def _upgrade_visual_if_stale(
        event_id: str,
        receipt: dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        """Append a current receipt while leaving historical receipts immutable."""

        if receipt is None or _is_current_nrrf837_visual(receipt):
            return receipt
        await runtime.live_sense.sense_event(event_id)
        return runtime.supernet_store.latest_visual_closure_receipt(event_id)

    async def _sense_commitment_lineage(
        proposal_id: str,
        *,
        primary_event_id: str,
    ) -> dict[str, Any]:
        """Refresh every participant-facing receipt in one commitment lineage."""

        proposal = _proposal_view(proposal_id)
        lineage_event_ids = [
            proposal.get("intent_event_id"),
            proposal.get("proposal_event_id"),
            *proposal.get("target_event_ids", []),
            *[
                item.get("decision_event_id")
                for item in proposal.get("decision_history", [])
            ],
        ]
        action_id = proposal.get("action_id")
        if action_id:
            for item in runtime.living_store.list_action_returns(
                action_id=action_id, limit=20_000
            ):
                lineage_event_ids.append(
                    _event_for_occurrence(item["occurrence_id"])["id"]
                )
        lineage_event_ids.extend(
            item["id"]
            for item in runtime.supernet_store.list_events(limit=100_000)
            if str(
                item.get("metadata", {}).get("commitment_proposal_id") or ""
            )
            == proposal_id
        )
        ordered = list(
            dict.fromkeys(
                str(event_id)
                for event_id in [*lineage_event_ids, primary_event_id]
                if event_id
            )
        )
        ordered = [
            event_id for event_id in ordered if event_id != primary_event_id
        ] + [primary_event_id]
        primary_sense: dict[str, Any] | None = None
        for event_id in ordered:
            sense = await runtime.live_sense.sense_event(event_id)
            if event_id == primary_event_id:
                primary_sense = sense
        if primary_sense is None:
            raise ValueError("The commitment lineage has no primary Sense event")
        return primary_sense

    async def _complete_page() -> str:
        return CLOSURE_ONLY_SUPERNET_HTML

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def completed_root() -> str:
        return await _complete_page()

    app.router.routes.insert(0, app.router.routes.pop())

    @app.get("/supernet", response_class=HTMLResponse, include_in_schema=False)
    async def completed_supernet_page() -> str:
        return await _complete_page()

    app.router.routes.insert(0, app.router.routes.pop())

    @app.get(
        "/natural-interface",
        response_class=HTMLResponse,
        include_in_schema=False,
    )
    async def natural_interface_page() -> str:
        return await _complete_page()

    app.router.routes.insert(0, app.router.routes.pop())

    @app.get("/supernet/interface/capabilities")
    async def natural_interface_capabilities() -> dict[str, Any]:
        return {
            "protocol": CLOSURE_UI_SCHEMA,
            "surface": "ACTIVE_PERSPECTIVE_TRANSLATIONAL_VISUALIZATION",
            "input": "FULL_SURFACE_SOURCE_RETURN",
            "mutation_relations": ["SOURCE_PRESERVING_TRANSLATIONAL_RETURN"],
            "parallel_ui_routes": False,
            "parallel_mutation_routes": False,
            "truth_issued": False,
        }

    @app.get("/supernet/interface")
    async def natural_interface_receipt(
        request: Request,
        focus_event_id: str | None = None,
        perspective_id: str | None = None,
    ) -> dict[str, Any]:
        try:
            principal = getattr(request.state, "principal", None) or {}
            selected_perspective = perspective_id or principal.get(
                "participant_id"
            )
            interface = runtime.natural_interface.select(
                focus_event_id=focus_event_id,
                perspective_id=selected_perspective,
            )
            focus = interface.get("focus_event") or {}
            event_id = str(focus.get("id") or "")
            visual = interface.get("visual_closure")
            if event_id and visual is not None and not _is_current_nrrf837_visual(
                visual
            ):
                await _upgrade_visual_if_stale(event_id, visual)
                interface = runtime.natural_interface.select(
                    focus_event_id=event_id,
                    perspective_id=selected_perspective,
                )
                interface["visual_receipt_upgraded_to"] = NRRF837_SCHEMA
            # The network surface is the projection itself.  Internal receipts
            # are inputs to its derivation, not parallel UI payloads.
            return {
                "closure_ui_contract": interface["closure_ui_contract"],
            }
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/supernet/visual-closure/receipts")
    async def visual_closure_receipts(limit: int = 1000) -> list[dict[str, Any]]:
        return runtime.supernet_store.list_visual_closure_receipts(
            limit=max(1, min(limit, 20_000))
        )

    @app.get("/supernet/visual-closure/receipts/{receipt_id}")
    async def visual_closure_receipt(receipt_id: str) -> dict[str, Any]:
        try:
            return runtime.supernet_store.get_visual_closure_receipt(receipt_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/supernet/events/{event_id}/visual-closure")
    async def event_visual_closure(event_id: str) -> dict[str, Any]:
        try:
            runtime.supernet_store.get_event(event_id)
            receipt = runtime.supernet_store.latest_visual_closure_receipt(event_id)
            if receipt is None:
                raise KeyError(
                    f"Supernet integration event {event_id} has no visual closure receipt"
                )
            upgraded = await _upgrade_visual_if_stale(event_id, receipt)
            if upgraded is None:
                raise KeyError(
                    f"Supernet integration event {event_id} has no visual closure receipt"
                )
            return upgraded
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/supernet/interface/admissions")
    async def admit_natural_interface(
        data: NaturalInterfaceAdmissionCreate,
    ) -> dict[str, Any]:
        try:
            return await runtime.natural_interface.admit(data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/sense")
    async def sensed_offer(data: ResourceEnvelope) -> dict[str, Any]:
        try:
            return await runtime.live_sense.offer(data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/events/{event_id}/sense-interact")
    async def sensed_interaction(
        event_id: str, data: ResourceEnvelope
    ) -> dict[str, Any]:
        try:
            return await runtime.live_sense.interact(event_id, data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/events/{event_id}/sense")
    async def sense_existing_event(event_id: str) -> dict[str, Any]:
        try:
            return await runtime.live_sense.sense_event(event_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/interface/offer")
    async def complete_interface_offer(data: CompleteInterfaceOffer) -> dict[str, Any]:
        """Enter any ordinary live form through the one interaction-time Sense path.

        Eight-sheaf placement is metadata on the exact canonical occurrence rather
        than a second source object. Specialized managers remain derived lenses.
        """

        try:
            adapter_label: str | None = None
            metadata = dict(data.metadata)
            relation_hints = list(data.relation_hints)
            relation_hints.extend(data.intent_tags)
            if data.location_label:
                relation_hints.append(data.location_label)
            if data.sheaf is not None:
                adapter_label = "embodied"
                metadata.update(
                    {
                        "sheaf": data.sheaf.value,
                        "eight_sheaf_supernet": True,
                        "hypothesis_status": (
                            "OPEN"
                            if data.sheaf.value == "UNKNOWN_UAP_HYPOTHESIS"
                            else None
                        ),
                        "alien_claim_verified": False,
                        "anomaly_is_not_explanation": True,
                    }
                )
                relation_hints.extend(["eight sheaf", data.sheaf.value])
            elif data.lens not in {None, "", "all", "source"}:
                try:
                    lens = IntegrationLens(data.lens)
                except ValueError as exc:
                    raise ValueError(f"Unknown Supernet lens: {data.lens}") from exc
                adapter_label = lens.value
                relation_hints.append(lens.value)

            envelope = ResourceEnvelope(
                exact_text=data.exact_text,
                authored_by=data.authored_by,
                form_label=data.form_label,
                source_location=data.location_label,
                perspective_id=data.perspective_id,
                affected_perspectives=data.affected_perspectives,
                capabilities=data.capabilities,
                constraints=data.constraints,
                relation_hints=list(dict.fromkeys(relation_hints)),
                adapter_label=adapter_label,
                parent_event_ids=(
                    [data.parent_event_id] if data.parent_event_id else []
                ),
                causal_predecessor_ids=(
                    [data.parent_event_id] if data.parent_event_id else []
                ),
                metadata={
                    **metadata,
                    "coordination_kind": (
                        data.coordination_kind.value
                        if data.coordination_kind is not None
                        else None
                    ),
                    "authorship_role": data.authorship_role.value,
                    "location_label": data.location_label,
                    "intent_tags": data.intent_tags,
                    "primary_black_mirror": True,
                    "exact_source_precedes_lens": True,
                    "truth_issued": False,
                },
            )
            if data.parent_event_id:
                result = await runtime.live_sense.interact(
                    data.parent_event_id, envelope
                )
            else:
                result = await runtime.live_sense.offer(envelope)
            return {
                **result,
                "focus_event_id": result["event_id"],
                "perspective_id": data.perspective_id,
                "sheaf": data.sheaf.value if data.sheaf else None,
                "lens": adapter_label or "source",
                "coordination": (
                    result.get("sense_receipt", {})
                    .get("visual_closure", {})
                    .get("coordination")
                ),
                "truth_issued": False,
            }
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/interface/intents")
    async def complete_interface_intent(
        data: CompleteInterfaceOffer,
    ) -> dict[str, Any]:
        """Preserve one thought as both a living problem and canonical intent event."""

        try:
            participant = _participant_for_handle(data.authored_by)
            perspective = _perspective_for_handle(
                participant, data.perspective_id
            )
            metadata = {
                **data.metadata,
                "authored_by": data.authored_by,
                "supernet_perspective_handle": data.perspective_id,
                "form_label": "intent",
                "coordination_kind": "intent",
                "authorship_role": AuthorshipRole.HUMAN.value,
                "location_label": data.location_label,
                "intent_tags": data.intent_tags,
                "capabilities": data.capabilities,
                "constraints": data.constraints,
                "relation_hints": list(
                    dict.fromkeys(
                        [
                            *data.relation_hints,
                            *data.intent_tags,
                            *([data.location_label] if data.location_label else []),
                        ]
                    )
                ),
                "primary_black_mirror": True,
                "exact_source_precedes_lens": True,
                "truth_issued": False,
            }
            title = " ".join(data.exact_text.strip().split())[:300]
            problem = await runtime.living.create_problem(
                ProblemCreate(
                    title=title,
                    exact_text=data.exact_text,
                    situations=[data.exact_text, *data.constraints],
                    created_by=participant["id"],
                    perspective_id=(perspective or {}).get("id"),
                    visibility=Visibility.PUBLIC,
                    affected_perspectives=data.affected_perspectives,
                    metadata=metadata,
                )
            )
            event = _event_for_occurrence(problem["occurrence_id"])
            sense = await runtime.live_sense.sense_event(event["id"])
            coordination = sense["visual_closure"].get("coordination")
            if coordination is not None:
                coordination["intent"]["problem_id"] = problem["id"]
            return {
                "event_id": event["id"],
                "focus_event_id": event["id"],
                "problem_id": problem["id"],
                "participant": participant,
                "problem": problem,
                "sense_receipt": sense,
                "coordination": coordination,
                "truth_issued": False,
            }
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    def serialize_proposal_creation(function: Any) -> Any:
        @wraps(function)
        async def serialized(*args: Any, **kwargs: Any) -> Any:
            async with proposal_creation_lock:
                return await function(*args, **kwargs)

        return serialized

    @app.post("/supernet/interface/commitments")
    @serialize_proposal_creation
    async def complete_interface_commitment_proposal(
        data: CompleteInterfaceCommitmentProposal,
    ) -> dict[str, Any]:
        """Create exact proposal terms and an OPEN collective action.

        The token is only a non-transferable receipt over selected paths.  It
        cannot consent, settle currency, block interaction, or issue truth.
        """

        try:
            intent = runtime.supernet_store.get_event(data.intent_event_id)
            problem = _problem_for_intent(intent)
            targets = [
                runtime.supernet_store.get_event(event_id)
                for event_id in data.target_event_ids
            ]
            required = list(data.required_participant_ids)
            if not required:
                required = [
                    data.proposed_by,
                    *[
                        str(target.get("authored_by") or "") for target in targets
                    ],
                ]
            required = list(dict.fromkeys(item for item in required if item))
            if data.proposed_by not in required:
                required.insert(0, data.proposed_by)
            signature = canonical_hash(
                {
                    "protocol": "closure.supernet/coordination-proposal-key-v2",
                    "intent_event_id": data.intent_event_id,
                    "target_event_ids": data.target_event_ids,
                    "proposed_by": data.proposed_by,
                    "title": data.title,
                    "exact_terms": data.exact_terms,
                    "perspective_id": data.perspective_id,
                    "required_participant_ids": required,
                    "resource_conditions": data.resource_conditions,
                    "open_assumptions": data.open_assumptions,
                    "metadata": data.metadata,
                    "unity_selector_version": UNITY_SELECTOR_VERSION,
                }
            )
            external_key = data.external_key or f"coordination-proposal:{signature}"
            existing = runtime.supernet_store.get_commitment_proposal_by_external_key(
                external_key
            )

            def same_proposal_payload(proposal: dict[str, Any] | None) -> bool:
                proposal_metadata = (proposal or {}).get("metadata") or {}
                persisted_request_metadata = proposal_metadata.get(
                    "request_metadata"
                )
                if not isinstance(persisted_request_metadata, dict):
                    persisted_request_metadata = {
                        key: value
                        for key, value in proposal_metadata.items()
                        if key
                        not in {
                            "title",
                            "proposed_by",
                            "perspective_id",
                            "identity_assurance",
                        }
                    }
                return bool(
                    proposal
                    and proposal.get("intent_event_id") == data.intent_event_id
                    and proposal.get("target_event_ids", [])
                    == data.target_event_ids
                    and proposal.get("proposed_by") == data.proposed_by
                    and proposal.get("title") == data.title
                    and proposal.get("exact_terms") == data.exact_terms
                    and proposal_metadata.get("perspective_id")
                    == data.perspective_id
                    and proposal.get("required_participant_ids", []) == required
                    and proposal.get("resource_conditions", [])
                    == data.resource_conditions
                    and proposal.get("open_assumptions", [])
                    == data.open_assumptions
                    and persisted_request_metadata == data.metadata
                    and proposal.get("unity_selector_version")
                    == UNITY_SELECTOR_VERSION
                )

            if existing is not None and not same_proposal_payload(existing):
                raise ValueError(
                    "The proposal external key is already bound to different exact terms or scope"
                )
            if existing is None and data.external_key is None:
                legacy_signature = hashlib.sha256(
                    "\x1f".join(
                        [
                            data.intent_event_id,
                            *sorted(data.target_event_ids),
                            data.proposed_by,
                            data.exact_terms,
                        ]
                    ).encode("utf-8")
                ).hexdigest()
                legacy = runtime.supernet_store.get_commitment_proposal_by_external_key(
                    f"coordination-proposal:{legacy_signature}"
                )
                if same_proposal_payload(legacy):
                    existing = legacy
            if existing is not None:
                proposal = _proposal_view(existing["id"])
                event_id = proposal["proposal_event_id"]
                return {
                    "proposal": proposal,
                    "coordination": await _coordination_for_event(event_id),
                    "truth_issued": False,
                }

            participant_rows = [_participant_for_handle(item) for item in required]
            action = await runtime.living.create_action(
                CollectiveActionCreate(
                    problem_id=problem["id"],
                    title=data.title,
                    exact_intent=data.exact_terms,
                    created_by=_participant_for_handle(data.proposed_by)["id"],
                    participant_ids=[item["id"] for item in participant_rows],
                    affected_perspectives=list(
                        dict.fromkeys(
                            [
                                *required,
                                *(
                                    [data.perspective_id]
                                    if data.perspective_id
                                    else []
                                ),
                            ]
                        )
                    ),
                    open_assumptions=list(
                        dict.fromkeys(
                            [*data.open_assumptions, *data.resource_conditions]
                        )
                    ),
                    visibility=Visibility.PUBLIC,
                    metadata={
                        **data.metadata,
                        "authored_by": data.proposed_by,
                        "perspective_id": (
                            data.perspective_id or data.proposed_by
                        ),
                        "form_label": "coordination agreement proposal",
                        "coordination_kind": "agreement",
                        "authorship_role": AuthorshipRole.HUMAN.value,
                        "source_intent_event_id": data.intent_event_id,
                        "target_event_ids": data.target_event_ids,
                        "required_participant_ids": required,
                        "resource_conditions": data.resource_conditions,
                        "open_assumptions": data.open_assumptions,
                        "unity_selector_version": UNITY_SELECTOR_VERSION,
                        "constraints": data.resource_conditions,
                        "relation_hints": [
                            "mutual authorship",
                            "agreement proposal",
                            "human consent required",
                        ],
                        "parent_event_ids": [
                            data.intent_event_id,
                            *data.target_event_ids,
                        ],
                        "causal_predecessor_ids": [
                            data.intent_event_id,
                            *data.target_event_ids,
                        ],
                        "supernet_external_key": (
                            "coordination-proposal-event:"
                            + canonical_hash(
                                {
                                    "proposal_signature": signature,
                                    "external_key": external_key,
                                }
                            )
                        ),
                        "token_transferable": False,
                        "currency_issued": False,
                        "interactions_gated": False,
                        "binding": False,
                        "truth_issued": False,
                    },
                )
            )
            proposal_event = _event_for_occurrence(action["occurrence_id"])
            stored, _created = runtime.supernet_store.create_commitment_proposal(
                {
                    "proposal_event_id": proposal_event["id"],
                    "intent_event_id": data.intent_event_id,
                    "action_id": action["id"],
                    "target_event_ids": data.target_event_ids,
                    "required_participant_ids": required,
                    "resource_conditions": data.resource_conditions,
                    "title": data.title,
                    "proposed_by": data.proposed_by,
                    "exact_terms": data.exact_terms,
                    "open_assumptions": data.open_assumptions,
                    "unity_selector_version": UNITY_SELECTOR_VERSION,
                    "external_key": external_key,
                    "metadata": {
                        **data.metadata,
                        "request_metadata": data.metadata,
                        "title": data.title,
                        "proposed_by": data.proposed_by,
                        "perspective_id": data.perspective_id,
                        "identity_assurance": "DEVELOPMENT_ATTESTATION",
                    },
                }
            )
            sense = await _sense_commitment_lineage(
                stored["id"], primary_event_id=proposal_event["id"]
            )
            return {
                "proposal": _proposal_view(stored["id"]),
                "action": action,
                "sense_receipt": sense,
                "coordination": sense["visual_closure"].get("coordination"),
                "truth_issued": False,
            }
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/interface/commitments/{proposal_id}/decisions")
    async def complete_interface_commitment_decision(
        proposal_id: str,
        data: CompleteInterfaceCommitmentDecision,
    ) -> dict[str, Any]:
        """Append one self-authored human decision; AI/token roles cannot decide."""

        try:
            if data.authorship_role != AuthorshipRole.HUMAN:
                raise ValueError(
                    f"{data.authorship_role.value} cannot accept or reject human consent"
                )
            if data.participant_id != data.authored_by:
                raise ValueError("A participant may record only their own decision")
            proposal = runtime.supernet_store.get_commitment_proposal(proposal_id)
            if data.participant_id not in proposal["required_participant_ids"]:
                raise ValueError(
                    f"Participant {data.participant_id} is not required by this proposal"
                )
            signature = hashlib.sha256(
                "\x1f".join(
                    [
                        proposal_id,
                        data.participant_id,
                        data.decision.value,
                        data.exact_text,
                    ]
                ).encode("utf-8")
            ).hexdigest()
            participant_actor = _participant_for_handle(data.participant_id)
            event_result = await runtime.interact_with_event(
                proposal["proposal_event_id"],
                ResourceEnvelope(
                    exact_text=data.exact_text,
                    authored_by=data.authored_by,
                    form_label=f"commitment decision {data.decision.value.lower()}",
                    source_id="supernet-coordination",
                    perspective_id=data.perspective_id or data.participant_id,
                    problem_id=runtime.supernet_store.get_event(
                        proposal["intent_event_id"]
                    ).get("problem_id"),
                    action_id=proposal.get("action_id"),
                    capabilities=data.resource_offers,
                    constraints=data.constraints,
                    relation_hints=[
                        "human commitment decision",
                        data.decision.value,
                        "mutual authorship",
                    ],
                    parent_event_ids=[proposal["proposal_event_id"]],
                    causal_predecessor_ids=[proposal["proposal_event_id"]],
                    affected_perspectives=proposal["required_participant_ids"],
                    external_key=data.external_key
                    or f"coordination-decision:{signature}",
                    metadata={
                        **data.metadata,
                        "coordination_kind": "commitment",
                        "authorship_role": AuthorshipRole.HUMAN.value,
                        "authored_handle": data.authored_by,
                        "internal_actor_id": participant_actor["id"],
                        "commitment_proposal_id": proposal_id,
                        "source_intent_event_id": proposal["intent_event_id"],
                        "participant_id": data.participant_id,
                        "decision": data.decision.value,
                        "resource_offers": data.resource_offers,
                        "token_transferable": False,
                        "currency_issued": False,
                        "interactions_gated": False,
                        "binding": False,
                        "truth_issued": False,
                    },
                ),
            )
            runtime.supernet_store.append_commitment_decision(
                proposal_id,
                {
                    "decision_event_id": event_result["event_id"],
                    "participant_id": data.participant_id,
                    "decision": data.decision.value,
                    "resource_offers": data.resource_offers,
                    "constraints": data.constraints,
                    "metadata": {
                        **data.metadata,
                        "authorship_role": AuthorshipRole.HUMAN.value,
                        "authored_by": data.authored_by,
                        "authored_handle": data.authored_by,
                        "internal_actor_id": participant_actor["id"],
                    },
                },
            )
            current = _proposal_view(proposal_id)
            action_id = current.get("action_id")
            if action_id:
                action = runtime.living_store.get_action(action_id)
                actor = participant_actor
                if current["consent_status"] == "ACCEPTED" and action[
                    "current_state"
                ] != ActionState.COMMITTED:
                    runtime.living.transition_action(
                        action_id,
                        ActionStateChange(
                            state=ActionState.COMMITTED,
                            reason=(
                                "Every required participant has a separate latest ACCEPT receipt"
                            ),
                            actor_id=actor["id"],
                        ),
                    )
                elif current["consent_status"] in {"REJECTED", "WITHDRAWN"} and action[
                    "current_state"
                ] == ActionState.COMMITTED:
                    runtime.living.transition_action(
                        action_id,
                        ActionStateChange(
                            state=ActionState.REOPENED,
                            reason="A required participant rejected or withdrew",
                            actor_id=actor["id"],
                        ),
                    )
            sense = await _sense_commitment_lineage(
                proposal_id, primary_event_id=event_result["event_id"]
            )
            return {
                "proposal": _proposal_view(proposal_id),
                "decision_event_id": event_result["event_id"],
                "sense_receipt": sense,
                "coordination": sense["visual_closure"].get("coordination"),
                "truth_issued": False,
            }
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/interface/commitments/{proposal_id}/returns")
    async def complete_interface_commitment_return(
        proposal_id: str,
        data: CompleteInterfaceCommitmentReturn,
    ) -> dict[str, Any]:
        """Return a real or explicitly simulated consequence to the same field."""

        try:
            proposal = _proposal_view(proposal_id)
            if proposal["consent_status"] != "ACCEPTED":
                raise ValueError(
                    "ACT and RETURN remain token-gated until every required human accepts"
                )
            action_id = proposal.get("action_id")
            if not action_id:
                raise ValueError("The proposal has no collective action")
            participant = _participant_for_handle(data.authored_by)
            enabling_decision_event_ids = [
                str(item.get("decision_event_id"))
                for item in proposal.get("decisions", [])
                if str(item.get("decision") or "").upper() == "ACCEPT"
                and item.get("decision_event_id")
            ]
            decision_history_event_ids = [
                str(item.get("decision_event_id"))
                for item in proposal.get("decision_history", [])
                if item.get("decision_event_id")
            ]
            returned = await runtime.living.add_action_return(
                action_id,
                ActionReturnCreate(
                    exact_text=data.exact_text,
                    authored_by=participant["id"],
                    affected_perspectives=data.affected_perspectives
                    or proposal["required_participant_ids"],
                    source_location=data.location_label,
                    metadata={
                        **data.metadata,
                        "authored_handle": data.authored_by,
                        "authored_by": data.authored_by,
                        "perspective_id": (
                            data.perspective_id or data.authored_by
                        ),
                        "form_label": "living action return",
                        "coordination_kind": "living_return",
                        "authorship_role": data.authorship_role.value,
                        "commitment_proposal_id": proposal_id,
                        "source_intent_event_id": proposal["intent_event_id"],
                        "action_id": action_id,
                        "location_label": data.location_label,
                        "parent_event_ids": [
                            proposal["proposal_event_id"],
                            *enabling_decision_event_ids,
                        ],
                        "causal_predecessor_ids": [
                            proposal["proposal_event_id"],
                            *enabling_decision_event_ids,
                        ],
                        "decision_history_event_ids": decision_history_event_ids,
                        "return_is_not_terminal": True,
                        "truth_issued": False,
                    },
                ),
            )
            runtime.living.reintegrate()
            return_event = _event_for_occurrence(returned["occurrence_id"])
            sense = await _sense_commitment_lineage(
                proposal_id, primary_event_id=return_event["id"]
            )
            return {
                "proposal": _proposal_view(proposal_id),
                "return": returned,
                "return_event_id": return_event["id"],
                "sense_receipt": sense,
                "coordination": sense["visual_closure"].get("coordination"),
                "truth_issued": False,
            }
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/supernet/interface/commitments/{proposal_id}")
    async def complete_interface_commitment(
        proposal_id: str,
    ) -> dict[str, Any]:
        try:
            proposal = _proposal_view(proposal_id)
            focus_event_id = proposal["proposal_event_id"]
            decisions = proposal.get("decision_history", [])
            if decisions:
                focus_event_id = decisions[-1]["decision_event_id"]
            returns = (
                runtime.living_store.list_action_returns(
                    action_id=proposal.get("action_id"), limit=20_000
                )
                if proposal.get("action_id")
                else []
            )
            if returns:
                focus_event_id = _event_for_occurrence(
                    returns[-1]["occurrence_id"]
                )["id"]
            return {
                "proposal": proposal,
                "coordination": await _coordination_for_event(focus_event_id),
                "truth_issued": False,
            }
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/supernet/interface/selections")
    async def complete_interface_selection(
        data: CompleteInterfaceSelection,
    ) -> dict[str, Any]:
        """Refine the actual live relation field through the existing NRRF790 audit."""

        try:
            matches = [
                reading
                for reading in runtime.selection_store.list_readings()
                if reading.get("source_event_id") == data.source_event_id
                and reading.get("metadata", {}).get("live_sense") is True
            ]
            if not matches:
                raise ValueError("The focused event has no live Sense relation field")
            source = max(matches, key=lambda item: item["created_at"])
            if data.selected_relation_id not in source["admissible_symbols"]:
                raise ValueError("The selected relation is not admitted by the source reading")
            reading = await runtime.selection.create_reading(
                SelectionReadingCreate(
                    name="Black Mirror authored relational refinement",
                    authored_by=data.authored_by,
                    field_symbols=source["field_symbols"],
                    admissible_symbols=source["admissible_symbols"],
                    selected_symbol=data.selected_relation_id,
                    source_event_id=data.source_event_id,
                    selection_scope="live Black Mirror relation refinement",
                    perspective_id=data.perspective_id or data.authored_by,
                    source_ids=source.get("source_ids", []),
                    metadata={
                        **data.metadata,
                        "parent_live_sense_reading_id": source["id"],
                        "reason": data.reason,
                        "authored_refinement": True,
                        "removed_alternatives_retained": True,
                        "truth_issued": False,
                    },
                )
            )
            return reading
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/interface/collective")
    async def complete_interface_collective(
        data: CompleteInterfaceCollective,
    ) -> dict[str, Any]:
        try:
            result = await runtime.topology.create_collective_trace(
                CollectiveTraceCreate(
                    authored_by=data.authored_by,
                    event_ids=data.event_ids,
                    exact_text=data.exact_text,
                    affected_perspectives=data.affected_perspectives,
                    relation_hints=["shared architecture", "collective interaction"],
                    metadata={
                        **data.metadata,
                        "perspective_id": data.perspective_id,
                        "primary_black_mirror": True,
                    },
                )
            )
            event_id = result["collective_event"]["id"]
            sense = await runtime.live_sense.sense_event(event_id)
            return {
                **result,
                "sense_receipt": sense,
                "focus_event_id": event_id,
                "truth_issued": False,
            }
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    async def _authoritative_closure_ui_contract(
        contract_id: str,
        *,
        perspective_id: str,
        focus_event_id: str | None,
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        """Re-derive the exact contract; never trust a browser-carried binding."""

        if focus_event_id:
            runtime.supernet_store.get_event(focus_event_id)
            before_interface = runtime.natural_interface.select(
                focus_event_id=focus_event_id,
                perspective_id=perspective_id,
            )
            before = before_interface.get("closure_ui_contract") or {}
            if (
                before.get("id") != contract_id
                or before.get("perspective_id") != perspective_id
                or before.get("focus_event_id") != focus_event_id
            ):
                return before, before_interface
            return before, before_interface

        current_interface = runtime.natural_interface.select(
            perspective_id=perspective_id,
        )
        current = current_interface.get("closure_ui_contract") or {}
        if current:
            return current, current_interface
        candidate = derive_open_ui_contract(perspective_id=perspective_id)
        return candidate, current_interface

    def _closure_ui_execution_fingerprint(
        *,
        contract_id: str,
        return_relation_id: str,
        perspective_id: str,
        focus_event_id: str | None,
        exact_source_return: str,
    ) -> str:
        return "closure-ui-execution:" + canonical_hash(
            {
                "contract_id": contract_id,
                "return_relation_id": return_relation_id,
                "perspective_id": perspective_id,
                "focus_event_id": focus_event_id,
                "exact_source_return": exact_source_return,
            }
        )

    def _closure_ui_principal_id(request: Request) -> str | None:
        principal = getattr(request.state, "principal", None) or {}
        role = str(principal.get("role") or "anonymous")
        participant_id = principal.get("participant_id")
        if role == "member" and not participant_id:
            raise HTTPException(
                status_code=403,
                detail="authenticated member has no bound participant identity",
            )
        if role == "operator" or not participant_id:
            return None
        return str(participant_id)

    def _bind_replayed_execution_to_principal(
        perspective_id: str, principal_id: str | None
    ) -> None:
        if principal_id is not None and perspective_id != principal_id:
            raise HTTPException(
                status_code=403,
                detail="the return perspective must match the authenticated participant",
            )

    def _validated_return_relation(
        contract: dict[str, Any],
        return_relation_id: str,
        perspective_id: str,
        focus_event_id: str | None,
        *,
        principal_id: str | None,
    ) -> dict[str, Any]:
        validation = validate_ui_contract(contract)
        if not validation["valid"]:
            raise ValueError("The current translational projection is invalid")
        if contract.get("status") not in {
            CLOSURE_UI_OPEN_STATUS,
            CLOSURE_UI_WITNESSED_STATUS,
        }:
            raise ValueError("The current truth constraint admits no return")
        relation = contract.get("return_relation")
        if not isinstance(relation, dict):
            raise ValueError("The current projection has no return relation")
        if relation.get("id") != return_relation_id:
            raise ValueError("The return relation is not the current projection relation")
        if contract.get("execution", {}).get("return_relation_id") != return_relation_id:
            raise ValueError("The return relation is not executable in this projection")
        if relation.get("kind") != "SOURCE_PRESERVING_TRANSLATIONAL_RETURN":
            raise ValueError("The submitted relation is not a translational return")
        if relation.get("creates_truth_directly") is not False:
            raise ValueError("A source return may not issue truth")
        if perspective_id != contract.get("perspective_id"):
            raise ValueError("The return perspective is not the active perspective")
        if focus_event_id != contract.get("focus_event_id"):
            raise ValueError("The return focus is not the active closure focus")
        _bind_replayed_execution_to_principal(perspective_id, principal_id)
        return relation

    @app.post(
        "/supernet/interface/projections/{contract_id}/return",
        response_model=None,
    )
    async def execute_closure_ui_return(
        contract_id: str,
        data: ClosureUIExecutionRequest,
        request: Request,
    ) -> Any:
        """Append one return, then rederive equality, closure and the UI."""

        async with contract_execution_lock:
            claimed_fingerprint: str | None = None
            try:
                principal_id = _closure_ui_principal_id(request)
                claimed_fingerprint = _closure_ui_execution_fingerprint(
                    contract_id=contract_id,
                    return_relation_id=data.return_relation_id,
                    perspective_id=data.perspective_id,
                    focus_event_id=data.focus_event_id,
                    exact_source_return=data.exact_source_return,
                )
                prior_execution = (
                    runtime.supernet_store.get_closure_ui_execution(
                        claimed_fingerprint
                    )
                )
                if prior_execution is not None:
                    _bind_replayed_execution_to_principal(
                        data.perspective_id, principal_id
                    )
                    if (
                        prior_execution["contract_id"] != contract_id
                        or prior_execution["action_id"]
                        != data.return_relation_id
                        or prior_execution["perspective_id"]
                        != data.perspective_id
                        or prior_execution["focus_event_id"]
                        != data.focus_event_id
                        or prior_execution["request_values"]
                        != {
                            "exact_source_return": data.exact_source_return
                        }
                    ):
                        raise ValueError(
                            "The return fingerprint does not match its source"
                        )
                    if (
                        prior_execution["status"] == "COMPLETED"
                        and isinstance(prior_execution.get("response"), dict)
                    ):
                        return {
                            **prior_execution["response"],
                            "replayed": True,
                        }
                    return JSONResponse(
                        status_code=409,
                        content={
                            "status": "RETURN_ALREADY_CLAIMED",
                            "returned": False,
                            "execution_fingerprint": claimed_fingerprint,
                            "prior_status": prior_execution["status"],
                        },
                    )
                current, current_interface = (
                    await _authoritative_closure_ui_contract(
                        contract_id,
                        perspective_id=data.perspective_id,
                        focus_event_id=data.focus_event_id,
                    )
                )
                if current.get("perspective_id") != data.perspective_id:
                    return JSONResponse(
                        status_code=409,
                        content={
                            "status": "STALE_CONTRACT",
                            "returned": False,
                            "closure_ui_contract": current,
                        },
                    )
                if current.get("focus_event_id") != data.focus_event_id:
                    return JSONResponse(
                        status_code=409,
                        content={
                            "status": "STALE_CONTRACT",
                            "returned": False,
                            "closure_ui_contract": current,
                        },
                    )
                if current.get("id") != contract_id:
                    return JSONResponse(
                        status_code=409,
                        content={
                            "status": "STALE_CONTRACT",
                            "returned": False,
                            "closure_ui_contract": current,
                        },
                    )
                if (
                    current.get("status") == CLOSURE_UI_WITNESSED_STATUS
                    and current.get("field_event_seq")
                    != runtime.supernet_store.latest_event_sequence()
                ):
                    return JSONResponse(
                        status_code=409,
                        content={
                            "status": "STALE_CONTRACT",
                            "returned": False,
                            "refresh_required": True,
                            "prior_contract_id": contract_id,
                        },
                    )
                relation = _validated_return_relation(
                    current,
                    data.return_relation_id,
                    data.perspective_id,
                    data.focus_event_id,
                    principal_id=principal_id,
                )
                request_values = {
                    "exact_source_return": data.exact_source_return
                }
                prior, claimed = (
                    runtime.supernet_store.claim_closure_ui_execution(
                        fingerprint=claimed_fingerprint,
                        contract_id=contract_id,
                        action_id=data.return_relation_id,
                        perspective_id=data.perspective_id,
                        focus_event_id=data.focus_event_id,
                        request_values=request_values,
                    )
                )
                if not claimed:
                    if prior["status"] == "COMPLETED" and isinstance(
                        prior.get("response"), dict
                    ):
                        return {
                            **prior["response"],
                            "replayed": True,
                        }
                    return JSONResponse(
                        status_code=409,
                        content={
                            "status": "RETURN_ALREADY_CLAIMED",
                            "returned": False,
                            "execution_fingerprint": claimed_fingerprint,
                            "prior_status": prior["status"],
                            "closure_ui_contract": current,
                        },
                    )
                # The universal return is the only primary mutation.  It enters
                # the canonical return ledger directly; no authored offer,
                # intent, agreement, token, or action manager is selected.
                exact_label = " ".join(
                    data.exact_source_return.strip().split()
                )[:240]
                focus_state_id = str(relation.get("focus_state_id") or "")
                selected_visual_value = str(
                    current.get("projection", {})
                    .get("reading", {})
                    .get(focus_state_id)
                    or data.exact_source_return
                )
                parent_event_id = (
                    str(relation.get("focus_event_id"))
                    if relation.get("focus_event_id")
                    else None
                )
                envelope = ResourceEnvelope(
                    exact_text=data.exact_source_return,
                    authored_by=data.perspective_id,
                    form_label=exact_label,
                    source_id="translational-visualization-return",
                    perspective_id=data.perspective_id,
                    affected_perspectives=[data.perspective_id],
                    parent_event_ids=[parent_event_id] if parent_event_id else [],
                    causal_predecessor_ids=(
                        [parent_event_id] if parent_event_id else []
                    ),
                    metadata={
                        "translational_visualization_id": current["id"],
                        "return_relation_id": data.return_relation_id,
                        "perspective_visual_value": selected_visual_value,
                        "source_return_displayed_in_focused_fibre": bool(
                            focus_state_id
                        ),
                        "focus_state_id": focus_state_id or None,
                        "universal_source_preserving_return": True,
                        "truth_issued": False,
                    },
                )
                result = (
                    await runtime.live_sense.interact(parent_event_id, envelope)
                    if parent_event_id
                    else await runtime.live_sense.offer(envelope)
                )

                focus_event_id = str(
                    result.get("event_id") or result.get("focus_event_id") or ""
                )
                if not focus_event_id:
                    raise ValueError(
                        "The source return produced no closure focus"
                    )
                perspective_id = data.perspective_id
                interface = runtime.natural_interface.select(
                    focus_event_id=focus_event_id,
                    perspective_id=perspective_id,
                )
                successor = interface.get("closure_ui_contract") or {}
                if not validate_ui_contract(successor)["valid"]:
                    raise ValueError(
                        "The return did not derive a valid successor projection"
                    )
                response = {
                    "status": "RETURNED",
                    "returned": True,
                    "replayed": False,
                    "execution_fingerprint": claimed_fingerprint,
                    "prior_contract_id": contract_id,
                    "return_relation_id": data.return_relation_id,
                    "focus_event_id": focus_event_id,
                    "closure_ui_contract": successor,
                    "truth_issued": False,
                }
                runtime.supernet_store.complete_closure_ui_execution(
                    claimed_fingerprint,
                    jsonable_encoder(response),
                )
                return response
            except KeyError as exc:
                if claimed_fingerprint is not None:
                    runtime.supernet_store.fail_closure_ui_execution(
                        claimed_fingerprint, str(exc)
                    )
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except ValueError as exc:
                if claimed_fingerprint is not None:
                    runtime.supernet_store.fail_closure_ui_execution(
                        claimed_fingerprint, str(exc)
                    )
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            except HTTPException as exc:
                if claimed_fingerprint is not None:
                    runtime.supernet_store.fail_closure_ui_execution(
                        claimed_fingerprint, str(exc.detail)
                    )
                raise
            except Exception as exc:
                if claimed_fingerprint is not None:
                    runtime.supernet_store.fail_closure_ui_execution(
                        claimed_fingerprint,
                        f"{type(exc).__name__}: {exc}",
                    )
                raise

    # Compatibility routes keep their URLs, but on the primary app they execute
    # interaction-time Sense rather than stopping after raw transport.
    @app.post("/supernet/integrate", include_in_schema=False)
    async def natural_surface_integrate(data: ResourceEnvelope) -> dict[str, Any]:
        return await sensed_offer(data)

    app.router.routes.insert(0, app.router.routes.pop())

    @app.post(
        "/supernet/events/{event_id}/interact",
        include_in_schema=False,
    )
    async def natural_surface_interact(
        event_id: str, data: ResourceEnvelope
    ) -> dict[str, Any]:
        return await sensed_interaction(event_id, data)

    app.router.routes.insert(0, app.router.routes.pop())

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_natural_interface_routes(base_api.create_app(config))


app = attach_natural_interface_routes(base_api.app)
