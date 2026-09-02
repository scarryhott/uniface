from __future__ import annotations

"""Compatibility surface for the continuous NRRF879–887 trading closure.

The older staged ENVIRONMENT -> VERIFIED_RETURN -> ... architecture is removed
as a semantic surface. Observation and trading are translation-equal readings
of one continuously reclosed state; OPEN is only its current boundary.
"""

from typing import Any, Mapping

from .trading_continuous_unified_closure_nrrf879_887 import (
    PROTOCOL,
    derive_continuous_unified_closure,
)


def derive_interactive_trading_architecture(*, trading_receipt: Mapping[str, Any]) -> dict[str, Any]:
    return derive_continuous_unified_closure(trading_receipt=trading_receipt)


__all__ = ["PROTOCOL", "derive_interactive_trading_architecture"]
