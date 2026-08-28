from __future__ import annotations

from typing import Any

from .natural_interface import NaturalInterfaceManager
from .runtime import ClosureSupernetRuntime
from .supernet_integrator import SupernetIntegrator


_PATCHED = False


def install_natural_interface_runtime() -> None:
    """Attach a derived UI reading; do not introduce another field or store."""

    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    original_capabilities = SupernetIntegrator.capabilities

    def capabilities(self: SupernetIntegrator) -> dict[str, Any]:
        base = original_capabilities(self)
        base.update(
            {
                "natural_supernet_interface_available": True,
                "ui_is_admitted_closure_reading": True,
                "natural_chart_unique_under_declared_contract": True,
                "source_fibre_reopenable_from_ui": True,
                "ui_interaction_returns_through_integrator": True,
                "semantic_layers_gated_by_receipts": True,
                "canonical_pixel_layout_selected": False,
                "determination_issues_truth": False,
            }
        )
        return base

    SupernetIntegrator.capabilities = capabilities

    original_init = ClosureSupernetRuntime.__init__

    def init(self: ClosureSupernetRuntime, config=None) -> None:
        original_init(self, config)
        self.natural_interface = NaturalInterfaceManager(self)

    def natural_interface_receipt(
        self: ClosureSupernetRuntime,
        *,
        focus_event_id: str | None = None,
        perspective_id: str | None = None,
    ) -> dict[str, Any]:
        return self.natural_interface.select(
            focus_event_id=focus_event_id,
            perspective_id=perspective_id,
        )

    ClosureSupernetRuntime.__init__ = init
    ClosureSupernetRuntime.natural_interface_receipt = natural_interface_receipt


install_natural_interface_runtime()
