from __future__ import annotations

from typing import Any

from .inversion import InversionSelfLimitManager
from .inversion_store import InversionStore
from .runtime import ClosureSupernetRuntime
from .supernet_integrator import SupernetIntegrator


_PATCHED = False


def install_inversion_runtime() -> None:
    """Attach NRRF795/796 to the one continuous Supernet runtime."""

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
            explicit == "inversion"
            or "nrrf795" in text
            or "nrrf796" in text
            or "self-limit" in text
            or "self limit" in text
            or "return inversion" in text
            or "one hair" in text
        ):
            return "inversion"
        return original_infer_adapter(form_label, metadata)

    def capabilities(self: SupernetIntegrator) -> dict[str, Any]:
        base = original_capabilities(self)
        base.update(
            {
                "representation_free_closure_derivation": True,
                "return_inversion_is_minus_transpose": True,
                "return_inversion_forced_under_declared_conditions": True,
                "scale_hair_neutral_self_limit": True,
                "one_hair_reading_under_declared_conditions": True,
                "representation_required": False,
                "phenomena_are_scoped_constructions": True,
                "physical_law_claimed": False,
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
        self.inversion_store = InversionStore(self.config.database_path)
        self.inversion = InversionSelfLimitManager(self, self.inversion_store)
        projection_run = self.projection.run

        def combined_projection_run() -> dict[str, Any]:
            projection = projection_run()
            inversion = self.inversion.projection()
            projection["representation_free_self_limit_inversion"] = {
                "stats": inversion["stats"],
                "source_reverse_index": inversion["source_reverse_index"],
                "formal_readings": ["NRRF795", "NRRF796"],
                "return_inversion": "-transpose",
                "representation_required": False,
                "one_hair_reading_under_declared_conditions": True,
                "physical_law_claimed": False,
                "runtime_is_formal_proof": False,
                "determination_issues_truth": False,
            }
            self.store.set_state("black_mirror_projection", projection)
            return projection

        self.projection.run = combined_projection_run

    async def cycle(self: ClosureSupernetRuntime):
        result = await original_cycle(self)
        projection = self.inversion.projection()
        stats = projection["stats"]
        black_mirror = self.projection.run()
        living = self.living_store.get_state("living_field_projection")
        if living is None:
            living = self.living.field_projection(black_mirror)
        living["representation_free_self_limit_inversion"] = projection
        living.setdefault("stats", {}).update(
            {
                "self_limit_relations": stats["relations"],
                "self_limit_exact": stats["self_limit_exact"],
                "return_inversion_involutive": stats["involutive"],
                "one_hair_constructions": stats["constructions"],
                "representation_required": False,
                "physical_law_claimed": False,
            }
        )
        living.setdefault("source_reverse_index", {}).update(
            projection["source_reverse_index"]
        )
        self.living_store.set_state("living_field_projection", living)
        payload = result.model_dump(mode="json")
        payload["inversion"] = stats
        self.store.set_state("last_cycle", payload)
        return result

    def status(self: ClosureSupernetRuntime):
        base_status = original_status(self)
        base = base_status.model_dump(mode="python")
        last_cycle = dict(base.get("last_cycle") or {})
        last_cycle["inversion"] = self.inversion_store.stats()
        base["last_cycle"] = last_cycle
        return type(base_status)(**base)

    def inversion_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = self.inversion_store.get_state("inversion_field_projection")
        return self.inversion.projection() if projection is None else projection

    def black_mirror(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_black_mirror(self)
        if "representation_free_self_limit_inversion" not in projection:
            inversion = self.inversion_field()
            projection["representation_free_self_limit_inversion"] = {
                "stats": inversion["stats"],
                "source_reverse_index": inversion["source_reverse_index"],
                "return_inversion": "-transpose",
                "representation_required": False,
                "physical_law_claimed": False,
            }
        return projection

    def living_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_living_field(self)
        if "representation_free_self_limit_inversion" not in projection:
            inversion = self.inversion_field()
            projection["representation_free_self_limit_inversion"] = inversion
            projection.setdefault("source_reverse_index", {}).update(
                inversion["source_reverse_index"]
            )
        return projection

    def close(self: ClosureSupernetRuntime) -> None:
        if hasattr(self, "inversion_store"):
            self.inversion_store.close()
        original_close(self)

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.cycle = cycle
    ClosureSupernetRuntime.status = status
    ClosureSupernetRuntime.inversion_field = inversion_field
    ClosureSupernetRuntime.black_mirror = black_mirror
    ClosureSupernetRuntime.living_field = living_field
    ClosureSupernetRuntime.close = close


install_inversion_runtime()
