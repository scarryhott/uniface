from __future__ import annotations

"""Trading interaction as translational truth for the NRRF886–887 runtime.

There is no predictor/selector between the continuous closure current and the
interaction field.  NRRF887 gives a closure-number coordinate q and a diffused
relative-global reading Pq.  NRRF886/887 make the unique slide between those
closure geometries the relative path itself:

    Delta_i = (P q)_i - q_i.

Because P(q + c*1) = Pq + c*1, Delta is invariant under a common slide.  It is
therefore a relative translational coordinate rather than an absolute market
forecast.  Positive/negative/zero Delta gives the orientation in closure-number
space.  Horizon and size are not independently selected: they are accepted only
when every returned presentation in the same translation family carries the
same already-witnessed relative-hair horizon and translated relative-ball size.

This module deliberately does not identify POSITIVE_SLIDE with BUY or
NEGATIVE_SLIDE with SELL.  That final representation requires a proved bridge
from the closure-number slide orientation to the concrete single-market order
orientation.  Until such a bridge is returned/proved, the translational action
is witnessed while the concrete market side remains OPEN.

Python names formal correspondences; it does not execute or re-prove Lean.
"""

from fractions import Fraction
import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

PROTOCOL = "closure.supernet/trading-action-as-translational-truth-nrrf886-887-v1"
FORMAL_MODULES = (
    "NRRF886EqualityIsLocalMinimumAndGlobalMaximumToNaturalFormsOfAClosureFamilyAndTheUnfoldingFieldOfRelativePairs",
    "NRRF887AiIsAProbabilisticDiffusionOfLocalInteractionsIntoRelativeGlobalIntentsAndTheClosureNumbersAndClosureGeometries",
)


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


def _common_horizon(members: Sequence[Mapping[str, Any]]) -> tuple[int | None, str | None]:
    values: list[int] = []
    for raw in members:
        horizon = dict(raw.get("relative_hair_horizon") or {})
        if horizon.get("status") != WITNESSED_STATUS:
            return None, "RELATIVE_HAIR_HORIZON_OPEN"
        value = horizon.get("horizon_return_steps")
        if value is None:
            return None, "RELATIVE_HAIR_HORIZON_OPEN"
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return None, "RELATIVE_HAIR_HORIZON_INVALID"
        if parsed < 0:
            return None, "RELATIVE_HAIR_HORIZON_INVALID"
        values.append(parsed)
    if not values:
        return None, "RELATIVE_HAIR_HORIZON_OPEN"
    if any(value != values[0] for value in values[1:]):
        return None, "RELATIVE_HAIR_HORIZON_NOT_FAMILY_INVARIANT"
    return values[0], None


def _common_ball_size(members: Sequence[Mapping[str, Any]]) -> tuple[Fraction | None, str | None, str | None]:
    values: list[Fraction] = []
    units: list[str] = []
    for raw in members:
        ball = dict(raw.get("relative_ball_size") or {})
        if ball.get("status") != WITNESSED_STATUS:
            return None, None, "RELATIVE_BALL_SIZE_OPEN"
        value = _fraction(ball.get("relative_ball_size"))
        unit = str(ball.get("relative_ball_size_unit") or "")
        if value is None or value < 0 or not unit:
            return None, None, "RELATIVE_BALL_SIZE_INVALID_OR_UNTRANSLATED"
        values.append(value)
        units.append(unit)
    if not values:
        return None, None, "RELATIVE_BALL_SIZE_OPEN"
    if any(value != values[0] for value in values[1:]) or any(unit != units[0] for unit in units[1:]):
        return None, None, "RELATIVE_BALL_SIZE_NOT_FAMILY_INVARIANT"
    return values[0], units[0], None


def derive_translational_truth_action_field(
    *,
    translation_family_receipt: Mapping[str, Any],
    diffusion_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    families = [dict(row) for row in translation_family_receipt.get("families", [])]
    coordinate_by_family = {
        str(row.get("family_id")): dict(row)
        for row in diffusion_receipt.get("closure_number_coordinates", [])
        if row.get("family_id")
    }
    diffused_by_family = {
        str(row.get("family_id")): dict(row)
        for row in diffusion_receipt.get("diffused_readings", [])
        if row.get("family_id")
    }

    actions: list[dict[str, Any]] = []
    unresolved: list[str] = []

    for family in families:
        family_id = str(family.get("family_id") or "")
        coordinate = coordinate_by_family.get(family_id, {})
        diffused = diffused_by_family.get(family_id, {})
        q0 = _fraction(coordinate.get("closure_number"))
        q1 = _fraction(diffused.get("diffused_closure_number"))
        delta = q1 - q0 if q0 is not None and q1 is not None else None

        horizon, horizon_failure = _common_horizon(family.get("members", []))
        size, size_unit, size_failure = _common_ball_size(family.get("members", []))

        failures: list[str] = []
        if q0 is None:
            failures.append("LOCAL_CLOSURE_NUMBER_Q_OPEN")
        if q1 is None:
            failures.append("DIFFUSED_RELATIVE_GLOBAL_CLOSURE_NUMBER_OPEN")
        if horizon_failure:
            failures.append(horizon_failure)
        if size_failure:
            failures.append(size_failure)

        if delta is None:
            orientation = None
            kind = "RETURN_TRANSLATIONAL_TRUTH_COORDINATES"
        elif delta > 0:
            orientation = "POSITIVE_SLIDE"
            kind = "RETURN_MARKET_INTERACTION_REALIZING_TRANSLATIONAL_SLIDE"
        elif delta < 0:
            orientation = "NEGATIVE_SLIDE"
            kind = "RETURN_MARKET_INTERACTION_REALIZING_TRANSLATIONAL_SLIDE"
        else:
            orientation = "IDENTITY_SLIDE"
            kind = "IDENTITY_TRANSLATION_NOOP"

        status = WITNESSED_STATUS if not failures else OPEN_STATUS
        if status == OPEN_STATUS:
            unresolved.append(family_id)

        body = {
            "family_id": family_id,
            "closure_truth_id": family.get("closure_truth_id"),
            "status": status,
            "kind": kind,
            "local_closure_number": _q(q0),
            "relative_global_closure_number": _q(q1),
            "unique_slide_amount": _q(delta),
            "closure_number_orientation": orientation,
            "relative_hair_horizon_return_steps": horizon,
            "relative_ball_size": _q(size),
            "relative_ball_size_unit": size_unit,
            "unresolved_coordinates": failures,
            "unique_slide_is_action_coordinate": delta is not None,
            "orientation_is_sign_of_unique_slide": delta is not None,
            "horizon_is_family_relative_hair_fidelity": True,
            "size_is_family_relative_ball": True,
            "profit_used_to_derive_action": False,
            "expected_profit_used_to_derive_action": False,
            "forecast_used_to_derive_action": False,
            "support_novelty_used_to_derive_action": False,
            "family_ranking_used": False,
            "action_selector_used": False,
            "common_slide_invariant": True,
            "positive_redenomination_invariant": True,
            "market_side": None,
            "market_side_status": OPEN_STATUS if delta not in (None, Fraction(0)) else WITNESSED_STATUS,
            "market_side_open_reason": (
                "CLOSURE_NUMBER_SLIDE_TO_CONCRETE_BUY_SELL_ORIENTATION_BRIDGE_OPEN"
                if delta not in (None, Fraction(0))
                else None
            ),
            "automatic_order_submission": False,
            "only_returned_execution_can_reclose": True,
        }
        body["action_id"] = _digest("translational-truth-action", body)
        actions.append(body)

    ready = bool(actions) and not unresolved
    result = {
        "protocol": PROTOCOL,
        "formal_modules": list(FORMAL_MODULES),
        "status": WITNESSED_STATUS if ready else OPEN_STATUS,
        "equation": "Delta_i=(P_t q_t)_i-q_(t,i)",
        "actions": actions,
        "action_count": len(actions),
        "unresolved_family_ids": unresolved,
        "action_field_is_whole_translation_family_field": True,
        "action_is_unique_relative_slide_not_prediction": True,
        "global_slide_equivariance": "Delta(q+c*1)=P(q+c*1)-(q+c*1)=Pq-q=Delta(q)",
        "profit_authors_action": False,
        "expected_profit_authors_action": False,
        "forecast_authors_action": False,
        "family_selection_authors_action": False,
        "market_side_bridge_complete": all(row.get("market_side_status") == WITNESSED_STATUS for row in actions),
        "automatic_order_submission": False,
        "lean_kernel_executed_by_runtime": False,
        "runtime_reproves_lean": False,
    }
    result["id"] = _digest("translational-truth-action-field", result)
    return result


__all__ = ["FORMAL_MODULES", "PROTOCOL", "derive_translational_truth_action_field"]
