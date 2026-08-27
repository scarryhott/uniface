from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_handed import create_app
from closure_supernet.completion_models import InvariantReadingInput
from closure_supernet.config import RuntimeConfig
from closure_supernet.handed_models import HandedLifeSystemCreate
from closure_supernet.runtime import ClosureSupernetRuntime
from closure_supernet.unify_closure_models import (
    ClosurePresentationCreate,
    ReturnClosureCreate,
    ReturnClosureMapCreate,
    TwoReturnClosureCreate,
)


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "unify-closure.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
    )


def plus_step(modulus: int, amount: int = 1) -> dict[str, str]:
    return {
        str(index): str((index + amount) % modulus)
        for index in range(modulus)
    }


def life_carrier() -> list[str]:
    return [f"{hand}:{phase}" for hand in ("LEFT", "RIGHT") for phase in range(4)]


def life_step(hand_flip: bool, phase_delta: int) -> dict[str, str]:
    result: dict[str, str] = {}
    for hand in ("LEFT", "RIGHT"):
        target_hand = (
            "RIGHT" if hand == "LEFT" else "LEFT"
        ) if hand_flip else hand
        for phase in range(4):
            result[f"{hand}:{phase}"] = f"{target_hand}:{(phase + phase_delta) % 4}"
    return result


def test_canonical_hair_hand_phase_and_joint_closure() -> None:
    runtime = ClosureSupernetRuntime(
        RuntimeConfig(
            database_path=Path("/tmp/nrrf802-canonical.db"),
            inbox_dir=Path("/tmp/nrrf802-canonical-inbox"),
            backup_dir=Path("/tmp/nrrf802-canonical-backups"),
            autonomy_enabled=False,
            environment="test",
        )
    )
    try:
        instances = runtime.unify_closure.projection()["canonical_instances"]
        assert instances["closure_defined_once"] is True
        assert instances["unified_cardinalities"] == {
            "hair": 1,
            "hand": 2,
            "phase": 4,
        }
        assert instances["hair_of_ball"]["hair_isClosure"] is True
        assert instances["hand_of_ballReturn"]["hand_isClosure"] is True
        assert instances["phase_of_selfLimit"]["phase_isClosure"] is True
        assert instances["closure2_life"]["cardinality"] == 1
        assert instances["closure2_life"]["closure2_life_subsingleton"] is True
        assert instances["closure2_life"]["unify_closure"] is True
        assert instances["closure2_life"]["unify_closure_symm"] is True
        assert instances["functoriality"]["map_id"] is True
        assert instances["functoriality"]["map_comp"] is True
    finally:
        runtime.close()


def test_return_closure_unique_lift_and_isclosure_witness(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            system = await runtime.unify_closure.create_return_closure(
                ReturnClosureCreate(
                    name="parity closure",
                    carrier=["0", "1", "2", "3"],
                    step=plus_step(4, 2),
                    step_label="+2 return",
                    readings=[
                        InvariantReadingInput(
                            name="parity",
                            values={"0": 0, "1": 1, "2": 0, "3": 1},
                        )
                    ],
                )
            )
            assert system["metadata"]["closure_kernel"] == "NRRF802"
            assert system["metadata"]["closure_kind"] == "SINGLE_RETURN"
            assert len(system["evaluation"]["classes"]) == 2
            reading = system["evaluation"]["readings"][0]
            assert reading["local_invariant"] is True
            assert reading["factors_through_completion"] is True
            assert reading["unique_factorization"] is True
            assert reading["decides_completion"] is True

            witness = await runtime.unify_closure.create_presentation_witness(
                ClosurePresentationCreate(
                    system_id=system["id"],
                    projection={"0": "even", "2": "even", "1": "odd", "3": "odd"},
                )
            )
            evaluation = witness["evaluation"]
            assert evaluation["return_invariant"] is True
            assert evaluation["projection_fibres_exactly_closure_classes"] is True
            assert evaluation["is_closure"] is True
            assert evaluation["closure_unique_iso_commutes_with_closure_maps"] is True
            assert set(evaluation["closure_unique_iso"].values()) == {"even", "odd"}

            source_event = runtime.supernet_store.get_event(system["source_event_id"])
            assert source_event["current_stage"] == "RETURNED"
            assert source_event["current_verdict"] == "OPEN"

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_functorial_return_map_intertwines_and_composes_with_closure(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            source = await runtime.unify_closure.create_return_closure(
                ReturnClosureCreate(
                    name="four cycle",
                    carrier=["0", "1", "2", "3"],
                    step=plus_step(4),
                )
            )
            target = await runtime.unify_closure.create_return_closure(
                ReturnClosureCreate(
                    name="two cycle",
                    carrier=["0", "1"],
                    step=plus_step(2),
                )
            )
            closure_map = await runtime.unify_closure.create_map(
                ReturnClosureMapCreate(
                    source_system_id=source["id"],
                    target_system_id=target["id"],
                    mapping={"0": "0", "1": "1", "2": "0", "3": "1"},
                )
            )
            assert closure_map["metadata"]["intertwines_return"] is True
            assert closure_map["metadata"]["map_cl"] is True
            assert closure_map["relation_preserving"] is True
            assert closure_map["map_mk_commutes"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_two_commuting_returns_unify_life_to_one_closure(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            system = await runtime.unify_closure.create_two_return_closure(
                TwoReturnClosureCreate(
                    name="life under both returns",
                    carrier=life_carrier(),
                    first_step=life_step(False, 1),
                    second_step=life_step(True, -1),
                    first_label="ballReturn",
                    second_label="hairReturn",
                )
            )
            assert system["metadata"]["closure_kind"] == "TWO_RETURN"
            assert system["metadata"]["returns_commute"] is True
            assert len(system["evaluation"]["classes"]) == 1
            assert system["evaluation"]["completion_idempotent"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_handed_life_now_exhibits_the_unified_closure_instances(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            system = await runtime.handed_life.create_system(
                HandedLifeSystemCreate(name="unified handed life")
            )
            evaluation = system["evaluation"]
            assert evaluation["closure_defined_once"] is True
            assert evaluation["hair_isClosure"] is True
            assert evaluation["hand_isClosure"] is True
            assert evaluation["phase_isClosure"] is True
            assert evaluation["unified_cardinalities"] == {
                "hair": 1,
                "hand": 2,
                "phase": 4,
            }
            assert evaluation["closure2_life_subsingleton"] is True
            assert evaluation["unify_closure"] is True
            event = runtime.supernet_store.get_event(system["integration_event_id"])
            determined = next(
                item for item in event["state_history"] if item["stage"] == "DETERMINED"
            )
            assert determined["rigidity_receipt"]["closure_defined_once"] is True
            assert determined["rigidity_receipt"]["closure2_life_subsingleton"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_unified_closure_api_uses_the_completion_field(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/unify-closure")
        assert page.status_code == 200
        assert "One closure, once" in page.text

        created = client.post(
            "/network/completion/closures",
            json={
                "name": "API return closure",
                "carrier": ["0", "1", "2", "3"],
                "step": plus_step(4, 2),
                "readings": [
                    {
                        "name": "parity",
                        "values": {"0": 0, "1": 1, "2": 0, "3": 1},
                    }
                ],
            },
        )
        assert created.status_code == 200, created.text
        payload = created.json()
        assert payload["metadata"]["closure_kernel"] == "NRRF802"
        assert len(payload["evaluation"]["classes"]) == 2

        instances = client.get("/network/completion/closure-instances")
        assert instances.status_code == 200
        assert instances.json()["unified_cardinalities"] == {
            "hair": 1,
            "hand": 2,
            "phase": 4,
        }

        field = client.get("/network/completion/unified-field")
        assert field.status_code == 200
        field_payload = field.json()
        assert field_payload["stats"]["systems"] == 1
        assert field_payload["uses_existing_completion_store"] is True
        assert field_payload["parallel_closure_runtime_created"] is False

        completion_field = client.get("/network/completion/field")
        assert completion_field.status_code == 200
        assert completion_field.json()["stats"]["systems"] == 1

        capabilities = client.get("/supernet/capabilities")
        assert capabilities.status_code == 200
        assert capabilities.json()["one_return_closure_construction"] is True
        assert capabilities.json()["parallel_closure_runtime_created"] is False
        assert capabilities.json()["determination_issues_truth"] is False
