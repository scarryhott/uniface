from __future__ import annotations

from typing import Any

from .live_sense import LiveNaturalInterfaceManager, LiveSenseManager
from .runtime import ClosureSupernetRuntime
from .supernet_integrator import SupernetIntegrator


_PATCHED = False


def install_natural_interface_runtime() -> None:
    """Attach the derived UI reading and interaction-time Sense to one field."""

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
                "interaction_time_sense": True,
                "sense_uses_existing_understanding_interpretation_admission": True,
                "sense_reconciles_translation_field": True,
                "sense_applies_existing_natural_selection": True,
                "background_autonomy_required_for_interaction_sense": False,
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
        self.live_sense = LiveSenseManager(self)
        self.natural_interface = LiveNaturalInterfaceManager(self)

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
