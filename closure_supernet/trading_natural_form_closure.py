from __future__ import annotations

"""Compatibility import for the authoritative NRRF870 trading closure.

The current trading runtime is implemented in
``trading_translation_closure_nrrf870``. This module name is retained so older
callers do not become a second semantic surface.
"""

from .trading_translation_closure_nrrf870 import (
    PROTOCOL,
    resolve_open_sensor_trading_closure,
)

__all__ = ["PROTOCOL", "resolve_open_sensor_trading_closure"]
