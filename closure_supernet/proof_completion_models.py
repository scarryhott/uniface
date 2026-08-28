from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from .completion_models import (
    InvariantReadingInput,
    InvariantTruthInput,
    LocalTranslationStepInput,
)


class ProofReceiptKind(StrEnum):
    DERIVATION = "DERIVATION"
    ADMISSION = "ADMISSION"
    BALANCE = "BALANCE"


class ProofSystemCreate(BaseModel):
    """Finite executable reading of an admitted relation ``r : X → X → Prop``."""

    name: str = Field(min_length=1, max_length=500)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    presentations: list[str] = Field(min_length=1, max_length=256)
    steps: list[LocalTranslationStepInput] = Field(default_factory=list, max_length=20_000)
    readings: list[InvariantReadingInput] = Field(default_factory=list, max_length=256)
    truths: list[InvariantTruthInput] = Field(default_factory=list, max_length=256)
    continuation_system_id: str | None = None
    turing_being_life_event_id: str | None = None
    geometry_completion_system_id: str | None = None
    source_event_id: str | None = None
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_relation(self) -> "ProofSystemCreate":
        self.presentations = list(dict.fromkeys(str(item) for item in self.presentations))
        if not self.presentations:
            raise ValueError("at least one presentation is required")
        known = set(self.presentations)
        for step in self.steps:
            if step.source not in known or step.target not in known:
                raise ValueError("every admitted-step endpoint must be a submitted presentation")
        for reading in self.readings:
            if set(reading.values) != known:
                raise ValueError(
                    f"reading {reading.name!r} must assign exactly every presentation"
                )
        for truth in self.truths:
            if set(truth.values) != known:
                raise ValueError(
                    f"truth {truth.name!r} must assign exactly every presentation"
                )
        self.source_ids = list(dict.fromkeys(self.source_ids))
        return self


class DerivationCreate(BaseModel):
    source: str = Field(min_length=1, max_length=500)
    target: str = Field(min_length=1, max_length=500)
    path: list[str] | None = Field(default=None, max_length=20_001)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    source_event_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AdmissionCreate(BaseModel):
    seeds: list[str] = Field(min_length=1, max_length=256)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    source_event_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize_seeds(self) -> "AdmissionCreate":
        self.seeds = list(dict.fromkeys(self.seeds))
        return self


class BalanceCreate(BaseModel):
    left: str = Field(min_length=1, max_length=500)
    right: str = Field(min_length=1, max_length=500)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    source_event_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DerivationWitness(BaseModel):
    source: str
    target: str
    admitted: bool
    length: int | None = None
    trace: list[str] = Field(default_factory=list)
    step_labels: list[str] = Field(default_factory=list)
    step_indices: list[int] = Field(default_factory=list)
    finite: bool = True
    shortest: bool = True
    proof_relevant: bool = True
    completion_proposition: bool


class AdmissionWitness(BaseModel):
    seeds: list[str]
    admitted_set: list[str]
    extensive: bool
    monotone_by_union: bool
    idempotent: bool
    fixed_point: bool
    least_step_closed_superset: bool


class BalanceWitness(BaseModel):
    left: str
    right: str
    balanced: bool
    forward: DerivationWitness
    reverse: DerivationWitness
    balance_class: str | None = None
    geometry_related: bool
    balance_implies_geometry: bool
    geometry_implies_balance: bool
    closure_equality_under_closed_return: bool


class ProofSystem(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    name: str
    authored_by: str
    presentations: list[str]
    steps: list[LocalTranslationStepInput]
    readings: list[InvariantReadingInput]
    truths: list[InvariantTruthInput]
    continuation_system_id: str | None = None
    turing_being_life_event_id: str | None = None
    geometry_completion_system_id: str | None = None
    source_event_id: str | None = None
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    evaluation: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class ProofReceipt(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    system_id: str
    kind: ProofReceiptKind
    authored_by: str
    source_event_id: str | None = None
    payload: dict[str, Any]
    evaluation: dict[str, Any]
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class ProofFieldProjection(BaseModel):
    generated_at: str
    systems: list[ProofSystem]
    receipts: list[ProofReceipt]
    stats: dict[str, Any]
    canonical_qg: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
    formal_readings: list[str] = [
        "NRRF799",
        "NRRF802",
        "NRRF805",
        "NRRF807",
        "NRRF811",
    ]
    canonical_runtime_operation: str = "integrate"
    completion_is_proof_truncation: bool = True
    proof_fibres_remain_reopenable: bool = True
    balance_is_mutual_admission: bool = True
    geometry_does_not_replace_proof: bool = True
    canonical_derivation_selected: bool = False
    truth_issued: bool = False
