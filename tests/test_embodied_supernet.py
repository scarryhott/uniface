from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_embodied import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.embodied_models import (
    ALL_SHEAVES,
    GLOBAL_HAIR_SHEAVES,
    LOCAL_BALL_SHEAVES,
    EmbodiedFieldCreate,
    EmbodiedLoopSensorCreate,
    EmbodiedRelationCreate,
    EmbodiedSectionCreate,
    SheafKind,
)
from closure_supernet.runtime import ClosureSupernetRuntime


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "supernet.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
    )


async def build_full_field(runtime: ClosureSupernetRuntime):
    sections = []
    for index, sheaf in enumerate(ALL_SHEAVES):
        section = await runtime.embodied.create_section(
            EmbodiedSectionCreate(
                name=f"section {index}",
                authored_by=f"p{index}",
                sheaf=sheaf,
                exact_text=f"exact source for {sheaf.value}",
                participants=[f"p{index}"],
                perspective_ids=[f"view{index}"],
                consent_scope=["embodied-test"],
                metadata={"test": True},
            )
        )
        sections.append(section)

    relations = []
    for index in range(len(sections) - 1):
        left = sections[index]
        right = sections[index + 1]
        relation = await runtime.embodied.create_relation(
            EmbodiedRelationCreate(
                name=f"relation {index}",
                authored_by="collective",
                left_section_id=left["id"],
                right_section_id=right["id"],
                forward_translation={"from": left["sheaf"], "to": right["sheaf"]},
                reverse_translation={"from": right["sheaf"], "to": left["sheaf"]},
                preserves=[left["id"], right["id"]],
                transforms=["presentation"],
                untranslated_residue=["later interpretation"],
                affected_perspectives=[
                    *left["perspective_ids"],
                    *right["perspective_ids"],
                ],
                consented_participant_ids=[
                    *left["participants"],
                    *right["participants"],
                ],
                reopening_conditions=["new human or sensor return"],
            )
        )
        relations.append(relation)

    field = await runtime.embodied.create_field(
        EmbodiedFieldCreate(
            name="complete embodied field",
            authored_by="collective",
            section_ids=[item["id"] for item in sections],
            relation_ids=[item["id"] for item in relations],
            implementation_metrics={"energy": 1.0, "latency": 2.0},
        )
    )
    return sections, relations, field


def test_eight_sheaves_form_one_local_ball_global_hair_field(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            sections, relations, field = await build_full_field(runtime)
            evaluation = field["evaluation"]
            assert len(sections) == 8
            assert len(relations) == 7
            assert evaluation["local_ball_complete"] is True
            assert evaluation["global_hair_complete"] is True
            assert evaluation["all_eight_sheaves_present"] is True
            assert evaluation["field_connected"] is True
            assert evaluation["ball_hair_connected"] is True
            assert evaluation["unique_natural_component"] is True
            assert evaluation["canonical_presentation"] is None
            assert evaluation["global_hair_open"] is True
            assert evaluation["syntropic_attractor_is_non_scalar"] is True
            assert evaluation["resource_metrics_are_downstream"] is True
            assert evaluation["physical_force_claimed"] is False
            assert evaluation["emotion_inferred"] is False
            assert evaluation["human_worth_scored"] is False
            unknown = next(
                item
                for item in sections
                if item["sheaf"] == SheafKind.UNKNOWN_UAP_HYPOTHESIS.value
            )
            assert unknown["metadata"]["hypothesis_status"] == "OPEN"
            assert unknown["metadata"]["alien_claim_verified"] is False
            event = runtime.supernet_store.get_event(field["integration_event_id"])
            determined = next(
                state for state in event["state_history"] if state["stage"] == "DETERMINED"
            )
            assert determined["verdict"] == "OPEN"
            assert determined["metadata"]["truth_issued"] is False
            assert determined["determined_form"]["canonical_presentation"] is None

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_relation_without_consent_remains_open(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            left = await runtime.embodied.create_section(
                EmbodiedSectionCreate(
                    name="human",
                    authored_by="a",
                    sheaf=SheafKind.HUMAN_INTERACTION,
                    exact_text="voluntary statement",
                    participants=["a"],
                    perspective_ids=["a-view"],
                )
            )
            right = await runtime.embodied.create_section(
                EmbodiedSectionCreate(
                    name="memory",
                    authored_by="b",
                    sheaf=SheafKind.AGI_SECOND_BRAIN,
                    exact_text="source-preserving memory",
                    participants=["b"],
                    perspective_ids=["b-view"],
                )
            )
            relation = await runtime.embodied.create_relation(
                EmbodiedRelationCreate(
                    name="missing consent",
                    left_section_id=left["id"],
                    right_section_id=right["id"],
                    forward_translation={"x": "y"},
                    reverse_translation={"y": "x"},
                    preserves=[left["id"], right["id"]],
                    untranslated_residue=["open"],
                    affected_perspectives=["a-view", "b-view"],
                    consented_participant_ids=["a"],
                    reopening_conditions=["b responds"],
                )
            )
            assert relation["evaluation"]["consent_scoped"] is False
            assert relation["evaluation"]["love_admissible"] is False
            event = runtime.supernet_store.get_event(relation["integration_event_id"])
            assert not any(
                state["stage"] == "DETERMINED" for state in event["state_history"]
            )
            assert event["current_verdict"] == "OPEN"

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_loop_sensor_reads_local_halt_and_global_continuation(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            sections, _relations, field = await build_full_field(runtime)
            local_ids = [
                item["id"]
                for item in sections
                if item["sheaf"] in {kind.value for kind in LOCAL_BALL_SHEAVES}
            ]
            hair_ids = [
                item["id"]
                for item in sections
                if item["sheaf"] in {kind.value for kind in GLOBAL_HAIR_SHEAVES}
            ]
            sensor = next(
                item
                for item in sections
                if item["sheaf"] == SheafKind.BLACK_MIRROR_SENSOR.value
            )
            reading = await runtime.embodied.create_sensor_read(
                EmbodiedLoopSensorCreate(
                    name="embodied return",
                    authored_by="sensor-agent",
                    field_id=field["id"],
                    sensor_section_id=sensor["id"],
                    resolution=4,
                    visible_section_ids=local_ids,
                    returned_section_ids=hair_ids,
                )
            )
            evaluation = reading["evaluation"]
            assert evaluation["absolute_origin_observed"] is False
            assert evaluation["background_independent_reading"] is True
            assert evaluation["local_halt_reading"] is True
            assert evaluation["global_continuation_reading"] is True
            assert evaluation["current_field_coverage_complete"] is True
            assert evaluation["single_sensor_complete"] is False
            assert evaluation["unknown_hypothesis_truth_issued"] is False
            event = runtime.supernet_store.get_event(reading["integration_event_id"])
            assert any(state["stage"] == "DETERMINED" for state in event["state_history"])
            assert event["current_verdict"] == "OPEN"

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_embodied_api_and_supernet_lens(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/embodied")
        assert page.status_code == 200
        assert "Embodied Eight-Sheaf Supernet" in page.text
        created = client.post(
            "/network/embodied/sections",
            json={
                "name": "public interaction",
                "authored_by": "participant",
                "sheaf": "HUMAN_INTERACTION",
                "exact_text": "one consented physical human interaction",
                "participants": ["participant"],
                "perspective_ids": ["participant-view"],
                "consent_scope": ["public-test"],
            },
        )
        assert created.status_code == 200
        assert created.json()["sheaf"] == "HUMAN_INTERACTION"
        field = client.get("/network/embodied/field")
        assert field.status_code == 200
        assert field.json()["stats"]["sections"] == 1
        assert field.json()["resource_metrics_are_downstream"] is True
        lens = client.get("/supernet/project", params={"lens": "embodied"})
        assert lens.status_code == 200
        assert lens.json()["lens"] == "embodied"
        capabilities = client.get("/supernet/capabilities")
        assert capabilities.status_code == 200
        assert capabilities.json()["embodied_eight_sheaf_supernet"] is True
        assert capabilities.json()["physical_force_claimed"] is False
        assert capabilities.json()["emotion_inferred"] is False
        assert capabilities.json()["human_worth_scored"] is False
