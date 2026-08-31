from __future__ import annotations

"""Current executable vocabulary for the historical closure audit."""

from typing import Sequence
from . import archive_closure_audit as _base

_base_normalize = _base._normalize


def _current_normalize(value: str) -> str:
    return " ".join(_base_normalize(value).replace(".", " ").split())


_base._normalize = _current_normalize
for _term in ("translates", "translated", "translating"):
    _normalized = _base._normalize(_term)
    if _normalized not in _base.RELATION_MARKERS:
        _base.RELATION_MARKERS = (*_base.RELATION_MARKERS, _normalized)

# One capability: the historical/versioned atlas relative to current TT. Older
# selector / unified-field wording is an alias, not a second semantic stage.
_base.CAPABILITIES["current-closure-relative-natural-form-atlas"] = (
    (
        "current closure relative natural form atlas",
        "current-closure-relative natural-form atlas",
        "full natural form atlas",
        "full natural-form atlas",
        "unified natural form field",
        "natural form field",
        "recognition equals selection",
        "natural form selector",
        "natural-form selector",
        "natural form selects interaction",
        "natural-form interaction selection",
        "open boundary is interaction frontier",
        "local global relative to current translational truth",
        "local-global relative to current translational truth",
        "local global is relative to current translational truth",
        "local-global is relative to current translational truth",
    ),
    ("current_closure_relative_natural_form_atlas.derive_current_closure_relative_atlas",),
)
_base.CAPABILITIES.pop("unified-natural-form-field", None)
_base.CAPABILITY_ALIASES = sorted(
    ((_base._normalize(alias), capability_id) for capability_id, (aliases, _) in _base.CAPABILITIES.items() for alias in aliases),
    key=lambda item: (-len(item[0]), item[0]),
)
_base.RUNTIME_CAPABILITIES = _base.CAPABILITIES

PROTOCOL = _base.PROTOCOL
SCHEMA = _base.SCHEMA
EXECUTABLE = _base.EXECUTABLE
WITNESSED = _base.WITNESSED
REGISTERED = _base.REGISTERED
OPEN = _base.OPEN
MISSING = _base.MISSING
STATUSES = _base.STATUSES
CAPABILITIES = _base.CAPABILITIES
RUNTIME_CAPABILITIES = _base.RUNTIME_CAPABILITIES
parse_archive = _base.parse_archive
classify_condition = _base.classify_condition
audit_archive = _base.audit_archive
audit_summary = _base.audit_summary
validate_archive_audit = _base.validate_archive_audit


def main(argv: Sequence[str] | None = None) -> int:
    return _base.main(argv)


__all__ = ["PROTOCOL","SCHEMA","EXECUTABLE","WITNESSED","REGISTERED","OPEN","MISSING","STATUSES","CAPABILITIES","RUNTIME_CAPABILITIES","parse_archive","classify_condition","audit_archive","audit_summary","validate_archive_audit","main"]
