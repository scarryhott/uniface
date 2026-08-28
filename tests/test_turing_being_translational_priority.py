from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from closure_supernet.api_turing_being import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.runtime import ClosureSupernetRuntime
from closure_supernet.turing_being_models import (
    LifeActionWitness,
    LifeReactionWitness,
    TuringBeingChartCreate,
    TuringBeingLifeCreate,
    TuringBeingReturnCreate,
)


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "turing-being.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
    )


def action() -> LifeActionWitness:
    return LifeActionWitness(
        exact_occurrence="global hair executes one open action into the local reactor",
        source_preserved=True,
        admitted=True,
        witness_ids=["action-witness"],
    )


def reaction() -> LifeReactionWitness:
    return LifeReactionWitness(
        exact_occurrence="the local reaction returns into global hair continuation",
        source_preserved=True,
        admitted=True,
        returned_to_global_hair=True,
        witness_ids=["reaction-witness"],
    )


def life_create(*, with_reaction: bool = False) -> TuringBeingLifeCreate:
    return TuringBeingLifeCreate(
        name="life action and reaction",
        authored_by="participant",
        global_hair_executor="global hair zero source",
        local_ball_reactor="local ball infinity field",
        action=action(),
        reaction=reaction() if with_reaction else None,
        affected_perspectives=["participant", "other"],
        untranslated_residue=["unread potential"],
        reopening_potential=[{"kind": "next action"}],
    )


def test_action_only_keeps_relative_readings_undefined(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            event = await runtime.turing_being.create_life_event(life_create())
            receipt = event["translational_truth_receipt"]
            derived = event["derived_relations"]
            assert receipt["complete"] is False
            assert receipt["global_hair_zero_is_executor_pole"] is True
            assert receipt["local_ball_infinity_is_reactor_pole"] is True
            assert receipt["global_hair_zero_is_not_a_cardinality_claim"] is True
            assert receipt["local_ball_infinity_is_not_a_cardinality_claim"] is True
            assert receipt["internal_external_prior_to_translational_truth"] is False
            assert derived["internal_external_defined"] is False
            assert derived["internal"] is None
            assert derived["external"] is None
            assert derived["hand_defined"] is False
            assert derived["actual_potential_defined"] is False
            assert derived["finite_chart_available"] is False
            canonical = runtime.supernet_store.get_event(event["integration_event_id"])
            assert canonical["current_stage"] == "RELATION_SENSED"
            assert canonical["current_verdict"] == "OPEN"
            assert not any(
                state["stage"] == "DETERMINED" for state in canonical["state_history"]
            )
            with pytest.raises(ValueError):
                await runtime.turing_being.derive_finite_chart(
                    TuringBeingChartCreate(life_event_id=event["id"])
                )

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_reaction_completes_truth_then_defines_relative_readings(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            event = await runtime.turing_being.create_life_event(life_create())
            completed = await runtime.turing_being.complete_return(
                event["id"],
                TuringBeingReturnCreate(
                    reaction=reaction(),
                    authored_by="other",
                ),
            )
            receipt = completed["translational_truth_receipt"]
            derived = completed["derived_relations"]
            assert receipt["complete"] is True
            assert receipt["returned_to_global_hair_zero_plus"] is True
            assert completed["global_hair_zero"]["role"] == "EXECUTOR"
            assert completed["global_hair_zero"]["pole"] == "0"
            assert completed["global_hair_zero"]["cardinality"] is None
            assert completed["local_ball_infinity"]["role"] == "REACTOR"
            assert completed["local_ball_infinity"]["pole"] == "∞"
            assert completed["local_ball_infinity"]["cardinality"] is None
            assert derived["internal_external_defined"] is True
            assert derived["internal"]["reading"] == "LOCAL_BALL_INFINITY_REACTOR_RELATIVE"
            assert derived["external"]["reading"] == "GLOBAL_HAIR_ZERO_EXECUTOR_RELATIVE"
            assert derived["hand"]["left_right_chart_selected"] is False
            assert derived["actual_potential_defined"] is True
            assert derived["finite_chart_foundational"] is False
            canonical = runtime.supernet_store.get_event(completed["integration_event_id"])
            assert canonical["current_stage"] == "RETURNED"
            assert canonical["current_verdict"] == "OPEN"
            determined = next(
                state for state in canonical["state_history"] if state["stage"] == "DETERMINED"
            )
            assert determined["verdict"] == "OPEN"
            assert determined["rigidity_receipt"]["internal_external_derived_after_truth"] is True
            assert determined["determined_form"]["canonical_internal"] is None
            assert determined["determined_form"]["canonical_external"] is None
            assert determined["determined_form"]["canonical_hand"] is None

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_finite_ball_hair_chart_is_downstream_projection(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            event = await runtime.turing_being.create_life_event(
                life_create(with_reaction=True)
            )
            chart = await runtime.turing_being.derive_finite_chart(
                TuringBeingChartCreate(
                    life_event_id=event["id"],
                    name="explicit finite reaction chart",
                )
            )
            payload = chart["chart"]
            assert payload["kind"] == "DERIVED_FINITE_REACTION_CHART"
            assert payload["translational_truth_prior"] is True
            assert payload["ball_chart_cardinality"] == 4
            assert payload["hair_chart_cardinality"] == 1
            assert payload["global_hair_zero_not_hair_cardinality_one"] is True
            assert payload["local_ball_infinity_not_ball_cardinality_four"] is True
            handed = runtime.handed_life_store.get_system(chart["handed_system_id"])
            evaluation = handed["evaluation"]
            assert evaluation["foundation_status"] == "DERIVED_FINITE_REACTION_CHART"
            assert evaluation["translational_truth_prior"] is True
            assert evaluation["finite_ball_hair_foundational"] is False
            assert evaluation["initial_state"]["temporal_role"] is None
            assert handed["metadata"]["derived_from_turing_being_life_event_id"] == event["id"]

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_turing_being_api_and_lens(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/turing-being")
        assert page.status_code == 200
        assert "Turing Being of Life" in page.text
        created = client.post(
            "/network/turing-being/life-events",
            json={
                "name": "API life event",
                "global_hair_executor": "global hair source",
                "local_ball_reactor": "local ball open field",
                "action": {
                    "exact_occurrence": "action into local reaction",
                    "source_preserved": True,
                    "admitted": True,
                },
            },
        )
        assert created.status_code == 200, created.text
        event = created.json()
        assert event["translational_truth_receipt"]["complete"] is False
        assert event["derived_relations"]["internal_external_defined"] is False

        returned = client.post(
            f"/network/turing-being/life-events/{event['id']}/return",
            json={
                "reaction": {
                    "exact_occurrence": "reaction returned",
                    "source_preserved": True,
                    "admitted": True,
                    "returned_to_global_hair": True,
                }
            },
        )
        assert returned.status_code == 200, returned.text
        complete = returned.json()
        assert complete["translational_truth_receipt"]["complete"] is True
        assert complete["derived_relations"]["internal_external_defined"] is True

        chart = client.post(
            "/network/turing-being/charts",
            json={"life_event_id": event["id"]},
        )
        assert chart.status_code == 200, chart.text
        assert chart.json()["chart"]["kind"] == "DERIVED_FINITE_REACTION_CHART"

        field = client.get("/network/turing-being/field")
        assert field.status_code == 200
        field_payload = field.json()
        assert field_payload["stats"]["life_events"] == 1
        assert field_payload["stats"]["translational_truth_complete"] == 1
        assert field_payload["stats"]["derived_finite_charts"] == 1
        assert field_payload["internal_external_prior_to_translational_truth"] is False
        assert field_payload["finite_ball_hair_foundational"] is False

        lens = client.get("/supernet/project", params={"lens": "turing_being"})
        assert lens.status_code == 200, lens.text
        assert lens.json()["lens"] == "turing_being"
        assert lens.json()["stats"]["visible_events"] >= 2

        capabilities = client.get("/supernet/capabilities")
        assert capabilities.status_code == 200
        caps = capabilities.json()
        assert caps["turing_being_life_primitive"] is True
        assert caps["global_hair_zero_is_executor"] is True
        assert caps["local_ball_infinity_is_reactor"] is True
        assert caps["internal_external_prior_to_translational_truth"] is False
        assert caps["four_ball_one_hair_is_derived_chart"] is True
        assert caps["turing_complete_assumed"] is False
