from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping


PROTOCOL = "SUPERNET-INTERACTION-CLOSURE"
SCHEMA = "closure.supernet/natural-form-interaction-closure-v1"


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def _unique(values: Iterable[Any]) -> list[str]:
    return list(
        dict.fromkeys(
            str(value)
            for value in values
            if value is not None and str(value)
        )
    )


def _continuum(coordination: Mapping[str, Any]) -> dict[str, Any]:
    value = coordination.get("continuum") or coordination.get(
        "nrrf837_continuum", {}
    )
    return dict(value) if isinstance(value, Mapping) else {}


def _active_perspective(
    *,
    nrrf843_ui: Mapping[str, Any],
    nrrf842_journey: Mapping[str, Any],
    coordination: Mapping[str, Any],
) -> str | None:
    perspectives = _unique(
        nrrf843_ui.get("ui_family", {}).get("perspective_ids", [])
    )
    candidates = _unique(
        [
            nrrf842_journey.get("chosen_perspective", {}).get(
                "perspective_id"
            ),
            coordination.get("intent", {}).get("perspective_id"),
            *perspectives,
        ]
    )
    return next((item for item in candidates if item in perspectives), None)


def _natural_form_indexes(
    truth_derivation: Mapping[str, Any],
) -> tuple[set[str], set[str], dict[str, str]]:
    form_ids: set[str] = set()
    members: set[str] = set()
    form_by_member: dict[str, str] = {}
    for form in truth_derivation.get("natural_forms", []):
        form_id = str(form.get("id") or form.get("natural_form") or "")
        if not form_id:
            continue
        form_ids.add(form_id)
        for member in _unique(form.get("members", [])):
            members.add(member)
            form_by_member[member] = form_id
    return form_ids, members, form_by_member


def _requested_form(operation: Any) -> str:
    value = str(operation or "interact").lower()
    return {
        "return": "RETURN",
        "reopen": "DISCOVER",
        "interact": "DISCOVER",
    }.get(value, value.upper())


def derive_interaction_closure(
    *,
    truth_derivation: dict[str, Any],
    nrrf843_ui: dict[str, Any],
    nrrf842_journey: dict[str, Any],
    coordination: dict[str, Any],
    ai_translation: dict[str, Any],
    tokenomic: dict[str, Any],
    visual_network: dict[str, Any],
    black_mirror: dict[str, Any],
    network_return: dict[str, Any],
) -> dict[str, Any]:
    """Close the physical/digital interaction surface through one UI truth.

    The physical topology is the evolving, source-preserved interaction field
    projected by the active perspective.  It is not a claim of physical law.
    The digital gate keeps every possible path visible, while admitting a path
    as equality or commitment only through the already-derived natural forms,
    the AI suggestion coordinate, the token form coordinate, and independent
    human consent.  No parallel UI, AI, token, or topology truth is introduced.
    """

    truth_id = truth_derivation.get("id")
    visual_closure_id = truth_derivation.get("visual_truth_closure", {}).get(
        "id"
    )
    ui_id = nrrf843_ui.get("id")
    continuum = _continuum(coordination)
    form_ids, truth_members, form_by_member = _natural_form_indexes(
        truth_derivation
    )
    truth_relation_ids = {
        str(item.get("truth_id") or "")
        for item in truth_derivation.get("truth_evaluations", [])
        if item.get("closure_admitted") is True
    }
    ai_relation_ids = {
        str(item)
        for item in ai_translation.get("admitted_relation_ids", [])
        if str(item)
    }
    token_members = {
        str(member)
        for unit in tokenomic.get("resource_units", [])
        for member in unit.get("member_occurrence_ids", [])
    }
    selected_form_id = str(continuum.get("selected_natural_form_id") or "")
    joint_gate = continuum.get("gates", {}).get("joint_product", {})
    chosen = nrrf842_journey.get("chosen_perspective", {})
    active_perspective = _active_perspective(
        nrrf843_ui=nrrf843_ui,
        nrrf842_journey=nrrf842_journey,
        coordination=coordination,
    )
    readings = nrrf843_ui.get("ui_family", {}).get("readings", {})
    reading = dict(readings.get(active_perspective, {})) if active_perspective else {}

    unification_checks = {
        "ui_translational_mirror_witnessed": bool(
            nrrf843_ui.get("status") == "WITNESSED"
            and nrrf843_ui.get("translational_mirror", {}).get("witnessed")
            is True
        ),
        "truth_constraint_located_in_ui": bool(
            nrrf843_ui.get("truth_constraint_location", {}).get("located")
            is True
        ),
        "ui_projection_is_truth_closure": bool(
            nrrf843_ui.get("closure_derivation_id") == truth_id
            and nrrf843_ui.get("visual_closure_id") == visual_closure_id
            and nrrf843_ui.get("ui_closure", {}).get(
                "closure_falls_out_from_ui_projection"
            )
            is True
        ),
        "journey_closes_at_same_truth": bool(
            nrrf842_journey.get("closed_state", {}).get("visual_closure_id")
            == visual_closure_id
        ),
        "perspective_is_authored": bool(
            active_perspective
            and chosen.get("chosen") is True
            and chosen.get("perspective_id") == active_perspective
        ),
        "continuum_factors_through_same_truth": bool(
            continuum.get("closure_derivation_id") == truth_id
        ),
        "selected_form_is_closure_derived": bool(
            selected_form_id and selected_form_id in form_ids
        ),
        "ai_relations_are_truth_witnesses": ai_relation_ids.issubset(
            truth_relation_ids
        ),
        "token_units_are_natural_form_members": bool(
            token_members and token_members.issubset(truth_members)
        ),
        "ai_token_coordinates_are_independent": bool(
            joint_gate.get("joint_gate_iff_product") is True
            and joint_gate.get("independent_coordinates") is True
        ),
    }
    unified = all(unification_checks.values())

    basis_by_display: dict[str, list[str]] = {}
    for state, display in reading.items():
        basis_by_display.setdefault(str(display), []).append(str(state))
    topology_basis = [
        {
            "display_fibre_id": display,
            "member_state_ids": sorted(members),
            "natural_form_ids": sorted(
                {
                    form_by_member[member]
                    for member in members
                    if member in form_by_member
                }
            ),
            "closure_fixed": True,
        }
        for display, members in sorted(basis_by_display.items())
    ]
    topology_nodes: list[dict[str, Any]] = []
    event_to_state: dict[str, str] = {}
    for node in visual_network.get("nodes", []):
        event_id = str(node.get("id") or "")
        state_id = str(node.get("occurrence_id") or event_id)
        event_to_state[event_id] = state_id
        topology_nodes.append(
            {
                "event_id": event_id,
                "state_id": state_id,
                "perspective_id": node.get("perspective_id"),
                "display_fibre_id": reading.get(state_id),
                "natural_form_id": form_by_member.get(state_id),
                "location_label": node.get("location_label"),
                "source_preserved": state_id in truth_members,
                "physical_world_return": bool(
                    str(node.get("authorship_role") or "").upper()
                    == "LIVING_SYSTEM"
                    or black_mirror.get("physical_sensor_attached") is True
                ),
            }
        )
    topology_relations = []
    for edge in visual_network.get("edges", []):
        source_event = str(edge.get("source") or "")
        target_event = str(edge.get("target") or "")
        source_state = event_to_state.get(source_event, source_event)
        target_state = event_to_state.get(target_event, target_event)
        truth_witnessed = bool(edge.get("generates_equality") is True)
        topology_relations.append(
            {
                "id": edge.get("id"),
                "source_event_id": source_event,
                "target_event_id": target_event,
                "source_state_id": source_state,
                "target_state_id": target_state,
                "relation_type": edge.get("relation_type"),
                "truth_constraint_status": (
                    "WITNESSED" if truth_witnessed else "OPEN"
                ),
                "same_display_fibre": bool(
                    reading.get(source_state) is not None
                    and reading.get(source_state) == reading.get(target_state)
                ),
                "generates_topological_identification": truth_witnessed,
                "visible_potential": True,
            }
        )
    journey = nrrf842_journey.get("journey", {})
    topology_frames = []
    for index, step in enumerate(journey.get("steps", []), start=1):
        state_ids = _unique(step.get("exact_source_ids", []))
        topology_frames.append(
            {
                "index": index,
                "event_id": step.get("event_id"),
                "stage": step.get("stage"),
                "perspective_id": step.get("perspective_id"),
                "source_state_ids": state_ids,
                "display_fibre_ids": _unique(
                    reading.get(state) for state in state_ids
                ),
                "source_preserved": True,
            }
        )

    gates = continuum.get("gates", {})
    ai_gate = gates.get("ai", {})
    token_gate = gates.get("token", {})
    admitted_interactions = {
        str(item) for item in ai_gate.get("admitted_interactions", [])
    }
    admitted_forms = _unique(token_gate.get("admitted_forms", []))
    gated_forms = _unique(token_gate.get("gated_forms", []))
    settlement = continuum.get("one_tap", {}).get("settlement", {})
    potentials: list[dict[str, Any]] = []
    for path in nrrf842_journey.get("truth_curved_light_cone", {}).get(
        "paths", []
    ):
        target_id = str(path.get("target_event_id") or "")
        shared_form_id = str(path.get("shared_natural_form_id") or "")
        truth_witnessed = bool(
            str(path.get("truth_constraint_status") or "OPEN").upper()
            == "WITNESSED"
            and shared_form_id in form_ids
        )
        ai_admitted = bool(not target_id or target_id in admitted_interactions)
        potentials.append(
            {
                "id": path.get("id"),
                "target_event_id": path.get("target_event_id"),
                "kind": path.get("kind"),
                "label": path.get("label"),
                "shared_natural_form_id": shared_form_id or None,
                "truth_constraint_status": (
                    "WITNESSED" if truth_witnessed else "OPEN"
                ),
                "ai_suggestion_admitted": ai_admitted,
                "visible_for_inspection": bool(unified and ai_admitted),
                "can_create_nonbinding_proposal": bool(
                    unified and ai_admitted and target_id
                ),
                "executes_as_equality": bool(unified and truth_witnessed),
                "can_become_commitment": bool(
                    unified
                    and truth_witnessed
                    and settlement.get("settled") is True
                ),
                "remains_connected_potential": True,
            }
        )

    next_operation = network_return.get("next_operation", {})
    operation = str(next_operation.get("action") or "interact")
    requested_form = _requested_form(operation)
    ordinary = operation.lower() in {"interact", "reopen"}
    higher = requested_form in {"AGREE", "COMMIT", "ACT", "RETURN"}
    token_passes = bool(
        ordinary
        or (
            requested_form in admitted_forms
            and (
                requested_form not in gated_forms
                or str(token_gate.get("status") or "OPEN").upper()
                == "SATISFIED"
            )
        )
    )
    unity_gate = nrrf842_journey.get("unity_gate", {})
    unity_passes = bool(
        not higher
        or unity_gate.get("necessary_condition_status") == "SATISFIED"
    )
    operation_enabled = bool(unified and token_passes and unity_passes)

    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "closure_derivation_id": truth_id,
        "visual_closure_id": visual_closure_id,
        "nrrf843_ui_id": ui_id,
        "status": "WITNESSED" if unified else "OPEN",
        "supernet_interaction_closed": unified,
        "one_interaction_surface": unified,
        "unification_constraint": {
            "status": "WITNESSED" if unified else "OPEN",
            "checks": unification_checks,
            "all_components_share_one_translational_truth": unified,
            "parallel_truth_runtime_present": False,
        },
        "black_mirror_physical_topology": {
            "status": "WITNESSED" if unified else "OPEN",
            "kind": "EVOLVING_SOURCE_PRESERVED_PERSPECTIVE_TOPOLOGY",
            "active_perspective_id": active_perspective,
            "projection_reading": reading,
            "closure_formula": "uiClosure(r,A) = r⁻¹(r(A))",
            "topology_basis": topology_basis,
            "nodes": topology_nodes,
            "relations": topology_relations,
            "evolution_frames": topology_frames,
            "evolves_with_source_journey": True,
            "closure_is_generated_by_projection": unified,
            "physical_world_status": (
                "CONNECTED_SOURCE_RETURN"
                if black_mirror.get("physical_sensor_attached") is True
                else "OPEN_NO_PHYSICAL_SENSOR"
            ),
            "physical_law_claimed": False,
            "canonical_physical_topology_claimed": False,
            "static_external_map": False,
        },
        "perspective_digital_potential_gate": {
            "status": "WITNESSED" if unified else "OPEN",
            "active_perspective_id": active_perspective,
            "potentials": potentials,
            "potential_count": len(potentials),
            "truth_witnessed_count": sum(
                item["truth_constraint_status"] == "WITNESSED"
                for item in potentials
            ),
            "open_potential_count": sum(
                item["truth_constraint_status"] == "OPEN"
                for item in potentials
            ),
            "open_potential_remains_visible": True,
            "open_potential_executes_as_equality": False,
            "ai_gate": {
                "status": ai_gate.get("status", "SUGGESTION_ONLY"),
                "admitted_interaction_ids": sorted(admitted_interactions),
                "can_consent": False,
                "can_bind": False,
                "controls_token_form_admission": False,
            },
            "token_gate": {
                "status": token_gate.get("status", "OPEN"),
                "admitted_forms": admitted_forms,
                "gated_forms": gated_forms,
                "gates_ordinary_interactions": False,
                "can_consent": False,
                "can_bind": False,
                "currency_issued": False,
            },
            "joint_gate_is_product": bool(
                joint_gate.get("joint_gate_iff_product") is True
            ),
            "correlated_commitment_is_separate": True,
            "independent_human_consent_required": True,
        },
        "active_operation": {
            "operation": operation,
            "label": next_operation.get("label"),
            "requested_natural_form": requested_form,
            "ordinary_interaction": ordinary,
            "truth_unification_passes": unified,
            "token_form_gate_passes": token_passes,
            "unity_potential_gate_passes": unity_passes,
            "enabled": operation_enabled,
            "status": "ADMITTED" if operation_enabled else "GATED_OPEN",
            "ordinary_interaction_remains_available": True,
        },
        "claims": {
            "truth_issued": False,
            "currency_issued": False,
            "legal_binding_claimed": False,
            "physical_law_claimed": False,
            "global_optimum_claimed": False,
            "human_worth_scored": False,
        },
    }
    body["id"] = _digest("interaction-closure", body)
    return body


__all__ = ["PROTOCOL", "SCHEMA", "derive_interaction_closure"]
