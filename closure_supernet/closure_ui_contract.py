from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from typing import Any, Iterable, Mapping


PROTOCOL = "SUPERNET-CLOSURE-ONLY-UI"
SCHEMA = "closure.supernet/perspective-interaction-ui-contract-v1"
BUILDER_VERSION = "closure-only-ui-1"
OPEN_STATUS = "OPEN_SOURCE_BOUNDARY"
BLOCKED_STATUS = "OPEN_TRUTH_CONSTRAINT"
WITNESSED_STATUS = "WITNESSED"
EXECUTION_ENDPOINT_TEMPLATE = "/supernet/interface/contracts/{contract_id}/execute"

ALLOWED_NODE_KINDS = {
    "surface",
    "region",
    "text",
    "metric",
    "input",
    "textarea",
    "select",
    "button",
    "topology",
}
ALLOWED_TEXT_TAGS = {"h1", "h2", "h3", "p", "strong", "span"}
ALLOWED_OPERATIONS = {
    "OFFER_SOURCE",
    "CONTINUE_INTERACTION",
    "PROPOSE_AGREEMENT",
    "DECIDE_AGREEMENT",
    "RETURN_AGREEMENT",
}
FIELD_KINDS = {"input", "textarea", "select"}


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _digest(prefix: str, value: Any) -> str:
    value_hash = hashlib.sha256(_stable(value).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{value_hash}"


def _unique(values: Iterable[Any]) -> list[str]:
    return list(
        dict.fromkeys(
            str(value)
            for value in values
            if value is not None and str(value)
        )
    )


def _basis(status: str) -> str:
    if status == WITNESSED_STATUS:
        return "TRANSLATIONAL_TRUTH_CLOSURE"
    if status == OPEN_STATUS:
        return "OPEN_AUTHORED_PERSPECTIVE_SOURCE_BOUNDARY"
    return "OPEN_UNWITNESSED_TRANSLATIONAL_TRUTH_CONSTRAINT"


def _derivation(
    *,
    status: str,
    perspective_id: str,
    closure_derivation_id: Any = None,
    visual_closure_id: Any = None,
    nrrf843_ui_id: Any = None,
    interaction_closure_id: Any = None,
    field_event_seq: int | None = None,
    natural_form_ids: Iterable[Any] = (),
    source_return_ids: Iterable[Any] = (),
) -> dict[str, Any]:
    return {
        "basis": _basis(status),
        "status": status,
        "perspective_id": perspective_id,
        "closure_derivation_id": closure_derivation_id,
        "visual_closure_id": visual_closure_id,
        "nrrf843_ui_id": nrrf843_ui_id,
        "interaction_closure_id": interaction_closure_id,
        "field_event_seq": field_event_seq,
        "natural_form_ids": _unique(natural_form_ids),
        "source_return_ids": _unique(source_return_ids),
        "truth_issued": False,
        "source_boundary_only": status == OPEN_STATUS,
    }


def _node(
    kind: str,
    node_id: str,
    derivation: dict[str, Any],
    **values: Any,
) -> dict[str, Any]:
    return {
        "id": node_id,
        "kind": kind,
        "derivation": derivation,
        **values,
    }


def _walk(node: Mapping[str, Any]) -> Iterable[dict[str, Any]]:
    yield dict(node)
    for child in node.get("children", []):
        if isinstance(child, Mapping):
            yield from _walk(child)


def _field(
    node_id: str,
    label: str,
    derivation: dict[str, Any],
    *,
    field_kind: str = "input",
    value: Any = "",
    placeholder: str = "",
    options: list[dict[str, str]] | None = None,
    required: bool = False,
    max_length: int = 4000,
) -> dict[str, Any]:
    return _node(
        field_kind,
        node_id,
        derivation,
        label=label,
        value=value,
        placeholder=placeholder,
        options=options or [],
        required=required,
        data_type="string",
        max_length=max_length,
    )


def _action(
    *,
    action_id: str,
    operation: str,
    label: str,
    derivation: dict[str, Any],
    input_field_ids: list[str],
    required_field_ids: list[str],
    immutable: dict[str, Any] | None = None,
    presentation: str = "primary",
) -> tuple[dict[str, Any], dict[str, Any]]:
    control = _node(
        "button",
        f"control:{action_id}",
        derivation,
        label=label,
        action_id=action_id,
        presentation=presentation,
    )
    binding = {
        "id": action_id,
        "operation": operation,
        "enabled": True,
        "input_field_ids": input_field_ids,
        "required_field_ids": required_field_ids,
        "immutable": immutable or {},
        "derivation": derivation,
        "external_semantic_action": False,
        "truth_issued": False,
    }
    return control, binding


def _source_fields(
    derivation: dict[str, Any],
    *,
    perspective_id: str,
    authored_by: str,
) -> list[dict[str, Any]]:
    return [
        _field(
            "author",
            "Author",
            derivation,
            value=authored_by,
            required=True,
            max_length=500,
        ),
        _field(
            "perspective",
            "Perspective",
            derivation,
            value=perspective_id,
            required=True,
            max_length=500,
        ),
        _field(
            "coordination_kind",
            "Natural interaction form",
            derivation,
            field_kind="select",
            value="intent",
            options=[
                {"value": "intent", "label": "Intent"},
                {"value": "person", "label": "Person"},
                {"value": "project", "label": "Project"},
                {"value": "resource", "label": "Resource"},
            ],
        ),
        _field(
            "location",
            "Relative locality",
            derivation,
            placeholder="optional locality",
            max_length=500,
        ),
        _field(
            "thought",
            "Perspective interaction",
            derivation,
            field_kind="textarea",
            placeholder="What do you want to understand, create, or do?",
            required=True,
            max_length=20_000,
        ),
    ]


def _source_action(
    *,
    action_id: str,
    operation: str,
    label: str,
    derivation: dict[str, Any],
    parent_event_id: str | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    return _action(
        action_id=action_id,
        operation=operation,
        label=label,
        derivation=derivation,
        input_field_ids=[
            "author",
            "perspective",
            "coordination_kind",
            "location",
            "thought",
        ],
        required_field_ids=["author", "perspective", "thought"],
        immutable={
            "parent_event_id": parent_event_id,
            "perspective_transition": operation == "OFFER_SOURCE",
            "closure_only_ui_contract": True,
        },
    )


def _theme(seed: str, derivation: dict[str, Any]) -> dict[str, Any]:
    hue = int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:6], 16) % 360
    complement = (hue + 112) % 360
    return {
        "derivation": derivation,
        "palette": {
            "background": f"hsl({hue} 38% 5%)",
            "surface": f"hsl({hue} 28% 10%)",
            "surface_alt": f"hsl({hue} 24% 14%)",
            "text": f"hsl({hue} 24% 94%)",
            "muted": f"hsl({hue} 13% 67%)",
            "accent": f"hsl({hue} 88% 66%)",
            "witnessed": f"hsl({complement} 78% 61%)",
            "open": "hsl(38 92% 61%)",
            "line": f"hsl({hue} 42% 30%)",
        },
        "geometry": {
            "max_width_px": 1420,
            "gap_px": 18,
            "radius_px": 22,
            "topology_height_px": 610,
        },
    }


def _renderer_contract() -> dict[str, Any]:
    return {
        "role": "GENERIC_CONTRACT_INTERPRETER",
        "visible_instance_source": "CONTRACT_ONLY",
        "hardcoded_visible_instances": False,
        "semantic_fallback": False,
        "undeclared_node_policy": "DO_NOT_RENDER",
        "undeclared_action_policy": "DO_NOT_EXECUTE",
        "allowed_node_kinds": sorted(ALLOWED_NODE_KINDS),
        "allowed_text_tags": sorted(ALLOWED_TEXT_TAGS),
    }


def _finish_contract(body: dict[str, Any]) -> dict[str, Any]:
    body["audit"] = _audit_contract(body)
    body["id"] = _digest("closure-ui-contract", body)
    return body


def derive_open_ui_contract(
    *,
    perspective_id: str | None = None,
) -> dict[str, Any]:
    perspective = str(perspective_id or "participant").strip() or "participant"
    derivation = _derivation(status=OPEN_STATUS, perspective_id=perspective)
    offer_control, offer_binding = _source_action(
        action_id="offer-source",
        operation="OFFER_SOURCE",
        label="Translate perspective into closure",
        derivation=derivation,
        parent_event_id=None,
    )
    root = _node(
        "surface",
        "open-perspective-contract",
        derivation,
        presentation="open-source",
        children=[
            _node(
                "region",
                "open-contract-reading",
                derivation,
                presentation="reading",
                children=[
                    _node(
                        "text",
                        "open-title",
                        derivation,
                        tag="h1",
                        text="OPEN PERSPECTIVE INTERACTION CONTRACT",
                    ),
                    _node(
                        "text",
                        "open-explanation",
                        derivation,
                        tag="p",
                        text=(
                            "No network form is displayed before a perspective "
                            "authors its source boundary. This contract derives "
                            "the complete first input without claiming closure."
                        ),
                    ),
                ],
            ),
            _node(
                "region",
                "open-source-composer",
                derivation,
                presentation="composer",
                children=[
                    *_source_fields(
                        derivation,
                        perspective_id=perspective,
                        authored_by=perspective,
                    ),
                    offer_control,
                ],
            ),
        ],
    )
    return _finish_contract(
        {
            "protocol": PROTOCOL,
            "schema": SCHEMA,
            "builder_version": BUILDER_VERSION,
            "status": OPEN_STATUS,
            "perspective_id": perspective,
            "focus_event_id": None,
            "closure_derivation_id": None,
            "visual_closure_id": None,
            "nrrf843_ui_id": None,
            "interaction_closure_id": None,
            "field_event_seq": None,
            "natural_form_ids": [],
            "source_return_ids": [],
            "root": root,
            "visual_form": _theme(f"open:{perspective}", derivation),
            "action_bindings": [offer_binding],
            "execution": {
                "endpoint_template": EXECUTION_ENDPOINT_TEMPLATE,
                "allowed_action_ids": [offer_binding["id"]],
                "source_boundary_actions_only": True,
                "contract_revalidation_required": True,
                "closure_only": True,
            },
            "renderer_contract": _renderer_contract(),
            "readiness_checks": {
                "authored_perspective_source_boundary": True,
                "translational_truth_closure_witnessed": False,
            },
            "claims": {
                "truth_issued": False,
                "natural_form_admitted": False,
                "price_issued": False,
                "legal_binding_claimed": False,
            },
        }
    )


def _derive_blocked_ui_contract(
    *,
    perspective_id: str,
    focus_event_id: str,
    closure_derivation_id: Any,
    visual_closure_id: Any,
    nrrf843_ui_id: Any,
    interaction_closure_id: Any,
    field_event_seq: int | None,
    natural_form_ids: list[str],
    source_return_ids: list[str],
    readiness_checks: dict[str, bool],
) -> dict[str, Any]:
    derivation = _derivation(
        status=BLOCKED_STATUS,
        perspective_id=perspective_id,
        closure_derivation_id=closure_derivation_id,
        visual_closure_id=visual_closure_id,
        nrrf843_ui_id=nrrf843_ui_id,
        interaction_closure_id=interaction_closure_id,
        field_event_seq=field_event_seq,
        natural_form_ids=natural_form_ids,
        source_return_ids=source_return_ids,
    )
    return _finish_contract(
        {
            "protocol": PROTOCOL,
            "schema": SCHEMA,
            "builder_version": BUILDER_VERSION,
            "status": BLOCKED_STATUS,
            "perspective_id": perspective_id,
            "focus_event_id": focus_event_id,
            "closure_derivation_id": closure_derivation_id,
            "visual_closure_id": visual_closure_id,
            "nrrf843_ui_id": nrrf843_ui_id,
            "interaction_closure_id": interaction_closure_id,
            "field_event_seq": field_event_seq,
            "natural_form_ids": natural_form_ids,
            "source_return_ids": source_return_ids,
            "root": _node(
                "surface",
                "open-truth-constraint",
                derivation,
                visible=False,
                children=[],
            ),
            "visual_form": _theme(
                f"blocked:{perspective_id}:{closure_derivation_id}",
                derivation,
            ),
            "action_bindings": [],
            "execution": {
                "endpoint_template": EXECUTION_ENDPOINT_TEMPLATE,
                "allowed_action_ids": [],
                "source_boundary_actions_only": False,
                "contract_revalidation_required": True,
                "closure_only": True,
            },
            "renderer_contract": _renderer_contract(),
            "readiness_checks": readiness_checks,
            "claims": {
                "truth_issued": False,
                "natural_form_admitted": False,
                "price_issued": False,
                "legal_binding_claimed": False,
            },
        }
    )


def _project_topology(
    *,
    physical_topology: dict[str, Any],
    visual_network: dict[str, Any],
    common_derivation: dict[str, Any],
    derivation_by_state: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    projected_nodes = list(physical_topology.get("nodes", []))
    source_by_event = {
        str(item.get("id") or ""): item
        for item in visual_network.get("nodes", [])
    }
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in projected_nodes:
        display = str(item.get("display_fibre_id") or "OPEN")
        groups.setdefault(display, []).append(item)
    positions: dict[str, dict[str, float]] = {}
    group_items = sorted(groups.items())
    for group_index, (_display, members) in enumerate(group_items):
        group_count = max(1, len(group_items))
        group_angle = (2 * math.pi * group_index / group_count) - math.pi / 2
        group_radius = 0 if group_count == 1 else 290
        center_x = group_radius * math.cos(group_angle)
        center_y = group_radius * 0.66 * math.sin(group_angle)
        ordered = sorted(
            members,
            key=lambda item: (
                str(item.get("natural_form_id") or ""),
                str(item.get("state_id") or ""),
                str(item.get("event_id") or ""),
            ),
        )
        member_radius = min(112, 34 + len(ordered) * 10)
        for member_index, member in enumerate(ordered):
            member_count = max(1, len(ordered))
            member_angle = 2 * math.pi * member_index / member_count
            event_id = str(member.get("event_id") or member.get("state_id") or "")
            positions[event_id] = {
                "x": round(
                    center_x
                    + (
                        0
                        if member_count == 1
                        else member_radius * math.cos(member_angle)
                    ),
                    3,
                ),
                "y": round(
                    center_y
                    + (
                        0
                        if member_count == 1
                        else member_radius * math.sin(member_angle)
                    ),
                    3,
                ),
            }
    nodes: list[dict[str, Any]] = []
    for item in projected_nodes:
        event_id = str(item.get("event_id") or item.get("state_id") or "")
        state_id = str(item.get("state_id") or "")
        source = source_by_event.get(event_id, {})
        exact_text = str(source.get("exact_text") or source.get("form_label") or event_id)
        label = exact_text if len(exact_text) <= 96 else exact_text[:93] + "..."
        nodes.append(
            {
                "id": event_id,
                "state_id": state_id,
                "label": label,
                "sublabel": str(
                    item.get("natural_form_id")
                    or item.get("perspective_id")
                    or ""
                ),
                "display_fibre_id": item.get("display_fibre_id"),
                "natural_form_id": item.get("natural_form_id"),
                "perspective_id": item.get("perspective_id"),
                "physical_world_return": bool(item.get("physical_world_return")),
                "radius": 38 if item.get("physical_world_return") else 30,
                "truth_status": (
                    WITNESSED_STATUS if item.get("source_preserved") else "OPEN"
                ),
                "derivation": derivation_by_state.get(
                    state_id, common_derivation
                ),
            }
        )
    edges: list[dict[str, Any]] = []
    for item in physical_topology.get("relations", []):
        state_ids = _unique(
            [item.get("source_state_id"), item.get("target_state_id")]
        )
        natural_ids = _unique(
            natural_id
            for state_id in state_ids
            for natural_id in derivation_by_state.get(
                state_id, {}
            ).get("natural_form_ids", [])
        )
        source_ids = _unique(
            source_id
            for state_id in state_ids
            for source_id in derivation_by_state.get(
                state_id, {}
            ).get("source_return_ids", [])
        )
        edge_derivation = {
            **common_derivation,
            "natural_form_ids": natural_ids
            or common_derivation["natural_form_ids"],
            "source_return_ids": source_ids
            or common_derivation["source_return_ids"],
        }
        edges.append(
            {
                "id": str(item.get("id") or ""),
                "source": str(item.get("source_event_id") or ""),
                "target": str(item.get("target_event_id") or ""),
                "label": str(item.get("relation_type") or ""),
                "truth_status": item.get("truth_constraint_status", "OPEN"),
                "same_display_fibre": bool(item.get("same_display_fibre")),
                "executes_as_equality": bool(
                    item.get("generates_topological_identification")
                ),
                "width": (
                    3
                    if item.get("truth_constraint_status") == WITNESSED_STATUS
                    else 1.5
                ),
                "derivation": edge_derivation,
            }
        )
    return {
        "projection": {
            "source": "NRRF843_ACTIVE_PERSPECTIVE_DISPLAY_READING",
            "active_perspective_id": physical_topology.get(
                "active_perspective_id"
            ),
            "closure_formula": physical_topology.get("closure_formula"),
            "display_reading": physical_topology.get("projection_reading", {}),
            "static_external_map": False,
            "physical_law_claimed": False,
            "derivation": common_derivation,
        },
        "view_box": [-520, -330, 1040, 660],
        "positions": positions,
        "nodes": nodes,
        "edges": edges,
        "evolution_frames": physical_topology.get("evolution_frames", []),
    }


def _proposal_form(
    *,
    derivation: dict[str, Any],
    coordination: dict[str, Any],
    potentials: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    intent = coordination.get("intent", {})
    intent_id = str(intent.get("event_id") or "")
    problem_id = str(intent.get("problem_id") or "")
    path_by_target = {
        str(item.get("target_event_id") or ""): item
        for item in coordination.get("paths", [])
    }
    admitted = [
        item
        for item in potentials
        if item.get("can_create_nonbinding_proposal") is True
        and item.get("visible_for_inspection") is True
        and item.get("target_event_id")
    ]
    if not intent_id or not problem_id or not admitted:
        return None, []
    options: list[dict[str, str]] = []
    for item in admitted:
        target_id = str(item["target_event_id"])
        path = path_by_target.get(target_id, {})
        options.append(
            {
                "value": target_id,
                "label": str(
                    path.get("label")
                    or item.get("label")
                    or item.get("kind")
                    or target_id
                ),
            }
        )
    fields = [
        _field(
            "proposal_target",
            "Potential path",
            derivation,
            field_kind="select",
            value=options[0]["value"],
            options=options,
            required=True,
        ),
        _field(
            "proposal_title",
            "Agreement form",
            derivation,
            value="Perspective interaction agreement",
            required=True,
            max_length=300,
        ),
        _field(
            "proposal_terms",
            "Exact mutual terms",
            derivation,
            field_kind="textarea",
            required=True,
            max_length=20_000,
        ),
        _field(
            "proposal_resources",
            "Resource constraints",
            derivation,
            field_kind="textarea",
            placeholder="one condition per line",
            max_length=20_000,
        ),
    ]
    control, binding = _action(
        action_id="propose-agreement",
        operation="PROPOSE_AGREEMENT",
        label="Author nonbinding agreement form",
        derivation=derivation,
        input_field_ids=[
            "author",
            "perspective",
            "proposal_target",
            "proposal_title",
            "proposal_terms",
            "proposal_resources",
        ],
        required_field_ids=[
            "author",
            "perspective",
            "proposal_target",
            "proposal_title",
            "proposal_terms",
        ],
        immutable={
            "intent_event_id": intent_id,
            "allowed_target_event_ids": [item["value"] for item in options],
            "closure_only_ui_contract": True,
        },
        presentation="commitment",
    )
    return (
        _node(
            "region",
            "agreement-proposal-contract",
            derivation,
            presentation="agreement",
            children=[
                _node(
                    "text",
                    "agreement-proposal-heading",
                    derivation,
                    tag="h2",
                    text="Mutual authorship agreement",
                ),
                *fields,
                control,
            ],
        ),
        [binding],
    )


def _active_agreement_form(
    *,
    derivation: dict[str, Any],
    coordination: dict[str, Any],
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    proposal = coordination.get("active_proposal") or {}
    proposal_id = str(proposal.get("id") or "")
    if not proposal_id:
        return None, []
    required = _unique(proposal.get("required_participant_ids", []))
    active_perspective = str(derivation.get("perspective_id") or "")
    participant_options = [
        {"value": active_perspective, "label": active_perspective}
    ] if active_perspective in required else []
    if not participant_options:
        return None, []
    participant_default = participant_options[0]["value"]
    children: list[dict[str, Any]] = [
        _node(
            "text",
            "active-agreement-heading",
            derivation,
            tag="h2",
            text=str(proposal.get("title") or "Active agreement"),
        ),
        _node(
            "metric",
            "active-agreement-status",
            derivation,
            label="Consent closure",
            value=str(
                proposal.get("consent_status")
                or proposal.get("status")
                or "OPEN"
            ),
        ),
        _node(
            "text",
            "active-agreement-terms",
            derivation,
            tag="p",
            text=str(proposal.get("exact_terms") or ""),
        ),
        _field(
            "decision_participant",
            "Your participant handle",
            derivation,
            field_kind="select",
            value=participant_default,
            options=participant_options,
            required=True,
            max_length=500,
        ),
        _field(
            "decision_text",
            "Exact decision statement",
            derivation,
            field_kind="textarea",
            required=True,
            max_length=20_000,
        ),
        _field(
            "decision_resources",
            "Resource offers",
            derivation,
            field_kind="textarea",
            placeholder="one offer per line",
            max_length=20_000,
        ),
        _field(
            "decision_constraints",
            "Decision constraints",
            derivation,
            field_kind="textarea",
            placeholder="one constraint per line",
            max_length=20_000,
        ),
    ]
    bindings: list[dict[str, Any]] = []
    for decision, label in (
        ("ACCEPT", "Accept exact terms"),
        ("REJECT", "Reject exact terms"),
        ("WITHDRAW", "Withdraw prior acceptance"),
    ):
        action_id = f"decide-{decision.lower()}"
        control, binding = _action(
            action_id=action_id,
            operation="DECIDE_AGREEMENT",
            label=label,
            derivation=derivation,
            input_field_ids=[
                "decision_participant",
                "perspective",
                "decision_text",
                "decision_resources",
                "decision_constraints",
            ],
            required_field_ids=[
                "decision_participant",
                "perspective",
                "decision_text",
            ],
            immutable={
                "proposal_id": proposal_id,
                "decision": decision,
                "closure_only_ui_contract": True,
            },
            presentation="consent",
        )
        children.append(control)
        bindings.append(binding)
    if str(proposal.get("consent_status") or "").upper() == "ACCEPTED":
        children.extend(
            [
                _field(
                    "return_author",
                    "Return author",
                    derivation,
                    value=participant_default,
                    required=True,
                    max_length=500,
                ),
                _field(
                    "return_text",
                    "Living action return",
                    derivation,
                    field_kind="textarea",
                    required=True,
                    max_length=20_000,
                ),
                _field(
                    "return_location",
                    "Return locality",
                    derivation,
                    max_length=500,
                ),
            ]
        )
        control, binding = _action(
            action_id="return-agreement",
            operation="RETURN_AGREEMENT",
            label="Return consequence to the field",
            derivation=derivation,
            input_field_ids=[
                "return_author",
                "perspective",
                "return_text",
                "return_location",
            ],
            required_field_ids=[
                "return_author",
                "perspective",
                "return_text",
            ],
            immutable={
                "proposal_id": proposal_id,
                "closure_only_ui_contract": True,
            },
            presentation="return",
        )
        children.append(control)
        bindings.append(binding)
    return (
        _node(
            "region",
            "active-agreement-contract",
            derivation,
            presentation="agreement",
            children=children,
        ),
        bindings,
    )


def derive_closure_ui_contract(
    *,
    truth_derivation: dict[str, Any],
    nrrf843_ui: dict[str, Any],
    nrrf842_journey: dict[str, Any],
    interaction_closure: dict[str, Any],
    coordination: dict[str, Any],
    visual_network: dict[str, Any],
    source_occurrences: list[dict[str, Any]],
    focus_event: dict[str, Any],
    field_event_seq: int | None = None,
) -> dict[str, Any]:
    physical_topology = interaction_closure.get(
        "black_mirror_physical_topology", {}
    )
    perspective = str(
        physical_topology.get("active_perspective_id")
        or nrrf842_journey.get("chosen_perspective", {}).get("perspective_id")
        or focus_event.get("perspective_id")
        or focus_event.get("authored_by")
        or "participant"
    )
    focus_event_id = str(focus_event.get("id") or "")
    authored_by = str(focus_event.get("authored_by") or perspective)
    natural_forms = list(truth_derivation.get("natural_forms", []))
    natural_form_ids = _unique(
        item.get("id") or item.get("natural_form") for item in natural_forms
    )
    visual_forms = list(
        truth_derivation.get("visual_existence", {}).get("forms", [])
    )
    source_return_ids = _unique(
        source_id
        for item in visual_forms
        for source_id in item.get("source_returns", [])
    )
    closure_derivation_id = truth_derivation.get("id")
    visual_closure_id = truth_derivation.get(
        "visual_truth_closure", {}
    ).get("id")
    nrrf843_ui_id = nrrf843_ui.get("id")
    interaction_closure_id = interaction_closure.get("id")
    active_reading = physical_topology.get("projection_reading", {})
    readiness_checks = {
        "closure_derivation_present": bool(closure_derivation_id),
        "visual_closure_present": bool(visual_closure_id),
        "natural_forms_present": bool(natural_form_ids),
        "source_return_provenance_present": bool(source_return_ids),
        "nrrf843_ui_witnessed": nrrf843_ui.get("status") == WITNESSED_STATUS,
        "nrrf843_ui_matches_closure": bool(
            nrrf843_ui.get("closure_derivation_id") == closure_derivation_id
            and nrrf843_ui.get("visual_closure_id") == visual_closure_id
        ),
        "truth_constraint_located_in_ui": bool(
            nrrf843_ui.get("truth_constraint_location", {}).get("located")
            is True
        ),
        "interaction_closure_witnessed": bool(
            interaction_closure.get("status") == WITNESSED_STATUS
            and interaction_closure.get("supernet_interaction_closed") is True
        ),
        "interaction_closure_matches_ui_truth": bool(
            interaction_closure.get("closure_derivation_id")
            == closure_derivation_id
            and interaction_closure.get("visual_closure_id")
            == visual_closure_id
            and interaction_closure.get("nrrf843_ui_id") == nrrf843_ui_id
        ),
        "active_perspective_projection_present": bool(
            perspective and active_reading
        ),
        "focus_event_present": bool(focus_event_id),
        "field_revision_present": bool(
            isinstance(field_event_seq, int) and field_event_seq > 0
        ),
    }
    if not all(readiness_checks.values()):
        return _derive_blocked_ui_contract(
            perspective_id=perspective,
            focus_event_id=focus_event_id,
            closure_derivation_id=closure_derivation_id,
            visual_closure_id=visual_closure_id,
            nrrf843_ui_id=nrrf843_ui_id,
            interaction_closure_id=interaction_closure_id,
            field_event_seq=field_event_seq,
            natural_form_ids=natural_form_ids,
            source_return_ids=source_return_ids,
            readiness_checks=readiness_checks,
        )
    common_derivation = _derivation(
        status=WITNESSED_STATUS,
        perspective_id=perspective,
        closure_derivation_id=closure_derivation_id,
        visual_closure_id=visual_closure_id,
        nrrf843_ui_id=nrrf843_ui_id,
        interaction_closure_id=interaction_closure_id,
        field_event_seq=field_event_seq,
        natural_form_ids=natural_form_ids,
        source_return_ids=source_return_ids,
    )
    form_by_state = {
        str(member): str(form.get("id") or form.get("natural_form") or "")
        for form in natural_forms
        for member in form.get("members", [])
    }
    returns_by_state = {
        str(item.get("id") or ""): _unique(item.get("source_returns", []))
        for item in visual_forms
    }
    derivation_by_state = {
        state_id: {
            **common_derivation,
            "natural_form_ids": _unique([form_by_state.get(state_id)]),
            "source_return_ids": returns
            or common_derivation["source_return_ids"],
        }
        for state_id, returns in returns_by_state.items()
    }
    topology = _project_topology(
        physical_topology=physical_topology,
        visual_network=visual_network,
        common_derivation=common_derivation,
        derivation_by_state=derivation_by_state,
    )
    potentials = list(
        interaction_closure.get(
            "perspective_digital_potential_gate", {}
        ).get("potentials", [])
    )
    potential_children = [
        _node(
            "region",
            f"potential:{item.get('id')}",
            common_derivation,
            presentation=(
                "witnessed"
                if item.get("truth_constraint_status") == WITNESSED_STATUS
                else "open"
            ),
            children=[
                _node(
                    "text",
                    f"potential-label:{item.get('id')}",
                    common_derivation,
                    tag="strong",
                    text=str(
                        item.get("label")
                        or item.get("kind")
                        or "OPEN potential"
                    ),
                ),
                _node(
                    "text",
                    f"potential-status:{item.get('id')}",
                    common_derivation,
                    tag="span",
                    text=(
                        f"{item.get('truth_constraint_status', 'OPEN')} · "
                        "equality execution "
                        f"{str(bool(item.get('executes_as_equality'))).upper()}"
                    ),
                ),
            ],
        )
        for item in potentials
        if item.get("visible_for_inspection") is True
        or item.get("remains_connected_potential") is True
    ]
    source_children = [
        _node(
            "text",
            f"source:{item.get('id')}",
            derivation_by_state.get(
                str(item.get("id") or ""), common_derivation
            ),
            tag="p",
            text=str(item.get("exact_text") or item.get("id") or ""),
        )
        for item in source_occurrences
    ]
    offer_control, offer_binding = _source_action(
        action_id="offer-next-source",
        operation="OFFER_SOURCE",
        label="Translate next perspective interaction",
        derivation=common_derivation,
        parent_event_id=None,
    )
    continue_control, continue_binding = _source_action(
        action_id="continue-local-interaction",
        operation="CONTINUE_INTERACTION",
        label="Continue within this perspective closure",
        derivation=common_derivation,
        parent_event_id=focus_event_id,
    )
    proposal_region, proposal_bindings = _proposal_form(
        derivation=common_derivation,
        coordination=coordination,
        potentials=potentials,
    )
    active_region, active_bindings = _active_agreement_form(
        derivation=common_derivation,
        coordination=coordination,
    )
    active_operation = interaction_closure.get("active_operation", {})
    title = (
        f"{perspective} · {len(natural_form_ids)} natural form"
        f"{'s' if len(natural_form_ids) != 1 else ''}"
    )
    root_children: list[dict[str, Any]] = [
        _node(
            "region",
            "closure-reading",
            common_derivation,
            presentation="reading",
            children=[
                _node(
                    "text",
                    "closure-title",
                    common_derivation,
                    tag="h1",
                    text=title,
                ),
                _node(
                    "text",
                    "closure-equation",
                    common_derivation,
                    tag="p",
                    text=(
                        "perspective interaction contract → UI mirror → "
                        "translational truth → natural form → interaction return"
                    ),
                ),
                _node(
                    "metric",
                    "closure-status",
                    common_derivation,
                    label="Supernet unification",
                    value=interaction_closure.get("status", "OPEN"),
                ),
                _node(
                    "metric",
                    "next-form-status",
                    common_derivation,
                    label="Next natural form",
                    value=(
                        f"{active_operation.get('requested_natural_form', 'OPEN')} · "
                        f"{active_operation.get('status', 'OPEN')}"
                    ),
                ),
            ],
        ),
        _node(
            "topology",
            "closure-topology",
            common_derivation,
            presentation="mirror",
            topology=topology,
        ),
        _node(
            "region",
            "source-fibre",
            common_derivation,
            presentation="source",
            children=[
                _node(
                    "text",
                    "source-heading",
                    common_derivation,
                    tag="h2",
                    text="Source-preserved perspective fibre",
                ),
                *source_children,
            ],
        ),
        _node(
            "region",
            "digital-potentials",
            common_derivation,
            presentation="potentials",
            children=[
                _node(
                    "text",
                    "potential-heading",
                    common_derivation,
                    tag="h2",
                    text="Perspective digital potential gate",
                ),
                *potential_children,
            ],
        ),
        _node(
            "region",
            "closure-composer",
            common_derivation,
            presentation="composer",
            children=[
                *_source_fields(
                    common_derivation,
                    perspective_id=perspective,
                    authored_by=authored_by,
                ),
                offer_control,
                continue_control,
            ],
        ),
    ]
    if proposal_region is not None:
        root_children.append(proposal_region)
    if active_region is not None:
        root_children.append(active_region)
    root = _node(
        "surface",
        "closure-perspective-contract",
        common_derivation,
        presentation="closure-field",
        children=root_children,
    )
    bindings = [
        offer_binding,
        continue_binding,
        *proposal_bindings,
        *active_bindings,
    ]
    return _finish_contract(
        {
            "protocol": PROTOCOL,
            "schema": SCHEMA,
            "builder_version": BUILDER_VERSION,
            "status": WITNESSED_STATUS,
            "perspective_id": perspective,
            "focus_event_id": focus_event_id,
            "closure_derivation_id": closure_derivation_id,
            "visual_closure_id": visual_closure_id,
            "nrrf843_ui_id": nrrf843_ui_id,
            "interaction_closure_id": interaction_closure_id,
            "field_event_seq": field_event_seq,
            "natural_form_ids": natural_form_ids,
            "source_return_ids": source_return_ids,
            "root": root,
            "visual_form": _theme(
                f"{perspective}:{closure_derivation_id}:{active_reading}",
                common_derivation,
            ),
            "action_bindings": bindings,
            "execution": {
                "endpoint_template": EXECUTION_ENDPOINT_TEMPLATE,
                "allowed_action_ids": [item["id"] for item in bindings],
                "source_boundary_actions_only": False,
                "contract_revalidation_required": True,
                "closure_only": True,
            },
            "renderer_contract": _renderer_contract(),
            "readiness_checks": readiness_checks,
            "claims": {
                "truth_issued": False,
                "natural_form_admitted": True,
                "price_issued": False,
                "physical_law_claimed": False,
                "legal_binding_claimed": False,
            },
        }
    )


def _derivation_errors(
    contract: Mapping[str, Any],
    derivation: Any,
    *,
    label: str,
) -> list[str]:
    if not isinstance(derivation, Mapping):
        return [f"{label}:missing-derivation"]
    status = str(contract.get("status") or "")
    errors: list[str] = []
    if derivation.get("basis") != _basis(status):
        errors.append(f"{label}:basis")
    if derivation.get("status") != status:
        errors.append(f"{label}:status")
    if derivation.get("perspective_id") != contract.get("perspective_id"):
        errors.append(f"{label}:perspective")
    if derivation.get("truth_issued") is not False:
        errors.append(f"{label}:truth-issued")
    if status == OPEN_STATUS:
        for key in (
            "closure_derivation_id",
            "visual_closure_id",
            "nrrf843_ui_id",
            "interaction_closure_id",
            "field_event_seq",
        ):
            if derivation.get(key) is not None:
                errors.append(f"{label}:{key}")
        if derivation.get("source_boundary_only") is not True:
            errors.append(f"{label}:source-boundary")
        return errors
    for key in (
        "closure_derivation_id",
        "visual_closure_id",
        "nrrf843_ui_id",
        "interaction_closure_id",
        "field_event_seq",
    ):
        if derivation.get(key) != contract.get(key):
            errors.append(f"{label}:{key}")
    if status == WITNESSED_STATUS:
        contract_forms = set(_unique(contract.get("natural_form_ids", [])))
        contract_sources = set(_unique(contract.get("source_return_ids", [])))
        derived_forms = set(_unique(derivation.get("natural_form_ids", [])))
        derived_sources = set(_unique(derivation.get("source_return_ids", [])))
        if not derived_forms or not derived_forms.issubset(contract_forms):
            errors.append(f"{label}:natural-forms")
        if not derived_sources or not derived_sources.issubset(contract_sources):
            errors.append(f"{label}:source-returns")
        if derivation.get("source_boundary_only") is not False:
            errors.append(f"{label}:not-source-boundary")
    return errors


def _audit_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if contract.get("protocol") != PROTOCOL:
        errors.append("contract:protocol")
    if contract.get("schema") != SCHEMA:
        errors.append("contract:schema")
    if contract.get("builder_version") != BUILDER_VERSION:
        errors.append("contract:builder-version")
    status = str(contract.get("status") or "")
    if status not in {OPEN_STATUS, BLOCKED_STATUS, WITNESSED_STATUS}:
        errors.append("contract:status")
    root = contract.get("root")
    nodes = list(_walk(root)) if isinstance(root, Mapping) else []
    if not nodes:
        errors.append("tree:missing-root")
    node_ids = [str(item.get("id") or "") for item in nodes]
    if any(not item for item in node_ids):
        errors.append("tree:empty-node-id")
    if len(node_ids) != len(set(node_ids)):
        errors.append("tree:duplicate-node-id")
    topology_record_count = 0
    for node in nodes:
        node_id = str(node.get("id") or "unknown")
        kind = str(node.get("kind") or "")
        if kind not in ALLOWED_NODE_KINDS:
            errors.append(f"node:{node_id}:kind")
        errors.extend(
            _derivation_errors(
                contract,
                node.get("derivation"),
                label=f"node:{node_id}",
            )
        )
        if kind == "text" and node.get("tag") not in ALLOWED_TEXT_TAGS:
            errors.append(f"node:{node_id}:tag")
        if kind in FIELD_KINDS:
            if node.get("data_type") != "string":
                errors.append(f"node:{node_id}:data-type")
            if not isinstance(node.get("max_length"), int):
                errors.append(f"node:{node_id}:max-length")
            if kind == "select":
                options = node.get("options", [])
                values = [
                    str(item.get("value") or "")
                    for item in options
                    if isinstance(item, Mapping)
                ]
                if not values or any(not value for value in values):
                    errors.append(f"node:{node_id}:options")
                if len(values) != len(set(values)):
                    errors.append(f"node:{node_id}:duplicate-options")
                if str(node.get("value") or "") not in values:
                    errors.append(f"node:{node_id}:selected-option")
        if kind != "topology":
            continue
        topology = node.get("topology")
        if not isinstance(topology, Mapping):
            errors.append(f"node:{node_id}:topology")
            continue
        projection = topology.get("projection")
        if not isinstance(projection, Mapping):
            errors.append(f"node:{node_id}:projection")
        else:
            errors.extend(
                _derivation_errors(
                    contract,
                    projection.get("derivation"),
                    label=f"node:{node_id}:projection",
                )
            )
            if projection.get("static_external_map") is not False:
                errors.append(f"node:{node_id}:static-map")
        topology_nodes = list(topology.get("nodes", []))
        topology_record_count += len(topology_nodes)
        topology_ids = [
            str(item.get("id") or "")
            for item in topology_nodes
            if isinstance(item, Mapping)
        ]
        if any(not item for item in topology_ids):
            errors.append(f"node:{node_id}:empty-topology-node")
        if len(topology_ids) != len(set(topology_ids)):
            errors.append(f"node:{node_id}:duplicate-topology-node")
        positions = topology.get("positions", {})
        if set(topology_ids) != set(str(key) for key in positions):
            errors.append(f"node:{node_id}:positions")
        for item in topology_nodes:
            if not isinstance(item, Mapping):
                errors.append(f"node:{node_id}:topology-node")
                continue
            errors.extend(
                _derivation_errors(
                    contract,
                    item.get("derivation"),
                    label=f"topology-node:{item.get('id')}",
                )
            )
            if not isinstance(item.get("radius"), (int, float)):
                errors.append(f"topology-node:{item.get('id')}:radius")
        topology_edges = list(topology.get("edges", []))
        topology_record_count += len(topology_edges)
        edge_ids = [
            str(item.get("id") or "")
            for item in topology_edges
            if isinstance(item, Mapping)
        ]
        if len(edge_ids) != len(set(edge_ids)):
            errors.append(f"node:{node_id}:duplicate-topology-edge")
        for item in topology_edges:
            if not isinstance(item, Mapping):
                errors.append(f"node:{node_id}:topology-edge")
                continue
            edge_id = str(item.get("id") or "")
            if (
                str(item.get("source") or "") not in topology_ids
                or str(item.get("target") or "") not in topology_ids
            ):
                errors.append(f"topology-edge:{edge_id}:endpoint")
            if (
                item.get("truth_status") != WITNESSED_STATUS
                and item.get("executes_as_equality") is True
            ):
                errors.append(f"topology-edge:{edge_id}:open-equality")
            if not isinstance(item.get("width"), (int, float)):
                errors.append(f"topology-edge:{edge_id}:width")
            errors.extend(
                _derivation_errors(
                    contract,
                    item.get("derivation"),
                    label=f"topology-edge:{edge_id}",
                )
            )
    field_nodes = [item for item in nodes if item.get("kind") in FIELD_KINDS]
    field_ids = [str(item.get("id") or "") for item in field_nodes]
    if len(field_ids) != len(set(field_ids)):
        errors.append("tree:duplicate-field-id")
    controls = [
        item
        for item in nodes
        if item.get("kind") == "button" and item.get("action_id")
    ]
    control_ids = [str(item.get("action_id")) for item in controls]
    if len(control_ids) != len(set(control_ids)):
        errors.append("tree:duplicate-control")
    actions = list(contract.get("action_bindings", []))
    action_ids = [
        str(item.get("id") or "")
        for item in actions
        if isinstance(item, Mapping)
    ]
    if any(not item for item in action_ids):
        errors.append("actions:empty-id")
    if len(action_ids) != len(set(action_ids)):
        errors.append("actions:duplicate-id")
    for item in actions:
        if not isinstance(item, Mapping):
            errors.append("actions:not-object")
            continue
        action_id = str(item.get("id") or "")
        if item.get("operation") not in ALLOWED_OPERATIONS:
            errors.append(f"action:{action_id}:operation")
        if item.get("enabled") is not True:
            errors.append(f"action:{action_id}:enabled")
        if item.get("external_semantic_action") is not False:
            errors.append(f"action:{action_id}:external")
        if item.get("truth_issued") is not False:
            errors.append(f"action:{action_id}:truth-issued")
        if any(
            key in item
            for key in ("endpoint", "endpoint_selector", "method", "payload", "url")
        ):
            errors.append(f"action:{action_id}:client-dispatch")
        input_ids = [str(value) for value in item.get("input_field_ids", [])]
        required_ids = [str(value) for value in item.get("required_field_ids", [])]
        if len(input_ids) != len(set(input_ids)):
            errors.append(f"action:{action_id}:duplicate-input")
        if not set(input_ids).issubset(set(field_ids)):
            errors.append(f"action:{action_id}:unknown-input")
        if not set(required_ids).issubset(set(input_ids)):
            errors.append(f"action:{action_id}:unknown-required")
        if not isinstance(item.get("immutable"), Mapping):
            errors.append(f"action:{action_id}:immutable")
        elif bool(item.get("immutable", {}).get("perspective_transition")) != (
            item.get("operation") == "OFFER_SOURCE"
        ):
            errors.append(f"action:{action_id}:perspective-transition")
        errors.extend(
            _derivation_errors(
                contract,
                item.get("derivation"),
                label=f"action:{action_id}",
            )
        )
    execution = contract.get("execution", {})
    allowed = [
        str(item) for item in execution.get("allowed_action_ids", [])
    ]
    if control_ids != action_ids:
        errors.append("actions:controls-order-or-membership")
    if action_ids != allowed:
        errors.append("actions:allowlist-order-or-membership")
    if execution.get("endpoint_template") != EXECUTION_ENDPOINT_TEMPLATE:
        errors.append("execution:endpoint-template")
    if execution.get("contract_revalidation_required") is not True:
        errors.append("execution:revalidation")
    if execution.get("closure_only") is not True:
        errors.append("execution:closure-only")
    renderer = contract.get("renderer_contract", {})
    if renderer.get("role") != "GENERIC_CONTRACT_INTERPRETER":
        errors.append("renderer:role")
    if renderer.get("visible_instance_source") != "CONTRACT_ONLY":
        errors.append("renderer:instance-source")
    if renderer.get("hardcoded_visible_instances") is not False:
        errors.append("renderer:hardcoded")
    if renderer.get("semantic_fallback") is not False:
        errors.append("renderer:fallback")
    if set(renderer.get("allowed_node_kinds", [])) != ALLOWED_NODE_KINDS:
        errors.append("renderer:node-kinds")
    if set(renderer.get("allowed_text_tags", [])) != ALLOWED_TEXT_TAGS:
        errors.append("renderer:text-tags")
    errors.extend(
        _derivation_errors(
            contract,
            contract.get("visual_form", {}).get("derivation"),
            label="visual-form",
        )
    )
    if status == OPEN_STATUS:
        if action_ids != ["offer-source"]:
            errors.append("open-boundary:actions")
        if any(
            item.get("operation") != "OFFER_SOURCE"
            for item in actions
            if isinstance(item, Mapping)
        ):
            errors.append("open-boundary:operation")
        if execution.get("source_boundary_actions_only") is not True:
            errors.append("open-boundary:execution")
        if contract.get("claims", {}).get("natural_form_admitted") is not False:
            errors.append("open-boundary:natural-form")
    elif status == BLOCKED_STATUS:
        if action_ids:
            errors.append("blocked:actions")
        if root and root.get("visible") is not False:
            errors.append("blocked:visible")
    elif status == WITNESSED_STATUS:
        for key in (
            "closure_derivation_id",
            "visual_closure_id",
            "nrrf843_ui_id",
            "interaction_closure_id",
            "field_event_seq",
            "focus_event_id",
        ):
            if not contract.get(key):
                errors.append(f"witnessed:{key}")
        if not contract.get("natural_form_ids"):
            errors.append("witnessed:natural-forms")
        if not contract.get("source_return_ids"):
            errors.append("witnessed:source-returns")
        if not all(contract.get("readiness_checks", {}).values()):
            errors.append("witnessed:readiness")
        if contract.get("claims", {}).get("natural_form_admitted") is not True:
            errors.append("witnessed:natural-form")
    ordered_errors = sorted(Counter(errors))
    derivation_error = any(
        suffix in item
        for item in ordered_errors
        for suffix in (
            ":basis",
            ":status",
            ":perspective",
            ":closure_derivation_id",
            ":visual_closure_id",
            ":nrrf843_ui_id",
            ":interaction_closure_id",
            ":field_event_seq",
            ":natural-forms",
            ":source-returns",
            ":missing-derivation",
        )
    )
    return {
        "node_count": len(nodes),
        "field_count": len(field_ids),
        "action_count": len(action_ids),
        "topology_record_count": topology_record_count,
        "all_nodes_and_topology_records_have_exact_derivation": (
            not derivation_error
        ),
        "unique_reachable_node_and_field_ids": not any(
            item.startswith("tree:") and "duplicate" in item
            for item in ordered_errors
        ),
        "controls_equal_actions_equal_execution_allowlist": not any(
            item.startswith("actions:") for item in ordered_errors
        ),
        "server_side_operation_allowlist_only": not any(
            item.startswith("action:")
            and (
                item.endswith(":operation")
                or item.endswith(":client-dispatch")
                or item.endswith(":external")
            )
            for item in ordered_errors
        ),
        "perspective_projection_not_static_external_map": not any(
            item.endswith(":static-map") for item in ordered_errors
        ),
        "hardcoded_visible_instances": False,
        "semantic_fallback": False,
        "errors": ordered_errors,
        "closure_only_execution": not ordered_errors,
    }


def validate_ui_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    structural = _audit_contract(contract)
    stored_audit = contract.get("audit")
    audit_matches = isinstance(stored_audit, Mapping) and dict(
        stored_audit
    ) == structural
    body = {key: value for key, value in contract.items() if key != "id"}
    expected_id = _digest("closure-ui-contract", body)
    id_matches = contract.get("id") == expected_id
    return {
        **structural,
        "stored_audit_matches_recomputation": audit_matches,
        "contract_id_matches_content": id_matches,
        "valid": bool(
            structural["closure_only_execution"]
            and audit_matches
            and id_matches
        ),
    }


__all__ = [
    "ALLOWED_NODE_KINDS",
    "ALLOWED_OPERATIONS",
    "BLOCKED_STATUS",
    "BUILDER_VERSION",
    "EXECUTION_ENDPOINT_TEMPLATE",
    "OPEN_STATUS",
    "PROTOCOL",
    "SCHEMA",
    "WITNESSED_STATUS",
    "derive_closure_ui_contract",
    "derive_open_ui_contract",
    "validate_ui_contract",
]
