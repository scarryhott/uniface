from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class Hand(StrEnum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"

    @property
    def inverse(self) -> "Hand":
        return Hand.RIGHT if self == Hand.LEFT else Hand.LEFT


class MotionKind(StrEnum):
    BALL_RETURN = "BALL_RETURN"
    HAIR_RETURN = "HAIR_RETURN"
    SELF_LIMIT = "SELF_LIMIT"


class HandedRecordKind(StrEnum):
    MOTION_TRACE = "MOTION_TRACE"
    HUMAN_RELATION = "HUMAN_RELATION"


class LifeState(BaseModel):
    hand: Hand
    ball_phase: int = Field(ge=0, lt=4)
    hair_class: str = "hair:unit"
    temporal_role: str


class HandedLifeSystemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=500)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    initial_hand: Hand = Hand.LEFT
    initial_ball_phase: int = Field(default=0, ge=0, lt=4)
    source_event_id: str | None = None
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize_sources(self) -> "HandedLifeSystemCreate":
        self.source_ids = list(dict.fromkeys(self.source_ids))
        return self


class HandedMotionCreate(BaseModel):
    system_id: str = Field(min_length=1)
    motion: MotionKind
    steps: int = Field(default=1, ge=0, le=10000)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    start_hand: Hand | None = None
    start_ball_phase: int | None = Field(default=None, ge=0, lt=4)
    source_event_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize_sources(self) -> "HandedMotionCreate":
        self.source_ids = list(dict.fromkeys(self.source_ids))
        return self


class HumanRelationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=500)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    source_participant: str = Field(min_length=1, max_length=500)
    target_participant: str = Field(min_length=1, max_length=500)
    source_standing: int
    target_standing: int
    gate_hand: Hand = Hand.LEFT
    common_shift: int = 7
    after_source_standing: int | None = None
    after_target_standing: int | None = None
    source_event_id: str | None = None
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_relation(self) -> "HumanRelationCreate":
        if self.source_participant == self.target_participant:
            raise ValueError("source_participant and target_participant must be distinct")
        paired = (self.after_source_standing is None) == (
            self.after_target_standing is None
        )
        if not paired:
            raise ValueError(
                "after_source_standing and after_target_standing must be supplied together"
            )
        self.source_ids = list(dict.fromkeys(self.source_ids))
        return self


class HandedLifeSystem(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    name: str
    authored_by: str
    initial_hand: Hand
    initial_ball_phase: int
    source_event_id: str | None = None
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    evaluation: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class HandedLifeRecord(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    kind: HandedRecordKind
    system_id: str | None = None
    name: str
    authored_by: str
    source_event_id: str | None = None
    payload: dict[str, Any]
    evaluation: dict[str, Any]
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class HandedLifeFieldProjection(BaseModel):
    generated_at: str
    systems: list[HandedLifeSystem]
    records: list[HandedLifeRecord]
    stats: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
    formal_readings: list[str] = ["NRRF799", "NRRF800"]
    canonical_runtime_operation: str = "integrate"
    ball_sheaves: int = 4
    hair_sheaves: int = 1
    biological_claimed: bool = False
    human_law_claimed: bool = False
    truth_issued: bool = False
