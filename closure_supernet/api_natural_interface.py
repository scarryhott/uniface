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
    app.version = "3.17.0"
    app.description += (
        "; the public Black Mirror is the complete operational surface of the one "
        "Supernet field: visual existence → perspective visual mirror → witnessed "
        "translational truth constraint → visual axiometry → closure-explicit meeting "
        "→ NRRF840 preimage/image closure → naturally admitted forms → a "
        "closure-transformed visual mirror → source-preserving interface return → "
        "next Sense. The semantic UI is the truth-constraint mechanism, not a static "
        "map of a closure computed elsewhere; without it Supernet truth remains OPEN. "
        "NRRF842 preserves the living source journey separately from its closed state, "
        "makes perspective an authored choice, scopes unity to one necessary gate on a "
        "shared transition rather than a rank on people, and derives the available paths "
        "as a semantic truth-curved light cone while ordinary interaction stays open. "
        "One unified runtime receipt now requires journey, mirror, SLEARN, AI, tokenomic "
        "forms, coordination, unity and UI actions to factor through that same truth "
        "closure; no external or internally isolated component has semantic authority. "
        "NRRF843 now executes the stronger direction: every perspective is a UI reading, "
        "faithful display translations share one equality, and closure is recomputed as "
        "the preimage of the displayed image. The UI therefore locates the truth "
        "constraint. The closed interaction receipt now makes the evolving "
        "source-preserved physical topology and the perspective digital potential "
        "gate two projections of that same UI truth: AI admits suggested edges for "
        "inspection, tokens admit natural interface forms, OPEN potential stays "
        "visible, and no path executes as equality or commitment without natural-form "
        "truth and independently authored consent. The interface locates the constraint "
        "and generates the closure it presents; a missing or non-mirror UI "
        "keeps the whole semantic Supernet OPEN without fallback. "
        "NRRF837 local/global composition, presentation selection, modality and freedom "
        "fibre are readings after truth; an explicitly witnessed 0↔∞ projective fold is "
        "also only a derived reading and never defines closure. "
        "The same persisted receipt is the SLEARN memory update, AI translation, "
        "tokenomic resource resolution and operational canvas topology. "
        "Perspective and eight-sheaf placement are carried on the same canonical event; "
        "no subsystem page is required for core interaction, no background autonomy is "
        "required, and presentation never manufactures truth. The primary website now "
        "contains only a generic transport mount: its complete visible scene, active "
        "perspective topology and executable controls come from a content-addressed "
        "closure UI contract. One server endpoint re-derives that contract before "
        "execution and rejects stale, altered or undeclared actions without fallback."
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
            **runtime.natural_interface.capabilities(),
            "live_sense": runtime.live_sense.capabilities(),
            "single_complete_operational_surface": True,
            "perspective_carried_by_primary_composer": True,
            "eight_sheaf_entry_on_primary_surface": True,
            "direct_relation_on_primary_surface": True,
            "direct_selection_or_rigidification_on_primary_surface": True,
            "direct_turing_return_on_primary_surface": True,
            "direct_collective_trace_on_primary_surface": True,
            "return_and_reopen_resense_on_primary_surface": True,
            "nrrf825_level_derived_on_primary_surface": True,
            "slearn_black_mirror_ai_tokenomic_visual_closure": True,
            "unified_visual_closure_receipt_persisted": True,
            "slearn_memory_changes_future_candidate_priority": True,
            "tokenomic_units_derived_from_equality_classes": True,
            "visual_network_drives_derived_next_operation": True,
            "intent_to_explainable_paths_on_primary_surface": True,
            "mutual_authorship_receipt_on_primary_surface": True,
            "nrrf837_continuum_on_primary_surface": True,
            "nrrf842_journey_state_separation": True,
            "chosen_perspective_receipt": True,
            "unity_gates_shared_trajectory_not_person": True,
            "no_human_level_ranking": True,
            "ordinary_interaction_remains_open": True,
            "truth_curved_light_cone": True,
            "semantic_not_physical_spacetime_curvature": True,
            "closure_does_not_end_living_journey": True,
            "necessary_conditions_not_sufficient": True,
            "one_translational_truth_semantic_runtime": True,
            "all_semantic_execution_factors_through_one_closure": True,
            "semantically_external_components": 0,
            "semantically_isolated_internal_components": 0,
            "open_potential_executes_as_equality": False,
            "browser_network_sensor_semantic_authority": False,
            "nrrf843_ui_is_translational_mirror": True,
            "ui_closure_is_preimage_of_displayed_image": True,
            "ui_projection_closure_matches_nrrf840": True,
            "truth_constraint_located_in_ui": True,
            "non_mirror_ui_supernet_status": "OPEN",
            "no_perspective_no_distinction": True,
            "thought_is_relation_eqvgen_of_visual_metaphor": True,
            "joint_ui_reading_unifies_natural_forms": True,
            "valuation_must_factor_through_ui_truth": True,
            "ui_price_issued": False,
            "black_mirror_evolving_physical_topology": True,
            "physical_topology_is_source_preserved_not_physical_law": True,
            "perspective_digital_potential_gate": True,
            "ai_suggestions_and_token_forms_share_ui_truth": True,
            "open_potential_remains_visible": True,
            "open_potential_can_execute_as_equality": False,
            "interaction_execution_requires_truth_unification": True,
            "token_gate_does_not_gate_ordinary_interaction": True,
            "commitment_requires_independent_human_consent": True,
            "closure_derived_from_translational_truth_axiometry_of_visual_existence": True,
            "nrrf840_exact_vis_closure_runtime_receipt": True,
            "nrrf840_closure_is_preimage_of_image": True,
            "every_admitted_member_has_source_return_observer_equality_witness": True,
            "closure_defined_by_external_limit_or_fold": False,
            "open_relation_generates_equality": False,
            "natural_forms_admitted_only_after_explicit_closure_derivation": True,
            "semantic_ui_is_perspective_visual_mirror": True,
            "semantic_ui_is_truth_constraint_location": True,
            "semantic_ui_participates_in_closure": True,
            "supernet_without_semantic_ui_status": "OPEN",
            "semantic_ui_is_static_external_network_map": False,
            "visual_geometry_is_interactive_closure_operator": True,
            "metaphorical_visual_forms_are_semantic": True,
            "thought_is_closure_of_metaphor_into_relations": True,
            "selected_form_closure_derived": True,
            "ui_is_closure_internal_natural_form": True,
            "actual_ui_render_state_factorized_through_closure": True,
            "external_renderer_is_transport_only": True,
            "external_renderer_has_no_semantic_fallback": True,
            "closure_only_ui_contract": True,
            "complete_visible_ui_derived_from_perspective_contract": True,
            "hardcoded_visible_ui_instances": False,
            "primary_browser_client_authored_action_routes": False,
            "single_server_revalidated_contract_executor": True,
            "stale_ui_contract_executes": False,
            "ui_topology_uses_active_nrrf843_perspective_reading": True,
            "open_source_boundary_claims_closure": False,
            "legacy_chart_is_transport_only": True,
            "legacy_chart_admission_defines_truth_or_closure": False,
            "ui_actions_are_returns_in_the_same_closure_environment": True,
            "local_global_compose_homomorphism_checked": True,
            "versioned_unity_selector_is_extra_data": True,
            "unity_selector_can_only_select_closure_admitted_forms": True,
            "unity_selector_network_derived": False,
            "modality_idempotence_checked": True,
            "global_equality_kernel_exposed": True,
            "global_equality_kernel_uses_only_truth_derived_compose": True,
            "authored_form_ids_define_equality": False,
            "freedom_fibre_exposed": True,
            "content_equality_preserves_actor_identity": True,
            "suggestion_equivalence_separate_from_contextual_ranking": True,
            "independent_product_gates_cannot_realise_correlated_commitment": True,
            "correlated_commitment_requires_separate_consent_relation": True,
            "partial_consent_natural_form": "COMMIT",
            "independent_human_commitment_decisions": True,
            "ai_can_suggest_but_cannot_bind": True,
            "commitment_tokens_gate_interactions": False,
            "commitment_tokens_transferable": False,
            "commitment_currency_issued": False,
            "commitment_security_enforcement": "OPEN",
            "primary_surface_component_selector": False,
            "projective_fold_derived_from_live_level": True,
            "projective_fold_requires_explicit_visual_axiometry_witness": True,
            "projective_fold_is_user_selected": False,
            "open_candidates_change_slearn_truth_memory": False,
            "two_person_E2E": "OPEN",
            "core_action_requires_subsystem_page": False,
            "canonical_pixel_layout_selected": False,
            "truth_issued_by_presentation": False,
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
            return interface
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

    def _closure_ui_nodes(root: dict[str, Any]) -> list[dict[str, Any]]:
        nodes = [root]
        for child in root.get("children", []):
            nodes.extend(_closure_ui_nodes(child))
        return nodes

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
        action_id: str,
        perspective_id: str,
        focus_event_id: str | None,
        values: dict[str, Any],
    ) -> str:
        return "closure-ui-execution:" + canonical_hash(
            {
                "contract_id": contract_id,
                "action_id": action_id,
                "perspective_id": perspective_id,
                "focus_event_id": focus_event_id,
                "values": values,
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
        values: dict[str, Any], principal_id: str | None
    ) -> None:
        if principal_id is None:
            return
        actors = [
            item
            for key in ("author", "decision_participant", "return_author")
            if isinstance((item := values.get(key)), str) and item
        ]
        if not actors or any(item != principal_id for item in actors):
            raise HTTPException(
                status_code=403,
                detail="action author must match the authenticated participant",
            )

    def _validated_contract_action(
        contract: dict[str, Any],
        action_id: str,
        submitted: dict[str, Any],
        *,
        principal_id: str | None,
    ) -> tuple[dict[str, Any], dict[str, str]]:
        validation = validate_ui_contract(contract)
        if not validation["valid"]:
            raise ValueError("The current closure UI contract is invalid")
        if contract.get("status") not in {
            CLOSURE_UI_OPEN_STATUS,
            CLOSURE_UI_WITNESSED_STATUS,
        }:
            raise ValueError("The current truth constraint admits no UI action")
        allowed = contract.get("execution", {}).get("allowed_action_ids", [])
        binding = next(
            (
                item
                for item in contract.get("action_bindings", [])
                if item.get("id") == action_id
            ),
            None,
        )
        if binding is None or action_id not in allowed:
            raise ValueError("The action is not admitted by this contract")
        if binding.get("enabled") is not True:
            raise ValueError("The contract action is not enabled")
        expected_ids = [str(item) for item in binding["input_field_ids"]]
        if set(submitted) != set(expected_ids):
            raise ValueError(
                "Submitted fields do not equal the contract input schema"
            )
        fields = {
            str(item["id"]): item
            for item in _closure_ui_nodes(contract["root"])
            if item.get("kind") in {"input", "textarea", "select"}
        }
        normalized: dict[str, str] = {}
        for field_id in expected_ids:
            value = submitted[field_id]
            if not isinstance(value, str):
                raise ValueError(
                    f"Closure UI field {field_id!r} must be text"
                )
            field = fields[field_id]
            if len(value) > int(field.get("max_length") or 0):
                raise ValueError(
                    f"Closure UI field {field_id!r} exceeds its contract limit"
                )
            if field_id in binding.get("required_field_ids", []) and not value.strip():
                raise ValueError(
                    f"Closure UI field {field_id!r} is required"
                )
            if field.get("kind") == "select":
                options = {
                    str(item.get("value"))
                    for item in field.get("options", [])
                }
                if value not in options:
                    raise ValueError(
                        f"Closure UI field {field_id!r} is outside its contract options"
                    )
            normalized[field_id] = value
        operation = str(binding["operation"])
        actor_field = {
            "OFFER_SOURCE": "author",
            "CONTINUE_INTERACTION": "author",
            "PROPOSE_AGREEMENT": "author",
            "DECIDE_AGREEMENT": "decision_participant",
            "RETURN_AGREEMENT": "return_author",
        }[operation]
        actor = normalized.get(actor_field, "")
        perspective = normalized.get("perspective", "")
        if actor != perspective:
            raise ValueError(
                "The action author must equal its authored perspective"
            )
        perspective_transition = bool(
            binding.get("immutable", {}).get("perspective_transition")
        )
        if (
            contract.get("status") == CLOSURE_UI_WITNESSED_STATUS
            and not perspective_transition
            and perspective != contract.get("perspective_id")
        ):
            raise ValueError(
                "The submitted perspective does not equal the witnessed contract"
            )
        if principal_id is not None and actor != principal_id:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"{actor_field} must match the authenticated participant"
                ),
            )
        return binding, normalized

    def _closure_ui_lines(value: str) -> list[str]:
        return list(
            dict.fromkeys(
                line.strip() for line in value.splitlines() if line.strip()
            )
        )

    def _closure_ui_optional(value: str) -> str | None:
        return value.strip() or None

    @app.post(
        "/supernet/interface/contracts/{contract_id}/execute",
        response_model=None,
    )
    async def execute_closure_ui_contract(
        contract_id: str,
        data: ClosureUIExecutionRequest,
        request: Request,
    ) -> Any:
        """Execute only an operation admitted by the freshly derived UI truth."""

        async with contract_execution_lock:
            claimed_fingerprint: str | None = None
            try:
                principal_id = _closure_ui_principal_id(request)
                claimed_fingerprint = _closure_ui_execution_fingerprint(
                    contract_id=contract_id,
                    action_id=data.action_id,
                    perspective_id=data.perspective_id,
                    focus_event_id=data.focus_event_id,
                    values=data.values,
                )
                prior_execution = (
                    runtime.supernet_store.get_closure_ui_execution(
                        claimed_fingerprint
                    )
                )
                if prior_execution is not None:
                    _bind_replayed_execution_to_principal(
                        prior_execution["request_values"], principal_id
                    )
                    if (
                        prior_execution["contract_id"] != contract_id
                        or prior_execution["action_id"] != data.action_id
                        or prior_execution["perspective_id"]
                        != data.perspective_id
                        or prior_execution["focus_event_id"]
                        != data.focus_event_id
                        or prior_execution["request_values"] != data.values
                    ):
                        raise ValueError(
                            "The execution fingerprint does not match its request"
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
                            "status": "EXECUTION_ALREADY_CLAIMED",
                            "executed": False,
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
                            "executed": False,
                            "closure_ui_contract": current,
                        },
                    )
                if current.get("focus_event_id") != data.focus_event_id:
                    return JSONResponse(
                        status_code=409,
                        content={
                            "status": "STALE_CONTRACT",
                            "executed": False,
                            "closure_ui_contract": current,
                        },
                    )
                if current.get("id") != contract_id:
                    return JSONResponse(
                        status_code=409,
                        content={
                            "status": "STALE_CONTRACT",
                            "executed": False,
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
                            "executed": False,
                            "refresh_required": True,
                            "prior_contract_id": contract_id,
                        },
                    )
                binding, values = _validated_contract_action(
                    current,
                    data.action_id,
                    data.values,
                    principal_id=principal_id,
                )
                operation = str(binding["operation"])
                immutable = dict(binding.get("immutable") or {})
                if values != data.values:
                    raise ValueError(
                        "Normalized closure fields changed the execution identity"
                    )
                prior, claimed = (
                    runtime.supernet_store.claim_closure_ui_execution(
                        fingerprint=claimed_fingerprint,
                        contract_id=contract_id,
                        action_id=data.action_id,
                        perspective_id=data.perspective_id,
                        focus_event_id=data.focus_event_id,
                        request_values=values,
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
                            "status": "EXECUTION_ALREADY_CLAIMED",
                            "executed": False,
                            "execution_fingerprint": claimed_fingerprint,
                            "prior_status": prior["status"],
                            "closure_ui_contract": current,
                        },
                    )
                result: dict[str, Any]
                if operation in {"OFFER_SOURCE", "CONTINUE_INTERACTION"}:
                    coordination_kind = values["coordination_kind"]
                    location = _closure_ui_optional(values["location"])
                    offer = CompleteInterfaceOffer(
                        exact_text=values["thought"],
                        authored_by=values["author"],
                        form_label=coordination_kind,
                        perspective_id=values["perspective"],
                        parent_event_id=(
                            str(immutable.get("parent_event_id"))
                            if immutable.get("parent_event_id")
                            else None
                        ),
                        affected_perspectives=[values["perspective"]],
                        relation_hints=[location] if location else [],
                        coordination_kind=coordination_kind,
                        location_label=location,
                        metadata={
                            "closure_only_ui_contract_id": current["id"],
                            "closure_ui_action_id": data.action_id,
                            "truth_issued": False,
                        },
                    )
                    if (
                        operation == "OFFER_SOURCE"
                        and coordination_kind == "intent"
                    ):
                        result = await complete_interface_intent(offer)
                    else:
                        result = await complete_interface_offer(offer)
                elif operation == "PROPOSE_AGREEMENT":
                    target = values["proposal_target"]
                    allowed_targets = {
                        str(item)
                        for item in immutable.get(
                            "allowed_target_event_ids", []
                        )
                    }
                    if target not in allowed_targets:
                        raise ValueError(
                            "The selected path is not admitted by this contract"
                        )
                    proposal = CompleteInterfaceCommitmentProposal(
                        intent_event_id=str(immutable["intent_event_id"]),
                        target_event_ids=[target],
                        exact_terms=values["proposal_terms"],
                        title=values["proposal_title"],
                        proposed_by=values["author"],
                        perspective_id=values["perspective"],
                        required_participant_ids=[],
                        resource_conditions=_closure_ui_lines(
                            values["proposal_resources"]
                        ),
                        metadata={
                            "closure_only_ui_contract_id": current["id"],
                            "closure_ui_action_id": data.action_id,
                            "truth_issued": False,
                        },
                    )
                    result = await complete_interface_commitment_proposal(
                        proposal
                    )
                elif operation == "DECIDE_AGREEMENT":
                    participant = values["decision_participant"]
                    decision = CompleteInterfaceCommitmentDecision(
                        participant_id=participant,
                        authored_by=participant,
                        decision=str(immutable["decision"]),
                        exact_text=values["decision_text"],
                        perspective_id=values["perspective"],
                        resource_offers=_closure_ui_lines(
                            values["decision_resources"]
                        ),
                        constraints=_closure_ui_lines(
                            values["decision_constraints"]
                        ),
                        metadata={
                            "closure_only_ui_contract_id": current["id"],
                            "closure_ui_action_id": data.action_id,
                            "truth_issued": False,
                        },
                    )
                    result = await complete_interface_commitment_decision(
                        str(immutable["proposal_id"]),
                        decision,
                    )
                elif operation == "RETURN_AGREEMENT":
                    return_data = CompleteInterfaceCommitmentReturn(
                        exact_text=values["return_text"],
                        authored_by=values["return_author"],
                        perspective_id=values["perspective"],
                        location_label=_closure_ui_optional(
                            values["return_location"]
                        ),
                        metadata={
                            "closure_only_ui_contract_id": current["id"],
                            "closure_ui_action_id": data.action_id,
                            "truth_issued": False,
                        },
                    )
                    result = await complete_interface_commitment_return(
                        str(immutable["proposal_id"]),
                        return_data,
                    )
                else:
                    raise ValueError(
                        "The contract operation is not server-allowlisted"
                    )

                focus_event_id = str(
                    result.get("focus_event_id")
                    or result.get("event_id")
                    or result.get("decision_event_id")
                    or result.get("return_event_id")
                    or result.get("proposal", {}).get("proposal_event_id")
                    or ""
                )
                if not focus_event_id:
                    raise ValueError(
                        "The executed interaction returned no closure focus"
                    )
                perspective_id = (
                    values.get("perspective")
                    or current.get("perspective_id")
                    or "participant"
                )
                interface = runtime.natural_interface.select(
                    focus_event_id=focus_event_id,
                    perspective_id=perspective_id,
                )
                successor = interface.get("closure_ui_contract") or {}
                if not validate_ui_contract(successor)["valid"]:
                    raise ValueError(
                        "The interaction did not derive a valid successor UI contract"
                    )
                response = {
                    "status": "EXECUTED",
                    "executed": True,
                    "replayed": False,
                    "execution_fingerprint": claimed_fingerprint,
                    "prior_contract_id": contract_id,
                    "action_id": data.action_id,
                    "result": result,
                    "interface": interface,
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
