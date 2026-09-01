from __future__ import annotations

"""Live Alpaca surface constrained to the NRRF879–881 runtime correspondence."""

import argparse
import json
import time
from typing import Any, Mapping

from .alpaca_live_closure import AlpacaLiveClosureAdapter, AlpacaLiveConfig
from .trading_nrrf879_881_runtime_bridge import derive_nrrf879_881_runtime_bridge

PROTOCOL = "closure.supernet/alpaca-nrrf879-881-live-v1"


class AlpacaNRRF879881Runtime:
    def __init__(self, adapter: AlpacaLiveClosureAdapter):
        self.adapter = adapter

    def resolve_once(self) -> dict[str, Any]:
        source_receipt = self.adapter.resolve_once()
        trading = dict(source_receipt.get("trading") or {})
        bridge = derive_nrrf879_881_runtime_bridge(
            temporal_trading_receipt=trading,
        )
        return {
            "protocol": PROTOCOL,
            "status": trading.get("status") if bridge["anti_smuggling_audit"]["valid"] else "OPEN",
            "trading": trading,
            "nrrf879_881_runtime": bridge,
            "automatic_order_submission": False,
            "runtime_semantic_author_present": bridge["anti_smuggling_audit"]["runtime_semantic_author_present"],
        }


def compact_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    bridge = dict(receipt.get("nrrf879_881_runtime") or {})
    trading = dict(receipt.get("trading") or {})
    return {
        "protocol": PROTOCOL,
        "status": receipt.get("status"),
        "symbol": bridge.get("symbol"),
        "temporal_closure_count": trading.get("temporal_closure_count"),
        "current_net_profit_truth_witnessed": trading.get("current_net_profit_truth_witnessed"),
        "anti_smuggling_audit": bridge.get("anti_smuggling_audit"),
        "formal_correspondence": bridge.get("formal_correspondence"),
        "market_state": bridge.get("market_state"),
        "account_state": bridge.get("account_state"),
        "closure_ball_ui": bridge.get("closure_ball_ui"),
        "open_or_selected_interactions": bridge.get("open_or_selected_interactions", []),
        "automatic_order_submission": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Alpaca through the NRRF879-881 formal runtime bridge")
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
