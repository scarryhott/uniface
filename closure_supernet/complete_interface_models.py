from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .embodied_models import SheafKind


class CoordinationKind(StrEnum):
    """Product-facing forms carried by the same canonical event field."""

    INTENT = "intent"
    PERSON = "person"
    PROJECT = "project"
    RESOURCE = "resource"
    ACTION = "action"
    LIVING_RETURN = "living_return"


class AuthorshipRole(StrEnum):
    """A contribution role, not an authentication or legal-identity claim."""

    HUMAN = "HUMAN"
    AI = "AI"
    TOKEN = "TOKEN"
    LIVING_SYSTEM = "LIVING_SYSTEM"


class CommitmentDecisionKind(StrEnum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    WITHDRAW = "WITHDRAW"


class CompleteInterfaceOffer(BaseModel):
    """One public Black Mirror offer, optionally situated in a known Supernet lens."""

    exact_text: str = Field(min_length=1)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    form_label: str = Field(default="note", min_length=1, max_length=240)
    perspective_id: str | None = None
    parent_event_id: str | None = None
    lens: str | None = Field(default=None, max_length=120)
    sheaf: SheafKind | None = None
    affected_perspectives: list[str] = Field(default_factory=list)
    relation_hints: list[str] = Field(default_factory=list)
    coordination_kind: CoordinationKind | None = None
    authorship_role: AuthorshipRole = AuthorshipRole.HUMAN
    location_label: str | None = Field(default=None, max_length=500)
    intent_tags: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("coordination_kind", mode="before")
    @classmethod
    def normalize_coordination_kind(cls, value: Any) -> Any:
        return value.lower() if isinstance(value, str) else value

    @model_validator(mode="after")
    def normalize(self) -> "CompleteInterfaceOffer":
        perspective = (self.perspective_id or self.authored_by).strip()
        self.perspective_id = perspective or self.authored_by
        self.affected_perspectives = list(
            dict.fromkeys(
                item
                for item in [*self.affected_perspectives, self.perspective_id]
                if item
            )
        )
        self.relation_hints = list(dict.fromkeys(self.relation_hints))
        self.intent_tags = list(dict.fromkeys(self.intent_tags))
        self.capabilities = list(dict.fromkeys(self.capabilities))
        self.constraints = list(dict.fromkeys(self.constraints))
        if self.location_label is not None:
            self.location_label = self.location_label.strip() or None
        if self.lens is not None:
            self.lens = self.lens.strip().lower() or None
        return self


class CompleteInterfaceCommitmentProposal(BaseModel):
    """Exact non-transferable coordination terms over one selected path."""

    intent_event_id: str = Field(min_length=1)
    target_event_ids: list[str] = Field(min_length=1)
    exact_terms: str = Field(min_length=1)
    title: str = Field(default="Coordination proposal", min_length=1, max_length=300)
    proposed_by: str = Field(default="participant", min_length=1, max_length=500)
    perspective_id: str | None = None
    required_participant_ids: list[str] = Field(default_factory=list)
    resource_conditions: list[str] = Field(default_factory=list)
    open_assumptions: list[str] = Field(default_factory=list)
    external_key: str | None = Field(default=None, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize(self) -> "CompleteInterfaceCommitmentProposal":
        self.target_event_ids = list(dict.fromkeys(self.target_event_ids))
        self.required_participant_ids = list(
            dict.fromkeys(self.required_participant_ids)
        )
        self.resource_conditions = list(dict.fromkeys(self.resource_conditions))
        self.open_assumptions = list(dict.fromkeys(self.open_assumptions))
        if self.intent_event_id in self.target_event_ids:
            raise ValueError("A selected path must target an event other than its intent")
        return self


class CompleteInterfaceCommitmentDecision(BaseModel):
    """One participant's append-only decision about exact proposal terms."""

    participant_id: str = Field(min_length=1, max_length=500)
    authored_by: str = Field(min_length=1, max_length=500)
    decision: CommitmentDecisionKind
    exact_text: str = Field(min_length=1)
    authorship_role: AuthorshipRole = AuthorshipRole.HUMAN
    perspective_id: str | None = None
    resource_offers: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    external_key: str | None = Field(default=None, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def human_decision_is_self_authored(
        self,
    ) -> "CompleteInterfaceCommitmentDecision":
        self.resource_offers = list(dict.fromkeys(self.resource_offers))
        self.constraints = list(dict.fromkeys(self.constraints))
        return self


class CompleteInterfaceCommitmentReturn(BaseModel):
    exact_text: str = Field(min_length=1)
    authored_by: str = Field(min_length=1, max_length=500)
    authorship_role: AuthorshipRole = AuthorshipRole.HUMAN
    perspective_id: str | None = None
    location_label: str | None = Field(default=None, max_length=500)
    affected_perspectives: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize(self) -> "CompleteInterfaceCommitmentReturn":
        self.affected_perspectives = list(
            dict.fromkeys(self.affected_perspectives)
        )
        if self.location_label is not None:
            self.location_label = self.location_label.strip() or None
        return self


class CompleteInterfaceSelection(BaseModel):
    """Authored refinement of a live Sense relation field.

    The original admissible alternatives remain in the NRRF790 receipt.  If the
    source reading branches, this is recorded as FORCED_ISOLATION rather than
    being mislabeled natural selection.
    """

    source_event_id: str = Field(min_length=1)
    selected_relation_id: str = Field(min_length=1)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    perspective_id: str | None = None
    reason: str = Field(
        default="Participant refines the live relational field",
        min_length=1,
        max_length=2000,
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class CompleteInterfaceCollective(BaseModel):
    event_ids: list[str] = Field(min_length=2)
    exact_text: str = Field(min_length=1)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    perspective_id: str | None = None
    affected_perspectives: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize(self) -> "CompleteInterfaceCollective":
        self.event_ids = list(dict.fromkeys(self.event_ids))
        if len(self.event_ids) < 2:
            raise ValueError("A collective return needs at least two distinct events")
        if self.perspective_id:
            self.affected_perspectives = list(
                dict.fromkeys([*self.affected_perspectives, self.perspective_id])
            )
        return self


class ClosureUIExecutionRequest(BaseModel):
    """Raw values submitted to one server-revalidated closure UI action.

    The browser is deliberately unable to submit an endpoint, HTTP method, or
    resolved domain payload.  Those are selected only after the current
    perspective-interaction contract has been re-derived on the server.
    """

    model_config = ConfigDict(extra="forbid")

    action_id: str = Field(min_length=1, max_length=240)
    perspective_id: str = Field(min_length=1, max_length=500)
    focus_event_id: str | None = Field(default=None, max_length=500)
    values: dict[str, Any] = Field(default_factory=dict)

    @field_validator("values")
    @classmethod
    def values_are_named_fields(cls, value: dict[str, Any]) -> dict[str, Any]:
        if len(value) > 64:
            raise ValueError("A closure UI action may submit at most 64 fields")
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            name = str(key).strip()
            if not name:
                raise ValueError("Closure UI field names may not be empty")
            if isinstance(item, (dict, list, tuple, set)):
                raise ValueError(
                    f"Closure UI field {name!r} must be a scalar transport value"
                )
            normalized[name] = item
        return normalized
