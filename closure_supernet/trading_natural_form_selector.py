from __future__ import annotations

"""Compatibility alias for the unified trading natural-form field.

Recognition and selection are not separate semantic stages. Current code should
use ``derive_unified_natural_form_field`` directly. This module remains only so
older imports do not break; it returns the same unified pre-action field and has
no selector mode, ranking, filtering, or independent semantic authority.
"""

from typing import Any, Mapping

from .trading_unified_natural_form_field import (
    PROTOCOL,
    derive_unified_natural_form_field,
)


def derive_natural_form_selection(
    *,
    natural_closure: Mapping[str, Any],
) -> dict[str, Any]:
    field = derive_unified_natural_form_field(natural_closure=natural_closure)
    return {
        **field,
        "compatibility_selector_name_only": True,
        "separate_selector_present": False,
        "recognition_equals_selection": True,
    }


__all__ = ["PROTOCOL", "derive_natural_form_selection"]
