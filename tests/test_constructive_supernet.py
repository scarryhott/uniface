from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_constructive import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.constructive_models import (
    AxiometricFormCreate,
    FiniteCommutativeGroupCreate,
    IdempotentTranslationCreate,
    TranslationChartCompareCreate,
    TranslationalClosureCreate,
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


def z2() -> FiniteCommutativeGroupCreate:
    return FiniteCommutativeGroupCreate(
        name="Z2",
        elements=["0", "1"],
        zero="0",
        addition={
            "0": {"0": "0", "1": "1"},
            "1": {"0": "1", "1": "0"},
        },
        inverse={"0": "0", "1": "1"},
    )


def test_u1_derives_hold_and_u3_is_defect(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            form = await runtime.constructive.create_form(
                AxiometricFormCreate(
                    name="split closure",
                    authored_by="participant",
                    source_carrier=["a", "b"],
                    presentation_carrier=["A", "B", "ghost"],
                    encode={"a": "A", "b": "B"},
                    evaluate={"A": "a", "B": "b", "ghost": "a"},
                )
            )
            evaluation = form["evaluation"]
            assert evaluation["u1_return"] is True
            assert evaluation["u2_hold_idempotent"] is True
            assert evaluation["u2_derived_from_u1"] is True
            assert evaluation["u3_closes"] is False
            assert evaluation["defect"] == ["ghost"]
            assert evaluation["classical_choice_required"] is False
            event = runtime.supernet_store.get_event(form["integration_event_id"])
            assert any(state["stage"] == "DETERMINED" for state in event["state_history"])
            determined = next(
                state for state in event["state_history"] if state["stage"] == "DETERMINED"
            )
            assert determined["verdict"] == "OPEN"
            assert determined["metadata"]["truth_issued"] is False

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_closing_form_has_empty_defect_and_all_u3_readings(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            form = await runtime.constructive.create_form(
                AxiometricFormCreate(
                    name="closing form",
                    source_carrier=["a", "b"],
                    presentation_carrier=["A", "B"],
                    encode={"a": "A", "b": "B"},
                    evaluate={"A": "a", "B": "b"},
                )
            )
            evaluation = form["evaluation"]
            assert evaluation["u3_closes"] is True
            assert evaluation["defect_empty"] is True
            assert evaluation["encode_surjective"] is True
            assert evaluation["evaluate_injective"] is True
            assert evaluation["encode_injective"] is True
            assert evaluation["evaluate_surjective"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_idempotent_translation_constructs_form_without_choice(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            form = await runtime.constructive.create_from_idempotent(
                IdempotentTranslationCreate(
                    name="hold form",
                    carrier=["x", "y"],
                    translation={"x": "x", "y": "x"},
                )
            )
            assert form["origin"] == "IDEMPOTENT_TRANSLATION_CONSTRUCTED_FORM"
            assert form["source_carrier"] == ["x"]
            assert form["evaluate"] == {"x": "x", "y": "x"}
            assert form["evaluation"]["u1_return"] is True
            assert form["evaluation"]["u2_hold_idempotent"] is True
            assert form["metadata"]["constructed_not_chosen"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_translational_truth_bridge_and_unique_shift(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            closure = await runtime.constructive.create_translation(
                TranslationalClosureCreate(
                    name="Z2 closure",
                    authored_by="participant",
                    group=z2(),
                    sites=["p", "q"],
                    base_site="p",
                    levels={"p": "0", "q": "1"},
                )
            )
            evaluation = closure["evaluation"]
            assert evaluation["relative_potential"] == {
                "p": {"p": "0", "q": "1"},
                "q": {"p": "1", "q": "0"},
            }
            assert evaluation["cocycle_consistent"] is True
            assert evaluation["relative_potential_complete"] is True
            assert evaluation["closure_form_closes"] is True
            assert evaluation["canonical_absolute_level"] is None
            bridge = runtime.constructive_store.get_form(
                evaluation["closure_form_id"]
            )
            assert bridge["origin"] == "TRANSLATIONAL_TRUTH_BRIDGE"
            assert bridge["evaluation"]["u3_closes"] is True

            comparison = await runtime.constructive.compare_chart(
                closure["id"],
                TranslationChartCompareCreate(
                    authored_by="participant",
                    levels={"p": "1", "q": "0"},
                ),
            )
            assert comparison["derived_shift"] == "1"
            assert comparison["charts_differ_by_common_shift"] is True
            assert comparison["relative_potentials_equal"] is True
            assert comparison["closure_equal"] is True
            assert comparison["unique_shift"] is True
            assert comparison["overlap_forces_equality"] is True
            assert comparison["classical_choice_required"] is False

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_constructive_api_and_supernet_lens(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        page = client.get("/constructive")
        assert page.status_code == 200
        assert "NRRF783 constructive unification" in page.text

        response = client.post(
            "/network/constructive/forms",
            json={
                "name": "API form",
                "authored_by": "api-participant",
                "source_carrier": ["a"],
                "presentation_carrier": ["A"],
                "encode": {"a": "A"},
                "evaluate": {"A": "a"},
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["evaluation"]["u1_return"] is True
        assert payload["evaluation"]["u3_closes"] is True

        field = client.get("/network/constructive/field")
        assert field.status_code == 200
        assert field.json()["stats"]["forms"] == 1
        assert field.json()["classical_choice_required"] is False

        lens = client.get("/supernet/project", params={"lens": "constructive"})
        assert lens.status_code == 200
        lens_payload = lens.json()
        assert lens_payload["lens"] == "constructive"
        assert lens_payload["stats"]["visible_events"] >= 1

        capabilities = client.get("/supernet/capabilities")
        assert capabilities.status_code == 200
        assert capabilities.json()["constructive_explicit_witnesses"] is True
        assert capabilities.json()["classical_choice_required"] is False
