from __future__ import annotations

import re
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


_PROTOCOL_VERSION = "closure.supernet/v1"
_ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class IntegrationKind(StrEnum):
    WEBHOOK_IN = "WEBHOOK_IN"
    WEBHOOK_OUT = "WEBHOOK_OUT"
    GITHUB_REPOSITORY = "GITHUB_REPOSITORY"
    HTTP_JSON_FEED = "HTTP_JSON_FEED"


class IntegrationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    kind: IntegrationKind
    config: dict[str, Any] = Field(default_factory=dict)
    secret_env: str | None = None
    enabled: bool = True

    @field_validator("secret_env")
    @classmethod
    def validate_secret_env(cls, value: str | None) -> str | None:
        if value is not None and not _ENV_NAME.fullmatch(value):
            raise ValueError("secret_env must be an environment-variable name, not a secret value")
        return value


class IntegrationRecord(BaseModel):
    id: str
    name: str
    kind: IntegrationKind
    config: dict[str, Any]
    secret_env: str | None
    enabled: bool
    cursor: dict[str, Any]
    last_success_at: str | None
    last_error: str | None
    created_at: str
    updated_at: str


class ExternalOccurrence(BaseModel):
    external_id: str | None = None
    exact_text: str = Field(min_length=1)
    source_id: str | None = None
    source_location: str | None = None
    source_context: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class IntegrationEnvelope(BaseModel):
    version: Literal["closure.supernet/v1"] = _PROTOCOL_VERSION
    items: list[ExternalOccurrence] = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IntegrationRunResult(BaseModel):
    id: str
    integration_id: str
    direction: str
    status: str
    pulled: int = 0
    pushed: int = 0
    skipped: int = 0
    errors: int = 0
    cursor: dict[str, Any] = Field(default_factory=dict)
    message: str = ""
    started_at: str
    finished_at: str


class IntegrationCapabilities(BaseModel):
    protocol: str = _PROTOCOL_VERSION
    kinds: list[IntegrationKind]
    inbound_signature_header: str = "X-Closure-Signature"
    outbound_signature_header: str = "X-Closure-Signature"
    secrets_are_environment_references: bool = True
    source_occurrences_are_immutable: bool = True
    turing_complete_assumed: bool = False
    zero_infinity_role: str = "reciprocal poles"
