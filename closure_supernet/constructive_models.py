from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


def _unique_strings(values: list[str], label: str) -> list[str]:
    normalized = [str(item).strip() for item in values]
    if any(not item for item in normalized):
        raise ValueError(f"{label} entries must be non-empty")
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{label} entries must be unique")
    return normalized


def _string_map(values: dict[str, str]) -> dict[str, str]:
    return {str(key).strip(): str(value).strip() for key, value in values.items()}


class AxiometricFormCreate(BaseModel):
    """A finite executable chart of the constructive closure datum.

    The section/encoding is supplied as data. The runtime checks U1, derives
    the hold translation and U2, and reads U3 through the explicit defect.
    """

    name: str = Field(min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    source_carrier: list[str] = Field(min_length=1)
    presentation_carrier: list[str] = Field(min_length=1)
    encode: dict[str, str] = Field(min_length=1)
    evaluate: dict[str, str] = Field(min_length=1)
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_chart(self) -> "AxiometricFormCreate":
        self.source_carrier = _unique_strings(self.source_carrier, "source_carrier")
        self.presentation_carrier = _unique_strings(
            self.presentation_carrier, "presentation_carrier"
        )
        self.encode = _string_map(self.encode)
        self.evaluate = _string_map(self.evaluate)
        source = set(self.source_carrier)
        presentation = set(self.presentation_carrier)
        if set(self.encode) != source:
            raise ValueError("encode must be total exactly on source_carrier")
        if set(self.evaluate) != presentation:
            raise ValueError("evaluate must be total exactly on presentation_carrier")
        if any(value not in presentation for value in self.encode.values()):
            raise ValueError("encode values must lie in presentation_carrier")
        if any(value not in source for value in self.evaluate.values()):
            raise ValueError("evaluate values must lie in source_carrier")
        self.source_ids = list(dict.fromkeys(str(item) for item in self.source_ids))
        return self


class IdempotentTranslationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    carrier: list[str] = Field(min_length=1)
    translation: dict[str, str] = Field(min_length=1)
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_translation(self) -> "IdempotentTranslationCreate":
        self.carrier = _unique_strings(self.carrier, "carrier")
        self.translation = _string_map(self.translation)
        carrier = set(self.carrier)
        if set(self.translation) != carrier:
            raise ValueError("translation must be total exactly on carrier")
        if any(value not in carrier for value in self.translation.values()):
            raise ValueError("translation values must lie in carrier")
        self.source_ids = list(dict.fromkeys(str(item) for item in self.source_ids))
        return self


class AxiometricFormEvaluation(BaseModel):
    u1_return: bool
    u1_failures: list[dict[str, str]]
    hold: dict[str, str]
    u2_hold_idempotent: bool
    u2_derived_from_u1: bool
    u3_closes: bool
    defect: list[str]
    defect_empty: bool
    defect_empty_iff_closes: bool
    encode_injective: bool
    evaluate_surjective: bool
    encode_surjective: bool
    evaluate_injective: bool
    fixed_presentations: list[str]
    admissible_form: bool
    section_carried_as_data: bool = True
    classical_choice_required: bool = False
    excluded_middle_required: bool = False
    decidable_carrier_equality: bool = True
    determination_issues_truth: bool = False


class AxiometricForm(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    name: str
    origin: str
    authored_by: str
    perspective_id: str | None
    problem_id: str | None
    source_carrier: list[str]
    presentation_carrier: list[str]
    encode: dict[str, str]
    evaluate: dict[str, str]
    evaluation: AxiometricFormEvaluation
    source_ids: list[str]
    metadata: dict[str, Any]
    created_at: str


class FiniteCommutativeGroupCreate(BaseModel):
    name: str = Field(default="finite commutative group", min_length=1, max_length=240)
    elements: list[str] = Field(min_length=1)
    zero: str = Field(min_length=1)
    addition: dict[str, dict[str, str]] = Field(min_length=1)
    inverse: dict[str, str] = Field(min_length=1)

    @model_validator(mode="after")
    def normalize_group(self) -> "FiniteCommutativeGroupCreate":
        self.elements = _unique_strings(self.elements, "group elements")
        self.zero = str(self.zero).strip()
        self.addition = {
            str(left).strip(): {
                str(right).strip(): str(value).strip()
                for right, value in row.items()
            }
            for left, row in self.addition.items()
        }
        self.inverse = _string_map(self.inverse)
        return self


class TranslationalClosureCreate(BaseModel):
    name: str = Field(min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    group: FiniteCommutativeGroupCreate
    sites: list[str] = Field(min_length=1)
    base_site: str = Field(min_length=1)
    levels: dict[str, str] = Field(min_length=1)
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_levels(self) -> "TranslationalClosureCreate":
        self.sites = _unique_strings(self.sites, "sites")
        self.base_site = str(self.base_site).strip()
        if self.base_site not in self.sites:
            raise ValueError("base_site must be supplied as one of sites")
        self.levels = _string_map(self.levels)
        if set(self.levels) != set(self.sites):
            raise ValueError("levels must be total exactly on sites")
        self.source_ids = list(dict.fromkeys(str(item) for item in self.source_ids))
        return self


class TranslationalClosureEvaluation(BaseModel):
    group_valid: bool
    base_site_supplied: bool
    relative_potential: dict[str, dict[str, str]]
    cocycle_consistent: bool
    common_shift_invariant: bool
    relative_potential_complete: bool
    closure_form_closes: bool
    closure_form_id: str
    absolute_levels_noncanonical: bool = True
    canonical_absolute_level: str | None = None
    site_chosen_by_runtime: bool = False
    classical_choice_required: bool = False
    excluded_middle_required: bool = False
    overlap_requires_witness: bool = True
    determination_issues_truth: bool = False


class TranslationalClosure(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    name: str
    authored_by: str
    perspective_id: str | None
    problem_id: str | None
    group: dict[str, Any]
    sites: list[str]
    base_site: str
    levels: dict[str, str]
    source_ids: list[str]
    evaluation: TranslationalClosureEvaluation
    metadata: dict[str, Any]
    created_at: str


class TranslationChartCompareCreate(BaseModel):
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    levels: dict[str, str] = Field(min_length=1)
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def normalize_levels(self) -> "TranslationChartCompareCreate":
        self.levels = _string_map(self.levels)
        self.source_ids = list(dict.fromkeys(str(item) for item in self.source_ids))
        return self


class TranslationChartComparison(BaseModel):
    id: str
    closure_id: str
    occurrence_id: str
    integration_event_id: str
    authored_by: str
    comparison_levels: dict[str, str]
    derived_shift: str
    charts_differ_by_common_shift: bool
    relative_potentials_equal: bool
    closure_equal: bool
    unique_shift: bool
    overlap_forces_equality: bool
    absolute_levels_noncanonical: bool
    classical_choice_required: bool = False
    excluded_middle_required: bool = False
    source_ids: list[str]
    metadata: dict[str, Any]
    created_at: str


class ConstructiveFieldProjection(BaseModel):
    generated_at: str
    forms: list[AxiometricForm]
    translations: list[TranslationalClosure]
    comparisons: list[TranslationChartComparison]
    stats: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
    formal_reading: str = "NRRF783"
    canonical_runtime_operation: str = "integrate"
    explicit_witnesses: bool = True
    section_carried_as_data: bool = True
    classical_choice_required: bool = False
    excluded_middle_required: bool = False
    runtime_is_formal_proof: bool = False
    determination_issues_truth: bool = False
