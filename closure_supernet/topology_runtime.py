from __future__ import annotations

from typing import Any

from .runtime import ClosureSupernetRuntime
from .topology import SupernetTopologyService
from .topology_models import TopologyMode


_PATCHED = False


def install_complete_supernet_interface_runtime() -> None:
    """Attach the continuous topology and selector surface to the one integrator."""

    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    original_init = ClosureSupernetRuntime.__init__
    original_cycle = ClosureSupernetRuntime.cycle
    original_black_mirror = ClosureSupernetRuntime.black_mirror
    original_living_field = ClosureSupernetRuntime.living_field

    def init(self: ClosureSupernetRuntime, config=None) -> None:
        original_init(self, config)
        self.topology = SupernetTopologyService(self)

    async def cycle(self: ClosureSupernetRuntime):
        result = await original_cycle(self)
        projection = self.topology.projection(mode=TopologyMode.FIELD)
        self.supernet_store.set_state("continuous_interface_projection", projection)
        return result

    def black_mirror(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_black_mirror(self)
        projection["continuous_supernet_interface"] = {
            "single_surface": True,
            "modes": [item.value for item in TopologyMode],
            "canonical_runtime_operation": "integrate",
            "selector_relation_first": True,
            "determination_issues_truth": False,
            "hardware_simulation_only": True,
        }
        return projection

    def living_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_living_field(self)
        projection["continuous_supernet_interface"] = {
            "single_surface": True,
            "modes": [item.value for item in TopologyMode],
            "subsystems_are_lenses": True,
        }
        return projection

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.cycle = cycle
    ClosureSupernetRuntime.black_mirror = black_mirror
    ClosureSupernetRuntime.living_field = living_field


install_complete_supernet_interface_runtime()
