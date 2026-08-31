from __future__ import annotations

"""Translational-truth refinement for the NRRF870 trading runtime.

The closure law is fixed.  The relation partition is not.  Successive returned
sensor frames are closed independently by the authoritative open-sensor kernel,
and the resulting natural forms are then quotiented by translational truth.

Two returned local balls are one semantic ball exactly when their normalized
natural forms / closure truths are equal.  Distinct raw presentations inside one
class are hair presentations, not new truths.  Consequently time, frame index,
source witness id, labels, and graph membership cannot author a partition.
"""

from collections import defaultdict
import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS
from .trading_natural_form_closure import resolve_open_sensor_trading_closure

PROTOCOL = "closure.supernet/trading-translational-truth-partition-v1"


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

    ``closure_id`` is already hair/provenance blind in NRRF870.  The explicit
    relation signature and unitary curvature are retained in the key so the
    equality remains auditable even if identifier formatting changes.
    """

    return (
        _relation_signature(form),
        str(form.get("unitary_curvature")),
        str(form.get("closure_id")),
    )


def derive_translational_truth_partition(
    *,
    observer_id: str | None,
    sensor_history: Sequence[Sequence[Mapping[str, Any]]],
    max_returns_per_frame: int | None = None,
) -> dict[str, Any]:
    observer = str(observer_id or "")
    frames: list[dict[str, Any]] = []
    members_by_truth: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)

    for frame_index, frame in enumerate(sensor_history):
        closed = resolve_open_sensor_trading_closure(
            observer_id=observer_id,
            sensor_feedback=[dict(row) for row in frame],
            max_returns=max_returns_per_frame,
        )
        frame_row = {
            "frame_index": frame_index,
            "closure_status": closed.get("status"),
            "natural_form_count": len(closed.get("natural_forms", [])),
            "boundary_receipt": closed.get("boundary_receipt"),
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
                    "directed_relation_signature": form.get("directed_relation_signature", []),
                    "unitary_curvature": form.get("unitary_curvature"),
                    "natural_profit": form.get("natural_profit"),
                    "raw_ball_partition": form.get("raw_ball_partition"),
                    "closure_ball_partition": form.get("closure_ball_partition"),
                    "interaction_witness_id": form.get("interaction_witness_id"),
                    "translation_id": form.get("translation_id"),
                }
            )

    classes: list[dict[str, Any]] = []
    for truth_key, members in sorted(members_by_truth.items(), key=lambda item: _stable(item[0])):
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
        classes.append(
            {
                "truth_class_id": _digest("trading-translational-truth", truth_body),
                "closure_id": closure_id,
                "directed_relation_signature": [
                    {"source_token": source, "target_token": target}
                    for source, target in relation_signature
                ],
                "unitary_curvature": curvature,
                "members": members,
                "member_count": len(members),
                "hair_orbit_member_count": len(distinct_raw),
                "interaction_witness_count": len(distinct_witnesses),
                "ball_equals_natural_form_class": True,
                "hair_differences_do_not_split_truth": True,
                "natural_form_equality_authors_partition": True,
                "frame_index_authors_partition": False,
                "source_witness_authors_partition": False,
            }
        )

    witnessed_frames = sum(1 for row in frames if row["closure_status"] == WITNESSED_STATUS)
    open_frames = len(frames) - witnessed_frames
    return {
        "protocol": PROTOCOL,
        "status": WITNESSED_STATUS if classes else OPEN_STATUS,
        "equation": "Ball_i ~ Ball_j <-> NaturalForm(Ball_i)=NaturalForm(Ball_j) <-> ClosureTruth_i=ClosureTruth_j",
        "translational_truth_is_partition_equality": True,
        "ball_hair_natural_form_are_relative_readings": True,
        "ball_is_truth_class_not_predeclared_graph_region": True,
        "hair_is_intra_class_presentation_not_new_truth": True,
        "natural_form_is_unique_normalized_class_representative": True,
        "relation_space_refines_from_returned_interaction": True,
        "history_length_authors_truth": False,
        "frame_boundaries_author_truth": False,
        "classes": classes,
        "class_count": len(classes),
        "frames": frames,
        "frame_count": len(frames),
        "witnessed_frame_count": witnessed_frames,
        "open_frame_count": open_frames,
        "id": _digest("trading-translational-truth-partition", {"observer": observer, "classes": classes}),
    }


__all__ = ["PROTOCOL", "derive_translational_truth_partition"]
