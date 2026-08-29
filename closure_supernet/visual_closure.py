from __future__ import annotations

from collections import Counter
from typing import Any


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if str(value)))


def learned_relation_memory(
    receipts: list[dict[str, Any]],
) -> dict[str, int]:
    """Count unique admitted relation witnesses already retained by SLEARN."""

    witnessed: dict[str, str] = {}
    for receipt in receipts:
        for relation in receipt.get("ai_translation", {}).get("relations", []):
            if str(relation.get("verdict", "OPEN")) == "FALSE":
                continue
            relation_id = str(relation.get("candidate_relation_id") or "")
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
) -> dict[str, Any]:
    """Derive one operational UI receipt from one interaction-time Sense.

    The receipt is not a dashboard summary.  It is the source-reversible data
    used by the primary canvas and its derived next action.  SLEARN memory is
    the accumulated set of admitted relation witnesses, AI translation is the
    existing interpretation/admission pipeline, and tokenomic units are the
    equality classes that can carry capabilities and constraints together.
    """

    _events_by_id, event_by_occurrence = _event_indexes(field_events)
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

    return {
        "protocol": "closure.supernet/visual-translational-closure-v1",
        "source_event_id": str(event["id"]),
        "closure_relation": [
            "BLACK_MIRROR_SENSE",
            "SLEARN_MEMORY",
            "AI_TRANSLATION",
            "TOKENOMIC_ADMISSION",
            "VISUAL_CLOSURE",
            "NETWORK_RETURN",
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
