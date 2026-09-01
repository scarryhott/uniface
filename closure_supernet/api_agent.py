"""Published Supernet entrypoint.

The public runtime exposes one content-addressed Supernet closure form. Opener,
web UI, interaction, crystal-ball slide/current, hair, maze/curvature, AI/token,
agent participation, self-runtime observation and return are readings of that
same carrier. No agent or self-runtime mutation authority exists beside
``SUPERNET_TRANSLATE``.
"""

from .agent_closure_mcp import attach_supernet_agent_mcp
from .self_runtime_projection import attach_self_runtime_projection
from .supernet_closure_runtime import create_app as _create_closure_app


def create_app(config=None):
    app = _create_closure_app(config)
    app = attach_supernet_agent_mcp(app)
    return attach_self_runtime_projection(app)


app = create_app()


__all__ = ["app", "create_app"]
