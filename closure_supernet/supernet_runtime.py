from __future__ import annotations

from typing import Any

from .models import OccurrenceCreate
from .runtime import ClosureSupernetRuntime
from .supernet_integrator import SupernetIntegrator
from .supernet_models import IntegrationLens, ResourceEnvelope
from .supernet_store import SupernetIntegrationStore


_PATCHED = False


def install_unified_supernet_runtime() -> None:
    """Make continuous integration, rather than a subsystem, the runtime center."""

    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    original_init = ClosureSupernetRuntime.__init__
    original_ingest = ClosureSupernetRuntime.ingest
    original_cycle = ClosureSupernetRuntime.cycle
    original_status = ClosureSupernetRuntime.status
    original_black_mirror = ClosureSupernetRuntime.black_mirror
    original_living_field = ClosureSupernetRuntime.living_field
    original_close = ClosureSupernetRuntime.close

    def init(self: ClosureSupernetRuntime, config=None) -> None:
        original_init(self, config)
        self.supernet_store = SupernetIntegrationStore(
            self.config.database_path
        )

        async def raw_ingest(data: OccurrenceCreate) -> dict[str, Any]:
            return await original_ingest(self, data)

        self.supernet_integrator = SupernetIntegrator(
            self.config,
            self.store,
            self.translation_store,
            self.supernet_store,
            raw_ingest,
        )
        self.integrator = self.supernet_integrator
        bootstrap = self.supernet_integrator.reconcile()
        if bootstrap["total"] or self.supernet_store.current_stage() is None:
            self.supernet_integrator.commit_stage(
                trigger="runtime-bootstrap"
            )

        projection_run = self.projection.run

        def combined_projection_run() -> dict[str, Any]:
            projection = projection_run()
            field = self.supernet_integrator.projection()
            projection["unified_supernet"] = {
                "stats": field["stats"],
                "current_stage": field["current_stage"],
                "lens_counts": field["lens_counts"],
                "source_reverse_index": field[
                    "source_reverse_index"
                ],
                "canonical_runtime_operation": "integrate",
                "subsystems_are_lenses": True,
                "canonical_language": None,
                "truth_issued_by_determination": False,
            }
            self.store.set_state("black_mirror_projection", projection)
            return projection

        self.projection.run = combined_projection_run

        living_projection = self.living.field_projection

        def combined_living_projection(
            black_mirror: dict[str, Any]
        ) -> dict[str, Any]:
            projection = living_projection(black_mirror)
            field = self.supernet_integrator.projection()
            projection["unified_supernet"] = field
            projection.setdefault("stats", {}).update(
                {
                    "supernet_integration_events": field["stats"][
                        "events"
                    ],
                    "supernet_field_stages": field["stats"]["stages"],
                    "supernet_open_events": field["stats"][
                        "open_events"
                    ],
                    "supernet_determined_events": field["stats"][
                        "determined_events"
                    ],
                    "supernet_returned_events": field["stats"][
                        "returned_events"
                    ],
                    "canonical_runtime_operation": "integrate",
                    "subsystems_are_lenses": True,
                }
            )
            projection.setdefault("source_reverse_index", {}).update(
                field["source_reverse_index"]
            )
            return projection

        self.living.field_projection = combined_living_projection

    async def ingest(
        self: ClosureSupernetRuntime, data: OccurrenceCreate
    ) -> dict[str, Any]:
        if not hasattr(self, "supernet_integrator"):
            return await original_ingest(self, data)
        metadata = dict(data.metadata)
        envelope = ResourceEnvelope(
            exact_text=data.exact_text,
            authored_by=str(
                metadata.get("authored_by")
                or metadata.get("created_by")
                or metadata.get("author_id")
                or data.source_id
            ),
            form_label=str(
                metadata.get("form_label")
                or metadata.get("resource_form_label")
                or metadata.get("living_form")
                or data.source_id
                or "source"
            ),
            language_label=metadata.get("language_label"),
            source_id=data.source_id,
            source_location=data.source_location,
            source_context=data.source_context,
            perspective_id=metadata.get("perspective_id"),
            problem_id=metadata.get("problem_id"),
            action_id=metadata.get("action_id"),
            visibility=str(metadata.get("visibility") or "PUBLIC"),
            capabilities=list(metadata.get("capabilities") or []),
            constraints=list(metadata.get("constraints") or []),
            relation_hints=list(metadata.get("relation_hints") or []),
            causal_predecessor_ids=list(
                metadata.get("causal_predecessor_ids") or []
            ),
            parent_event_ids=list(
                metadata.get("parent_event_ids") or []
            ),
            affected_perspectives=list(
                metadata.get("affected_perspectives") or []
            ),
            evidence_status=data.evidence_status,
            adapter_label=metadata.get("adapter_label"),
            external_key=metadata.get("supernet_external_key"),
            metadata=metadata,
        )
        receipt = await self.supernet_integrator.integrate(envelope)
        occurrence = receipt.get("occurrence")
        if occurrence is None:
            occurrence_id = receipt["occurrence_ids"][0]
            occurrence = self.store.get_occurrence(occurrence_id)
        occurrence["supernet_integration_event_id"] = receipt["event_id"]
        occurrence["supernet_field_stage_id"] = receipt[
            "field_stage_id"
        ]
        return occurrence

    async def integrate_resource(
        self: ClosureSupernetRuntime, envelope: ResourceEnvelope
    ) -> dict[str, Any]:
        return await self.supernet_integrator.integrate(envelope)

    async def interact_with_event(
        self: ClosureSupernetRuntime,
        event_id: str,
        envelope: ResourceEnvelope,
    ) -> dict[str, Any]:
        self.supernet_store.get_event(event_id)
        updated = envelope.model_copy(
            update={
                "parent_event_ids": list(
                    dict.fromkeys(
                        [*envelope.parent_event_ids, event_id]
                    )
                )
            }
        )
        return await self.supernet_integrator.integrate(updated)

    async def cycle(self: ClosureSupernetRuntime):
        pre = self.supernet_integrator.reconcile()
        result = await original_cycle(self)
        post = self.supernet_integrator.reconcile()
        stage = self.supernet_integrator.commit_stage(
            trigger=f"runtime-cycle:{result.cycle_id}"
        )
        field = self.supernet_integrator.projection()
        black_mirror = self.projection.run()
        living = self.living_store.get_state(
            "living_field_projection"
        )
        if living is None:
            living = self.living.field_projection(black_mirror)
        living["unified_supernet"] = field
        living.setdefault("stats", {}).update(
            {
                "supernet_integration_events": field["stats"]["events"],
                "supernet_field_stages": field["stats"]["stages"],
                "canonical_runtime_operation": "integrate",
                "subsystems_are_lenses": True,
            }
        )
        living.setdefault("source_reverse_index", {}).update(
            field["source_reverse_index"]
        )
        self.living_store.set_state(
            "living_field_projection", living
        )
        cycle_summary = {
            "cycle_id": result.cycle_id,
            "pre_reconciled": pre,
            "post_reconciled": post,
            "field_stage": stage,
            "field_stats": field["stats"],
            "canonical_runtime_operation": "integrate",
        }
        self.supernet_store.set_state("last_cycle", cycle_summary)
        self.store.set_state("supernet_last_cycle", cycle_summary)
        return result

    def status(self: ClosureSupernetRuntime):
        base_status = original_status(self)
        base = base_status.model_dump(mode="python")
        last_cycle = dict(base.get("last_cycle") or {})
        last_cycle["unified_supernet"] = (
            self.supernet_store.get_state_value("last_cycle", {})
        )
        base["last_cycle"] = last_cycle
        return type(base_status)(**base)

    def supernet_field(
        self: ClosureSupernetRuntime,
        lens: IntegrationLens | str = IntegrationLens.ALL,
    ) -> dict[str, Any]:
        return self.supernet_integrator.projection(lens)

    def black_mirror(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_black_mirror(self)
        if "unified_supernet" not in projection:
            field = self.supernet_field()
            projection["unified_supernet"] = {
                "stats": field["stats"],
                "current_stage": field["current_stage"],
                "lens_counts": field["lens_counts"],
                "source_reverse_index": field[
                    "source_reverse_index"
                ],
                "canonical_runtime_operation": "integrate",
                "subsystems_are_lenses": True,
            }
        return projection

    def living_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_living_field(self)
        if "unified_supernet" not in projection:
            field = self.supernet_field()
            projection["unified_supernet"] = field
            projection.setdefault("source_reverse_index", {}).update(
                field["source_reverse_index"]
            )
        return projection

    def close(self: ClosureSupernetRuntime) -> None:
        if hasattr(self, "supernet_store"):
            self.supernet_store.close()
        original_close(self)

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.ingest = ingest
    ClosureSupernetRuntime.integrate_resource = integrate_resource
    ClosureSupernetRuntime.interact_with_event = interact_with_event
    ClosureSupernetRuntime.cycle = cycle
    ClosureSupernetRuntime.status = status
    ClosureSupernetRuntime.supernet_field = supernet_field
    ClosureSupernetRuntime.black_mirror = black_mirror
    ClosureSupernetRuntime.living_field = living_field
    ClosureSupernetRuntime.close = close


install_unified_supernet_runtime()
