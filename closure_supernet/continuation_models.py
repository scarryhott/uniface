from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class ContinuationSystemCreate(BaseModel):
    """One finite executable chart of a pointed translation ``(X, step, origin)``."""

    name: str = Field(min_length=1, max_length=500)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    presentations: list[str] = Field(min_length=1, max_length=256)
    step: dict[str, str]
    origin: str = Field(min_length=1, max_length=500)
    step_label: str = Field(default="translation step", min_length=1, max_length=500)
    continuation_horizon: int = Field(default=16, ge=0, le=20_000)
    turing_being_life_event_id: str | None = None
    source_event_id: str | None = None
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_translation(self) -> "ContinuationSystemCreate":
        self.presentations = list(dict.fromkeys(str(item) for item in self.presentations))
        if not self.presentations:
            raise ValueError("at least one presentation is required")
        known = set(self.presentations)
        self.step = {str(key): str(value) for key, value in self.step.items()}
        if set(self.step) != known:
            raise ValueError("step must assign exactly every submitted presentation")
        if any(value not in known for value in self.step.values()):
            raise ValueError("every step value must be a submitted presentation")
        if self.origin not in known:
            raise ValueError("origin must be a submitted presentation")
        self.source_ids = list(dict.fromkeys(self.source_ids))
        return self


class ContinuationMapCreate(BaseModel):
    source_system_id: str = Field(min_length=1)
    target_system_id: str = Field(min_length=1)
    mapping: dict[str, str]
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    source_event_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RuleWitness(BaseModel):
    source: str
    target: str
    related: bool
    iterate: int | None = None
    path: list[str] = Field(default_factory=list)
    exact_unfolded_path: bool
    directed: bool = True


class GeometryWitness(BaseModel):
    source: str
    target: str
    related: bool
    closure_class: str | None = None
    meeting_value: str | None = None
    source_iterate: int | None = None
    target_iterate: int | None = None
    source_path: list[str] = Field(default_factory=list)
    target_path: list[str] = Field(default_factory=list)
    continuations_meet: bool
    forward_rule_source_to_target: bool
    forward_rule_target_to_source: bool
    symmetry_added_by_geometry: bool


class ContinuationPoint(BaseModel):
    index: int
    presentation: str
    closure_class: str


class ContinuationSystem(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    completion_system_id: str
    proof_system_id: str | None = None
    name: str
    authored_by: str
    presentations: list[str]
    step: dict[str, str]
    origin: str
    step_label: str
    continuation_horizon: int
    turing_being_life_event_id: str | None = None
    source_event_id: str | None = None
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    evaluation: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str

    @model_validator(mode="before")
    @classmethod
    def derive_proof_system_id(cls, value: Any) -> Any:
        if isinstance(value, dict) and not value.get("proof_system_id"):
            copied = dict(value)
            copied["proof_system_id"] = (
                dict(copied.get("metadata") or {}).get("proof_system_id")
                or dict(copied.get("evaluation") or {}).get("proof_system_id")
            )
            return copied
        return value


class ContinuationMap(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    completion_map_id: str
    source_system_id: str
    target_system_id: str
    mapping: dict[str, str]
    authored_by: str
    source_event_id: str | None = None
    evaluation: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class ContinuationFieldProjection(BaseModel):
    generated_at: str
    systems: list[ContinuationSystem]
    maps: list[ContinuationMap]
    stats: dict[str, Any]
    canonical_examples: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
    formal_readings: list[str] = [
        "NRRF799",
        "NRRF802",
        "NRRF805",
        "NRRF807",
        "NRRF811",
    ]
    canonical_runtime_operation: str = "integrate"
    rule_and_geometry_are_lenses: bool = True
    proof_completion_linked: bool = True
    rule_direction_preserved: bool = True
    geometry_does_not_fabricate_rule_witness: bool = True
    truth_issued: bool = False
