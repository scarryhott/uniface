"""Published Supernet entrypoint.

The production app exposes only the minimal closure projection and its one
source-preserving return relation. Interactive closure-equation evaluation is
available as a pure opt-in adapter, never as a second production operation
surface.
"""

from .minimal_projection_runtime import app, create_app


__all__ = ["app", "create_app"]
