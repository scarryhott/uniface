from __future__ import annotations

from typing import Any

from .constructive import ConstructiveClosureManager
from .constructive_store import ConstructiveStore
from .runtime import ClosureSupernetRuntime
from .supernet_integrator import SupernetIntegrator


_PATCHED = False


def install_constructive_runtime() -> None:
    """Attach NRRF783 explicit-witness forms to the one Supernet runtime."""

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
                str(metadata.get("living_form", "")),
                str(metadata.get("formal_reading", "")),
            ]
        ).lower()
        if (
            explicit == "constructive"
            or "constructive" in text
            or "axiometric form" in text
            or "nrrf783" in text
        ):
            return "constructive"
        return original_infer_adapter(form_label, metadata)

    def capabilities(self: SupernetIntegrator) -> dict[str, Any]:
        base = original_capabilities(self)
        base.update(
            {
                "constructive_explicit_witnesses": True,
                "section_carried_as_data": True,
                "classical_choice_required": False,
                "excluded_middle_required": False,
                "runtime_is_formal_proof": False,
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
        self.constructive_store = ConstructiveStore(self.config.database_path)
        self.constructive = ConstructiveClosureManager(self, self.constructive_store)

        projection_run = self.projection.run

        def combined_projection_run() -> dict[str, Any]:
            projection = projection_run()
            constructive = self.constructive.projection()
            projection["constructive_axiometric_unification"] = {
                "stats": constructive["stats"],
                "source_reverse_index": constructive["source_reverse_index"],
                "formal_reading": "NRRF783",
                "explicit_witnesses": True,
                "section_carried_as_data": True,
                "classical_choice_required": False,
                "excluded_middle_required": False,
                "runtime_is_formal_proof": False,
                "determination_issues_truth": False,
            }
            self.store.set_state("black_mirror_projection", projection)
            return projection

        self.projection.run = combined_projection_run

    async def cycle(self: ClosureSupernetRuntime):
        result = await original_cycle(self)
        projection = self.constructive.projection()
        stats = projection["stats"]
        black_mirror = self.projection.run()
        living = self.living_store.get_state("living_field_projection")
        if living is None:
            living = self.living.field_projection(black_mirror)
        living["constructive_axiometric_unification"] = projection
        living.setdefault("stats", {}).update(
            {
                "constructive_forms": stats["forms"],
                "constructive_admissible_forms": stats["admissible_forms"],
                "constructive_closing_forms": stats["closing_forms"],
                "constructive_translations": stats["translations"],
                "constructive_comparisons": stats["comparisons"],
                "classical_choice_required": False,
                "excluded_middle_required": False,
            }
        )
        living.setdefault("source_reverse_index", {}).update(
            projection["source_reverse_index"]
        )
        self.living_store.set_state("living_field_projection", living)
        payload = result.model_dump(mode="json")
        payload["constructive"] = stats
        self.store.set_state("last_cycle", payload)
        return result

    def status(self: ClosureSupernetRuntime):
        base_status = original_status(self)
        base = base_status.model_dump(mode="python")
        last_cycle = dict(base.get("last_cycle") or {})
        last_cycle["constructive"] = self.constructive_store.stats()
        base["last_cycle"] = last_cycle
        return type(base_status)(**base)

    def constructive_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = self.constructive_store.get_state(
            "constructive_field_projection"
        )
        return self.constructive.projection() if projection is None else projection

    def black_mirror(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_black_mirror(self)
        if "constructive_axiometric_unification" not in projection:
            constructive = self.constructive_field()
            projection["constructive_axiometric_unification"] = {
                "stats": constructive["stats"],
                "source_reverse_index": constructive["source_reverse_index"],
                "formal_reading": "NRRF783",
                "explicit_witnesses": True,
                "classical_choice_required": False,
                "excluded_middle_required": False,
            }
        return projection

    def living_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_living_field(self)
        if "constructive_axiometric_unification" not in projection:
            constructive = self.constructive_field()
            projection["constructive_axiometric_unification"] = constructive
            projection.setdefault("source_reverse_index", {}).update(
                constructive["source_reverse_index"]
            )
        return projection

    def close(self: ClosureSupernetRuntime) -> None:
        if hasattr(self, "constructive_store"):
            self.constructive_store.close()
        original_close(self)

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.cycle = cycle
    ClosureSupernetRuntime.status = status
    ClosureSupernetRuntime.constructive_field = constructive_field
    ClosureSupernetRuntime.black_mirror = black_mirror
    ClosureSupernetRuntime.living_field = living_field
    ClosureSupernetRuntime.close = close


install_constructive_runtime()
