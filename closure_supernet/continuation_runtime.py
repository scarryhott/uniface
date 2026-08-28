from __future__ import annotations

from typing import Any

from .continuation import ContinuationManager
from .continuation_store import ContinuationStore
from .runtime import ClosureSupernetRuntime
from .supernet_integrator import SupernetIntegrator


_PATCHED = False


def install_continuation_runtime() -> None:
    """Attach NRRF807 after Turing Being without replacing completion or life."""

    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    original_infer_adapter = SupernetIntegrator._infer_adapter
    original_capabilities = SupernetIntegrator.capabilities

    def infer_adapter(form_label: str, metadata: dict[str, Any]) -> str:
        explicit = str(metadata.get("adapter_label") or "").lower()
        text = " ".join(
            [
                explicit,
                str(form_label),
                str(metadata.get("source_kind", "")),
                str(metadata.get("kind", "")),
                str(metadata.get("formal_reading", "")),
                " ".join(str(item) for item in metadata.get("formal_readings", [])),
            ]
        ).lower()
        if (
            explicit == "continuation"
            or "nrrf807" in text
            or "natural continuation" in text
            or "rulerel" in text
            or "geomrel" in text
            or "continuations meet" in text
        ):
            return "continuation"
        return original_infer_adapter(form_label, metadata)

    def capabilities(self: SupernetIntegrator) -> dict[str, Any]:
        base = original_capabilities(self)
        base.update(
            {
                "natural_continuation_available": True,
                "rule_is_directed_continuation_range": True,
                "geometry_is_generated_closure_equality": True,
                "rule_le_geometry": True,
                "geometry_eq_eqvgen_rule": True,
                "geometry_iff_continuations_meet": True,
                "rule_eq_geometry_iff_rule_symmetric": True,
                "finite_injective_rule_eq_geometry": True,
                "continuation_natural_under_translation_morphisms": True,
                "geometry_does_not_fabricate_rule_witness": True,
                "continuation_step_admissibility_derived_by_nrrf807": False,
                "determination_issues_truth": False,
            }
        )
        return base

    SupernetIntegrator._infer_adapter = staticmethod(infer_adapter)
    SupernetIntegrator.capabilities = capabilities

    original_init = ClosureSupernetRuntime.__init__
    original_cycle = ClosureSupernetRuntime.cycle
    original_status = ClosureSupernetRuntime.status
    original_black_mirror = ClosureSupernetRuntime.black_mirror
    original_living_field = ClosureSupernetRuntime.living_field
    original_close = ClosureSupernetRuntime.close

    def init(self: ClosureSupernetRuntime, config=None) -> None:
        original_init(self, config)
        self.continuation_store = ContinuationStore(self.config.database_path)
        self.continuation = ContinuationManager(self, self.continuation_store)
        projection_run = self.projection.run

        def combined_projection_run() -> dict[str, Any]:
            projection = projection_run()
            continuation = self.continuation.projection()
            projection["rule_geometry_continuation"] = {
                "stats": continuation["stats"],
                "source_reverse_index": continuation["source_reverse_index"],
                "formal_readings": ["NRRF799", "NRRF802", "NRRF805", "NRRF807"],
                "rule_and_geometry_are_lenses": True,
                "rule_direction_preserved": True,
                "geometry_does_not_fabricate_rule_witness": True,
                "truth_issued": False,
            }
            self.store.set_state("black_mirror_projection", projection)
            return projection

        self.projection.run = combined_projection_run

    async def cycle(self: ClosureSupernetRuntime):
        result = await original_cycle(self)
        projection = self.continuation.projection()
        stats = projection["stats"]
        black_mirror = self.projection.run()
        living = self.living_store.get_state("living_field_projection")
        if living is None:
            living = self.living.field_projection(black_mirror)
        living["rule_geometry_continuation"] = projection
        living.setdefault("stats", {}).update(
            {
                "continuation_systems": stats["systems"],
                "continuation_maps": stats["maps"],
                "rule_equals_geometry": stats["rule_equals_geometry"],
                "rule_strictly_inside_geometry": stats[
                    "rule_strictly_inside_geometry"
                ],
                "continuations_linked_turing_being": stats[
                    "linked_turing_being"
                ],
                "geometry_does_not_fabricate_rule_witness": True,
            }
        )
        living.setdefault("source_reverse_index", {}).update(
            projection["source_reverse_index"]
        )
        self.living_store.set_state("living_field_projection", living)
        payload = result.model_dump(mode="json")
        payload["continuation"] = stats
        self.store.set_state("last_cycle", payload)
        return result

    def status(self: ClosureSupernetRuntime):
        base_status = original_status(self)
        base = base_status.model_dump(mode="python")
        last_cycle = dict(base.get("last_cycle") or {})
        last_cycle["continuation"] = self.continuation_store.stats()
        base["last_cycle"] = last_cycle
        return type(base_status)(**base)

    def continuation_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = self.continuation_store.get_state(
            "continuation_field_projection"
        )
        return self.continuation.projection() if projection is None else projection

    def black_mirror(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_black_mirror(self)
        if "rule_geometry_continuation" not in projection:
            continuation = self.continuation_field()
            projection["rule_geometry_continuation"] = {
                "stats": continuation["stats"],
                "source_reverse_index": continuation["source_reverse_index"],
                "rule_and_geometry_are_lenses": True,
                "geometry_does_not_fabricate_rule_witness": True,
                "truth_issued": False,
            }
        return projection

    def living_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_living_field(self)
        if "rule_geometry_continuation" not in projection:
            continuation = self.continuation_field()
            projection["rule_geometry_continuation"] = continuation
            projection.setdefault("source_reverse_index", {}).update(
                continuation["source_reverse_index"]
            )
        return projection

    def close(self: ClosureSupernetRuntime) -> None:
        if hasattr(self, "continuation_store"):
            self.continuation_store.close()
        original_close(self)

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.cycle = cycle
    ClosureSupernetRuntime.status = status
    ClosureSupernetRuntime.continuation_field = continuation_field
    ClosureSupernetRuntime.black_mirror = black_mirror
    ClosureSupernetRuntime.living_field = living_field
    ClosureSupernetRuntime.close = close


install_continuation_runtime()
