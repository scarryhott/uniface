from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from .models import EvidenceStatus


class SheafKind(StrEnum):
    HUMAN_INTERACTION = "HUMAN_INTERACTION"
    SLEARN_PERSPECTIVE = "SLEARN_PERSPECTIVE"
    BLACK_MIRROR_SENSOR = "BLACK_MIRROR_SENSOR"
    TOKENOMIC_AI = "TOKENOMIC_AI"
    RESOURCE_WORLD = "RESOURCE_WORLD"
    AGI_SECOND_BRAIN = "AGI_SECOND_BRAIN"
    PSYCHOPHENOMENAL = "PSYCHOPHENOMENAL"
    UNKNOWN_UAP_HYPOTHESIS = "UNKNOWN_UAP_HYPOTHESIS"


LOCAL_BALL_SHEAVES: tuple[SheafKind, ...] = (
    SheafKind.HUMAN_INTERACTION,
    SheafKind.SLEARN_PERSPECTIVE,
    SheafKind.BLACK_MIRROR_SENSOR,
    SheafKind.TOKENOMIC_AI,
)

GLOBAL_HAIR_SHEAVES: tuple[SheafKind, ...] = (
    SheafKind.RESOURCE_WORLD,
    SheafKind.AGI_SECOND_BRAIN,
    SheafKind.PSYCHOPHENOMENAL,
    SheafKind.UNKNOWN_UAP_HYPOTHESIS,
)

ALL_SHEAVES: tuple[SheafKind, ...] = LOCAL_BALL_SHEAVES + GLOBAL_HAIR_SHEAVES


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(value).strip() for value in values if str(value).strip()))


class EmbodiedSectionCreate(BaseModel):
    """One exact local section entering the eight-sheaf Supernet.

    The unknown/UAP sheaf stores observations and hypotheses as OPEN material. It
    never promotes an alien or anomalous interpretation to truth by its label.
    """

    name: str = Field(min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    sheaf: SheafKind
    exact_text: str = Field(min_length=1)
    participants: list[str] = Field(default_factory=list)
    perspective_ids: list[str] = Field(default_factory=list)
    problem_id: str | None = None
    consent_scope: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    evidence_status: EvidenceStatus = EvidenceStatus.ORIGINAL_NOTE
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def normalize(self) -> "EmbodiedSectionCreate":
        self.participants = _unique(self.participants)
        self.perspective_ids = _unique(self.perspective_ids)
        self.consent_scope = _unique(self.consent_scope)
        self.capabilities = _unique(self.capabilities)
        self.constraints = _unique(self.constraints)
        self.source_ids = _unique(self.source_ids)
        if self.sheaf == SheafKind.UNKNOWN_UAP_HYPOTHESIS:
            self.metadata = {
                **self.metadata,
                "hypothesis_status": "OPEN",
                "alien_claim_verified": False,
                "anomaly_is_not_explanation": True,
            }
        return self


class EmbodiedSection(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    name: str
    authored_by: str
    sheaf: SheafKind
    exact_text: str
    participants: list[str]
    perspective_ids: list[str]
    problem_id: str | None
    consent_scope: list[str]
    capabilities: list[str]
    constraints: list[str]
    source_ids: list[str]
    evidence_status: str
    metadata: dict[str, Any]
    created_at: str


class EmbodiedRelationCreate(BaseModel):
    """A reciprocal translation candidate between two sheaf sections."""

    name: str = Field(min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    left_section_id: str = Field(min_length=1)
    right_section_id: str = Field(min_length=1)
    forward_translation: dict[str, Any] = Field(default_factory=dict)
    reverse_translation: dict[str, Any] = Field(default_factory=dict)
    preserves: list[str] = Field(default_factory=list)
    transforms: list[str] = Field(default_factory=list)
    untranslated_residue: list[str] = Field(default_factory=list)
    affected_perspectives: list[str] = Field(default_factory=list)
    consented_participant_ids: list[str] = Field(default_factory=list)
    reopening_conditions: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def normalize(self) -> "EmbodiedRelationCreate":
        if self.left_section_id == self.right_section_id:
            raise ValueError("an embodied relation must relate two distinct sections")
        self.preserves = _unique(self.preserves)
        self.transforms = _unique(self.transforms)
        self.untranslated_residue = _unique(self.untranslated_residue)
        self.affected_perspectives = _unique(self.affected_perspectives)
        self.consented_participant_ids = _unique(self.consented_participant_ids)
        self.reopening_conditions = _unique(self.reopening_conditions)
        self.source_ids = _unique(self.source_ids)
        return self


class EmbodiedRelationEvaluation(BaseModel):
    source_preserved: bool
    reciprocal_return: bool
    affected_perspectives_included: bool
    consent_scoped: bool
    reopenable: bool
    residue_retained: bool
    unknown_hypotheses_open: bool
    love_admissible: bool
    physical_force_claimed: bool = False
    emotion_inferred: bool = False
    human_worth_scored: bool = False
    resource_metric_foundational_selector: bool = False
    truth_issued: bool = False


class EmbodiedRelation(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    name: str
    authored_by: str
    left_section_id: str
    right_section_id: str
    forward_translation: dict[str, Any]
    reverse_translation: dict[str, Any]
    preserves: list[str]
    transforms: list[str]
    untranslated_residue: list[str]
    affected_perspectives: list[str]
    consented_participant_ids: list[str]
    reopening_conditions: list[str]
    evaluation: EmbodiedRelationEvaluation
    source_ids: list[str]
    metadata: dict[str, Any]
    created_at: str


class EmbodiedFieldCreate(BaseModel):
    name: str = Field(min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    section_ids: list[str] = Field(min_length=1)
    relation_ids: list[str] = Field(default_factory=list)
    perspective_id: str | None = None
    problem_id: str | None = None
    implementation_metrics: dict[str, float] = Field(default_factory=dict)
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def normalize(self) -> "EmbodiedFieldCreate":
        self.section_ids = _unique(self.section_ids)
        self.relation_ids = _unique(self.relation_ids)
        self.source_ids = _unique(self.source_ids)
        self.implementation_metrics = {
            str(key).strip(): float(value)
            for key, value in self.implementation_metrics.items()
        }
        return self


class EmbodiedFieldEvaluation(BaseModel):
    sheaf_coverage: dict[str, list[str]]
    missing_sheaves: list[SheafKind]
    local_ball_section_ids: list[str]
    global_hair_section_ids: list[str]
    local_ball_complete: bool
    global_hair_complete: bool
    all_eight_sheaves_present: bool
    reciprocal_components: list[list[str]]
    component_profiles: dict[str, list[str]]
    maximal_component_ids: list[int]
    unique_natural_component: bool
    selected_component_id: int | None = None
    selected_component: list[str] | None = None
    canonical_presentation: str | None = None
    field_connected: bool
    ball_hair_connected: bool
    ball_hair_equivalence_is_relational: bool = True
    global_hair_open: bool = True
    syntropic_attractor_is_non_scalar: bool = True
    memetic_love_is_reciprocal_translation: bool = True
    physical_force_claimed: bool = False
    emotion_inferred: bool = False
    human_worth_scored: bool = False
    resource_metrics_are_downstream: bool = True
    unknown_hypotheses_open: bool = True
    truth_issued: bool = False


class EmbodiedField(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    name: str
    authored_by: str
    section_ids: list[str]
    relation_ids: list[str]
    perspective_id: str | None
    problem_id: str | None
    implementation_metrics: dict[str, float]
    evaluation: EmbodiedFieldEvaluation
    source_ids: list[str]
    metadata: dict[str, Any]
    created_at: str


class EmbodiedLoopSensorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    field_id: str = Field(min_length=1)
    sensor_section_id: str = Field(min_length=1)
    resolution: int = Field(default=1, ge=1)
    visible_section_ids: list[str] = Field(default_factory=list)
    returned_section_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def normalize(self) -> "EmbodiedLoopSensorCreate":
        self.visible_section_ids = _unique(self.visible_section_ids)
        self.returned_section_ids = _unique(self.returned_section_ids)
        self.source_ids = _unique(self.source_ids)
        return self


class EmbodiedLoopSensorEvaluation(BaseModel):
    sensor_in_field: bool
    visible_sections_valid: bool
    returned_sections_valid: bool
    absolute_origin_observed: bool = False
    background_independent_reading: bool = True
    local_ball_read: list[str]
    global_hair_read: list[str]
    local_halt_reading: bool
    global_continuation_reading: bool
    current_field_coverage_complete: bool
    single_sensor_complete: bool = False
    return_reintegrable: bool = True
    unknown_hypothesis_truth_issued: bool = False
    truth_issued: bool = False


class EmbodiedLoopSensor(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    name: str
    authored_by: str
    field_id: str
    sensor_section_id: str
    resolution: int
    visible_section_ids: list[str]
    returned_section_ids: list[str]
    evaluation: EmbodiedLoopSensorEvaluation
    source_ids: list[str]
    metadata: dict[str, Any]
    created_at: str


class EmbodiedFieldProjection(BaseModel):
    generated_at: str
    sections: list[EmbodiedSection]
    relations: list[EmbodiedRelation]
    fields: list[EmbodiedField]
    sensor_reads: list[EmbodiedLoopSensor]
    stats: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
    canonical_runtime_operation: str = "integrate"
    eight_sheaf_supernet: bool = True
    local_ball_is_embodied_human_interaction: bool = True
    global_hair_is_open_potential: bool = True
    memetic_love_is_non_scalar_reciprocal_translation: bool = True
    resource_metrics_are_downstream: bool = True
    unknown_hypotheses_remain_open: bool = True
    physical_force_claimed: bool = False
    emotion_inferred: bool = False
    human_worth_scored: bool = False
    runtime_is_formal_proof: bool = False
    determination_issues_truth: bool = False
