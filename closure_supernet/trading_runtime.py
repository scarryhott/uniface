from __future__ import annotations

from typing import Any

from .runtime import ClosureSupernetRuntime
from .trading import ClassicalTradingManager
from .trading_store import TradingStore


_PATCHED = False


def install_trading_runtime() -> None:
    """Attach NRRF780 as a simulation-only lens of the one integrator."""

    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    original_init = ClosureSupernetRuntime.__init__
    original_cycle = ClosureSupernetRuntime.cycle
    original_status = ClosureSupernetRuntime.status
    original_black_mirror = ClosureSupernetRuntime.black_mirror
    original_living_field = ClosureSupernetRuntime.living_field
    original_close = ClosureSupernetRuntime.close

    def init(self: ClosureSupernetRuntime, config=None) -> None:
        original_init(self, config)
        self.trading_store = TradingStore(self.config.database_path)
        self.trading = ClassicalTradingManager(self, self.trading_store)

        projection_run = self.projection.run

        def combined_projection_run() -> dict[str, Any]:
            projection = projection_run()
            trading = self.trading.projection()
            projection["classical_trading"] = {
                "stats": trading["stats"],
                "source_reverse_index": trading["source_reverse_index"],
                "formal_reading": "NRRF780",
                "simulation_only": True,
                "direct_market_execution": False,
                "determination_issues_truth": False,
            }
            self.store.set_state("black_mirror_projection", projection)
            return projection

        self.projection.run = combined_projection_run

    async def cycle(self: ClosureSupernetRuntime):
        result = await original_cycle(self)
        trading = self.trading.projection()
        stats = trading["stats"]
        result.trading_transactions = int(stats["transactions"])
        result.trading_systems = int(stats["systems"])
        result.trading_circuits = int(stats["circuits"])
        result.trading_pnl = int(stats["pnl"])

        black_mirror = self.projection.run()
        living = self.living_store.get_state("living_field_projection")
        if living is None:
            living = self.living.field_projection(black_mirror)
        living["classical_trading"] = trading
        living.setdefault("stats", {}).update(
            {
                "trading_transactions": stats["transactions"],
                "trading_systems": stats["systems"],
                "trading_circuits": stats["circuits"],
                "trading_pnl": stats["pnl"],
                "trading_simulation_only": True,
                "direct_market_execution": False,
            }
        )
        living.setdefault("source_reverse_index", {}).update(
            trading["source_reverse_index"]
        )
        self.living_store.set_state("living_field_projection", living)
        self.store.set_state("last_cycle", result.model_dump(mode="json"))
        return result

    def status(self: ClosureSupernetRuntime):
        base_status = original_status(self)
        base = base_status.model_dump(mode="python")
        stats = self.trading_store.stats()
        base.update(
            {
                "trading_transactions": stats["transactions"],
                "trading_systems": stats["systems"],
                "trading_circuits": stats["circuits"],
                "trading_pnl": stats["pnl"],
                "trading_enabled": self.config.trading_enabled,
                "trading_simulation_only": True,
                "trading_direct_market_execution": False,
            }
        )
        return type(base_status)(**base)

    def trading_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = self.trading_store.get_state("trading_field_projection")
        return self.trading.projection() if projection is None else projection

    def black_mirror(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_black_mirror(self)
        if "classical_trading" not in projection:
            trading = self.trading_field()
            projection["classical_trading"] = {
                "stats": trading["stats"],
                "source_reverse_index": trading["source_reverse_index"],
                "formal_reading": "NRRF780",
                "simulation_only": True,
                "direct_market_execution": False,
            }
        return projection

    def living_field(self: ClosureSupernetRuntime) -> dict[str, Any]:
        projection = original_living_field(self)
        if "classical_trading" not in projection:
            trading = self.trading_field()
            projection["classical_trading"] = trading
            projection.setdefault("source_reverse_index", {}).update(
                trading["source_reverse_index"]
            )
        return projection

    def close(self: ClosureSupernetRuntime) -> None:
        if hasattr(self, "trading_store"):
            self.trading_store.close()
        original_close(self)

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.cycle = cycle
    ClosureSupernetRuntime.status = status
    ClosureSupernetRuntime.trading_field = trading_field
    ClosureSupernetRuntime.black_mirror = black_mirror
    ClosureSupernetRuntime.living_field = living_field
    ClosureSupernetRuntime.close = close


install_trading_runtime()
