from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient
from mcp import Client

from closure_supernet.api_agent import create_app
from closure_supernet.config import RuntimeConfig


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


def test_agent_mcp_is_mounted_on_the_completed_runtime(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        caps = client.get("/supernet/agent/capabilities")
        assert caps.status_code == 200
        payload = caps.json()
        assert payload["endpoint"] == "/mcp"
        assert payload["tool_only"] is True
        assert payload["same_runtime"] is True
        assert payload["admin_privilege"] is False
        assert payload["truth_privilege"] is False
        assert "supernet_offer" in payload["tools"]
        routes = {getattr(route, "path", None) for route in app.routes}
        assert "/mcp" in routes
        assert app.version == "3.11.0"


def test_mcp_agent_discovers_tools_and_participates_in_live_sense(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    runtime = app.state.runtime

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

            first_call = await client.call_tool(
                "supernet_offer",
                {
                    "exact_text": "Agent and participant share one source-preserving relation.",
                    "actor_id": "openai-agent",
                    "perspective_id": "openai-agent",
                    "form_label": "agent interaction",
                    "sheaf": "AGI_SECOND_BRAIN",
                },
            )
            assert first_call.is_error is False
            first = _structured(first_call)
            first_id = first["event_id"]
            event = runtime.supernet_store.get_event(first_id)
            assert event["authored_by"] == "openai-agent"
            assert event["perspective_id"] == "openai-agent"
            assert event["metadata"]["agent_mcp"] is True
            assert event["metadata"]["sheaf"] == "AGI_SECOND_BRAIN"
            assert first["truth_issued"] is False

            second_call = await client.call_tool(
                "supernet_offer",
                {
                    "exact_text": "Agent and participant share one source-preserving relation.",
                    "actor_id": "participant-b",
                    "perspective_id": "participant-b",
                    "form_label": "human interaction",
                    "sheaf": "HUMAN_INTERACTION",
                },
            )
            second = _structured(second_call)
            assert second["sense_receipt"]["candidate_relation_ids"]
            assert second["sense_receipt"]["formal_pipeline_reused"] is True
            assert second["interface"]["sense_depth"] is not None
            assert second["truth_issued"] is False

            store = runtime.supernet_store
            stale_row = store._conn.execute(  # noqa: SLF001 - upgrade fixture
                """SELECT id,receipt FROM supernet_visual_closure_receipts
                WHERE source_event_id=? ORDER BY seq DESC LIMIT 1""",
                (second["event_id"],),
            ).fetchone()
            assert stale_row is not None
            stale_payload = json.loads(str(stale_row["receipt"]))
            stale_coordination = stale_payload.get("coordination") or {}
            stale_coordination.pop("nrrf837_continuum", None)
            stale_coordination.pop("continuum", None)
            stale_payload["coordination"] = stale_coordination
            with store._lock:  # noqa: SLF001 - upgrade fixture
                store._conn.execute(  # noqa: SLF001 - upgrade fixture
                    """UPDATE supernet_visual_closure_receipts
                    SET input_signature=?,receipt=? WHERE id=?""",
                    (
                        f"pre-nrrf837:mcp:{second['event_id']}",
                        json.dumps(stale_payload, sort_keys=True),
                        str(stale_row["id"]),
                    ),
                )
                store._conn.commit()  # noqa: SLF001 - upgrade fixture

            observed = _structured(
                await client.call_tool(
                    "supernet_observe",
                    {"event_id": second["event_id"], "perspective_id": "participant-b"},
                )
            )
            assert any(
                row["id"] == second["event_id"] for row in observed["recent_events"]
            )
            assert any(
                source["exact_text"]
                == "Agent and participant share one source-preserving relation."
                for source in observed["interface"]["source_fibre"]
            )
            assert observed["interface"]["sense_depth"] is not None
            assert observed["interface"]["visual_closure"]["coordination"][
                "nrrf837_continuum"
            ]["schema"] == "closure.supernet/nrrf837-continuum-v1"
            assert observed["interface"]["visual_closure"]["id"] != str(
                stale_row["id"]
            )
            assert observed["subsystems_are_lenses"] is True
            assert observed["truth_issued"] is False

    try:
        asyncio.run(scenario())
    finally:
        runtime.close()
