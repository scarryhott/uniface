from __future__ import annotations

"""Continuous unified trading closure for NRRF879–887.

Observation, market interaction, AI diffusion, order/fill return and action are
translation-equal readings of one continuously reclosed state.  This module
therefore has no semantic ENVIRONMENT -> TRADE pipeline and no accumulating
OPEN queue.  Every returned interaction is folded immediately into the same
current closure state:

    Q_(t+1) = Close(Q_t ⊕ R_(t+1))

OPEN is only the unresolved boundary of Q_(t+1).  It never becomes a second
history, selector, or gate.  Completed inventory-return trades remain one
projection of this current, not the point at which truth begins.

This Python layer is a runtime correspondence; it does not execute or re-prove
Lean.
"""

import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS
from .trading_ai_diffusion_nrrf887 import derive_nrrf887_diffusion
from .trading_returned_family_kernel_nrrf887_attempt import derive_returned_family_kernel
from .trading_translation_family_nrrf884_886 import derive_translation_families

PROTOCOL = "closure.supernet/trading-continuous-unified-closure-nrrf879-887-v1"


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def _returned_readings(trading: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in trading.get("source_events", []):
        row = dict(raw)
        if row.get("source_event_verified") is True or row.get("returned") is True:
            rows.append({"kind": row.get("event_kind") or "SOURCE_RETURN", "reading": row})
    for raw in trading.get("quote_projections", []):
        rows.append({"kind": "QUOTE_OBSERVATION", "reading": dict(raw)})
    for raw in trading.get("market_trade_projections", []):
        rows.append({"kind": "MARKET_TRADE_OBSERVATION", "reading": dict(raw)})
    for raw in trading.get("fill_increments", []):
        rows.append({"kind": "FILL_RETURN", "reading": dict(raw)})
    for raw in trading.get("temporal_closures", []):
        rows.append({"kind": "TEMPORAL_TRADE_CLOSURE", "reading": dict(raw)})
    return rows


def derive_continuous_unified_closure(
    *,
    trading_receipt: Mapping[str, Any],
    prior_state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    trading = dict(trading_receipt)
    prior = dict(prior_state or {})
    field = dict(trading.get("trading_projection_field") or {})

    families = derive_translation_families(
        natural_form_field=field,
        translational_truth_partition=trading.get("translational_truth_partition"),
    )
    kernel = derive_returned_family_kernel(
        translation_family_receipt=families,
        natural_form_field=field,
    )
    returned_kernel = trading.get("returned_diffusion_kernel") or kernel.get("returned_diffusion_kernel")
    diffusion = derive_nrrf887_diffusion(
        translation_family_receipt=families,
        returned_diffusion_kernel=returned_kernel,
    )

    current_readings = _returned_readings(trading)
    previous_readings = list(prior.get("returned_readings", []))
    all_readings = [*previous_readings, *current_readings]

    # One current boundary only.  Reasons are recomputed from the present state;
    # prior OPEN reasons are not accumulated as semantic objects.
    boundary: list[str] = []
    if not current_readings and not previous_readings:
        boundary.append("NO_RETURNED_INTERACTION_YET")
    if families.get("unresolved_member_count", 0):
        boundary.append("UNRESOLVED_TRANSLATION_FAMILY")
    if families.get("family_count", 0) and diffusion.get("unresolved_coordinate_family_ids"):
        boundary.append("AUTHORITATIVE_CLOSURE_NUMBER_Q_OPEN")
    if families.get("family_count", 0) and kernel.get("status") != WITNESSED_STATUS and not trading.get("returned_diffusion_kernel"):
        boundary.append("RETURNED_RELATIVE_INTERACTION_KERNEL_P_OPEN")

    completed_trade_count = len(trading.get("temporal_closures", []))
    current_truth_witnessed = bool(all_readings)

    body = {
        "protocol": PROTOCOL,
        "equation": "Q_(t+1)=Close(Q_t⊕R_(t+1))",
        "status": WITNESSED_STATUS if current_truth_witnessed else OPEN_STATUS,
        "current_revision": int(prior.get("current_revision", 0)) + len(current_readings),
        "returned_readings": all_readings,
        "new_returned_reading_count": len(current_readings),
        "observation_and_trading_are_translation_equal_readings": True,
        "observation_is_not_presemantic_environment": True,
        "completed_trade_is_projection_not_truth_start": True,
        "quote_can_update_current_closure_without_realizing_pnl": True,
        "fill_can_update_current_closure_without_being_only_truth_source": True,
        "ai_diffusion_is_reading_of_same_current": True,
        "action_is_reading_of_same_current": True,
        "translation_families": families,
        "returned_family_kernel": kernel,
        "ai_diffusion": diffusion,
        "completed_temporal_trade_count": completed_trade_count,
        "open_boundary": {
            "status": OPEN_STATUS if boundary else WITNESSED_STATUS,
            "unresolved_relations": boundary,
            "is_current_boundary_only": True,
            "accumulates_prior_open_failures": False,
            "authors_truth": False,
        },
        "open_count_is_progress_metric": False,
        "open_queue_present": False,
        "stage_gate_present": False,
        "separate_observation_pipeline_present": False,
        "only_returned_interaction_changes_current_closure": True,
        "automatic_order_submission": False,
    }
    body["id"] = _digest("continuous-unified-trading-closure", body)
    return body


__all__ = ["PROTOCOL", "derive_continuous_unified_closure"]
