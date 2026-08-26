from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_resource import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.living_models import ParticipantCreate
from closure_supernet.models import Verdict
from closure_supernet.resource_models import (
    ProtocolReceiptCreate,
    ResourceCreate,
    ResourceEngagementCreate,
    ResourceReturnCreate,
    ResourceTranslationCreate,
    ResourceTranslationDecisionCreate,
)
from closure_supernet.runtime import ClosureSupernetRuntime


def make_runtime(tmp_path: Path) -> ClosureSupernetRuntime:
    return ClosureSupernetRuntime(
        RuntimeConfig(
            database_path=tmp_path / "runtime.db",
            inbox_dir=tmp_path / "inbox",
            autonomy_enabled=False,
        )
    )


async def seed_resources(runtime: ClosureSupernetRuntime):
    author = runtime.living.create_participant(ParticipantCreate(display_name="Author"))
    other = runtime.living.create_participant(ParticipantCreate(display_name="Other"))
    first = await runtime.resource_protocol.create_resource(
        ResourceCreate(
            exact_text="A lesson carried as a living resource.",
            created_by=author["id"],
            form_label="lesson-seed-defined-by-author",
            language_label="author-language-A",
            capabilities=["teach", "reopen"],
        )
    )
    second = await runtime.resource_protocol.create_resource(
        ResourceCreate(
            exact_text="The same field approached as collaborative action.",
            created_by=other["id"],
            form_label="collective-action-shape-not-in-registry",
            language_label="community-language-B",
            capabilities=["coordinate"],
        )
    )
    return author, other, first, second


def test_resource_forms_and_languages_are_open_not_registry_selected(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario():
            _author, _other, first, second = await seed_resources(runtime)
            assert first["form_label"] == "lesson-seed-defined-by-author"
            assert second["form_label"] == "collective-action-shape-not-in-registry"
            field = runtime.resource_protocol.projection()
            assert field["stats"]["finite_resource_registry"] is False
            assert field["stats"]["canonical_language_selected"] is False
            assert field["stats"]["protocol_is_translational_truth"] is False
            assert field["source_reverse_index"][f"resource:{first['id']}"] == [
                first["occurrence_id"]
            ]

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_protocol_success_does_not_admit_translation_truth(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario():
            author, _other, first, second = await seed_resources(runtime)
            receipt = await runtime.resource_protocol.create_protocol_receipt(
                ProtocolReceiptCreate(
                    resource_id=first["id"],
                    recorded_by=author["id"],
                    transport_label="successful-wire-handshake",
                    protocol_verdict=True,
                    exact_receipt="The transport delivered the bytes successfully.",
                )
            )
            translation = await runtime.resource_protocol.create_translation(
                ResourceTranslationCreate(
                    source_resource_id=first["id"],
                    target_resource_id=second["id"],
                    authored_by=author["id"],
                    exact_text="Read the lesson through the collective action without choosing one language.",
                    relation_label="cross-frame reading",
                    source_frame="lesson frame",
                    target_frame="action frame",
                    source_language="author-language-A",
                    target_language="community-language-B",
                    protocol_verdict=True,
                    transport_label="successful-wire-handshake",
                    faithfulness={"source": 1.0, "meaning": 0.6},
                )
            )
            assert receipt["protocol_verdict"] is True
            assert translation["protocol_verdict"] is True
            assert translation["current_verdict"] == str(Verdict.OPEN)
            stage, _ = runtime.resource_protocol.integrate_live_stage("protocol-test")
            assert stage["open_translation_ids"] == [translation["id"]]
            assert len(stage["natural_components"]) == 2

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_relative_admission_naturally_unifies_without_canonical_language(
    tmp_path: Path,
) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario():
            author, _other, first, second = await seed_resources(runtime)
            translation = await runtime.resource_protocol.create_translation(
                ResourceTranslationCreate(
                    source_resource_id=first["id"],
                    target_resource_id=second["id"],
                    authored_by=author["id"],
                    exact_text="The two forms translate while preserving both source languages.",
                    relation_label="mutual natural-form translation",
                    source_frame="source frame",
                    target_frame="target frame",
                    source_language=first["language_label"],
                    target_language=second["language_label"],
                    preserved=["both exact sources", "both language labels"],
                    faithfulness={"source": 1.0, "authorship": 1.0},
                )
            )
            runtime.resource_protocol.decide_translation(
                translation["id"],
                ResourceTranslationDecisionCreate(
                    verdict=Verdict.TRUE,
                    reason="Both participants admit this translation at the present scope.",
                    decided_by=author["id"],
                ),
            )
            stage, created = runtime.resource_protocol.integrate_live_stage(
                "relative-admission"
            )
            assert created is True
            assert stage["admitted_translation_ids"] == [translation["id"]]
            assert len(stage["natural_components"]) == 1
            component = stage["natural_components"][0]
            assert set(component["resource_ids"]) == {first["id"], second["id"]}
            assert component["canonical_form"] is None
            assert component["canonical_language"] is None
            assert set(component["language_labels"]) == {
                "author-language-A",
                "community-language-B",
            }
            assert stage["complete_coverage"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_return_self_reintegrates_as_open_translation_and_new_resource(
    tmp_path: Path,
) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario():
            author, _other, first, _second = await seed_resources(runtime)
            engagement = await runtime.resource_protocol.create_engagement(
                ResourceEngagementCreate(
                    resource_id=first["id"],
                    actor_id=author["id"],
                    exact_text="The participant studies and changes the lesson through action.",
                    engagement_label="active study and transformation",
                    preserves=["source lesson"],
                    transforms=["participant understanding"],
                )
            )
            returned = await runtime.resource_protocol.create_return(
                ResourceReturnCreate(
                    engagement_id=engagement["id"],
                    exact_text="A returned practice formed from the lesson.",
                    authored_by=author["id"],
                    form_label="practice-return",
                    language_label="embodied-language-C",
                )
            )
            assert returned["reintegration_status"] == "PENDING"
            result = await runtime.cycle()
            assert result.resource_reintegrations == 1
            assert result.resources == 3
            reintegration = runtime.resource_store.list_reintegrations()[0]
            assert reintegration["status"] == "REINTEGRATED_OPEN"
            translation = runtime.resource_store.get_translation(
                reintegration["translation_id"]
            )
            assert translation["current_verdict"] == str(Verdict.OPEN)
            returned_resource = runtime.resource_store.get_resource(
                returned["returned_resource_id"]
            )
            assert returned_resource["parent_resource_id"] == first["id"]
            assert returned_resource["metadata"]["return_is_not_terminal"] is True
            field = runtime.living_field()
            assert field["live_resource_protocol"]["stats"]["self_reintegrating"] is True

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_live_limit_signature_is_delivery_order_independent(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario():
            author, _other, first, second = await seed_resources(runtime)
            translation = await runtime.resource_protocol.create_translation(
                ResourceTranslationCreate(
                    source_resource_id=first["id"],
                    target_resource_id=second["id"],
                    authored_by=author["id"],
                    exact_text="Admit one translation for the limit signature.",
                    relation_label="limit relation",
                    source_frame="A",
                    target_frame="B",
                )
            )
            runtime.resource_protocol.decide_translation(
                translation["id"],
                ResourceTranslationDecisionCreate(
                    verdict=Verdict.TRUE,
                    reason="relative test admission",
                    decided_by=author["id"],
                ),
            )
            resources = runtime.resource_store.list_resources()
            translations = runtime.resource_store.list_translations()
            forward = runtime.resource_protocol.canonical_limit_signature(
                resources, translations
            )
            reverse = runtime.resource_protocol.canonical_limit_signature(
                list(reversed(resources)), list(reversed(translations))
            )
            assert forward == reverse
            stage, _ = runtime.resource_protocol.integrate_live_stage("order-test")
            assert stage["limit_signature"] == forward
            projection = runtime.resource_protocol.projection()
            assert projection["stats"]["live_limit_matches_current_batch"] is True
            assert stage["delivery_order"]

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_resource_api_is_public_complete_and_nonterminal(tmp_path: Path) -> None:
    config = RuntimeConfig(
        database_path=tmp_path / "api.db",
        inbox_dir=tmp_path / "inbox",
        autonomy_enabled=False,
    )
    app = create_app(config)
    with TestClient(app) as client:
        participant = client.post(
            "/network/participants", json={"display_name": "Public participant"}
        ).json()
        capabilities = client.get("/network/resources/capabilities")
        assert capabilities.status_code == 200
        assert capabilities.json()["finite_resource_registry"] is False
        assert capabilities.json()["canonical_language_selected"] is False
        resource = client.post(
            "/network/resources",
            json={
                "exact_text": "A publicly authored resource form.",
                "created_by": participant["id"],
                "form_label": "public-form-without-registry",
                "language_label": "participant-chosen-language",
            },
        )
        assert resource.status_code == 200
        assert client.get("/resources").status_code == 200
        integrated = client.post("/network/resource-live/integrate")
        assert integrated.status_code == 200
        assert integrated.json()["stage"]["complete_coverage"] is True
        field = client.get("/network/resource-field")
        assert field.status_code == 200
        stats = field.json()["stats"]
        assert stats["nonterminal"] is True
        assert stats["complete_network_coverage"] is True
        assert stats["protocol_verdict_is_truth"] is False
