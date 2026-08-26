from __future__ import annotations

import hashlib
from typing import Any

from .hardware_models import (
    HardwareConstraintCreate,
    HardwareConstraintSynthesisCreate,
)


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def source_metavector(source_texts: list[str], dimensions: int) -> list[float]:
    """Derive a deterministic bounded vector from exact source text.

    This is a reproducible software selection chart, not a claim that hashing is
    the source-level metavector operator. Exact source IDs and text remain in the
    resulting constraint so the selection can be inspected or replaced.
    """

    if not source_texts:
        raise ValueError("Constraint synthesis requires at least one exact source")
    seed = "\n\u241e\n".join(source_texts).encode("utf-8")
    output: list[float] = []
    counter = 0
    while len(output) < max(1, dimensions):
        digest = hashlib.sha256(seed + counter.to_bytes(4, "big")).digest()
        for byte in digest:
            output.append((float(byte) / 127.5) - 1.0)
            if len(output) >= dimensions:
                break
        counter += 1
    return [round(value, 12) for value in output]


def map_metavector_to_controls(
    device: dict[str, Any], vector: list[float]
) -> dict[str, float]:
    channels = device["control_channels"]
    if not channels:
        raise ValueError("Device has no declared control channels")
    controls: dict[str, float] = {}
    for index, channel in enumerate(channels):
        raw = vector[index % len(vector)]
        bound = device["safety_envelope"][channel]
        minimum = float(bound["minimum"])
        maximum = float(bound["maximum"])
        if minimum >= 0.0:
            value = minimum + ((raw + 1.0) / 2.0) * (maximum - minimum)
        else:
            scale = max(abs(minimum), abs(maximum))
            value = raw * scale
        controls[channel] = round(_clamp(value, minimum, maximum), 12)
    return controls


def synthesize_constraint(
    device: dict[str, Any],
    data: HardwareConstraintSynthesisCreate,
    source_texts: list[str],
) -> HardwareConstraintCreate:
    vector = source_metavector(
        source_texts,
        max(4, len(device["control_channels"])),
    )
    controls = map_metavector_to_controls(device, vector)
    duration = (
        min(1.0, float(device["max_duration_seconds"]))
        if data.duration_seconds is None
        else float(data.duration_seconds)
    )
    if duration > float(device["max_duration_seconds"]):
        raise ValueError("Requested constraint duration exceeds device safety envelope")
    metadata = {
        **data.metadata,
        "selective_temporary_global_constraint": True,
        "source_reversible": True,
        "constraint_is_not_global_truth": True,
        "metavector_chart": "deterministic-source-hash-v1",
        "simulation_required": True,
        "operator_execution_required": True,
    }
    return HardwareConstraintCreate(
        device_id=data.device_id,
        created_by=data.created_by,
        exact_intent=data.exact_intent,
        source_occurrence_ids=list(dict.fromkeys(data.source_occurrence_ids)),
        source_translation_ids=list(dict.fromkeys(data.source_translation_ids)),
        source_interaction_ids=list(dict.fromkeys(data.source_interaction_ids)),
        participant_ids=list(dict.fromkeys(data.participant_ids)),
        agent_ids=list(dict.fromkeys(data.agent_ids)),
        affected_perspectives=list(dict.fromkeys(data.affected_perspectives)),
        selected_metavector=vector,
        control_values=controls,
        duration_seconds=duration,
        expected_return=data.expected_return,
        metadata=metadata,
    )
