from __future__ import annotations

"""The Supernet interaction is the active UI reading, not a product workflow.

AI, token, human, sensor, contract, and physical returns are states in the same
source-preserving carrier. Their only executable interaction is extension of
the active perspective relation followed by re-closure.
"""

import hashlib
import json
from typing import Any, Iterable, Mapping


PROTOCOL = "SUPERNET-INTERACTION-CLOSURE"
SCHEMA = "closure.supernet/perspective-interaction-relation-v2"


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(prefix: str, value: Any) -> str:
    content = hashlib.sha256(_stable(value).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{content}"


def _unique(values: Iterable[Any]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if value is not None and str(value)))


def _active_perspective(
    nrrf843_ui: Mapping[str, Any],
    nrrf842_journey: Mapping[str, Any],
) -> str | None:
    perspectives = _unique(nrrf843_ui.get("ui_family", {}).get("perspective_ids", []))
    chosen = str(nrrf842_journey.get("chosen_perspective", {}).get("perspective_id") or "")
    if chosen in perspectives:
        return chosen
    return perspectives[0] if len(perspectives) == 1 else None


def _natural_form_indexes(
    truth_derivation: Mapping[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    forms: dict[str, dict[str, Any]] = {}
    form_by_member: dict[str, str] = {}
    for raw in truth_derivation.get("natural_forms", []):
        form = dict(raw)
        form_id = str(form.get("id") or "")
        if not form_id:
            continue
        forms[form_id] = form
        for member in _unique(form.get("members", [])):
            form_by_member[member] = form_id
    return forms, form_by_member


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

    The historical materialized readings are accepted for receipt compatibility
    but cannot gate, widen, label, or otherwise author this relation.
    """

    del coordination, ai_translation, tokenomic, network_return
    truth_id = str(truth_derivation.get("id") or "")
    visual_closure_id = str(truth_derivation.get("visual_truth_closure", {}).get("id") or "")
    ui_id = str(nrrf843_ui.get("id") or "")
    active_perspective = _active_perspective(nrrf843_ui, nrrf842_journey)
    readings = nrrf843_ui.get("ui_family", {}).get("readings", {})
    reading = dict(readings.get(active_perspective, {})) if active_perspective else {}
    forms, form_by_member = _natural_form_indexes(truth_derivation)
    truth_members = set(form_by_member)

    checks = {
        "perspective_visualization_witnessed": bool(
            truth_derivation.get("status") == "WITNESSED"
            and truth_derivation.get("supernet_open") is False
        ),
        "ui_is_same_visualization": bool(
            nrrf843_ui.get("status") == "WITNESSED"
            and nrrf843_ui.get("closure_derivation_id") == truth_id
            and nrrf843_ui.get("visual_closure_id") == visual_closure_id
        ),
        "truth_constraint_is_ui_kernel": bool(
            nrrf843_ui.get("truth_constraint_location", {}).get("located") is True
            and nrrf843_ui.get("ui_closure", {}).get("closure_falls_out_from_ui_projection") is True
        ),
        "active_perspective_reading_present": bool(
            active_perspective and reading and set(reading) == truth_members
        ),
        "natural_forms_are_visual_fibres": bool(forms),
    }
    unified = all(checks.values())

    basis_by_display: dict[str, list[str]] = {}
    for state, display in reading.items():
        basis_by_display.setdefault(str(display), []).append(str(state))
    topology_basis = [
        {
            "display_fibre_id": display,
            "member_state_ids": sorted(members),
            "natural_form_id": form_by_member[members[0]] if members else None,
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
                "physical_world_return": bool(black_mirror.get("physical_sensor_attached") is True),
            }
        )

    topology_relations: list[dict[str, Any]] = []
    for edge in visual_network.get("edges", []):
        source_event = str(edge.get("source") or "")
        target_event = str(edge.get("target") or "")
        source_state = event_to_state.get(source_event)
        target_state = event_to_state.get(target_event)
        if not source_state or not target_state:
            continue
        same_fibre = reading[source_state] == reading[target_state]
        witnessed = bool(
            same_fibre and form_by_member.get(source_state) == form_by_member.get(target_state)
        )
        topology_relations.append(
            {
                "id": str(edge.get("id") or _digest("relation", edge)),
                "source_event_id": source_event,
                "target_event_id": target_event,
                "source_state_id": source_state,
                "target_state_id": target_state,
                "truth_constraint_status": "WITNESSED" if witnessed else "OPEN",
                "same_display_fibre": same_fibre,
                "generates_topological_identification": witnessed,
                "visible_potential": not witnessed,
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
            "checks": checks,
            "all_components_share_one_translational_truth": unified,
            "parallel_truth_runtime_present": False,
        },
        "black_mirror_physical_topology": {
            "status": "WITNESSED" if unified else "OPEN",
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
            "status": "WITNESSED" if unified else "OPEN",
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
        },
        "claims": {
            "truth_is_visualization_kernel": unified,
            "currency_issued": False,
            "legal_binding_claimed": False,
            "physical_law_claimed": False,
        },
    }
    body["id"] = _digest("interaction-closure", body)
    return body


__all__ = ["PROTOCOL", "SCHEMA", "derive_interaction_closure"]
