from __future__ import annotations

from typing import Any

from .completion import TranslationalCompletionManager
from .completion_store import CompletionStore
from .runtime import ClosureSupernetRuntime
from .supernet_integrator import SupernetIntegrator


_PATCHED = False


def install_completion_runtime() -> None:
    """Attach NRRF798/799 to the one continuous Supernet runtime."""

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
            explicit == "completion"
            or "nrrf798" in text
            or "nrrf799" in text
            or "eqvgen" in text
            or "translational completion" in text
            or "finite reach" in text
            or "local global completion" in text
        ):
            return "completion"
        return original_infer_adapter(form_label, metadata)

    def capabilities(self: SupernetIntegrator) -> dict[str, Any]:
        base = original_capabilities(self)
        base.update(
            {
                "bare_local_steps_generate_completion": True,
                "every_completion_equality_has_finite_local_lineage": True,
                "local_invariance_iff_global_translationality": True,
                "local_truths_recover_global_completion": True,
                "completion_universal_factorization": True,
                "completion_functorial": True,
                "completion_idempotent": True,
                "directed_occurrence_is_not_automatically_admitted_step": True,
                "canonical_representative_selected": False,
                "runtime_is_formal_proof": False,
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
        self.completion_store = CompletionStore(self.config.database_path)
        self.completion = TranslationalCompletionManager(self, self.completion_store)
        projection_run = self.projection.run

        def combined_projection_run() -> dict[str, Any]:
            projection = projection_run()
            completion = self.completion.projection()
            projection["natural_translational_completion"] = {
                "stats": completion["stats"],
                "source_reverse_index": completion["source_reverse_index"],
                "formal_readings": ["NRRF798", "NRRF799"],
                "local_global_same_completion": True,
                "every_global_identification_requires_finite_local_lineage": True,
                "completion_idempotent": True,
                "truth_issued": False,
            }
            self.store.set_state("black_mirror_projection", projection)
            return projection

        self.projection.run = combined_projection_run

    async def cycle(self: ClosureSupernetRuntime):
        result = await original_cycle(self)
        projection = self.completion.projection()
        stats = projection["stats"]
        black_mirror = self.projection.run()
        living = self.living_store.get_state("living_field_projection")
        if living is None:
            living = self.living.field_projection(black_mirror)
        living["natural_translational_completion"] = projection
        living.setdefault("stats", {}).update(
            {
                "completion_systems": stats["systems"],
                "completion_local_steps": stats["local_steps"],
                "completion_classes": stats["completion_classes"],
                "finite_path_complete_systems": stats["finite_path_complete"],
                "completion_maps": stats["maps"],
                "local_global_same_completion": True,
                "completion_idempotent": True,
            }
        )
        living.setdefault("source_reverse_index", {}).update(
            projection["source_reverse_index"]
        )
        self.living_store.set_state("living_field_projection", living)
        payload = result.model_dump(mode="json")
        payload["completion"] = stats
        self.store.set_state("last_cycle", payload)
        return result

    def status(self: ClosureSupernetRuntime):
        base_status = original_status(self)
        base = base_status.model_dump(mode="python")
        last_cycle = dict(base.get("last_cycle") or {})
        last_cycle["completion"] = self.completion_store.stats()
        base["last_cycle"] = last_cycle
        return type(base_status)(**base)

    def completion_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = self.completion_store.get_state("completion_field_projection")
        return self.completion.projection() if projection is None else projection

    def black_mirror(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_black_mirror(self)
        if "natural_translational_completion" not in projection:
            completion = self.completion_field()
            projection["natural_translational_completion"] = {
                "stats": completion["stats"],
                "source_reverse_index": completion["source_reverse_index"],
                "local_global_same_completion": True,
                "every_global_identification_requires_finite_local_lineage": True,
                "truth_issued": False,
            }
        return projection

    def living_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_living_field(self)
        if "natural_translational_completion" not in projection:
            completion = self.completion_field()
            projection["natural_translational_completion"] = completion
            projection.setdefault("source_reverse_index", {}).update(
                completion["source_reverse_index"]
            )
        return projection

    def close(self: ClosureSupernetRuntime) -> None:
        if hasattr(self, "completion_store"):
            self.completion_store.close()
        original_close(self)

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.cycle = cycle
    ClosureSupernetRuntime.status = status
    ClosureSupernetRuntime.completion_field = completion_field
    ClosureSupernetRuntime.black_mirror = black_mirror
    ClosureSupernetRuntime.living_field = living_field
    ClosureSupernetRuntime.close = close


install_completion_runtime()
