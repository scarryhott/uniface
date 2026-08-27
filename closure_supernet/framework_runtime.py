from __future__ import annotations

from typing import Any

from .framework_store import FrameworkStore
from .frameworks import TranslationalFrameworkManager
from .runtime import ClosureSupernetRuntime
from .supernet_integrator import SupernetIntegrator


_PATCHED = False


def install_framework_runtime() -> None:
    """Attach NRRF784/785 to the one continuous Supernet runtime."""
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    original_infer_adapter = SupernetIntegrator._infer_adapter
    original_capabilities = SupernetIntegrator.capabilities

    def infer_adapter(form_label: str, metadata: dict[str, Any]) -> str:
        explicit = str(metadata.get("adapter_label") or "").lower()
        text = " ".join([explicit, str(form_label), str(metadata.get("source_kind", "")), str(metadata.get("kind", "")), str(metadata.get("formal_reading", ""))]).lower()
        if explicit == "framework" or "nrrf784" in text or "nrrf785" in text or "translational truth framework" in text or "natural selection arena" in text or "contextual obstruction" in text:
            return "framework"
        return original_infer_adapter(form_label, metadata)

    def capabilities(self: SupernetIntegrator) -> dict[str, Any]:
        base = original_capabilities(self)
        base.update({
            "level_natural_selection": True,
            "selector_factors_through_level_orbits": True,
            "resource_metrics_are_downstream": True,
            "translational_truth_unique_on_presentation_orbits": True,
            "classical_and_contextual_share_truth": True,
            "global_assignment_required_for_truth": False,
            "contextual_truth_retained": True,
            "classical_choice_required": False,
            "excluded_middle_required": False,
            "runtime_is_formal_proof": False,
        })
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
        self.framework_store = FrameworkStore(self.config.database_path)
        self.frameworks = TranslationalFrameworkManager(self, self.framework_store)
        projection_run = self.projection.run

        def combined_projection_run() -> dict[str, Any]:
            projection = projection_run()
            framework = self.frameworks.projection()
            projection["natural_translational_truth_unification"] = {
                "stats": framework["stats"],
                "source_reverse_index": framework["source_reverse_index"],
                "formal_readings": ["NRRF784", "NRRF785"],
                "natural_selection_is_orbit_selection": True,
                "resource_metrics_are_downstream": True,
                "classical_and_contextual_share_truth": True,
                "global_assignment_required_for_truth": False,
                "runtime_is_formal_proof": False,
                "determination_issues_truth": False,
            }
            self.store.set_state("black_mirror_projection", projection)
            return projection

        self.projection.run = combined_projection_run

    async def cycle(self: ClosureSupernetRuntime):
        result = await original_cycle(self)
        projection = self.frameworks.projection()
        stats = projection["stats"]
        black_mirror = self.projection.run()
        living = self.living_store.get_state("living_field_projection")
        if living is None:
            living = self.living.field_projection(black_mirror)
        living["natural_translational_truth_unification"] = projection
        living.setdefault("stats", {}).update({
            "naturality_arenas": stats["arenas"],
            "natural_arenas": stats["natural_arenas"],
            "truth_frameworks": stats["frameworks"],
            "classical_frameworks": stats["classical"],
            "contextual_frameworks": stats["contextual"],
            "truth_selection_bridges": stats["bridges"],
            "resource_metrics_are_downstream": True,
            "global_assignment_required_for_truth": False,
        })
        living.setdefault("source_reverse_index", {}).update(projection["source_reverse_index"])
        self.living_store.set_state("living_field_projection", living)
        payload = result.model_dump(mode="json")
        payload["frameworks"] = stats
        self.store.set_state("last_cycle", payload)
        return result

    def status(self: ClosureSupernetRuntime):
        base_status = original_status(self)
        base = base_status.model_dump(mode="python")
        last_cycle = dict(base.get("last_cycle") or {})
        last_cycle["frameworks"] = self.framework_store.stats()
        base["last_cycle"] = last_cycle
        return type(base_status)(**base)

    def framework_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = self.framework_store.get_state("framework_field_projection")
        return self.frameworks.projection() if projection is None else projection

    def black_mirror(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_black_mirror(self)
        if "natural_translational_truth_unification" not in projection:
            framework = self.framework_field()
            projection["natural_translational_truth_unification"] = {
                "stats": framework["stats"],
                "source_reverse_index": framework["source_reverse_index"],
                "formal_readings": ["NRRF784", "NRRF785"],
                "resource_metrics_are_downstream": True,
                "classical_and_contextual_share_truth": True,
                "global_assignment_required_for_truth": False,
            }
        return projection

    def living_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_living_field(self)
        if "natural_translational_truth_unification" not in projection:
            framework = self.framework_field()
            projection["natural_translational_truth_unification"] = framework
            projection.setdefault("source_reverse_index", {}).update(framework["source_reverse_index"])
        return projection

    def close(self: ClosureSupernetRuntime) -> None:
        if hasattr(self, "framework_store"):
            self.framework_store.close()
        original_close(self)

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.cycle = cycle
    ClosureSupernetRuntime.status = status
    ClosureSupernetRuntime.framework_field = framework_field
    ClosureSupernetRuntime.black_mirror = black_mirror
    ClosureSupernetRuntime.living_field = living_field
    ClosureSupernetRuntime.close = close


install_framework_runtime()
