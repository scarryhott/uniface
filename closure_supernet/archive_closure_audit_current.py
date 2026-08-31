from __future__ import annotations

"""Current runtime registry for the deterministic historical archive audit.

The base audit engine is deliberately stable.  This module extends only the
current executable vocabulary and relation morphology, then delegates all
classification and receipt logic back to that engine.
"""

from typing import Any, Mapping, Sequence

from . import archive_closure_audit as _base

# Natural-language inflections are presentation hair, not distinct relation
# semantics. They must resolve to the same cross-form translation test.
for _term in ("translates", "translated", "translating"):
    _normalized = _base._normalize(_term)
    if _normalized not in _base.RELATION_MARKERS:
        _base.RELATION_MARKERS = (*_base.RELATION_MARKERS, _normalized)

# PR #93 made natural-form OPEN interaction selection executable. Register it
# without changing any historical chart identity or equality condition.
_base.CAPABILITIES["natural-form-selector"] = (
    (
        "natural form selector",
        "natural-form selector",
        "natural form selects interaction",
        "natural-form interaction selection",
        "open boundary is interaction frontier",
    ),
    ("trading_natural_form_selector.derive_natural_form_selection",),
)
_base.CAPABILITY_ALIASES = sorted(
    (
        (_base._normalize(alias), capability_id)
        for capability_id, (aliases, _) in _base.CAPABILITIES.items()
        for alias in aliases
    ),
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


__all__ = [
    "PROTOCOL",
    "SCHEMA",
    "EXECUTABLE",
    "WITNESSED",
    "REGISTERED",
    "OPEN",
    "MISSING",
    "STATUSES",
    "CAPABILITIES",
    "RUNTIME_CAPABILITIES",
    "parse_archive",
    "classify_condition",
    "audit_archive",
    "audit_summary",
    "validate_archive_audit",
    "main",
]
