"""Typed records for the hardware closure chart.

This package is a digital chart of a hardware loop, not Closure.
Notebook operators are proposed device-relative realizations, not
established physical identities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Mapping, Protocol


SAFETY_POLICY_VERSION = "hardware-safety-v1-simulated-optical"
CHART_NOTE = "digital chart of a hardware loop, not Closure; TRUE not issued"


class Refusal(str, Enum):
    NO_ADMISSION = "no_admission"
    EXPIRED = "expired"
    REVOKED = "revoked"
    UNDEFINED_FORM = "undefined_form_OPEN"
    RAW_AI_PROPOSAL_ALONE = "raw_ai_proposal_alone"
    NETWORK_INTERPRETATION_IS_NOT_ACTUATION = "admissible_interpretation_neq_authorized_actuation"
    UNBOUNDED = "unbounded"
    DEVICE_CLOSED = "device_CLOSED_institutional_review_only"
    SIMULATION_FAILED = "simulation_failed"
    MISSING_APPROVALS = "missing_approvals"
    WRONG_DEVICE = "wrong_device"
    PUBLIC_CONSENSUS = "undifferentiated_public_consensus"
    RAW_AI_OUTPUT_TO_HARDWARE = "raw_ai_output_never_u_t"
    NOT_TEMPORARY = "constraint_not_temporary"
    MISSING_ENVELOPE = "missing_safety_envelope"
    WRONG_POLICY = "safety_policy_mismatch"
    REAL_HARDWARE_FORBIDDEN = "real_laser_slm_quantum_voltage_magnet_cryo_fusion_forbidden"


class DeviceKind(str, Enum):
    SIMULATED_OPTICAL_ELLIPSE = "simulated_low_energy_optical_ellipse"
    QUANTUM_ADAPTER = "quantum_adapter_stub"
    FUSION_ADAPTER = "fusion_adapter_stub"


class DeviceStatus(str, Enum):
    SIMULATED = "simulated"
    CLOSED = "CLOSED"
    OPEN = "OPEN"


class FormStatus(str, Enum):
    DEFINED = "defined_rho_d"
    OPEN = "OPEN"


class ProposalOrigin(str, Enum):
    HUMAN = "human"
    AUTONOMOUS_AI = "autonomous_ai"
    SENSOR = "sensor"
    COLLECTIVE = "collective"


class AdmissionKind(str, Enum):
    NETWORK_INTERPRETATION = "admissible_as_network_interpretation"
    HARDWARE_ACTUATION = "authorized_as_hardware_actuation"


class ActuationDecision(str, Enum):
    ACTUATED = "actuated"
    REFUSED = "refused"


class Clock(Protocol):
    def now(self) -> datetime: ...


class UtcClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


@dataclass
class FrozenClock:
    t: datetime

    def now(self) -> datetime:
        return self.t

    def advance(self, delta: timedelta) -> None:
        self.t = self.t + delta


@dataclass(frozen=True)
class SensorChannel:
    channel_id: str
    device_id: str
    kind: str
    unit: str
    simulated: bool = True


@dataclass(frozen=True)
class ActuatorChannel:
    channel_id: str
    device_id: str
    control_variable: str
    min_value: float
    max_value: float
    unit: str
    simulated: bool = True


@dataclass(frozen=True)
class Device:
    device_id: str
    kind: DeviceKind
    status: DeviceStatus
    sensor_channels: tuple[SensorChannel, ...]
    actuator_channels: tuple[ActuatorChannel, ...]
    safety_policy_version: str
    simulated: bool = True
    real_laser: bool = False
    real_slm: bool = False
    real_quantum_controller: bool = False
    real_voltage: bool = False
    real_magnet: bool = False
    real_cryo: bool = False
    real_fusion: bool = False
    institutional_review_only: bool = False
    note: str = CHART_NOTE


@dataclass(frozen=True)
class NaturalForm:
    form_id: str
    symbol: str
    notebook_operator: str


@dataclass(frozen=True)
class DeviceConstraint:
    device_id: str
    control_variable: str
    min_value: float
    max_value: float
    unit: str


@dataclass(frozen=True)
class RhoDImage:
    """Image of ρ_D : NaturalForm ⇁ DeviceConstraint.

    Undefined forms stay OPEN: neither rejected nor allowed to actuate.
    """

    form: NaturalForm
    device_id: str
    constraint: DeviceConstraint | None
    status: FormStatus

    @property
    def actuatable(self) -> bool:
        return self.status == FormStatus.DEFINED and self.constraint is not None


@dataclass(frozen=True)
class Metavector:
    phase: float | None = None
    intensity: float | None = None
    orientation: float | None = None

    def as_map(self) -> dict[str, float]:
        out: dict[str, float] = {}
        if self.phase is not None:
            out["phase"] = self.phase
        if self.intensity is not None:
            out["intensity"] = self.intensity
        if self.orientation is not None:
            out["orientation"] = self.orientation
        return out


@dataclass(frozen=True)
class SimulationResult:
    run_id: str
    passed: bool
    summary: str
    predicted_return: Mapping[str, float]
    energy_bound_ok: bool
    notes: str = "simulation of low-energy optical ellipse; not a physical chamber"


@dataclass(frozen=True)
class HardwareSafetyPolicy:
    version: str = SAFETY_POLICY_VERSION
    min_human_approvals: int = 2
    allow_ai_as_sole_approver: bool = False
    allow_raw_ai_output: bool = False
    allow_undifferentiated_public_consensus: bool = False
    max_intensity: float = 1.0
    require_simulation_pass: bool = True
    require_defined_rho_d: bool = True
    simulated_devices_only: bool = True


@dataclass(frozen=True)
class Interaction:
    interaction_id: str
    origin: ProposalOrigin
    actor_id: str
    device_id: str
    natural_forms: tuple[NaturalForm, ...]
    requested_controls: Mapping[str, float]
    at: datetime
    raw_ai_output: bool = False
    undifferentiated_public_consensus: bool = False
    sequence: int = 0
    causal_predecessor_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class TemporaryGlobalConstraint:
    """G_t — temporary, device-relative collective constraint.

    Hardware does not receive G_t raw. Hardware receives u_t = SafetyEnvelope_D(G_t).
    """

    constraint_id: str
    device_id: str
    G_t: Mapping[str, float]
    source_interaction_ids: tuple[str, ...]
    participant_ids: tuple[str, ...]
    agent_ids: tuple[str, ...]
    expires_at: datetime
    duration: timedelta
    temporary: bool
    device_relative: bool
    bounded: bool
    source_reversible: bool
    time_limited: bool
    revocable: bool
    causally_ordered: bool
    approved_under_safety_policy: bool
    safety_policy_version: str
    sequence: int = 0
    causal_predecessor_ids: tuple[str, ...] = ()
    open_unmapped_forms: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConstraintProposal:
    proposal_id: str
    origin: ProposalOrigin
    author_id: str
    device_id: str
    natural_forms: tuple[NaturalForm, ...]
    requested_controls: Mapping[str, float]
    source_interaction_ids: tuple[str, ...]
    created_at: datetime
    raw_ai_output: bool = False
    undifferentiated_public_consensus: bool = False
    sequence: int = 0
    causal_predecessor_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class SafetyEnvelope:
    """u_t = SafetyEnvelope_D(G_t). The only command hardware may receive."""

    envelope_id: str
    device_id: str
    source_interaction_ids: tuple[str, ...]
    participant_ids: tuple[str, ...]
    agent_ids: tuple[str, ...]
    selected_metavector: Metavector
    mapped_control_variables: tuple[str, ...]
    min_values: Mapping[str, float]
    max_values: Mapping[str, float]
    duration: timedelta
    expires_at: datetime
    required_approvals: tuple[str, ...]
    approvals: tuple[str, ...]
    safety_policy_version: str
    simulation_result: SimulationResult | None
    actuation_receipt_id: str | None
    rollback_neutral_state: Mapping[str, float]
    constraint_id: str
    revoked: bool = False
    causal_predecessor_ids: tuple[str, ...] = ()
    sequence: int = 0
    chart_not_closure: bool = True
    command: str = "u_t=SafetyEnvelope_D(G_t)"


@dataclass(frozen=True)
class ConstraintAdmission:
    admission_id: str
    proposal_id: str
    kind: AdmissionKind
    envelope_id: str | None
    admitted_at: datetime
    expires_at: datetime
    revoked: bool = False
    causal_predecessor_ids: tuple[str, ...] = ()
    sequence: int = 0
    note: str = "admissible as a network interpretation ≠ authorized as a hardware actuation"


@dataclass(frozen=True)
class ActuationReceipt:
    receipt_id: str
    envelope_id: str | None
    device_id: str
    decision: ActuationDecision
    refused_reason: Refusal | None
    applied_controls: Mapping[str, float]
    at: datetime
    simulated: bool = True
    sequence: int = 0
    causal_predecessor_ids: tuple[str, ...] = ()
    admission_id: str | None = None
    note: str = CHART_NOTE


@dataclass(frozen=True)
class PhysicalReturn:
    return_id: str
    receipt_id: str
    device_id: str
    sensor_readings: Mapping[str, float]
    source_reversible: bool
    reintegrates_to_network: bool
    source_interaction_ids: tuple[str, ...]
    at: datetime
    simulated: bool = True
    note: str = "physical-style return from simulated optical ellipse; not a real chamber"
    sequence: int = 0
    causal_predecessor_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class VerificationRun:
    run_id: str
    envelope_id: str
    simulation: SimulationResult
    policy_ok: bool
    rho_d_defined: bool
    at: datetime
    sequence: int = 0


@dataclass(frozen=True)
class NetworkReopening:
    reopening_id: str
    return_id: str
    next_interaction_id: str
    cycle_index: int
    sequence: int = 0
    causal_predecessor_ids: tuple[str, ...] = ()
    note: str = "reopened network cycle; TRUE not issued; chart not Closure"


@dataclass(frozen=True)
class Participant:
    participant_id: str
    kind: str  # human | autonomous_ai | sensor
    display: str


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    import uuid

    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def natural_form(symbol: str) -> NaturalForm:
    return NaturalForm(
        form_id=f"form-{symbol}",
        symbol=symbol,
        notebook_operator=(
            f"proposed device-relative realization of {symbol}; "
            "not an established physical identity"
        ),
    )
