from __future__ import annotations

"""Agent participation as a projection of the one Supernet closure transition.

The MCP transport is only another perspective on the published closure form.
Every mutation is wrapped by the same ``SUPERNET_TRANSLATE`` receipt family used
by the browser/runtime boundary. Self-observation is a read of that same closure
form and cannot author truth.
"""

import os
from contextlib import asynccontextmanager
from typing import Annotated, Any, Awaitable, Callable, Literal, Mapping

from fastapi import FastAPI
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from pydantic import Field

from . import full_supernet_potential_gate as _digest_base
from .embodied_models import SheafKind
from .nrrf892_runtime_bridge import VISION_SLIDE_OPERATOR
from .selection_models import SelectionReadingCreate
from .supernet_closure_form import (
    TRANSLATE_OPERATOR,
    TRANSLATE_RECEIPT_SCHEMA,
    derive_full_supernet_gate_contract,
)
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


def _provenance(runtime: Any) -> dict[str, str]:
    result: dict[str, str] = {}
    ledger = getattr(runtime, "ledger", None)
    if ledger is None:
        return result
    for item in ledger.list_returns():
        event_id = str(item.get("id") or "")
        perspective_id = str(item.get("perspective_id") or "")
        if event_id and perspective_id:
            result[event_id] = perspective_id
    return result


def _closure_gate(
    runtime: Any,
    perspective_id: str | None,
    focus_event_id: str | None,
) -> dict[str, Any]:
    perspective = perspective_id or "runtime:self"
    closure_contract = runtime.project(
        perspective_id=perspective,
        focus_event_id=focus_event_id,
    )
    return derive_full_supernet_gate_contract(
        closure_contract,
        source_perspective_by_event=_provenance(runtime),
    )


def _self_runtime_reading(
    runtime: Any,
    perspective_id: str | None,
    focus_event_id: str | None,
) -> dict[str, Any]:
    gate = _closure_gate(runtime, perspective_id, focus_event_id)
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


def _agent_translation_receipt(
    source_gate: Mapping[str, Any],
    target_gate: Mapping[str, Any],
    *,
    interaction_kind: str,
    actor_id: str,
    focus_event_id: str | None,
) -> dict[str, Any]:
    source_form = source_gate["supernet_closure_form"]
    target_form = target_gate["supernet_closure_form"]
    source_identity = source_form["runtime_identity_id"]
    target_identity = target_form["runtime_identity_id"]
    preserved = source_identity == target_identity
    body = {
        "schema": TRANSLATE_RECEIPT_SCHEMA,
        "operator": TRANSLATE_OPERATOR,
        "relation_id": f"agent:{interaction_kind}:{focus_event_id or 'continuing'}",
        "agent_interaction_kind": interaction_kind,
        "agent_actor_id": actor_id,
        "source_gate_id": source_gate["id"],
        "source_closure_form_id": source_form["id"],
        "source_runtime_identity_id": source_identity,
        "target_gate_id": target_gate["id"],
        "target_closure_form_id": target_form["id"],
        "target_runtime_identity_id": target_identity,
        "runtime_identity_is_translational_truth": True,
        "runtime_identity_preserved": preserved,
        "translational_truth_preserved": preserved,
        "truth_refined": not preserved,
        "runtime_state_change_is_this_translation": True,
        "agent_interaction_is_this_translation": True,
        "browser_and_agent_share_translation_operator": True,
        "semantic_transition_is_visual_transition": True,
        "separate_agent_mutation_authority": False,
        "self_runtime_is_closure_form_reading": True,
        "vision_slide_operator": VISION_SLIDE_OPERATOR,
    }
    body["id"] = _digest_base._digest("supernet-translate", body)
    return body


async def _close_agent_mutation(
    runtime: Any,
    *,
    perspective_id: str,
    source_focus_event_id: str | None,
    interaction_kind: str,
    actor_id: str,
    mutation: Callable[[], Awaitable[tuple[dict[str, Any], str | None]]],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    source_gate = _closure_gate(runtime, perspective_id, source_focus_event_id)
    result, target_focus_event_id = await mutation()
    target_gate = _closure_gate(runtime, perspective_id, target_focus_event_id)
    receipt = _agent_translation_receipt(
        source_gate,
        target_gate,
        interaction_kind=interaction_kind,
        actor_id=actor_id,
        focus_event_id=target_focus_event_id,
    )
    return result, receipt, _self_runtime_reading(
        runtime, perspective_id, target_focus_event_id
    )


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
        "two_person_E2E": "CONTINUING",
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
    if getattr(app.state, "supernet_agent_mcp_attached", False):
        return app

    runtime = app.state.runtime
    app.state.supernet_agent_mcp_attached = True
    mcp = MCPServer("Closure Supernet Agent")

    @mcp.tool(
        title="Observe Supernet",
        annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False),
    )
    async def supernet_observe(
        event_id: str | None = None,
        perspective_id: str | None = None,
        limit: Annotated[int, Field(ge=1, le=50)] = 12,
    ) -> dict[str, Any]:
        perspective = perspective_id or "runtime:self"
        field = runtime.supernet_field()
        events = list(field.get("events", []))[-limit:]
        if event_id is None and events:
            event_id = events[-1]["id"]
        return {
            "field_stage": field.get("current_stage"),
            "stats": field.get("stats", {}),
            "recent_events": events,
            "interface": await _compact_interface(runtime, event_id, perspective),
            "self_runtime": _self_runtime_reading(runtime, perspective, event_id),
            "subsystems_are_lenses": True,
            "self_observation_authors_truth": False,
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
        exact_text: Annotated[str, Field(min_length=1)],
        actor_id: str = "openai-agent",
        perspective_id: str | None = None,
        form_label: str = "agent interaction",
        parent_event_id: str | None = None,
        sheaf: AgentSheaf | None = None,
    ) -> dict[str, Any]:
        perspective = perspective_id or actor_id
        metadata: dict[str, Any] = {
            "agent_mcp": True,
            "agent_role": "participant",
            "translation_operator": TRANSLATE_OPERATOR,
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
                    "hypothesis_status": "CONTINUING"
                    if sheaf_value == "UNKNOWN_UAP_HYPOTHESIS"
                    else None,
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

        async def mutation() -> tuple[dict[str, Any], str | None]:
            result = (
                await runtime.live_sense.interact(parent_event_id, envelope)
                if parent_event_id
                else await runtime.live_sense.offer(envelope)
            )
            return result, result["event_id"]

        result, translation, self_runtime = await _close_agent_mutation(
            runtime,
            perspective_id=perspective,
            source_focus_event_id=parent_event_id,
            interaction_kind="OFFER",
            actor_id=actor_id,
            mutation=mutation,
        )
        event_id = result["event_id"]
        return {
            "event_id": event_id,
            "occurrence_ids": result.get("occurrence_ids", []),
            "sense_receipt": result.get("sense_receipt"),
            "translation": translation,
            "self_runtime": self_runtime,
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
        perspective = perspective_id or actor_id

        async def mutation() -> tuple[dict[str, Any], str | None]:
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
            result["sense_receipt"] = await runtime.live_sense.sense_event(event_id)
            return result, event_id

        result, translation, self_runtime = await _close_agent_mutation(
            runtime,
            perspective_id=perspective,
            source_focus_event_id=source_event_id,
            interaction_kind="RELATE",
            actor_id=actor_id,
            mutation=mutation,
        )
        event_id = result["relation_event"]["id"]
        return {
            "relation_event_id": event_id,
            "relation_event": result["relation_event"],
            "sense_receipt": result["sense_receipt"],
            "translation": translation,
            "self_runtime": self_runtime,
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
        perspective = perspective_id or actor_id
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

        async def mutation() -> tuple[dict[str, Any], str | None]:
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
            return {"selection": reading}, source_event_id

        result, translation, self_runtime = await _close_agent_mutation(
            runtime,
            perspective_id=perspective,
            source_focus_event_id=source_event_id,
            interaction_kind="REFINE",
            actor_id=actor_id,
            mutation=mutation,
        )
        return {
            **result,
            "translation": translation,
            "self_runtime": self_runtime,
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
        perspective = perspective_id or actor_id

        async def mutation() -> tuple[dict[str, Any], str | None]:
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
            result["sense_receipt"] = await runtime.live_sense.sense_event(returned_id)
            return result, returned_id

        result, translation, self_runtime = await _close_agent_mutation(
            runtime,
            perspective_id=perspective,
            source_focus_event_id=event_id,
            interaction_kind="RETURN",
            actor_id=actor_id,
            mutation=mutation,
        )
        returned_id = result["returned_event"]["id"]
        return {
            "source_event_id": event_id,
            "returned_event_id": returned_id,
            "source_transition": result["source_transition"],
            "sense_receipt": result["sense_receipt"],
            "translation": translation,
            "self_runtime": self_runtime,
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
        perspective = perspective_id or actor_id

        async def mutation() -> tuple[dict[str, Any], str | None]:
            transition = runtime.topology.reopen(
                event_id,
                EventReopenCreate(
                    actor_id=actor_id,
                    reason=reason,
                    reopened_sites=reopened_sites or [],
                    successor_hints=successor_hints or [],
                    metadata={
                        "agent_mcp": True,
                        "perspective_id": perspective,
                        "truth_issued": False,
                    },
                ),
            )
            sense = await runtime.live_sense.sense_event(event_id)
            return {"transition": transition, "sense_receipt": sense}, event_id

        result, translation, self_runtime = await _close_agent_mutation(
            runtime,
            perspective_id=perspective,
            source_focus_event_id=event_id,
            interaction_kind="REOPEN",
            actor_id=actor_id,
            mutation=mutation,
        )
        return {
            "event_id": event_id,
            **result,
            "translation": translation,
            "self_runtime": self_runtime,
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
        ids = _unique(event_ids)
        if len(ids) < 2:
            raise ValueError("A collective continuation requires at least two distinct events")
        perspective = perspective_id or actor_id

        async def mutation() -> tuple[dict[str, Any], str | None]:
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
            result["sense_receipt"] = await runtime.live_sense.sense_event(event_id)
            return result, event_id

        result, translation, self_runtime = await _close_agent_mutation(
            runtime,
            perspective_id=perspective,
            source_focus_event_id=ids[0],
            interaction_kind="COLLECTIVE",
            actor_id=actor_id,
            mutation=mutation,
        )
        event_id = result["collective_event"]["id"]
        return {
            "collective_event_id": event_id,
            "sense_receipt": result["sense_receipt"],
            "translation": translation,
            "self_runtime": self_runtime,
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
