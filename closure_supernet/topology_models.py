from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from .models import EvidenceStatus


class TopologyMode(StrEnum):
    FIELD = "field"
    PERSPECTIVE_ZOOM = "perspective-zoom"
    POINT_LINE_LOOP = "point-line-loop"
    TRUTH_DIAGONAL = "truth-diagonal"
    METAVECTOR = "metavector"
    BALL_HAIR = "ball-hair"
    ZERO_INFINITY = "zero-infinity"
    LIGHT_CONE = "light-cone"
    ELLIPSE_MIRROR = "ellipse-mirror"
    SHARED_ARCHITECTURE = "shared-architecture"
    SELECTOR = "selector"
    ANATOMY_TREE = "anatomy-tree"


class EventRelationCreate(BaseModel):
    source_event_id: str = Field(min_length=1)
    target_event_id: str = Field(min_length=1)
    authored_by: str = Field(default="participant", min_length=1)
    relation_label: str = Field(default="OPEN_RELATION", min_length=1, max_length=240)
    exact_text: str | None = None
    language_label: str | None = None
    preserves: list[str] = Field(default_factory=list)
    transforms: list[str] = Field(default_factory=list)
    omitted: list[str] = Field(default_factory=list)
    affected_perspectives: list[str] = Field(default_factory=list)
    bidirectional: bool = False
    unitary: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def distinct_endpoints(self) -> "EventRelationCreate":
        if self.source_event_id == self.target_event_id:
            raise ValueError("A relation requires two distinct integration events")
        for name in ("preserves", "transforms", "omitted", "affected_perspectives"):
            setattr(self, name, list(dict.fromkeys(getattr(self, name))))
        return self


class RigidificationCreate(BaseModel):
    actor_id: str = Field(default="participant", min_length=1)
    site_admissibility: dict[str, list[str]] = Field(min_length=1)
    partial_input: dict[str, str | None] = Field(default_factory=dict)
    unitary_step: dict[str, str] = Field(default_factory=dict)
    reason: str = Field(
        default="Interaction refines the admissibility relation at the selected scope",
        min_length=1,
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize_relation(self) -> "RigidificationCreate":
        normalized: dict[str, list[str]] = {}
        for site, values in self.site_admissibility.items():
            key = str(site).strip()
            if not key:
                raise ValueError("Rigidification sites must have non-empty names")
            unique = [str(item) for item in dict.fromkeys(values) if str(item)]
            if not unique:
                raise ValueError(f"Site {key} must admit at least one symbol")
            normalized[key] = unique
        self.site_admissibility = normalized
        return self


class EventReturnCreate(BaseModel):
    actor_id: str = Field(default="participant", min_length=1)
    exact_text: str = Field(min_length=1)
    form_label: str = Field(default="returned form", min_length=1, max_length=240)
    language_label: str | None = None
    relation_hints: list[str] = Field(default_factory=list)
    affected_perspectives: list[str] = Field(default_factory=list)
    evidence_status: EvidenceStatus = EvidenceStatus.ORIGINAL_NOTE
    metadata: dict[str, Any] = Field(default_factory=dict)


class EventReopenCreate(BaseModel):
    actor_id: str = Field(default="participant", min_length=1)
    reason: str = Field(min_length=1)
    reopened_sites: list[str] = Field(default_factory=list)
    successor_hints: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CollectiveTraceCreate(BaseModel):
    authored_by: str = Field(default="participant", min_length=1)
    event_ids: list[str] = Field(min_length=2)
    exact_text: str = Field(min_length=1)
    form_label: str = Field(default="collective action", min_length=1, max_length=240)
    language_label: str | None = None
    affected_perspectives: list[str] = Field(default_factory=list)
    relation_hints: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def unique_trace(self) -> "CollectiveTraceCreate":
        self.event_ids = list(dict.fromkeys(self.event_ids))
        if len(self.event_ids) < 2:
            raise ValueError("A collective trace requires at least two distinct events")
        return self
