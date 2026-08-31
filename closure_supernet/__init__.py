"""Closure Supernet package.

Importing the published package has no semantic side effects.  Historical
research runtimes remain available through lazy compatibility attributes, but
the production entrypoint imports only the minimal translational projection.
"""

from typing import Any


__version__ = "3.20.0"
__all__ = ["ClosureSupernetRuntime", "RuntimeConfig"]


def __getattr__(name: str) -> Any:
    if name == "RuntimeConfig":
        from .config import RuntimeConfig

        return RuntimeConfig
    if name == "ClosureSupernetRuntime":
        from .runtime import ClosureSupernetRuntime

        return ClosureSupernetRuntime
    raise AttributeError(name)
