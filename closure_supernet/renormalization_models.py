from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, model_validator


class RegularizedFamilyCreate(BaseModel):
    """A finite live chart of a regularized family.

    The formal NRRF781 theorem is not reduced to this finite representation.
    This payload is the current runtime evidence from which a scoped
    universality witness and relative closure may be determined.
    """

    name: str = Field(min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    members: dict[str, list[Decimal]] = Field(min_length=2)
    cutoff_labels: list[str] = Field(default_factory=list)
    tolerance: Decimal = Field(default=Decimal("0"), ge=0)
    perspective_id: str | None = None
    problem_id: str | None = None
    universality_source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_family(self) -> "RegularizedFamilyCreate":
        normalized: dict[str, list[Decimal]] = {}
        width: int | None = None
        for raw_name, raw_values in self.members.items():
            name = str(raw_name).strip()
            if not name:
                raise ValueError("family member names must be non-empty")
            values = [Decimal(str(value)) for value in raw_values]
            if not values:
                raise ValueError(f"member {name} must have at least one cutoff value")
            if any(not value.is_finite() for value in values):
                raise ValueError(f"member {name} contains a non-finite amplitude")
            if width is None:
                width = len(values)
            elif len(values) != width:
                raise ValueError("all family members must use the same cutoff count")
            normalized[name] = values
        self.members = normalized
        assert width is not None
        if not self.cutoff_labels:
            self.cutoff_labels = [str(index) for index in range(width)]
        else:
            self.cutoff_labels = [str(item) for item in self.cutoff_labels]
            if len(self.cutoff_labels) != width:
                raise ValueError("cutoff_labels must match the member cutoff count")
        if len(set(self.cutoff_labels)) != len(self.cutoff_labels):
            raise ValueError("cutoff_labels must be unique")
        self.universality_source_ids = list(dict.fromkeys(self.universality_source_ids))
        if not self.tolerance.is_finite():
            raise ValueError("tolerance must be finite")
        return self


class RegularizedFamilyExtend(BaseModel):
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    cutoff_labels: list[str] = Field(min_length=1)
    members: dict[str, list[Decimal]] = Field(min_length=2)
    universality_source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_extension(self) -> "RegularizedFamilyExtend":
        self.cutoff_labels = [str(item) for item in self.cutoff_labels]
        if len(set(self.cutoff_labels)) != len(self.cutoff_labels):
            raise ValueError("extension cutoff_labels must be unique")
        width = len(self.cutoff_labels)
        normalized: dict[str, list[Decimal]] = {}
        for raw_name, raw_values in self.members.items():
            name = str(raw_name).strip()
            if not name:
                raise ValueError("family member names must be non-empty")
            values = [Decimal(str(value)) for value in raw_values]
            if len(values) != width:
                raise ValueError("each extension member must match cutoff_labels")
            if any(not value.is_finite() for value in values):
                raise ValueError(f"member {name} contains a non-finite amplitude")
            normalized[name] = values
        self.members = normalized
        self.universality_source_ids = list(dict.fromkeys(self.universality_source_ids))
        return self


class UniversalityEvaluation(BaseModel):
    member_names: list[str]
    cutoff_labels: list[str]
    common_divergence_universal: bool
    relative_closure_determined: bool
    cutoff_independent: bool
    scheme_free: bool
    limit_free: bool
    selector_rigid: bool
    determination_issues_truth: bool = False
    absolute_level_determined: bool = False
    finite_observation_scope: bool = True
    reference_member: str
    common_component_chart: list[str]
    relative_member_chart: dict[str, str]
    pairwise_differences: dict[str, dict[str, str]]
    pairwise_max_drift: dict[str, dict[str, str]]
    maximum_drift: str
    cocycle_consistent: bool
    greatest_scheme_invariant_content: bool
    dropped_content: str = "common additive absolute level"
    obstructions: list[dict[str, Any]] = Field(default_factory=list)


class RegularizedFamily(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    parent_family_id: str | None
    name: str
    authored_by: str
    perspective_id: str | None
    problem_id: str | None
    cutoff_labels: list[str]
    members: dict[str, list[str]]
    tolerance: str
    universality_source_ids: list[str]
    universality: UniversalityEvaluation
    status: str
    metadata: dict[str, Any]
    created_at: str


class RenormalizationSchemeCreate(BaseModel):
    name: str = Field(default="scheme chart", min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    counterterm: list[Decimal] = Field(min_length=1)
    shift_probe: Decimal = Decimal("1")
    scheme_source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_scheme(self) -> "RenormalizationSchemeCreate":
        self.counterterm = [Decimal(str(value)) for value in self.counterterm]
        if any(not value.is_finite() for value in self.counterterm):
            raise ValueError("counterterm contains a non-finite value")
        self.shift_probe = Decimal(str(self.shift_probe))
        if not self.shift_probe.is_finite():
            raise ValueError("shift_probe must be finite")
        self.scheme_source_ids = list(dict.fromkeys(self.scheme_source_ids))
        return self


class SchemeEvaluation(BaseModel):
    admissible_scheme: bool
    counterterm: list[str]
    renormalized_sequences: dict[str, list[str]]
    renormalized_values: dict[str, str]
    maximum_residual_drift: str
    relative_differences: dict[str, dict[str, str]]
    matches_relative_closure: bool
    shift_probe: str
    shifted_counterterm: list[str]
    shifted_renormalized_values: dict[str, str]
    shift_moves_absolute_values: bool
    shift_preserves_relative_closure: bool
    absolute_chart_noncanonical: bool = True
    scheme_is_closure: bool = False
    relative_closure_limit_required: bool = False
    external_condition_required_for_absolute_level: bool = True


class RenormalizationScheme(BaseModel):
    id: str
    family_id: str
    occurrence_id: str
    integration_event_id: str
    name: str
    authored_by: str
    scheme_source_ids: list[str]
    evaluation: SchemeEvaluation
    metadata: dict[str, Any]
    created_at: str


class RenormalizationFieldProjection(BaseModel):
    generated_at: str
    families: list[RegularizedFamily]
    schemes: list[RenormalizationScheme]
    stats: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
    formal_reading: str = "NRRF781"
    canonical_runtime_operation: str = "integrate"
    scheme_is_closure: bool = False
    absolute_level_determined: bool = False
    determination_issues_truth: bool = False
