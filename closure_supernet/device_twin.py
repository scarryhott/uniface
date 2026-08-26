"""Simulated first device and CLOSED institutional-review stubs.

FIRST DEVICE = simulated low-energy optical ellipse.
No real laser, SLM, quantum controller, voltage, magnet, cryo, or fusion.

ρ_D defined only for:
  r → path / delay / gain / translation
  i → phase / polarization
  hair → perturbation directions
  ball → bounded optical envelope
  ellipse → mirror / phase-transfer geometry
  metavector → phase / intensity / orientation
Everything else stays OPEN: neither rejected nor allowed to actuate.

Notebook operators are proposed device-relative realizations, not
established physical identities.
"""

from __future__ import annotations

from typing import Mapping

from .hardware_models import (
    ActuatorChannel,
    Device,
    DeviceConstraint,
    DeviceKind,
    DeviceStatus,
    FormStatus,
    NaturalForm,
    RhoDImage,
    SAFETY_POLICY_VERSION,
    SensorChannel,
    SimulationResult,
    new_id,
)

# Partial map ρ_D : NaturalForm ⇁ DeviceConstraint for the optical ellipse.
OPTICAL_RHO_D: dict[str, tuple[str, ...]] = {
    "r": ("path", "delay", "gain", "translation"),
    "i": ("phase", "polarization"),
    "hair": ("perturbation_directions",),
    "ball": ("bounded_optical_envelope",),
    "ellipse": ("mirror_geometry", "phase_transfer_geometry"),
    "metavector": ("phase", "intensity", "orientation"),
}

OPTICAL_UNITS: dict[str, str] = {
    "path": "sim.path",
    "delay": "sim.delay",
    "gain": "sim.gain",
    "translation": "sim.translation",
    "phase": "sim.rad",
    "polarization": "sim.pol",
    "perturbation_directions": "sim.hair",
    "bounded_optical_envelope": "sim.ball",
    "mirror_geometry": "sim.ellipse.mirror",
    "phase_transfer_geometry": "sim.ellipse.phase_transfer",
    "intensity": "sim.intensity",
    "orientation": "sim.rad",
}

OPTICAL_BOUNDS: dict[str, tuple[float, float]] = {
    "path": (0.0, 1.0),
    "delay": (0.0, 1.0),
    "gain": (0.0, 1.0),
    "translation": (-1.0, 1.0),
    "phase": (-1.0, 1.0),
    "polarization": (0.0, 1.0),
    "perturbation_directions": (0.0, 1.0),
    "bounded_optical_envelope": (0.0, 1.0),
    "mirror_geometry": (0.0, 1.0),
    "phase_transfer_geometry": (0.0, 1.0),
    "intensity": (0.0, 1.0),
    "orientation": (-1.0, 1.0),
}

NEUTRAL_STATE: dict[str, float] = {k: 0.0 for k in OPTICAL_BOUNDS}


def optical_rho_d(form: NaturalForm, device: Device) -> RhoDImage:
    """ρ_D for the simulated optical ellipse. Undefined → OPEN, not actuatable."""
    if device.kind != DeviceKind.SIMULATED_OPTICAL_ELLIPSE:
        return RhoDImage(form=form, device_id=device.device_id, constraint=None, status=FormStatus.OPEN)
    targets = OPTICAL_RHO_D.get(form.symbol)
    if not targets:
        return RhoDImage(form=form, device_id=device.device_id, constraint=None, status=FormStatus.OPEN)
    # Image is the set of control variables; a representative constraint is returned
    # for the first mapped variable. Callers use mapped_controls() for the full set.
    first = targets[0]
    lo, hi = OPTICAL_BOUNDS[first]
    constraint = DeviceConstraint(
        device_id=device.device_id,
        control_variable=first,
        min_value=lo,
        max_value=hi,
        unit=OPTICAL_UNITS[first],
    )
    return RhoDImage(form=form, device_id=device.device_id, constraint=constraint, status=FormStatus.DEFINED)


def mapped_controls_for_forms(
    forms: tuple[NaturalForm, ...], device: Device
) -> tuple[dict[str, tuple[float, float]], tuple[str, ...]]:
    """Return (defined control → (min, max), OPEN form symbols)."""
    defined: dict[str, tuple[float, float]] = {}
    open_forms: list[str] = []
    if device.kind != DeviceKind.SIMULATED_OPTICAL_ELLIPSE:
        return {}, tuple(f.symbol for f in forms)
    for form in forms:
        targets = OPTICAL_RHO_D.get(form.symbol)
        if not targets:
            open_forms.append(form.symbol)
            continue
        for name in targets:
            defined[name] = OPTICAL_BOUNDS[name]
    return defined, tuple(open_forms)


def register_simulated_optical_ellipse(device_id: str | None = None) -> Device:
    did = device_id or "optical-ellipse-sim-1"
    sensors = (
        SensorChannel(channel_id=f"{did}-photometry", device_id=did, kind="photometry", unit="sim.intensity"),
        SensorChannel(channel_id=f"{did}-phase-return", device_id=did, kind="phase_return", unit="sim.rad"),
        SensorChannel(channel_id=f"{did}-orientation-return", device_id=did, kind="orientation_return", unit="sim.rad"),
    )
    actuators = tuple(
        ActuatorChannel(
            channel_id=f"{did}-{name}",
            device_id=did,
            control_variable=name,
            min_value=lo,
            max_value=hi,
            unit=OPTICAL_UNITS[name],
            simulated=True,
        )
        for name, (lo, hi) in OPTICAL_BOUNDS.items()
    )
    return Device(
        device_id=did,
        kind=DeviceKind.SIMULATED_OPTICAL_ELLIPSE,
        status=DeviceStatus.SIMULATED,
        sensor_channels=sensors,
        actuator_channels=actuators,
        safety_policy_version=SAFETY_POLICY_VERSION,
        simulated=True,
        real_laser=False,
        real_slm=False,
        real_quantum_controller=False,
        real_voltage=False,
        real_magnet=False,
        real_cryo=False,
        real_fusion=False,
        institutional_review_only=False,
        note="FIRST DEVICE = simulated low-energy optical ellipse. Not a real laser/SLM. Chart, not Closure.",
    )


def quantum_adapter_stub(device_id: str | None = None) -> Device:
    did = device_id or "quantum-adapter-stub"
    return Device(
        device_id=did,
        kind=DeviceKind.QUANTUM_ADAPTER,
        status=DeviceStatus.CLOSED,
        sensor_channels=(),
        actuator_channels=(),
        safety_policy_version=SAFETY_POLICY_VERSION,
        simulated=True,
        real_quantum_controller=False,
        institutional_review_only=True,
        note="CLOSED / institutional-review only. Not a real quantum controller.",
    )


def fusion_adapter_stub(device_id: str | None = None) -> Device:
    did = device_id or "fusion-adapter-stub"
    return Device(
        device_id=did,
        kind=DeviceKind.FUSION_ADAPTER,
        status=DeviceStatus.CLOSED,
        sensor_channels=(),
        actuator_channels=(),
        safety_policy_version=SAFETY_POLICY_VERSION,
        simulated=True,
        real_fusion=False,
        institutional_review_only=True,
        note="CLOSED / institutional-review only. Not a real fusion system.",
    )


class SimulatedOpticalEllipseTwin:
    """Device twin. Applies only u_t = SafetyEnvelope_D(G_t) after gateway checks."""

    def __init__(self, device: Device) -> None:
        if device.kind != DeviceKind.SIMULATED_OPTICAL_ELLIPSE:
            raise ValueError("twin is only for the simulated optical ellipse")
        if device.real_laser or device.real_slm or device.real_voltage or device.real_magnet or device.real_cryo or device.real_fusion or device.real_quantum_controller:
            raise ValueError("real hardware is forbidden in this pass")
        self.device = device
        self.state: dict[str, float] = dict(NEUTRAL_STATE)

    def simulate(self, controls: Mapping[str, float], max_intensity: float = 1.0) -> SimulationResult:
        energy_ok = True
        reasons: list[str] = []
        predicted: dict[str, float] = {}
        channels = {c.control_variable: c for c in self.device.actuator_channels}
        for name, value in controls.items():
            ch = channels.get(name)
            if ch is None:
                reasons.append(f"unmapped control {name} stays OPEN")
                continue
            if value < ch.min_value or value > ch.max_value:
                energy_ok = False
                reasons.append(f"{name} out of [{ch.min_value}, {ch.max_value}]")
                continue
            if name == "intensity" and value > max_intensity:
                energy_ok = False
                reasons.append("intensity exceeds simulated low-energy bound")
                continue
            predicted[name] = float(value)
        passed = energy_ok and bool(predicted) and not any("out of" in r or "exceeds" in r for r in reasons)
        return SimulationResult(
            run_id=new_id("sim"),
            passed=passed,
            summary="; ".join(reasons) if reasons else "bounds ok; simulated low-energy optical ellipse",
            predicted_return=predicted,
            energy_bound_ok=energy_ok,
        )

    def apply(self, controls: Mapping[str, float]) -> dict[str, float]:
        applied: dict[str, float] = {}
        channels = {c.control_variable: c for c in self.device.actuator_channels}
        for name, value in controls.items():
            ch = channels.get(name)
            if ch is None:
                continue
            self.state[name] = float(value)
            applied[name] = float(value)
        return applied

    def rollback_neutral(self) -> dict[str, float]:
        self.state = dict(NEUTRAL_STATE)
        return dict(self.state)

    def sense(self) -> dict[str, float]:
        return {
            "photometry": self.state.get("intensity", 0.0),
            "phase_return": self.state.get("phase", 0.0),
            "orientation_return": self.state.get("orientation", 0.0),
            "bounded_optical_envelope": self.state.get("bounded_optical_envelope", 0.0),
        }
