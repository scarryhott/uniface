from __future__ import annotations

from typing import Any

from .runtime import ClosureSupernetRuntime
from .selection import SelectionAuditManager
from .selection_store import SelectionStore
from .supernet_integrator import SupernetIntegrator


_PATCHED = False


def install_selection_runtime() -> None:
    """Attach NRRF790 completeness/isolation audit to the one runtime."""

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
                str(metadata.get("formal_reading", "")),
                str(metadata.get("selection_state", "")),
            ]
        ).lower()
        if (
            explicit == "selector"
            or "nrrf790" in text
            or "forced isolation" in text
            or "natural selection" in text
            or "selection completeness" in text
        ):
            return "selector"
        return original_infer_adapter(form_label, metadata)

    def capabilities(self: SupernetIntegrator) -> dict[str, Any]:
        base = original_capabilities(self)
        base.update(
            {
                "complete_iff_natural_selection": True,
                "incomplete_choice_is_forced_isolation": True,
                "empty_reading_selects_nothing": True,
                "natural_selection_never_removes_admissible_alternative": True,
                "forced_isolation_retains_removed_alternatives": True,
                "forced_isolation_carries_symmetry_witness": True,
                "selection_applies_after_level_orbit_unification": True,
                "canonical_presentation": None,
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
        self.selection_store = SelectionStore(self.config.database_path)
        self.selection = SelectionAuditManager(self, self.selection_store)
        projection_run = self.projection.run

        def combined_projection_run() -> dict[str, Any]:
            projection = projection_run()
            selection = self.selection.projection()
            projection["complete_natural_selection_incomplete_forced_isolation"] = {
                "stats": selection["stats"],
                "source_reverse_index": selection["source_reverse_index"],
                "formal_reading": "NRRF790",
                "natural_selection_requires_completeness": True,
                "forced_isolation_retains_removed_alternatives": True,
                "empty_reading_selects_nothing": True,
                "canonical_presentation": None,
                "determination_issues_truth": False,
            }
            self.store.set_state("black_mirror_projection", projection)
            return projection

        self.projection.run = combined_projection_run

    async def cycle(self: ClosureSupernetRuntime):
        result = await original_cycle(self)
        projection = self.selection.projection()
        stats = projection["stats"]
        black_mirror = self.projection.run()
        living = self.living_store.get_state("living_field_projection")
        if living is None:
            living = self.living.field_projection(black_mirror)
        living["complete_natural_selection_incomplete_forced_isolation"] = projection
        living.setdefault("stats", {}).update(
            {
                "selection_readings": stats["readings"],
                "natural_selections": stats["natural_selections"],
                "forced_isolations": stats["forced_isolations"],
                "open_branching_readings": stats["open_branching"],
                "empty_selection_readings": stats["empty"],
            }
        )
        living.setdefault("source_reverse_index", {}).update(
            projection["source_reverse_index"]
        )
        self.living_store.set_state("living_field_projection", living)
        payload = result.model_dump(mode="json")
        payload["selection_audit"] = stats
        self.store.set_state("last_cycle", payload)
        return result

    def status(self: ClosureSupernetRuntime):
        base_status = original_status(self)
        base = base_status.model_dump(mode="python")
        last_cycle = dict(base.get("last_cycle") or {})
        last_cycle["selection_audit"] = self.selection_store.stats()
        base["last_cycle"] = last_cycle
        return type(base_status)(**base)

    def selection_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = self.selection_store.get_state("selection_field_projection")
        return self.selection.projection() if projection is None else projection

    def black_mirror(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_black_mirror(self)
        if "complete_natural_selection_incomplete_forced_isolation" not in projection:
            selection = self.selection_field()
            projection["complete_natural_selection_incomplete_forced_isolation"] = {
                "stats": selection["stats"],
                "source_reverse_index": selection["source_reverse_index"],
                "formal_reading": "NRRF790",
                "natural_selection_requires_completeness": True,
                "forced_isolation_retains_removed_alternatives": True,
                "canonical_presentation": None,
            }
        return projection

    def living_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_living_field(self)
        if "complete_natural_selection_incomplete_forced_isolation" not in projection:
            selection = self.selection_field()
            projection["complete_natural_selection_incomplete_forced_isolation"] = selection
            projection.setdefault("source_reverse_index", {}).update(
                selection["source_reverse_index"]
            )
        return projection

    def close(self: ClosureSupernetRuntime) -> None:
        if hasattr(self, "selection_store"):
            self.selection_store.close()
        original_close(self)

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.cycle = cycle
    ClosureSupernetRuntime.status = status
    ClosureSupernetRuntime.selection_field = selection_field
    ClosureSupernetRuntime.black_mirror = black_mirror
    ClosureSupernetRuntime.living_field = living_field
    ClosureSupernetRuntime.close = close


install_selection_runtime()
