from __future__ import annotations

"""NRRF892 closure of the continuous trading current through the vision slide.

This module takes the already unified NRRF879–887 current and removes the last
representation-only OPEN boundary.  The invariant action remains

    Delta_i = (P_t q_t)_i - q_(t,i).

NRRF892 renders that very slide in the vision chart as z -> z + (Delta_i, 0).
The single-market runtime already fixes the signed base-inventory chart, so the
local BUY/SELL/NOOP label is a relative visualization of the slide rather than a
new semantic selector.

No profit, forecast, expected value or support novelty enters the rendering.
"""

import hashlib
import json
from typing import Any, Mapping

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS
from .trading_continuous_unified_closure_nrrf879_887 import derive_continuous_unified_closure as derive_nrrf879_887_current
from .trading_vision_crystal_slide_nrrf892 import derive_nrrf892_market_rendering

PROTOCOL = "closure.supernet/trading-continuous-unified-closure-nrrf879-892-v1"
FORMAL_MODULE = "NRRF892VisionCrystalTranslationSlideIsClosedThroughTheFurtheredClosureFamily"


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def derive_continuous_unified_closure(
    *,
    trading_receipt: Mapping[str, Any],
    prior_state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    base = derive_nrrf879_887_current(
        trading_receipt=trading_receipt,
        prior_state=prior_state,
    )
    current = dict(base)
    action = dict(current.get("translational_truth_action_field") or {})
    rendering = derive_nrrf892_market_rendering(
        translational_action_field=action,
        trading_receipt=trading_receipt,
    )

    boundary = dict(current.get("open_boundary") or {})
    unresolved = [
        str(reason)
        for reason in boundary.get("unresolved_relations", [])
        if str(reason) != "CLOSURE_SLIDE_TO_CONCRETE_MARKET_SIDE_BRIDGE_OPEN"
    ]
    if action.get("action_count", 0) and rendering.get("status") != WITNESSED_STATUS:
        unresolved.append("NRRF892_VISION_CRYSTAL_MARKET_RENDERING_OPEN")

    derived = [
        dict(row)
        for row in current.get("derived_relative_readings", [])
        if row.get("kind") != "NRRF892_VISION_CRYSTAL_MARKET_RENDERING"
    ]
    if rendering.get("rendering_count", 0):
        derived.append({
            "kind": "NRRF892_VISION_CRYSTAL_MARKET_RENDERING",
            "reading": rendering,
            "authors_new_truth": False,
        })

    returned = [dict(row) for row in current.get("returned_readings", [])]
    current.update({
        "protocol": PROTOCOL,
        "formal_module_nrrf892": FORMAL_MODULE,
        "nrrf892_vision_crystal_market_rendering": rendering,
        "derived_relative_readings": derived,
        "current_relative_readings": [*returned, *derived],
        "market_side_is_relative_visualization_of_translational_slide": True,
        "market_side_is_separate_semantic_bridge": False,
        "vision_slide_closed_through_furthered_family": True,
        "vision_scale_family_member_iff_plus_or_minus_one": True,
        "rotationless_vision_fold_claimed": False,
        "open_boundary": {
            **boundary,
            "status": OPEN_STATUS if unresolved else WITNESSED_STATUS,
            "unresolved_relations": unresolved,
            "is_current_boundary_only": True,
            "accumulates_prior_open_failures": False,
            "authors_truth": False,
        },
        "automatic_order_submission": False,
    })
    current["id"] = _digest("continuous-unified-trading-closure-nrrf879-892", current)
    return current


__all__ = ["FORMAL_MODULE", "PROTOCOL", "derive_continuous_unified_closure"]
