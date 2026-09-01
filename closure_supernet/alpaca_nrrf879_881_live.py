from __future__ import annotations

"""Live Alpaca surface constrained to the NRRF879–887 runtime correspondence."""

import argparse
import json
import time
from typing import Any, Mapping

from .alpaca_live_closure import AlpacaLiveClosureAdapter, AlpacaLiveConfig
from .trading_ai_diffusion_nrrf887 import derive_nrrf887_diffusion
from .trading_nrrf879_881_runtime_bridge import derive_nrrf879_881_runtime_bridge
from .trading_returned_family_kernel_nrrf887_attempt import (
    derive_candidate_fold_embedding,
    derive_returned_family_kernel,
)
from .trading_translation_family_nrrf884_886 import derive_translation_families

PROTOCOL = "closure.supernet/alpaca-nrrf879-887-live-v4-kernel-attempt"


class AlpacaNRRF879881Runtime:
    def __init__(self, adapter: AlpacaLiveClosureAdapter):
        self.adapter = adapter

    def resolve_once(self) -> dict[str, Any]:
        source_receipt = self.adapter.resolve_once()
        trading = dict(source_receipt.get("trading") or {})
        natural_form_field = dict(trading.get("trading_projection_field") or {})
        bridge = derive_nrrf879_881_runtime_bridge(
            temporal_trading_receipt=trading,
        )
        family = derive_translation_families(
            natural_form_field=natural_form_field,
            translational_truth_partition=trading.get("translational_truth_partition"),
        )

        # P can be derived from the returned temporal family sequence without a
        # predictor.  We use an explicitly returned upstream kernel when one is
        # present; otherwise the history-derived kernel is the only fallback.
        kernel_attempt = derive_returned_family_kernel(
            translation_family_receipt=family,
            natural_form_field=natural_form_field,
        )
        returned_kernel = trading.get("returned_diffusion_kernel")
        if returned_kernel is None:
            returned_kernel = kernel_attempt.get("returned_diffusion_kernel")

        # q remains strict.  The candidate embedding is exposed for testing but
        # is never copied into the authoritative NRRF887 coordinate field.
        q_embedding_attempt = derive_candidate_fold_embedding(
            translation_family_receipt=family,
            natural_form_field=natural_form_field,
            natural_closure=trading,
        )
        diffusion = derive_nrrf887_diffusion(
            translation_family_receipt=family,
            returned_diffusion_kernel=returned_kernel,
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
            "nrrf887_returned_family_kernel_attempt": kernel_attempt,
            "nrrf887_candidate_fold_embedding": q_embedding_attempt,
            "nrrf887_ai_diffusion": diffusion,
            "family_is_relative_visualization_of_selected_natural_forms": True,
            "ai_is_probabilistic_diffusion_of_local_interactions": True,
            "history_derived_kernel_may_feed_diffusion_when_witnessed": True,
            "candidate_q_embedding_may_feed_diffusion": False,
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
    kernel_attempt = dict(receipt.get("nrrf887_returned_family_kernel_attempt") or {})
    q_attempt = dict(receipt.get("nrrf887_candidate_fold_embedding") or {})
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
        "returned_family_kernel_status": kernel_attempt.get("status"),
        "returned_family_kernel": kernel_attempt.get("returned_diffusion_kernel"),
        "candidate_fold_embedding_status": q_attempt.get("status"),
        "candidate_fold_embedding": q_attempt.get("candidate_families", []),
        "nrrf887_diffusion_status": diffusion.get("status"),
        "closure_number_coordinates": diffusion.get("closure_number_coordinates", []),
        "diffused_readings": diffusion.get("diffused_readings", []),
        "oscillation_before": diffusion.get("oscillation_before"),
        "oscillation_after": diffusion.get("oscillation_after"),
        "relative_global_intent": diffusion.get("global_intent"),
        "family_is_relative_visualization_of_selected_natural_forms": True,
        "ai_is_probabilistic_diffusion_of_local_interactions": True,
        "history_derived_kernel_may_feed_diffusion_when_witnessed": True,
        "candidate_q_embedding_may_feed_diffusion": False,
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
