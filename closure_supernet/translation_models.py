from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from .models import EvidenceStatus, Verdict


class TranslationKind(StrEnum):
    SOURCE_RELATION = "SOURCE_RELATION"
    NOTE_LOOP_STEP = "NOTE_LOOP_STEP"
    PROBLEM_INTERACTION = "PROBLEM_INTERACTION"
    SOLUTION_RETURN = "SOLUTION_RETURN"
    COLLECTIVE_ACTION = "COLLECTIVE_ACTION"
    ACTION_CONSEQUENCE = "ACTION_CONSEQUENCE"
    LANGUAGE_TRANSLATION = "LANGUAGE_TRANSLATION"
    FRAME_TRANSLATION = "FRAME_TRANSLATION"
    FORMALIZATION = "FORMALIZATION"
    REOPENING = "REOPENING"
    RESIDUE_RETURN = "RESIDUE_RETURN"
    ORDER_EFFECT = "ORDER_EFFECT"
    RULE_REINTERPRETATION = "RULE_REINTERPRETATION"
    COMPOSED = "COMPOSED"


class TranslationState(StrEnum):
    PROPOSED = "PROPOSED"
    INTERPRETED = "INTERPRETED"
    ADMITTED = "ADMITTED"
    RETURNED = "RETURNED"
    REOPENED = "REOPENED"
    REJECTED = "REJECTED"


class TranslationRole(StrEnum):
    SOURCE = "SOURCE"
    TARGET = "TARGET"
    RETURN = "RETURN"
    SUCCESSOR_POTENTIAL = "SUCCESSOR_POTENTIAL"
    AFFECTED = "AFFECTED"


class RelativeFormRef(BaseModel):
    form_type: str = Field(min_length=1, max_length=120)
    form_id: str = Field(min_length=1, max_length=500)
    occurrence_id: str | None = None
    role: TranslationRole = TranslationRole.SOURCE
    label: str | None = Field(default=None, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TranslationEventCreate(BaseModel):
    kind: TranslationKind = TranslationKind.SOURCE_RELATION
    exact_source_ids: list[str] = Field(min_length=1)
    source_forms: list[RelativeFormRef] = Field(min_length=1)
    target_forms: list[RelativeFormRef] = Field(default_factory=list)
    participant_ids: list[str] = Field(default_factory=list)
    participating_perspective_ids: list[str] = Field(default_factory=list)
    interaction_trace_ids: list[str] = Field(default_factory=list)
    relation_type: str = Field(default="OPEN_RELATION", min_length=1, max_length=200)
    preserves: list[str] = Field(default_factory=list)
    transforms: list[str] = Field(default_factory=list)
    untranslated: list[str] = Field(default_factory=list)
    affected_perspectives: list[str] = Field(default_factory=list)
    frame_and_scope: str = Field(default="relative interaction field", min_length=1)
    admission_scope: str = Field(default="local provisional admission", min_length=1)
    reopening_conditions: list[str] = Field(default_factory=list)
    predecessor_translation_ids: list[str] = Field(default_factory=list)
    successor_potential: list[RelativeFormRef] = Field(default_factory=list)
    evidence_status: EvidenceStatus = EvidenceStatus.INTERPRETED_RELATION
    generated_by: str = Field(default="participant", min_length=1)
    external_key: str | None = Field(default=None, max_length=500)
    transport: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def source_reversible(self) -> "TranslationEventCreate":
        self.exact_source_ids = list(dict.fromkeys(self.exact_source_ids))
        self.predecessor_translation_ids = list(
            dict.fromkeys(self.predecessor_translation_ids)
        )
        if not self.preserves:
            self.preserves = ["exact source occurrences", "source reversibility"]
        if not self.reopening_conditions:
            self.reopening_conditions = [
                "new interaction, omitted perspective or returned consequence may reopen"
            ]
        return self


class TranslationStateCreate(BaseModel):
    state: TranslationState
    verdict: Verdict = Verdict.OPEN
    reason: str = Field(min_length=1)
    actor_id: str = Field(default="runtime", min_length=1)
    interpretation_id: str | None = None
    admission_id: str | None = None
    returned_form: RelativeFormRef | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TranslationStateRecord(BaseModel):
    id: str
    translation_id: str
    state: TranslationState
    verdict: Verdict
    reason: str
    actor_id: str
    interpretation_id: str | None
    admission_id: str | None
    returned_form: RelativeFormRef | None
    metadata: dict[str, Any]
    created_at: str


class TranslationEvent(BaseModel):
    id: str
    kind: TranslationKind
    exact_source_ids: list[str]
    source_forms: list[RelativeFormRef]
    target_forms: list[RelativeFormRef]
    participant_ids: list[str]
    participating_perspective_ids: list[str]
    interaction_trace_ids: list[str]
    relation_type: str
    preserves: list[str]
    transforms: list[str]
    untranslated: list[str]
    affected_perspectives: list[str]
    frame_and_scope: str
    admission_scope: str
    reopening_conditions: list[str]
    predecessor_translation_ids: list[str]
    successor_potential: list[RelativeFormRef]
    evidence_status: EvidenceStatus
    generated_by: str
    external_key: str | None
    transport: dict[str, Any]
    metadata: dict[str, Any]
    current_state: TranslationState
    current_verdict: Verdict
    state_history: list[TranslationStateRecord]
    created_at: str


class TranslationCompositionCreate(BaseModel):
    predecessor_translation_ids: list[str] = Field(min_length=2)
    generated_by: str = Field(default="participant", min_length=1)
    frame_and_scope: str = Field(default="composed relative translation", min_length=1)
    relation_type: str = Field(default="COMPOSED_TRANSLATION", min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TranslationFieldProjection(BaseModel):
    generated_at: str
    translations: list[TranslationEvent]
    edges: list[dict[str, Any]]
    open_translations: list[str]
    returned_translations: list[str]
    reopened_translations: list[str]
    derived_views: dict[str, list[str]]
    stats: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
    protocol_is_transport_only: bool = True
    closure_reading: str = "translational truth through interaction"
