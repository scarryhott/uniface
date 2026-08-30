from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Annotated, Any, Literal

from fastapi import FastAPI
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from pydantic import Field

from .embodied_models import SheafKind
from .selection_models import SelectionReadingCreate
from .supernet_models import ResourceEnvelope
from .topology_models import (
    CollectiveTraceCreate,
    EventRelationCreate,
    EventReopenCreate,
    EventReturnCreate,
)

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


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in values if str(item)))


async def _compact_interface(
    runtime: Any,
    event_id: str | None,
    perspective_id: str | None,
) -> dict[str, Any]:
    receipt = runtime.natural_interface.select(
        focus_event_id=event_id,
        perspective_id=perspective_id,
    )
    focused = receipt.get("focus_event") or {}
    return {
        "focus_event_id": receipt.get("focus_event_id") or focused.get("id") or event_id,
        "perspective_id": perspective_id,
        "natural_chart": receipt.get("natural_chart"),
        "sense_depth": receipt.get("sense_depth"),
        "closure_level": receipt.get("closure_level"),
        "visual_closure": receipt.get("visual_closure"),
        "proof_depth": receipt.get("proof_depth"),
        "continuation_depth": receipt.get("continuation_depth"),
        "turing_being_depth": receipt.get("turing_being_depth"),
        "source_fibre": receipt.get("source_fibre", []),
        "two_person_E2E": "OPEN",
        "truth_issued": False,
    }


def _allowed_hosts(config: Any) -> list[str]:
    hosts = {
        "localhost",
        "localhost:*",
        "127.0.0.1",
        "127.0.0.1:*",
        "uniface-supernet-production.up.railway.app",
        "uniface-supernet-production.up.railway.app:*",
    }
    for raw in list(getattr(config, "trusted_hosts", ())) + [
        os.getenv("RAILWAY_PUBLIC_DOMAIN", ""),
    ]:
        host = str(raw).strip()
        if not host or "*" in host or "://" in host:
            continue
        hosts.add(host)
        if ":" not in host:
            hosts.add(f"{host}:*")
    return sorted(hosts)


def _allowed_origins(config: Any) -> list[str]:
    origins = {
        "https://chatgpt.com",
        "https://chat.openai.com",
        "https://platform.openai.com",
        *[str(item) for item in getattr(config, "cors_origins", ()) if str(item)],
    }
    return sorted(origins)


def attach_supernet_agent_mcp(app: FastAPI) -> FastAPI:
    """Mount one authenticated MCP tool surface over the completed Supernet runtime.

    The MCP server is not another semantic runtime. Every mutating tool calls the
    same live Sense/topology/selection operations used by the public Black Mirror.
    """

    if getattr(app.state, "supernet_agent_mcp_attached", False):
        return app

    runtime = app.state.runtime
    app.state.supernet_agent_mcp_attached = True
    app.description += (
        "; a tool-only Streamable HTTP MCP surface lets external ChatGPT/Codex-style "
        "agents observe and participate in the same Supernet field. Agent calls have "
        "no admin or truth privilege and preserve OPEN, source, proof and return semantics"
    )

    mcp = MCPServer("Closure Supernet Agent")

    @mcp.tool(
        title="Observe Supernet",
        annotations=ToolAnnotations(
            read_only_hint=True,
            open_world_hint=False,
        ),
    )
    async def supernet_observe(
        event_id: str | None = None,
        perspective_id: str | None = None,
        limit: Annotated[int, Field(ge=1, le=50)] = 12,
    ) -> dict[str, Any]:
        """Use this when the agent needs the current field, recent events, or one event's Black Mirror context without changing Supernet."""

        field = runtime.supernet_field()
        events = list(field.get("events", []))[-limit:]
        if event_id is None and events:
            event_id = events[-1]["id"]
        return {
            "field_stage": field.get("current_stage"),
            "stats": field.get("stats", {}),
            "recent_events": events,
            "interface": await _compact_interface(runtime, event_id, perspective_id),
            "subsystems_are_lenses": True,
            "canonical_language": None,
            "truth_issued": False,
        }

    @mcp.tool(
        title="Offer or interact in Supernet",
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def supernet_offer(
        exact_text: Annotated[str, Field(min_length=1, description="Exact source text to preserve before Sense.")],
        actor_id: str = "openai-agent",
        perspective_id: str | None = None,
        form_label: str = "agent interaction",
        parent_event_id: str | None = None,
        sheaf: AgentSheaf | None = None,
    ) -> dict[str, Any]:
        """Use this when the agent should add a new exact source or interact with a focused event; the interaction immediately runs the existing Sense/interpretation/admission/selection pipeline."""

        perspective = perspective_id or actor_id
        metadata: dict[str, Any] = {
            "agent_mcp": True,
            "agent_role": "participant",
            "truth_issued": False,
        }
        hints = ["agent interaction"]
        adapter_label = "agent"
        if sheaf is not None:
            sheaf_value = SheafKind(sheaf).value
            adapter_label = "embodied"
            metadata.update(
                {
                    "sheaf": sheaf_value,
                    "eight_sheaf_supernet": True,
                    "hypothesis_status": "OPEN" if sheaf_value == "UNKNOWN_UAP_HYPOTHESIS" else None,
                    "alien_claim_verified": False,
                    "anomaly_is_not_explanation": True,
                }
            )
            hints.extend(["eight sheaf", sheaf_value])
        envelope = ResourceEnvelope(
            exact_text=exact_text,
            authored_by=actor_id,
            form_label=form_label,
            perspective_id=perspective,
            affected_perspectives=[perspective],
            relation_hints=_unique(hints),
            parent_event_ids=[parent_event_id] if parent_event_id else [],
            causal_predecessor_ids=[parent_event_id] if parent_event_id else [],
            adapter_label=adapter_label,
            metadata=metadata,
        )
        result = (
            await runtime.live_sense.interact(parent_event_id, envelope)
            if parent_event_id
            else await runtime.live_sense.offer(envelope)
        )
        event_id = result["event_id"]
        return {
            "event_id": event_id,
            "occurrence_ids": result.get("occurrence_ids", []),
            "sense_receipt": result.get("sense_receipt"),
            "interface": await _compact_interface(runtime, event_id, perspective),
            "truth_issued": False,
        }

    @mcp.tool(
        title="Relate Supernet events",
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def supernet_relate(
        source_event_id: str,
        target_event_id: str,
        relation_label: str,
        actor_id: str = "openai-agent",
        perspective_id: str | None = None,
        bidirectional: bool = False,
    ) -> dict[str, Any]:
        """Use this when the agent should propose an explicit directed or reciprocal relation between two existing Supernet events; geometry never substitutes for direction."""

        perspective = perspective_id or actor_id
        result = await runtime.topology.create_relation(
            EventRelationCreate(
                source_event_id=source_event_id,
                target_event_id=target_event_id,
                authored_by=actor_id,
                relation_label=relation_label,
                affected_perspectives=[perspective],
                bidirectional=bidirectional,
                preserves=["exact sources", "direction", "source provenance"],
                metadata={"agent_mcp": True, "truth_issued": False},
            )
        )
        event_id = result["relation_event"]["id"]
        sense = await runtime.live_sense.sense_event(event_id)
        return {
            "relation_event_id": event_id,
            "relation_event": result["relation_event"],
            "sense_receipt": sense,
            "interface": await _compact_interface(runtime, event_id, perspective),
            "truth_issued": False,
        }

    @mcp.tool(
        title="Refine a live relation",
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def supernet_refine(
        source_event_id: str,
        selected_relation_id: str,
        actor_id: str = "openai-agent",
        perspective_id: str | None = None,
        reason: str = "Agent refines the live relational field",
    ) -> dict[str, Any]:
        """Use this when the agent intentionally selects one currently admissible Sense relation. If alternatives remain, Supernet records forced isolation rather than natural selection."""

        matches = [
            reading
            for reading in runtime.selection_store.list_readings()
            if reading.get("source_event_id") == source_event_id
            and reading.get("metadata", {}).get("live_sense") is True
        ]
        if not matches:
            raise ValueError("The focused event has no live Sense relation field")
        source = max(matches, key=lambda item: item["created_at"])
        if selected_relation_id not in source["admissible_symbols"]:
            raise ValueError("The selected relation is not admitted by the source reading")
        perspective = perspective_id or actor_id
        reading = await runtime.selection.create_reading(
            SelectionReadingCreate(
                name="MCP agent relational refinement",
                authored_by=actor_id,
                field_symbols=source["field_symbols"],
                admissible_symbols=source["admissible_symbols"],
                selected_symbol=selected_relation_id,
                source_event_id=source_event_id,
                selection_scope="agent MCP relation refinement",
                perspective_id=perspective,
                source_ids=source.get("source_ids", []),
                metadata={
                    "agent_mcp": True,
                    "parent_live_sense_reading_id": source["id"],
                    "reason": reason,
                    "removed_alternatives_retained": True,
                    "truth_issued": False,
                },
            )
        )
        return {
            "selection": reading,
            "interface": await _compact_interface(runtime, source_event_id, perspective),
            "truth_issued": False,
        }

    @mcp.tool(
        title="Return a Supernet form",
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def supernet_return(
        event_id: str,
        exact_text: Annotated[str, Field(min_length=1)],
        actor_id: str = "openai-agent",
        perspective_id: str | None = None,
        form_label: str = "agent return",
    ) -> dict[str, Any]:
        """Use this when the agent should return a result or consequence into the focused lineage; the returned child is immediately re-sensed and remains nonterminal."""

        perspective = perspective_id or actor_id
        result = await runtime.topology.return_event(
            event_id,
            EventReturnCreate(
                actor_id=actor_id,
                exact_text=exact_text,
                form_label=form_label,
                affected_perspectives=[perspective],
                metadata={"agent_mcp": True, "truth_issued": False},
            ),
        )
        returned_id = result["returned_event"]["id"]
        sense = await runtime.live_sense.sense_event(returned_id)
        return {
            "source_event_id": event_id,
            "returned_event_id": returned_id,
            "source_transition": result["source_transition"],
            "sense_receipt": sense,
            "interface": await _compact_interface(runtime, returned_id, perspective),
            "truth_issued": False,
        }

    @mcp.tool(
        title="Reopen a Supernet event",
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def supernet_reopen(
        event_id: str,
        reason: Annotated[str, Field(min_length=1)],
        actor_id: str = "openai-agent",
        perspective_id: str | None = None,
        reopened_sites: list[str] | None = None,
        successor_hints: list[str] | None = None,
    ) -> dict[str, Any]:
        """Use this when a prior return or determination should become open successor potential again without erasing its history."""

        perspective = perspective_id or actor_id
        transition = runtime.topology.reopen(
            event_id,
            EventReopenCreate(
                actor_id=actor_id,
                reason=reason,
                reopened_sites=reopened_sites or [],
                successor_hints=successor_hints or [],
                metadata={"agent_mcp": True, "perspective_id": perspective, "truth_issued": False},
            ),
        )
        sense = await runtime.live_sense.sense_event(event_id)
        return {
            "event_id": event_id,
            "transition": transition,
            "sense_receipt": sense,
            "interface": await _compact_interface(runtime, event_id, perspective),
            "truth_issued": False,
        }

    @mcp.tool(
        title="Create a collective continuation",
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def supernet_collective(
        event_ids: Annotated[list[str], Field(min_length=2)],
        exact_text: Annotated[str, Field(min_length=1)],
        actor_id: str = "openai-agent",
        perspective_id: str | None = None,
    ) -> dict[str, Any]:
        """Use this when the agent should join two or more existing trajectories into one new shared-architecture occurrence while preserving every source lineage."""

        ids = _unique(event_ids)
        if len(ids) < 2:
            raise ValueError("A collective continuation requires at least two distinct events")
        perspective = perspective_id or actor_id
        result = await runtime.topology.create_collective_trace(
            CollectiveTraceCreate(
                authored_by=actor_id,
                event_ids=ids,
                exact_text=exact_text,
                affected_perspectives=[perspective],
                relation_hints=["shared architecture", "collective interaction", "agent MCP"],
                metadata={"agent_mcp": True, "perspective_id": perspective, "truth_issued": False},
            )
        )
        event_id = result["collective_event"]["id"]
        sense = await runtime.live_sense.sense_event(event_id)
        return {
            "collective_event_id": event_id,
            "sense_receipt": sense,
            "interface": await _compact_interface(runtime, event_id, perspective),
            "truth_issued": False,
        }

    security = TransportSecuritySettings(
        allowed_hosts=_allowed_hosts(runtime.config),
        allowed_origins=_allowed_origins(runtime.config),
    )
    mcp_app = mcp.streamable_http_app(
        streamable_http_path="/",
        stateless_http=True,
        json_response=True,
        transport_security=security,
    )
    app.mount("/mcp", mcp_app, name="supernet-agent-mcp")

    original_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def combined_lifespan(host_app: FastAPI):
        async with original_lifespan(host_app):
            async with mcp.session_manager.run():
                yield

    app.router.lifespan_context = combined_lifespan
    app.state.supernet_agent_mcp = mcp

    @app.get("/supernet/agent/capabilities")
    async def supernet_agent_capabilities() -> dict[str, Any]:
        return {
            "protocol": "MCP Streamable HTTP",
            "endpoint": "/mcp",
            "tool_only": True,
            "tools": [
                "supernet_observe",
                "supernet_offer",
                "supernet_relate",
                "supernet_refine",
                "supernet_return",
                "supernet_reopen",
                "supernet_collective",
            ],
            "same_runtime": True,
            "background_autonomy_required": False,
            "admin_privilege": False,
            "truth_privilege": False,
            "source_preserving": True,
            "open_reopenable": True,
            "production_auth_applies": True,
            "canonical_pixel_layout": None,
        }

    return app
