from __future__ import annotations

"""The Supernet interaction is the active UI reading, not a product workflow.

AI, token, human, sensor, contract, and physical returns are relative readings
of one source-preserving carrier. Only an explicit perspective return and a
recomputed equality of UI and natural-form fibres can witness interaction
closure. Stored status booleans and compatibility products never author it.
"""

import hashlib
import json
from typing import Any, Iterable, Mapping

from .closure_continuity import (
    OPEN_STATUS,
    WITNESSED_STATUS,
    ClosureWitness,
    audit_translational_continuity,
    combine_witnesses,
    compatibility_reading_receipt,
    derive_perspective_reading,
    derive_projection_equivalence,
)


PROTOCOL = "SUPERNET-INTERACTION-CLOSURE"
SCHEMA = "closure.supernet/perspective-interaction-relation-v3"


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(prefix: str, value: Any) -> str:
    content = hashlib.sha256(_stable(value).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{content}"


def _unique(values: Iterable[Any]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if value is not None and str(value)))


def _natural_form_indexes(
    truth_derivation: Mapping[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, str], list[str]]:
    forms: dict[str, dict[str, Any]] = {}
    form_by_member: dict[str, str] = {}
    conflicts: set[str] = set()
    for raw in truth_derivation.get("natural_forms", []):
        form = dict(raw)
        form_id = str(form.get("id") or "")
        if not form_id:
            continue
        forms[form_id] = form
        for member in _unique(form.get("members", [])):
            previous = form_by_member.get(member)
            if previous is not None and previous != form_id:
                conflicts.add(member)
            else:
                form_by_member[member] = form_id
    return forms, form_by_member, sorted(conflicts)


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
    """Return the one source-derived interactive relation.

    Historical materialized readings remain visible for receipt compatibility,
    but they cannot gate, widen, select, or label the translational truth.
    """

    truth_id = str(truth_derivation.get("id") or "")
    visual_closure_id = str(
        truth_derivation.get("visual_truth_closure", {}).get("id") or ""
    )
    ui_id = str(nrrf843_ui.get("id") or "")
    forms, form_by_member, conflicting_form_members = _natural_form_indexes(
        truth_derivation
    )
    truth_members = set(form_by_member)

    perspective = derive_perspective_reading(
        nrrf843_ui=nrrf843_ui,
        nrrf842_journey=nrrf842_journey,
        truth_members=truth_members,
    )
    active_perspective = perspective["active_perspective_id"]
    reading = perspective["projection_reading"]
    projection = derive_projection_equivalence(
        reading=reading,
        form_by_member=form_by_member,
        conflicting_form_members=conflicting_form_members,
    )

    witnesses = [
        ClosureWitness(
            "truth_source_present",
            bool(truth_id and visual_closure_id and forms and not conflicting_form_members),
            "A source-derived closure, visual closure and conflict-free natural forms are required.",
            tuple(item for item in (truth_id, visual_closure_id) if item),
        ),
        ClosureWitness(
            "ui_links_to_truth_source",
            bool(
                truth_id
                and visual_closure_id
                and nrrf843_ui.get("closure_derivation_id") == truth_id
                and nrrf843_ui.get("visual_closure_id") == visual_closure_id
            ),
            "The UI must point to the same source closure; a stored WITNESSED flag is insufficient.",
            tuple(item for item in (ui_id, truth_id, visual_closure_id) if item),
        ),
        ClosureWitness(
            "perspective_return_witnessed",
            bool(perspective["selection_witnessed"]),
            "Perspective must arrive through an explicit source-authored return; no singleton fallback is allowed.",
            tuple(item for item in (str(active_perspective or ""),) if item),
        ),
        ClosureWitness(
            "active_reading_total",
            bool(projection["reading_total"]),
            "The active perspective must read every and only source members in the closure.",
            tuple(projection["truth_member_ids"]),
        ),
        ClosureWitness(
            "ui_kernel_equals_natural_form_partition",
            bool(projection["partition_equal"]),
            "UI fibres and natural-form fibres must be extensionally the same partition.",
            tuple(projection["truth_member_ids"]),
        ),
    ]
    continuity = combine_witnesses(witnesses)
    unified = continuity["status"] == WITNESSED_STATUS
    checks = {
        name: bool(receipt["holds"])
        for name, receipt in continuity["witnesses"].items()
    }

    basis_by_display: dict[str, list[str]] = {}
    for state, display in reading.items():
        basis_by_display.setdefault(str(display), []).append(str(state))
    topology_basis = [
        {
            "display_fibre_id": display,
            "member_state_ids": sorted(members),
            "natural_form_id": form_by_member.get(members[0]) if members else None,
            "closure_fixed": bool(
                members and len({form_by_member.get(member) for member in members}) == 1
            ),
        }
        for display, members in sorted(basis_by_display.items())
    ]

    topology_nodes: list[dict[str, Any]] = []
    event_to_state: dict[str, str] = {}
    for node in visual_network.get("nodes", []):
        event_id = str(node.get("id") or "")
        state_id = str(node.get("occurrence_id") or event_id)
        if not event_id or state_id not in reading:
            continue
        event_to_state[event_id] = state_id
        topology_nodes.append(
            {
                "event_id": event_id,
                "state_id": state_id,
                "perspective_id": active_perspective,
                "display_fibre_id": reading[state_id],
                "natural_form_id": form_by_member.get(state_id),
                "source_preserved": state_id in truth_members,
                "physical_world_return": bool(
                    black_mirror.get("physical_sensor_attached") is True
                ),
            }
        )

    topology_relations: list[dict[str, Any]] = []
    semantic_relations: list[dict[str, Any]] = []
    for edge in visual_network.get("edges", []):
        source_event = str(edge.get("source") or "")
        target_event = str(edge.get("target") or "")
        source_state = event_to_state.get(source_event)
        target_state = event_to_state.get(target_event)
        if not source_state or not target_state:
            continue
        same_fibre = reading[source_state] == reading[target_state]
        witnessed = bool(
            same_fibre
            and form_by_member.get(source_state) == form_by_member.get(target_state)
        )
        status = WITNESSED_STATUS if witnessed else OPEN_STATUS
        relation_id = str(edge.get("id") or _digest("relation", edge))
        topology_relations.append(
            {
                "id": relation_id,
                "source_event_id": source_event,
                "target_event_id": target_event,
                "source_state_id": source_state,
                "target_state_id": target_state,
                "truth_constraint_status": status,
                "same_display_fibre": same_fibre,
                "generates_topological_identification": witnessed,
                "visible_potential": not witnessed,
            }
        )
        semantic_relations.append(
            {
                "source_state_id": source_state,
                "target_state_id": target_state,
                "truth_constraint_status": status,
            }
        )

    potentials = [
        {
            "id": relation["id"],
            "target_event_id": relation["target_event_id"],
            "shared_natural_form_id": (
                form_by_member.get(relation["source_state_id"])
                if relation["same_display_fibre"]
                else None
            ),
            "truth_constraint_status": relation["truth_constraint_status"],
            "executes_as_equality": relation["generates_topological_identification"],
            "remains_connected_potential": True,
        }
        for relation in topology_relations
        if relation["visible_potential"]
    ]

    relative_readings = {
        name: compatibility_reading_receipt(
            name,
            value,
            closure_derivation_id=truth_id,
        )
        for name, value in {
            "coordination": coordination,
            "ai_translation": ai_translation,
            "tokenomic": tokenomic,
            "network_return": network_return,
        }.items()
    }

    truth_core = {
        "closure_derivation_id": truth_id,
        "visual_closure_id": visual_closure_id,
        "active_perspective_id": active_perspective,
        "natural_form_partition": projection["natural_form_partition"],
        "ui_partition": projection["reading_partition"],
        "witnesses": checks,
        "relations": semantic_relations,
    }
    translational_truth_id = _digest("translational-truth", truth_core)

    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "closure_derivation_id": truth_id,
        "visual_closure_id": visual_closure_id,
        "nrrf843_ui_id": ui_id,
        "translational_truth_id": translational_truth_id,
        "status": WITNESSED_STATUS if unified else OPEN_STATUS,
        "supernet_interaction_closed": unified,
        "closed_relation_not_closed_existence": unified,
        "existence_closed": False,
        "dialectic_continuation_status": OPEN_STATUS,
        "one_interaction_surface": unified,
        "translational_continuity": continuity,
        "unification_constraint": {
            "status": WITNESSED_STATUS if unified else OPEN_STATUS,
            "checks": checks,
            "all_components_share_one_translational_truth": unified,
            "parallel_truth_runtime_present": False,
            "stored_status_flags_used_as_evidence": False,
            "configuration_authors_truth": False,
        },
        "projection_equivalence": projection,
        "perspective_selection": perspective,
        "relative_readings": relative_readings,
        "black_mirror_physical_topology": {
            "status": WITNESSED_STATUS if unified else OPEN_STATUS,
            "active_perspective_id": active_perspective,
            "projection_reading": reading,
            "closure_formula": "uiClosure(r,A)=r^-1(r(A))",
            "topology_basis": topology_basis,
            "nodes": topology_nodes,
            "relations": topology_relations,
            "closure_is_generated_by_projection": unified,
            "static_external_map": False,
            "physical_law_claimed": False,
        },
        "perspective_digital_potential_gate": {
            "status": WITNESSED_STATUS if unified else OPEN_STATUS,
            "active_perspective_id": active_perspective,
            "potentials": potentials,
            "open_potential_remains_visible": True,
            "open_potential_executes_as_equality": False,
            "independent_gate_layer_present": False,
        },
        "return_relation": {
            "kind": "SOURCE_PRESERVING_TRANSLATIONAL_RETURN",
            "full_surface": True,
            "reclose_after_return": True,
            "operation_enum": None,
            "continuation_status": OPEN_STATUS,
            "closed_argument_closes_existence": False,
        },
        "claims": {
            "truth_is_visualization_kernel": unified,
            "currency_issued": False,
            "legal_binding_claimed": False,
            "physical_law_claimed": False,
            "absolute_truth_issued": False,
        },
    }
    body["continuity_self_audit"] = audit_translational_continuity(body)
    body["id"] = _digest(
        "interaction-closure",
        {
            "translational_truth_id": translational_truth_id,
            "continuation_status": OPEN_STATUS,
            "continuity_self_audit": body["continuity_self_audit"]["status"],
        },
    )
    return body


__all__ = ["PROTOCOL", "SCHEMA", "derive_interaction_closure"]
