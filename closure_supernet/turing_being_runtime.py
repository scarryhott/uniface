from __future__ import annotations

from typing import Any

from .runtime import ClosureSupernetRuntime
from .supernet_integrator import SupernetIntegrator
from .turing_being import TuringBeingManager
from .turing_being_store import TuringBeingStore


_PATCHED = False


def install_turing_being_runtime() -> None:
    """Attach NRRF805 after completion and handed charts, without replacing either."""

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
            explicit == "turing_being"
            or "nrrf805" in text
            or "turing being" in text
            or "global hair zero" in text
            or "local ball infinity" in text
            or "translational truth prior" in text
        ):
            return "turing_being"
        return original_infer_adapter(form_label, metadata)

    def capabilities(self: SupernetIntegrator) -> dict[str, Any]:
        base = original_capabilities(self)
        base.update(
            {
                "turing_being_life_primitive": True,
                "global_hair_zero_is_executor": True,
                "local_ball_infinity_is_reactor": True,
                "zero_infinity_are_poles_not_cardinalities": True,
                "internal_external_prior_to_translational_truth": False,
                "hand_prior_to_translational_truth": False,
                "actual_potential_prior_to_translational_truth": False,
                "finite_ball_hair_chart_prior_to_translational_truth": False,
                "four_ball_one_hair_is_derived_chart": True,
                "turing_complete_assumed": False,
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
        self.turing_being_store = TuringBeingStore(self.config.database_path)
        self.turing_being = TuringBeingManager(self, self.turing_being_store)
        projection_run = self.projection.run

        def combined_projection_run() -> dict[str, Any]:
            projection = projection_run()
            turing = self.turing_being.projection()
            projection["turing_being_life"] = {
                "stats": turing["stats"],
                "source_reverse_index": turing["source_reverse_index"],
                "formal_readings": ["NRRF799", "NRRF800", "NRRF802", "NRRF805"],
                "primitive": turing["primitive"],
                "internal_external_prior_to_translational_truth": False,
                "finite_ball_hair_foundational": False,
                "truth_issued": False,
            }
            self.store.set_state("black_mirror_projection", projection)
            return projection

        self.projection.run = combined_projection_run

    async def cycle(self: ClosureSupernetRuntime):
        result = await original_cycle(self)
        projection = self.turing_being.projection()
        stats = projection["stats"]
        black_mirror = self.projection.run()
        living = self.living_store.get_state("living_field_projection")
        if living is None:
            living = self.living.field_projection(black_mirror)
        living["turing_being_life"] = projection
        living.setdefault("stats", {}).update(
            {
                "turing_being_life_events": stats["life_events"],
                "turing_being_truth_complete": stats["translational_truth_complete"],
                "turing_being_awaiting_reaction": stats["awaiting_reaction"],
                "turing_being_internal_external_defined": stats[
                    "internal_external_defined"
                ],
                "turing_being_derived_finite_charts": stats["derived_finite_charts"],
                "internal_external_prior_to_translational_truth": False,
                "finite_ball_hair_foundational": False,
            }
        )
        living.setdefault("source_reverse_index", {}).update(
            projection["source_reverse_index"]
        )
        self.living_store.set_state("living_field_projection", living)
        payload = result.model_dump(mode="json")
        payload["turing_being"] = stats
        self.store.set_state("last_cycle", payload)
        return result

    def status(self: ClosureSupernetRuntime):
        base_status = original_status(self)
        base = base_status.model_dump(mode="python")
        last_cycle = dict(base.get("last_cycle") or {})
        last_cycle["turing_being"] = self.turing_being_store.stats()
        base["last_cycle"] = last_cycle
        return type(base_status)(**base)

    def turing_being_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = self.turing_being_store.get_state("turing_being_field_projection")
        return self.turing_being.projection() if projection is None else projection

    def black_mirror(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_black_mirror(self)
        if "turing_being_life" not in projection:
            turing = self.turing_being_field()
            projection["turing_being_life"] = {
                "stats": turing["stats"],
                "source_reverse_index": turing["source_reverse_index"],
                "primitive": turing["primitive"],
                "internal_external_prior_to_translational_truth": False,
                "finite_ball_hair_foundational": False,
                "truth_issued": False,
            }
        return projection

    def living_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_living_field(self)
        if "turing_being_life" not in projection:
            turing = self.turing_being_field()
            projection["turing_being_life"] = turing
            projection.setdefault("source_reverse_index", {}).update(
                turing["source_reverse_index"]
            )
        return projection

    def close(self: ClosureSupernetRuntime) -> None:
        if hasattr(self, "turing_being_store"):
            self.turing_being_store.close()
        original_close(self)

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.cycle = cycle
    ClosureSupernetRuntime.status = status
    ClosureSupernetRuntime.turing_being_field = turing_being_field
    ClosureSupernetRuntime.black_mirror = black_mirror
    ClosureSupernetRuntime.living_field = living_field
    ClosureSupernetRuntime.close = close


install_turing_being_runtime()
