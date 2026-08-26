from __future__ import annotations

from typing import Any

from .renormalization import RenormalizationManager
from .renormalization_store import RenormalizationStore
from .runtime import ClosureSupernetRuntime
from .supernet_integrator import SupernetIntegrator


_PATCHED = False


def install_renormalization_runtime() -> None:
    """Attach NRRF781 to the one continuous Supernet field."""

    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    original_infer_adapter = SupernetIntegrator._infer_adapter

    def infer_adapter(form_label: str, metadata: dict[str, Any]) -> str:
        explicit = str(metadata.get("adapter_label") or "").lower()
        text = " ".join(
            [
                explicit,
                str(form_label),
                str(metadata.get("source_kind", "")),
                str(metadata.get("kind", "")),
                str(metadata.get("living_form", "")),
            ]
        ).lower()
        if explicit == "renormalization" or "renormal" in text or "nrrf781" in text:
            return "renormalization"
        return original_infer_adapter(form_label, metadata)

    SupernetIntegrator._infer_adapter = staticmethod(infer_adapter)

    original_init = ClosureSupernetRuntime.__init__
    original_cycle = ClosureSupernetRuntime.cycle
    original_status = ClosureSupernetRuntime.status
    original_black_mirror = ClosureSupernetRuntime.black_mirror
    original_living_field = ClosureSupernetRuntime.living_field
    original_close = ClosureSupernetRuntime.close

    def init(self: ClosureSupernetRuntime, config=None) -> None:
        original_init(self, config)
        self.renormalization_store = RenormalizationStore(self.config.database_path)
        self.renormalization = RenormalizationManager(self, self.renormalization_store)

        projection_run = self.projection.run

        def combined_projection_run() -> dict[str, Any]:
            projection = projection_run()
            renormalization = self.renormalization.projection()
            projection["relative_renormalization_closure"] = {
                "stats": renormalization["stats"],
                "source_reverse_index": renormalization["source_reverse_index"],
                "formal_reading": "NRRF781",
                "scheme_is_closure": False,
                "absolute_level_determined": False,
                "determination_issues_truth": False,
            }
            self.store.set_state("black_mirror_projection", projection)
            return projection

        self.projection.run = combined_projection_run

    async def cycle(self: ClosureSupernetRuntime):
        result = await original_cycle(self)
        projection = self.renormalization.projection()
        stats = projection["stats"]
        black_mirror = self.projection.run()
        living = self.living_store.get_state("living_field_projection")
        if living is None:
            living = self.living.field_projection(black_mirror)
        living["relative_renormalization_closure"] = projection
        living.setdefault("stats", {}).update(
            {
                "renormalization_families": stats["families"],
                "renormalization_determined_closures": stats[
                    "determined_closures"
                ],
                "renormalization_open_universality": stats["open_universality"],
                "renormalization_schemes": stats["schemes"],
                "absolute_level_determined": False,
                "scheme_is_closure": False,
            }
        )
        living.setdefault("source_reverse_index", {}).update(
            projection["source_reverse_index"]
        )
        self.living_store.set_state("living_field_projection", living)

        payload = result.model_dump(mode="json")
        payload["renormalization"] = stats
        self.store.set_state("last_cycle", payload)
        return result

    def status(self: ClosureSupernetRuntime):
        base_status = original_status(self)
        base = base_status.model_dump(mode="python")
        last_cycle = dict(base.get("last_cycle") or {})
        last_cycle["renormalization"] = self.renormalization_store.stats()
        base["last_cycle"] = last_cycle
        return type(base_status)(**base)

    def renormalization_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = self.renormalization_store.get_state(
            "renormalization_field_projection"
        )
        return self.renormalization.projection() if projection is None else projection

    def black_mirror(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_black_mirror(self)
        if "relative_renormalization_closure" not in projection:
            renormalization = self.renormalization_field()
            projection["relative_renormalization_closure"] = {
                "stats": renormalization["stats"],
                "source_reverse_index": renormalization["source_reverse_index"],
                "formal_reading": "NRRF781",
                "scheme_is_closure": False,
                "absolute_level_determined": False,
            }
        return projection

    def living_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_living_field(self)
        if "relative_renormalization_closure" not in projection:
            renormalization = self.renormalization_field()
            projection["relative_renormalization_closure"] = renormalization
            projection.setdefault("source_reverse_index", {}).update(
                renormalization["source_reverse_index"]
            )
        return projection

    def close(self: ClosureSupernetRuntime) -> None:
        if hasattr(self, "renormalization_store"):
            self.renormalization_store.close()
        original_close(self)

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.cycle = cycle
    ClosureSupernetRuntime.status = status
    ClosureSupernetRuntime.renormalization_field = renormalization_field
    ClosureSupernetRuntime.black_mirror = black_mirror
    ClosureSupernetRuntime.living_field = living_field
    ClosureSupernetRuntime.close = close


install_renormalization_runtime()
