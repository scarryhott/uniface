from __future__ import annotations

"""Translational-truth-only learning for the NRRF870 trading runtime.

There is no second dynamics law. Every returned sensor frame is closed by the
authoritative open-sensor kernel and the resulting normalized natural forms are
quotiented by translational truth.

Two returned local balls are one semantic ball exactly when their normalized
natural forms / closure truths are equal. Distinct raw presentations inside one
class are hair presentations, not new truths. Distinct natural forms are not
silently connected by a trend, tolerance, forecast, or learned transition law:
they remain distinct translational truths until a returned interaction itself
witnesses equality.

"Learning" therefore means only refinement of the translational-truth quotient:
- a returned member of an already witnessed class is the same truth through hair;
- a new normalized natural form witnesses a new truth class;
- an OPEN frame contributes no synthetic truth;
- profit is learned only when an actually returned truth class itself has
  positive natural profit (equivalently negative unitary curvature).
"""

from collections import defaultdict
from decimal import Decimal, InvalidOperation
import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS
from .trading_natural_form_closure import resolve_open_sensor_trading_closure

PROTOCOL = "closure.supernet/trading-translational-truth-alone-v2"


def _stable(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode()).hexdigest()[:24]}"


def _relation_signature(form: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    return tuple(
        (str(row.get("source_token")), str(row.get("target_token")))
        for row in form.get("directed_relation_signature", [])
    )


def _truth_key(form: Mapping[str, Any]) -> tuple[Any, ...]:
    """Canonical normalized natural-form equality key.

    ``closure_id`` is already hair/provenance blind in NRRF870. The explicit
    directed relation signature and unitary curvature keep the equality
    independently auditable if identifier formatting changes.
    """

    return (
        _relation_signature(form),
        str(form.get("unitary_curvature")),
        str(form.get("closure_id")),
    )


def _positive(value: Any) -> bool:
    try:
        number = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return False
    return number.is_finite() and number > 0


def derive_translational_truth_partition(
    *,
    observer_id: str | None,
    sensor_history: Sequence[Sequence[Mapping[str, Any]]],
    max_returns_per_frame: int | None = None,
) -> dict[str, Any]:
    """Refine trading knowledge using translational truth alone.

    Frame order is retained only as interaction provenance. It cannot create an
    equality, a transition law, or a profit prediction. All semantic classes are
    determined solely by normalized natural-form equality.
    """

    observer = str(observer_id or "")
    frames: list[dict[str, Any]] = []
    members_by_truth: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)

    for frame_index, frame in enumerate(sensor_history):
        closed = resolve_open_sensor_trading_closure(
            observer_id=observer_id,
            sensor_feedback=[dict(row) for row in frame],
            max_returns=max_returns_per_frame,
        )
        frame_row: dict[str, Any] = {
            "frame_index": frame_index,
            "closure_status": closed.get("status"),
            "natural_form_count": len(closed.get("natural_forms", [])),
            "boundary_receipt": closed.get("boundary_receipt"),
            "translational_truth_events": [],
        }
        frames.append(frame_row)
        for form_index, form in enumerate(closed.get("natural_forms", [])):
            truth_key = _truth_key(form)
            members_by_truth[truth_key].append(
                {
                    "frame_index": frame_index,
                    "form_index": form_index,
                    "closure_id": form.get("closure_id"),
                    "relation_continuum_id": form.get("relation_continuum_id"),
                    "directed_relation_signature": form.get(
                        "directed_relation_signature", []
                    ),
                    "unitary_curvature": form.get("unitary_curvature"),
                    "natural_profit": form.get("natural_profit"),
                    "amplitude": form.get("amplitude"),
                    "timing": form.get("timing"),
                    "raw_ball_partition": form.get("raw_ball_partition"),
                    "closure_ball_partition": form.get("closure_ball_partition"),
                    "interaction_witness_id": form.get("interaction_witness_id"),
                    "translation_id": form.get("translation_id"),
                }
            )

    classes: list[dict[str, Any]] = []
    member_lookup: dict[tuple[int, int], dict[str, Any]] = {}
    profitable_class_ids: list[str] = []

    for truth_key, members in sorted(
        members_by_truth.items(), key=lambda item: _stable(item[0])
    ):
        relation_signature, curvature, closure_id = truth_key
        raw_presentations = [member.get("raw_ball_partition") for member in members]
        witness_ids = [member.get("interaction_witness_id") for member in members]
        distinct_raw = {_stable(value) for value in raw_presentations}
        distinct_witnesses = {str(value) for value in witness_ids}
        truth_body = {
            "observer_id": observer,
            "directed_relation_signature": relation_signature,
            "unitary_curvature": curvature,
            "closure_id": closure_id,
        }
        truth_class_id = _digest("trading-translational-truth", truth_body)
        representative_profit = members[0].get("natural_profit") if members else None
        profitable = _positive(representative_profit)
        if profitable:
            profitable_class_ids.append(truth_class_id)

        for member in members:
            member["truth_class_id"] = truth_class_id
            member["profitable_truth_class"] = profitable
            member_lookup[(int(member["frame_index"]), int(member["form_index"]))] = member

        classes.append(
            {
                "truth_class_id": truth_class_id,
                "closure_id": closure_id,
                "directed_relation_signature": [
                    {"source_token": source, "target_token": target}
                    for source, target in relation_signature
                ],
                "unitary_curvature": curvature,
                "natural_profit": representative_profit,
                "profitable_truth_class": profitable,
                "members": members,
                "member_count": len(members),
                "hair_orbit_member_count": len(distinct_raw),
                "interaction_witness_count": len(distinct_witnesses),
                "ball_equals_natural_form_class": True,
                "hair_differences_do_not_split_truth": True,
                "natural_form_equality_authors_partition": True,
                "frame_index_authors_partition": False,
                "source_witness_authors_partition": False,
                "profit_is_property_of_truth_class": True,
                "profit_is_not_transition_rule": True,
            }
        )

    # Interaction order may tell us whether a class has been encountered before,
    # but it never changes class equality. There is deliberately no inter-class
    # trajectory, similarity metric, tolerance, or forecast here.
    seen_truth_classes: set[str] = set()
    learning_events: list[dict[str, Any]] = []
    for frame_row in frames:
        frame_index = int(frame_row["frame_index"])
        frame_members = sorted(
            (
                member
                for (member_frame, _), member in member_lookup.items()
                if member_frame == frame_index
            ),
            key=lambda member: int(member["form_index"]),
        )
        if not frame_members:
            event = {
                "frame_index": frame_index,
                "status": OPEN_STATUS,
                "event": "OPEN_NO_TRANSLATIONAL_TRUTH",
                "truth_class_id": None,
                "authors_truth": False,
                "predicts_profit": False,
            }
            learning_events.append(event)
            frame_row["translational_truth_events"].append(event)
            continue

        for member in frame_members:
            truth_class_id = str(member["truth_class_id"])
            already_witnessed = truth_class_id in seen_truth_classes
            event = {
                "frame_index": frame_index,
                "form_index": int(member["form_index"]),
                "status": WITNESSED_STATUS,
                "event": (
                    "SAME_TRANSLATIONAL_TRUTH_RETURNED"
                    if already_witnessed
                    else "NEW_TRANSLATIONAL_TRUTH_WITNESSED"
                ),
                "truth_class_id": truth_class_id,
                "closure_id": member.get("closure_id"),
                "unitary_curvature": member.get("unitary_curvature"),
                "natural_profit": member.get("natural_profit"),
                "profitable_truth_class": member.get("profitable_truth_class") is True,
                "hair_return_of_known_truth": already_witnessed,
                "authors_truth": False,
                "predicts_profit": False,
            }
            learning_events.append(event)
            frame_row["translational_truth_events"].append(event)
            seen_truth_classes.add(truth_class_id)

    witnessed_frames = sum(
        1 for row in frames if row["closure_status"] == WITNESSED_STATUS
    )
    open_frames = len(frames) - witnessed_frames
    learned_profit = bool(profitable_class_ids)

    return {
        "protocol": PROTOCOL,
        "status": WITNESSED_STATUS if classes else OPEN_STATUS,
        "equation": (
            "Ball_i ~ Ball_j <-> NaturalForm(Ball_i)=NaturalForm(Ball_j) "
            "<-> ClosureTruth_i=ClosureTruth_j"
        ),
        "translational_truth_alone": True,
        "translational_truth_is_partition_equality": True,
        "ball_hair_natural_form_are_relative_readings": True,
        "ball_is_truth_class_not_predeclared_graph_region": True,
        "hair_is_intra_class_presentation_not_new_truth": True,
        "natural_form_is_unique_normalized_class_representative": True,
        "relation_space_refines_from_returned_interaction": True,
        "distinct_natural_forms_are_not_declared_translations": True,
        "inter_class_dynamics_law_present": False,
        "trend_model_present": False,
        "forecast_model_present": False,
        "similarity_tolerance_present": False,
        "profit_trajectory_present": False,
        "history_length_authors_truth": False,
        "frame_boundaries_author_truth": False,
        "learning_is_truth_partition_refinement": True,
        "profit_learning_is_discovery_not_prediction": True,
        "profit_learning_definition": (
            "exists returned translational-truth class with natural_profit > 0"
        ),
        "learned_profit": learned_profit,
        "profitable_truth_class_count": len(profitable_class_ids),
        "profitable_truth_class_ids": profitable_class_ids,
        "classes": classes,
        "class_count": len(classes),
        "learning_events": learning_events,
        "frames": frames,
        "frame_count": len(frames),
        "witnessed_frame_count": witnessed_frames,
        "open_frame_count": open_frames,
        "id": _digest(
            "trading-translational-truth-alone",
            {"observer": observer, "classes": classes},
        ),
    }


__all__ = ["PROTOCOL", "derive_translational_truth_partition"]
