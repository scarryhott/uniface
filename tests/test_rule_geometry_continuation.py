from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from closure_supernet.api_continuation import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.continuation_models import (
    ContinuationMapCreate,
    ContinuationSystemCreate,
)
from closure_supernet.runtime import ClosureSupernetRuntime
from closure_supernet.turing_being_models import (
    LifeActionWitness,
    LifeReactionWitness,
    TuringBeingLifeCreate,
    TuringBeingReturnCreate,
)


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "continuation.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
    )


def ball_create() -> ContinuationSystemCreate:
    return ContinuationSystemCreate(
        name="four-phase ball continuation",
        presentations=["0", "1", "2", "3"],
        step={"0": "1", "1": "2", "2": "3", "3": "0"},
        origin="0",
        step_label="ballStep",
        continuation_horizon=8,
    )


def branch_create() -> ContinuationSystemCreate:
    return ContinuationSystemCreate(
        name="two sources meet at one return",
        presentations=["a", "b", "c"],
        step={"a": "b", "b": "b", "c": "b"},
        origin="a",
        step_label="return",
        continuation_horizon=4,
    )


def test_ball_rule_and_geometry_coincide(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            system = await runtime.continuation.create_system(ball_create())
            evaluation = system["evaluation"]
            assert evaluation["step_injective"] is True
            assert evaluation["rule_le_geometry"] is True
            assert evaluation["geometry_eq_eqvgen_rule"] is True
            assert evaluation["rule_eq_geometry"] is True
            assert evaluation["rule_symmetric"] is True
            assert evaluation["finite_injective_rule_eq_geometry"] is True
            assert evaluation["geom_iff_continuations_meet"] is True
            assert evaluation["cl_continuation_constant"] is True
            assert evaluation["continuation_unique"] is True
            assert evaluation["geometry_only_pairs"] == []

            rule = runtime.continuation.rule_witness(system["id"], "0", "3")
            assert rule["related"] is True
            assert rule["iterate"] == 3
            assert rule["path"] == ["0", "1", "2", "3"]

            geometry = runtime.continuation.geometry_witness(
                system["id"], "0", "3"
            )
            assert geometry["related"] is True
            assert geometry["continuations_meet"] is True
            assert geometry["forward_rule_source_to_target"] is True

            event = runtime.supernet_store.get_event(system["integration_event_id"])
            assert event["current_stage"] == "RETURNED"
            assert event["current_verdict"] == "OPEN"

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_geometry_keeps_meeting_without_fabricating_forward_rule(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            system = await runtime.continuation.create_system(branch_create())
            evaluation = system["evaluation"]
            assert evaluation["rule_le_geometry"] is True
            assert evaluation["rule_eq_geometry"] is False
            assert evaluation["rule_symmetric"] is False
            assert evaluation["rule_eq_geometry_iff_rule_symmetric"] is True
            assert evaluation["geometry_only_pair_count"] > 0
            assert evaluation["geometry_does_not_supply_missing_rule_witness"] is True

            rule = runtime.continuation.rule_witness(system["id"], "a", "c")
            assert rule["related"] is False
            assert rule["path"] == []

            geometry = runtime.continuation.geometry_witness(
                system["id"], "a", "c"
            )
            assert geometry["related"] is True
            assert geometry["meeting_value"] == "b"
            assert geometry["source_iterate"] == 1
            assert geometry["target_iterate"] == 1
            assert geometry["forward_rule_source_to_target"] is False
            assert geometry["symmetry_added_by_geometry"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_translation_morphism_carries_rule_geometry_and_continuation(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            source = await runtime.continuation.create_system(ball_create())
            target = await runtime.continuation.create_system(
                ContinuationSystemCreate(
                    name="two-phase quotient",
                    presentations=["0", "1"],
                    step={"0": "1", "1": "0"},
                    origin="0",
                    step_label="phaseStep",
                    continuation_horizon=8,
                )
            )
            mapping = await runtime.continuation.create_map(
                ContinuationMapCreate(
                    source_system_id=source["id"],
                    target_system_id=target["id"],
                    mapping={"0": "0", "1": "1", "2": "0", "3": "1"},
                )
            )
            evaluation = mapping["evaluation"]
            assert evaluation["intertwines_translation"] is True
            assert evaluation["morphism_rule"] is True
            assert evaluation["morphism_geom"] is True
            assert evaluation["continuation_natural"] is True
            assert evaluation["completion_map_mk_commutes"] is True
            assert evaluation["geometry_does_not_fabricate_rule_witness"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_turing_being_truth_must_precede_real_world_continuation(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            life = await runtime.turing_being.create_life_event(
                TuringBeingLifeCreate(
                    name="life before continuation",
                    global_hair_executor="global hair zero",
                    local_ball_reactor="local ball infinity",
                    action=LifeActionWitness(
                        exact_occurrence="executor opens the reactor"
                    ),
                )
            )
            linked = ContinuationSystemCreate(
                name="returned life continuation",
                presentations=["hair0", "ball", "hair0+"],
                step={"hair0": "ball", "ball": "hair0+", "hair0+": "hair0+"},
                origin="hair0",
                turing_being_life_event_id=life["id"],
            )
            with pytest.raises(ValueError):
                await runtime.continuation.create_system(linked)

            completed = await runtime.turing_being.complete_return(
                life["id"],
                TuringBeingReturnCreate(
                    reaction=LifeReactionWitness(
                        exact_occurrence="reactor returns into global continuation"
                    )
                ),
            )
            assert completed["translational_truth_receipt"]["complete"] is True
            system = await runtime.continuation.create_system(linked)
            assert system["turing_being_life_event_id"] == life["id"]
            assert system["evaluation"]["real_world_step_admissibility"] == (
                "TRANSLATIONAL_TRUTH_PRIOR"
            )
            assert system["metadata"]["turing_being_translational_truth_prior"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_continuation_api_and_supernet_lens(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/continuation")
        assert page.status_code == 200
        assert "Rule and geometry" in page.text

        created = client.post(
            "/network/continuations/systems",
            json={
                "name": "API branching continuation",
                "presentations": ["a", "b", "c"],
                "step": {"a": "b", "b": "b", "c": "b"},
                "origin": "a",
                "continuation_horizon": 5,
            },
        )
        assert created.status_code == 200, created.text
        system = created.json()
        assert system["evaluation"]["rule_eq_geometry"] is False

        rule = client.get(
            f"/network/continuations/systems/{system['id']}/rule",
            params={"source": "a", "target": "c"},
        )
        assert rule.status_code == 200
        assert rule.json()["related"] is False

        geometry = client.get(
            f"/network/continuations/systems/{system['id']}/geometry",
            params={"source": "a", "target": "c"},
        )
        assert geometry.status_code == 200
        assert geometry.json()["related"] is True
        assert geometry.json()["meeting_value"] == "b"

        continuation = client.get(
            f"/network/continuations/systems/{system['id']}/continuation",
            params={"steps": 4},
        )
        assert continuation.status_code == 200
        assert continuation.json()["unique"] is True
        assert continuation.json()["closure_constant"] is True

        field = client.get("/network/continuations/field")
        assert field.status_code == 200
        payload = field.json()
        assert payload["stats"]["systems"] == 1
        assert payload["stats"]["rule_strictly_inside_geometry"] == 1
        assert payload["canonical_examples"]["ball"]["rule_eq_geometry"] is True
        assert payload["geometry_does_not_fabricate_rule_witness"] is True

        lens = client.get("/supernet/project", params={"lens": "continuation"})
        assert lens.status_code == 200, lens.text
        assert lens.json()["lens"] == "continuation"
        assert lens.json()["stats"]["visible_events"] >= 1

        capabilities = client.get("/supernet/capabilities")
        assert capabilities.status_code == 200
        caps = capabilities.json()
        assert caps["natural_continuation_available"] is True
        assert caps["rule_le_geometry"] is True
        assert caps["geometry_does_not_fabricate_rule_witness"] is True
        assert caps["determination_issues_truth"] is False
