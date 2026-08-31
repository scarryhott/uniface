from __future__ import annotations

"""Derived pre-action horizon and size for the unified trading natural form.

There is no externally fixed semantic horizon and no externally authored trade
size in this layer.

For a returned natural form N:

    horizon(N) = exact empirical persistence depth of the relative hair / truth
                 class into later executable returned closures;

    size(N)    = bottleneck translated capacity of the returned relative ball.

Hair fidelity is measured only through exact translational-truth equality.  No
epsilon, score threshold, trend, forecast, or similarity rule is introduced.
The fidelity profile at lag h asks whether an occurrence of the current truth
class at frame t is returned as the same truth class at an executable frame
t+h.  The derived horizon is the longest contiguous lag prefix with perfect
observed fidelity.  If there is no executable comparison, horizon remains OPEN.

Ball size is only derived when every leg of the returned closed itinerary carries
an explicitly translated relative capacity in one common unit.  Raw venue quote
sizes in incomparable asset units are not silently combined.  If translated
capacity is missing, size remains OPEN.
"""

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS
from .trading_natural_form_closure import resolve_open_sensor_trading_closure

PROTOCOL = "closure.supernet/trading-relative-hair-horizon-ball-size-v1"


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return result if result.is_finite() else None


def _text(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def _return_id(row: Mapping[str, Any], index: int) -> str:
    return str(row.get("return_id") or row.get("id") or f"sensor-return-{index}")


def _relation_signature(form: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    return tuple(
        (str(row.get("source_token") or ""), str(row.get("target_token") or ""))
        for row in form.get("directed_relation_signature", [])
    )


def _executable(form: Mapping[str, Any]) -> bool:
    trade = dict(form.get("trade_projection") or {})
    return (
        form.get("status") == WITNESSED_STATUS
        and trade.get("execution_return_status") == WITNESSED_STATUS
    )


def _frame_forms(
    *,
    observer_id: str | None,
    frame: Sequence[Mapping[str, Any]],
    max_returns: int | None,
) -> list[dict[str, Any]]:
    closure = resolve_open_sensor_trading_closure(
        observer_id=observer_id,
        sensor_feedback=frame,
        max_returns=max_returns,
    )
    return [
        dict(form)
        for form in closure.get("natural_forms", [])
        if form.get("status") == WITNESSED_STATUS
    ]


def derive_relative_hair_horizon(
    *,
    current_form: Mapping[str, Any],
    observer_id: str | None,
    sensor_history: Sequence[Sequence[Mapping[str, Any]]],
    max_returns: int | None = None,
) -> dict[str, Any]:
    """Derive horizon from exact hair/TT fidelity to later executable closure."""

    current_id = str(current_form.get("closure_truth_id") or current_form.get("closure_id") or "")
    signature = _relation_signature(current_form)
    if not current_id or not signature or len(sensor_history) < 2:
        return {
            "status": OPEN_STATUS,
            "relative_hair_fidelity": None,
            "horizon_return_steps": None,
            "fidelity_profile": [],
            "open_reason": "INSUFFICIENT_RETURNED_HISTORY_FOR_RELATIVE_HAIR_FIDELITY",
            "fixed_horizon": None,
            "fixed_horizon_authors_truth": False,
            "derived_from_exact_translational_truth": True,
        }

    frames = [
        _frame_forms(
            observer_id=observer_id,
            frame=frame,
            max_returns=max_returns,
        )
        for frame in sensor_history
    ]
    by_frame: list[dict[tuple[tuple[str, str], ...], list[dict[str, Any]]]] = []
    for forms in frames:
        grouped: dict[tuple[tuple[str, str], ...], list[dict[str, Any]]] = {}
        for form in forms:
            grouped.setdefault(_relation_signature(form), []).append(form)
        by_frame.append(grouped)

    profile: list[dict[str, Any]] = []
    horizon = 0
    any_comparison = False
    perfect_prefix = True
    for lag in range(1, len(by_frame)):
        comparable = 0
        same_truth = 0
        for left_index in range(0, len(by_frame) - lag):
            left_forms = by_frame[left_index].get(signature, [])
            if not any(
                str(form.get("closure_truth_id") or form.get("closure_id") or "") == current_id
                for form in left_forms
            ):
                continue
            right_forms = [
                form
                for form in by_frame[left_index + lag].get(signature, [])
                if _executable(form)
            ]
            if not right_forms:
                continue
            comparable += 1
            if any(
                str(form.get("closure_truth_id") or form.get("closure_id") or "") == current_id
                for form in right_forms
            ):
                same_truth += 1
        fidelity = None if comparable == 0 else same_truth / comparable
        profile.append(
            {
                "lag_return_steps": lag,
                "comparable_occurrences": comparable,
                "same_truth_occurrences": same_truth,
                "relative_hair_fidelity": fidelity,
                "perfect_exact_fidelity": bool(comparable and same_truth == comparable),
            }
        )
        if comparable:
            any_comparison = True
            if perfect_prefix and same_truth == comparable:
                horizon = lag
            else:
                perfect_prefix = False

    if not any_comparison:
        return {
            "status": OPEN_STATUS,
            "relative_hair_fidelity": None,
            "horizon_return_steps": None,
            "fidelity_profile": profile,
            "open_reason": "NO_LATER_EXECUTABLE_CLOSURE_COMPARISON",
            "fixed_horizon": None,
            "fixed_horizon_authors_truth": False,
            "derived_from_exact_translational_truth": True,
        }

    lag_one = next(
        (row for row in profile if row["lag_return_steps"] == 1 and row["comparable_occurrences"]),
        None,
    )
    return {
        "status": WITNESSED_STATUS,
        "relative_hair_fidelity": (
            lag_one["relative_hair_fidelity"] if lag_one is not None else None
        ),
        "horizon_return_steps": horizon,
        "fidelity_profile": profile,
        "zero_horizon": horizon == 0,
        "fixed_horizon": None,
        "fixed_horizon_authors_truth": False,
        "horizon_is_derived_from_relative_hair_fidelity": True,
        "derived_from_exact_translational_truth": True,
        "similarity_tolerance_used": False,
    }


def derive_relative_ball_size(
    *,
    current_form: Mapping[str, Any],
    current_feedback: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Derive relative ball size as returned-cycle bottleneck capacity."""

    raw_by_id = {
        _return_id(row, index): dict(row)
        for index, row in enumerate(current_feedback)
    }
    return_ids = [str(value) for value in current_form.get("return_ids", [])]
    capacities: list[tuple[str, Decimal, str]] = []
    missing: list[str] = []
    for return_id in return_ids:
        row = raw_by_id.get(return_id)
        if row is None:
            missing.append(return_id)
            continue
        raw_value = None
        for key in (
            "relative_ball_size",
            "relative_size",
            "executable_relative_size",
            "relative_capacity",
            "translated_size",
        ):
            if row.get(key) is not None:
                raw_value = row.get(key)
                break
        value = _decimal(raw_value)
        unit = str(row.get("relative_size_unit") or row.get("capacity_unit") or "")
        if value is None or value < 0 or not unit:
            missing.append(return_id)
            continue
        capacities.append((return_id, value, unit))

    units = {unit for _, _, unit in capacities}
    if missing or len(capacities) != len(return_ids) or len(units) != 1:
        return {
            "status": OPEN_STATUS,
            "relative_ball_size": None,
            "unit": next(iter(units)) if len(units) == 1 else None,
            "missing_or_incomparable_return_ids": missing,
            "open_reason": (
                "RELATIVE_BALL_CAPACITY_MUST_BE_RETURNED_IN_ONE_TRANSLATED_UNIT"
            ),
            "raw_quote_size_is_not_silently_a_relative_ball_size": True,
            "external_position_size_authors_action": False,
        }

    bottleneck_id, bottleneck, unit = min(capacities, key=lambda item: item[1])
    return {
        "status": WITNESSED_STATUS,
        "relative_ball_size": _text(bottleneck),
        "unit": unit,
        "bottleneck_return_id": bottleneck_id,
        "leg_capacities": [
            {"return_id": return_id, "relative_capacity": _text(value), "unit": edge_unit}
            for return_id, value, edge_unit in capacities
        ],
        "size_is_relative_ball_bottleneck": True,
        "external_position_size_authors_action": False,
    }


def derive_preaction_relative_coordinates(
    *,
    observer_id: str | None,
    natural_closure: Mapping[str, Any],
    current_feedback: Sequence[Mapping[str, Any]],
    sensor_history: Sequence[Sequence[Mapping[str, Any]]] = (),
    max_returns: int | None = None,
) -> dict[str, Any]:
    """Derive horizon and size for every returned natural form before action."""

    by_closure_id: dict[str, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    for raw in natural_closure.get("natural_forms", []):
        form = dict(raw)
        closure_id = str(form.get("closure_id") or form.get("closure_truth_id") or "")
        if not closure_id:
            continue
        horizon = derive_relative_hair_horizon(
            current_form=form,
            observer_id=observer_id,
            sensor_history=sensor_history,
            max_returns=max_returns,
        )
        size = derive_relative_ball_size(
            current_form=form,
            current_feedback=current_feedback,
        )
        coordinates = {
            "closure_id": closure_id,
            "relative_hair_horizon": horizon,
            "relative_ball_size": size,
            "horizon_from_relative_hair_fidelity": True,
            "size_from_relative_ball": True,
            "derived_before_action": True,
        }
        by_closure_id[closure_id] = coordinates
        rows.append(coordinates)

    return {
        "protocol": PROTOCOL,
        "equation": (
            "H(N)=exact relative-hair fidelity depth into later executable closure; "
            "Size(N)=bottleneck translated capacity of the relative ball"
        ),
        "forms": rows,
        "by_closure_id": by_closure_id,
        "horizon_from_relative_hair_fidelity": True,
        "size_from_relative_ball": True,
        "fixed_horizon_present": False,
        "external_position_size_present": False,
        "derived_before_action": True,
    }


__all__ = [
    "PROTOCOL",
    "derive_preaction_relative_coordinates",
    "derive_relative_ball_size",
    "derive_relative_hair_horizon",
]
