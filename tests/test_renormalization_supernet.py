from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_renormalization import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.renormalization_models import (
    RegularizedFamilyCreate,
    RegularizedFamilyExtend,
    RenormalizationSchemeCreate,
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


def test_common_divergence_determines_relative_closure_without_true(
    tmp_path: Path,
) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            family = await runtime.renormalization.create_family(
                RegularizedFamilyCreate(
                    name="three translated members",
                    authored_by="participant-a",
                    cutoff_labels=["0", "1", "2"],
                    members={
                        "A": ["10", "11", "12"],
                        "B": ["13", "14", "15"],
                        "C": ["7", "8", "9"],
                    },
                )
            )
            assert family["status"] == "RELATIVE_CLOSURE_DETERMINED"
            assert family["universality"]["relative_closure_determined"] is True
            assert family["universality"]["pairwise_differences"]["B"]["A"] == "3"
            assert family["universality"]["pairwise_differences"]["A"]["C"] == "3"
            assert family["universality"]["absolute_level_determined"] is False
            event = runtime.supernet_store.get_event(family["integration_event_id"])
            assert event["current_stage"] == "RETURNED"
            assert event["current_verdict"] == "OPEN"
            determined = [
                state for state in event["state_history"] if state["stage"] == "DETERMINED"
            ]
            assert len(determined) == 1
            assert determined[0]["verdict"] == "OPEN"
            assert determined[0]["determined_form"]["absolute_level"] is None
            assert determined[0]["metadata"]["truth_issued"] is False
            lens = runtime.supernet_field("renormalization")
            assert any(item["id"] == event["id"] for item in lens["events"])

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_nonuniversal_family_remains_open_and_undetermined(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            family = await runtime.renormalization.create_family(
                RegularizedFamilyCreate(
                    name="member-dependent divergence",
                    cutoff_labels=["0", "1", "2"],
                    members={"A": ["10", "11", "12"], "B": ["13", "15", "16"]},
                )
            )
            assert family["status"] == "OPEN_UNIVERSALITY"
            assert family["universality"]["relative_closure_determined"] is False
            assert family["universality"]["obstructions"]
            event = runtime.supernet_store.get_event(family["integration_event_id"])
            assert not any(
                state.get("determined_form") is not None
                for state in event["state_history"]
            )
            assert event["current_verdict"] == "OPEN"

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_scheme_shift_moves_absolute_values_but_preserves_closure(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            family = await runtime.renormalization.create_family(
                RegularizedFamilyCreate(
                    name="scheme ambiguity",
                    cutoff_labels=["0", "1", "2"],
                    members={"A": ["10", "11", "12"], "B": ["13", "14", "15"]},
                )
            )
            scheme = await runtime.renormalization.create_scheme(
                family["id"],
                RenormalizationSchemeCreate(
                    name="reference member subtraction",
                    counterterm=["10", "11", "12"],
                    shift_probe="5",
                ),
            )
            evaluation = scheme["evaluation"]
            assert evaluation["admissible_scheme"] is True
            assert evaluation["renormalized_values"] == {"A": "0", "B": "3"}
            assert evaluation["shifted_renormalized_values"] == {"A": "-5", "B": "-2"}
            assert evaluation["shift_moves_absolute_values"] is True
            assert evaluation["shift_preserves_relative_closure"] is True
            assert evaluation["matches_relative_closure"] is True
            assert evaluation["scheme_is_closure"] is False
            event = runtime.supernet_store.get_event(scheme["integration_event_id"])
            assert event["current_verdict"] == "OPEN"

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_new_cutoff_evidence_reopens_parent_and_creates_successor(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            parent = await runtime.renormalization.create_family(
                RegularizedFamilyCreate(
                    name="extendable family",
                    cutoff_labels=["0", "1"],
                    members={"A": ["10", "11"], "B": ["13", "14"]},
                )
            )
            child = await runtime.renormalization.extend_family(
                parent["id"],
                RegularizedFamilyExtend(
                    authored_by="participant-b",
                    cutoff_labels=["2", "3"],
                    members={"A": ["12", "13"], "B": ["15", "16"]},
                ),
            )
            assert child["parent_family_id"] == parent["id"]
            assert child["status"] == "RELATIVE_CLOSURE_DETERMINED"
            parent_event = runtime.supernet_store.get_event(parent["integration_event_id"])
            assert any(state["stage"] == "REOPENED" for state in parent_event["state_history"])
            child_event = runtime.supernet_store.get_event(child["integration_event_id"])
            assert parent["integration_event_id"] in child_event["parent_event_ids"]

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_renormalization_api_is_live_supernet_lens(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        capabilities = client.get("/network/renormalization/capabilities")
        assert capabilities.status_code == 200
        assert capabilities.json()["formal_reading"] == "NRRF781"

        response = client.post(
            "/network/renormalization/families",
            json={
                "name": "API family",
                "authored_by": "api-participant",
                "cutoff_labels": ["0", "1", "2"],
                "members": {"left": ["20", "21", "22"], "right": ["17", "18", "19"]},
            },
        )
        assert response.status_code == 200
        family = response.json()
        assert family["universality"]["relative_closure_determined"] is True

        closure = client.get(
            f"/network/renormalization/families/{family['id']}/closure"
        )
        assert closure.status_code == 200
        assert closure.json()["absolute_level"] is None
        assert closure.json()["truth_issued"] is False

        field = client.get("/network/renormalization/field")
        assert field.status_code == 200
        assert field.json()["stats"]["determined_closures"] == 1

        lens = client.get("/supernet/project", params={"lens": "renormalization"})
        assert lens.status_code == 200
        assert lens.json()["lens"] == "renormalization"
        assert lens.json()["events"]

        page = client.get("/renormalization")
        assert page.status_code == 200
        assert "Relative Renormalization Closure" in page.text
