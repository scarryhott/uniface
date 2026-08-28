from __future__ import annotations

from fastapi import FastAPI

from . import api_natural_interface as base_api
from .agent_mcp import attach_supernet_agent_mcp
from .config import RuntimeConfig


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_supernet_agent_mcp(base_api.create_app(config))


app = attach_supernet_agent_mcp(base_api.app)

__all__ = ["app", "create_app"]
