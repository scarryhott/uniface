from __future__ import annotations

"""Live Alpaca surface for the continuous NRRF879–892 trading closure."""

import argparse
import json
import time
from typing import Any, Mapping

from .alpaca_live_closure import AlpacaLiveClosureAdapter, AlpacaLiveConfig
from .trading_ai_diffusion_nrrf887 import derive_nrrf887_diffusion
from .trading_continuous_unified_closure_nrrf879_892 import derive_continuous_unified_closure
from .trading_nrrf879_881_runtime_bridge import derive_nrrf879_881_runtime_bridge
from .trading_returned_family_kernel_nrrf887_attempt import (
    derive_candidate_fold_embedding,
    derive_returned_family_kernel,
)
from .trading_translation_family_nrrf884_886 import derive_translation_families

PROTOCOL = "closure.supernet/alpaca-nrrf879-892-live-v9-vision-slide"


class AlpacaNRRF879881Runtime:
    def __init__(self, adapter: AlpacaLiveClosureAdapter):
        self.adapter = adapter
        self._continuous_state: dict[str, Any] = {}

    def resolve_once(self) -> dict[str, Any]:
        source_receipt = self.adapter.resolve_once()
        trading = dict(source_receipt.get("trading") or {})
        natural_form_field = dict(trading.get("trading_projection_field") or {})
        bridge = derive_nrrf879_881_runtime_bridge(temporal_trading_receipt=trading)
        family = derive_translation_families(
            natural_form_field=natural_form_field,
            translational_truth_partition=trading.get("translational_truth_partition"),
        )
        kernel_attempt = derive_returned_family_kernel(
            translation_family_receipt=family,
            natural_form_field=natural_form_field,
        )
        returned_kernel = trading.get("returned_diffusion_kernel") or kernel_attempt.get("returned_diffusion_kernel")
        q_embedding_attempt = derive_candidate_fold_embedding(
            translation_family_receipt=family,
            natural_form_field=natural_form_field,
            natural_closure=trading,
        )
        diffusion = derive_nrrf887_diffusion(
            translation_family_receipt=family,
            returned_diffusion_kernel=returned_kernel,
        )
        continuous = derive_continuous_unified_closure(
            trading_receipt=trading,
            prior_state=self._continuous_state,
        )
        self._continuous_state = continuous

        valid = bool(
            bridge["anti_smuggling_audit"]["valid"]
            and family.get("unresolved_member_count", 0) == 0
        )
        return {
            "protocol": PROTOCOL,
            "status": continuous.get("status") if valid else "OPEN",
            "trading": trading,
            "continuous_unified_closure": continuous,
            "nrrf879_881_runtime": bridge,
            "nrrf884_886_translation_families": family,
            "nrrf887_returned_family_kernel_attempt": kernel_attempt,
            "nrrf887_candidate_fold_embedding": q_embedding_attempt,
            "nrrf887_ai_diffusion": diffusion,
            "translational_truth_action_field": continuous.get("translational_truth_action_field"),
            "nrrf892_vision_crystal_market_rendering": continuous.get("nrrf892_vision_crystal_market_rendering"),
            "observation_and_trading_are_translation_equal_readings": True,
            "open_is_current_boundary_not_accumulated_queue": True,
            "realized_profit_is_projection_of_same_continuous_closure": True,
            "action_is_unique_relative_slide_not_prediction": True,
            "market_side_is_relative_visualization_of_translational_slide": True,
            "market_side_is_separate_semantic_bridge": False,
            "vision_slide_closed_through_furthered_family": True,
            "stage_gate_present": False,
            "separate_observation_pipeline_present": False,
            "family_is_relative_visualization_of_selected_natural_forms": True,
            "ai_is_probabilistic_diffusion_of_local_interactions": True,
            "history_derived_kernel_may_feed_diffusion_when_witnessed": True,
            "candidate_q_embedding_may_feed_diffusion": False,
            "new_tt_class_means_trade": False,
            "same_tt_class_means_do_not_trade": False,
            "fixed_price_subset_is_maximally_unified": False,
            "profitability_authors_family_membership": False,
            "profitability_authors_diffusion": False,
            "profitability_authors_action": False,
            "automatic_order_submission": False,
            "runtime_semantic_author_present": bridge["anti_smuggling_audit"]["runtime_semantic_author_present"],
        }


def compact_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    continuous = dict(receipt.get("continuous_unified_closure") or {})
    profit = dict(continuous.get("realized_profit_projection") or {})
    action = dict(continuous.get("translational_truth_action_field") or {})
    rendering = dict(continuous.get("nrrf892_vision_crystal_market_rendering") or {})
    diffusion = dict(receipt.get("nrrf887_ai_diffusion") or {})
    bridge = dict(receipt.get("nrrf879_881_runtime") or {})
    return {
        "protocol": PROTOCOL,
        "status": receipt.get("status"),
        "symbol": bridge.get("symbol"),
        "current_revision": continuous.get("current_revision"),
        "new_returned_reading_count": continuous.get("new_returned_reading_count"),
        "completed_temporal_trade_count": continuous.get("completed_temporal_trade_count"),
        "realized_profit_status": profit.get("status"),
        "realized_net_profit_quote": profit.get("realized_net_profit_quote"),
        "new_realized_profit_delta_quote": profit.get("new_realized_profit_delta_quote"),
        "open_net_profit_temporal_closure_ids": profit.get("open_net_profit_temporal_closure_ids", []),
        "open_boundary": continuous.get("open_boundary"),
        "translation_family_count": continuous.get("translation_families", {}).get("family_count"),
        "returned_family_kernel_status": continuous.get("returned_family_kernel", {}).get("status"),
        "nrrf887_diffusion_status": diffusion.get("status"),
        "relative_global_intent": diffusion.get("global_intent"),
        "translational_truth_action_status": action.get("status"),
        "translational_truth_actions": action.get("actions", []),
        "nrrf892_market_rendering_status": rendering.get("status"),
        "nrrf892_market_renderings": rendering.get("renderings", []),
        "market_side_is_relative_visualization_of_translational_slide": True,
        "observation_and_trading_are_translation_equal_readings": True,
        "realized_profit_is_projection_of_same_continuous_closure": True,
        "action_is_unique_relative_slide_not_prediction": True,
        "open_is_current_boundary_not_accumulated_queue": True,
        "fixed_price_subset_is_maximally_unified": False,
        "profitability_authors_family_membership": False,
        "profitability_authors_action": False,
        "stage_gate_present": False,
        "separate_observation_pipeline_present": False,
        "automatic_order_submission": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Alpaca through continuous NRRF879-892 closure")
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
