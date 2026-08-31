from __future__ import annotations

"""Continuation of natural trading closure across returned sensor states.

A sequence of returned sensor frames is not a fixed horizon and does not create a
trend signal. Each frame is first closed by the authoritative open-sensor trading
kernel. Witnessed natural forms are then identified only by their directed
relation continuum. Curvature motion, amplitude motion, maze timing, signal and
trade are readings of that same relational continuum.

The continuation may describe motion toward or away from positive natural
profit, but that description never authors closure or execution. A profitable
crossing is executable only when the current natural-form trade projection is
itself source-witnessed and admissible.
"""

from decimal import Decimal
import hashlib
import json
from typing import Any, Mapping, Sequence

from .closure_continuity import OPEN_STATUS, WITNESSED_STATUS
from .trading_natural_form_closure import resolve_open_sensor_trading_closure

PROTOCOL = "closure.supernet/trading-natural-form-continuation-nrrf868-869-v1"


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _digest(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(_stable(value).encode('utf-8')).hexdigest()[:24]}"


def _decimal(value: Any) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _text(value: Decimal) -> str:
    return format(value, "f")


def _canonical_directed_cycle(token_path: Sequence[Any]) -> tuple[tuple[str, str], ...]:
    tokens = [str(token) for token in token_path]
    if len(tokens) < 2:
        return ()
    pairs = [(left, right) for left, right in zip(tokens[:-1], tokens[1:])]
    if not pairs:
        return ()
    rotations = [tuple(pairs[index:] + pairs[:index]) for index in range(len(pairs))]
    return min(rotations)


def _continuum_id(observer_id: str, form: Mapping[str, Any]) -> tuple[str, list[dict[str, str]]]:
    signature = _canonical_directed_cycle(form.get("token_path", []))
    relations = [
        {"source_token": source, "target_token": target}
        for source, target in signature
    ]
    return (
        _digest(
            "trading-relation-continuum",
            {"observer_id": observer_id, "directed_relations": relations},
        ),
        relations,
    )


def _movement(previous_profit: Decimal, current_profit: Decimal) -> str:
    if current_profit > previous_profit:
        return "TOWARD_PROFIT"
    if current_profit < previous_profit:
        return "AWAY_FROM_PROFIT"
    return "STABLE"


def resolve_trading_closure_continuation(
    *,
    observer_id: str | None,
    sensor_history: Sequence[Sequence[Mapping[str, Any]]],
    max_returns_per_frame: int | None = None,
) -> dict[str, Any]:
    """Close successive returned sensor frames and derive continuum motion.

    ``sensor_history`` is an evidence sequence, never a semantic holding period.
    Exact duplicate frames are ignored because no new returned interaction has
    entered the arena. No regression, forecast, threshold or time window can
    create a natural form.
    """

    observer = str(observer_id or "")
    frames: list[dict[str, Any]] = []
    seen_frames: set[str] = set()
    tracks: dict[str, dict[str, Any]] = {}

    for supplied_index, raw_frame in enumerate(sensor_history):
        raw_rows = [dict(row) for row in raw_frame]
        frame_fingerprint = _digest("sensor-frame", raw_rows)
        if frame_fingerprint in seen_frames:
            frames.append(
                {
                    "supplied_index": supplied_index,
                    "frame_id": frame_fingerprint,
                    "status": OPEN_STATUS,
                    "duplicate_return_state": True,
                    "authors_truth": False,
                    "reason": "NO_NEW_RETURNED_INTERACTION",
                }
            )
            continue
        seen_frames.add(frame_fingerprint)

        closed = resolve_open_sensor_trading_closure(
            observer_id=observer,
            sensor_feedback=raw_rows,
            max_returns=max_returns_per_frame,
        )
        frame_row: dict[str, Any] = {
            "supplied_index": supplied_index,
            "frame_id": frame_fingerprint,
            "status": closed["status"],
            "duplicate_return_state": False,
            "natural_form_count": len(closed.get("natural_forms", [])),
            "boundary_receipt": closed.get("boundary_receipt"),
            "continuum_readings": [],
        }

        for form in closed.get("natural_forms", []):
            if form.get("status") != WITNESSED_STATUS:
                continue
            continuum_id, directed_relations = _continuum_id(observer, form)
            profit = _decimal(form["natural_profit"])
            curvature = _decimal(form["unitary_curvature"])
            amplitude = _decimal(form["amplitude"])
            trade = dict(form.get("trade_projection") or {})
            reading = {
                "continuum_id": continuum_id,
                "closure_translation_id": form.get("closure_id"),
                "directed_relations": directed_relations,
                "ball_id": form.get("ball_id"),
                "unitary_curvature": _text(curvature),
                "natural_profit": _text(profit),
                "amplitude": _text(amplitude),
                "timing": form.get("timing"),
                "signal_projection": form.get("signal_projection"),
                "trade_projection": trade,
                "amplitude_timing_translation_equal": form.get(
                    "amplitude_timing_translation_equal"
                ) is True,
                "signal_trade_translation_equal": form.get(
                    "signal_trade_translation_equal"
                ) is True,
            }
            frame_row["continuum_readings"].append(reading)

            track = tracks.setdefault(
                continuum_id,
                {
                    "continuum_id": continuum_id,
                    "observer_id": observer or None,
                    "directed_relations": directed_relations,
                    "readings": [],
                    "transitions": [],
                    "fixed_horizon": None,
                    "trajectory_authors_truth": False,
                    "curvature_motion_is_relative_projection": True,
                    "profit_crossing_authors_trade": False,
                },
            )
            previous = track["readings"][-1] if track["readings"] else None
            track["readings"].append(
                {
                    "frame_index": supplied_index,
                    **reading,
                }
            )
            if previous is not None:
                previous_profit = _decimal(previous["natural_profit"])
                previous_curvature = _decimal(previous["unitary_curvature"])
                previous_amplitude = _decimal(previous["amplitude"])
                profit_delta = profit - previous_profit
                curvature_delta = curvature - previous_curvature
                amplitude_delta = amplitude - previous_amplitude
                movement = _movement(previous_profit, profit)
                crossed_positive = previous_profit <= 0 < profit
                crossed_nonpositive = previous_profit > 0 >= profit
                track["transitions"].append(
                    {
                        "from_frame_index": previous["frame_index"],
                        "to_frame_index": supplied_index,
                        "from_closure_translation_id": previous[
                            "closure_translation_id"
                        ],
                        "to_closure_translation_id": form.get("closure_id"),
                        "continuum_id": continuum_id,
                        "profit_delta": _text(profit_delta),
                        "curvature_delta": _text(curvature_delta),
                        "amplitude_delta": _text(amplitude_delta),
                        "movement": movement,
                        "crossed_positive_natural_profit": crossed_positive,
                        "crossed_nonpositive_natural_profit": crossed_nonpositive,
                        "movement_is_forecast": False,
                        "movement_authors_truth": False,
                        "current_trade_admissible": trade.get("admissible") is True,
                        "current_execution_return_status": trade.get(
                            "execution_return_status"
                        ),
                    }
                )

        frames.append(frame_row)

    track_rows = sorted(tracks.values(), key=lambda row: row["continuum_id"])
    for track in track_rows:
        readings = track["readings"]
        transitions = track["transitions"]
        latest = readings[-1] if readings else None
        track["status"] = WITNESSED_STATUS if latest else OPEN_STATUS
        track["latest_natural_profit"] = (
            latest["natural_profit"] if latest is not None else None
        )
        track["latest_unitary_curvature"] = (
            latest["unitary_curvature"] if latest is not None else None
        )
        track["latest_movement"] = (
            transitions[-1]["movement"] if transitions else "UNRESOLVED"
        )
        track["positive_crossing_count"] = sum(
            transition["crossed_positive_natural_profit"]
            for transition in transitions
        )
        track["latest_trade_admissible"] = bool(
            latest
            and (latest.get("trade_projection") or {}).get("admissible") is True
        )

    witnessed_tracks = [row for row in track_rows if row["status"] == WITNESSED_STATUS]
    return {
        "protocol": PROTOCOL,
        "equation": (
            "returned sensor states -> natural-form closures -> same directed "
            "relation continuum -> curvature/amplitude/timing continuation"
        ),
        "status": WITNESSED_STATUS if observer and witnessed_tracks else OPEN_STATUS,
        "observer_id": observer or None,
        "frames": frames,
        "continua": track_rows,
        "continuum_count": len(track_rows),
        "fixed_horizon": None,
        "history_length_authors_truth": False,
        "trajectory_authors_truth": False,
        "curvature_motion_is_relative_projection": True,
        "amplitude_timing_remain_one_translation": True,
        "signal_trade_remain_one_translation": True,
        "positive_crossing_authors_trade": False,
        "execution_requires_current_return_witness": True,
        "continuation_status": OPEN_STATUS,
        "existence_closed": False,
        "id": _digest(
            "trading-closure-continuation",
            {
                "observer_id": observer,
                "frames": [row["frame_id"] for row in frames],
                "continua": [row["continuum_id"] for row in track_rows],
            },
        ),
    }


__all__ = ["PROTOCOL", "resolve_trading_closure_continuation"]
