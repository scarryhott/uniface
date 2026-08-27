from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_framework import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.constructive_models import FiniteCommutativeGroupCreate
from closure_supernet.framework_models import (
    NaturalSelectionArenaCreate,
    PresentationRef,
    TranslationalTruthFrameworkCreate,
    TruthSelectionBridgeCreate,
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


def z3() -> FiniteCommutativeGroupCreate:
    return FiniteCommutativeGroupCreate(
        name="Z3",
        elements=["0", "1", "2"],
        zero="0",
        addition={
            "0": {"0": "0", "1": "1", "2": "2"},
            "1": {"0": "1", "1": "2", "2": "0"},
            "2": {"0": "2", "1": "0", "2": "1"},
        },
        inverse={"0": "0", "1": "2", "2": "1"},
    )


def arena_data() -> NaturalSelectionArenaCreate:
    return NaturalSelectionArenaCreate(
        name="one selected natural orbit",
        authored_by="participant",
        forms=["x0", "x1", "x2"],
        group=z3(),
        action={
            "0": {"x0": "x0", "x1": "x1", "x2": "x2"},
            "1": {"x0": "x1", "x1": "x2", "x2": "x0"},
            "2": {"x0": "x2", "x1": "x0", "x2": "x1"},
        },
        selected={"x0": True, "x1": True, "x2": True},
        resource_metric={"x0": 0, "x1": 1, "x2": 2},
    )


def contextual_data() -> TranslationalTruthFrameworkCreate:
    return TranslationalTruthFrameworkCreate(
        name="contextual parity",
        authored_by="participant",
        observables=["q0", "q1", "q2"],
        frames=["f0", "f1", "f2"],
        values=["0", "1"],
        default_value="0",
        group=z3(),
        frame_action={
            "0": {"f0": "f0", "f1": "f1", "f2": "f2"},
            "1": {"f0": "f1", "f1": "f2", "f2": "f0"},
            "2": {"f0": "f2", "f1": "f0", "f2": "f1"},
        },
        observable_action={
            "0": {"q0": "q0", "q1": "q1", "q2": "q2"},
            "1": {"q0": "q1", "q1": "q2", "q2": "q0"},
            "2": {"q0": "q2", "q1": "q0", "q2": "q1"},
        },
        verdicts={
            "f0": {"q0": "0", "q1": "1", "q2": None},
            "f1": {"q0": None, "q1": "0", "q2": "1"},
            "f2": {"q0": "1", "q1": None, "q2": "0"},
        },
    )


def test_natural_selector_uses_orbit_not_metric(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            arena = await runtime.frameworks.create_arena(arena_data())
            evaluation = arena["evaluation"]
            assert evaluation["natural"] is True
            assert evaluation["selector_fixed_under_shift"] is True
            assert evaluation["factors_through_orbits"] is True
            assert evaluation["unique_selected_orbit"] is True
            assert evaluation["resource_metric_selector_natural"] is False
            assert evaluation["resource_metric_foundational_selector"] is False
            assert evaluation["metric_flip_witnesses"]
            event = runtime.supernet_store.get_event(arena["integration_event_id"])
            determined = next(state for state in event["state_history"] if state["stage"] == "DETERMINED")
            assert determined["verdict"] == "OPEN"
            assert determined["determined_form"]["canonical_presentation"] is None
            assert determined["metadata"]["truth_issued"] is False
        asyncio.run(scenario())
    finally:
        runtime.close()


def test_contextual_framework_retains_unique_orbit_truth(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            framework = await runtime.frameworks.create_framework(contextual_data())
            evaluation = framework["evaluation"]
            assert evaluation["joint_translation_invariant"] is True
            assert evaluation["truth_unique"] is True
            assert evaluation["fragment_noncontextual"] is True
            assert evaluation["classification"] == "CONTEXTUAL"
            assert evaluation["contextual"] is True
            assert evaluation["classical"] is False
            assert evaluation["global_assignment"] is None
            assert evaluation["global_section_is_not_truth_object"] is True
            assert set(evaluation["orbit_truth"].values()) == {None, "0", "1"}
            event = runtime.supernet_store.get_event(framework["integration_event_id"])
            determined = next(state for state in event["state_history"] if state["stage"] == "DETERMINED")
            assert determined["verdict"] == "OPEN"
            assert determined["determined_form"]["classification"] == "CONTEXTUAL"
        asyncio.run(scenario())
    finally:
        runtime.close()


def test_natural_selector_reunifies_with_contextual_truth(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            arena = await runtime.frameworks.create_arena(arena_data())
            framework = await runtime.frameworks.create_framework(contextual_data())
            bridge = await runtime.frameworks.create_bridge(
                TruthSelectionBridgeCreate(
                    name="natural contextual truth",
                    authored_by="participant",
                    arena_id=arena["id"],
                    framework_id=framework["id"],
                    form_to_presentation={
                        "x0": PresentationRef(frame="f0", observable="q0"),
                        "x1": PresentationRef(frame="f1", observable="q1"),
                        "x2": PresentationRef(frame="f2", observable="q2"),
                    },
                )
            )
            assert bridge["equivariant"] is True
            assert bridge["natural_selector"] is True
            assert bridge["framework_translational_truth"] is True
            assert bridge["unified"] is True
            assert bridge["framework_classification"] == "CONTEXTUAL"
            assert set(bridge["selected_orbit_truth"].values()) == {"0"}
            assert bridge["global_assignment_required_for_truth"] is False
            assert bridge["resource_metric_foundational_selector"] is False
            event = runtime.supernet_store.get_event(bridge["integration_event_id"])
            assert any(state["stage"] == "DETERMINED" for state in event["state_history"])
        asyncio.run(scenario())
    finally:
        runtime.close()


def test_framework_api_and_supernet_lens(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/frameworks")
        assert page.status_code == 200
        assert "Natural translational truth" in page.text
        arena = client.post("/network/frameworks/naturality", json=arena_data().model_dump(mode="json"))
        assert arena.status_code == 200
        assert arena.json()["evaluation"]["natural"] is True
        framework = client.post("/network/frameworks/truth", json=contextual_data().model_dump(mode="json"))
        assert framework.status_code == 200
        assert framework.json()["evaluation"]["classification"] == "CONTEXTUAL"
        bridge = client.post(
            "/network/frameworks/bridges",
            json={
                "name": "API bridge",
                "authored_by": "participant",
                "arena_id": arena.json()["id"],
                "framework_id": framework.json()["id"],
                "form_to_presentation": {
                    "x0": {"frame": "f0", "observable": "q0"},
                    "x1": {"frame": "f1", "observable": "q1"},
                    "x2": {"frame": "f2", "observable": "q2"},
                },
            },
        )
        assert bridge.status_code == 200
        assert bridge.json()["unified"] is True
        field = client.get("/network/frameworks/field")
        assert field.status_code == 200
        assert field.json()["stats"]["contextual"] == 1
        assert field.json()["stats"]["unified_bridges"] == 1
        lens = client.get("/supernet/project", params={"lens": "framework"})
        assert lens.status_code == 200
        assert lens.json()["lens"] == "framework"
        assert lens.json()["stats"]["visible_events"] >= 3
        capabilities = client.get("/supernet/capabilities")
        assert capabilities.status_code == 200
        assert capabilities.json()["classical_and_contextual_share_truth"] is True
        assert capabilities.json()["resource_metrics_are_downstream"] is True
