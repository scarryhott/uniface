from __future__ import annotations

from typing import Any

from .embodied import EmbodiedSupernetManager
from .embodied_store import EmbodiedStore
from .runtime import ClosureSupernetRuntime
from .supernet_integrator import SupernetIntegrator


_PATCHED = False


def install_embodied_runtime() -> None:
    """Attach the embodied eight-sheaf field to the one continuous runtime."""

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
                str(metadata.get("sheaf", "")),
            ]
        ).lower()
        if (
            explicit == "embodied"
            or "eight sheaf" in text
            or "embodied" in text
            or "memetic love" in text
            or "local ball" in text
            or "global hair" in text
        ):
            return "embodied"
        return original_infer_adapter(form_label, metadata)

    def capabilities(self: SupernetIntegrator) -> dict[str, Any]:
        base = original_capabilities(self)
        base.update(
            {
                "embodied_eight_sheaf_supernet": True,
                "local_ball_is_human_interaction_network": True,
                "global_hair_is_open_potential": True,
                "memetic_love_is_reciprocal_translation": True,
                "syntropic_attractor_is_non_scalar": True,
                "resource_metrics_are_downstream": True,
                "unknown_hypotheses_remain_open": True,
                "physical_force_claimed": False,
                "emotion_inferred": False,
                "human_worth_scored": False,
                "single_sensor_complete": False,
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
        self.embodied_store = EmbodiedStore(self.config.database_path)
        self.embodied = EmbodiedSupernetManager(self, self.embodied_store)
        projection_run = self.projection.run

        def combined_projection_run() -> dict[str, Any]:
            projection = projection_run()
            embodied = self.embodied.projection()
            projection["embodied_eight_sheaf_supernet"] = {
                "stats": embodied["stats"],
                "source_reverse_index": embodied["source_reverse_index"],
                "local_ball_is_embodied_human_interaction": True,
                "global_hair_is_open_potential": True,
                "memetic_love_is_reciprocal_translation": True,
                "syntropic_attractor_is_non_scalar": True,
                "resource_metrics_are_downstream": True,
                "unknown_hypotheses_remain_open": True,
                "physical_force_claimed": False,
                "emotion_inferred": False,
                "human_worth_scored": False,
                "determination_issues_truth": False,
            }
            self.store.set_state("black_mirror_projection", projection)
            return projection

        self.projection.run = combined_projection_run

    async def cycle(self: ClosureSupernetRuntime):
        result = await original_cycle(self)
        projection = self.embodied.projection()
        stats = projection["stats"]
        black_mirror = self.projection.run()
        living = self.living_store.get_state("living_field_projection")
        if living is None:
            living = self.living.field_projection(black_mirror)
        living["embodied_eight_sheaf_supernet"] = projection
        living.setdefault("stats", {}).update(
            {
                "embodied_sections": stats["sections"],
                "embodied_sheaves_present": stats["sheaves_present"],
                "embodied_relations": stats["relations"],
                "love_admissible_relations": stats["love_admissible_relations"],
                "embodied_fields": stats["fields"],
                "all_eight_sheaf_fields": stats["all_eight_sheaf_fields"],
                "embodied_sensor_reads": stats["sensor_reads"],
                "resource_metrics_are_downstream": True,
                "unknown_hypotheses_remain_open": True,
            }
        )
        living.setdefault("source_reverse_index", {}).update(
            projection["source_reverse_index"]
        )
        self.living_store.set_state("living_field_projection", living)
        payload = result.model_dump(mode="json")
        payload["embodied"] = stats
        self.store.set_state("last_cycle", payload)
        return result

    def status(self: ClosureSupernetRuntime):
        base_status = original_status(self)
        base = base_status.model_dump(mode="python")
        last_cycle = dict(base.get("last_cycle") or {})
        last_cycle["embodied"] = self.embodied_store.stats()
        base["last_cycle"] = last_cycle
        return type(base_status)(**base)

    def embodied_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = self.embodied_store.get_state("embodied_field_projection")
        return self.embodied.projection() if projection is None else projection

    def black_mirror(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_black_mirror(self)
        if "embodied_eight_sheaf_supernet" not in projection:
            embodied = self.embodied_field()
            projection["embodied_eight_sheaf_supernet"] = {
                "stats": embodied["stats"],
                "source_reverse_index": embodied["source_reverse_index"],
                "local_ball_is_embodied_human_interaction": True,
                "global_hair_is_open_potential": True,
                "resource_metrics_are_downstream": True,
                "unknown_hypotheses_remain_open": True,
            }
        return projection

    def living_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_living_field(self)
        if "embodied_eight_sheaf_supernet" not in projection:
            embodied = self.embodied_field()
            projection["embodied_eight_sheaf_supernet"] = embodied
            projection.setdefault("source_reverse_index", {}).update(
                embodied["source_reverse_index"]
            )
        return projection

    def close(self: ClosureSupernetRuntime) -> None:
        if hasattr(self, "embodied_store"):
            self.embodied_store.close()
        original_close(self)

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.cycle = cycle
    ClosureSupernetRuntime.status = status
    ClosureSupernetRuntime.embodied_field = embodied_field
    ClosureSupernetRuntime.black_mirror = black_mirror
    ClosureSupernetRuntime.living_field = living_field
    ClosureSupernetRuntime.close = close


install_embodied_runtime()
