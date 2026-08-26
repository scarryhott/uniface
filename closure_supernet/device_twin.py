from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import pvariance
from typing import Any

from .hardware_models import HardwareDeviceKind


@dataclass(frozen=True, slots=True)
class TwinSimulationResult:
    output_reading: dict[str, Any]
    metrics: dict[str, float]
    safe: bool
    reason: str


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _normalized(value: float, minimum: float, maximum: float) -> float:
    if maximum == minimum:
        return 0.0
    return _clamp((value - minimum) / (maximum - minimum))


def _validate_envelope(
    device: dict[str, Any], constraint: dict[str, Any]
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    envelope = device["safety_envelope"]
    controls = constraint["control_values"]
    for channel in device["control_channels"]:
        if channel not in controls:
            errors.append(f"missing control {channel}")
            continue
        bound = envelope[channel]
        value = float(controls[channel])
        if not math.isfinite(value):
            errors.append(f"non-finite control {channel}")
        elif value < float(bound["minimum"]) or value > float(bound["maximum"]):
            errors.append(
                f"control {channel}={value} outside "
                f"[{bound['minimum']},{bound['maximum']}]"
            )
    unknown = sorted(set(controls) - set(device["control_channels"]))
    if unknown:
        errors.append(f"unknown controls: {unknown}")
    if float(constraint["duration_seconds"]) > float(device["max_duration_seconds"]):
        errors.append("constraint duration exceeds device maximum")
    return not errors, errors


def _target_fidelity(
    output_vector: list[float], expected: dict[str, Any]
) -> float:
    target = expected.get("target_sensor_vector")
    if isinstance(target, list) and len(target) == len(output_vector):
        values = [float(value) for value in target]
        distance = math.sqrt(
            sum((left - right) ** 2 for left, right in zip(output_vector, values))
            / max(1, len(output_vector))
        )
        return _clamp(1.0 - distance)
    if "target_intensity" in expected:
        return _clamp(1.0 - abs(output_vector[0] - float(expected["target_intensity"])))
    return _clamp(sum(output_vector) / max(1, len(output_vector)))


def _simulate_optical_ellipse(
    device: dict[str, Any], constraint: dict[str, Any]
) -> TwinSimulationResult:
    bounded, errors = _validate_envelope(device, constraint)
    controls = constraint["control_values"]
    envelope = device["safety_envelope"]

    phase_x = float(controls.get("phase_x", 0.0))
    phase_y = float(controls.get("phase_y", 0.0))
    polarization = float(controls.get("polarization", 0.0))
    intensity_raw = float(controls.get("intensity", 0.0))
    intensity_bound = envelope.get("intensity", {"minimum": 0.0, "maximum": 1.0})
    drive = _normalized(
        intensity_raw,
        float(intensity_bound["minimum"]),
        float(intensity_bound["maximum"]),
    )

    # This is a deterministic low-energy device twin, not an optical-physics
    # claim. It provides a reproducible return relation for the software loop.
    phase_delta = math.pi * (phase_x - phase_y)
    phase_sum = phase_x + phase_y
    path_return = math.cos(phase_delta / 2.0) ** 2
    symmetry = _clamp(1.0 - abs(phase_sum) / 2.0)
    polarization_return = (math.cos(math.pi * polarization) + 1.0) / 2.0
    return_intensity = _clamp(
        drive
        * (0.45 + 0.55 * path_return)
        * (0.70 + 0.30 * symmetry)
        * (0.80 + 0.20 * polarization_return)
    )
    phase_return = (math.sin(phase_delta) + 1.0) / 2.0
    sensor_vector = [return_intensity, phase_return, polarization_return]
    stability = _clamp(1.0 - pvariance(sensor_vector))
    return_fidelity = _target_fidelity(sensor_vector, constraint["expected_return"])
    path_invariant = math.cos(2.0 * phase_delta)

    output = {
        "device_reading": "simulated optical ellipse return",
        "sensor_vector": [round(value, 12) for value in sensor_vector],
        "return_intensity": round(return_intensity, 12),
        "phase_return": round(phase_return, 12),
        "polarization_return": round(polarization_return, 12),
        "path_invariant": round(path_invariant, 12),
        "selected_metavector": constraint["selected_metavector"],
        "control_values": controls,
        "simulation_only": True,
        "physical_law_claimed": False,
    }
    metrics = {
        "return_fidelity": round(return_fidelity, 12),
        "stability": round(stability, 12),
        "symmetry": round(symmetry, 12),
        "path_return": round(path_return, 12),
        "drive": round(drive, 12),
    }
    reason = (
        "bounded simulated optical return"
        if bounded
        else "unsafe constraint: " + "; ".join(errors)
    )
    return TwinSimulationResult(output, metrics, bounded, reason)


def _simulate_sensor_loop(
    device: dict[str, Any], constraint: dict[str, Any]
) -> TwinSimulationResult:
    bounded, errors = _validate_envelope(device, constraint)
    channels = device["control_channels"]
    controls = constraint["control_values"]
    normalized: list[float] = []
    for channel in channels:
        bound = device["safety_envelope"][channel]
        normalized.append(
            _normalized(
                float(controls.get(channel, bound["neutral"])),
                float(bound["minimum"]),
                float(bound["maximum"]),
            )
        )
    mean = sum(normalized) / max(1, len(normalized))
    return_mix = _clamp(mean * (1.0 - pvariance(normalized)))
    sensor_vector = normalized + [return_mix]
    output = {
        "device_reading": "simulated generic sensor-loop return",
        "sensor_vector": [round(value, 12) for value in sensor_vector],
        "return_mix": round(return_mix, 12),
        "selected_metavector": constraint["selected_metavector"],
        "control_values": controls,
        "simulation_only": True,
        "physical_law_claimed": False,
    }
    metrics = {
        "return_fidelity": round(
            _target_fidelity(sensor_vector, constraint["expected_return"]), 12
        ),
        "stability": round(_clamp(1.0 - pvariance(sensor_vector)), 12),
        "symmetry": round(_clamp(1.0 - (max(normalized) - min(normalized))), 12),
        "path_return": round(return_mix, 12),
        "drive": round(mean, 12),
    }
    reason = "bounded simulated sensor-loop return" if bounded else "unsafe constraint: " + "; ".join(errors)
    return TwinSimulationResult(output, metrics, bounded, reason)


def simulate_device(
    device: dict[str, Any], constraint: dict[str, Any]
) -> TwinSimulationResult:
    kind = HardwareDeviceKind(device["kind"])
    if kind == HardwareDeviceKind.SIMULATED_OPTICAL_ELLIPSE:
        return _simulate_optical_ellipse(device, constraint)
    if kind == HardwareDeviceKind.SIMULATED_SENSOR_LOOP:
        return _simulate_sensor_loop(device, constraint)
    raise ValueError(f"No safe device twin registered for {kind}")
