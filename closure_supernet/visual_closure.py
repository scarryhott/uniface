from __future__ import annotations

from collections import Counter
from typing import Any

from .closure_ui_contract import derive_closure_ui_contract
from .coordination import build_coordination_receipt
from .interaction_closure import derive_interaction_closure
from .nrrf842_journey import derive_nrrf842_journey_receipt
from .nrrf843_ui_mirror import derive_nrrf843_ui_receipt
from .translational_truth_axiometry import (
    derive_closure,
    derive_interface_natural_form,
)
from .truth_constrained_runtime import derive_unified_truth_runtime


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if str(value)))


def learned_relation_memory(
    receipts: list[dict[str, Any]],
) -> dict[str, int]:
    """Count unique admitted relation witnesses already retained by SLEARN."""

    witnessed: dict[str, str] = {}
    for receipt in receipts:
        for relation in receipt.get("visual_network", {}).get("edges", []):
            if relation.get("generates_equality") is not True:
                continue
            relation_id = str(
                relation.get("id") or relation.get("candidate_relation_id") or ""
            )
            relation_type = str(relation.get("relation_type") or "OPEN_RELATION")
            if relation_id:
                witnessed[relation_id] = relation_type
    return dict(sorted(Counter(witnessed.values()).items()))


def _event_indexes(
    events: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    by_id = {str(event["id"]): event for event in events}
    by_occurrence: dict[str, dict[str, Any]] = {}
    for event in events:
        for occurrence_id in event.get("exact_source_ids", []):
            # Events arrive in field sequence.  Keep the first event that
            # source-preserved an occurrence rather than replacing it with a
            # later translation/reconciliation event that merely references
            # the same occurrence.  Resource capabilities and constraints
            # belong to the source event; derived relation events are lenses.
            by_occurrence.setdefault(str(occurrence_id), event)
    return by_id, by_occurrence


def _resource_units(
    closure_level: dict[str, Any],
    event_by_occurrence: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    forms = closure_level.get("truth_closes_level_alone", {}).get(
        "natural_forms", []
    )
    for index, form in enumerate(forms):
        members = [str(item) for item in form.get("members", [])]
        events = [
            event_by_occurrence[item]
            for item in members
            if item in event_by_occurrence
        ]
        units.append(
            {
                "id": f"closure-unit:{closure_level['level_id']}:{index}",
                "natural_form": str(form.get("natural_form") or f"L/{index}"),
                "member_occurrence_ids": members,
                "member_event_ids": _unique(
                    [str(event["id"]) for event in events]
                ),
                "member_contributions": [
                    {
                        "event_id": str(event["id"]),
                        "authored_by": event.get("authored_by"),
                        "authorship_role": event.get("metadata", {}).get(
                            "authorship_role", "HUMAN"
                        ),
                        "member_occurrence_ids": [
                            occurrence_id
                            for occurrence_id in event.get("exact_source_ids", [])
                            if str(occurrence_id) in members
                        ],
                        "capabilities": list(event.get("capabilities", [])),
                        "constraints": list(event.get("constraints", [])),
                    }
                    for event in events
                ],
                "capabilities": sorted(
                    {
                        str(capability)
                        for event in events
                        for capability in event.get("capabilities", [])
                    }
                ),
                "constraints": sorted(
                    {
                        str(constraint)
                        for event in events
                        for constraint in event.get("constraints", [])
                    }
                ),
                "admission_basis": "one natural-form class of the active equality level",
            }
        )
    return units


def _next_operation(
    event: dict[str, Any],
    closure_level: dict[str, Any],
    admitted_relations: list[dict[str, Any]],
) -> dict[str, Any]:
    stage = str(event.get("current_stage") or "SOURCE_PRESERVED")
    endpoint = str(closure_level.get("endpoint") or "OPEN")
    if stage == "RETURNED":
        action, label, reason = (
            "reopen",
            "Reopen returned field",
            "A return is present, so reopening is the next source-preserving operation.",
        )
    elif stage == "REOPENED":
        action, label, reason = (
            "interact",
            "Next Sense",
            "The return has reopened and can now be sensed with a new occurrence.",
        )
    elif admitted_relations and endpoint in {"⊤", "⊥=⊤"}:
        action, label, reason = (
            "return",
            "Return admitted closure",
            "The active returns close the sensed states to one natural form.",
        )
    else:
        action, label, reason = (
            "interact",
            "Continue relative closure",
            "The current level remains relative or has no admitted relation; the next occurrence must extend the field.",
        )
    return {
        "action": action,
        "label": label,
        "reason": reason,
        "derived_from": [stage, endpoint, len(admitted_relations)],
        "user_selected_phase": False,
    }


def build_visual_closure_receipt(
    *,
    event: dict[str, Any],
    source_occurrences: list[dict[str, Any]],
    relation_receipts: list[dict[str, Any]],
    closure_level: dict[str, Any],
    selection_reading: dict[str, Any] | None,
    prior_receipts: list[dict[str, Any]],
    field_events: list[dict[str, Any]],
    field_occurrences: list[dict[str, Any]],
    commitment_proposals: list[dict[str, Any]],
    living_problems: list[dict[str, Any]],
    living_actions: list[dict[str, Any]],
    living_returns: list[dict[str, Any]],
    field_event_seq: int | None = None,
) -> dict[str, Any]:
    """Derive one operational UI receipt from one interaction-time Sense.

    The receipt is not a dashboard summary.  It is the source-reversible data
    used by the primary canvas and its derived next action.  SLEARN memory is
    the accumulated set of admitted relation witnesses, AI translation is the
    existing interpretation/admission pipeline, and tokenomic units are the
    equality classes that can carry capabilities and constraints together.
    """

    events_by_id, event_by_occurrence = _event_indexes(field_events)
    occurrences_by_id = {
        str(occurrence["id"]): occurrence for occurrence in field_occurrences
    }
    source_ids = [str(item["id"]) for item in source_occurrences]
    current_relation_types = _unique(
        [str(item.get("relation_type") or "OPEN_RELATION") for item in relation_receipts]
    )
    memory_before = learned_relation_memory(prior_receipts)
    admitted = [
        item
        for item in relation_receipts
        if str(item.get("verdict", "OPEN")) != "FALSE"
    ]

    current_unique = {
        str(item.get("candidate_relation_id")): str(
            item.get("relation_type") or "OPEN_RELATION"
        )
        for item in admitted
        if item.get("candidate_relation_id")
    }
    memory_after_counter = Counter(memory_before)
    prior_relation_ids = {
        str(relation.get("candidate_relation_id"))
        for receipt in prior_receipts
        for relation in receipt.get("ai_translation", {}).get("relations", [])
        if str(relation.get("verdict", "OPEN")) != "FALSE"
    }
    for relation_id, relation_type in current_unique.items():
        if relation_id not in prior_relation_ids:
            memory_after_counter[relation_type] += 1
    memory_after = dict(sorted(memory_after_counter.items()))

    units = _resource_units(closure_level, event_by_occurrence)
    next_operation = _next_operation(event, closure_level, admitted)
    evaluation = (selection_reading or {}).get("evaluation", {})
    selected_relation_id = evaluation.get("selected_symbol") or (
        (selection_reading or {}).get("selected_symbol")
    )

    natural_form_for_occurrence = {
        str(member): str(form.get("natural_form"))
        for form in closure_level.get("truth_closes_level_alone", {}).get(
            "natural_forms", []
        )
        for member in form.get("members", [])
    }
    node_occurrence_ids = _unique(
        [
            *source_ids,
            *[
                str(item.get(key))
                for item in relation_receipts
                for key in ("source_occurrence", "target_occurrence")
                if item.get(key)
            ],
        ]
    )
    nodes: list[dict[str, Any]] = []
    for occurrence_id in node_occurrence_ids:
        owner = event_by_occurrence.get(occurrence_id)
        nodes.append(
            {
                "id": str(owner["id"]) if owner else f"occurrence:{occurrence_id}",
                "occurrence_id": occurrence_id,
                "form_label": (
                    owner.get("form_label") if owner else "exact occurrence"
                ),
                "authored_by": owner.get("authored_by") if owner else "source",
                "perspective_id": (
                    owner.get("perspective_id")
                    or owner.get("metadata", {}).get("perspective_id")
                    if owner
                    else None
                ),
                "authorship_role": (
                    owner.get("metadata", {}).get("authorship_role", "HUMAN")
                    if owner
                    else "OPEN"
                ),
                "coordination_kind": (
                    owner.get("metadata", {}).get("coordination_kind")
                    if owner
                    else None
                ),
                "exact_text": (
                    occurrences_by_id.get(occurrence_id, {}).get("exact_text")
                ),
                "location_label": (
                    owner.get("metadata", {}).get("location_label")
                    if owner
                    else None
                ),
                "capabilities": owner.get("capabilities", []) if owner else [],
                "constraints": owner.get("constraints", []) if owner else [],
                "natural_form": natural_form_for_occurrence.get(occurrence_id),
                "focus": occurrence_id in source_ids,
                "current_stage": owner.get("current_stage") if owner else "OPEN",
                "current_verdict": owner.get("current_verdict") if owner else "OPEN",
            }
        )

    edges: list[dict[str, Any]] = []
    for relation in relation_receipts:
        source_occurrence = str(relation.get("source_occurrence") or "")
        target_occurrence = str(relation.get("target_occurrence") or "")
        source_event = event_by_occurrence.get(source_occurrence)
        target_event = event_by_occurrence.get(target_occurrence)
        edges.append(
            {
                "id": str(relation.get("candidate_relation_id") or ""),
                "source": (
                    str(source_event["id"])
                    if source_event
                    else f"occurrence:{source_occurrence}"
                ),
                "target": (
                    str(target_event["id"])
                    if target_event
                    else f"occurrence:{target_occurrence}"
                ),
                "relation_type": str(
                    relation.get("relation_type") or "OPEN_RELATION"
                ),
                "verdict": str(relation.get("verdict") or "OPEN"),
                "admitted": str(relation.get("verdict") or "OPEN") != "FALSE",
                "slearn_memory_before": memory_before.get(
                    str(relation.get("relation_type") or "OPEN_RELATION"), 0
                ),
                "why": {
                    "rationale": relation.get("rationale"),
                    "admission_reason": relation.get("admission_reason"),
                    "score": relation.get("score"),
                    "verdict": str(relation.get("verdict") or "OPEN"),
                    "candidate_relation_id": relation.get(
                        "candidate_relation_id"
                    ),
                    "source_occurrence": source_occurrence,
                    "target_occurrence": target_occurrence,
                    "truth_issued": False,
                },
            }
        )

    metadata = event.get("metadata", {})
    adapter = str(event.get("adapter_label") or "")
    sheaf = str(metadata.get("sheaf") or "")
    physical_sensor = adapter == "hardware" or sheaf == "BLACK_MIRROR_SENSOR"
    sensor_kind = (
        "physical-sensor"
        if physical_sensor
        else "agent-or-network"
        if metadata.get("agent_authored") or adapter == "agent"
        else "human-interface"
    )
    coordination = build_coordination_receipt(
        event=event,
        field_events=field_events,
        field_occurrences=field_occurrences,
        relation_receipts=relation_receipts,
        commitment_proposals=commitment_proposals,
        living_problems=living_problems,
        living_actions=living_actions,
        living_returns=living_returns,
        closure_level_id=str(closure_level["level_id"]),
        closure_derivation=closure_level.get("translational_truth_axiometry"),
    )
    visible_event_ids = {
        str(coordination.get("intent", {}).get("event_id") or ""),
        *[
            str(path.get("target_event_id") or "")
            for path in coordination.get("paths", [])
        ],
    }
    existing_node_ids = {str(node["id"]) for node in nodes}
    for visible_event_id in visible_event_ids:
        if not visible_event_id or visible_event_id in existing_node_ids:
            continue
        visible_event = events_by_id.get(visible_event_id)
        if visible_event is None:
            continue
        occurrence_id = str((visible_event.get("exact_source_ids") or [""])[0])
        nodes.append(
            {
                "id": visible_event_id,
                "occurrence_id": occurrence_id,
                "form_label": visible_event.get("form_label"),
                "authored_by": visible_event.get("authored_by"),
                "perspective_id": (
                    visible_event.get("perspective_id")
                    or visible_event.get("metadata", {}).get("perspective_id")
                ),
                "authorship_role": visible_event.get("metadata", {}).get(
                    "authorship_role", "HUMAN"
                ),
                "coordination_kind": visible_event.get("metadata", {}).get(
                    "coordination_kind"
                ),
                "exact_text": occurrences_by_id.get(occurrence_id, {}).get(
                    "exact_text"
                ),
                "location_label": visible_event.get("metadata", {}).get(
                    "location_label"
                ),
                "capabilities": visible_event.get("capabilities", []),
                "constraints": visible_event.get("constraints", []),
                "natural_form": natural_form_for_occurrence.get(occurrence_id),
                "focus": visible_event_id == str(event["id"]),
                "current_stage": visible_event.get("current_stage"),
                "current_verdict": visible_event.get("current_verdict"),
            }
        )
        existing_node_ids.add(visible_event_id)

    receipt = {
        "protocol": "closure.supernet/visual-translational-closure-v1",
        "source_event_id": str(event["id"]),
        "source_provenance": {
            "source_stream": str(event.get("source_stream") or "legacy"),
            "exact_source_occurrence_ids": source_ids,
            "evidence_status": str(event.get("evidence_status") or "OPEN"),
            "adapter_label": event.get("adapter_label"),
            "equality_authority": False,
            "resource_admission_authority": False,
        },
        "closure_relation": [
            "SOURCE_JOURNEY_LEDGER",
            "VISUAL_EXISTENCE",
            "CHOSEN_PERSPECTIVE",
            "NRRF843_UI_FAMILY_READING",
            "PERSPECTIVE_VISUAL_MIRROR",
            "TRANSLATIONAL_MIRROR",
            "TRANSLATIONAL_TRUTH",
            "VISUAL_AXIOMETRY",
            "CLOSURE_EXPLICIT_MEETING",
            "NRRF843_UI_PREIMAGE_IMAGE_CLOSURE",
            "NRRF840_CLOSURE_CORRESPONDENCE",
            "TRUTH_CONSTRAINT_LOCATED_IN_UI",
            "NATURAL_FORM_ADMISSION",
            "THOUGHT_RELATION_EQVGEN",
            "UNITY_POTENTIAL_GATE",
            "TRUTH_CURVED_LIGHT_CONE",
            "BLACK_MIRROR_EVOLVING_PHYSICAL_TOPOLOGY",
            "PERSPECTIVE_DIGITAL_POTENTIAL_GATE",
            "AI_TOKEN_INTERACTION_CLOSURE",
            "SUPERNET_UNIFICATION_CONSTRAINT",
            "PERSPECTIVE_INTERACTION_UI_CONTRACT",
            "ONE_TRUTH_CONSTRAINED_RUNTIME",
            "FULL_UI_NATURAL_FORM_PROJECTION",
            "CLOSURE_ONLY_UI_EXECUTION",
            "INTERFACE_CLOSURE_RETURN",
        ],
        "operational_return_cycle": [
            "BLACK_MIRROR_SENSE",
            "NRRF843_UI_FAMILY_PROJECTION",
            "TRANSLATIONAL_MIRROR",
            "SLEARN_MEMORY",
            "AI_TRANSLATION",
            "UI_TRUTH_CONSTRAINT",
            "UI_PREIMAGE_IMAGE_CLOSURE",
            "CLOSURE_TRANSFORMED_MIRROR",
            "EVOLVING_PHYSICAL_TOPOLOGY",
            "DIGITAL_POTENTIAL_GATE",
            "AI_TOKEN_TRUTH_UNIFICATION",
            "PERSPECTIVE_INTERACTION_UI_CONTRACT",
            "FULL_UI_NATURAL_FORM_PROJECTION",
            "CLOSURE_ONLY_UI_EXECUTION",
            "INTERFACE_CLOSURE_RETURN",
            "BLACK_MIRROR_SENSE",
        ],
        "black_mirror": {
            "sensed": bool(source_occurrences),
            "sensor_kind": sensor_kind,
            "exact_source_occurrence_ids": source_ids,
            "source_preserved": True,
            "external_occurrence_received": True,
            "physical_sensor_attached": physical_sensor,
            "physical_sensor_status": "CONNECTED" if physical_sensor else "OPEN",
        },
        "slearn": {
            "memory_receipts_before": len(prior_receipts),
            "memory_receipts_after": len(prior_receipts) + 1,
            "relation_memory_before": memory_before,
            "relation_memory_after": memory_after,
            "current_relation_types": current_relation_types,
            "memory_influence": {
                relation_type: memory_before.get(relation_type, 0)
                for relation_type in current_relation_types
            },
            "learned_from_receipt_ids": [
                str(item["id"]) for item in prior_receipts[-32:] if item.get("id")
            ],
            "next_sense_reads_accumulated_field": True,
            "learning_kind": "source-preserving admitted relation memory",
        },
        "ai_translation": {
            "executed": True,
            "pipeline": [
                "UnderstandingAgent",
                "InterpretationAgent",
                "AdmissionPolicy",
                "TranslationField",
                "NRRF790",
                "NRRF825",
            ],
            "relations": relation_receipts,
            "admitted_relation_ids": [
                str(item["candidate_relation_id"])
                for item in admitted
                if item.get("candidate_relation_id")
            ],
            "selection_state": evaluation.get("state", "OPEN"),
            "selected_relation_id": selected_relation_id,
            "truth_issued": False,
        },
        "tokenomic": {
            "resolved": True,
            "resource_basis": "active equality-level natural forms",
            "resource_units": units,
            "resource_unit_count": len(units),
            "admitted_relation_capacity": len(admitted),
            "next_operation": next_operation,
            "currency_issued": False,
            "human_worth_scored": False,
            "resource_metric_is_foundational_selector": False,
        },
        "visual_network": {
            "derived": True,
            "nodes": nodes,
            "edges": edges,
            "natural_form_classes": units,
            "closure_level_id": closure_level["level_id"],
            "closure_level_endpoint": closure_level["endpoint"],
            "projective_fold": closure_level["projective_fold"],
            "canonical_pixel_layout_selected": False,
            "network_ui_is_operational_surface": True,
        },
        "coordination": coordination,
        "network_return": {
            "open": True,
            "current_stage": event.get("current_stage"),
            "next_operation": next_operation,
            "return_reopens_next_sense": True,
            "two_person_E2E": "OPEN",
        },
        "operational_closure": {
            "black_mirror_sensed": bool(source_occurrences),
            "slearn_memory_committed": True,
            "ai_translation_executed": True,
            "tokenomic_resources_derived": bool(units),
            "visual_network_derived": True,
            "network_return_open": True,
            "receipt_persisted": False,
            "all_desired_functions_in_this_occurrence": False,
        },
        "closure_level": closure_level,
        "two_person_E2E": "OPEN",
        "truth_issued": False,
    }

    visual_forms = []
    active_perspective = str(
        event.get("perspective_id")
        or event.get("metadata", {}).get("perspective_id")
        or event.get("authored_by")
        or "perspective"
    )
    active_perspective_reading: dict[str, str] = {}
    for state in closure_level.get("states", []):
        occurrence = occurrences_by_id.get(str(state), {})
        owner = event_by_occurrence.get(str(state), {})
        owner_metadata = owner.get("metadata", {})
        exact_visual_form = str(occurrence.get("exact_text") or "")
        # A return made through a focused natural form carries that form's
        # actual displayed value.  Otherwise the exact source is its visual
        # value.  No classifier, similarity score, or post-hoc truth fibre is
        # allowed to supply this reading.
        perspective_visual_value = str(
            owner_metadata.get("perspective_visual_value")
            or exact_visual_form
        )
        active_perspective_reading[str(state)] = perspective_visual_value
        visual_forms.append(
            {
                "id": state,
                "state": {
                    "source_occurrence_id": state,
                    "perspective_id": (
                        owner.get("perspective_id")
                        or owner_metadata.get("perspective_id")
                        or owner.get("authored_by")
                        or "OPEN"
                    ),
                    "exact_visual_form": exact_visual_form,
                    "active_perspective_visual_value": perspective_visual_value,
                    "form_label": owner.get("form_label"),
                    "operator_path": occurrence.get("operator_path", []),
                },
                "existence_provenance": [f"source-return:{state}"],
                "source_return_ids": [state],
            }
        )
    relative_truths = [
        {
            "id": relation.get("candidate_relation_id") or relation.get("id"),
            "source": relation.get("source_occurrence"),
            "target": relation.get("target_occurrence"),
            "verdict": relation.get("verdict", "OPEN"),
            "statement": relation.get("relation_type"),
            "provenance": [
                relation.get("interpretation_id"),
                relation.get("admission_id"),
            ],
            "source_return_ids": relation.get("source_return_ids")
            or [
                relation.get("source_occurrence"),
                relation.get("target_occurrence"),
            ],
            "visual_equation": relation.get("visual_equation"),
            "compatible": relation.get("compatible", False),
            "closure_explicit": relation.get("closure_explicit"),
        }
        for relation in relation_receipts
        if relation.get("source_occurrence") and relation.get("target_occurrence")
    ]
    truth_derivation = derive_closure(
        visual_forms,
        relative_truths,
        perspective_readings={
            active_perspective: active_perspective_reading
        },
    )
    truth_evaluations = {
        evaluation.truth_id: evaluation
        for evaluation in truth_derivation.truth_evaluations
    }
    for edge in receipt["visual_network"]["edges"]:
        evaluation = truth_evaluations.get(str(edge.get("id") or ""))
        witnessed = bool(
            evaluation is not None
            and evaluation.closure_admitted
        )
        edge["admitted"] = witnessed
        edge["translational_truth_status"] = (
            "WITNESSED" if witnessed else "OPEN"
        )
        edge["generates_equality"] = witnessed
        edge["why"]["translational_truth_status"] = edge[
            "translational_truth_status"
        ]
    witnessed_relation_ids = [
        str(edge["id"])
        for edge in receipt["visual_network"]["edges"]
        if edge["generates_equality"] and edge.get("id")
    ]
    witnessed_relation_id_set = set(witnessed_relation_ids)
    witnessed_relations = [
        relation
        for relation in relation_receipts
        if str(relation.get("candidate_relation_id") or relation.get("id") or "")
        in witnessed_relation_id_set
    ]
    next_operation = _next_operation(
        event,
        closure_level,
        witnessed_relations,
    )
    current_witnessed = {
        str(relation.get("candidate_relation_id") or relation.get("id") or ""):
        str(relation.get("relation_type") or "OPEN_RELATION")
        for relation in witnessed_relations
    }
    prior_witnessed_ids = {
        str(edge.get("id") or edge.get("candidate_relation_id") or "")
        for prior in prior_receipts
        for edge in prior.get("visual_network", {}).get("edges", [])
        if edge.get("generates_equality") is True
    }
    witnessed_memory_after = Counter(memory_before)
    for relation_id, relation_type in current_witnessed.items():
        if relation_id and relation_id not in prior_witnessed_ids:
            witnessed_memory_after[relation_type] += 1
    receipt["slearn"]["relation_memory_after"] = dict(
        sorted(witnessed_memory_after.items())
    )
    receipt["slearn"]["memory_basis"] = (
        "closure-admitted translational-truth witnesses only"
    )
    receipt["slearn"]["open_candidates_change_truth_memory"] = False
    receipt["ai_translation"]["retained_candidate_relation_ids"] = [
        str(item["candidate_relation_id"])
        for item in admitted
        if item.get("candidate_relation_id")
    ]
    receipt["ai_translation"]["admitted_relation_ids"] = witnessed_relation_ids
    receipt["ai_translation"]["admission_means_translational_truth_witness"] = True
    receipt["tokenomic"]["admitted_relation_capacity"] = len(
        witnessed_relation_ids
    )
    receipt["tokenomic"]["next_operation"] = next_operation
    receipt["network_return"]["next_operation"] = next_operation
    receipt["network_return"]["witnessed_relation_count"] = len(
        witnessed_relation_ids
    )

    # UI semantics are not mirrored in a second node/action inventory.  The
    # projection and its universal return relation are derived below and are
    # the only interface carrier.
    semantic_elements: list[dict[str, Any]] = []
    interface_actions: list[dict[str, Any]] = []
    truth_derivation_dict = truth_derivation.to_dict()
    # The first coordination pass identifies which source-preserved events must
    # enter visual existence.  Re-derive its continuum here from the resulting
    # joint truth closure so coordination cannot retain a parallel closure id.
    coordination = build_coordination_receipt(
        event=event,
        field_events=field_events,
        field_occurrences=field_occurrences,
        relation_receipts=relation_receipts,
        commitment_proposals=commitment_proposals,
        living_problems=living_problems,
        living_actions=living_actions,
        living_returns=living_returns,
        closure_level_id=str(closure_level["level_id"]),
        closure_derivation=truth_derivation_dict,
    )
    receipt["coordination"] = coordination
    nrrf843_ui = derive_nrrf843_ui_receipt(
        truth_derivation=truth_derivation_dict,
    )
    receipt["nrrf843_ui"] = nrrf843_ui
    nrrf842_journey = derive_nrrf842_journey_receipt(
        focus_event=event,
        field_events=field_events,
        perspective_visual_mirror=(
            truth_derivation.perspective_visual_mirror.to_dict()
        ),
        visual_truth_closure=truth_derivation.visual_truth_closure.to_dict(),
        natural_forms=closure_level.get("truth_closes_level_alone", {}).get(
            "natural_forms", []
        ),
        coordination=coordination,
    )
    receipt["nrrf842_journey"] = nrrf842_journey
    interaction_closure = derive_interaction_closure(
        truth_derivation=truth_derivation_dict,
        nrrf843_ui=nrrf843_ui,
        nrrf842_journey=nrrf842_journey,
        coordination=coordination,
        ai_translation=receipt["ai_translation"],
        tokenomic=receipt["tokenomic"],
        visual_network=receipt["visual_network"],
        black_mirror=receipt["black_mirror"],
        network_return=receipt["network_return"],
    )
    receipt["interaction_closure"] = interaction_closure
    closure_ui_contract = derive_closure_ui_contract(
        truth_derivation=truth_derivation_dict,
        nrrf843_ui=nrrf843_ui,
        nrrf842_journey=nrrf842_journey,
        interaction_closure=interaction_closure,
        coordination=coordination,
        visual_network=receipt["visual_network"],
        source_occurrences=source_occurrences,
        focus_event=event,
        field_event_seq=field_event_seq,
    )
    receipt["closure_ui_contract"] = closure_ui_contract
    unified_truth_runtime = derive_unified_truth_runtime(
        truth_derivation=truth_derivation_dict,
        nrrf843_ui=nrrf843_ui,
        nrrf842_journey=nrrf842_journey,
        interaction_closure=interaction_closure,
        closure_ui_contract=closure_ui_contract,
        coordination=coordination,
        semantic_elements=semantic_elements,
        interface_actions=interface_actions,
        slearn=receipt["slearn"],
        ai_translation=receipt["ai_translation"],
        tokenomic=receipt["tokenomic"],
    )
    receipt["unified_truth_runtime"] = unified_truth_runtime
    receipt["operational_closure"].update(
        {
            "translational_truth_axiometry_derived": True,
            "open_edges_excluded_from_equality": True,
            "natural_forms_derived_before_admission": True,
            "perspective_visual_mirror_is_truth_constraint_surface": True,
            "interface_required_for_supernet_truth": True,
            "supernet_without_interface_remains_open": True,
            "interface_is_active_visual_closure_mechanism": True,
            "metaphorical_forms_are_semantic": True,
            "thought_closes_metaphor_into_relations": True,
            "nrrf843_ui_family_reading_executed": True,
            "nrrf843_translational_mirror_witnessed": (
                nrrf843_ui["translational_mirror"]["witnessed"]
            ),
            "nrrf843_ui_projection_generates_closure": nrrf843_ui[
                "ui_closure"
            ]["closure_falls_out_from_ui_projection"],
            "nrrf843_truth_constraint_located_in_ui": nrrf843_ui[
                "truth_constraint_location"
            ]["located"],
            "nrrf843_thought_eqvgen_executed": nrrf843_ui["thought"][
                "least_closed_relation_computed"
            ],
            "nrrf843_no_external_closure_or_truth": not (
                nrrf843_ui["ui_family"]["external_closure_assumed"]
                or nrrf843_ui["ui_family"]["external_truth_assumed"]
            ),
            "nrrf840_preimage_image_closure_executed": True,
            "closure_free_of_external_limit": True,
            "closure_free_of_unnatural_limit": True,
            "interface_natural_form_derived_inside_closure": True,
            "external_renderer_transport_only": True,
            "journey_preserved_separately_from_closed_state": True,
            "chosen_perspective_receipt_present": True,
            "unity_gate_scoped_to_shared_trajectory": True,
            "ordinary_interaction_remains_open": True,
            "truth_curved_light_cone_derived": True,
            "black_mirror_physical_topology_derived": interaction_closure[
                "black_mirror_physical_topology"
            ]["closure_is_generated_by_projection"],
            "perspective_digital_potential_gate_derived": interaction_closure[
                "perspective_digital_potential_gate"
            ]["status"]
            == "WITNESSED",
            "ai_token_interaction_closed_by_truth_unification": (
                interaction_closure["supernet_interaction_closed"]
            ),
            "closure_only_ui_contract_derived": (
                closure_ui_contract["audit"]["closure_only_execution"]
            ),
            "all_visible_ui_relations_closure_derived": (
                closure_ui_contract["audit"][
                    "all_visual_existence_has_exact_derivation"
                ]
            ),
            "single_full_surface_return_relation": (
                closure_ui_contract["audit"][
                    "full_surface_is_only_return_aperture"
                ]
            ),
            "no_hardcoded_visible_ui_instances": not (
                closure_ui_contract["renderer_relation"][
                    "fixed_visible_controls"
                ]
                or closure_ui_contract["renderer_relation"][
                    "authored_visible_vocabulary"
                ]
                or closure_ui_contract["renderer_relation"]["fallback_visuals"]
            ),
            "open_digital_potential_remains_visible": interaction_closure[
                "perspective_digital_potential_gate"
            ]["open_potential_remains_visible"],
            "closure_continues_living_history": True,
            "one_semantic_truth_runtime_witnessed": (
                unified_truth_runtime["status"] == "WITNESSED"
            ),
            "no_semantically_external_component": not unified_truth_runtime[
                "semantic_external_component_ids"
            ],
            "no_semantically_isolated_component": not unified_truth_runtime[
                "semantic_isolated_component_ids"
            ],
        }
    )
    # Factor the actual projected relation by equality fibre.  Earlier versions
    # copied one enormous pre-authored render state onto every member; that made
    # factorisation tautological and did not derive UI content.  Each payload
    # below is now exactly the visual value of one natural form.
    projection = closure_ui_contract["projection"]
    projected_states = {
        str(item["id"]): item for item in projection.get("states", [])
    }
    fibre_values: dict[str, dict[str, Any]] = {}
    for fibre in projection.get("equality_fibres", []):
        members = set(str(item) for item in fibre["member_state_ids"])
        fibre_values[str(fibre["id"])] = {
            "natural_form_id": fibre["id"],
            "member_state_ids": sorted(members),
            "source_returns": [
                {
                    "state_id": state_id,
                    "source_return_ids": projected_states[state_id][
                        "source_return_ids"
                    ],
                    "source_trace": projected_states[state_id]["source_trace"],
                }
                for state_id in sorted(members)
            ],
            "translations": [
                item
                for item in projection.get("translations", [])
                if item.get("source_state_id") in members
                or item.get("target_state_id") in members
            ],
            "potentials": [
                item
                for item in projection.get("potentials", [])
                if item.get("shared_natural_form_id") == fibre["id"]
                or item.get("target_state_id") in members
                or (
                    item.get("target_state_id") is None
                    and closure_ui_contract.get("return_relation", {}).get(
                        "parent_natural_form_id"
                    )
                    == fibre["id"]
                )
            ],
            "relation_digest": projection["visualization"].get(
                "relation_digest"
            ),
        }
    quotient_reading = {
        state: {
            "natural_form_id": truth_derivation.natural_form_for(state).id,
            "perspective_visual_value": fibre_values[
                truth_derivation.natural_form_for(state).id
            ],
        }
        for state in truth_derivation.visual_existence.form_ids
    }
    interface_form = derive_interface_natural_form(
        truth_derivation,
        quotient_reading,
    ).to_dict()
    interface_render_state = {
        "closure_derivation_id": truth_derivation.id,
        "visual_closure_id": truth_derivation.visual_truth_closure.id,
        "nrrf843_ui_id": nrrf843_ui["id"],
        "interaction_closure_id": interaction_closure["id"],
        "closure_ui_contract": closure_ui_contract,
        "projection": projection,
        "return_relation": closure_ui_contract.get("return_relation"),
    }
    interface_form.update(
        {
            "kind": "SUPERNET_INTERFACE_NATURAL_FORM",
            "admission_status": "NATURALLY_ADMITTED",
            "truth_form_equals_visual_equality": True,
            "ui_factors_through_translational_truth": True,
            "ui_is_external_ontology": False,
            "renderer_role": "TRANSLATIONAL_RELATION_EVALUATOR",
            "semantic_elements": [],
            "actions": [],
            "render_state": interface_render_state,
            "render_state_factorized": True,
            "factorization_is_per_equality_fibre": True,
            "constant_whole_scene_factorization": False,
        }
    )
    receipt["translational_truth_axiometry"] = truth_derivation_dict
    receipt["interface_natural_form"] = interface_form
    return receipt
