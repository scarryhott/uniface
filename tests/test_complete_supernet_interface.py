from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_supernet import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.runtime import ClosureSupernetRuntime
from closure_supernet.supernet_models import ResourceEnvelope
from closure_supernet.topology_models import (
    CollectiveTraceCreate,
    EventRelationCreate,
    EventReopenCreate,
    EventReturnCreate,
    RigidificationCreate,
    TopologyMode,
)


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "complete-supernet.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
    )


def test_every_intended_geometry_is_one_projection_of_same_events(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            first = await runtime.integrate_resource(
                ResourceEnvelope(
                    exact_text="point → line → loop → return → new point",
                    authored_by="person-a",
                    form_label="point line loop",
                    relation_hints=["point-line-loop-return"],
                )
            )
            second = await runtime.integrate_resource(
                ResourceEnvelope(
                    exact_text="ball ↔ hair and 0 ↔ ∞ reciprocal poles",
                    authored_by="person-b",
                    form_label="ball hair",
                    relation_hints=["ball-hair", "zero-infinity"],
                )
            )
            third = await runtime.interact_with_event(
                first["event_id"],
                ResourceEnvelope(
                    exact_text="loop sensor selection returns a successor potential",
                    authored_by="closure-ai",
                    form_label="agent interaction",
                    adapter_label="agent",
                ),
            )
            await runtime.topology.create_relation(
                EventRelationCreate(
                    source_event_id=first["event_id"],
                    target_event_id=second["event_id"],
                    authored_by="person-a",
                    relation_label="BALL_HAIR_PATH_TRANSLATION",
                    preserves=["exact sources"],
                )
            )
            await runtime.topology.create_collective_trace(
                CollectiveTraceCreate(
                    authored_by="person-b",
                    event_ids=[
                        first["event_id"],
                        second["event_id"],
                        third["event_id"],
                    ],
                    exact_text="Two people and one agent form one collective trajectory.",
                )
            )
            ids = {
                item["id"] for item in runtime.supernet_integrator.projection()["events"]
            }
            for mode in TopologyMode:
                projection = runtime.topology.projection(
                    mode=mode,
                    focus_event_id=first["event_id"],
                )
                assert {item["id"] for item in projection["nodes"]} == ids
                assert projection["canonical_runtime_operation"] == "integrate"
                assert projection["subsystems_are_lenses"] is True
                assert projection["canonical_language"] is None
                assert projection["truth_issued_by_determination"] is False
            metavector = runtime.topology.projection(mode=TopologyMode.METAVECTOR)
            assert all("degree" in node["metavector"] for node in metavector["nodes"])
            assert metavector["components"]
            zero_inf = runtime.topology.projection(
                mode=TopologyMode.ZERO_INFINITY,
                focus_event_id=first["event_id"],
            )
            assert zero_inf["zero_infinity"]["zero_event_id"] == first["event_id"]
            light_cone = runtime.topology.projection(
                mode=TopologyMode.LIGHT_CONE,
                focus_event_id=first["event_id"],
            )
            assert third["event_id"] in light_cone["light_cone"]["future_event_ids"]
        asyncio.run(scenario())
    finally:
        runtime.close()


def test_interactive_rigidification_fills_only_when_relation_is_rigid(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            receipt = await runtime.integrate_resource(
                ResourceEnvelope(
                    exact_text="An undetermined string whose relation is still open.",
                    authored_by="selector-participant",
                    form_label="undetermined instantiation",
                    adapter_label="selector",
                )
            )
            open_result = runtime.topology.rigidify(
                receipt["event_id"],
                RigidificationCreate(
                    actor_id="selector-participant",
                    site_admissibility={
                        "site:0": ["point", "line"],
                        "site:1": ["loop"],
                    },
                    partial_input={"site:1": "loop"},
                ),
            )
            assert open_result["rigid"] is False
            assert open_result["open_sites"] == ["site:0"]
            assert open_result["event"]["current_verdict"] == "OPEN"

            determined = runtime.topology.rigidify(
                receipt["event_id"],
                RigidificationCreate(
                    actor_id="selector-participant",
                    site_admissibility={
                        "site:0": ["point"],
                        "site:1": ["loop"],
                    },
                    partial_input={"site:1": "loop"},
                    unitary_step={"point": "loop", "loop": "point"},
                ),
            )
            assert determined["rigid"] is True
            assert determined["determined_form"] == {
                "site:0": "point",
                "site:1": "loop",
            }
            assert determined["event"]["current_stage"] == "DETERMINED"
            assert determined["event"]["current_verdict"] == "OPEN"
            assert determined["truth_issued"] is False
            assert determined["unitary_path_partition"]["unique_generated_partition"] is True
            selector = runtime.topology.projection(
                mode=TopologyMode.SELECTOR,
                focus_event_id=receipt["event_id"],
            )
            assert selector["selector"]["rigid"] is True
            assert selector["selector"]["determined_form"]["site:0"] == "point"
        asyncio.run(scenario())
    finally:
        runtime.close()


def test_return_and_reopening_remain_in_same_field(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            source = await runtime.integrate_resource(
                ResourceEnvelope(
                    exact_text="A selected natural form can return without terminating.",
                    authored_by="participant",
                    form_label="source",
                )
            )
            returned = await runtime.topology.return_event(
                source["event_id"],
                EventReturnCreate(
                    actor_id="participant",
                    exact_text="The return becomes a new open resource.",
                    form_label="returned resource",
                ),
            )
            child_id = returned["returned_event"]["id"]
            assert returned["source_transition"]["event"]["current_stage"] == "RETURNED"
            assert returned["source_transition"]["event"]["current_verdict"] == "OPEN"
            reopened = runtime.topology.reopen(
                source["event_id"],
                EventReopenCreate(
                    actor_id="participant",
                    reason="The returned consequence reveals another open site.",
                    reopened_sites=["site:future"],
                ),
            )
            assert reopened["event"]["current_stage"] == "REOPENED"
            assert reopened["event"]["current_verdict"] == "OPEN"
            topology = runtime.topology.projection(
                mode=TopologyMode.POINT_LINE_LOOP,
                focus_event_id=source["event_id"],
            )
            assert child_id in topology["event_ids"]
            assert any(
                edge["source"] == source["event_id"] and edge["target"] == child_id
                for edge in topology["edges"]
            )
        asyncio.run(scenario())
    finally:
        runtime.close()


def test_complete_ui_and_direct_manipulation_api(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        root = client.get("/")
        assert root.status_code == 200
        assert "One continuous integrator" in root.text
        assert "truth-diagonal" in root.text
        assert "ellipse-mirror" in root.text
        assert "Rigidify" in root.text or "rigidify" in root.text

        first = client.post(
            "/supernet/integrate",
            json={
                "exact_text": "Local perspective enters the shared field.",
                "authored_by": "person-a",
                "form_label": "perspective",
            },
        ).json()
        second = client.post(
            "/supernet/integrate",
            json={
                "exact_text": "Another perspective remains distinct.",
                "authored_by": "person-b",
                "form_label": "perspective",
            },
        ).json()
        relation = client.post(
            "/supernet/relations",
            json={
                "source_event_id": first["event_id"],
                "target_event_id": second["event_id"],
                "authored_by": "person-a",
                "relation_label": "FRAME_TRANSLATION",
            },
        )
        assert relation.status_code == 200

        rigid = client.post(
            f"/supernet/events/{first['event_id']}/rigidify",
            json={
                "actor_id": "person-a",
                "site_admissibility": {"direction": ["relative-east"]},
                "partial_input": {},
                "unitary_step": {"relative-east": "relative-east"},
            },
        )
        assert rigid.status_code == 200
        assert rigid.json()["truth_issued"] is False

        topology = client.get(
            "/supernet/topology",
            params={
                "mode": "truth-diagonal",
                "focus_event_id": first["event_id"],
            },
        )
        assert topology.status_code == 200
        payload = topology.json()
        assert payload["mode"] == "truth-diagonal"
        assert payload["truth_diagonal"]["equality_during_translation"] is True

        context = client.get(f"/supernet/events/{first['event_id']}/context")
        assert context.status_code == 200
        assert context.json()["event"]["id"] == first["event_id"]
