from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from .models import EvidenceStatus, Verdict


class IntegrationStage(StrEnum):
    RECEIVED = "RECEIVED"
    SOURCE_PRESERVED = "SOURCE_PRESERVED"
    RELATION_SENSED = "RELATION_SENSED"
    ADMITTED = "ADMITTED"
    DETERMINED = "DETERMINED"
    RETURNED = "RETURNED"
    REOPENED = "REOPENED"
    REJECTED = "REJECTED"


class IntegrationLens(StrEnum):
    ALL = "all"
    SOURCE = "source"
    PROBLEM = "problem"
    RESOURCE = "resource"
    TRANSLATION = "translation"
    SELECTOR = "selector"
    REOPENING = "reopening"
    ACTION = "action"
    HARDWARE = "hardware"
    EQUALITY = "equality"
    AGENT = "agent"
    TRADING = "trading"
    RENORMALIZATION = "renormalization"
    CONSTRUCTIVE = "constructive"
    FRAMEWORK = "framework"
    EMBODIED = "embodied"
    INVERSION = "inversion"
    COMPLETION = "completion"


class ResourceEnvelope(BaseModel):
    """One open relative form entering the continuous Supernet integrator."""

    exact_text: str = Field(min_length=1)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    form_label: str = Field(default="resource", min_length=1, max_length=240)
    language_label: str | None = Field(default=None, max_length=240)
    source_id: str = Field(default="supernet", min_length=1, max_length=240)
    source_location: str | None = None
    source_context: str | None = None
    perspective_id: str | None = None
    problem_id: str | None = None
    action_id: str | None = None
    visibility: str = Field(default="PUBLIC", min_length=1, max_length=80)
    capabilities: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    relation_hints: list[str] = Field(default_factory=list)
    causal_predecessor_ids: list[str] = Field(default_factory=list)
    parent_event_ids: list[str] = Field(default_factory=list)
    affected_perspectives: list[str] = Field(default_factory=list)
    evidence_status: EvidenceStatus = EvidenceStatus.ORIGINAL_NOTE
    adapter_label: str | None = Field(default=None, max_length=240)
    external_key: str | None = Field(default=None, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize_open_lists(self) -> "ResourceEnvelope":
        for name in (
            "capabilities",
            "constraints",
            "relation_hints",
            "causal_predecessor_ids",
            "parent_event_ids",
            "affected_perspectives",
        ):
            setattr(self, name, list(dict.fromkeys(getattr(self, name))))
        return self


class IntegrationStateCreate(BaseModel):
    stage: IntegrationStage
    verdict: Verdict = Verdict.OPEN
    reason: str = Field(min_length=1)
    actor_id: str = Field(default="runtime", min_length=1)
    rigidity_scope: list[str] = Field(default_factory=list)
    rigidity_receipt: dict[str, Any] | None = None
    determined_form: dict[str, Any] | None = None
    unitary_path_partition: dict[str, Any] | None = None
    returned_resource_ids: list[str] = Field(default_factory=list)
    successor_potential: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def determination_requires_receipt(self) -> "IntegrationStateCreate":
        if self.stage == IntegrationStage.DETERMINED:
            if self.rigidity_receipt is None or self.determined_form is None:
                raise ValueError(
                    "DETERMINED requires an explicit rigidity receipt and determined form"
                )
            if self.verdict != Verdict.OPEN:
                raise ValueError(
                    "Natural-form determination does not issue TRUE or FALSE automatically"
                )
        return self


class SupernetIntegrationEvent(BaseModel):
    id: str
    seq: int
    external_key: str | None
    exact_source_ids: list[str]
    authored_by: str
    perspective_id: str | None
    problem_id: str | None
    action_id: str | None
    form_label: str
    language_label: str | None
    visibility: str
    capabilities: list[str]
    constraints: list[str]
    relation_hints: list[str]
    causal_predecessor_ids: list[str]
    parent_event_ids: list[str]
    affected_perspectives: list[str]
    evidence_status: str
    adapter_label: str | None
    metadata: dict[str, Any]
    current_stage: IntegrationStage
    current_verdict: Verdict
    state_history: list[dict[str, Any]]
    created_at: str


class IntegrationReceipt(BaseModel):
    event_id: str
    occurrence_ids: list[str]
    current_stage: IntegrationStage
    current_verdict: Verdict
    field_stage_id: str
    field_stage_index: int
    history_signature: str
    limit_signature: str
    returned_resource_ids: list[str] = Field(default_factory=list)
    successor_potential: list[dict[str, Any]] = Field(default_factory=list)
    source_reverse_index: dict[str, list[str]] = Field(default_factory=dict)
    canonical_runtime_operation: str = "integrate"
    truth_issued_by_determination: bool = False


class UnifiedFieldStage(BaseModel):
    id: str
    stage_index: int
    previous_stage_id: str | None
    trigger: str
    trigger_event_id: str | None
    event_ids: list[str]
    history_signature: str
    limit_signature: str
    event_count: int
    open_count: int
    admitted_count: int
    determined_count: int
    returned_count: int
    reopened_count: int
    summary: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
    created_at: str


class SupernetFieldProjection(BaseModel):
    generated_at: str
    events: list[SupernetIntegrationEvent]
    edges: list[dict[str, Any]]
    current_stage: UnifiedFieldStage | None
    stages: list[UnifiedFieldStage]
    lens: IntegrationLens = IntegrationLens.ALL
    lens_counts: dict[str, int]
    stats: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
    canonical_runtime_operation: str = "integrate"
    subsystems_are_lenses: bool = True
    canonical_language: str | None = None
    protocol_is_transport_only: bool = True
    truth_issued_by_determination: bool = False
