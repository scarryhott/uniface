from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from . import api_natural_interface as base_api
from . import agent_mcp as agent_mcp_module
from .agent_mcp import attach_supernet_agent_mcp
from .config import RuntimeConfig


def _compact_interface_with_focus(
    runtime: Any,
    event_id: str | None,
    perspective_id: str | None,
) -> dict[str, Any]:
    """Keep the explicit agent focus even when the UI receipt stores it as an object."""

    receipt = runtime.natural_interface.select(
        focus_event_id=event_id,
        perspective_id=perspective_id,
    )
    focused = receipt.get("focus_event") or {}
    return {
        "focus_event_id": receipt.get("focus_event_id") or focused.get("id") or event_id,
        "perspective_id": perspective_id,
        "natural_chart": receipt.get("natural_chart"),
        "sense_depth": receipt.get("sense_depth"),
        "proof_depth": receipt.get("proof_depth"),
        "continuation_depth": receipt.get("continuation_depth"),
        "turing_being_depth": receipt.get("turing_being_depth"),
        "source_fibre": receipt.get("source_fibre", []),
        "truth_issued": False,
    }


# Tool functions registered by agent_mcp resolve this module global at call time.
# Correct the compact projection without introducing another runtime or tool layer.
agent_mcp_module._compact_interface = _compact_interface_with_focus


def create_app(config: RuntimeConfig | None = None) -> FastAPI:
    return attach_supernet_agent_mcp(base_api.create_app(config))


app = attach_supernet_agent_mcp(base_api.app)

__all__ = ["app", "create_app"]
