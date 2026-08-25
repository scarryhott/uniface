from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from .models import EvidenceStatus, Verdict


class Visibility(StrEnum):
    PRIVATE = "PRIVATE"
    SHARED = "SHARED"
    COMMUNITY = "COMMUNITY"
    PUBLIC = "PUBLIC"
    PSEUDONYMOUS_PUBLIC = "PSEUDONYMOUS_PUBLIC"


class ProblemState(StrEnum):
    OPEN = "OPEN"
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    LOCALLY_SETTLED = "LOCALLY_SETTLED"
    REOPENED = "REOPENED"


class ActionState(StrEnum):
    PROPOSED = "PROPOSED"
    COMMITTED = "COMMITTED"
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    REOPENED = "REOPENED"


class InteractionKind(StrEnum):
    NOTE = "NOTE"
    QUESTION = "QUESTION"
    INTERPRETATION = "INTERPRETATION"
    TRANSLATION = "TRANSLATION"
    ACTION_PROPOSAL = "ACTION_PROPOSAL"
    RETURN = "RETURN"
    REINTERPRETATION = "REINTERPRETATION"


class ReintegrationStatus(StrEnum):
    OPEN = "OPEN"
    AUTHOR_CONFIRMED = "AUTHOR_CONFIRMED"
    REJECTED = "REJECTED"


class ParticipantCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=200)
    public_key: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Participant(BaseModel):
    id: str
    display_name: str
    public_key: str | None
    metadata: dict[str, Any]
    created_at: str


class PerspectiveCreate(BaseModel):
    participant_id: str
    label: str = Field(min_length=1, max_length=200)
    description: str = Field(default="")
    visibility: Visibility = Visibility.PUBLIC
    parent_perspective_id: str | None = None
    source_occurrence_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Perspective(BaseModel):
    id: str
    participant_id: str
    label: str
    description: str
    visibility: Visibility
    parent_perspective_id: str | None
    source_occurrence_id: str | None
    metadata: dict[str, Any]
    created_at: str


class ProblemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    exact_text: str = Field(min_length=1)
    situations: list[str] = Field(min_length=1)
    created_by: str
    perspective_id: str | None = None
    visibility: Visibility = Visibility.PUBLIC
    affected_perspectives: list[str] = Field(default_factory=list)
    language_label: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def problem_is_real(self) -> "ProblemCreate":
        if not any(item.strip() for item in self.situations):
            raise ValueError("A real problem must present at least one non-empty situation")
        return self


class ProblemStateChange(BaseModel):
    state: ProblemState
    reason: str = Field(min_length=1)
    actor_id: str


class Problem(BaseModel):
    id: str
    occurrence_id: str
    title: str
    situations: list[str]
    created_by: str
    perspective_id: str | None
    visibility: Visibility
    affected_perspectives: list[str]
    language_label: str | None
    metadata: dict[str, Any]
    current_state: ProblemState
    created_at: str


class NoteCreate(BaseModel):
    author_id: str
    exact_text: str = Field(min_length=1)
    perspective_id: str | None = None
    visibility: Visibility = Visibility.PUBLIC
    affected_perspectives: list[str] = Field(default_factory=list)
    source_context: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class InteractionCreate(BaseModel):
    from_problem_id: str
    to_problem_id: str | None = None
    author_id: str
    exact_text: str = Field(min_length=1)
    kind: InteractionKind = InteractionKind.INTERPRETATION
    source_perspective_id: str | None = None
    target_perspective_id: str | None = None
    affected_perspectives: list[str] = Field(default_factory=list)
    preserves: list[str] = Field(default_factory=list)
    transforms: list[str] = Field(default_factory=list)
    omits: list[str] = Field(default_factory=list)
    parent_interaction_id: str | None = None
    visibility: Visibility = Visibility.PUBLIC
    metadata: dict[str, Any] = Field(default_factory=dict)


class Interaction(BaseModel):
    id: str
    occurrence_id: str
    from_problem_id: str
    to_problem_id: str
    author_id: str
    kind: InteractionKind
    source_perspective_id: str | None
    target_perspective_id: str | None
    affected_perspectives: list[str]
    preserves: list[str]
    transforms: list[str]
    omits: list[str]
    parent_interaction_id: str | None
    visibility: Visibility
    metadata: dict[str, Any]
    solution_receipt_id: str
    created_at: str


class SolutionReceipt(BaseModel):
    id: str
    interaction_id: str
    problem_id: str
    target_problem_id: str
    verdict: Verdict
    reason: str
    created_at: str


class CollectiveActionCreate(BaseModel):
    problem_id: str
    title: str = Field(min_length=1, max_length=300)
    exact_intent: str = Field(min_length=1)
    created_by: str
    participant_ids: list[str] = Field(default_factory=list)
    affected_perspectives: list[str] = Field(default_factory=list)
    open_assumptions: list[str] = Field(default_factory=list)
    visibility: Visibility = Visibility.PUBLIC
    metadata: dict[str, Any] = Field(default_factory=dict)


class ActionStateChange(BaseModel):
    state: ActionState
    reason: str = Field(min_length=1)
    actor_id: str


class CollectiveAction(BaseModel):
    id: str
    problem_id: str
    occurrence_id: str
    title: str
    created_by: str
    participant_ids: list[str]
    affected_perspectives: list[str]
    open_assumptions: list[str]
    visibility: Visibility
    metadata: dict[str, Any]
    current_state: ActionState
    created_at: str


class ActionReturnCreate(BaseModel):
    exact_text: str = Field(min_length=1)
    authored_by: str
    evidence_status: EvidenceStatus = EvidenceStatus.ORIGINAL_NOTE
    affected_perspectives: list[str] = Field(default_factory=list)
    source_location: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ActionReturn(BaseModel):
    id: str
    action_id: str
    occurrence_id: str
    authored_by: str
    evidence_status: EvidenceStatus
    affected_perspectives: list[str]
    metadata: dict[str, Any]
    created_at: str


class ReintegrationDecisionCreate(BaseModel):
    status: ReintegrationStatus
    reason: str = Field(min_length=1)
    author_id: str


class ReintegrationProposal(BaseModel):
    id: str
    problem_id: str
    action_id: str
    return_id: str
    source_occurrence_id: str
    target_occurrence_id: str
    candidate_relation_id: str
    proposal_text: str
    preserved: list[str]
    changed: list[str]
    open_questions: list[str]
    affected_perspectives: list[str]
    current_status: ReintegrationStatus
    current_reason: str | None = None
    generated_by: str
    created_at: str


class LivingFieldProjection(BaseModel):
    generated_at: str
    participants: list[Participant]
    perspectives: list[Perspective]
    problems: list[Problem]
    interactions: list[Interaction]
    actions: list[CollectiveAction]
    returns: list[ActionReturn]
    reintegration: list[ReintegrationProposal]
    black_mirror: dict[str, Any]
    stats: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
