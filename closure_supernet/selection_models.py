from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class SelectionReadingState(StrEnum):
    EMPTY_TOTAL_ISOLATION = "EMPTY_TOTAL_ISOLATION"
    OPEN_BRANCHING = "OPEN_BRANCHING"
    NATURAL_SELECTION = "NATURAL_SELECTION"
    FORCED_ISOLATION = "FORCED_ISOLATION"


class SelectionReadingCreate(BaseModel):
    """Finite live reading of NRRF790 completeness and isolation.

    ``field_symbols`` is the available symbol field. ``admissible_symbols`` is
    the reading itself. ``selected_symbol`` is optional and records an authored
    isolation when several symbols remain admissible; it never manufactures a
    natural selection.
    """

    name: str = Field(min_length=1, max_length=240)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    field_symbols: list[str] = Field(min_length=1)
    admissible_symbols: list[str] = Field(default_factory=list)
    selected_symbol: str | None = None
    source_event_id: str | None = None
    selection_scope: str = Field(default="participant-relative", min_length=1, max_length=240)
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_key: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def normalize_reading(self) -> "SelectionReadingCreate":
        self.field_symbols = list(
            dict.fromkeys(str(item).strip() for item in self.field_symbols if str(item).strip())
        )
        if not self.field_symbols:
            raise ValueError("field_symbols must contain at least one symbol")
        self.admissible_symbols = list(
            dict.fromkeys(
                str(item).strip()
                for item in self.admissible_symbols
                if str(item).strip()
            )
        )
        field = set(self.field_symbols)
        if any(item not in field for item in self.admissible_symbols):
            raise ValueError("every admissible symbol must belong to field_symbols")
        if self.selected_symbol is not None:
            self.selected_symbol = str(self.selected_symbol).strip()
            if not self.selected_symbol:
                self.selected_symbol = None
            elif self.selected_symbol not in self.admissible_symbols:
                raise ValueError("selected_symbol must be admitted by the original reading")
        self.source_ids = list(dict.fromkeys(str(item) for item in self.source_ids))
        return self


class SelectionReadingEvaluation(BaseModel):
    state: SelectionReadingState
    complete: bool
    incomplete: bool
    empty: bool
    branching: bool
    admissible_count: int
    natural_selection: bool
    natural_selection_symbol: str | None
    forced_isolation: bool
    isolated_symbol: str | None
    removed_admissible_symbols: list[str]
    strict_strengthening: bool
    symmetry_witness: dict[str, Any] | None
    selected_symbol_fixed_by_all_reading_symmetries: bool
    completing_is_isolating: bool
    natural_selection_iff_not_forced_isolation: bool
    no_natural_selector_away_from_completeness: bool
    total_isolation_from_field: bool
    selection_authority_required: bool
    selected_orbit_not_canonical_presentation: bool = True
    truth_issued: bool = False


class SelectionReading(BaseModel):
    id: str
    occurrence_id: str
    integration_event_id: str
    name: str
    authored_by: str
    field_symbols: list[str]
    admissible_symbols: list[str]
    selected_symbol: str | None
    source_event_id: str | None
    selection_scope: str
    perspective_id: str | None
    problem_id: str | None
    evaluation: SelectionReadingEvaluation
    source_ids: list[str]
    metadata: dict[str, Any]
    created_at: str


class SelectionFieldProjection(BaseModel):
    generated_at: str
    readings: list[SelectionReading]
    stats: dict[str, int]
    source_reverse_index: dict[str, list[str]]
    formal_reading: str = "NRRF790"
    canonical_runtime_operation: str = "integrate"
    natural_selection_requires_completeness: bool = True
    incomplete_selection_is_forced_isolation: bool = True
    natural_selection_never_removes_admissible_alternative: bool = True
    empty_reading_selects_nothing: bool = True
    canonical_presentation: str | None = None
    determination_issues_truth: bool = False
