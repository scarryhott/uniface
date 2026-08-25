from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from closure_supernet.api import create_app
from closure_supernet.axiometry import extract_operator_path
from closure_supernet.config import RuntimeConfig
from closure_supernet.integration_models import IntegrationCreate, IntegrationKind
from closure_supernet.models import OccurrenceCreate
from closure_supernet.runtime import ClosureSupernetRuntime


def make_runtime(tmp_path: Path, **overrides) -> ClosureSupernetRuntime:
    config = RuntimeConfig(
        database_path=tmp_path / "runtime.db",
        inbox_dir=tmp_path / "inbox",
        autonomy_enabled=False,
        **overrides,
    )
    return ClosureSupernetRuntime(config)


def test_zero_and_infinity_are_indexed_as_reciprocal_poles(tmp_path: Path) -> None:
    path = extract_operator_path("0 ↔ ∞")
    assert path[0]["key"] == "ZERO_INFINITY"
    assert path[0]["role"] == "reciprocal poles"
    runtime = make_runtime(tmp_path)
    try:
        assert runtime.integrations.capabilities().zero_infinity_role == "reciprocal poles"
    finally:
        runtime.close()


def test_signed_inbound_webhook_is_source_preserving_and_idempotent(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("CLOSURE_TEST_WEBHOOK_SECRET", "shared-secret")
    runtime = make_runtime(tmp_path)
    try:
        record = runtime.integrations.create(
            IntegrationCreate(
                name="signed-inbound",
                kind=IntegrationKind.WEBHOOK_IN,
                secret_env="CLOSURE_TEST_WEBHOOK_SECRET",
            )
        )
        payload = {
            "version": "closure.supernet/v1",
            "items": [
                {
                    "external_id": "note-1",
                    "exact_text": "0 ↔ ∞ are reciprocal poles",
                    "source_id": "external-notebook",
                    "source_location": "external://notebook/1",
                }
            ],
        }
        raw = json.dumps(payload, sort_keys=True).encode("utf-8")
        signature = "sha256=" + hmac.new(
            b"shared-secret", raw, hashlib.sha256
        ).hexdigest()

        async def scenario() -> None:
            first = await runtime.integrations.ingest_webhook(record.id, raw, signature)
            second = await runtime.integrations.ingest_webhook(record.id, raw, signature)
            assert first["pulled"] == 1 and first["skipped"] == 0
            assert second["pulled"] == 0 and second["skipped"] == 1

        asyncio.run(scenario())
        occurrences = runtime.store.list_occurrences()
        assert len(occurrences) == 1
        assert occurrences[0]["exact_text"] == "0 ↔ ∞ are reciprocal poles"
        assert occurrences[0]["metadata"]["external_assertion_is_not_truth"] is True
        assert occurrences[0]["operator_path"][0]["role"] == "reciprocal poles"
    finally:
        runtime.close()


def test_http_json_feed_uses_etag_and_exact_occurrences(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.headers.get("If-None-Match") == '"v1"':
            return httpx.Response(304)
        return httpx.Response(
            200,
            headers={"ETag": '"v1"', "Content-Type": "application/json"},
            json={
                "items": [
                    {
                        "external_id": "feed-note-1",
                        "exact_text": "ball ↔ hair",
                        "source_location": "https://feed.example/notes/1",
                    }
                ]
            },
        )

    runtime.integrations._client_factory = lambda: httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    )
    try:
        record = runtime.integrations.create(
            IntegrationCreate(
                name="json-feed",
                kind=IntegrationKind.HTTP_JSON_FEED,
                config={"url": "https://feed.example/notes"},
            )
        )

        async def scenario() -> None:
            first = await runtime.integrations.poll_enabled(record.id)
            second = await runtime.integrations.poll_enabled(record.id)
            assert first[0].pulled == 1
            assert second[0].pulled == 0

        asyncio.run(scenario())
        assert len(requests) == 2
        assert requests[1].headers["If-None-Match"] == '"v1"'
        occurrence = runtime.store.list_occurrences()[0]
        assert occurrence["exact_text"] == "ball ↔ hair"
        assert occurrence["metadata"]["integration_kind"] == "HTTP_JSON_FEED"
    finally:
        runtime.close()


def test_github_repository_connector_retains_path_and_blob_provenance(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    note = "loop ↔ sensor ↔ selection"
    encoded = base64.b64encode(note.encode("utf-8")).decode("ascii")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/git/trees/main"):
            return httpx.Response(
                200,
                json={
                    "sha": "tree-sha-1",
                    "truncated": False,
                    "tree": [
                        {
                            "path": "notes/loop.md",
                            "type": "blob",
                            "sha": "blob-sha-1",
                            "size": len(note.encode("utf-8")),
                        }
                    ],
                },
            )
        if request.url.path.endswith("/git/blobs/blob-sha-1"):
            return httpx.Response(200, json={"encoding": "base64", "content": encoded})
        return httpx.Response(404)

    runtime.integrations._client_factory = lambda: httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    )
    try:
        record = runtime.integrations.create(
            IntegrationCreate(
                name="github-notes",
                kind=IntegrationKind.GITHUB_REPOSITORY,
                config={
                    "repository": "example/notes",
                    "ref": "main",
                    "include": ["**/*.md"],
                },
            )
        )

        async def scenario() -> None:
            result = await runtime.integrations.poll_enabled(record.id)
            assert result[0].pulled == 1

        asyncio.run(scenario())
        occurrence = runtime.store.list_occurrences()[0]
        metadata = occurrence["metadata"]
        assert occurrence["source_location"] == "github://example/notes@tree-sha-1/notes/loop.md"
        assert metadata["tree_sha"] == "tree-sha-1"
        assert metadata["blob_sha"] == "blob-sha-1"
        assert metadata["path"] == "notes/loop.md"
    finally:
        runtime.close()


def test_outbound_webhook_exports_projection_signature_and_advances_cursor(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("CLOSURE_TEST_OUTBOUND_SECRET", "outbound-secret")
    runtime = make_runtime(tmp_path)
    deliveries: list[tuple[bytes, httpx.Headers]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        deliveries.append((request.content, request.headers))
        return httpx.Response(202, json={"accepted": True})

    runtime.integrations._client_factory = lambda: httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    )
    try:
        asyncio.run(
            runtime.ingest(
                OccurrenceCreate(
                    exact_text="point → line → loop → return → new point",
                    source_id="test",
                )
            )
        )
        record = runtime.integrations.create(
            IntegrationCreate(
                name="outbound",
                kind=IntegrationKind.WEBHOOK_OUT,
                config={"url": "https://sink.example/closure"},
                secret_env="CLOSURE_TEST_OUTBOUND_SECRET",
            )
        )

        async def scenario() -> None:
            projection = runtime.black_mirror()
            first = await runtime.integrations.push_enabled(projection)
            assert first[0].pushed >= 1
            cursor_after_first = runtime.integration_store.get_integration(record.id)["cursor"]["event_seq"]
            second = await runtime.integrations.push_enabled(projection)
            cursor_after_second = runtime.integration_store.get_integration(record.id)["cursor"]["event_seq"]
            assert second[0].pushed == 0
            assert cursor_after_second >= cursor_after_first

        asyncio.run(scenario())
        assert len(deliveries) == 1
        raw, headers = deliveries[0]
        expected = "sha256=" + hmac.new(
            b"outbound-secret", raw, hashlib.sha256
        ).hexdigest()
        assert headers["X-Closure-Signature"] == expected
        payload = json.loads(raw)
        assert payload["version"] == "closure.supernet/v1"
        assert payload["nonterminal"] is True
        assert payload["turing_complete_assumed"] is False
        assert "source_reverse_index" in payload
    finally:
        runtime.close()


def test_registry_persists_only_secret_environment_name(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    try:
        record = runtime.integrations.create(
            IntegrationCreate(
                name="secret-reference",
                kind=IntegrationKind.WEBHOOK_IN,
                secret_env="CLOSURE_EXTERNAL_SECRET",
            )
        )
        stored = runtime.integration_store.get_integration(record.id)
        assert stored["secret_env"] == "CLOSURE_EXTERNAL_SECRET"
        assert "secret" not in json.dumps(stored["config"]).casefold()
    finally:
        runtime.close()


def test_fastapi_integration_registration_capabilities_and_webhook(tmp_path: Path) -> None:
    config = RuntimeConfig(
        database_path=tmp_path / "api.db",
        inbox_dir=tmp_path / "api-inbox",
        autonomy_enabled=False,
    )
    app = create_app(config)
    with TestClient(app) as client:
        capabilities = client.get("/integrations/capabilities")
        assert capabilities.status_code == 200
        assert capabilities.json()["zero_infinity_role"] == "reciprocal poles"

        created = client.post(
            "/integrations",
            json={"name": "api-inbound", "kind": "WEBHOOK_IN", "config": {}},
        )
        assert created.status_code == 200
        integration_id = created.json()["id"]

        webhook = client.post(
            f"/integrations/{integration_id}/webhook",
            json={
                "version": "closure.supernet/v1",
                "items": [
                    {
                        "external_id": "api-1",
                        "exact_text": "0 ↔ ∞",
                        "source_id": "api-peer",
                    }
                ],
            },
        )
        assert webhook.status_code == 200
        assert webhook.json()["pulled"] == 1
        occurrence = client.get("/occurrences").json()[0]
        assert occurrence["operator_path"][0]["role"] == "reciprocal poles"
