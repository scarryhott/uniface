from __future__ import annotations

from collections import Counter
from typing import Any

from .coordination import build_coordination_receipt
from .translational_truth_axiometry import (
    derive_closure,
    derive_interface_natural_form,
)


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
        "closure_relation": [
            "VISUAL_EXISTENCE",
            "TRANSLATIONAL_TRUTH",
            "VISUAL_AXIOMETRY",
            "CLOSURE_EXPLICIT_MEETING",
            "NATURAL_FORM_ADMISSION",
            "INTERFACE_NATURAL_FORM",
        ],
        "operational_return_cycle": [
            "BLACK_MIRROR_SENSE",
            "SLEARN_MEMORY",
            "AI_TRANSLATION",
            "INTERFACE_RETURN",
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

    visual_forms = [
        {
            "id": state,
            "state": {"source_occurrence_id": state},
            "existence_provenance": [f"source-return:{state}"],
        }
        for state in closure_level.get("states", [])
    ]
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
    truth_derivation = derive_closure(visual_forms, relative_truths)
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

    def element_derivation(member_ids: list[str]) -> dict[str, Any]:
        form_ids = sorted(
            {
                truth_derivation.natural_form_for(member_id).id
                for member_id in member_ids
                if member_id in truth_derivation.visual_existence.form_ids
            }
        )
        return {
            "source_return_ids": member_ids,
            "natural_form_ids": form_ids,
            "closure_derivation_id": truth_derivation.id,
            "derived_inside_closure": bool(form_ids),
        }

    semantic_elements: list[dict[str, Any]] = []
    for node in receipt["visual_network"]["nodes"]:
        occurrence_id = str(node.get("occurrence_id") or "")
        derivation = element_derivation(
            [occurrence_id] if occurrence_id else []
        )
        naturally_admitted = bool(derivation["natural_form_ids"])
        semantic_elements.append(
            {
                "id": f"ui-node:{node['id']}",
                "kind": "NODE",
                "admission_status": (
                    "NATURALLY_ADMITTED" if naturally_admitted else "OPEN"
                ),
                **derivation,
                "derived_inside_closure": naturally_admitted,
            }
        )
    for edge in receipt["visual_network"]["edges"]:
        relation = next(
            (
                item
                for item in relation_receipts
                if str(item.get("candidate_relation_id") or "")
                == str(edge.get("id") or "")
            ),
            {},
        )
        endpoints = [
            str(relation.get("source_occurrence") or ""),
            str(relation.get("target_occurrence") or ""),
        ]
        derivation = element_derivation([item for item in endpoints if item])
        relation_witnessed = bool(edge["generates_equality"])
        semantic_elements.append(
            {
                "id": f"ui-edge:{edge.get('id')}",
                "kind": "TRANSLATION_EDGE",
                "admission_status": edge["translational_truth_status"],
                "generates_equality": relation_witnessed,
                "potential_visible": True,
                **derivation,
                "derived_inside_closure": relation_witnessed,
            }
        )

    next_action = receipt["network_return"]["next_operation"]
    interface_actions = [
        {
            "id": f"interface-return:{next_action['action']}",
            "operation": next_action["action"],
            "kind": "RETURN_IN_SAME_CLOSURE_ENVIRONMENT",
            "source_return_ids": source_ids,
            "closure_derivation_id": truth_derivation.id,
            "requires_source_preserved_round_trip": True,
            "changes_interface_without_new_receipt": False,
        }
    ]
    receipt["operational_closure"].update(
        {
            "translational_truth_axiometry_derived": True,
            "open_edges_excluded_from_equality": True,
            "natural_forms_derived_before_admission": True,
            "interface_natural_form_derived_inside_closure": True,
            "external_renderer_transport_only": True,
        }
    )
    interface_render_state = {
        "source_event_id": receipt["source_event_id"],
        "focus_event": {
            "id": receipt["source_event_id"],
            "current_stage": event.get("current_stage"),
            "current_verdict": event.get("current_verdict"),
            "authored_by": event.get("authored_by"),
            "form_label": event.get("form_label"),
        },
        "source_fibre": [
            {
                "id": str(item.get("id") or ""),
                "exact_text": item.get("exact_text"),
                "source_id": item.get("source_id"),
                "form_label": item.get("form_label"),
            }
            for item in source_occurrences
        ],
        "derivation_order": receipt["closure_relation"],
        "truth_form_equals_visual_equality": True,
        "ui_factors_through_translational_truth": True,
        "ui_is_external_ontology": False,
        "renderer_role": "TRANSPORT_ONLY",
        "coordination": coordination,
        "visual_network": receipt["visual_network"],
        "closure_level": closure_level,
        "tokenomic": receipt["tokenomic"],
        "slearn": receipt["slearn"],
        "ai_translation": receipt["ai_translation"],
        "network_return": receipt["network_return"],
        "operational_closure": receipt["operational_closure"],
        "semantic_elements": semantic_elements,
        "actions": interface_actions,
    }
    quotient_reading = {
        state: {
            "natural_form_id": truth_derivation.natural_form_for(state).id,
            "render_state": interface_render_state,
        }
        for state in truth_derivation.visual_existence.form_ids
    }
    interface_form = derive_interface_natural_form(
        truth_derivation,
        quotient_reading,
    ).to_dict()
    if truth_derivation.visual_existence.form_ids:
        first_member = truth_derivation.visual_existence.form_ids[0]
        validated_render_state = interface_form["closure_projection"][
            first_member
        ]["render_state"]
    else:
        validated_render_state = interface_render_state
    interface_form.update(
        {
            "kind": "SUPERNET_INTERFACE_NATURAL_FORM",
            "admission_status": "NATURALLY_ADMITTED",
            "derivation_order": validated_render_state["derivation_order"],
            "truth_form_equals_visual_equality": validated_render_state[
                "truth_form_equals_visual_equality"
            ],
            "ui_factors_through_translational_truth": validated_render_state[
                "ui_factors_through_translational_truth"
            ],
            "ui_is_external_ontology": validated_render_state[
                "ui_is_external_ontology"
            ],
            "renderer_role": validated_render_state["renderer_role"],
            "semantic_elements": validated_render_state["semantic_elements"],
            "actions": validated_render_state["actions"],
            "render_state": validated_render_state,
            "render_state_factorized": True,
        }
    )
    receipt["translational_truth_axiometry"] = truth_derivation.to_dict()
    receipt["interface_natural_form"] = interface_form
    return receipt
