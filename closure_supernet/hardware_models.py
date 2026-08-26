from __future__ import annotations

import math
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from .models import EvidenceStatus, Verdict


class HardwareDeviceKind(StrEnum):
    """Safe device drivers shipped with Closure Supernet.

    The first implementation deliberately contains only simulated devices. A
    physical adapter can implement the same interface later, but it is not
    enabled merely by naming a device or setting an environment variable.
    """

    SIMULATED_OPTICAL_ELLIPSE = "SIMULATED_OPTICAL_ELLIPSE"
    SIMULATED_SENSOR_LOOP = "SIMULATED_SENSOR_LOOP"


class HardwareDeviceState(StrEnum):
    REGISTERED = "REGISTERED"
    READY = "READY"
    DISABLED = "DISABLED"


class HardwareConstraintState(StrEnum):
    PROPOSED = "PROPOSED"
    SIMULATED = "SIMULATED"
    ADMITTED = "ADMITTED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    EXPIRED = "EXPIRED"
    REOPENED = "REOPENED"


class HardwareReturnState(StrEnum):
    PENDING = "PENDING"
    REINTEGRATED_OPEN = "REINTEGRATED_OPEN"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"


class ControlBound(BaseModel):
    minimum: float = -1.0
    maximum: float = 1.0
    neutral: float = 0.0

    @model_validator(mode="after")
    def valid_bound(self) -> "ControlBound":
        values = (self.minimum, self.maximum, self.neutral)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Control bounds must be finite")
        if self.minimum > self.maximum:
            raise ValueError("Control minimum cannot exceed maximum")
        if not self.minimum <= self.neutral <= self.maximum:
            raise ValueError("Control neutral must lie inside its bound")
        return self


class HardwareDeviceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=240)
    exact_description: str = Field(min_length=1)
    created_by: str = Field(min_length=1)
    kind: HardwareDeviceKind = HardwareDeviceKind.SIMULATED_OPTICAL_ELLIPSE
    capabilities: list[str] = Field(default_factory=list)
    control_channels: list[str] = Field(default_factory=list)
    safety_envelope: dict[str, ControlBound] = Field(default_factory=dict)
    minimum_approvals: int = Field(default=1, ge=1, le=16)
    max_duration_seconds: float = Field(default=5.0, gt=0.0, le=60.0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def simulated_and_bounded(self) -> "HardwareDeviceCreate":
        if not self.control_channels:
            if self.kind == HardwareDeviceKind.SIMULATED_OPTICAL_ELLIPSE:
                self.control_channels = [
                    "phase_x",
                    "phase_y",
                    "polarization",
                    "intensity",
                ]
            else:
                self.control_channels = ["sensor_gain", "loop_bias", "return_mix"]
        self.control_channels = list(dict.fromkeys(self.control_channels))
        if not self.safety_envelope:
            self.safety_envelope = {
                channel: ControlBound(
                    minimum=0.0 if "intensity" in channel or "gain" in channel else -1.0,
                    maximum=1.0,
                    neutral=0.0,
                )
                for channel in self.control_channels
            }
        missing = [
            channel for channel in self.control_channels if channel not in self.safety_envelope
        ]
        if missing:
            raise ValueError(f"Missing safety bounds for controls: {missing}")
        return self


class HardwareDevice(BaseModel):
    id: str
    occurrence_id: str
    name: str
    kind: HardwareDeviceKind
    created_by: str
    capabilities: list[str]
    control_channels: list[str]
    safety_envelope: dict[str, ControlBound]
    minimum_approvals: int
    max_duration_seconds: float
    driver: str
    state: HardwareDeviceState
    metadata: dict[str, Any]
    created_at: str


class HardwareConstraintSynthesisCreate(BaseModel):
    device_id: str
    created_by: str
    exact_intent: str = Field(min_length=1)
    source_occurrence_ids: list[str] = Field(min_length=1)
    source_translation_ids: list[str] = Field(default_factory=list)
    source_interaction_ids: list[str] = Field(default_factory=list)
    participant_ids: list[str] = Field(default_factory=list)
    agent_ids: list[str] = Field(default_factory=list)
    affected_perspectives: list[str] = Field(default_factory=list)
    duration_seconds: float | None = Field(default=None, gt=0.0, le=60.0)
    expected_return: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class HardwareConstraintCreate(BaseModel):
    device_id: str
    created_by: str
    exact_intent: str = Field(min_length=1)
    source_occurrence_ids: list[str] = Field(min_length=1)
    source_translation_ids: list[str] = Field(default_factory=list)
    source_interaction_ids: list[str] = Field(default_factory=list)
    participant_ids: list[str] = Field(default_factory=list)
    agent_ids: list[str] = Field(default_factory=list)
    affected_perspectives: list[str] = Field(default_factory=list)
    selected_metavector: list[float] = Field(min_length=1)
    control_values: dict[str, float] = Field(min_length=1)
    duration_seconds: float = Field(gt=0.0, le=60.0)
    expected_return: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def finite_controls(self) -> "HardwareConstraintCreate":
        if not all(math.isfinite(value) for value in self.selected_metavector):
            raise ValueError("Metavector values must be finite")
        if not all(math.isfinite(value) for value in self.control_values.values()):
            raise ValueError("Control values must be finite")
        return self


class HardwareConstraintDecisionCreate(BaseModel):
    verdict: Verdict
    reason: str = Field(min_length=1)
    decided_by: str = Field(min_length=1)


class HardwareConstraintSimulationCreate(BaseModel):
    requested_by: str = Field(min_length=1)


class HardwareConstraintExecutionCreate(BaseModel):
    requested_by: str = Field(min_length=1)


class HardwareConstraintStateRecord(BaseModel):
    id: str
    constraint_id: str
    state: HardwareConstraintState
    verdict: Verdict
    reason: str
    actor_id: str
    metadata: dict[str, Any]
    created_at: str


class HardwareConstraintDecision(BaseModel):
    id: str
    constraint_id: str
    verdict: Verdict
    reason: str
    decided_by: str
    created_at: str


class HardwareConstraint(BaseModel):
    id: str
    occurrence_id: str
    translation_id: str | None
    device_id: str
    created_by: str
    source_occurrence_ids: list[str]
    source_translation_ids: list[str]
    source_interaction_ids: list[str]
    participant_ids: list[str]
    agent_ids: list[str]
    affected_perspectives: list[str]
    selected_metavector: list[float]
    control_values: dict[str, float]
    duration_seconds: float
    expected_return: dict[str, Any]
    expires_at: str
    metadata: dict[str, Any]
    current_state: HardwareConstraintState
    current_verdict: Verdict
    state_history: list[HardwareConstraintStateRecord]
    decisions: list[HardwareConstraintDecision]
    created_at: str


class HardwareTwinRun(BaseModel):
    id: str
    constraint_id: str
    requested_by: str
    driver: str
    input_controls: dict[str, float]
    output_reading: dict[str, Any]
    metrics: dict[str, float]
    safe: bool
    reason: str
    created_at: str


class HardwareActuationReceipt(BaseModel):
    id: str
    constraint_id: str
    twin_run_id: str
    requested_by: str
    mode: str
    control_values: dict[str, float]
    output_reading: dict[str, Any]
    status: str
    return_id: str | None
    created_at: str


class HardwareReturn(BaseModel):
    id: str
    actuation_id: str
    constraint_id: str
    device_id: str
    occurrence_id: str
    authored_by: str
    sensor_reading: dict[str, Any]
    evidence_status: EvidenceStatus
    reintegration_status: HardwareReturnState
    translation_id: str | None
    metadata: dict[str, Any]
    created_at: str
    updated_at: str


class HardwareFieldProjection(BaseModel):
    generated_at: str
    devices: list[HardwareDevice]
    constraints: list[HardwareConstraint]
    twin_runs: list[HardwareTwinRun]
    actuations: list[HardwareActuationReceipt]
    returns: list[HardwareReturn]
    stats: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
    direct_physical_actuation: bool = False
    high_energy_actuation: bool = False
    simulation_only: bool = True
    closure_reading: str = (
        "digital interaction selects a temporary bounded device constraint; "
        "the simulated physical return re-enters the living translation field"
    )
