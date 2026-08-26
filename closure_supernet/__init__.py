"""Closure Supernet living production runtime.

Exact source occurrences remain canonical. TranslationEvents remain directed
interaction, resources/problems/actions remain living relative forms, and the
production layer adds authenticated participation, operational durability,
realtime access control, health, audit, and recovery without becoming Closure.
"""

from . import living_store_runtime as _living_store_runtime
from . import reopening_store_runtime as _reopening_store_runtime
from .config import RuntimeConfig
from .runtime import ClosureSupernetRuntime
from . import resource_runtime as _resource_runtime
from . import equality_runtime as _equality_runtime

__all__ = ["RuntimeConfig", "ClosureSupernetRuntime"]
__version__ = "0.8.0"
