"""Published Supernet entrypoint.

The public runtime exposes one content-addressed Supernet closure form. Opener,
web UI, interaction, crystal-ball slide/current, hair, maze/curvature, AI/token,
agent participation, self-runtime observation and return are readings of that
same carrier. No agent or self-runtime mutation authority exists beside
``SUPERNET_TRANSLATE``.
"""

from .agent_closure_mcp import attach_supernet_agent_mcp
from .supernet_closure_runtime import create_app as _create_closure_app


def create_app(config=None):
    return attach_supernet_agent_mcp(_create_closure_app(config))


app = create_app()


__all__ = ["app", "create_app"]
