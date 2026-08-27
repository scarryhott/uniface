from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class LocalTranslationStepInput(BaseModel):
    source: str = Field(min_length=1, max_length=500)
    target: str = Field(min_length=1, max_length=500)
    label: str = Field(default="local translation", min_length=1, max_length=500)
    admitted_for_completion: bool = True
    witness: dict[str, Any] = Field(default_factory=dict)


class InvariantReadingInput(BaseModel):
    name: str = Field(min_length=1, max_length=500)
    values: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)


class InvariantTruthInput(BaseModel):
    name: str = Field(min_length=1, max_length=500)
    values: dict[str, bool]
    metadata: dict[str, Any] = Field(default_factory=dict)


class CompletionSystemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=500)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    presentations: list[str] = Field(min_length=1, max_length=256)
    steps: list[LocalTranslationStepInput] = Field(default_factory=list, max_length=20_000)
    readings: list[InvariantReadingInput] = Field(default_factory=list, max_length=256)
    truths: list[InvariantTruthInput] = Field(default_factory=list, max_length=256)
    source_event_id: str | None = None
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_system(self) -> "CompletionSystemCreate":
        self.presentations = list(dict.fromkeys(self.presentations))
        if not self.presentations:
            raise ValueError("at least one presentation is required")
        known = set(self.presentations)
        for step in self.steps:
            if step.source not in known or step.target not in known:
                raise ValueError("every step endpoint must be a submitted presentation")
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


class CompletionExtensionCreate(BaseModel):
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    added_presentations: list[str] = Field(default_factory=list, max_length=256)
    added_steps: list[LocalTranslationStepInput] = Field(default_factory=list, max_length=20_000)
    readings: list[InvariantReadingInput] | None = None
    truths: list[InvariantTruthInput] | None = None
    source_event_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CompletionMapCreate(BaseModel):
    source_system_id: str = Field(min_length=1)
    target_system_id: str = Field(min_length=1)
    mapping: dict[str, str]
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    source_event_id: str | None = None
    parent_map_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CompletionMapComposeCreate(BaseModel):
    first_map_id: str = Field(min_length=1)
    second_map_id: str = Field(min_length=1)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReachWitness(BaseModel):
    source: str
    target: str
    related: bool
    path: list[str] = Field(default_factory=list)
    step_labels: list[str] = Field(default_factory=list)
    length: int | None = None
    finite_local_lineage: bool


class GenerationStage(BaseModel):
    index: int
    related_ordered_pairs: int
    newly_related_ordered_pairs: int
    cumulative: bool = True


class CompletionClass(BaseModel):
    id: str
    representative: str
    members: list[str]
    finite_reach_from_representative: list[ReachWitness]


class ReadingReceipt(BaseModel):
    name: str
    local_invariant: bool
    global_invariant: bool
    local_iff_global: bool
    factors_through_completion: bool
    unique_factorization: bool
    quotient_values: dict[str, Any] | None = None
    decides_completion: bool
    range_values: list[Any] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TruthReceipt(BaseModel):
    name: str
    local_invariant: bool
    global_invariant: bool
    local_iff_global: bool
    factors_through_completion: bool
    quotient_values: dict[str, bool] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CompletionEvaluation(BaseModel):
    classes: list[CompletionClass]
    class_of: dict[str, str]
    generation_stages: list[GenerationStage]
    max_finite_witness_length: int
    every_identification_has_finite_local_path: bool
    no_global_jump: bool
    local_global_reading_equivalent: bool
    local_global_truth_equivalent: bool
    all_local_truths_recover_completion: bool
    canonical_class_truths: dict[str, dict[str, bool]]
    readings: list[ReadingReceipt]
    truths: list[TruthReceipt]
    pushed_step_generates_only_equality: bool
    completion_closed: bool
    completion_idempotent: bool
    quotient_map_natural: bool
    universal_factorization_available: bool
    canonical_representative_selected: bool = False
    truth_issued: bool = False


class CompletionSystem(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    name: str
    authored_by: str
    presentations: list[str]
    steps: list[LocalTranslationStepInput]
    readings: list[InvariantReadingInput]
    truths: list[InvariantTruthInput]
    source_event_id: str | None = None
    parent_system_id: str | None = None
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    evaluation: CompletionEvaluation
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class CompletionMap(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    source_system_id: str
    target_system_id: str
    mapping: dict[str, str]
    relation_preserving: bool
    induced_class_map: dict[str, str] | None = None
    map_mk_commutes: bool
    identity_map: bool
    parent_map_ids: list[str] = Field(default_factory=list)
    authored_by: str
    source_event_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class CompletionFieldProjection(BaseModel):
    generated_at: str
    systems: list[CompletionSystem]
    maps: list[CompletionMap]
    stats: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
    formal_readings: list[str] = ["NRRF798", "NRRF799"]
    canonical_runtime_operation: str = "integrate"
    local_global_same_completion: bool = True
    every_global_identification_requires_finite_local_lineage: bool = True
    truth_issued: bool = False
