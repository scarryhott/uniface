from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from . import api_proof_completion as base_api
from .complete_interface_models import (
    CompleteInterfaceCollective,
    CompleteInterfaceOffer,
    CompleteInterfaceSelection,
)
from .complete_interface_web import COMPLETE_NATURAL_SUPERNET_HTML
from .config import RuntimeConfig
from .natural_interface_models import NaturalInterfaceAdmissionCreate
from .selection_models import SelectionReadingCreate
from .supernet_models import IntegrationLens, ResourceEnvelope
from .topology_models import CollectiveTraceCreate


def attach_natural_interface_routes(app: FastAPI) -> FastAPI:
    if getattr(app.state, "natural_interface_routes_attached", False):
        return app
    runtime = app.state.runtime
    app.state.natural_interface_routes_attached = True
    app.version = "3.6.0"
    app.description += (
        "; the public Black Mirror is the complete operational surface of the one "
        "Supernet field: exact source → interaction-time Sense → interpretation/admission "
        "→ TranslationField → NRRF790 selection/OPEN branching → source-reversible chart "
        "→ direct relation, refinement, return, reopening or collective continuation. "
        "Perspective and eight-sheaf placement are carried on the same canonical event; "
        "no subsystem page is required for core interaction, no background autonomy is "
        "required, and presentation never manufactures truth."
    )

    async def _complete_page() -> str:
        return COMPLETE_NATURAL_SUPERNET_HTML

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def completed_root() -> str:
        return await _complete_page()

    app.router.routes.insert(0, app.router.routes.pop())

    @app.get("/supernet", response_class=HTMLResponse, include_in_schema=False)
    async def completed_supernet_page() -> str:
        return await _complete_page()

    app.router.routes.insert(0, app.router.routes.pop())

    @app.get(
        "/natural-interface",
        response_class=HTMLResponse,
        include_in_schema=False,
    )
    async def natural_interface_page() -> str:
        return await _complete_page()

    app.router.routes.insert(0, app.router.routes.pop())

    @app.get("/supernet/interface/capabilities")
    async def natural_interface_capabilities() -> dict[str, Any]:
        return {
            **runtime.natural_interface.capabilities(),
            "live_sense": runtime.live_sense.capabilities(),
            "single_complete_operational_surface": True,
            "perspective_carried_by_primary_composer": True,
            "eight_sheaf_entry_on_primary_surface": True,
            "direct_relation_on_primary_surface": True,
            "direct_selection_or_rigidification_on_primary_surface": True,
            "direct_turing_return_on_primary_surface": True,
            "direct_collective_trace_on_primary_surface": True,
            "core_action_requires_subsystem_page": False,
            "canonical_pixel_layout_selected": False,
            "truth_issued_by_presentation": False,
        }

    @app.get("/supernet/interface")
    async def natural_interface_receipt(
        focus_event_id: str | None = None,
        perspective_id: str | None = None,
    ) -> dict[str, Any]:
        try:
            return runtime.natural_interface.select(
                focus_event_id=focus_event_id,
                perspective_id=perspective_id,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/interface/admissions")
    async def admit_natural_interface(
        data: NaturalInterfaceAdmissionCreate,
    ) -> dict[str, Any]:
        try:
            return await runtime.natural_interface.admit(data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/sense")
    async def sensed_offer(data: ResourceEnvelope) -> dict[str, Any]:
        try:
            return await runtime.live_sense.offer(data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/events/{event_id}/sense-interact")
    async def sensed_interaction(
        event_id: str, data: ResourceEnvelope
    ) -> dict[str, Any]:
        try:
            return await runtime.live_sense.interact(event_id, data)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/events/{event_id}/sense")
    async def sense_existing_event(event_id: str) -> dict[str, Any]:
        try:
            return await runtime.live_sense.sense_event(event_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/interface/offer")
    async def complete_interface_offer(data: CompleteInterfaceOffer) -> dict[str, Any]:
        """Enter any ordinary live form through the one interaction-time Sense path.

        Eight-sheaf placement is metadata on the exact canonical occurrence rather
        than a second source object.  Specialized managers remain derived lenses.
        """

        try:
            adapter_label: str | None = None
            metadata = dict(data.metadata)
            relation_hints = list(data.relation_hints)
            if data.sheaf is not None:
                adapter_label = "embodied"
                metadata.update(
                    {
                        "sheaf": data.sheaf.value,
                        "eight_sheaf_supernet": True,
                        "hypothesis_status": (
                            "OPEN"
                            if data.sheaf.value == "UNKNOWN_UAP_HYPOTHESIS"
                            else None
                        ),
                        "alien_claim_verified": False,
                        "anomaly_is_not_explanation": True,
                    }
                )
                relation_hints.extend(["eight sheaf", data.sheaf.value])
            elif data.lens not in {None, "", "all", "source"}:
                try:
                    lens = IntegrationLens(data.lens)
                except ValueError as exc:
                    raise ValueError(f"Unknown Supernet lens: {data.lens}") from exc
                adapter_label = lens.value
                relation_hints.append(lens.value)

            envelope = ResourceEnvelope(
                exact_text=data.exact_text,
                authored_by=data.authored_by,
                form_label=data.form_label,
                perspective_id=data.perspective_id,
                affected_perspectives=data.affected_perspectives,
                relation_hints=list(dict.fromkeys(relation_hints)),
                adapter_label=adapter_label,
                parent_event_ids=(
                    [data.parent_event_id] if data.parent_event_id else []
                ),
                causal_predecessor_ids=(
                    [data.parent_event_id] if data.parent_event_id else []
                ),
                metadata={
                    **metadata,
                    "primary_black_mirror": True,
                    "exact_source_precedes_lens": True,
                    "truth_issued": False,
                },
            )
            if data.parent_event_id:
                result = await runtime.live_sense.interact(
                    data.parent_event_id, envelope
                )
            else:
                result = await runtime.live_sense.offer(envelope)
            return {
                **result,
                "focus_event_id": result["event_id"],
                "perspective_id": data.perspective_id,
                "sheaf": data.sheaf.value if data.sheaf else None,
                "lens": adapter_label or "source",
                "truth_issued": False,
            }
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/interface/selections")
    async def complete_interface_selection(
        data: CompleteInterfaceSelection,
    ) -> dict[str, Any]:
        """Refine the actual live relation field through the existing NRRF790 audit."""

        try:
            matches = [
                reading
                for reading in runtime.selection_store.list_readings()
                if reading.get("source_event_id") == data.source_event_id
                and reading.get("metadata", {}).get("live_sense") is True
            ]
            if not matches:
                raise ValueError("The focused event has no live Sense relation field")
            source = max(matches, key=lambda item: item["created_at"])
            if data.selected_relation_id not in source["admissible_symbols"]:
                raise ValueError("The selected relation is not admitted by the source reading")
            reading = await runtime.selection.create_reading(
                SelectionReadingCreate(
                    name="Black Mirror authored relational refinement",
                    authored_by=data.authored_by,
                    field_symbols=source["field_symbols"],
                    admissible_symbols=source["admissible_symbols"],
                    selected_symbol=data.selected_relation_id,
                    source_event_id=data.source_event_id,
                    selection_scope="live Black Mirror relation refinement",
                    perspective_id=data.perspective_id or data.authored_by,
                    source_ids=source.get("source_ids", []),
                    metadata={
                        **data.metadata,
                        "parent_live_sense_reading_id": source["id"],
                        "reason": data.reason,
                        "authored_refinement": True,
                        "removed_alternatives_retained": True,
                        "truth_issued": False,
                    },
                )
            )
            return reading
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/supernet/interface/collective")
    async def complete_interface_collective(
        data: CompleteInterfaceCollective,
    ) -> dict[str, Any]:
        try:
            result = await runtime.topology.create_collective_trace(
                CollectiveTraceCreate(
                    authored_by=data.authored_by,
                    event_ids=data.event_ids,
                    exact_text=data.exact_text,
                    affected_perspectives=data.affected_perspectives,
                    relation_hints=["shared architecture", "collective interaction"],
                    metadata={
                        **data.metadata,
                        "perspective_id": data.perspective_id,
                        "primary_black_mirror": True,
                    },
                )
            )
            event_id = result["collective_event"]["id"]
            sense = await runtime.live_sense.sense_event(event_id)
            return {
                **result,
                "sense_receipt": sense,
                "focus_event_id": event_id,
                "truth_issued": False,
            }
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Compatibility routes keep their URLs, but on the primary app they execute
    # interaction-time Sense rather than stopping after raw transport.
    @app.post("/supernet/integrate", include_in_schema=False)
    async def natural_surface_integrate(data: ResourceEnvelope) -> dict[str, Any]:
        return await sensed_offer(data)

    app.router.routes.insert(0, app.router.routes.pop())

    @app.post(
        "/supernet/events/{event_id}/interact",
        include_in_schema=False,
    )
    async def natural_surface_interact(
        event_id: str, data: ResourceEnvelope
    ) -> dict[str, Any]:
        return await sensed_interaction(event_id, data)

    app.router.routes.insert(0, app.router.routes.pop())

    return app


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_natural_interface_routes(base_api.create_app(config))


app = attach_natural_interface_routes(base_api.app)
