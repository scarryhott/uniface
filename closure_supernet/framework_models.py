from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from .constructive_models import FiniteCommutativeGroupCreate


def _unique(values: list[str], label: str) -> list[str]:
    normalized = [str(item).strip() for item in values]
    if any(not item for item in normalized):
        raise ValueError(f"{label} entries must be non-empty")
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{label} entries must be unique")
    return normalized


def _normalize_action(
    action: dict[str, dict[str, str]],
) -> dict[str, dict[str, str]]:
    return {
        str(level).strip(): {
            str(source).strip(): str(target).strip()
            for source, target in row.items()
        }
        for level, row in action.items()
    }


class FrameworkClassification(StrEnum):
    CLASSICAL = "CLASSICAL"
    NONCONTEXTUAL_PARTIAL = "NONCONTEXTUAL_PARTIAL"
    CONTEXTUAL = "CONTEXTUAL"
    OPEN_TRANSLATIONAL_LAW = "OPEN_TRANSLATIONAL_LAW"


class NaturalSelectionArenaCreate(BaseModel):
    """Finite executable chart of NRRF784 conscious selective naturality."""

    name: str = Field(min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    forms: list[str] = Field(min_length=1)
    group: FiniteCommutativeGroupCreate
    action: dict[str, dict[str, str]] = Field(min_length=1)
    selected: dict[str, bool] = Field(min_length=1)
    resource_metric: dict[str, Decimal] | None = None
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_arena(self) -> "NaturalSelectionArenaCreate":
        self.forms = _unique(self.forms, "forms")
        form_set = set(self.forms)
        self.action = _normalize_action(self.action)
        group_set = set(self.group.elements)
        if set(self.action) != group_set:
            raise ValueError("action must have exactly one row for every group element")
        for level, row in self.action.items():
            if set(row) != form_set:
                raise ValueError(f"action row {level} must be total exactly on forms")
            if any(target not in form_set for target in row.values()):
                raise ValueError(f"action row {level} leaves the form arena")
        self.selected = {str(key).strip(): bool(value) for key, value in self.selected.items()}
        if set(self.selected) != form_set:
            raise ValueError("selected must give one verdict for every form")
        if self.resource_metric is not None:
            metric = {
                str(key).strip(): Decimal(str(value))
                for key, value in self.resource_metric.items()
            }
            if set(metric) != form_set:
                raise ValueError("resource_metric must cover every form")
            if any(not value.is_finite() for value in metric.values()):
                raise ValueError("resource_metric values must be finite")
            self.resource_metric = metric
        self.source_ids = list(dict.fromkeys(str(item) for item in self.source_ids))
        return self


class NaturalSelectionEvaluation(BaseModel):
    group_valid: bool
    action_valid: bool
    natural: bool
    selector_fixed_under_shift: bool
    factors_through_orbits: bool
    orbits: list[list[str]]
    orbit_of: dict[str, int]
    orbit_verdicts: dict[str, bool | None]
    selected_orbit_ids: list[int]
    unique_selected_orbit: bool
    canonical_presentation: str | None = None
    naturality_self_natural: bool = True
    resource_metric_present: bool
    resource_metric_selector_natural: bool | None = None
    resource_metric_level_invariant: bool | None = None
    metric_selected_forms: list[str] = Field(default_factory=list)
    metric_selected_orbit_cost_constant: bool | None = None
    metric_flip_witnesses: list[dict[str, Any]] = Field(default_factory=list)
    resource_metric_foundational_selector: bool = False
    no_argmin_level_line_formal_reading: bool = True
    classical_choice_required: bool = False
    excluded_middle_required: bool = False
    runtime_is_formal_proof: bool = False
    determination_issues_truth: bool = False


class NaturalSelectionArena(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    name: str
    authored_by: str
    perspective_id: str | None
    problem_id: str | None
    forms: list[str]
    group: dict[str, Any]
    action: dict[str, dict[str, str]]
    selected: dict[str, bool]
    resource_metric: dict[str, str] | None
    evaluation: NaturalSelectionEvaluation
    source_ids: list[str]
    metadata: dict[str, Any]
    created_at: str


class TranslationalTruthFrameworkCreate(BaseModel):
    """Finite frame-observable chart of NRRF785 translational truth."""

    name: str = Field(min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    observables: list[str] = Field(min_length=1)
    frames: list[str] = Field(min_length=1)
    values: list[str] = Field(min_length=1)
    default_value: str = Field(min_length=1)
    group: FiniteCommutativeGroupCreate
    frame_action: dict[str, dict[str, str]] = Field(min_length=1)
    observable_action: dict[str, dict[str, str]] = Field(min_length=1)
    verdicts: dict[str, dict[str, str | None]] = Field(min_length=1)
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_framework(self) -> "TranslationalTruthFrameworkCreate":
        self.observables = _unique(self.observables, "observables")
        self.frames = _unique(self.frames, "frames")
        self.values = _unique(self.values, "values")
        self.default_value = str(self.default_value).strip()
        if self.default_value not in self.values:
            raise ValueError("default_value must be supplied as one of values")
        frame_set = set(self.frames)
        observable_set = set(self.observables)
        group_set = set(self.group.elements)
        self.frame_action = _normalize_action(self.frame_action)
        self.observable_action = _normalize_action(self.observable_action)
        for label, action, carrier in (
            ("frame_action", self.frame_action, frame_set),
            ("observable_action", self.observable_action, observable_set),
        ):
            if set(action) != group_set:
                raise ValueError(f"{label} must have exactly one row per group element")
            for level, row in action.items():
                if set(row) != carrier:
                    raise ValueError(f"{label} row {level} must be total on its carrier")
                if any(target not in carrier for target in row.values()):
                    raise ValueError(f"{label} row {level} leaves its carrier")
        normalized_verdicts: dict[str, dict[str, str | None]] = {}
        if set(self.verdicts) != frame_set:
            raise ValueError("verdicts must have exactly one row for every frame")
        value_set = set(self.values)
        for frame, row in self.verdicts.items():
            normalized = {
                str(observable).strip(): None if value is None else str(value).strip()
                for observable, value in row.items()
            }
            if set(normalized) != observable_set:
                raise ValueError(f"verdict row {frame} must cover every observable")
            if any(value is not None and value not in value_set for value in normalized.values()):
                raise ValueError(f"verdict row {frame} uses a value outside values")
            normalized_verdicts[str(frame).strip()] = normalized
        self.verdicts = normalized_verdicts
        self.source_ids = list(dict.fromkeys(str(item) for item in self.source_ids))
        return self


class TranslationalTruthEvaluation(BaseModel):
    group_valid: bool
    frame_action_valid: bool
    observable_action_valid: bool
    joint_translation_invariant: bool
    invariance_failures: list[dict[str, Any]]
    presentation_orbits: list[list[str]]
    presentation_orbit_of: dict[str, int]
    orbit_truth: dict[str, str | None]
    truth_unique: bool
    fragment_noncontextual: bool
    frame_assignments: dict[str, dict[str, str]]
    total: bool
    noncontextual: bool
    classical: bool
    contextual: bool
    frame_free_total: bool
    invariant_global_assignment: bool
    global_assignment: dict[str, str] | None
    contextual_obstructions: list[dict[str, Any]]
    classification: FrameworkClassification
    truth_is_translational_not_absolute: bool = True
    global_section_is_not_truth_object: bool = True
    local_classical_global_obstruction_possible: bool = True
    natural_orbit_truth: bool = True
    classical_choice_required: bool = False
    excluded_middle_required: bool = False
    runtime_is_formal_proof: bool = False
    determination_issues_truth: bool = False


class TranslationalTruthFramework(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    name: str
    authored_by: str
    perspective_id: str | None
    problem_id: str | None
    observables: list[str]
    frames: list[str]
    values: list[str]
    default_value: str
    group: dict[str, Any]
    frame_action: dict[str, dict[str, str]]
    observable_action: dict[str, dict[str, str]]
    verdicts: dict[str, dict[str, str | None]]
    evaluation: TranslationalTruthEvaluation
    source_ids: list[str]
    metadata: dict[str, Any]
    created_at: str


class PresentationRef(BaseModel):
    frame: str = Field(min_length=1)
    observable: str = Field(min_length=1)


class TruthSelectionBridgeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    arena_id: str = Field(min_length=1)
    framework_id: str = Field(min_length=1)
    form_to_presentation: dict[str, PresentationRef] = Field(min_length=1)
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def normalize_sources(self) -> "TruthSelectionBridgeCreate":
        self.form_to_presentation = {
            str(form).strip(): presentation
            for form, presentation in self.form_to_presentation.items()
        }
        self.source_ids = list(dict.fromkeys(str(item) for item in self.source_ids))
        return self


class TruthSelectionBridge(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    name: str
    authored_by: str
    arena_id: str
    framework_id: str
    form_to_presentation: dict[str, PresentationRef]
    equivariant: bool
    equivariance_failures: list[dict[str, Any]]
    natural_selector: bool
    framework_translational_truth: bool
    selected_framework_orbit_ids: list[int]
    selected_orbit_truth: dict[str, str | None]
    unified: bool
    framework_classification: FrameworkClassification
    global_assignment_required_for_truth: bool = False
    resource_metric_foundational_selector: bool = False
    canonical_presentation: str | None = None
    truth_issued: bool = False
    source_ids: list[str]
    metadata: dict[str, Any]
    created_at: str


class FrameworkFieldProjection(BaseModel):
    generated_at: str
    arenas: list[NaturalSelectionArena]
    frameworks: list[TranslationalTruthFramework]
    bridges: list[TruthSelectionBridge]
    stats: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
    formal_readings: list[str] = Field(default_factory=lambda: ["NRRF784", "NRRF785"])
    canonical_runtime_operation: str = "integrate"
    naturality_selects_orbits: bool = True
    translational_truth_shared_by_classical_and_contextual: bool = True
    resource_metrics_are_downstream: bool = True
    global_assignment_required_for_truth: bool = False
    classical_choice_required: bool = False
    excluded_middle_required: bool = False
    runtime_is_formal_proof: bool = False
    determination_issues_truth: bool = False
