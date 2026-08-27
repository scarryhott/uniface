from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_completion import create_app
from closure_supernet.completion_models import (
    CompletionExtensionCreate,
    CompletionMapComposeCreate,
    CompletionMapCreate,
    CompletionSystemCreate,
    InvariantReadingInput,
    InvariantTruthInput,
    LocalTranslationStepInput,
)
from closure_supernet.config import RuntimeConfig
from closure_supernet.runtime import ClosureSupernetRuntime


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "completion.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
    )


def step_two_system() -> CompletionSystemCreate:
    return CompletionSystemCreate(
        name="translation by two",
        authored_by="participant",
        presentations=["0", "1", "2", "3"],
        steps=[
            LocalTranslationStepInput(source="0", target="2", label="+2"),
            LocalTranslationStepInput(source="1", target="3", label="+2"),
        ],
        readings=[
            InvariantReadingInput(
                name="parity",
                values={"0": 0, "1": 1, "2": 0, "3": 1},
            )
        ],
        truths=[
            InvariantTruthInput(
                name="even class",
                values={"0": True, "1": False, "2": True, "3": False},
            )
        ],
    )


def test_local_steps_generate_exact_global_completion(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            system = await runtime.completion.create_system(step_two_system())
            evaluation = system["evaluation"]
            classes = {frozenset(item["members"]) for item in evaluation["classes"]}
            assert classes == {frozenset({"0", "2"}), frozenset({"1", "3"})}
            assert evaluation["every_identification_has_finite_local_path"] is True
            assert evaluation["no_global_jump"] is True
            assert evaluation["local_global_reading_equivalent"] is True
            assert evaluation["local_global_truth_equivalent"] is True
            assert evaluation["all_local_truths_recover_completion"] is True
            assert evaluation["readings"][0]["local_invariant"] is True
            assert evaluation["readings"][0]["global_invariant"] is True
            assert evaluation["readings"][0]["decides_completion"] is True
            assert evaluation["readings"][0]["unique_factorization"] is True
            assert evaluation["completion_closed"] is True
            assert evaluation["completion_idempotent"] is True
            event = runtime.supernet_store.get_event(system["integration_event_id"])
            assert event["current_stage"] == "RETURNED"
            assert event["current_verdict"] == "OPEN"
            determined = next(
                state for state in event["state_history"] if state["stage"] == "DETERMINED"
            )
            assert determined["rigidity_receipt"]["equivalence_assumed"] is False
            assert determined["rigidity_receipt"]["local_global_same_completion"] is True
            assert determined["determined_form"]["canonical_representative"] is None

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_generation_stages_and_finite_path_witness(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            system = await runtime.completion.create_system(
                CompletionSystemCreate(
                    name="three point chain",
                    presentations=["a", "b", "c"],
                    steps=[
                        LocalTranslationStepInput(source="a", target="b", label="ab"),
                        LocalTranslationStepInput(source="b", target="c", label="bc"),
                    ],
                )
            )
            stages = system["evaluation"]["generation_stages"]
            assert [item["index"] for item in stages] == [0, 1, 2]
            assert [item["related_ordered_pairs"] for item in stages] == [3, 7, 9]
            witness = runtime.completion.reach_witness(system["id"], "a", "c")
            assert witness["related"] is True
            assert witness["path"] == ["a", "b", "c"]
            assert witness["step_labels"] == ["ab", "bc"]
            assert witness["length"] == 2
            assert witness["finite_local_lineage"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_directed_occurrence_is_not_automatically_admitted_translation(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            system = await runtime.completion.create_system(
                CompletionSystemCreate(
                    name="unadmitted directed occurrence",
                    presentations=["human-a", "human-b"],
                    steps=[
                        LocalTranslationStepInput(
                            source="human-a",
                            target="human-b",
                            label="one-way observation",
                            admitted_for_completion=False,
                        )
                    ],
                )
            )
            assert len(system["evaluation"]["classes"]) == 2
            witness = runtime.completion.reach_witness(
                system["id"], "human-a", "human-b"
            )
            assert witness["related"] is False
            assert witness["finite_local_lineage"] is False

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_new_local_step_reopens_and_extends_completion(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            parent = await runtime.completion.create_system(step_two_system())
            child = await runtime.completion.extend_system(
                parent["id"],
                CompletionExtensionCreate(
                    authored_by="second participant",
                    added_steps=[
                        LocalTranslationStepInput(source="0", target="1", label="bridge")
                    ],
                    readings=[
                        InvariantReadingInput(
                            name="constant after bridge",
                            values={"0": "one", "1": "one", "2": "one", "3": "one"},
                        )
                    ],
                    truths=[
                        InvariantTruthInput(
                            name="whole class",
                            values={"0": True, "1": True, "2": True, "3": True},
                        )
                    ],
                ),
            )
            assert child["parent_system_id"] == parent["id"]
            assert len(child["evaluation"]["classes"]) == 1
            parent_event = runtime.supernet_store.get_event(parent["integration_event_id"])
            assert parent_event["current_stage"] == "REOPENED"
            assert parent_event["current_verdict"] == "OPEN"
            assert child["evaluation"]["readings"][0]["decides_completion"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_functorial_maps_and_composition(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            first = await runtime.completion.create_system(step_two_system())
            second = await runtime.completion.create_system(
                CompletionSystemCreate(
                    name="two class target",
                    presentations=["even", "odd"],
                    steps=[],
                )
            )
            third = await runtime.completion.create_system(
                CompletionSystemCreate(
                    name="renamed target",
                    presentations=["E", "O"],
                    steps=[],
                )
            )
            map_one = await runtime.completion.create_map(
                CompletionMapCreate(
                    source_system_id=first["id"],
                    target_system_id=second["id"],
                    mapping={"0": "even", "2": "even", "1": "odd", "3": "odd"},
                )
            )
            map_two = await runtime.completion.create_map(
                CompletionMapCreate(
                    source_system_id=second["id"],
                    target_system_id=third["id"],
                    mapping={"even": "E", "odd": "O"},
                )
            )
            composed = await runtime.completion.compose_maps(
                CompletionMapComposeCreate(
                    first_map_id=map_one["id"],
                    second_map_id=map_two["id"],
                )
            )
            assert map_one["relation_preserving"] is True
            assert map_one["map_mk_commutes"] is True
            assert composed["relation_preserving"] is True
            assert composed["mapping"] == {"0": "E", "2": "E", "1": "O", "3": "O"}
            assert composed["parent_map_ids"] == [map_one["id"], map_two["id"]]

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_completion_api_interface_and_supernet_lens(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/completion")
        assert page.status_code == 200
        assert "Local step" in page.text
        created = client.post(
            "/network/completion/systems",
            json=step_two_system().model_dump(mode="json"),
        )
        assert created.status_code == 200
        payload = created.json()
        assert len(payload["evaluation"]["classes"]) == 2
        witness = client.get(
            f"/network/completion/systems/{payload['id']}/witness",
            params={"source": "0", "target": "2"},
        )
        assert witness.status_code == 200
        assert witness.json()["path"] == ["0", "2"]
        field = client.get("/network/completion/field")
        assert field.status_code == 200
        assert field.json()["stats"]["systems"] == 1
        assert field.json()["local_global_same_completion"] is True
        lens = client.get("/supernet/project", params={"lens": "completion"})
        assert lens.status_code == 200
        assert lens.json()["lens"] == "completion"
        capabilities = client.get("/supernet/capabilities")
        assert capabilities.status_code == 200
        assert capabilities.json()["bare_local_steps_generate_completion"] is True
        assert capabilities.json()["every_completion_equality_has_finite_local_lineage"] is True
        assert capabilities.json()["determination_issues_truth"] is False
