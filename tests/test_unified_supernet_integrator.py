from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_supernet import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.living_models import ParticipantCreate
from closure_supernet.models import OccurrenceCreate, Verdict
from closure_supernet.resource_models import ResourceCreate
from closure_supernet.runtime import ClosureSupernetRuntime
from closure_supernet.supernet_models import IntegrationStage, ResourceEnvelope
from closure_supernet.translation_models import (
    RelativeFormRef,
    TranslationEventCreate,
    TranslationState,
    TranslationStateCreate,
)


def make_config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        database_path=tmp_path / "supernet.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
    )


def test_integrate_is_the_single_runtime_transition(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            receipt = await runtime.integrate_resource(
                ResourceEnvelope(
                    exact_text="point → line → loop → return → new point",
                    authored_by="participant-a",
                    form_label="notebook path",
                    language_label="source axiometry",
                    relation_hints=["point-line-loop-return"],
                )
            )
            event = runtime.supernet_store.get_event(receipt["event_id"])
            assert event["exact_source_ids"] == receipt["occurrence_ids"]
            assert event["current_stage"] == "RELATION_SENSED"
            assert event["current_verdict"] == "OPEN"
            assert receipt["truth_issued_by_determination"] is False

            field = runtime.supernet_field()
            assert field["canonical_runtime_operation"] == "integrate"
            assert field["subsystems_are_lenses"] is True
            assert field["canonical_language"] is None
            assert field["stats"]["events"] == 1
            assert field["current_stage"]["event_count"] == 1

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_determination_requires_rigidity_and_does_not_issue_true(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            receipt = await runtime.integrate_resource(
                ResourceEnvelope(
                    exact_text="An undetermined string with one relation-rigid site",
                    authored_by="selector-participant",
                    form_label="undetermined instantiation",
                    adapter_label="selector",
                )
            )
            result = runtime.supernet_integrator.determine(
                receipt["event_id"],
                actor_id="selector-participant",
                rigidity_scope=["site:0"],
                rigidity_receipt={
                    "site:0": {
                        "admissible_symbols": ["line"],
                        "unique": True,
                    }
                },
                determined_form={"site:0": "line"},
                unitary_path_partition={
                    "path": ["point", "line"],
                    "partition": [["line"]],
                },
            )
            event = result["event"]
            assert event["current_stage"] == IntegrationStage.DETERMINED
            assert event["current_verdict"] == Verdict.OPEN
            assert event["state_history"][-1]["determined_form"] == {
                "site:0": "line"
            }
            assert event["state_history"][-1]["metadata"][
                "truth_issued"
            ] is False

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_existing_resource_endpoint_is_a_lens_over_same_integrator(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            participant = runtime.living.create_participant(
                ParticipantCreate(display_name="Resource participant")
            )
            resource = await runtime.resource_protocol.create_resource(
                ResourceCreate(
                    exact_text="A lesson returned as a living resource",
                    created_by=participant["id"],
                    form_label="lesson",
                    language_label="participant language",
                )
            )
            central = runtime.supernet_store.get_by_external_key(
                f"occurrence:{resource['occurrence_id']}"
            )
            assert central is not None
            assert runtime.supernet_integrator._lens(central) == "resource"
            resource_lens = runtime.supernet_field("resource")
            assert any(
                resource["occurrence_id"] in item["exact_source_ids"]
                for item in resource_lens["events"]
            )
            assert resource_lens["stats"]["all_events"] >= 1

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_translation_reconciles_into_same_event_field(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            left = await runtime.ingest(
                OccurrenceCreate(exact_text="ball", source_id="test")
            )
            right = await runtime.ingest(
                OccurrenceCreate(exact_text="hair", source_id="test")
            )
            translation = runtime.translation.create(
                TranslationEventCreate(
                    exact_source_ids=[left["id"], right["id"]],
                    source_forms=[
                        RelativeFormRef(
                            form_type="source",
                            form_id="ball",
                            occurrence_id=left["id"],
                        )
                    ],
                    target_forms=[
                        RelativeFormRef(
                            form_type="source",
                            form_id="hair",
                            occurrence_id=right["id"],
                        )
                    ],
                    relation_type="BALL_HAIR_RETURN",
                    generated_by="participant",
                )
            )
            runtime.translation.transition(
                translation["id"],
                TranslationStateCreate(
                    state=TranslationState.ADMITTED,
                    verdict=Verdict.TRUE,
                    reason="Scoped participant admission",
                    actor_id="participant",
                ),
            )
            runtime.supernet_integrator.reconcile_translations()
            integrated = runtime.supernet_store.get_by_external_key(
                f"translation:{translation['id']}"
            )
            assert integrated is not None
            assert integrated["current_stage"] == "ADMITTED"
            assert integrated["current_verdict"] == "TRUE"
            assert integrated["metadata"]["canonical_translation_id"] == translation["id"]

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_field_limit_signature_is_stable_without_new_integration(tmp_path: Path) -> None:
    runtime = ClosureSupernetRuntime(make_config(tmp_path))
    try:
        async def scenario() -> None:
            await runtime.integrate_resource(
                ResourceEnvelope(
                    exact_text="0 ↔ ∞ reciprocal poles",
                    form_label="source chart",
                )
            )
            first = runtime.supernet_integrator.commit_stage(
                trigger="first-replay"
            )
            second = runtime.supernet_integrator.commit_stage(
                trigger="second-replay"
            )
            assert first["limit_signature"] == second["limit_signature"]
            assert first["history_signature"] == second["history_signature"]
            assert second["stage_index"] == first["stage_index"] + 1

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_unified_supernet_api_is_primary_surface(tmp_path: Path) -> None:
    app = create_app(make_config(tmp_path))
    with TestClient(app) as client:
        root = client.get("/")
        assert root.status_code == 200
        assert "One continuous integrator" in root.text

        response = client.post(
            "/supernet/integrate",
            json={
                "exact_text": "A public interaction enters one Supernet field",
                "authored_by": "api-participant",
                "form_label": "interaction",
            },
        )
        assert response.status_code == 200
        receipt = response.json()
        assert receipt["canonical_runtime_operation"] == "integrate"

        field = client.get("/supernet/field")
        assert field.status_code == 200
        payload = field.json()
        assert payload["stats"]["events"] == 1
        assert payload["subsystems_are_lenses"] is True

        projected = client.get(
            "/supernet/project", params={"lens": "source"}
        )
        assert projected.status_code == 200
        assert projected.json()["lens"] == "source"
