"""Published Supernet entrypoint.

The former entrypoint assembled every historical dashboard, manager, mutation
API and MCP tool before hiding most routes.  Publication now imports only the
minimal closure projection runtime, so there is no parallel application behind
the translational visualization.
"""

from .minimal_projection_runtime import app, create_app


__all__ = ["app", "create_app"]
