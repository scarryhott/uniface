"""Published Supernet entrypoint.

The public runtime exposes one content-addressed Supernet closure form. Opener,
web UI, interaction, crystal-ball slide/current, hair, maze/curvature, AI/token
phase and return are projections of that same carrier. Older runtime modules
remain compatibility evidence only and are not the published semantic boundary.
"""

from .supernet_closure_runtime import app, create_app


__all__ = ["app", "create_app"]
