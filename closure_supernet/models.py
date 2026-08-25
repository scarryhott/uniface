from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Verdict(StrEnum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    OPEN = "OPEN"


class OccurrenceStatus(StrEnum):
    ORIGINAL_NOTE = "ORIGINAL_NOTE"
    LATER_READING = "LATER_READING"
    FORMAL_SOURCE = "FORMAL_SOURCE"
    SIMULATION_SOURCE = "SIMULATION_SOURCE"
    RULE_SOURCE = "RULE_SOURCE"


class RelationType(StrEnum):
    SAME_LITERAL_EQUATION = "SAME_LITERAL_EQUATION"
    NOTATIONAL_VARIANT = "NOTATIONAL_VARIANT"
    SAME_OPERATOR_PATH = "SAME_OPERATOR_PATH"
    INVERSE_PATH = "INVERSE_PATH"
    FRAME_TRANSLATION = "FRAME_TRANSLATION"
    REFINEMENT = "REFINEMENT"
    COARSENING = "COARSENING"
    PRECURSOR = "PRECURSOR"
    LATER_READING = "LATER_READING"
    FORMALIZES = "FORMALIZES"
    SIMULATES = "SIMULATES"
    CONTRADICTS = "CONTRADICTS"
    PHYSICAL_ANALOGY = "PHYSICAL_ANALOGY"
    SOCIOECONOMIC_ANALOGY = "SOCIOECONOMIC_ANALOGY"
    MORAL_CONSEQUENCE = "MORAL_CONSEQUENCE"
    MODEL_SUGGESTED_RELATION = "MODEL_SUGGESTED_RELATION"
    OPEN_RELATION = "OPEN_RELATION"


class EvidenceStatus(StrEnum):
    ORIGINAL_NOTE = "ORIGINAL_NOTE"
    MODEL_SUGGESTED_RELATION = "MODEL_SUGGESTED_RELATION"
    INTERPRETED_RELATION = "INTERPRETED_RELATION"
    AUTHOR_CONFIRMED_RELATION = "AUTHOR_CONFIRMED_RELATION"
    FORMALLY_PROVED_UNDER_READING = "FORMALLY_PROVED_UNDER_READING"
    SIMULATED_UNDER_ASSUMPTIONS = "SIMULATED_UNDER_ASSUMPTIONS"
    EMPIRICALLY_SUPPORTED = "EMPIRICALLY_SUPPORTED"
    PHYSICAL_HYPOTHESIS = "PHYSICAL_HYPOTHESIS"
    SOCIOECONOMIC_PROPOSAL = "SOCIOECONOMIC_PROPOSAL"
    MORAL_CONSEQUENCE = "MORAL_CONSEQUENCE"
    REJECTED_RELATION = "REJECTED_RELATION"
    OPEN = "OPEN"


class RuleState(StrEnum):
    PROPOSED = "PROPOSED"
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"


class OccurrenceCreate(BaseModel):
    exact_text: str = Field(min_length=1)
    source_id: str = Field(default="manual")
    source_location: str | None = None
    source_context: str | None = None
    status: OccurrenceStatus = OccurrenceStatus.ORIGINAL_NOTE
    evidence_status: EvidenceStatus = EvidenceStatus.ORIGINAL_NOTE
    metadata: dict[str, Any] = Field(default_factory=dict)


class Occurrence(BaseModel):
    id: str
    source_id: str
    exact_text: str
    exact_symbols: list[str]
    operator_path: list[dict[str, Any]]
    source_location: str | None = None
    source_context: str | None = None
    status: str
    evidence_status: str
    checksum: str
    metadata: dict[str, Any]
    created_at: str


class CandidateRelation(BaseModel):
    id: str
    source_occurrence: str
    target_occurrence: str
    relation_type: str
    score: float
    rationale: str
    proposed_by: str
    status: str
    created_at: str


class InterpretationWitness(BaseModel):
    id: str
    candidate_relation_id: str
    source_operator_path: list[dict[str, Any]]
    target_operator_path: list[dict[str, Any]]
    preserved_structure: list[str]
    transformed_structure: list[str]
    omitted_or_hidden_structure: list[str]
    frame_and_scope: str
    reverse_path: list[str]
    affected_perspectives: list[str]
    formal_scope: str
    empirical_scope: str
    reopening: str
    generated_by: str
    status: str
    created_at: str


class AdmissionDecision(BaseModel):
    id: str
    interpretation_id: str
    verdict: Verdict
    checks: dict[str, bool]
    reason: str
    rule_version: str
    decided_by: str
    created_at: str


class AuthorDecision(BaseModel):
    verdict: Verdict
    reason: str = Field(min_length=1)
    author_id: str = Field(default="author")


class RuleVersionCreate(BaseModel):
    rule_id: str
    exact_rule_text: str
    reason_for_change: str
    parent_version: str | None = None
    state: RuleState = RuleState.PROPOSED
    metadata: dict[str, Any] = Field(default_factory=dict)


class RuleVersion(BaseModel):
    id: str
    rule_id: str
    version: str
    parent_version: str | None
    exact_rule_text: str
    reason_for_change: str
    state: str
    metadata: dict[str, Any]
    created_at: str


class OpenSeam(BaseModel):
    id: str
    source_occurrence: str | None
    target_occurrence: str | None
    reason: str
    status: Verdict = Verdict.OPEN
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class ProjectionClass(BaseModel):
    id: str
    member_ids: list[str]
    labels: list[str]
    operators: list[str]
    opacity: int
    evidence_statuses: list[str]


class ProjectionEdge(BaseModel):
    source: str
    target: str
    relation_type: str
    verdict: Verdict
    interpretation_id: str | None = None


class BlackMirrorProjection(BaseModel):
    generated_at: str
    classes: list[ProjectionClass]
    edges: list[ProjectionEdge]
    open_seams: list[OpenSeam]
    stats: dict[str, Any]
    source_reverse_index: dict[str, list[str]]


class RuntimeCycleResult(BaseModel):
    cycle_id: str
    ingested: int = 0
    candidates: int = 0
    interpretations: int = 0
    admissions: int = 0
    open_seams: int = 0
    rule_proposals: int = 0
    projection_classes: int = 0
    projection_edges: int = 0
    integration_pulled: int = 0
    integration_pushed: int = 0
    integration_runs: int = 0
    integration_errors: int = 0
    started_at: str
    finished_at: str


class RuntimeStatus(BaseModel):
    running: bool
    cycle_count: int
    last_cycle: dict[str, Any] | None
    autonomy_interval_seconds: float
    llm_mode: str
    enabled_integrations: int = 0
    integration_errors: int = 0
    turing_complete_assumed: bool = False
