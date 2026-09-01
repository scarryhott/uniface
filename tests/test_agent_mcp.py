from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient
from mcp import Client

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.supernet_closure_form import TRANSLATE_OPERATOR


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "agent-mcp.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def _structured(result):
    payload = result.structured_content
    assert payload is not None
    if set(payload) == {"result"} and isinstance(payload["result"], dict):
        return payload["result"]
    return payload


def test_agent_mcp_is_transport_over_the_published_closure_runtime(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        response = client.get("/supernet/agent/capabilities")
        assert response.status_code == 200
        caps = response.json()
        assert caps["endpoint"] == "/mcp"
        assert caps["tool_only"] is True
        assert caps["same_runtime"] is True
        assert caps["published_semantic_carrier"] == "SUPERNET_CLOSURE_FORM"
        assert caps["translation_operator"] == TRANSLATE_OPERATOR
        assert caps["agent_interaction_is_supernet_translate"] is True
        assert caps["self_runtime_is_closure_form_reading"] is True
        assert caps["separate_agent_mutation_authority"] is False
        assert caps["admin_privilege"] is False
        assert caps["truth_privilege"] is False
        assert "/mcp" in {getattr(route, "path", None) for route in app.routes}


def test_agent_offer_is_the_same_translation_and_self_runtime_reading(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    runtime = app.state.runtime
    exact = "Agent and participant share one source-preserving relation."

    async def scenario() -> None:
        async with Client(app.state.supernet_agent_mcp) as client:
            listed = await client.list_tools()
            names = {tool.name for tool in listed.tools}
            assert {
                "supernet_observe",
                "supernet_offer",
                "supernet_relate",
                "supernet_refine",
                "supernet_return",
                "supernet_reopen",
                "supernet_collective",
            }.issubset(names)

            before = _structured(
                await client.call_tool(
                    "supernet_observe", {"perspective_id": "openai-agent"}
                )
            )
            offered = _structured(
                await client.call_tool(
                    "supernet_offer",
                    {
                        "exact_text": exact,
                        "actor_id": "openai-agent",
                        "perspective_id": "openai-agent",
                        "form_label": "agent interaction",
                        "sheaf": "AGI_SECOND_BRAIN",
                    },
                )
            )
            assert offered["truth_issued"] is False
            assert offered["translation"]["operator"] == TRANSLATE_OPERATOR
            assert offered["translation"]["runtime_state_change_is_this_translation"] is True
            assert offered["agent_interaction_is_this_translation"] is True
            assert offered["separate_agent_mutation_authority"] is False
            assert offered["self_runtime"]["runtime_identity_is_translational_truth"] is True
            assert offered["translation"]["source_runtime_identity_id"] == before["self_runtime"]["runtime_identity_id"]
            assert offered["translation"]["target_runtime_identity_id"] == offered["self_runtime"]["runtime_identity_id"]

            returns = runtime.ledger.list_returns()
            assert returns
            assert returns[-1]["exact_source"] == exact

            observed = _structured(
                await client.call_tool(
                    "supernet_observe",
                    {
                        "event_id": offered["event_id"],
                        "perspective_id": "openai-agent",
                    },
                )
            )
            assert observed["self_runtime"]["runtime_identity_id"] == offered["self_runtime"]["runtime_identity_id"]
            assert observed["self_runtime"]["self_observation_authors_truth"] is False
            assert observed["subsystems_are_lenses"] is True

    try:
        asyncio.run(scenario())
    finally:
        runtime.close()
