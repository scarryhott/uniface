from __future__ import annotations

from typing import Any

from .equality_network import RelativeEqualityManager
from .equality_store import RelativeEqualityStore
from .runtime import ClosureSupernetRuntime


_PATCHED = False


def install_relative_equality_runtime() -> None:
    """Layer context-indexed relative equality over the TranslationEvent field."""

    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    original_init = ClosureSupernetRuntime.__init__
    original_cycle = ClosureSupernetRuntime.cycle
    original_status = ClosureSupernetRuntime.status
    original_black_mirror = ClosureSupernetRuntime.black_mirror
    original_close = ClosureSupernetRuntime.close

    def init(self: ClosureSupernetRuntime, config=None) -> None:
        original_init(self, config)
        self.relative_equality_store = RelativeEqualityStore(
            self.config.database_path
        )
        self.relative_equality = RelativeEqualityManager(
            self.store,
            self.translation_store,
            self.relative_equality_store,
        )

        projection_run = self.projection.run

        def combined_projection_run() -> dict[str, Any]:
            projection = projection_run()
            equality = self.relative_equality.projection()
            projection["relative_equality"] = {
                "stats": equality["stats"],
                "source_reverse_index": equality["source_reverse_index"],
                "natural_components": equality["natural_components"],
                "context_indexed": True,
                "witness_valued": True,
                "directed_translation_precedes_equality": True,
                "canonical_language": None,
                "automatic_global_truth": False,
            }
            self.store.set_state("black_mirror_projection", projection)
            return projection

        self.projection.run = combined_projection_run

    def reconcile_relative_equalities(self: ClosureSupernetRuntime) -> int:
        if not self.config.relative_equality_enabled:
            return 0
        return self.relative_equality.reconcile_translation_pairs(
            translation_limit=self.config.equality_translation_scan_limit,
            pair_limit=self.config.equality_pairs_per_cycle,
        )

    async def cycle(self: ClosureSupernetRuntime):
        result = await original_cycle(self)
        created = self.reconcile_relative_equalities()
        equality = self.relative_equality.projection()
        stats = equality["stats"]
        result.equality_candidates_created = created
        result.equality_contexts = int(stats["contexts"])
        result.equality_witnesses = int(stats["witnesses"])
        result.equality_coherences = int(stats["coherences"])
        result.equality_admitted = int(stats["admitted_equalities"])
        result.equality_open = int(stats["open_equalities"])
        result.equality_reopened = int(stats["reopened_equalities"])
        result.equality_components = int(stats["natural_components"])

        black_mirror = self.projection.run()
        living = self.living_store.get_state("living_field_projection")
        if living is None:
            living = self.living.field_projection(black_mirror)
        living["relative_equality"] = equality
        living.setdefault("stats", {}).update(
            {
                "equality_contexts": stats["contexts"],
                "relative_equality_witnesses": stats["witnesses"],
                "admitted_relative_equalities": stats["admitted_equalities"],
                "open_relative_equalities": stats["open_equalities"],
                "reopened_relative_equalities": stats["reopened_equalities"],
                "relative_natural_components": stats["natural_components"],
                "relative_equality_context_indexed": True,
                "relative_equality_witness_valued": True,
                "canonical_equality_language": None,
            }
        )
        living.setdefault("source_reverse_index", {}).update(
            equality["source_reverse_index"]
        )
        self.living_store.set_state("living_field_projection", living)
        self.store.set_state("last_cycle", result.model_dump(mode="json"))
        return result

    def status(self: ClosureSupernetRuntime):
        base_status = original_status(self)
        base = base_status.model_dump(mode="python")
        equality = self.relative_equality.projection()
        stats = equality["stats"]
        base.update(
            {
                "equality_contexts": stats["contexts"],
                "equality_witnesses": stats["witnesses"],
                "equality_coherences": stats["coherences"],
                "equality_admitted": stats["admitted_equalities"],
                "equality_open": stats["open_equalities"],
                "equality_reopened": stats["reopened_equalities"],
                "equality_components": stats["natural_components"],
                "relative_equality_enabled": self.config.relative_equality_enabled,
                "relative_equality_context_indexed": True,
                "relative_equality_witness_valued": True,
            }
        )
        return type(base_status)(**base)

    def relative_equality_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = self.relative_equality_store.get_state(
            "relative_equality_projection"
        )
        if projection is None:
            projection = self.relative_equality.projection()
        return projection

    def black_mirror(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_black_mirror(self)
        if "relative_equality" not in projection:
            equality = self.relative_equality_field()
            projection["relative_equality"] = {
                "stats": equality["stats"],
                "source_reverse_index": equality["source_reverse_index"],
                "natural_components": equality["natural_components"],
                "context_indexed": True,
                "witness_valued": True,
                "canonical_language": None,
            }
        return projection

    def close(self: ClosureSupernetRuntime) -> None:
        if hasattr(self, "relative_equality_store"):
            self.relative_equality_store.close()
        original_close(self)

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.reconcile_relative_equalities = (
        reconcile_relative_equalities
    )
    ClosureSupernetRuntime.cycle = cycle
    ClosureSupernetRuntime.status = status
    ClosureSupernetRuntime.relative_equality_field = relative_equality_field
    ClosureSupernetRuntime.black_mirror = black_mirror
    ClosureSupernetRuntime.close = close


install_relative_equality_runtime()
