from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable


PROTOCOL = "NRRF842"
SCHEMA = "closure.supernet/nrrf842-journey-unity-v1"
FORMAL_MODULE = (
    "NRRF842NecessaryConditionsClosureNotJourneyLevelsRequireUnityChosenPerspective"
)

BASE_PHASES = frozenset({"DISCOVER", "CONNECT"})
HIGHER_PHASES = frozenset({"AGREE", "COMMIT", "ACT", "RETURN"})


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


def _event_order(event: dict[str, Any]) -> tuple[int, str, str]:
    try:
        sequence = int(event.get("seq") or 0)
    except (TypeError, ValueError):
        sequence = 0
    return (
        sequence,
        str(event.get("created_at") or ""),
        str(event.get("id") or ""),
    )


def _ancestry(
    focus_event: dict[str, Any],
    field_events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Return source-preserved ancestry without flattening its causal edges."""

    events = {
        str(event.get("id") or ""): event
        for event in field_events
        if event.get("id")
    }
    focus_id = str(focus_event.get("id") or "")
    if focus_id:
        events.setdefault(focus_id, focus_event)

    visited: set[str] = set()
    pending = [focus_id] if focus_id else []
    edges: list[dict[str, str]] = []
    while pending:
        event_id = pending.pop()
        if not event_id or event_id in visited:
            continue
        visited.add(event_id)
        event = events.get(event_id)
        if event is None:
            continue
        for parent_id in _unique(event.get("parent_event_ids", [])):
            edges.append({"source_event_id": parent_id, "target_event_id": event_id})
            if parent_id not in visited:
                pending.append(parent_id)

    history_events = sorted(
        (events[event_id] for event_id in visited if event_id in events),
        key=_event_order,
    )
    return history_events, sorted(
        edges,
        key=lambda edge: (edge["source_event_id"], edge["target_event_id"]),
    )


def _history_step(event: dict[str, Any]) -> dict[str, Any]:
    metadata = event.get("metadata", {})
    return {
        "event_id": str(event.get("id") or ""),
        "parent_event_ids": _unique(event.get("parent_event_ids", [])),
        "stage": str(event.get("current_stage") or "SOURCE_PRESERVED"),
        "verdict": str(event.get("current_verdict") or "OPEN"),
        "authored_by": event.get("authored_by"),
        "authorship_role": str(metadata.get("authorship_role") or "HUMAN"),
        "perspective_id": (
            event.get("perspective_id")
            or metadata.get("perspective_id")
        ),
        "form_label": event.get("form_label"),
        "exact_source_ids": _unique(event.get("exact_source_ids", [])),
        "created_at": event.get("created_at"),
    }


def _chosen_perspective(focus_event: dict[str, Any]) -> dict[str, Any]:
    metadata = focus_event.get("metadata", {})
    role = str(metadata.get("authorship_role") or "HUMAN").upper()
    direct = focus_event.get("perspective_id")
    metadata_value = metadata.get("perspective_id")
    perspective_id = direct or metadata_value
    source = (
        "EVENT_PERSPECTIVE"
        if direct
        else "SOURCE_METADATA"
        if metadata_value
        else "OPEN"
    )
    living_choice = bool(perspective_id) and role in {"HUMAN", "LIVING_SYSTEM"}
    return {
        "perspective_id": perspective_id,
        "status": "CHOSEN" if living_choice else "OPEN",
        "chosen": living_choice,
        "choice_source": source,
        "authorship_role": role,
        "free_choice_of_perspective": True,
        "ai_may_suggest_not_choose_for_a_living_author": True,
        "no_fixed_perspective_is_universal": True,
        "distinct_perspectives_may_realise_one_unity": True,
        "not_choosing_is_a_cap_not_a_contradiction": True,
    }


def _phase(coordination: dict[str, Any]) -> str:
    continuum = coordination.get("continuum") or coordination.get(
        "nrrf837_continuum", {}
    )
    return str(
        continuum.get("modality", {}).get("operator")
        or coordination.get("natural_form_operator", {}).get("natural_form")
        or "DISCOVER"
    ).upper()


def _participant_unity(
    coordination: dict[str, Any],
) -> dict[str, Any]:
    proposal = coordination.get("active_proposal") or {}
    continuum = coordination.get("continuum") or coordination.get(
        "nrrf837_continuum", {}
    )
    settlement = continuum.get("one_tap", {}).get("settlement", {})
    required = _unique(
        proposal.get("required_participant_ids", [])
        or settlement.get("required_participant_ids", [])
    )
    decisions = list(
        proposal.get("decision_history", [])
        or proposal.get("decisions", [])
    )
    latest_decisions: dict[str, dict[str, Any]] = {}
    for decision in decisions:
        participant = str(
            decision.get("participant_id")
            or decision.get("authored_by")
            or ""
        )
        if participant:
            latest_decisions[participant] = decision
    human_acceptances = list(settlement.get("human_acceptances", []))
    accepted = _unique(
        [
            *[
                item.get("participant_id")
                for item in human_acceptances
                if str(item.get("authorship_role") or "HUMAN").upper()
                == "HUMAN"
            ],
            *[
                item.get("participant_id") or item.get("authored_by")
                for item in latest_decisions.values()
                if str(item.get("decision") or item.get("status") or "").upper()
                == "ACCEPT"
                and str(item.get("authorship_role") or "HUMAN").upper()
                == "HUMAN"
                and (
                    not item.get("authored_by")
                    or str(item.get("authored_by"))
                    == str(item.get("participant_id"))
                )
            ],
        ]
    )
    rejected = _unique(
        item.get("participant_id") or item.get("authored_by")
        for item in latest_decisions.values()
        if str(item.get("decision") or item.get("status") or "").upper()
        in {"REJECT", "REJECTED", "WITHDRAW", "WITHDRAWN"}
    )
    pending = [item for item in required if item not in accepted]
    if required:
        reached = not pending and not rejected
        basis = "EVERY_REQUIRED_HUMAN_AUTHORED_ACCEPTANCE" if reached else "OPEN"
    else:
        reached = True
        basis = "LOCAL_TRAJECTORY_NO_COMMUNITY_ASSERTED"
    return {
        "community_asserted": bool(required),
        "required_participant_ids": required,
        "accepted_participant_ids": accepted,
        "pending_participant_ids": pending,
        "dissenting_participant_ids": rejected,
        "unity_reached": reached,
        "unity_basis": basis,
        "community_level_is_shared_transition_only": True,
        "one_unresolved_member_keeps_shared_ascent_open": bool(
            required and (pending or rejected)
        ),
        "member_access_restricted": False,
        "member_ranked": False,
    }


def _unity_gate(
    *,
    focus_event: dict[str, Any],
    coordination: dict[str, Any],
    chosen_perspective: dict[str, Any],
) -> dict[str, Any]:
    continuum = coordination.get("continuum") or coordination.get(
        "nrrf837_continuum", {}
    )
    selected_form_id = continuum.get("selected_natural_form_id")
    phase = _phase(coordination)
    community = _participant_unity(coordination)
    local_unity = bool(chosen_perspective["chosen"] and selected_form_id)
    unity_reached = bool(local_unity and community["unity_reached"])
    higher_requested = phase in HIGHER_PHASES
    condition_status = (
        "SATISFIED" if not higher_requested or unity_reached else "OPEN"
    )
    return {
        "id": _digest(
            "unity-gate",
            {
                "event": focus_event.get("id"),
                "phase": phase,
                "form": selected_form_id,
                "perspective": chosen_perspective.get("perspective_id"),
                "community": community,
            },
        ),
        "scope": "SHARED_TRAJECTORY_NOT_PERSON",
        "requested_phase": phase,
        "base_phases": sorted(BASE_PHASES),
        "higher_phases": sorted(HIGHER_PHASES),
        "higher_transition_requested": higher_requested,
        "selected_natural_form_id": selected_form_id,
        "local_unity_reached": local_unity,
        "unity_reached": unity_reached,
        "necessary_condition_status": condition_status,
        "transition_status": condition_status,
        "transition_authorized_by_this_gate": False,
        "unity_is_one_potential_gate": True,
        "unity_not_sufficient_for_ascent": True,
        "gate_checked_at_every_stage": True,
        "ordinary_interaction_open": True,
        "interactions_gated": False,
        "human_worth_scored": False,
        "person_ranked": False,
        "community": community,
    }


def _truth_curved_light_cone(
    *,
    focus_event: dict[str, Any],
    perspective_visual_mirror: dict[str, Any],
    visual_truth_closure: dict[str, Any],
    coordination: dict[str, Any],
    unity_gate: dict[str, Any],
) -> dict[str, Any]:
    paths: list[dict[str, Any]] = []
    for path in coordination.get("paths", []):
        why = path.get("why", {})
        if not isinstance(why, dict):
            why = {"explanation": str(why)}
        shared_form = why.get("shared_natural_form_id") or path.get(
            "natural_form_id"
        )
        status = str(
            why.get("formal_suggestion_status")
            or why.get("translational_truth_status")
            or "OPEN"
        ).upper()
        path_id = str(path.get("id") or "")
        target_id = str(path.get("target_event_id") or "")
        paths.append(
            {
                "id": path_id or _digest("light-ray", [target_id, shared_form]),
                "target_event_id": target_id,
                "kind": str(path.get("kind") or "INTERACTION").upper(),
                "label": path.get("label"),
                "shared_natural_form_id": shared_form,
                "truth_constraint_status": status,
                "unity_potential": bool(shared_form),
                "local_freedom_preserved": True,
                "interaction_available": True,
                "why": why,
            }
        )
    if not paths:
        paths.append(
            {
                "id": _digest("light-ray", [focus_event.get("id"), "OPEN"]),
                "target_event_id": None,
                "kind": "OPEN_CONTINUATION",
                "label": "Continue the living field",
                "shared_natural_form_id": None,
                "truth_constraint_status": "OPEN",
                "unity_potential": False,
                "local_freedom_preserved": True,
                "interaction_available": True,
                "why": {"reason": "No source-preserved relation path is yet witnessed."},
            }
        )
    witnessed_count = sum(
        path["truth_constraint_status"] == "WITNESSED" for path in paths
    )
    return {
        "id": _digest(
            "truth-light-cone",
            {
                "event": focus_event.get("id"),
                "mirror": perspective_visual_mirror.get("id"),
                "closure": visual_truth_closure.get("id"),
                "paths": paths,
            },
        ),
        "kind": "SEMANTIC_TRUTH_CURVATURE_NOT_PHYSICAL_SPACETIME",
        "physical_light_cone_claimed": False,
        "origin": {
            "focus_event_id": str(focus_event.get("id") or ""),
            "perspective_id": chosen_perspective_id(focus_event),
            "visual_mirror_id": perspective_visual_mirror.get("id"),
            "visual_closure_id": visual_truth_closure.get("id"),
        },
        "paths": paths,
        "path_count": len(paths),
        "witnessed_truth_constraint_count": witnessed_count,
        "open_path_count": len(paths) - witnessed_count,
        "curvature": {
            "basis": "RELATIVE_TRANSLATIONAL_TRUTH_CONSTRAINTS",
            "changes_with_perspective": True,
            "canonical_geometry_claimed": False,
            "unity_gate_status": unity_gate["necessary_condition_status"],
        },
        "natural_language": {
            "primitives": [
                "FORM",
                "PERSPECTIVE",
                "RELATION",
                "TRAJECTORY",
                "TRUTH_CONSTRAINT",
                "RETURN",
            ],
            "continuation_grammar": (
                "FORM + PERSPECTIVE + RELATION + TRAJECTORY + "
                "TRUTH_CONSTRAINT -> NATURAL_CONTINUATION"
            ),
            "metaphorical_forms_are_semantic": True,
            "thought_derivation": (
                "THOUGHT_IS_CLOSURE_OF_METAPHOR_INTO_RELATIONS"
            ),
        },
    }


def chosen_perspective_id(event: dict[str, Any]) -> Any:
    metadata = event.get("metadata", {})
    return event.get("perspective_id") or metadata.get("perspective_id")


def derive_nrrf842_journey_receipt(
    *,
    focus_event: dict[str, Any],
    field_events: list[dict[str, Any]],
    perspective_visual_mirror: dict[str, Any],
    visual_truth_closure: dict[str, Any],
    natural_forms: list[dict[str, Any]],
    coordination: dict[str, Any],
) -> dict[str, Any]:
    """Derive the living trajectory beside, never inside, its closed state.

    This is the executable product bridge for NRRF842.  It records necessary
    conditions and a unity gate without treating either as sufficient, and it
    never converts a shared transition level into a rank or access rule for a
    person.
    """

    history_events, causal_edges = _ancestry(focus_event, field_events)
    history_steps = [_history_step(event) for event in history_events]
    history_id = _digest(
        "journey",
        {"steps": history_steps, "causal_edges": causal_edges},
    )
    closure_state_basis = {
        "visual_closure_id": visual_truth_closure.get("id"),
        "natural_form_ids": _unique(
            form.get("id") or form.get("natural_form") for form in natural_forms
        ),
    }
    closure_state = {
        **closure_state_basis,
        "focus_member_id": str(
            (focus_event.get("exact_source_ids") or [focus_event.get("id") or ""])[0]
        ),
        "focus_member_is_provenance_not_closed_state_identity": True,
    }
    closure_state["id"] = _digest("closed-state", closure_state_basis)
    perspective = _chosen_perspective(focus_event)
    unity_gate = _unity_gate(
        focus_event=focus_event,
        coordination=coordination,
        chosen_perspective=perspective,
    )
    light_cone = _truth_curved_light_cone(
        focus_event=focus_event,
        perspective_visual_mirror=perspective_visual_mirror,
        visual_truth_closure=visual_truth_closure,
        coordination=coordination,
        unity_gate=unity_gate,
    )
    return {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "formal_module": FORMAL_MODULE,
        "id": _digest(
            "nrrf842",
            {
                "history": history_id,
                "closed_state": closure_state["id"],
                "perspective": perspective,
                "unity_gate": unity_gate["id"],
                "light_cone": light_cone["id"],
            },
        ),
        "journey": {
            "id": history_id,
            "focus_event_id": str(focus_event.get("id") or ""),
            "steps": history_steps,
            "step_count": len(history_steps),
            "causal_edges": causal_edges,
            "source_preserved": True,
            "continues_after_closed_state": True,
        },
        "closed_state": closure_state,
        "state_journey_separation": {
            "closure_is_journey": False,
            "same_closed_state_identifies_histories": False,
            "closure_state_local": True,
            "closed_state_can_continue": True,
            "history_preserved_outside_truth_quotient": True,
        },
        "necessary_conditions": {
            "conditions": [
                "SOURCE_PRESERVED",
                "PERSPECTIVE_VISUALIZED",
                "TRUTH_CONSTRAINT_PRESENT",
                "CLOSURE_DERIVED",
            ],
            "known_conditions_present": all(
                [
                    bool(history_steps),
                    bool(perspective_visual_mirror.get("id")),
                    bool(visual_truth_closure.get("id")),
                    bool(natural_forms),
                ]
            ),
            "necessary_not_sufficient": True,
            "conditions_are_sufficient": False,
            "complete_living_system_claimed": False,
        },
        "chosen_perspective": perspective,
        "unity_gate": unity_gate,
        "truth_curved_light_cone": light_cone,
        "claims": {
            "truth_issued": False,
            "physical_light_cone_claimed": False,
            "complete_living_system_claimed": False,
            "economic_value_claimed": False,
            "human_level_claimed": False,
            "ordinary_interaction_remains_open": True,
        },
    }
