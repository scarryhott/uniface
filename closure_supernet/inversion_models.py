from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator


Matrix3 = list[list[Decimal]]
Vector3 = list[Decimal]


def _decimal(value: Any, label: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except Exception as exc:  # pragma: no cover - pydantic reports the path
        raise ValueError(f"{label} must contain decimal values") from exc
    if not result.is_finite():
        raise ValueError(f"{label} values must be finite")
    return result


def normalize_matrix3(value: Any, label: str = "matrix") -> Matrix3:
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"{label} must have exactly three rows")
    rows: Matrix3 = []
    for row_index, row in enumerate(value):
        if not isinstance(row, list) or len(row) != 3:
            raise ValueError(f"{label} row {row_index} must have exactly three entries")
        rows.append([
            _decimal(entry, f"{label}[{row_index}]")
            for entry in row
        ])
    return rows


def normalize_vector3(value: Any, label: str = "vector") -> Vector3:
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"{label} must have exactly three entries")
    return [_decimal(entry, label) for entry in value]


class HairConstructionKind(StrEnum):
    ENTANGLEMENT_ORDER_DEFECT = "ENTANGLEMENT_ORDER_DEFECT"
    SUPERPOSITION_HAIR_SUM = "SUPERPOSITION_HAIR_SUM"
    SINGULARITY_SEAM_HAIR = "SINGULARITY_SEAM_HAIR"
    DEMON_NEUTRAL_NO_GAIN = "DEMON_NEUTRAL_NO_GAIN"


class LocalRelationCreate(BaseModel):
    """Finite executable chart of the NRRF796 local-relation reading."""

    name: str = Field(min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    matrix: Matrix3
    source_event_id: str | None = None
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    tolerance: Decimal = Decimal("1e-24")
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def normalize(self) -> "LocalRelationCreate":
        self.matrix = normalize_matrix3(self.matrix)
        self.tolerance = _decimal(self.tolerance, "tolerance")
        if self.tolerance <= 0:
            raise ValueError("tolerance must be positive")
        self.source_ids = list(dict.fromkeys(str(item) for item in self.source_ids))
        return self


class LocalRelationEvaluation(BaseModel):
    relation: list[list[str]]
    return_inversion: list[list[str]]
    return_inversion_involutive: bool
    return_inversion_linear_chart: bool = True
    return_inversion_forced_under_declared_conditions: bool = True

    return_symmetric_part: list[list[str]]
    hair_part: list[list[str]]
    scale_part: list[list[str]]
    neutral_part: list[list[str]]
    reconstruction: list[list[str]]
    reconstruction_exact: bool

    divergence: str
    normalized_hair: list[str]
    coordinate_curl: list[str]
    axial_reconstruction_exact: bool

    divergence_reversed_by_inversion: bool
    hair_preserved_by_inversion: bool
    hair_sector_fixed: bool
    return_symmetric_sector_anti_fixed: bool
    neutral_sector_anti_fixed: bool

    total_content: str
    scale_content: str
    hair_content: str
    neutral_content: str
    self_limit_sum: str
    self_limit_exact: bool
    self_limit_inversion_invariant: bool
    divergence_within_self_limit: bool
    hair_within_self_limit: bool
    scale_saturation: bool
    hair_saturation: bool
    joint_readings_saturate: bool
    joint_saturation_iff_neutral_zero: bool

    pure_scale: bool
    pure_hair: bool
    neutral_zero: bool
    neutral_nonzero: bool
    unique_hair_reading_under_declared_conditions: bool = True
    representation_required: bool = False
    representation_used: bool = False
    runtime_normalization: str = "normalized_hair is the inverse axial vector of (A-Aᵀ)/2; coordinate_curl is twice that vector"
    runtime_content_chart: str = "Frobenius-squared orthogonal sector content"
    runtime_is_formal_proof: bool = False
    physical_law_claimed: bool = False
    truth_issued: bool = False


class LocalRelation(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    name: str
    authored_by: str
    source_event_id: str | None
    perspective_id: str | None
    problem_id: str | None
    matrix: list[list[str]]
    tolerance: str
    evaluation: LocalRelationEvaluation
    source_ids: list[str]
    metadata: dict[str, Any]
    created_at: str


class EntanglementConstructionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    left_hair: Vector3
    right_hair: Vector3
    source_event_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    tolerance: Decimal = Decimal("1e-24")
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def normalize(self) -> "EntanglementConstructionCreate":
        self.left_hair = normalize_vector3(self.left_hair, "left_hair")
        self.right_hair = normalize_vector3(self.right_hair, "right_hair")
        self.tolerance = _decimal(self.tolerance, "tolerance")
        if self.tolerance <= 0:
            raise ValueError("tolerance must be positive")
        self.source_ids = list(dict.fromkeys(str(item) for item in self.source_ids))
        return self


class SuperpositionConstructionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    summands: list[Matrix3] = Field(min_length=2)
    source_event_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    tolerance: Decimal = Decimal("1e-24")
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def normalize(self) -> "SuperpositionConstructionCreate":
        self.summands = [
            normalize_matrix3(matrix, f"summands[{index}]")
            for index, matrix in enumerate(self.summands)
        ]
        self.tolerance = _decimal(self.tolerance, "tolerance")
        if self.tolerance <= 0:
            raise ValueError("tolerance must be positive")
        self.source_ids = list(dict.fromkeys(str(item) for item in self.source_ids))
        return self


class SingularityConstructionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    direction: Vector3
    angle_radians: Decimal
    at_seam: bool = False
    source_event_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    tolerance: Decimal = Decimal("1e-12")
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def normalize(self) -> "SingularityConstructionCreate":
        self.direction = normalize_vector3(self.direction, "direction")
        self.angle_radians = _decimal(self.angle_radians, "angle_radians")
        self.tolerance = _decimal(self.tolerance, "tolerance")
        if self.tolerance <= 0:
            raise ValueError("tolerance must be positive")
        self.source_ids = list(dict.fromkeys(str(item) for item in self.source_ids))
        return self


class DemonConstructionCreate(BaseModel):
    """One submitted witness of the module's neutral no-gain conditions."""

    name: str = Field(min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    neutral_input: Matrix3
    submitted_output: Matrix3
    source_event_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    tolerance: Decimal = Decimal("1e-24")
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def normalize(self) -> "DemonConstructionCreate":
        self.neutral_input = normalize_matrix3(self.neutral_input, "neutral_input")
        self.submitted_output = normalize_matrix3(self.submitted_output, "submitted_output")
        self.tolerance = _decimal(self.tolerance, "tolerance")
        if self.tolerance <= 0:
            raise ValueError("tolerance must be positive")
        self.source_ids = list(dict.fromkeys(str(item) for item in self.source_ids))
        return self


class HairConstruction(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    kind: HairConstructionKind
    name: str
    authored_by: str
    source_event_id: str | None
    payload: dict[str, Any]
    evaluation: dict[str, Any]
    source_ids: list[str]
    metadata: dict[str, Any]
    created_at: str


class InversionFieldProjection(BaseModel):
    generated_at: str
    relations: list[LocalRelation]
    constructions: list[HairConstruction]
    stats: dict[str, Any]
    source_reverse_index: dict[str, list[str]]
    formal_readings: list[str] = Field(default_factory=lambda: ["NRRF795", "NRRF796"])
    canonical_runtime_operation: str = "integrate"
    representation_required: bool = False
    unique_inversion_under_declared_conditions: bool = True
    unique_hair_reading_under_declared_conditions: bool = True
    self_limit_chart: str = "Frobenius-squared scale + hair + neutral decomposition"
    physical_law_claimed: bool = False
    runtime_is_formal_proof: bool = False
    determination_issues_truth: bool = False
