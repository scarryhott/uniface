from __future__ import annotations

"""NRRF892 vision-crystal rendering of the translational trading action.

The action field is already the unique NRRF886/887 slide

    Delta_i = (P q)_i - q_i.

NRRF892 closes that slide through the furthered closure family and gives its
vision-chart realization as the horizontal translation

    slideTrans t z = z + (t, 0).

The single-market temporal trading runtime already has a canonical signed base
inventory coordinate: BUY increases base inventory and SELL decreases it.
Therefore, in that canonical trading vision chart, the sign of the horizontal
slide is exactly the concrete market-side rendering:

    t > 0 -> BUY
    t < 0 -> SELL
    t = 0 -> NOOP.

BUY/SELL are chart-relative labels of one slide, not additional semantic truth.
A family change may change the chart rendering; the slide relation itself is the
invariant object.  NRRF892 also supplies the exact redenomination boundary:
visionScale c is itself in the furthered closure family iff c = +/-1.  This does
not contradict NRRF887 closure-number redenomination invariance; it limits when
the *vision scaling map itself* is a family member.

Python names the formal correspondence; it does not execute or re-prove Lean.
"""

from fractions import Fraction
import hashlib
import json
from typing import Any, Mapping

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

PROTOCOL = "closure.supernet/trading-vision-crystal-slide-nrrf892-v1"
FORMAL_MODULE = "NRRF892VisionCrystalTranslationSlideIsClosedThroughTheFurtheredClosureFamily"


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def _fraction(value: Any) -> Fraction | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return value if isinstance(value, Fraction) else Fraction(str(value).strip())
    except (ValueError, ZeroDivisionError, TypeError):
        return None


def _q(value: Fraction | None) -> str | None:
    if value is None:
        return None
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def derive_nrrf892_market_rendering(
    *,
    translational_action_field: Mapping[str, Any],
    trading_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    symbol = str(trading_receipt.get("symbol") or "")
    single_market = "/" in symbol and symbol.count("/") == 1
    base, quote = symbol.split("/", 1) if single_market else (None, None)

    rows: list[dict[str, Any]] = []
    unresolved: list[str] = []
    for raw in translational_action_field.get("actions", []):
        action = dict(raw)
        family_id = str(action.get("family_id") or "")
        delta = _fraction(action.get("unique_slide_amount"))
        failures: list[str] = []
        if action.get("status") != WITNESSED_STATUS:
            failures.append("TRANSLATIONAL_ACTION_OPEN")
        if delta is None:
            failures.append("UNIQUE_SLIDE_AMOUNT_OPEN")
        if not single_market:
            failures.append("CANONICAL_SINGLE_MARKET_VISION_CHART_OPEN")

        if failures:
            side = None
            side_status = OPEN_STATUS
            unresolved.append(family_id)
        elif delta > 0:
            side = "BUY"
            side_status = WITNESSED_STATUS
        elif delta < 0:
            side = "SELL"
            side_status = WITNESSED_STATUS
        else:
            side = "NOOP"
            side_status = WITNESSED_STATUS

        row = {
            "family_id": family_id,
            "closure_truth_id": action.get("closure_truth_id"),
            "status": WITNESSED_STATUS if not failures else OPEN_STATUS,
            "unique_slide_amount": _q(delta),
            "vision_slide_vector": [_q(delta), "0"] if delta is not None else None,
            "vision_slide_equation": "slideTrans t z = z + (t,0)",
            "market_side": side,
            "market_side_status": side_status,
            "market_side_is_canonical_chart_rendering_not_new_truth": True,
            "canonical_trading_vision_chart": {
                "x_axis": f"SIGNED_{base}_INVENTORY_TRANSLATION" if base else None,
                "positive_x": "BUY_INCREASES_BASE_INVENTORY" if base else None,
                "negative_x": "SELL_DECREASES_BASE_INVENTORY" if base else None,
                "y_axis": "VISION_ROTATION_COORDINATE",
            },
            "slide_is_closure_family_member": True,
            "slide_is_gravitational_ratio_one": True,
            "slide_group_zero_comp_inverse": True,
            "vision_crystal_is_slide_orbit": True,
            "slide_acts_simply_transitively_on_vision_crystal": True,
            "closure_family_conjugate_of_slide_is_translation": True,
            "family_chart_change_preserves_slide_relation": True,
            "buy_sell_label_is_chart_relative": True,
            "closure_number_action_redenomination_invariant": True,
            "vision_scale_is_family_member_iff_scale_is_pm_one": True,
            "arbitrary_vision_redenomination_is_family_member": False,
            "allowed_vision_family_scales": ["1", "-1"],
            "profit_used_to_render_market_side": False,
            "forecast_used_to_render_market_side": False,
            "unresolved": failures,
            "automatic_order_submission": False,
            "only_returned_execution_recloses": True,
        }
        row["rendering_id"] = _digest("nrrf892-market-rendering", row)
        rows.append(row)

    result = {
        "protocol": PROTOCOL,
        "formal_module": FORMAL_MODULE,
        "status": WITNESSED_STATUS if rows and not unresolved else OPEN_STATUS,
        "symbol": symbol or None,
        "base": base,
        "quote": quote,
        "renderings": rows,
        "rendering_count": len(rows),
        "unresolved_family_ids": unresolved,
        "vision_chart_defined_only_for_nonzero_rotation_folds": True,
        "rotationless_fold_claimed": False,
        "slide_closed_through_furthered_family": True,
        "market_side_is_relative_visualization_of_slide": True,
        "market_side_authors_truth": False,
        "profit_authors_market_side": False,
        "automatic_order_submission": False,
        "lean_kernel_executed_by_runtime": False,
        "runtime_reproves_lean": False,
    }
    result["id"] = _digest("trading-vision-crystal-slide-nrrf892", result)
    return result


__all__ = ["FORMAL_MODULE", "PROTOCOL", "derive_nrrf892_market_rendering"]
