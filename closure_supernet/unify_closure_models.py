from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator

from .completion_models import InvariantReadingInput, InvariantTruthInput


def _normalize_carrier(values: list[str]) -> list[str]:
    normalized = list(dict.fromkeys(str(item) for item in values if str(item)))
    if not normalized:
        raise ValueError("carrier must contain at least one presentation")
    return normalized


def _validate_step(carrier: list[str], step: dict[str, str], label: str) -> dict[str, str]:
    known = set(carrier)
    normalized = {str(key): str(value) for key, value in step.items()}
    if set(normalized) != known:
        raise ValueError(f"{label} must assign exactly every carrier presentation")
    if any(value not in known for value in normalized.values()):
        raise ValueError(f"every {label} value must be a carrier presentation")
    return normalized


class ReturnClosureCreate(BaseModel):
    """Finite runtime presentation of NRRF802 `Closure step`."""

    name: str = Field(min_length=1, max_length=500)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    carrier: list[str] = Field(min_length=1, max_length=512)
    step: dict[str, str]
    step_label: str = Field(default="return", min_length=1, max_length=500)
    readings: list[InvariantReadingInput] = Field(default_factory=list, max_length=256)
    truths: list[InvariantTruthInput] = Field(default_factory=list, max_length=256)
    source_event_id: str | None = None
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_closure(self) -> "ReturnClosureCreate":
        self.carrier = _normalize_carrier(self.carrier)
        self.step = _validate_step(self.carrier, self.step, "step")
        known = set(self.carrier)
        for reading in self.readings:
            if set(reading.values) != known:
                raise ValueError(
                    f"reading {reading.name!r} must assign exactly every carrier presentation"
                )
        for truth in self.truths:
            if set(truth.values) != known:
                raise ValueError(
                    f"truth {truth.name!r} must assign exactly every carrier presentation"
                )
        self.source_ids = list(dict.fromkeys(self.source_ids))
        return self


class TwoReturnClosureCreate(BaseModel):
    """Finite runtime presentation of NRRF802 `Closure₂ f g`."""

    name: str = Field(min_length=1, max_length=500)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    carrier: list[str] = Field(min_length=1, max_length=512)
    first_step: dict[str, str]
    second_step: dict[str, str]
    first_label: str = Field(default="first return", min_length=1, max_length=500)
    second_label: str = Field(default="second return", min_length=1, max_length=500)
    readings: list[InvariantReadingInput] = Field(default_factory=list, max_length=256)
    truths: list[InvariantTruthInput] = Field(default_factory=list, max_length=256)
    source_event_id: str | None = None
    perspective_id: str | None = None
    problem_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_closure(self) -> "TwoReturnClosureCreate":
        self.carrier = _normalize_carrier(self.carrier)
        self.first_step = _validate_step(self.carrier, self.first_step, "first_step")
        self.second_step = _validate_step(self.carrier, self.second_step, "second_step")
        known = set(self.carrier)
        for reading in self.readings:
            if set(reading.values) != known:
                raise ValueError(
                    f"reading {reading.name!r} must assign exactly every carrier presentation"
                )
        for truth in self.truths:
            if set(truth.values) != known:
                raise ValueError(
                    f"truth {truth.name!r} must assign exactly every carrier presentation"
                )
        self.source_ids = list(dict.fromkeys(self.source_ids))
        return self


class ReturnClosureMapCreate(BaseModel):
    source_system_id: str = Field(min_length=1)
    target_system_id: str = Field(min_length=1)
    mapping: dict[str, str]
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    source_event_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ClosurePresentationCreate(BaseModel):
    """A proposed external closure map `p`, audited against one canonical closure."""

    system_id: str = Field(min_length=1)
    projection: dict[str, str]
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    source_event_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
