from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient
from mcp import Client

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.nrrf892_runtime_bridge import VISION_SLIDE_OPERATOR
from closure_supernet.supernet_closure_form import TRANSLATE_OPERATOR


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "agent-self-runtime-closure.db",
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


def test_agent_surface_is_one_closure_transition_not_parallel_runtime(tmp_path: Path) -> None:
    app = create_app(_config(tmp_path))
    with TestClient(app) as client:
        caps = client.get("/supernet/agent/capabilities")
        assert caps.status_code == 200
        payload = caps.json()

    assert payload["same_runtime"] is True
    assert payload["published_semantic_carrier"] == "SUPERNET_CLOSURE_FORM"
    assert payload["translation_operator"] == TRANSLATE_OPERATOR
    assert payload["runtime_identity"] == "TRANSLATIONAL_TRUTH_CLASS"
    assert payload["runtime_identity_is_translational_truth"] is True
    assert payload["agent_interaction_is_supernet_translate"] is True
    assert payload["self_runtime_is_closure_form_reading"] is True
    assert payload["separate_agent_mutation_authority"] is False
    assert payload["vision_slide_operator"] == VISION_SLIDE_OPERATOR


def test_agent_interaction_and_self_observation_close_through_same_runtime_identity(
    tmp_path: Path,
) -> None:
    app = create_app(_config(tmp_path))
    runtime = app.state.runtime

    async def scenario() -> None:
        async with Client(app.state.supernet_agent_mcp) as client:
            before = _structured(
                await client.call_tool(
                    "supernet_observe",
                    {"perspective_id": "openai-agent"},
                )
            )
            self_before = before["self_runtime"]
            assert self_before["published_semantic_carrier"] == "SUPERNET_CLOSURE_FORM"
            assert self_before["translation_operator"] == TRANSLATE_OPERATOR
            assert self_before["runtime_identity_is_translational_truth"] is True

            offered = _structured(
                await client.call_tool(
                    "supernet_offer",
                    {
                        "exact_text": "Agent interaction returns into the same self runtime closure form.",
                        "actor_id": "openai-agent",
                        "perspective_id": "openai-agent",
                        "form_label": "agent self runtime interaction",
                        "sheaf": "AGI_SECOND_BRAIN",
                    },
                )
            )
            translation = offered["translation"]
            assert translation["operator"] == TRANSLATE_OPERATOR
            assert translation["runtime_state_change_is_this_translation"] is True
            assert translation["agent_interaction_is_this_translation"] is True
            assert translation["runtime_identity_is_translational_truth"] is True
            assert translation["source_runtime_identity_id"] == self_before["runtime_identity_id"]
            assert translation["target_runtime_identity_id"] == offered["self_runtime"]["runtime_identity_id"]
            assert offered["self_runtime"]["published_semantic_carrier"] == "SUPERNET_CLOSURE_FORM"
            assert offered["self_runtime"]["translation_operator"] == TRANSLATE_OPERATOR

            after = _structured(
                await client.call_tool(
                    "supernet_observe",
                    {
                        "event_id": offered["event_id"],
                        "perspective_id": "openai-agent",
                    },
                )
            )
            assert after["self_runtime"]["runtime_identity_id"] == offered["self_runtime"]["runtime_identity_id"]
            assert after["self_runtime"]["runtime_identity_is_translational_truth"] is True
            assert after["self_runtime"]["self_observation_authors_truth"] is False

    try:
        asyncio.run(scenario())
    finally:
        runtime.close()
