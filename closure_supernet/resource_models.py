from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator

from .living_models import Visibility
from .models import EvidenceStatus, Verdict


class ResourceCreate(BaseModel):
    """One exact resource occurrence in an author-selected natural form.

    ``form_label`` and ``language_label`` are deliberately open strings.  The
    protocol has no finite registry that decides which resource forms or
    languages may participate.
    """

    exact_text: str = Field(min_length=1)
    created_by: str
    form_label: str = Field(min_length=1, max_length=240)
    language_label: str | None = Field(default=None, max_length=240)
    perspective_id: str | None = None
    problem_id: str | None = None
    action_id: str | None = None
    parent_resource_id: str | None = None
    visibility: Visibility = Visibility.PUBLIC
    affected_perspectives: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Resource(BaseModel):
    id: str
    occurrence_id: str
    created_by: str
    form_label: str
    language_label: str | None
    perspective_id: str | None
    problem_id: str | None
    action_id: str | None
    parent_resource_id: str | None
    visibility: Visibility
    affected_perspectives: list[str]
    capabilities: list[str]
    constraints: list[str]
    metadata: dict[str, Any]
    created_at: str


class ResourceEngagementCreate(BaseModel):
    resource_id: str
    actor_id: str
    exact_text: str = Field(min_length=1)
    engagement_label: str = Field(min_length=1, max_length=240)
    language_label: str | None = Field(default=None, max_length=240)
    perspective_id: str | None = None
    problem_id: str | None = None
    interaction_id: str | None = None
    affected_perspectives: list[str] = Field(default_factory=list)
    preserves: list[str] = Field(default_factory=list)
    transforms: list[str] = Field(default_factory=list)
    omits: list[str] = Field(default_factory=list)
    visibility: Visibility = Visibility.PUBLIC
    metadata: dict[str, Any] = Field(default_factory=dict)


class ResourceEngagement(BaseModel):
    id: str
    resource_id: str
    occurrence_id: str
    actor_id: str
    engagement_label: str
    language_label: str | None
    perspective_id: str | None
    problem_id: str | None
    interaction_id: str | None
    affected_perspectives: list[str]
    preserves: list[str]
    transforms: list[str]
    omits: list[str]
    visibility: Visibility
    metadata: dict[str, Any]
    created_at: str


class ResourceTranslationCreate(BaseModel):
    source_resource_id: str
    target_resource_id: str
    authored_by: str
    exact_text: str = Field(min_length=1)
    relation_label: str = Field(min_length=1, max_length=240)
    source_frame: str = Field(min_length=1, max_length=500)
    target_frame: str = Field(min_length=1, max_length=500)
    source_language: str | None = Field(default=None, max_length=240)
    target_language: str | None = Field(default=None, max_length=240)
    preserved: list[str] = Field(default_factory=list)
    transformed: list[str] = Field(default_factory=list)
    omitted: list[str] = Field(default_factory=list)
    faithfulness: dict[str, float] = Field(default_factory=dict)
    affected_perspectives: list[str] = Field(default_factory=list)
    protocol_verdict: bool | None = None
    transport_label: str | None = Field(default=None, max_length=240)
    visibility: Visibility = Visibility.PUBLIC
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_open_faithfulness(self) -> "ResourceTranslationCreate":
        for dimension, value in self.faithfulness.items():
            if not dimension.strip():
                raise ValueError("Faithfulness dimensions must have non-empty names")
            if value < 0.0 or value > 1.0:
                raise ValueError("Faithfulness values must lie in [0,1]")
        return self


class ResourceTranslationDecisionCreate(BaseModel):
    verdict: Verdict
    reason: str = Field(min_length=1)
    decided_by: str
    scope: str = Field(default="participant-relative", min_length=1, max_length=240)


class ResourceTranslation(BaseModel):
    id: str
    occurrence_id: str
    source_resource_id: str
    target_resource_id: str
    authored_by: str
    relation_label: str
    source_frame: str
    target_frame: str
    source_language: str | None
    target_language: str | None
    preserved: list[str]
    transformed: list[str]
    omitted: list[str]
    faithfulness: dict[str, float]
    affected_perspectives: list[str]
    protocol_verdict: bool | None
    transport_label: str | None
    visibility: Visibility
    metadata: dict[str, Any]
    candidate_relation_id: str | None
    current_verdict: Verdict
    current_reason: str
    current_scope: str
    decided_by: str
    created_at: str


class ResourceReturnCreate(BaseModel):
    engagement_id: str
    exact_text: str = Field(min_length=1)
    authored_by: str
    form_label: str = Field(min_length=1, max_length=240)
    language_label: str | None = Field(default=None, max_length=240)
    evidence_status: EvidenceStatus = EvidenceStatus.ORIGINAL_NOTE
    affected_perspectives: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    source_location: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ResourceReturn(BaseModel):
    id: str
    engagement_id: str
    source_resource_id: str
    returned_resource_id: str
    occurrence_id: str
    authored_by: str
    affected_perspectives: list[str]
    evidence_status: EvidenceStatus
    metadata: dict[str, Any]
    reintegration_status: str
    created_at: str


class ResourceReintegration(BaseModel):
    id: str
    return_id: str
    source_resource_id: str
    returned_resource_id: str
    translation_id: str | None
    candidate_relation_id: str | None
    status: str
    open_questions: list[str]
    affected_perspectives: list[str]
    created_at: str
    updated_at: str


class ProtocolReceiptCreate(BaseModel):
    resource_id: str
    recorded_by: str
    transport_label: str = Field(min_length=1, max_length=240)
    wire_reference: str | None = None
    protocol_verdict: bool
    exact_receipt: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProtocolReceipt(BaseModel):
    id: str
    resource_id: str
    occurrence_id: str
    recorded_by: str
    transport_label: str
    wire_reference: str | None
    protocol_verdict: bool
    metadata: dict[str, Any]
    created_at: str


class LiveResourceStage(BaseModel):
    id: str
    stage_index: int
    previous_stage_id: str | None
    trigger: str
    delivery_order: list[str]
    resource_ids: list[str]
    engagement_ids: list[str]
    translation_ids: list[str]
    admitted_translation_ids: list[str]
    open_translation_ids: list[str]
    rejected_translation_ids: list[str]
    natural_components: list[dict[str, Any]]
    stage_signature: str
    limit_signature: str
    complete_coverage: bool
    canonical_language: str | None
    source_reverse_index: dict[str, list[str]]
    created_at: str


class ResourceFieldProjection(BaseModel):
    generated_at: str
    resources: list[Resource]
    engagements: list[ResourceEngagement]
    translations: list[ResourceTranslation]
    returns: list[ResourceReturn]
    reintegrations: list[ResourceReintegration]
    protocol_receipts: list[ProtocolReceipt]
    stages: list[LiveResourceStage]
    current_stage: LiveResourceStage | None
    stats: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
