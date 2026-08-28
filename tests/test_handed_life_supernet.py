from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_handed import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.handed_models import (
    Hand,
    HandedLifeSystemCreate,
    HandedMotionCreate,
    HumanRelationCreate,
    MotionKind,
)
from closure_supernet.runtime import ClosureSupernetRuntime


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "handed.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
    )


def test_four_ball_one_hair_completion_and_left_gate(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            system = await runtime.handed_life.create_system(
                HandedLifeSystemCreate(
                    name="left-handed chart gate",
                    initial_hand=Hand.LEFT,
                    initial_ball_phase=0,
                )
            )
            evaluation = system["evaluation"]
            assert evaluation["ball_card"] == 4
            assert evaluation["ball_step_period"] == 4
            assert evaluation["ball_step_iterate_four_is_identity"] is True
            assert evaluation["ball_step_ne_identity_below_four"] is True
            assert evaluation["ball_return_never_touches_hand"] is True
            assert evaluation["hair_card"] == 1
            assert evaluation["hair_equiv_punit"] is True
            assert evaluation["four_ball_one_hair"] is True
            assert evaluation["completion_every_identification_has_finite_path"] is True
            assert evaluation["completion_no_global_jump"] is True
            assert evaluation["completion_idempotent"] is True
            assert evaluation["commuting_maps"]["commuting_bijections"] == 4
            assert evaluation["commuting_maps"]["all_are_ball_translations"] is True
            assert evaluation["self_limit_same_ball_phase"] is True
            assert evaluation["self_limit_inverts_hand"] is True
            assert evaluation["self_limit_involutive"] is True
            assert evaluation["self_limit_order_exact"] == 2
            assert evaluation["left_gate_visits_each_ball_sheaf_once"] is True
            assert evaluation["left_gate_alternates_hands"] is True
            assert evaluation["left_gate_alternates_potential_actual"] is False
            assert evaluation["potential_actual_requires_translational_truth"] is True
            assert evaluation["left_gate_closes_after_four"] is True
            assert evaluation["left_gate_same_hair_throughout"] is True
            assert evaluation["initial_state"]["temporal_role"] is None
            assert evaluation["initial_state"]["internal_external_defined"] is False
            assert evaluation["foundation_status"] == "UNBOUND_FINITE_CHART"
            assert evaluation["finite_ball_hair_foundational"] is False
            assert evaluation["global_hair_zero_not_hair_cardinality_one"] is True
            assert evaluation["local_ball_infinity_not_ball_cardinality_four"] is True
            event = runtime.supernet_store.get_event(system["integration_event_id"])
            assert event["current_stage"] == "RETURNED"
            assert event["current_verdict"] == "OPEN"
            determined = next(
                state for state in event["state_history"] if state["stage"] == "DETERMINED"
            )
            assert determined["verdict"] == "OPEN"
            assert determined["rigidity_receipt"]["hair_card"] == 1
            assert determined["rigidity_receipt"]["biological_interpretation_selected"] is False

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_ball_hair_and_self_limit_motion_traces(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            system = await runtime.handed_life.create_system(
                HandedLifeSystemCreate(name="motion system", initial_ball_phase=2)
            )
            ball = await runtime.handed_life.create_motion(
                HandedMotionCreate(
                    system_id=system["id"],
                    motion=MotionKind.BALL_RETURN,
                    steps=5,
                )
            )
            assert ball["evaluation"]["ball_return_hand_preserved"] is True
            assert ball["evaluation"]["end"]["ball_phase"] == 3
            assert ball["evaluation"]["end"]["hand"] == "LEFT"
            assert ball["evaluation"]["end"]["temporal_role"] is None

            hair = await runtime.handed_life.create_motion(
                HandedMotionCreate(
                    system_id=system["id"],
                    motion=MotionKind.HAIR_RETURN,
                    steps=3,
                )
            )
            assert hair["evaluation"]["hair_gate_iff_odd"] is True
            assert hair["evaluation"]["end"]["hand"] == "RIGHT"
            assert hair["evaluation"]["same_hair_throughout"] is True

            self_limit = await runtime.handed_life.create_motion(
                HandedMotionCreate(
                    system_id=system["id"],
                    motion=MotionKind.SELF_LIMIT,
                    steps=2,
                )
            )
            assert self_limit["evaluation"]["self_limit_fixed_ball_phase"] is True
            assert self_limit["evaluation"]["self_limit_gate_iff_odd"] is True
            assert self_limit["evaluation"]["closed_full_state"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_human_relation_ball_return_hair_gate_and_shift_invariance(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            away = await runtime.handed_life.create_human_relation(
                HumanRelationCreate(
                    name="away from gate",
                    source_participant="u",
                    target_participant="v",
                    source_standing=0,
                    target_standing=1,
                    after_source_standing=0,
                    after_target_standing=2,
                    common_shift=19,
                )
            )
            e = away["evaluation"]
            assert e["nothing_absolute_read"] is True
            assert e["common_shift_invariant"] is True
            assert e["reverse_hands_are_inverse"] is True
            assert e["reverse_ball_phases_are_inverse"] is True
            assert e["same_hair_both_directions"] is True
            assert e["transition_class"] == "BALL_RETURN"
            assert e["one_act_away_from_gate_is_ball_return"] is True
            assert e["four_acts_ball_blind"] is True
            assert e["four_acts_relation_changed_by_four"] is True
            assert e["forward_state"]["temporal_role"] is None

            gate = await runtime.handed_life.create_human_relation(
                HumanRelationCreate(
                    name="equal-standing gate",
                    source_participant="u",
                    target_participant="v",
                    source_standing=0,
                    target_standing=0,
                    gate_hand=Hand.LEFT,
                    after_source_standing=1,
                    after_target_standing=0,
                )
            )
            g = gate["evaluation"]
            assert g["forward_state"]["hand"] == "LEFT"
            assert g["after"]["state"]["hand"] == "RIGHT"
            assert g["after"]["state"]["ball_phase"] == 3
            assert g["transition_class"] == "HAIR_RETURN"
            assert g["one_act_at_gate_is_hair_return"] is True
            assert g["human_law_claimed"] is False
            for record in (away, gate):
                event = runtime.supernet_store.get_event(record["integration_event_id"])
                assert event["current_verdict"] == "OPEN"

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_handed_life_api_interface_and_supernet_lens(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/handed-life")
        assert page.status_code == 200
        assert "Handed life temporal closure" in page.text

        system = client.post(
            "/network/handed-life/systems",
            json={
                "name": "API gate",
                "authored_by": "participant",
                "initial_hand": "LEFT",
                "initial_ball_phase": 1,
            },
        )
        assert system.status_code == 200, system.text
        system_payload = system.json()
        assert system_payload["evaluation"]["four_ball_one_hair"] is True
        assert system_payload["evaluation"]["finite_ball_hair_foundational"] is False

        trace = client.post(
            "/network/handed-life/traces",
            json={
                "system_id": system_payload["id"],
                "motion": "HAIR_RETURN",
                "steps": 1,
            },
        )
        assert trace.status_code == 200, trace.text
        assert trace.json()["evaluation"]["end"]["hand"] == "RIGHT"

        relation = client.post(
            "/network/handed-life/human-relations",
            json={
                "name": "API relation",
                "source_participant": "a",
                "target_participant": "b",
                "source_standing": 0,
                "target_standing": 1,
            },
        )
        assert relation.status_code == 200, relation.text
        assert relation.json()["evaluation"]["common_shift_invariant"] is True

        field = client.get("/network/handed-life/field")
        assert field.status_code == 200
        assert field.json()["stats"]["systems"] == 1
        assert field.json()["stats"]["records"] == 2
        assert field.json()["biological_claimed"] is False

        lens = client.get("/supernet/project", params={"lens": "handed"})
        assert lens.status_code == 200, lens.text
        assert lens.json()["lens"] == "handed"
        assert lens.json()["stats"]["visible_events"] >= 3

        capabilities = client.get("/supernet/capabilities")
        assert capabilities.status_code == 200
        assert capabilities.json()["handed_life_ball_sheaves"] == 4
        assert capabilities.json()["handed_life_hair_sheaves"] == 1
        assert capabilities.json()["biological_life_claimed"] is False
