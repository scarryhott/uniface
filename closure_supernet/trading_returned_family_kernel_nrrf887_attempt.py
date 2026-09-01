from __future__ import annotations

"""Attempt the remaining NRRF887 live bridge without inventing semantic data.

Two objects are deliberately separated.

1. ``derive_returned_family_kernel`` builds an exact-rational stochastic kernel
   only from chronological returned natural-form occurrences.  No profit,
   forecast, novelty, wall clock, or price direction enters the weights.
2. ``derive_candidate_fold_embedding`` probes a possible trading -> NRRF887
   coordinate map.  The candidate is

       q_candidate = closed curvature / total absolute natural edge variation.

   It is exact, positive-re-denomination invariant, lies in [-1,1], and has the
   zero-curvature locus at q=0.  It is NOT promoted to NRRF887 truth because no
   current Lean theorem identifies trading total variation with NRRF887 fold
   rotation or proves the required slide/Hodge correspondences.

Python does not execute or re-prove the Lean kernel.
"""

from fractions import Fraction
import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS

PROTOCOL = "closure.supernet/trading-returned-family-kernel-nrrf887-attempt-v1"


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


def _q(q: Fraction | None) -> str | None:
    if q is None:
        return None
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def derive_returned_family_kernel(
    *,
    translation_family_receipt: Mapping[str, Any],
    natural_form_field: Mapping[str, Any],
) -> dict[str, Any]:
    """Build P_ij from actually returned family-to-family temporal transitions."""

    families = [dict(x) for x in translation_family_receipt.get("families", [])]
    truth_to_family = {
        str(f.get("closure_truth_id")): str(f.get("family_id"))
        for f in families
        if f.get("closure_truth_id") and f.get("family_id")
    }
    family_ids = [str(f.get("family_id")) for f in families if f.get("family_id")]

    occurrences: list[str] = []
    unresolved_occurrences: list[str] = []
    for raw in natural_form_field.get("returned_natural_forms", []):
        row = dict(raw)
        if row.get("returned_truth_member") is not True:
            continue
        truth_id = str(row.get("closure_truth_id") or "")
        family_id = truth_to_family.get(truth_id)
        if family_id is None:
            unresolved_occurrences.append(str(row.get("form_id") or truth_id or "UNKNOWN"))
            continue
        occurrences.append(family_id)

    counts = {source: {target: 0 for target in family_ids} for source in family_ids}
    for source, target in zip(occurrences, occurrences[1:]):
        counts[source][target] += 1

    missing_outgoing = [source for source in family_ids if sum(counts[source].values()) == 0]
    ready = bool(family_ids) and len(occurrences) >= 2 and not unresolved_occurrences and not missing_outgoing

    matrix: list[list[str]] = []
    if ready:
        for source in family_ids:
            total = sum(counts[source].values())
            matrix.append([_q(Fraction(counts[source][target], total)) or "0" for target in family_ids])

    returned_kernel = {
        "returned": True,
        "locality_ids": family_ids,
        "matrix": matrix,
        "uses_future_profit": False,
        "uses_expected_profit": False,
        "uses_forecast": False,
        "uses_support_novelty": False,
        "uses_wall_clock": False,
        "weights_are_relative_frequencies_of_returned_transitions": True,
    } if ready else None

    body = {
        "protocol": PROTOCOL,
        "status": WITNESSED_STATUS if ready else OPEN_STATUS,
        "family_ids": family_ids,
        "returned_occurrence_sequence": occurrences,
        "returned_occurrence_count": len(occurrences),
        "transition_counts": counts,
        "unresolved_occurrences": unresolved_occurrences,
        "families_without_returned_outgoing_transition": missing_outgoing,
        "returned_diffusion_kernel": returned_kernel,
        "kernel_is_source_history_derived": True,
        "profit_authors_kernel": False,
        "forecast_authors_kernel": False,
        "novelty_authors_kernel": False,
        "absence_of_outgoing_evidence_creates_self_loop": False,
    }
    body["id"] = _digest("returned-family-kernel", body)
    return body


def derive_candidate_fold_embedding(
    *,
    translation_family_receipt: Mapping[str, Any],
    natural_form_field: Mapping[str, Any],
    natural_closure: Mapping[str, Any],
) -> dict[str, Any]:
    """Probe, but do not authorize, a trading closure-number embedding."""

    edge_values = {
        str(row.get("return_id")): _fraction(row.get("natural_form_value"))
        for row in natural_closure.get("sensor_returns", [])
        if row.get("return_id") and _fraction(row.get("natural_form_value")) is not None
    }
    forms_by_id = {
        str(row.get("form_id")): dict(row)
        for row in natural_form_field.get("returned_natural_forms", [])
        if row.get("form_id")
    }

    family_rows: list[dict[str, Any]] = []
    for raw_family in translation_family_receipt.get("families", []):
        family = dict(raw_family)
        candidates: list[Fraction] = []
        members: list[dict[str, Any]] = []
        for member_id in family.get("member_ids", []):
            form = forms_by_id.get(str(member_id), {})
            curvature = _fraction(form.get("unitary_curvature"))
            ids = [str(x) for x in form.get("return_ids", [])]
            natural_edges = [edge_values[x] for x in ids if x in edge_values]
            complete = bool(ids) and len(natural_edges) == len(ids) and curvature is not None
            rotation_candidate = sum((abs(x) for x in natural_edges), Fraction(0)) if complete else None
            q_candidate = (
                curvature / rotation_candidate
                if complete and rotation_candidate is not None and rotation_candidate > 0
                else None
            )
            if q_candidate is not None:
                candidates.append(q_candidate)
            members.append({
                "form_id": member_id,
                "curvature_extension_candidate": _q(curvature),
                "total_variation_rotation_candidate": _q(rotation_candidate),
                "closure_number_candidate": _q(q_candidate),
                "edge_evidence_complete": complete,
                "inside_unit_interval": abs(q_candidate) <= 1 if q_candidate is not None else None,
            })

        family_constant = bool(candidates) and len(candidates) == len(members) and all(q == candidates[0] for q in candidates[1:])
        family_rows.append({
            "family_id": family.get("family_id"),
            "closure_truth_id": family.get("closure_truth_id"),
            "members": members,
            "candidate_is_family_constant": family_constant,
            "family_closure_number_candidate": _q(candidates[0]) if family_constant else None,
            "semantic_status": OPEN_STATUS,
            "open_reason": "UNPROVED_TRADING_TO_NRRF887_FOLD_EMBEDDING",
        })

    body = {
        "protocol": PROTOCOL,
        "status": OPEN_STATUS,
        "candidate_families": family_rows,
        "candidate_equation": "q_candidate=unitary_curvature/sum(abs(returned_natural_edge_value))",
        "positive_redenomination_invariant_by_construction": True,
        "candidate_abs_q_le_one_by_triangle_inequality": True,
        "candidate_zero_when_curvature_zero": True,
        "nrrf887_slide_translation_law_proved_for_embedding": False,
        "nrrf887_hodge_inversion_law_proved_for_embedding": False,
        "candidate_authors_trading_truth": False,
        "candidate_feeds_authoritative_diffusion": False,
        "profit_used_as_input": False,
        "future_data_used": False,
        "required_next_theorem": "TRADING_NATURAL_FORM_TO_NRRF887_FOLD_PRESERVES_NATURAL_FORM_SLIDE_HODGE",
    }
    body["id"] = _digest("candidate-trading-fold-embedding", body)
    return body


__all__ = ["PROTOCOL", "derive_candidate_fold_embedding", "derive_returned_family_kernel"]
