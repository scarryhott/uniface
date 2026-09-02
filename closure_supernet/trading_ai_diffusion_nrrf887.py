from __future__ import annotations

"""NRRF887 closure-number geometry and AI diffusion runtime correspondence.

This layer starts only after NRRF884–886 has identified translation families.
It does not infer closure numbers from profit, labels, novelty, or market trend.
A closure number is accepted only when returned explicitly or when exact
extension/rotation coordinates are available.  Diffusion is accepted only from
an explicit returned finite stochastic kernel.

Python names the NRRF887 correspondence; it does not execute or re-prove Lean.
"""

from fractions import Fraction
import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

PROTOCOL = "closure.supernet/trading-ai-diffusion-nrrf887-v1"
FORMAL_MODULE = "NRRF887AiIsAProbabilisticDiffusionOfLocalInteractionsIntoRelativeGlobalIntentsAndTheClosureNumbersAndClosureGeometries"


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def _fraction(value: Any) -> Fraction | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        if isinstance(value, Fraction):
            return value
        if isinstance(value, int):
            return Fraction(value)
        if isinstance(value, str):
            return Fraction(value.strip())
        return Fraction(str(value))
    except (ValueError, ZeroDivisionError, TypeError):
        return None


def _q_string(q: Fraction | None) -> str | None:
    if q is None:
        return None
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def _family_closure_number(family: Mapping[str, Any]) -> tuple[Fraction | None, str]:
    centre = dict(family.get("natural_form_centre") or {})
    explicit = _fraction(centre.get("closure_number"))
    if explicit is not None:
        return explicit, "RETURNED_CLOSURE_NUMBER"

    extension = _fraction(centre.get("extension"))
    rotation = _fraction(centre.get("rotation"))
    if extension is not None and rotation is not None and rotation != 0:
        return extension / rotation, "DERIVED_EXTENSION_PER_ROTATION"

    member_values: list[Fraction] = []
    for raw in family.get("members", []):
        member = dict(raw)
        q = _fraction(member.get("closure_number"))
        if q is None:
            ext = _fraction(member.get("extension"))
            rot = _fraction(member.get("rotation"))
            q = ext / rot if ext is not None and rot not in (None, 0) else None
        if q is not None:
            member_values.append(q)
    if member_values and all(q == member_values[0] for q in member_values[1:]):
        return member_values[0], "COMMON_RETURNED_MEMBER_CLOSURE_NUMBER"
    return None, "OPEN_NO_CLOSURE_NUMBER_COORDINATE"


def _coordinates(families: Sequence[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    unresolved: list[str] = []
    for raw in families:
        family = dict(raw)
        family_id = str(family.get("family_id") or family.get("closure_truth_id") or "")
        q, provenance = _family_closure_number(family)
        if q is None:
            unresolved.append(family_id)
        rows.append({
            "family_id": family_id,
            "closure_truth_id": family.get("closure_truth_id"),
            "status": WITNESSED_STATUS if q is not None else OPEN_STATUS,
            "closure_number": _q_string(q),
            "closure_number_provenance": provenance,
            "kakeya_zero": q == 0 if q is not None else None,
            "ball_hair_closed": abs(q) <= 1 if q is not None else None,
            "profit_authors_closure_number": False,
            "novelty_authors_closure_number": False,
        })
    return rows, unresolved


def _parse_kernel(
    kernel: Mapping[str, Any] | None,
    family_ids: Sequence[str],
) -> tuple[list[list[Fraction]] | None, list[str]]:
    if not kernel:
        return None, ["NO_RETURNED_DIFFUSION_KERNEL"]
    failures: list[str] = []
    if kernel.get("returned") is not True:
        failures.append("KERNEL_NOT_RETURNED")
    if kernel.get("uses_future_profit") is True or kernel.get("uses_expected_profit") is True or kernel.get("uses_forecast") is True:
        failures.append("KERNEL_SMUGGLES_PROFIT_OR_FORECAST")

    locality_ids = [str(x) for x in kernel.get("locality_ids", [])]
    if locality_ids != list(family_ids):
        failures.append("KERNEL_LOCALITIES_DO_NOT_MATCH_FAMILIES")
    raw_matrix = kernel.get("matrix")
    if not isinstance(raw_matrix, list) or len(raw_matrix) != len(family_ids):
        failures.append("KERNEL_DIMENSION_MISMATCH")
        return None, failures

    matrix: list[list[Fraction]] = []
    for row in raw_matrix:
        if not isinstance(row, list) or len(row) != len(family_ids):
            failures.append("KERNEL_DIMENSION_MISMATCH")
            return None, failures
        parsed = [_fraction(x) for x in row]
        if any(x is None for x in parsed):
            failures.append("KERNEL_NON_RATIONAL_ENTRY")
            return None, failures
        exact = [x for x in parsed if x is not None]
        if any(x < 0 for x in exact):
            failures.append("KERNEL_NEGATIVE_ENTRY")
        if sum(exact, Fraction(0)) != 1:
            failures.append("KERNEL_ROW_NOT_STOCHASTIC")
        matrix.append(exact)
    return (matrix if not failures else None), failures


def _oscillation(values: Sequence[Fraction]) -> Fraction:
    return max(values) - min(values) if values else Fraction(0)


def _diffuse(matrix: Sequence[Sequence[Fraction]], values: Sequence[Fraction]) -> list[Fraction]:
    return [sum((w * q for w, q in zip(row, values)), Fraction(0)) for row in matrix]


def derive_nrrf887_diffusion(
    *,
    translation_family_receipt: Mapping[str, Any],
    returned_diffusion_kernel: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    families = [dict(x) for x in translation_family_receipt.get("families", [])]
    coordinates, unresolved = _coordinates(families)
    family_ids = [str(row["family_id"]) for row in coordinates]
    matrix, kernel_failures = _parse_kernel(returned_diffusion_kernel, family_ids)

    q_values = [_fraction(row.get("closure_number")) for row in coordinates]
    coordinate_ready = bool(coordinates) and not unresolved and all(q is not None for q in q_values)
    values = [q for q in q_values if q is not None]
    ready = coordinate_ready and matrix is not None and not kernel_failures

    before_osc = _oscillation(values) if coordinate_ready else None
    after: list[Fraction] = _diffuse(matrix, values) if ready and matrix is not None else []
    after_osc = _oscillation(after) if after else None

    diffused = []
    if ready:
        lo, hi = min(values), max(values)
        for family_id, q0, q1 in zip(family_ids, values, after):
            diffused.append({
                "family_id": family_id,
                "before_closure_number": _q_string(q0),
                "diffused_closure_number": _q_string(q1),
                "inside_returned_range": lo <= q1 <= hi,
                "ball_hair_closed_after_diffusion": abs(q1) <= 1,
                "diffused_reading_is_definite_closure_geometry": True,
            })

    constant_before = bool(values) and all(q == values[0] for q in values[1:])
    constant_after = bool(after) and all(q == after[0] for q in after[1:])
    body = {
        "protocol": PROTOCOL,
        "formal_module": FORMAL_MODULE,
        "status": WITNESSED_STATUS if ready else OPEN_STATUS,
        "closure_number_coordinates": coordinates,
        "coordinate_count": len(coordinates),
        "unresolved_coordinate_family_ids": unresolved,
        "returned_diffusion_kernel_present": bool(returned_diffusion_kernel),
        "kernel_failures": kernel_failures,
        "diffused_readings": diffused,
        "oscillation_before": _q_string(before_osc),
        "oscillation_after": _q_string(after_osc),
        "oscillation_nonincreasing": (after_osc <= before_osc) if ready and after_osc is not None and before_osc is not None else None,
        "constant_reading_fixed": (constant_before and constant_after and values == after) if ready else None,
        "closure_preserved_if_all_local_closed": (
            all(abs(q) <= 1 for q in after) if ready and all(abs(q) <= 1 for q in values) else None
        ),
        "global_intent": {
            "status": WITNESSED_STATUS if ready and constant_after else OPEN_STATUS,
            "closure_number": _q_string(after[0]) if ready and constant_after else None,
            "actual_limit_claimed": False,
            "consensus_after_this_returned_step": constant_after if ready else None,
        },
        "slide_translation_equivariance_is_formal_correspondence": True,
        "closure_geometry_level_sets_are_natural_forms": True,
        "kakeya_is_zero": True,
        "hodge_is_inverse": True,
        "slide_is_translation": True,
        "ball_hair_closed_iff_abs_q_le_one": True,
        "profit_authors_diffusion": False,
        "forecast_authors_diffusion": False,
        "support_novelty_authors_diffusion": False,
        "diffusion_authors_trading_truth": False,
        "only_returned_interaction_recloses_trading_truth": True,
        "automatic_order_submission": False,
        "lean_kernel_executed_by_runtime": False,
        "runtime_reproves_lean": False,
    }
    body["id"] = _digest("trading-ai-diffusion-nrrf887", body)
    return body


__all__ = ["FORMAL_MODULE", "PROTOCOL", "derive_nrrf887_diffusion"]
