from __future__ import annotations

"""Interactive trading architecture for the NRRF879–887 stack.

This module does not create a new trading strategy.  It makes the closure loop
explicit and fail-OPEN at every boundary where the returned data is not enough:

    environment -> verified return -> temporal closure -> translation family
    -> closure number -> returned family kernel -> diffusion -> interaction
    proposal -> new verified return -> reclosure

Only verified returned market/account events may change trading truth.  Public
quotes/trades can populate the environment and OPEN boundary but cannot stand in
for account fills, inventory return, returned fees, or the NRRF887 fold
extension/rotation coordinate.
"""

import hashlib
import json
from typing import Any, Mapping

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS
from .trading_ai_diffusion_nrrf887 import derive_nrrf887_diffusion
from .trading_returned_family_kernel_nrrf887_attempt import (
    derive_candidate_fold_embedding,
    derive_returned_family_kernel,
)
from .trading_translation_family_nrrf884_886 import derive_translation_families

PROTOCOL = "closure.supernet/trading-interactive-architecture-nrrf879-887-v1"


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def derive_interactive_trading_architecture(*, trading_receipt: Mapping[str, Any]) -> dict[str, Any]:
    trading = dict(trading_receipt)
    field = dict(trading.get("trading_projection_field") or {})
    families = derive_translation_families(
        natural_form_field=field,
        translational_truth_partition=trading.get("translational_truth_partition"),
    )
    kernel_attempt = derive_returned_family_kernel(
        translation_family_receipt=families,
        natural_form_field=field,
    )
    candidate_q = derive_candidate_fold_embedding(
        translation_family_receipt=families,
        natural_form_field=field,
        natural_closure=trading,
    )
    diffusion = derive_nrrf887_diffusion(
        translation_family_receipt=families,
        returned_diffusion_kernel=(
            trading.get("returned_diffusion_kernel")
            or kernel_attempt.get("returned_diffusion_kernel")
        ),
    )

    temporal_closures = list(trading.get("temporal_closures", []))
    verified_return_ready = bool(trading.get("source_event_ids"))
    temporal_closure_ready = bool(temporal_closures)
    family_ready = families.get("status") == WITNESSED_STATUS
    q_ready = bool(diffusion.get("closure_number_coordinates")) and not diffusion.get("unresolved_coordinate_family_ids")
    kernel_ready = kernel_attempt.get("status") == WITNESSED_STATUS or bool(trading.get("returned_diffusion_kernel"))
    diffusion_ready = diffusion.get("status") == WITNESSED_STATUS

    # The final action law is deliberately not guessed.  Even a witnessed Pq is
    # a natural-form/AI state; a separate theorem must identify its trading
    # interaction projection.  Until then the architecture emits one OPEN
    # interaction request instead of a buy/sell instruction.
    if diffusion_ready:
        interaction = {
            "status": OPEN_STATUS,
            "kind": "RETURN_INTERACTION_OF_DIFFUSED_CLOSURE_GEOMETRY",
            "requires_new_verified_return": True,
            "automatic_order_submission": False,
            "buy_or_sell_invented": False,
            "profit_target_invented": False,
            "open_reason": "UNPROVED_DIFFUSED_CLOSURE_GEOMETRY_TO_TRADING_ACTION_PROJECTION",
        }
    else:
        missing = []
        if not verified_return_ready:
            missing.append("VERIFIED_ACCOUNT_RETURN")
        if not temporal_closure_ready:
            missing.append("TEMPORAL_INVENTORY_RETURN")
        if not family_ready:
            missing.append("TRANSLATION_FAMILY")
        if not q_ready:
            missing.append("AUTHORITATIVE_CLOSURE_NUMBER_Q")
        if not kernel_ready:
            missing.append("RETURNED_FAMILY_KERNEL_P")
        interaction = {
            "status": OPEN_STATUS,
            "kind": "RETURN_MISSING_INTERACTIVE_CLOSURE_DATA",
            "missing": missing,
            "requires_new_verified_return": True,
            "automatic_order_submission": False,
            "buy_or_sell_invented": False,
        }

    stages = [
        {"stage": "ENVIRONMENT", "status": WITNESSED_STATUS if trading.get("symbol") else OPEN_STATUS,
         "truth_authority": False},
        {"stage": "VERIFIED_RETURN", "status": WITNESSED_STATUS if verified_return_ready else OPEN_STATUS,
         "truth_authority": True},
        {"stage": "TEMPORAL_CLOSURE", "status": WITNESSED_STATUS if temporal_closure_ready else OPEN_STATUS,
         "truth_authority": True},
        {"stage": "TRANSLATION_FAMILY", "status": WITNESSED_STATUS if family_ready else OPEN_STATUS,
         "truth_authority": True},
        {"stage": "CLOSURE_NUMBER_Q", "status": WITNESSED_STATUS if q_ready else OPEN_STATUS,
         "truth_authority": True},
        {"stage": "RETURNED_KERNEL_P", "status": WITNESSED_STATUS if kernel_ready else OPEN_STATUS,
         "truth_authority": False},
        {"stage": "AI_DIFFUSION_PQ", "status": WITNESSED_STATUS if diffusion_ready else OPEN_STATUS,
         "truth_authority": False},
        {"stage": "INTERACTION_PROJECTION", "status": OPEN_STATUS,
         "truth_authority": False},
    ]

    body = {
        "protocol": PROTOCOL,
        "equation": "R_t -> N_t -> [N_t]_TT -> q_t -> P_t q_t -> OPEN interaction -> R_(t+1) -> reclosure",
        "status": OPEN_STATUS,
        "stages": stages,
        "translation_families": families,
        "returned_family_kernel_attempt": kernel_attempt,
        "candidate_fold_embedding": candidate_q,
        "nrrf887_diffusion": diffusion,
        "interaction_projection": interaction,
        "public_quote_or_trade_can_author_inventory_return": False,
        "public_quote_or_trade_can_author_returned_fee": False,
        "public_quote_or_trade_can_author_closure_number": False,
        "candidate_q_authors_truth": False,
        "kernel_uses_future_profit": False,
        "automatic_order_submission": False,
        "only_new_verified_return_recloses": True,
    }
    body["id"] = _digest("trading-interactive-architecture-nrrf879-887", body)
    return body


__all__ = ["PROTOCOL", "derive_interactive_trading_architecture"]
