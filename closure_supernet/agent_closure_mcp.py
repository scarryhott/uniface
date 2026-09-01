from __future__ import annotations

"""Agent and self-runtime readings of the one Supernet closure form.

MCP is transport only. Every mutating tool resolves to the current
``AI_CONTINUING`` interaction and invokes the exact same ``SUPERNET_TRANSLATE``
handler used by the browser. The canonical translation receipt is never amended
by the agent adapter. Self-observation projects the same content-addressed
closure form and has no truth authority.
"""

import os
from typing import Annotated, Any, Literal

from fastapi import FastAPI
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from pydantic import Field

from .nrrf892_runtime_bridge import VISION_SLIDE_OPERATOR
from .supernet_closure_form import TRANSLATE_OPERATOR, derive_full_supernet_gate_contract

AgentSheaf = Literal[
    "HUMAN_INTERACTION",
    "SLEARN_PERSPECTIVE",
    "BLACK_MIRROR_SENSOR",
    "TOKENOMIC_AI",
    "RESOURCE_WORLD",
    "AGI_SECOND_BRAIN",
    "PSYCHOPHENOMENAL",
    "UNKNOWN_UAP_HYPOTHESIS",
]


def _provenance(runtime: Any) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in runtime.ledger.list_returns():
        event_id = str(item.get("id") or "")
        perspective_id = str(item.get("perspective_id") or "")
        if event_id and perspective_id:
            result[event_id] = perspective_id
    return result


def _gate(runtime: Any, perspective_id: str, focus_event_id: str | None = None) -> dict[str, Any]:
    closure = runtime.project(perspective_id=perspective_id, focus_event_id=focus_event_id)
    return derive_full_supernet_gate_contract(
        closure,
        source_perspective_by_event=_provenance(runtime),
    )


def _self_reading(gate: dict[str, Any]) -> dict[str, Any]:
    form = gate["supernet_closure_form"]
    return {
        "published_semantic_carrier": "SUPERNET_CLOSURE_FORM",
        "closure_form_id": form["id"],
        "translation_operator": TRANSLATE_OPERATOR,
        "runtime_identity_id": form["runtime_identity_id"],
        "truth_invariant_id": form["truth_invariant_id"],
        "runtime_identity_is_translational_truth": True,
        "vision_slide_operator": VISION_SLIDE_OPERATOR,
        "self_runtime_is_closure_form_reading": True,
        "self_observation_authors_truth": False,
        "separate_self_runtime_authority": False,
    }


def _continuing_interaction(gate: dict[str, Any]) -> dict[str, Any]:
    for row in gate["supernet_closure_form"].get("interactions") or []:
        if row.get("ai_token_phase") == "AI_CONTINUING":
            return row
    raise ValueError("The current closure form has no continuing interaction to translate")


def _compact_interface(gate: dict[str, Any], perspective_id: str) -> dict[str, Any]:
    closure = gate["closure_ui_contract"]
    return {
        "focus_event_id": gate.get("focus_event_id"),
        "perspective_id": perspective_id,
        "natural_chart": gate["supernet_closure_form"].get("seen_id"),
        "closure_level": gate["supernet_closure_form"]["id"],
        "visual_closure": closure,
        "source_fibre": closure.get("source_occurrences") or [],
        "two_person_E2E": "CONTINUING",
        "truth_issued": False,
    }


def _allowed_hosts() -> list[str]:
    hosts = {
        "localhost",
        "localhost:*",
        "127.0.0.1",
        "127.0.0.1:*",
        "testserver",
        "testserver:*",
        "uniface-supernet-production.up.railway.app",
        "uniface-supernet-production.up.railway.app:*",
    }
    railway = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
    if railway and "*" not in railway and "://" not in railway:
        hosts.add(railway)
        if ":" not in railway:
            hosts.add(f"{railway}:*")
    return sorted(hosts)


def attach_supernet_agent_mcp(app: FastAPI) -> FastAPI:
    if getattr(app.state, "supernet_agent_mcp_attached", False):
        return app

    runtime = app.state.runtime
    translate = app.state.supernet_translate
    app.state.supernet_agent_mcp_attached = True
    mcp = MCPServer("Closure Supernet Agent")

    def current(perspective_id: str | None, focus_event_id: str | None = None) -> dict[str, Any]:
        return _gate(runtime, perspective_id or "runtime:self", focus_event_id)

    async def translate_text(
        *,
        exact_text: str,
        actor_id: str,
        perspective_id: str | None,
        focus_event_id: str | None,
        interaction_kind: str,
        form_label: str | None = None,
        sheaf: str | None = None,
    ) -> dict[str, Any]:
        perspective = perspective_id or actor_id
        source = current(perspective, focus_event_id)
        interaction = _continuing_interaction(source)
        result = await translate(
            source["id"],
            {
                "relation_id": interaction["path_id"],
                "perspective_id": perspective,
                "focus_event_id": source.get("focus_event_id"),
                "navigation_context": source["navigation_context"],
                "source_closure_form_id": source["supernet_closure_form_id"],
                "source_interaction_id": interaction["id"],
                "exact_source_return": exact_text.strip(),
                "local_perspective_hair_millidegrees": 0,
                "local_perspective_zoom_milli": 1000,
            },
        )
        target = result["supernet_potential_gate"]
        return {
            "event_id": target.get("focus_event_id"),
            "translation": dict(result["translation"]),
            "self_runtime": _self_reading(target),
            "interface": _compact_interface(target, perspective),
            "agent_interaction_kind": interaction_kind,
            "agent_actor_id": actor_id,
            "agent_form_label": form_label,
            "agent_sheaf": sheaf,
            "agent_interaction_is_this_translation": True,
            "browser_and_agent_share_translation_operator": True,
            "separate_agent_mutation_authority": False,
            "truth_issued": False,
        }

    @mcp.tool(title="Observe Supernet", annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False))
    async def supernet_observe(
        event_id: str | None = None,
        perspective_id: str | None = None,
        limit: Annotated[int, Field(ge=1, le=50)] = 12,
    ) -> dict[str, Any]:
        perspective = perspective_id or "runtime:self"
        gate = current(perspective, event_id)
        return {
            "recent_events": runtime.ledger.list_returns()[-limit:],
            "interface": _compact_interface(gate, perspective),
            "self_runtime": _self_reading(gate),
            "subsystems_are_lenses": True,
            "self_observation_authors_truth": False,
            "truth_issued": False,
        }

    @mcp.tool(title="Offer or interact in Supernet", annotations=ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False))
    async def supernet_offer(exact_text: Annotated[str, Field(min_length=1)], actor_id: str = "openai-agent", perspective_id: str | None = None, form_label: str = "agent interaction", parent_event_id: str | None = None, sheaf: AgentSheaf | None = None) -> dict[str, Any]:
        return await translate_text(exact_text=exact_text, actor_id=actor_id, perspective_id=perspective_id, focus_event_id=parent_event_id, interaction_kind="OFFER", form_label=form_label, sheaf=sheaf)

    @mcp.tool(title="Relate Supernet events", annotations=ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False))
    async def supernet_relate(source_event_id: str, target_event_id: str, relation_label: str, actor_id: str = "openai-agent", perspective_id: str | None = None, bidirectional: bool = False) -> dict[str, Any]:
        direction = "<->" if bidirectional else "->"
        return await translate_text(exact_text=f"RELATE {source_event_id} {direction} {target_event_id}: {relation_label}", actor_id=actor_id, perspective_id=perspective_id, focus_event_id=source_event_id, interaction_kind="RELATE")

    @mcp.tool(title="Refine a live relation", annotations=ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False))
    async def supernet_refine(source_event_id: str, selected_relation_id: str, actor_id: str = "openai-agent", perspective_id: str | None = None, reason: str = "Agent refines the live relational field") -> dict[str, Any]:
        return await translate_text(exact_text=f"REFINE {selected_relation_id}: {reason}", actor_id=actor_id, perspective_id=perspective_id, focus_event_id=source_event_id, interaction_kind="REFINE")

    @mcp.tool(title="Return a Supernet form", annotations=ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False))
    async def supernet_return(event_id: str, exact_text: Annotated[str, Field(min_length=1)], actor_id: str = "openai-agent", perspective_id: str | None = None, form_label: str = "agent return") -> dict[str, Any]:
        return await translate_text(exact_text=exact_text, actor_id=actor_id, perspective_id=perspective_id, focus_event_id=event_id, interaction_kind="RETURN", form_label=form_label)

    @mcp.tool(title="Continue a Supernet event", annotations=ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False))
    async def supernet_reopen(event_id: str, reason: Annotated[str, Field(min_length=1)], actor_id: str = "openai-agent", perspective_id: str | None = None, reopened_sites: list[str] | None = None, successor_hints: list[str] | None = None) -> dict[str, Any]:
        return await translate_text(exact_text=f"CONTINUE {event_id}: {reason}; sites={','.join(reopened_sites or [])}; hints={','.join(successor_hints or [])}", actor_id=actor_id, perspective_id=perspective_id, focus_event_id=event_id, interaction_kind="CONTINUE")

    @mcp.tool(title="Create a collective continuation", annotations=ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False))
    async def supernet_collective(event_ids: Annotated[list[str], Field(min_length=2)], exact_text: Annotated[str, Field(min_length=1)], actor_id: str = "openai-agent", perspective_id: str | None = None) -> dict[str, Any]:
        ids = list(dict.fromkeys(event_ids))
        if len(ids) < 2:
            raise ValueError("A collective continuation requires at least two distinct events")
        return await translate_text(exact_text=f"COLLECTIVE[{','.join(ids)}]: {exact_text}", actor_id=actor_id, perspective_id=perspective_id, focus_event_id=ids[0], interaction_kind="COLLECTIVE")

    mcp_app = mcp.streamable_http_app(
        streamable_http_path="/",
        stateless_http=True,
        json_response=True,
        transport_security=TransportSecuritySettings(
            allowed_hosts=_allowed_hosts(),
            allowed_origins=["https://chat.openai.com", "https://chatgpt.com", "https://platform.openai.com"],
        ),
    )
    app.mount("/mcp", mcp_app, name="supernet-agent-mcp")
    app.state.supernet_agent_mcp = mcp

    @app.get("/supernet/agent/capabilities")
    async def supernet_agent_capabilities() -> dict[str, Any]:
        return {
            "protocol": "MCP Streamable HTTP",
            "endpoint": "/mcp",
            "tool_only": True,
            "tools": ["supernet_observe", "supernet_offer", "supernet_relate", "supernet_refine", "supernet_return", "supernet_reopen", "supernet_collective"],
            "same_runtime": True,
            "published_semantic_carrier": "SUPERNET_CLOSURE_FORM",
            "translation_operator": TRANSLATE_OPERATOR,
            "runtime_identity": "TRANSLATIONAL_TRUTH_CLASS",
            "runtime_identity_is_translational_truth": True,
            "agent_interaction_is_supernet_translate": True,
            "self_runtime_is_closure_form_reading": True,
            "separate_agent_mutation_authority": False,
            "vision_slide_operator": VISION_SLIDE_OPERATOR,
            "background_autonomy_required": False,
            "admin_privilege": False,
            "truth_privilege": False,
            "source_preserving": True,
            "continuing_returned_only": True,
            "production_auth_applies": True,
            "canonical_pixel_layout": None,
        }

    return app


__all__ = ["AgentSheaf", "attach_supernet_agent_mcp"]
