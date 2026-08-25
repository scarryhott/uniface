"""Closure Supernet autonomous runtime.

The runtime treats exact source occurrences as canonical and all embeddings,
formal charts, projections, and AI interpretations as reversible derived views.
"""

from .config import RuntimeConfig
from .runtime import ClosureSupernetRuntime

__all__ = ["RuntimeConfig", "ClosureSupernetRuntime"]
__version__ = "0.1.0"
