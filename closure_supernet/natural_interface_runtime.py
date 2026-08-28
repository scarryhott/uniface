from __future__ import annotations

from typing import Any

from .embodied_models import GLOBAL_HAIR_SHEAVES, LOCAL_BALL_SHEAVES
from .live_sense import LiveNaturalInterfaceManager, LiveSenseManager
from .runtime import ClosureSupernetRuntime
from .supernet_integrator import SupernetIntegrator


_PATCHED = False
_LOCAL = {item.value for item in LOCAL_BALL_SHEAVES}
_GLOBAL = {item.value for item in GLOBAL_HAIR_SHEAVES}


class CompleteNaturalInterfaceManager(LiveNaturalInterfaceManager):
    """Final Black Mirror reading over the same event field.

    The existing relation selector remains prior. Eight-sheaf placement only
    situates that relation as local-ball or global-hair context and never creates
    a second ontology or a truth upgrade.
    """

    def _select_chart(
        self,
        event: dict[str, Any] | None,
        *,
        proof: dict[str, Any] | None,
        continuation: dict[str, Any] | None,
        life: dict[str, Any] | None,
    ) -> dict[str, Any]:
        chart = super()._select_chart(
            event,
            proof=proof,
            continuation=continuation,
            life=life,
        )
        if event is None:
            return chart
        sheaf = str(event.get("metadata", {}).get("sheaf") or "")
        if sheaf not in _LOCAL and sheaf not in _GLOBAL:
            return chart
        region = "LOCAL BALL" if sheaf in _LOCAL else "GLOBAL HAIR"
        chart["required_layers"] = list(
            dict.fromkeys([region, sheaf, *chart.get("required_layers", [])])
        )
        if chart.get("kind") == "SHARED_ARCHITECTURE":
            chart["title"] = f"{region.title()} · {sheaf.replace('_', ' ').title()}"
            chart["axiometric_reading"] = (
                "The exact occurrence is situated in the eight-sheaf application chart "
                f"as {sheaf}; {region.lower()} is a relative field reading, not a second runtime."
            )
            chart["selection_reason"] = (
                "The focused occurrence explicitly carries an eight-sheaf receipt; "
                "the smallest faithful chart preserves its local-ball/global-hair location."
            )
        else:
            chart["title"] = f"{chart['title']} · {region.title()}"
        chart["eight_sheaf"] = sheaf
        chart["ball_hair_region"] = region
        chart["truth_issued"] = False
        return chart



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
                "perspective_drives_interface_reselection": True,
                "eight_sheaf_context_preserved_in_natural_chart": True,
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
        self.natural_interface = CompleteNaturalInterfaceManager(self)

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
