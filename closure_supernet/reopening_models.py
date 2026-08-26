from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class ReopeningMode(StrEnum):
    TRIVIAL = "TRIVIAL"
    SINGLE_REMOVAL = "SINGLE_REMOVAL"
    JOINT_SUSPENSION = "JOINT_SUSPENSION"
    POWERSET = "POWERSET"
    CUSTOM = "CUSTOM"


class ReopeningProcessState(StrEnum):
    ACTIVE = "ACTIVE"
    STABLE_AT_CURRENT_FINITE_SCOPE = "STABLE_AT_CURRENT_FINITE_SCOPE"
    MAX_ROUNDS_REACHED = "MAX_ROUNDS_REACHED"
    REOPENED = "REOPENED"


class ResidueRoundState(StrEnum):
    STRICTLY_REOPENED = "STRICTLY_REOPENED"
    STABLE_AT_CURRENT_FINITE_SCOPE = "STABLE_AT_CURRENT_FINITE_SCOPE"
    EMPTY_RESIDUE = "EMPTY_RESIDUE"


class OrderEffect(StrEnum):
    SAME_READING = "SAME_READING"
    CONTENT_PRESERVING = "CONTENT_PRESERVING"
    MEANING_CHANGING = "MEANING_CHANGING"
    NOT_COMPARABLE = "NOT_COMPARABLE"


class ClosureRuleSpec(BaseModel):
    premise_occurrence_ids: list[str] = Field(default_factory=list)
    conclusion_occurrence_id: str
    label: str | None = None


class ReopeningVariantSpec(BaseModel):
    label: str = Field(min_length=1, max_length=240)
    held_occurrence_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReopeningFamilyCreate(BaseModel):
    problem_id: str
    name: str = Field(min_length=1, max_length=300)
    created_by: str
    assumption_occurrence_ids: list[str] = Field(min_length=1)
    mode: ReopeningMode = ReopeningMode.CUSTOM
    joint_suspensions: list[list[str]] = Field(default_factory=list)
    custom_variants: list[ReopeningVariantSpec] = Field(default_factory=list)
    closure_rules: list[ClosureRuleSpec] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_family(self) -> "ReopeningFamilyCreate":
        if len(set(self.assumption_occurrence_ids)) != len(self.assumption_occurrence_ids):
            raise ValueError("Assumption occurrences must be unique while retaining their order")
        if self.mode == ReopeningMode.CUSTOM and not self.custom_variants:
            raise ValueError("CUSTOM reopening requires at least one explicit variant")
        if self.mode == ReopeningMode.JOINT_SUSPENSION and not self.joint_suspensions:
            raise ValueError("JOINT_SUSPENSION requires at least one suspension set")
        return self


class ReopeningVariant(BaseModel):
    id: str
    family_id: str
    label: str
    held_occurrence_ids: list[str]
    closure_occurrence_ids: list[str]
    order_index: int
    metadata: dict[str, Any]
    created_at: str


class ReopeningFamily(BaseModel):
    id: str
    problem_id: str
    name: str
    created_by: str
    assumption_occurrence_ids: list[str]
    mode: ReopeningMode
    closure_rules: list[ClosureRuleSpec]
    remaining_star_ids: list[str]
    closure_verified: bool
    variants: list[ReopeningVariant]
    metadata: dict[str, Any]
    created_at: str


class OrderedReadingCreate(BaseModel):
    problem_id: str
    participant_id: str
    exact_text: str = Field(min_length=1)
    held_occurrence_ids: list[str] = Field(min_length=1)
    dependency_edges: list[tuple[str, str]] = Field(default_factory=list)
    meaning_key: str = Field(min_length=1, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_reading(self) -> "OrderedReadingCreate":
        if len(set(self.held_occurrence_ids)) != len(self.held_occurrence_ids):
            raise ValueError("A held ordered reading cannot repeat an occurrence")
        held = set(self.held_occurrence_ids)
        for source, target in self.dependency_edges:
            if source not in held or target not in held:
                raise ValueError("Dependency edges must refer to held occurrences")
        return self


class OrderedReading(BaseModel):
    id: str
    problem_id: str
    participant_id: str
    occurrence_id: str
    held_occurrence_ids: list[str]
    dependency_edges: list[tuple[str, str]]
    meaning_key: str
    metadata: dict[str, Any]
    created_at: str


class OrderAssessment(BaseModel):
    id: str
    left_reading_id: str
    right_reading_id: str
    same_content: bool
    order_changed: bool
    effect: OrderEffect
    rationale: str
    created_at: str


class ReopeningProcessCreate(BaseModel):
    problem_id: str
    name: str = Field(min_length=1, max_length=300)
    created_by: str
    initial_assumption_ids: list[str] = Field(min_length=1)
    mode: ReopeningMode = ReopeningMode.SINGLE_REMOVAL
    joint_suspensions: list[list[str]] = Field(default_factory=list)
    closure_rules: list[ClosureRuleSpec] = Field(default_factory=list)
    max_rounds: int = Field(default=32, ge=1, le=512)
    previous_process_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_process(self) -> "ReopeningProcessCreate":
        if self.mode == ReopeningMode.CUSTOM:
            raise ValueError("Iterated processes require a generative family mode, not CUSTOM")
        if self.mode == ReopeningMode.JOINT_SUSPENSION and not self.joint_suspensions:
            raise ValueError("JOINT_SUSPENSION requires at least one suspension set")
        if len(set(self.initial_assumption_ids)) != len(self.initial_assumption_ids):
            raise ValueError("Initial assumptions must be unique")
        return self


class ReopeningProcess(BaseModel):
    id: str
    problem_id: str
    name: str
    created_by: str
    mode: ReopeningMode
    initial_assumption_ids: list[str]
    joint_suspensions: list[list[str]]
    closure_rules: list[ClosureRuleSpec]
    max_rounds: int
    state: ReopeningProcessState
    previous_process_id: str | None
    metadata: dict[str, Any]
    created_at: str


class ResidueRound(BaseModel):
    id: str
    process_id: str
    round_index: int
    input_assumption_ids: list[str]
    family_id: str
    remaining_star_ids: list[str]
    closed: bool
    strictly_reopened: bool
    state: ResidueRoundState
    previous_round_id: str | None
    created_at: str


class MoralConnectionCreate(BaseModel):
    round_id: str
    participant_a_id: str
    participant_b_id: str
    understanding_a_ids: list[str] = Field(default_factory=list)
    understanding_b_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MoralConnection(BaseModel):
    id: str
    round_id: str
    participant_a_id: str
    participant_b_id: str
    understanding_a_ids: list[str]
    understanding_b_ids: list[str]
    residue_ids: list[str]
    agrees_on_residue: bool
    plurality_a_ids: list[str]
    plurality_b_ids: list[str]
    metadata: dict[str, Any]
    created_at: str


class ReopeningProjection(BaseModel):
    generated_at: str
    families: list[ReopeningFamily]
    ordered_readings: list[OrderedReading]
    order_assessments: list[OrderAssessment]
    processes: list[ReopeningProcess]
    rounds: list[ResidueRound]
    moral_connections: list[MoralConnection]
    stats: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
