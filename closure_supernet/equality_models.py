from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from .models import Verdict
from .translation_models import RelativeFormRef


class EqualityWitnessState(StrEnum):
    PROPOSED = "PROPOSED"
    REVERSIBLE = "REVERSIBLE"
    COHERENT = "COHERENT"
    ADMITTED = "ADMITTED"
    REOPENED = "REOPENED"
    REJECTED = "REJECTED"


class CoherenceSide(StrEnum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class EqualityContextCreate(BaseModel):
    label: str = Field(min_length=1, max_length=500)
    exact_source_ids: list[str] = Field(min_length=1)
    authored_by: str = Field(default="participant", min_length=1)
    participant_ids: list[str] = Field(default_factory=list)
    perspective_ids: list[str] = Field(default_factory=list)
    frame_and_scope: str = Field(default="relative interaction context", min_length=1)
    predecessor_context_id: str | None = None
    reopening_translation_id: str | None = None
    external_key: str | None = Field(default=None, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def dedupe(self) -> "EqualityContextCreate":
        self.exact_source_ids = list(dict.fromkeys(self.exact_source_ids))
        self.participant_ids = list(dict.fromkeys(self.participant_ids))
        self.perspective_ids = list(dict.fromkeys(self.perspective_ids))
        return self


class EqualityContext(EqualityContextCreate):
    id: str
    created_at: str


class RelativeEqualityCreate(BaseModel):
    context_id: str
    left_form: RelativeFormRef
    right_form: RelativeFormRef
    forward_translation_id: str
    reverse_translation_id: str | None = None
    exact_source_ids: list[str] = Field(min_length=1)
    invariant: list[str] = Field(default_factory=list)
    residue: list[str] = Field(default_factory=list)
    return_form: RelativeFormRef | None = None
    reopening_conditions: list[str] = Field(default_factory=list)
    authored_by: str = Field(default="participant", min_length=1)
    external_key: str | None = Field(default=None, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def source_reversible(self) -> "RelativeEqualityCreate":
        self.exact_source_ids = list(dict.fromkeys(self.exact_source_ids))
        if not self.invariant:
            self.invariant = ["exact source occurrences", "source reversibility"]
        if not self.reopening_conditions:
            self.reopening_conditions = [
                "new interaction, changed admission, omitted perspective, or returned consequence may reopen"
            ]
        return self


class EqualityDecisionCreate(BaseModel):
    verdict: Verdict
    reason: str = Field(min_length=1)
    decided_by: str = Field(default="participant", min_length=1)
    scope: str = Field(default="context-relative admission", min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EqualityDecisionRecord(EqualityDecisionCreate):
    id: str
    witness_id: str
    created_at: str


class RelativeEqualityWitness(RelativeEqualityCreate):
    id: str
    current_state: EqualityWitnessState
    current_verdict: Verdict
    current_reason: str
    reversible: bool
    coherent: bool
    eligible_for_true: bool
    left_coherence_id: str | None = None
    right_coherence_id: str | None = None
    decision_history: list[EqualityDecisionRecord] = Field(default_factory=list)
    created_at: str


class ReturnCoherenceCreate(BaseModel):
    witness_id: str
    side: CoherenceSide
    path_translation_ids: list[str] = Field(min_length=2)
    return_form: RelativeFormRef
    exact_source_ids: list[str] = Field(min_length=1)
    preserved: list[str] = Field(default_factory=list)
    residue: list[str] = Field(default_factory=list)
    authored_by: str = Field(default="participant", min_length=1)
    external_key: str | None = Field(default=None, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def dedupe(self) -> "ReturnCoherenceCreate":
        self.path_translation_ids = list(dict.fromkeys(self.path_translation_ids))
        self.exact_source_ids = list(dict.fromkeys(self.exact_source_ids))
        if not self.preserved:
            self.preserved = ["return to the same context-relative form"]
        return self


class CoherenceDecisionRecord(EqualityDecisionCreate):
    id: str
    coherence_id: str
    created_at: str


class ReturnCoherence(ReturnCoherenceCreate):
    id: str
    path_admitted: bool
    current_verdict: Verdict
    current_reason: str
    decision_history: list[CoherenceDecisionRecord] = Field(default_factory=list)
    created_at: str


class EqualityContextReopenCreate(BaseModel):
    label: str = Field(min_length=1, max_length=500)
    exact_source_ids: list[str] = Field(min_length=1)
    reopening_translation_id: str
    authored_by: str = Field(default="participant", min_length=1)
    frame_and_scope: str = Field(default="successor relative-equality context", min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EqualityChartCreate(BaseModel):
    context_id: str | None = None
    name: str = Field(min_length=1, max_length=500)
    exact_source_ids: list[str] = Field(min_length=1)
    carrier_context: str = Field(min_length=1)
    generator: str = Field(min_length=1)
    inverse_reading: str = Field(min_length=1)
    invariant: list[str] = Field(default_factory=list)
    residue: list[str] = Field(default_factory=list)
    return_form: str = Field(min_length=1)
    reopening: str = Field(min_length=1)
    authored_by: str = Field(default="participant", min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def dedupe(self) -> "EqualityChartCreate":
        self.exact_source_ids = list(dict.fromkeys(self.exact_source_ids))
        return self


class EqualityChart(EqualityChartCreate):
    id: str
    created_at: str


class NaturalFormComponent(BaseModel):
    id: str
    context_id: str
    member_forms: list[RelativeFormRef]
    witness_ids: list[str]
    exact_source_ids: list[str]
    form_labels: list[str]
    language_labels: list[str]
    canonical_form: None = None
    canonical_language: None = None


class RelativeEqualityFieldProjection(BaseModel):
    contexts: list[EqualityContext]
    witnesses: list[RelativeEqualityWitness]
    coherences: list[ReturnCoherence]
    charts: list[EqualityChart]
    natural_components: list[NaturalFormComponent]
    stats: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
    closure_relations: list[str]
    context_indexed: bool = True
    witness_valued: bool = True
    directed_translation_precedes_equality: bool = True
    automatic_global_truth: bool = False
    canonical_language_selected: bool = False
    protocol_is_transport_only: bool = True
