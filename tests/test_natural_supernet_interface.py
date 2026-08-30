from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_natural_interface import create_app
from closure_supernet.completion_models import LocalTranslationStepInput
from closure_supernet.config import RuntimeConfig
from closure_supernet.natural_interface_models import (
    NaturalChartKind,
    NaturalInterfaceAdmissionCreate,
)
from closure_supernet.proof_completion_models import ProofSystemCreate
from closure_supernet.runtime import ClosureSupernetRuntime
from closure_supernet.supernet_models import ResourceEnvelope
from closure_supernet.topology_models import EventReturnCreate


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "natural-interface.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        trusted_hosts=("testserver", "localhost", "127.0.0.1"),
    )


def test_empty_and_source_point_are_the_minimal_admitted_charts(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        empty = runtime.natural_interface.select()
        assert empty["natural_chart"]["kind"] == NaturalChartKind.EMPTY_FIELD
        assert empty["admission_receipt"]["ui_admitted"] is False
        assert empty["admission_receipt"]["legacy_chart_transport_only"] is True
        assert empty["admission_receipt"]["canonical_pixel_layout_selected"] is False

        async def scenario() -> None:
            source = await runtime.integrate_resource(
                ResourceEnvelope(
                    exact_text="The exact note enters before any stronger relation.",
                    authored_by="person-a",
                    form_label="note",
                )
            )
            selected = runtime.natural_interface.select(
                focus_event_id=source["event_id"]
            )
            assert selected["natural_chart"]["kind"] == NaturalChartKind.SOURCE_POINT
            assert selected["natural_chart"]["minimal_sufficient"] is True
            assert selected["source_fibre"][0]["exact_text"].startswith(
                "The exact note"
            )
            assert selected["canonical_runtime_operation"] == "integrate"
            assert selected["truth_issued"] is False

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_selector_turing_return_and_collective_chart_selection(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            selector = await runtime.integrate_resource(
                ResourceEnvelope(
                    exact_text="Several symbols remain admissible at the open site.",
                    authored_by="selector",
                    form_label="undetermined instantiation",
                    adapter_label="selector",
                )
            )
            assert runtime.natural_interface.select(
                focus_event_id=selector["event_id"]
            )["natural_chart"]["kind"] == NaturalChartKind.OPEN_SELECTOR

            turing = await runtime.integrate_resource(
                ResourceEnvelope(
                    exact_text="Global hair 0 executes into local ball infinity.",
                    authored_by="life",
                    form_label="Turing Being action",
                    adapter_label="turing_being",
                )
            )
            turing_ui = runtime.natural_interface.select(
                focus_event_id=turing["event_id"]
            )
            assert turing_ui["natural_chart"]["kind"] == NaturalChartKind.TURING_BEING
            assert {
                "internal",
                "external",
                "semantic hand",
                "actual/potential",
            }.issubset(turing_ui["natural_chart"]["hidden_until_receipt"])

            returned_source = await runtime.integrate_resource(
                ResourceEnvelope(
                    exact_text="A bounded form can return and reopen.",
                    authored_by="returner",
                    form_label="return source",
                )
            )
            await runtime.topology.return_event(
                returned_source["event_id"],
                EventReturnCreate(
                    actor_id="returner",
                    exact_text="Returned successor potential.",
                ),
            )
            return_ui = runtime.natural_interface.select(
                focus_event_id=returned_source["event_id"]
            )
            assert (
                return_ui["natural_chart"]["kind"]
                == NaturalChartKind.RETURN_BALL_HAIR
            )

            collective = await runtime.integrate_resource(
                ResourceEnvelope(
                    exact_text="Two people contribute to one shared architecture.",
                    authored_by="person-a",
                    form_label="collective action",
                    affected_perspectives=["person-a", "person-b"],
                )
            )
            collective_ui = runtime.natural_interface.select(
                focus_event_id=collective["event_id"]
            )
            assert (
                collective_ui["natural_chart"]["kind"]
                == NaturalChartKind.SHARED_ARCHITECTURE
            )

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_rule_geometry_and_proof_balance_are_selected_only_with_receipts(
    tmp_path: Path,
) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            parent = await runtime.integrate_resource(
                ResourceEnvelope(
                    exact_text="A point starts one directed lineage.",
                    authored_by="person-a",
                    form_label="point",
                )
            )
            child = await runtime.interact_with_event(
                parent["event_id"],
                ResourceEnvelope(
                    exact_text="The next translated point continues the line.",
                    authored_by="person-a",
                    form_label="continuation",
                ),
            )
            lineage = runtime.natural_interface.select(
                focus_event_id=child["event_id"]
            )
            assert lineage["natural_chart"]["kind"] == NaturalChartKind.RULE_GEOMETRY

            proof = await runtime.proof_completion.create_system(
                ProofSystemCreate(
                    name="finite proof field",
                    authored_by="prover",
                    presentations=["a", "b", "c"],
                    steps=[
                        LocalTranslationStepInput(source="a", target="b", label="r₁"),
                        LocalTranslationStepInput(source="b", target="c", label="r₂"),
                    ],
                )
            )
            proof_ui = runtime.natural_interface.select(
                focus_event_id=proof["integration_event_id"]
            )
            assert proof_ui["natural_chart"]["kind"] == NaturalChartKind.PROOF_BALANCE
            assert proof_ui["proof_depth"]["completion_eq_proof"] is True
            assert proof_ui["proof_depth"]["canonical_derivation"] is None
            assert proof_ui["proof_depth"]["proof_fibre_reopenable"] is True
            assert set(proof_ui["natural_chart"]["required_layers"]) == {
                "Deriv",
                "Admits",
                "Balance",
                "MetaAbs",
            }

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_interface_admission_is_a_returned_open_supernet_event(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            source = await runtime.integrate_resource(
                ResourceEnvelope(
                    exact_text="The UI is an invariant interactive reading of closure.",
                    authored_by="person-a",
                    form_label="interface theorem",
                )
            )
            admitted = await runtime.natural_interface.admit(
                NaturalInterfaceAdmissionCreate(
                    focus_event_id=source["event_id"],
                    authored_by="person-a",
                )
            )
            event = admitted["event"]
            assert event["current_stage"] == "RETURNED"
            assert event["current_verdict"] == "OPEN"
            determined = next(
                state
                for state in event["state_history"]
                if state["stage"] == "DETERMINED"
            )
            assert determined["determined_form"]["canonical_pixel_layout"] is None
            assert (
                determined["rigidity_receipt"][
                    "natural_form_unique_under_declared_contract"
                ]
                is True
            )
            assert admitted["truth_issued"] is False

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_natural_interface_is_primary_and_classic_topology_is_a_rechart(
    tmp_path: Path,
) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        root = client.get("/")
        supernet = client.get("/supernet")
        natural = client.get("/natural-interface")
        classic = client.get("/supernet/classic")
        receipt = client.get("/supernet/interface")
        capabilities = client.get("/supernet/interface/capabilities")

        assert root.status_code == 200
        assert root.text == supernet.text == natural.text
        assert "Natural Black Mirror" in root.text
        assert "One continuous integrator" in root.text
        assert "truth-diagonal" in root.text
        assert "ellipse-mirror" in root.text
        assert "Rigidify" in root.text

        assert classic.status_code == 200
        assert "Living Continuous Interface" in classic.text
        assert classic.text != root.text

        payload = receipt.json()
        assert payload["natural_chart"]["kind"] == "EMPTY_FIELD"
        assert payload["admission_receipt"]["ui_admitted"] is False
        assert payload["admission_receipt"]["semantic_interface_receipt"] == (
            "visual_closure.interface_natural_form"
        )
        assert payload["admission_receipt"]["interaction_lifts_to_supernet_event"] is True

        caps = capabilities.json()
        assert caps["natural_form_unique_under_declared_contract"] is True
        assert caps["canonical_pixel_layout_selected"] is False
        assert caps["determination_issues_truth"] is False
        assert caps["live_sense"]["interaction_time_sense"] is True
        assert app.version == "3.11.0"
