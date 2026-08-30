from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable

from .closure_ui_contract import (
    SCHEMA as CLOSURE_UI_SCHEMA,
    WITNESSED_STATUS as CLOSURE_UI_WITNESSED,
    validate_ui_contract,
)


PROTOCOL = "closure.supernet/one-truth-constrained-runtime-v1"
SCHEMA = "closure.supernet/unified-truth-runtime-v1"


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


def _component(
    name: str,
    *,
    connected: bool,
    closure_derivation_id: Any,
    visual_closure_id: Any,
    source_return_ids: Iterable[Any],
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "factorization_status": "WITNESSED" if connected else "OPEN",
        "factors_through_translational_truth": connected,
        "closure_derivation_id": closure_derivation_id,
        "visual_closure_id": visual_closure_id,
        "source_return_ids": _unique(source_return_ids),
        "semantic_external": False,
        "semantically_isolated": False,
        **(detail or {}),
    }


def derive_unified_truth_runtime(
    *,
    truth_derivation: dict[str, Any],
    nrrf843_ui: dict[str, Any],
    nrrf842_journey: dict[str, Any],
    interaction_closure: dict[str, Any],
    closure_ui_contract: dict[str, Any],
    coordination: dict[str, Any],
    semantic_elements: list[dict[str, Any]],
    interface_actions: list[dict[str, Any]],
    slearn: dict[str, Any],
    ai_translation: dict[str, Any],
    tokenomic: dict[str, Any],
) -> dict[str, Any]:
    """Factor every semantic Supernet operation through one truth closure.

    Source forms are boundary data of the same carrier.  OPEN relations stay
    connected potential but cannot act as equality.  HTML, SVG, networks and
    sensors transport source forms; none is allowed to become a second truth
    or UI ontology.
    """

    derivation_id = truth_derivation.get("id")
    visual_closure = truth_derivation.get("visual_truth_closure", {})
    visual_closure_id = visual_closure.get("id")
    mirror_id = truth_derivation.get("perspective_visual_mirror", {}).get("id")
    natural_forms = list(truth_derivation.get("natural_forms", []))
    natural_form_ids = _unique(item.get("id") for item in natural_forms)
    source_return_ids = _unique(
        source_id
        for form in truth_derivation.get("visual_existence", {}).get("forms", [])
        for source_id in form.get("source_return_ids", [])
    )
    witnessed_relation_ids = {
        str(item.get("truth_id") or "")
        for item in truth_derivation.get("truth_evaluations", [])
        if item.get("closure_admitted") is True
    }
    ai_admitted_ids = {
        str(item)
        for item in ai_translation.get("admitted_relation_ids", [])
        if str(item)
    }
    ai_connected = ai_admitted_ids.issubset(witnessed_relation_ids)

    semantic_connected = all(
        (
            item.get("admission_status") in {"OPEN", None}
            or (
                item.get("closure_derivation_id") == derivation_id
                and item.get("visual_closure_id") == visual_closure_id
                and item.get("derived_inside_closure") is True
            )
        )
        for item in semantic_elements
    )
    action_connected = all(
        item.get("closure_derivation_id") == derivation_id
        and item.get("requires_source_preserved_round_trip") is True
        for item in interface_actions
    )
    continuum = coordination.get("continuum") or coordination.get(
        "nrrf837_continuum", {}
    )
    selected_form_id = continuum.get("selected_natural_form_id")
    coordination_connected = bool(
        continuum.get("closure_derivation_id") == derivation_id
        and (
            selected_form_id in natural_form_ids
            or continuum.get("natural_form_admission_status") == "OPEN"
        )
    )
    journey_connected = bool(
        nrrf842_journey.get("closed_state", {}).get("visual_closure_id")
        == visual_closure_id
        and nrrf842_journey.get("journey", {}).get("source_preserved") is True
    )
    mirror_connected = bool(
        derivation_id
        and visual_closure_id
        and mirror_id
        and nrrf843_ui.get("status") == "WITNESSED"
        and nrrf843_ui.get("closure_derivation_id") == derivation_id
        and nrrf843_ui.get("visual_closure_id") == visual_closure_id
        and nrrf843_ui.get("visual_mirror_id") == mirror_id
        and nrrf843_ui.get("ui_closure", {}).get(
            "closure_falls_out_from_ui_projection"
        )
        is True
        and nrrf843_ui.get("truth_constraint_location", {}).get("located")
        is True
    )
    slearn_connected = bool(
        slearn.get("open_candidates_change_truth_memory") is False
        and slearn.get("memory_basis")
        == "closure-admitted translational-truth witnesses only"
    )
    truth_members = {
        str(member)
        for form in natural_forms
        for member in form.get("members", [])
    }
    token_members = {
        str(member)
        for unit in tokenomic.get("resource_units", [])
        for member in unit.get("member_occurrence_ids", [])
    }
    token_connected = bool(token_members and token_members.issubset(truth_members))
    unity_gate = nrrf842_journey.get("unity_gate", {})
    unity_connected = bool(
        journey_connected
        and coordination_connected
        and unity_gate.get("selected_natural_form_id") == selected_form_id
        and unity_gate.get("scope") == "SHARED_TRAJECTORY_NOT_PERSON"
    )
    interaction_connected = bool(
        mirror_connected
        and coordination_connected
        and interaction_closure.get("status") == "WITNESSED"
        and interaction_closure.get("supernet_interaction_closed") is True
        and interaction_closure.get("closure_derivation_id") == derivation_id
        and interaction_closure.get("visual_closure_id") == visual_closure_id
        and interaction_closure.get("nrrf843_ui_id") == nrrf843_ui.get("id")
        and interaction_closure.get("unification_constraint", {}).get(
            "all_components_share_one_translational_truth"
        )
        is True
        and interaction_closure.get("black_mirror_physical_topology", {}).get(
            "closure_is_generated_by_projection"
        )
        is True
        and interaction_closure.get(
            "perspective_digital_potential_gate", {}
        ).get("open_potential_executes_as_equality")
        is False
    )
    closure_ui_validation = validate_ui_contract(closure_ui_contract)
    closure_ui_connected = bool(
        closure_ui_validation["valid"]
        and closure_ui_contract.get("schema") == CLOSURE_UI_SCHEMA
        and closure_ui_contract.get("status") == CLOSURE_UI_WITNESSED
        and closure_ui_contract.get("closure_derivation_id") == derivation_id
        and closure_ui_contract.get("visual_closure_id") == visual_closure_id
        and closure_ui_contract.get("nrrf843_ui_id") == nrrf843_ui.get("id")
        and closure_ui_contract.get("interaction_closure_id")
        == interaction_closure.get("id")
        and closure_ui_contract.get("execution", {}).get("closure_only") is True
        and closure_ui_contract.get("renderer_contract", {}).get(
            "visible_instance_source"
        )
        == "CONTRACT_ONLY"
    )

    components = [
        _component(
            "SOURCE_JOURNEY",
            connected=journey_connected,
            closure_derivation_id=derivation_id,
            visual_closure_id=visual_closure_id,
            source_return_ids=source_return_ids,
        ),
        _component(
            "PERSPECTIVE_VISUAL_MIRROR",
            connected=mirror_connected,
            closure_derivation_id=derivation_id,
            visual_closure_id=visual_closure_id,
            source_return_ids=source_return_ids,
            detail={
                "visual_mirror_id": mirror_id,
                "nrrf843_ui_id": nrrf843_ui.get("id"),
                "closure_source": "UI_PREIMAGE_OF_IMAGE",
            },
        ),
        _component(
            "SLEARN_MEMORY",
            connected=slearn_connected,
            closure_derivation_id=derivation_id,
            visual_closure_id=visual_closure_id,
            source_return_ids=source_return_ids,
        ),
        _component(
            "AI_TRANSLATION",
            connected=ai_connected,
            closure_derivation_id=derivation_id,
            visual_closure_id=visual_closure_id,
            source_return_ids=source_return_ids,
            detail={
                "witnessed_relation_ids": sorted(witnessed_relation_ids),
                "open_candidates_can_generate_equality": False,
            },
        ),
        _component(
            "TOKENOMIC_NATURAL_FORMS",
            connected=token_connected,
            closure_derivation_id=derivation_id,
            visual_closure_id=visual_closure_id,
            source_return_ids=token_members,
            detail={"currency_issued": False},
        ),
        _component(
            "LOCAL_GLOBAL_COORDINATION",
            connected=coordination_connected,
            closure_derivation_id=derivation_id,
            visual_closure_id=visual_closure_id,
            source_return_ids=source_return_ids,
            detail={"selected_natural_form_id": selected_form_id},
        ),
        _component(
            "UNITY_POTENTIAL_GATE",
            connected=unity_connected,
            closure_derivation_id=derivation_id,
            visual_closure_id=visual_closure_id,
            source_return_ids=source_return_ids,
            detail={
                "necessary_condition_status": unity_gate.get(
                    "necessary_condition_status", "OPEN"
                ),
                "authorizes_transition_alone": False,
            },
        ),
        _component(
            "AI_TOKEN_INTERACTION_CLOSURE",
            connected=interaction_connected,
            closure_derivation_id=derivation_id,
            visual_closure_id=visual_closure_id,
            source_return_ids=source_return_ids,
            detail={
                "interaction_closure_id": interaction_closure.get("id"),
                "physical_topology_status": interaction_closure.get(
                    "black_mirror_physical_topology", {}
                ).get("status", "OPEN"),
                "digital_potential_gate_status": interaction_closure.get(
                    "perspective_digital_potential_gate", {}
                ).get("status", "OPEN"),
                "active_operation_status": interaction_closure.get(
                    "active_operation", {}
                ).get("status", "GATED_OPEN"),
            },
        ),
        _component(
            "INTERACTIVE_UI_FORM",
            connected=(
                semantic_connected
                and action_connected
                and mirror_connected
                and interaction_connected
                and closure_ui_connected
            ),
            closure_derivation_id=derivation_id,
            visual_closure_id=visual_closure_id,
            source_return_ids=source_return_ids,
            detail={
                "admitted_semantic_element_ids": [
                    item.get("id")
                    for item in semantic_elements
                    if item.get("admission_status") not in {"OPEN", None}
                ],
                "allowed_return_operations": [
                    item.get("operation")
                    for item in closure_ui_contract.get("action_bindings", [])
                ],
                "closure_ui_contract_id": closure_ui_contract.get("id"),
                "closure_ui_contract_valid": closure_ui_validation["valid"],
                "all_visible_ui_nodes_contract_derived": (
                    closure_ui_validation[
                        "all_nodes_and_topology_records_have_exact_derivation"
                    ]
                ),
            },
        ),
    ]
    open_components = [
        item["name"]
        for item in components
        if item["factorization_status"] != "WITNESSED"
    ]
    unified = not open_components
    light_cone_paths = [
        {
            "id": item.get("id"),
            "target_event_id": item.get("target_event_id"),
            "constraint_status": item.get("truth_constraint_status", "OPEN"),
            "executes_as_equality": (
                item.get("truth_constraint_status") == "WITNESSED"
            ),
            "remains_connected_potential": True,
        }
        for item in nrrf842_journey.get("truth_curved_light_cone", {}).get(
            "paths", []
        )
    ]
    body = {
        "protocol": PROTOCOL,
        "schema": SCHEMA,
        "closure_derivation_id": derivation_id,
        "visual_closure_id": visual_closure_id,
        "visual_mirror_id": mirror_id,
        "nrrf843_ui_id": nrrf843_ui.get("id"),
        "interaction_closure_id": interaction_closure.get("id"),
        "closure_ui_contract_id": closure_ui_contract.get("id"),
        "source_return_ids": source_return_ids,
        "natural_form_ids": natural_form_ids,
        "status": "WITNESSED" if unified else "OPEN",
        "one_semantic_runtime": unified,
        "all_semantics_factor_through_one_translational_truth": unified,
        "separate_ui_semantic_runtime": False,
        "separate_ai_semantic_runtime": False,
        "separate_token_semantic_runtime": False,
        "semantic_external_component_ids": [],
        "semantic_isolated_component_ids": [],
        "open_factorization_component_ids": open_components,
        "components": components,
        "light_cone_paths": light_cone_paths,
        "execution": {
            "constraint_source": (
                "NRRF843_UI_PREIMAGE_IMAGE_TRANSLATIONAL_TRUTH_CLOSURE"
            ),
            "allowed_return_operations": (
                [
                    item.get("operation")
                    for item in closure_ui_contract.get("action_bindings", [])
                ]
                if unified
                else []
            ),
            "allowed_contract_action_ids": (
                closure_ui_contract.get("execution", {}).get(
                    "allowed_action_ids", []
                )
                if unified
                else []
            ),
            "closure_ui_contract_revalidated": closure_ui_validation["valid"],
            "active_operation": interaction_closure.get("active_operation"),
            "open_relations_execute_as_equality": False,
            "source_preserved_round_trip_required": True,
            "ordinary_interaction_open": True,
        },
        "transport_boundary": {
            "browser_html_svg": "TRANSPORT_ONLY",
            "network_io": "TRANSPORT_ONLY",
            "sensors": "SOURCE_CARRIER_ONLY",
            "can_define_semantics": False,
            "can_issue_truth": False,
            "can_admit_forms": False,
        },
        "truth_issued": False,
    }
    body["id"] = _digest("unified-truth-runtime", body)
    return body
