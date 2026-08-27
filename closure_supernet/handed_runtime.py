from __future__ import annotations

from typing import Any

from .handed import HandedLifeManager
from .handed_store import HandedLifeStore
from .runtime import ClosureSupernetRuntime
from .supernet_integrator import SupernetIntegrator


_PATCHED = False


def install_handed_life_runtime() -> None:
    """Attach NRRF800 to the one continuous Supernet runtime."""

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
            explicit == "handed"
            or "nrrf800" in text
            or "handed life" in text
            or "ballreturn" in text
            or "hairreturn" in text
            or "four-ball" in text
            or "potential gate" in text
        ):
            return "handed"
        return original_infer_adapter(form_label, metadata)

    def capabilities(self: SupernetIntegrator) -> dict[str, Any]:
        base = original_capabilities(self)
        base.update(
            {
                "handed_life_ball": "ZMod 4",
                "handed_life_ball_sheaves": 4,
                "handed_life_hair_sheaves": 1,
                "handed_life_hair_is_ball_completion": True,
                "ball_return_preserves_hand": True,
                "hair_return_inverts_hand": True,
                "self_limit_is_hand_inversion_at_fixed_ball_phase": True,
                "left_handed_potential_gate": True,
                "human_relation_mapping_available": True,
                "biological_chirality_claimed": False,
                "biological_life_claimed": False,
                "human_law_claimed": False,
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
        self.handed_life_store = HandedLifeStore(self.config.database_path)
        self.handed_life = HandedLifeManager(self, self.handed_life_store)
        projection_run = self.projection.run

        def combined_projection_run() -> dict[str, Any]:
            projection = projection_run()
            handed = self.handed_life.projection()
            projection["handed_life_temporal_closure"] = {
                "stats": handed["stats"],
                "source_reverse_index": handed["source_reverse_index"],
                "formal_readings": ["NRRF799", "NRRF800"],
                "ball_sheaves": 4,
                "hair_sheaves": 1,
                "hair_is_ball_completion": True,
                "biological_claimed": False,
                "human_law_claimed": False,
                "truth_issued": False,
            }
            self.store.set_state("black_mirror_projection", projection)
            return projection

        self.projection.run = combined_projection_run

    async def cycle(self: ClosureSupernetRuntime):
        result = await original_cycle(self)
        projection = self.handed_life.projection()
        stats = projection["stats"]
        black_mirror = self.projection.run()
        living = self.living_store.get_state("living_field_projection")
        if living is None:
            living = self.living.field_projection(black_mirror)
        living["handed_life_temporal_closure"] = projection
        living.setdefault("stats", {}).update(
            {
                "handed_life_systems": stats["systems"],
                "handed_life_records": stats["records"],
                "four_ball_one_hair_systems": stats["four_ball_one_hair"],
                "left_handed_gate_traces": stats["left_gate_traces"],
                "human_relation_readings": stats["human_relations"],
                "handed_ball_returns": stats["ball_returns"],
                "handed_hair_returns": stats["hair_returns"],
                "biological_life_claimed": False,
                "human_law_claimed": False,
            }
        )
        living.setdefault("source_reverse_index", {}).update(
            projection["source_reverse_index"]
        )
        self.living_store.set_state("living_field_projection", living)
        payload = result.model_dump(mode="json")
        payload["handed_life"] = stats
        self.store.set_state("last_cycle", payload)
        return result

    def status(self: ClosureSupernetRuntime):
        base_status = original_status(self)
        base = base_status.model_dump(mode="python")
        last_cycle = dict(base.get("last_cycle") or {})
        last_cycle["handed_life"] = self.handed_life_store.stats()
        base["last_cycle"] = last_cycle
        return type(base_status)(**base)

    def handed_life_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = self.handed_life_store.get_state(
            "handed_life_field_projection"
        )
        return self.handed_life.projection() if projection is None else projection

    def black_mirror(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_black_mirror(self)
        if "handed_life_temporal_closure" not in projection:
            handed = self.handed_life_field()
            projection["handed_life_temporal_closure"] = {
                "stats": handed["stats"],
                "source_reverse_index": handed["source_reverse_index"],
                "ball_sheaves": 4,
                "hair_sheaves": 1,
                "hair_is_ball_completion": True,
                "truth_issued": False,
            }
        return projection

    def living_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_living_field(self)
        if "handed_life_temporal_closure" not in projection:
            handed = self.handed_life_field()
            projection["handed_life_temporal_closure"] = handed
            projection.setdefault("source_reverse_index", {}).update(
                handed["source_reverse_index"]
            )
        return projection

    def close(self: ClosureSupernetRuntime) -> None:
        if hasattr(self, "handed_life_store"):
            self.handed_life_store.close()
        original_close(self)

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.cycle = cycle
    ClosureSupernetRuntime.status = status
    ClosureSupernetRuntime.handed_life_field = handed_life_field
    ClosureSupernetRuntime.black_mirror = black_mirror
    ClosureSupernetRuntime.living_field = living_field
    ClosureSupernetRuntime.close = close


install_handed_life_runtime()
