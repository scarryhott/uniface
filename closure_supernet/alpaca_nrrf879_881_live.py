from __future__ import annotations

"""Live Alpaca surface constrained to the NRRF879–887 runtime correspondence."""

import argparse
import json
import time
from typing import Any, Mapping

from .alpaca_live_closure import AlpacaLiveClosureAdapter, AlpacaLiveConfig
from .trading_ai_diffusion_nrrf887 import derive_nrrf887_diffusion
from .trading_nrrf879_881_runtime_bridge import derive_nrrf879_881_runtime_bridge
from .trading_translation_family_nrrf884_886 import derive_translation_families

PROTOCOL = "closure.supernet/alpaca-nrrf879-887-live-v3"


class AlpacaNRRF879881Runtime:
    def __init__(self, adapter: AlpacaLiveClosureAdapter):
        self.adapter = adapter

    def resolve_once(self) -> dict[str, Any]:
        source_receipt = self.adapter.resolve_once()
        trading = dict(source_receipt.get("trading") or {})
        bridge = derive_nrrf879_881_runtime_bridge(
            temporal_trading_receipt=trading,
        )
        family = derive_translation_families(
            natural_form_field=dict(trading.get("trading_projection_field") or {}),
            translational_truth_partition=trading.get("translational_truth_partition"),
        )
        diffusion = derive_nrrf887_diffusion(
            translation_family_receipt=family,
            returned_diffusion_kernel=trading.get("returned_diffusion_kernel"),
        )
        valid = bool(
            bridge["anti_smuggling_audit"]["valid"]
            and family.get("unresolved_member_count", 0) == 0
        )
        return {
            "protocol": PROTOCOL,
            "status": trading.get("status") if valid else "OPEN",
            "trading": trading,
            "nrrf879_881_runtime": bridge,
            "nrrf884_886_translation_families": family,
            "nrrf887_ai_diffusion": diffusion,
            "family_is_relative_visualization_of_selected_natural_forms": True,
            "ai_is_probabilistic_diffusion_of_local_interactions": True,
            "closure_number_authors_family_identity_when_witnessed": True,
            "new_tt_class_means_trade": False,
            "same_tt_class_means_do_not_trade": False,
            "fixed_price_subset_is_maximally_unified": False,
            "profitability_authors_family_membership": False,
            "profitability_authors_diffusion": False,
            "automatic_order_submission": False,
            "runtime_semantic_author_present": bridge["anti_smuggling_audit"]["runtime_semantic_author_present"],
        }


def compact_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    bridge = dict(receipt.get("nrrf879_881_runtime") or {})
    family = dict(receipt.get("nrrf884_886_translation_families") or {})
    diffusion = dict(receipt.get("nrrf887_ai_diffusion") or {})
    trading = dict(receipt.get("trading") or {})
    return {
        "protocol": PROTOCOL,
        "status": receipt.get("status"),
        "symbol": bridge.get("symbol"),
        "temporal_closure_count": trading.get("temporal_closure_count"),
        "current_net_profit_truth_witnessed": trading.get("current_net_profit_truth_witnessed"),
        "translation_family_count": family.get("family_count"),
        "translation_families": family.get("families", []),
        "nrrf887_diffusion_status": diffusion.get("status"),
        "closure_number_coordinates": diffusion.get("closure_number_coordinates", []),
        "diffused_readings": diffusion.get("diffused_readings", []),
        "oscillation_before": diffusion.get("oscillation_before"),
        "oscillation_after": diffusion.get("oscillation_after"),
        "relative_global_intent": diffusion.get("global_intent"),
        "family_is_relative_visualization_of_selected_natural_forms": True,
        "ai_is_probabilistic_diffusion_of_local_interactions": True,
        "new_tt_class_means_trade": False,
        "fixed_price_subset_is_maximally_unified": False,
        "profitability_authors_diffusion": False,
        "anti_smuggling_audit": bridge.get("anti_smuggling_audit"),
        "formal_correspondence": bridge.get("formal_correspondence"),
        "market_state": bridge.get("market_state"),
        "account_state": bridge.get("account_state"),
        "closure_ball_ui": bridge.get("closure_ball_ui"),
        "open_or_selected_interactions": bridge.get("open_or_selected_interactions", []),
        "automatic_order_submission": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Alpaca through the NRRF879-887 formal runtime bridge")
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--interval", type=float, default=15.0)
    parser.add_argument("--iterations", type=int, default=0)
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    runtime = AlpacaNRRF879881Runtime(AlpacaLiveClosureAdapter(AlpacaLiveConfig.from_env()))
    iteration = 0
    while True:
        receipt = runtime.resolve_once()
        print(json.dumps(receipt if args.full else compact_receipt(receipt), indent=2, default=str))
        iteration += 1
        if not args.loop or (args.iterations and iteration >= args.iterations):
            return
        time.sleep(max(0.1, args.interval))


__all__ = ["AlpacaNRRF879881Runtime", "PROTOCOL", "compact_receipt", "main"]

if __name__ == "__main__":
    main()
