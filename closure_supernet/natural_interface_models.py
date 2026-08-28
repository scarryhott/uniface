from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class NaturalChartKind(StrEnum):
    EMPTY_FIELD = "EMPTY_FIELD"
    SOURCE_POINT = "SOURCE_POINT"
    OPEN_SELECTOR = "OPEN_SELECTOR"
    TURING_BEING = "TURING_BEING"
    RULE_GEOMETRY = "RULE_GEOMETRY"
    PROOF_BALANCE = "PROOF_BALANCE"
    RETURN_BALL_HAIR = "RETURN_BALL_HAIR"
    SHARED_ARCHITECTURE = "SHARED_ARCHITECTURE"


class NaturalInterfaceAdmissionCreate(BaseModel):
    focus_event_id: str | None = None
    perspective_id: str | None = None
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    reason: str = Field(
        default="Admit the current minimal source-reversible Black Mirror chart",
        min_length=1,
        max_length=2000,
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
