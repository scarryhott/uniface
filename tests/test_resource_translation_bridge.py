from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from closure_supernet.api_resource import create_app
from closure_supernet.config import RuntimeConfig
from closure_supernet.living_models import ParticipantCreate
from closure_supernet.models import Verdict
from closure_supernet.resource_models import (
    ResourceCreate,
    ResourceTranslationCreate,
    ResourceTranslationDecisionCreate,
)
from closure_supernet.runtime import ClosureSupernetRuntime


def make_runtime(tmp_path: Path) -> ClosureSupernetRuntime:
    return ClosureSupernetRuntime(
        RuntimeConfig(
            database_path=tmp_path / "bridge.db",
            inbox_dir=tmp_path / "inbox",
            autonomy_enabled=False,
        )
    )


def test_resource_translation_is_a_canonical_translation_event(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    try:
        async def scenario() -> None:
            participant = runtime.living.create_participant(
                ParticipantCreate(display_name="Translator")
            )
            source = await runtime.resource_protocol.create_resource(
                ResourceCreate(
                    exact_text="A learning resource in its own source language.",
                    created_by=participant["id"],
                    form_label="lesson",
                    language_label="source-language",
                )
            )
            target = await runtime.resource_protocol.create_resource(
                ResourceCreate(
                    exact_text="A coordinated action in another language.",
                    created_by=participant["id"],
                    form_label="collective-action",
                    language_label="action-language",
                )
            )
            proposed = await runtime.resource_protocol.create_translation(
                ResourceTranslationCreate(
                    source_resource_id=source["id"],
                    target_resource_id=target["id"],
                    authored_by=participant["id"],
                    exact_text="Translate the lesson into action without replacing either language.",
                    relation_label="lesson-to-action",
                    source_frame="learning frame",
                    target_frame="action frame",
                    source_language=source["language_label"],
                    target_language=target["language_label"],
                    protocol_verdict=True,
                    transport_label="successful-web-transport",
                )
            )
            assert runtime.reconcile_resource_translations() >= 1
            canonical = runtime.translation_store.get_by_external_key(
                f"resource_translation:{proposed['id']}"
            )
            assert canonical is not None
            assert canonical["current_verdict"] == "OPEN"
            assert canonical["transport"]["protocol_verdict"] is True
            assert canonical["transport"]["protocol_verdict_is_not_truth"] is True
            assert canonical["source_forms"][0]["form_type"] == "resource"
            assert canonical["target_forms"][0]["form_type"] == "resource"

            runtime.resource_protocol.decide_translation(
                proposed["id"],
                ResourceTranslationDecisionCreate(
                    verdict=Verdict.TRUE,
                    reason="Participant-relative admission preserves both forms.",
                    decided_by=participant["id"],
                ),
            )
            runtime.reconcile_resource_translations()
            canonical = runtime.translation_store.get_by_external_key(
                f"resource_translation:{proposed['id']}"
            )
            assert canonical["current_state"] == "ADMITTED"
            assert canonical["current_verdict"] == "TRUE"
            stage, _ = runtime.resource_protocol.integrate_live_stage(
                "canonical-bridge-test"
            )
            assert len(stage["natural_components"]) == 1

        asyncio.run(scenario())
    finally:
        runtime.close()


def test_resource_api_preserves_translation_api(tmp_path: Path) -> None:
    app = create_app(
        RuntimeConfig(
            database_path=tmp_path / "api.db",
            inbox_dir=tmp_path / "inbox",
            autonomy_enabled=False,
        )
    )
    with TestClient(app) as client:
        assert client.get("/translation").status_code == 200
        assert client.get("/resources").status_code == 200
        translation_capabilities = client.get("/network/translations/capabilities")
        resource_capabilities = client.get("/network/resources/capabilities")
        assert translation_capabilities.status_code == 200
        assert resource_capabilities.status_code == 200
        assert translation_capabilities.json()["canonical_live_primitive"] == "TranslationEvent"
        assert resource_capabilities.json()["finite_resource_registry"] is False
        assert resource_capabilities.json()["canonical_language_selected"] is False
