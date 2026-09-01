from __future__ import annotations

"""NRRF892 closure of the continuous trading current through the vision slide.

This module takes the already unified NRRF879–887 current and removes the last
representation-only OPEN boundary.  The invariant action remains

    Delta_i = (P_t q_t)_i - q_(t,i).

NRRF892 renders that very slide in the vision chart as z -> z + (Delta_i, 0).
The single-market runtime already fixes the signed base-inventory chart, so the
local BUY/SELL/NOOP label is a relative visualization of the slide rather than a
new semantic selector.

The live interaction integral then measures the naturally persisting relation:
formal exact TT horizon stays the already-derived relative-hair horizon, while a
separate weaker vision horizon counts causal quote returns for which the market
rendering persists.  Gross price curvature and spread lower-bound friction are
diagnostics only.  Actual profit remains the returned cost-complete temporal
inventory closure.
"""

import hashlib
import json
from typing import Any, Mapping

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS
from .trading_continuous_unified_closure_nrrf879_887 import derive_continuous_unified_closure as derive_nrrf879_887_current
from .trading_live_interaction_integration_nrrf892 import derive_live_interaction_integration
from .trading_vision_crystal_slide_nrrf892 import derive_nrrf892_market_rendering

PROTOCOL = "closure.supernet/trading-continuous-unified-closure-nrrf879-892-v2-live-interaction"
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
    prior = dict(prior_state or {})
    base = derive_nrrf879_887_current(
        trading_receipt=trading_receipt,
        prior_state=prior,
    )
    current = dict(base)
    action = dict(current.get("translational_truth_action_field") or {})
    rendering = derive_nrrf892_market_rendering(
        translational_action_field=action,
        trading_receipt=trading_receipt,
    )
    live_integration = derive_live_interaction_integration(
        trading_receipt=trading_receipt,
        continuous_current=current,
        nrrf892_rendering=rendering,
        prior_integration=prior.get("live_interaction_integration"),
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
        if row.get("kind") not in {
            "NRRF892_VISION_CRYSTAL_MARKET_RENDERING",
            "LIVE_INTERACTION_INTEGRATION_NRRF892",
        }
    ]
    if rendering.get("rendering_count", 0):
        derived.append({
            "kind": "NRRF892_VISION_CRYSTAL_MARKET_RENDERING",
            "reading": rendering,
            "authors_new_truth": False,
        })
    if live_integration.get("family_integrations"):
        derived.append({
            "kind": "LIVE_INTERACTION_INTEGRATION_NRRF892",
            "reading": live_integration,
            "authors_new_truth": False,
        })

    returned = [dict(row) for row in current.get("returned_readings", [])]
    current.update({
        "protocol": PROTOCOL,
        "formal_module_nrrf892": FORMAL_MODULE,
        "nrrf892_vision_crystal_market_rendering": rendering,
        "live_interaction_integration": live_integration,
        "live_interaction_profit_function": live_integration.get("live_profit_function"),
        "derived_relative_readings": derived,
        "current_relative_readings": [*returned, *derived],
        "market_side_is_relative_visualization_of_translational_slide": True,
        "market_side_is_separate_semantic_bridge": False,
        "vision_slide_closed_through_furthered_family": True,
        "vision_scale_family_member_iff_plus_or_minus_one": True,
        "rotationless_vision_fold_claimed": False,
        "formal_horizon_and_vision_horizon_are_kept_distinct": True,
        "fixed_holding_period_used_for_live_profit_function": False,
        "live_interaction_diagnostic_authors_action": False,
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
