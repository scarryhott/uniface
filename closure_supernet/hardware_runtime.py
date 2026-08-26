from __future__ import annotations

from typing import Any

from .hardware_gateway import HardwareClosureManager
from .hardware_store import HardwareClosureStore
from .runtime import ClosureSupernetRuntime


_PATCHED = False


def install_hardware_closure_runtime() -> None:
    """Layer the bounded Black Mirror hardware loop over the living runtime."""

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
        self.hardware_store = HardwareClosureStore(self.config.database_path)
        self.hardware = HardwareClosureManager(
            self.config,
            self.store,
            self.living_store,
            self.translation_store,
            self.translation,
            self.hardware_store,
            self.ingest,
        )

        projection_run = self.projection.run

        def combined_projection_run() -> dict[str, Any]:
            projection = projection_run()
            hardware = self.hardware.projection()
            projection["hardware_closure_loop"] = {
                "stats": hardware["stats"],
                "source_reverse_index": hardware["source_reverse_index"],
                "simulation_only": True,
                "direct_physical_actuation": False,
                "temporary_global_constraint": True,
                "return_reintegrates_open": True,
            }
            self.store.set_state("black_mirror_projection", projection)
            return projection

        self.projection.run = combined_projection_run

    async def cycle(self: ClosureSupernetRuntime):
        expired = 0
        reintegrated = 0
        if self.config.hardware_closure_enabled:
            expired = self.hardware.expire_constraints()
            reintegrated = await self.hardware.reintegrate_pending(
                self.config.hardware_reintegrations_per_cycle
            )
        result = await original_cycle(self)
        hardware = self.hardware.projection()
        stats = hardware["stats"]
        result.hardware_devices = int(stats["devices"])
        result.hardware_constraints = int(stats["constraints"])
        result.hardware_twin_runs = int(stats["twin_runs"])
        result.hardware_actuations = int(stats["actuations"])
        result.hardware_returns = int(stats["returns"])
        result.hardware_pending_returns = int(stats["pending_returns"])
        result.hardware_reintegrations = reintegrated
        result.hardware_expired_constraints = expired

        black_mirror = self.projection.run()
        living = self.living_store.get_state("living_field_projection")
        if living is None:
            living = self.living.field_projection(black_mirror)
        living["hardware_closure_loop"] = hardware
        living.setdefault("stats", {}).update(
            {
                "hardware_devices": stats["devices"],
                "hardware_constraints": stats["constraints"],
                "hardware_twin_runs": stats["twin_runs"],
                "hardware_actuations": stats["actuations"],
                "hardware_returns": stats["returns"],
                "hardware_pending_returns": stats["pending_returns"],
                "hardware_simulation_only": True,
                "direct_physical_actuation": False,
            }
        )
        living.setdefault("source_reverse_index", {}).update(
            hardware["source_reverse_index"]
        )
        self.living_store.set_state("living_field_projection", living)
        self.store.set_state("last_cycle", result.model_dump(mode="json"))
        return result

    def status(self: ClosureSupernetRuntime):
        base_status = original_status(self)
        base = base_status.model_dump(mode="python")
        stats = self.hardware_store.stats()
        base.update(
            {
                "hardware_devices": stats["devices"],
                "hardware_constraints": stats["constraints"],
                "hardware_twin_runs": stats["twin_runs"],
                "hardware_actuations": stats["actuations"],
                "hardware_returns": stats["returns"],
                "hardware_pending_returns": stats["pending_returns"],
                "hardware_closure_enabled": self.config.hardware_closure_enabled,
                "hardware_simulation_only": True,
                "hardware_direct_physical_actuation": False,
            }
        )
        return type(base_status)(**base)

    def hardware_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = self.hardware_store.get_state("hardware_field_projection")
        if projection is None:
            projection = self.hardware.projection()
        return projection

    def black_mirror(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_black_mirror(self)
        if "hardware_closure_loop" not in projection:
            hardware = self.hardware_field()
            projection["hardware_closure_loop"] = {
                "stats": hardware["stats"],
                "source_reverse_index": hardware["source_reverse_index"],
                "simulation_only": True,
                "direct_physical_actuation": False,
                "temporary_global_constraint": True,
            }
        return projection

    def close(self: ClosureSupernetRuntime) -> None:
        if hasattr(self, "hardware_store"):
            self.hardware_store.close()
        original_close(self)

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.cycle = cycle
    ClosureSupernetRuntime.status = status
    ClosureSupernetRuntime.hardware_field = hardware_field
    ClosureSupernetRuntime.black_mirror = black_mirror
    ClosureSupernetRuntime.close = close


install_hardware_closure_runtime()
