"""Closure Supernet unified living integration runtime.

Exact source occurrences remain canonical. The runtime's one semantic operation
is continuous integration: every offered or returned relative form receives an
append-only integration receipt and contributes to a replayable successor field.
Living, translation, equality, resource, reopening, agent and bounded hardware
modules remain adapters and lenses over that field.
"""

from . import living_store_runtime as _living_store_runtime
from . import reopening_store_runtime as _reopening_store_runtime
from .config import RuntimeConfig
from .runtime import ClosureSupernetRuntime
from . import resource_runtime as _resource_runtime
from . import equality_runtime as _equality_runtime
from . import hardware_runtime as _hardware_runtime
from . import supernet_runtime as _supernet_runtime

__all__ = ["RuntimeConfig", "ClosureSupernetRuntime"]
__version__ = "1.0.0"
