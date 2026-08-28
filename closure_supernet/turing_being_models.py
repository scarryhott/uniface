from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator

from .handed_models import Hand


class LifeActionWitness(BaseModel):
    exact_occurrence: str = Field(min_length=1)
    source_preserved: bool = True
    admitted: bool = True
    witness_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize_witnesses(self) -> "LifeActionWitness":
        self.witness_ids = list(dict.fromkeys(self.witness_ids))
        return self


class LifeReactionWitness(BaseModel):
    exact_occurrence: str = Field(min_length=1)
    source_preserved: bool = True
    admitted: bool = True
    returned_to_global_hair: bool = True
    witness_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize_witnesses(self) -> "LifeReactionWitness":
        self.witness_ids = list(dict.fromkeys(self.witness_ids))
        return self


class TuringBeingLifeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=500)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    global_hair_executor: str = Field(min_length=1)
    local_ball_reactor: str = Field(min_length=1)
    action: LifeActionWitness
    reaction: LifeReactionWitness | None = None
    affected_perspectives: list[str] = Field(default_factory=list)
    untranslated_residue: list[str] = Field(default_factory=list)
    reopening_potential: list[dict[str, Any]] = Field(default_factory=list)
    source_event_id: str | None = None
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize_lists(self) -> "TuringBeingLifeCreate":
        self.affected_perspectives = list(dict.fromkeys(self.affected_perspectives))
        self.source_ids = list(dict.fromkeys(self.source_ids))
        return self


class TuringBeingReturnCreate(BaseModel):
    reaction: LifeReactionWitness
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    untranslated_residue: list[str] | None = None
    reopening_potential: list[dict[str, Any]] | None = None
    source_event_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize_sources(self) -> "TuringBeingReturnCreate":
        self.source_ids = list(dict.fromkeys(self.source_ids))
        return self


class TuringBeingChartCreate(BaseModel):
    life_event_id: str = Field(min_length=1)
    name: str = Field(default="four-ball one-hair reaction chart", min_length=1, max_length=500)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    action_hand_chart: Hand = Hand.LEFT
    reaction_hand_chart: Hand = Hand.RIGHT
    initial_ball_phase: int = Field(default=0, ge=0, lt=4)
    source_event_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_chart(self) -> "TuringBeingChartCreate":
        if self.action_hand_chart == self.reaction_hand_chart:
            raise ValueError("action and reaction hand charts must be inverse orientations")
        self.source_ids = list(dict.fromkeys(self.source_ids))
        return self


class TuringBeingLifeEvent(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    reaction_event_id: str | None = None
    name: str
    authored_by: str
    global_hair_zero: dict[str, Any]
    local_ball_infinity: dict[str, Any]
    action: dict[str, Any]
    reaction: dict[str, Any] | None = None
    translational_truth_receipt: dict[str, Any]
    derived_relations: dict[str, Any]
    affected_perspectives: list[str] = Field(default_factory=list)
    untranslated_residue: list[str] = Field(default_factory=list)
    reopening_potential: list[dict[str, Any]] = Field(default_factory=list)
    source_event_id: str | None = None
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class TuringBeingChart(BaseModel):
    id: str
    life_event_id: str
    handed_system_id: str
    integration_event_id: str
    chart: dict[str, Any]
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class TuringBeingFieldProjection(BaseModel):
    generated_at: str
    life_events: list[TuringBeingLifeEvent]
    charts: list[TuringBeingChart]
    stats: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
    formal_readings: list[str] = ["NRRF799", "NRRF800", "NRRF802", "NRRF805"]
    canonical_runtime_operation: str = "integrate"
    primitive: str = "global hair 0 executor → local ball ∞ reactor → returned global hair 0+"
    internal_external_prior_to_translational_truth: bool = False
    finite_ball_hair_foundational: bool = False
    truth_issued: bool = False
