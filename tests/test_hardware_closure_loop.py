from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from closure_supernet.api_hardware import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.hardware_models import (
    HardwareConstraintCreate,
    HardwareConstraintDecisionCreate,
    HardwareConstraintExecutionCreate,
    HardwareConstraintSimulationCreate,
    HardwareConstraintSynthesisCreate,
    HardwareDeviceCreate,
)
from closure_supernet.living_models import ParticipantCreate
from closure_supernet.models import OccurrenceCreate, Verdict
from closure_supernet.runtime import ClosureSupernetRuntime


def make_runtime(tmp_path: Path) -> ClosureSupernetRuntime:
    return ClosureSupernetRuntime(
        RuntimeConfig(
            database_path=tmp_path / "hardware.db",
            inbox_dir=tmp_path / "inbox",
            backup_dir=tmp_path / "backups",
            autonomy_enabled=False,
            environment="test",
        )
    )


def test_two_humans_one_agent_optical_loop_reintegrates(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario() -> None:
            person_a = runtime.living.create_participant(
                ParticipantCreate(display_name="Person A")
            )
            person_b = runtime.living.create_participant(
                ParticipantCreate(display_name="Person B")
            )
            agent = runtime.living.create_participant(
                ParticipantCreate(display_name="Closure AI", metadata={"agent": True})
            )
            source = await runtime.ingest(
                OccurrenceCreate(
                    exact_text=(
                        "Black Mirror light metavector 0-inf path ellipse mirror: "
                        "select one temporary bounded return experiment."
                    ),
                    source_id="hardware-test",
                )
            )
            device = await runtime.hardware.register_device(
                HardwareDeviceCreate(
                    name="Tabletop Ellipse Twin",
                    exact_description=(
                        "A deterministic low-energy optical ellipse device twin with "
                        "phase, polarization and intensity channels."
                    ),
                    created_by=person_a["id"],
                    minimum_approvals=2,
                    capabilities=[
                        "source-reversible phase selection",
                        "bounded sensor return",
                    ],
                )
            )
            assert device["kind"] == "SIMULATED_OPTICAL_ELLIPSE"
            assert runtime.hardware.capabilities()["direct_physical_actuation"] is False

            constraint = await runtime.hardware.synthesize_constraint(
                HardwareConstraintSynthesisCreate(
                    device_id=device["id"],
                    created_by=person_a["id"],
                    exact_intent=(
                        "Translate the three participants' current relation into one "
                        "temporary optical return constraint."
                    ),
                    source_occurrence_ids=[source["id"]],
                    participant_ids=[person_a["id"], person_b["id"]],
                    agent_ids=[agent["id"]],
                    affected_perspectives=["person-a", "person-b", "closure-ai"],
                    duration_seconds=0.5,
                    expected_return={"target_intensity": 0.5},
                )
            )
            assert constraint["current_state"] == "PROPOSED"
            assert constraint["current_verdict"] == "OPEN"
            assert constraint["translation_id"]
            canonical = runtime.translation_store.get_translation(
                constraint["translation_id"]
            )
            assert canonical["relation_type"] == "TEMPORARY_HARDWARE_CONSTRAINT"
            assert canonical["current_verdict"] == "OPEN"

            with pytest.raises(ValueError):
                await runtime.hardware.execute_constraint(
                    constraint["id"],
                    HardwareConstraintExecutionCreate(requested_by=person_a["id"]),
                )

            twin = runtime.hardware.simulate_constraint(
                constraint["id"],
                HardwareConstraintSimulationCreate(requested_by=agent["id"]),
            )
            assert twin["safe"] is True
            assert twin["output_reading"]["simulation_only"] is True
            assert "return_fidelity" in twin["metrics"]

            one_approval = runtime.hardware.decide_constraint(
                constraint["id"],
                HardwareConstraintDecisionCreate(
                    verdict=Verdict.TRUE,
                    reason="Person A admits the bounded twin-tested proposal.",
                    decided_by=person_a["id"],
                ),
            )
            assert one_approval["current_state"] == "SIMULATED"

            admitted = runtime.hardware.decide_constraint(
                constraint["id"],
                HardwareConstraintDecisionCreate(
                    verdict=Verdict.TRUE,
                    reason="Person B independently admits the same temporary scope.",
                    decided_by=person_b["id"],
                ),
            )
            assert admitted["current_state"] == "ADMITTED"
            assert admitted["current_verdict"] == "TRUE"

            actuation = await runtime.hardware.execute_constraint(
                constraint["id"],
                HardwareConstraintExecutionCreate(requested_by=person_a["id"]),
            )
            assert actuation["mode"] == "SIMULATED_TWIN"
            assert actuation["return_id"]
            hardware_return = runtime.hardware_store.get_return(
                actuation["return_id"]
            )
            assert hardware_return["reintegration_status"] == "PENDING"
            assert hardware_return["evidence_status"] == "SIMULATED_UNDER_ASSUMPTIONS"

            reintegrated = await runtime.hardware.reintegrate_pending(16)
            assert reintegrated == 1
            hardware_return = runtime.hardware_store.get_return(
                actuation["return_id"]
            )
            assert hardware_return["reintegration_status"] == "REINTEGRATED_OPEN"
            return_translation = runtime.translation_store.get_translation(
                hardware_return["translation_id"]
            )
            assert return_translation["relation_type"] == "BLACK_MIRROR_HARDWARE_RETURN"
            assert return_translation["current_verdict"] == "OPEN"
            assert return_translation["successor_potential"]

            field = runtime.hardware.projection()
            assert field["stats"]["devices"] == 1
            assert field["stats"]["actuations"] == 1
            assert field["stats"]["returns"] == 1
            assert field["simulation_only"] is True
            assert field["direct_physical_actuation"] is False
            assert f"hardware_return:{hardware_return['id']}" in field[
                "source_reverse_index"
            ]

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_constraint_outside_envelope_is_rejected(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario() -> None:
            participant = runtime.living.create_participant(
                ParticipantCreate(display_name="Bounded Participant")
            )
            source = await runtime.ingest(
                OccurrenceCreate(exact_text="A bounded optical source", source_id="test")
            )
            device = await runtime.hardware.register_device(
                HardwareDeviceCreate(
                    name="Bounded Twin",
                    exact_description="Simulation-only bounded ellipse twin",
                    created_by=participant["id"],
                )
            )
            with pytest.raises(ValueError, match="outside safety envelope"):
                await runtime.hardware.create_constraint(
                    HardwareConstraintCreate(
                        device_id=device["id"],
                        created_by=participant["id"],
                        exact_intent="Attempt an invalid intensity command",
                        source_occurrence_ids=[source["id"]],
                        selected_metavector=[0.0, 0.0, 0.0, 1.0],
                        control_values={
                            "phase_x": 0.0,
                            "phase_y": 0.0,
                            "polarization": 0.0,
                            "intensity": 2.0,
                        },
                        duration_seconds=0.5,
                    )
                )

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_autonomous_cycle_reintegrates_pending_hardware_return(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario() -> None:
            participant = runtime.living.create_participant(
                ParticipantCreate(display_name="Cycle Participant")
            )
            source = await runtime.ingest(
                OccurrenceCreate(exact_text="Cycle source", source_id="cycle-test")
            )
            device = await runtime.hardware.register_device(
                HardwareDeviceCreate(
                    name="Cycle Twin",
                    exact_description="Cycle-integrated simulated optical twin",
                    created_by=participant["id"],
                )
            )
            constraint = await runtime.hardware.synthesize_constraint(
                HardwareConstraintSynthesisCreate(
                    device_id=device["id"],
                    created_by=participant["id"],
                    exact_intent="Run one autonomous hardware reintegration cycle",
                    source_occurrence_ids=[source["id"]],
                    participant_ids=[participant["id"]],
                )
            )
            runtime.hardware.simulate_constraint(
                constraint["id"],
                HardwareConstraintSimulationCreate(requested_by=participant["id"]),
            )
            runtime.hardware.decide_constraint(
                constraint["id"],
                HardwareConstraintDecisionCreate(
                    verdict=Verdict.TRUE,
                    reason="Admit safe twin run",
                    decided_by=participant["id"],
                ),
            )
            receipt = await runtime.hardware.execute_constraint(
                constraint["id"],
                HardwareConstraintExecutionCreate(requested_by=participant["id"]),
            )
            before = runtime.hardware_store.get_return(receipt["return_id"])
            assert before["reintegration_status"] == "PENDING"
            cycle = await runtime.cycle()
            assert cycle.hardware_reintegrations == 1
            assert cycle.hardware_returns == 1
            after = runtime.hardware_store.get_return(receipt["return_id"])
            assert after["reintegration_status"] == "REINTEGRATED_OPEN"
            status = runtime.status()
            assert status.hardware_closure_enabled is True
            assert status.hardware_simulation_only is True
            assert status.hardware_direct_physical_actuation is False

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_hardware_api_full_path_and_operator_boundary(tmp_path: Path) -> None:
    config = RuntimeConfig(
        database_path=tmp_path / "api.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
    )
    app = create_app(config)
    with TestClient(app) as client:
        assert client.get("/hardware").status_code == 200
        capabilities = client.get("/network/hardware/capabilities")
        assert capabilities.status_code == 200
        assert capabilities.json()["simulation_only"] is True
        assert capabilities.json()["nuclear_actuation"] is False

        person = client.post(
            "/network/participants", json={"display_name": "API Person"}
        ).json()
        source = client.post(
            "/occurrences",
            json={"exact_text": "API hardware source", "source_id": "api-test"},
        ).json()
        device_response = client.post(
            "/admin/hardware/devices",
            json={
                "name": "API Ellipse Twin",
                "exact_description": "API-registered simulation-only ellipse twin",
                "created_by": person["id"],
            },
        )
        assert device_response.status_code == 200
        device = device_response.json()
        constraint = client.post(
            "/network/hardware/constraints/synthesize",
            json={
                "device_id": device["id"],
                "created_by": person["id"],
                "exact_intent": "Synthesize a bounded API constraint",
                "source_occurrence_ids": [source["id"]],
                "participant_ids": [person["id"]],
            },
        ).json()
        simulated = client.post(
            f"/network/hardware/constraints/{constraint['id']}/simulate",
            json={"requested_by": person["id"]},
        )
        assert simulated.status_code == 200
        decided = client.post(
            f"/network/hardware/constraints/{constraint['id']}/decision",
            json={
                "verdict": "TRUE",
                "reason": "Admit the safe API twin result",
                "decided_by": person["id"],
            },
        )
        assert decided.status_code == 200
        assert decided.json()["current_state"] == "ADMITTED"
        executed = client.post(
            f"/admin/hardware/constraints/{constraint['id']}/execute",
            json={"requested_by": person["id"]},
        )
        assert executed.status_code == 200
        reintegrated = client.post("/admin/hardware/reintegrate")
        assert reintegrated.status_code == 200
        field = client.get("/network/hardware/field")
        assert field.status_code == 200
        assert field.json()["stats"]["returns"] == 1
        assert client.get("/production").status_code == 200

    production = RuntimeConfig(
        database_path=tmp_path / "protected.db",
        inbox_dir=tmp_path / "protected-inbox",
        backup_dir=tmp_path / "protected-backups",
        autonomy_enabled=False,
        environment="production",
        public_development_mode=False,
        auth_mode="api_key",
        auth_api_keys_json=json.dumps(
            {
                "operator-key": {"subject": "operator", "role": "operator"},
                "member-key": {"subject": "member", "role": "member"},
            }
        ),
        session_secret="test-session-secret-that-is-long-enough",
        trusted_hosts=("testserver",),
    )
    protected_app = create_app(production)
    with TestClient(protected_app) as client:
        forbidden = client.post(
            "/admin/hardware/constraints/not-real/execute",
            headers={"X-Closure-API-Key": "member-key"},
            json={"requested_by": "member"},
        )
        assert forbidden.status_code == 403
        anonymous_field = client.get("/network/hardware/field")
        assert anonymous_field.status_code == 200
