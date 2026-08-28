from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator

from .embodied_models import SheafKind


class CompleteInterfaceOffer(BaseModel):
    """One public Black Mirror offer, optionally situated in a known Supernet lens."""

    exact_text: str = Field(min_length=1)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    form_label: str = Field(default="note", min_length=1, max_length=240)
    perspective_id: str | None = None
    parent_event_id: str | None = None
    lens: str | None = Field(default=None, max_length=120)
    sheaf: SheafKind | None = None
    affected_perspectives: list[str] = Field(default_factory=list)
    relation_hints: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize(self) -> "CompleteInterfaceOffer":
        perspective = (self.perspective_id or self.authored_by).strip()
        self.perspective_id = perspective or self.authored_by
        self.affected_perspectives = list(
            dict.fromkeys(
                item
                for item in [*self.affected_perspectives, self.perspective_id]
                if item
            )
        )
        self.relation_hints = list(dict.fromkeys(self.relation_hints))
        if self.lens is not None:
            self.lens = self.lens.strip().lower() or None
        return self


class CompleteInterfaceSelection(BaseModel):
    """Authored refinement of a live Sense relation field.

    The original admissible alternatives remain in the NRRF790 receipt.  If the
    source reading branches, this is recorded as FORCED_ISOLATION rather than
    being mislabeled natural selection.
    """

    source_event_id: str = Field(min_length=1)
    selected_relation_id: str = Field(min_length=1)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    perspective_id: str | None = None
    reason: str = Field(
        default="Participant refines the live relational field",
        min_length=1,
        max_length=2000,
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class CompleteInterfaceCollective(BaseModel):
    event_ids: list[str] = Field(min_length=2)
    exact_text: str = Field(min_length=1)
    authored_by: str = Field(default="participant", min_length=1, max_length=500)
    perspective_id: str | None = None
    affected_perspectives: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize(self) -> "CompleteInterfaceCollective":
        self.event_ids = list(dict.fromkeys(self.event_ids))
        if len(self.event_ids) < 2:
            raise ValueError("A collective return needs at least two distinct events")
        if self.perspective_id:
            self.affected_perspectives = list(
                dict.fromkeys([*self.affected_perspectives, self.perspective_id])
            )
        return self
