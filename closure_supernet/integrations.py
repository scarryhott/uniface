from __future__ import annotations

import base64
import fnmatch
import hashlib
import hmac
import ipaddress
import json
import os
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote, urlparse

import httpx

from .config import RuntimeConfig
from .integration_models import (
    ExternalOccurrence,
    IntegrationCapabilities,
    IntegrationCreate,
    IntegrationEnvelope,
    IntegrationKind,
    IntegrationRecord,
    IntegrationRunResult,
)
from .integration_store import IntegrationStore
from .models import OccurrenceCreate
from .store import EventStore


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _stable_external_id(item: ExternalOccurrence) -> str:
    if item.external_id:
        return item.external_id
    basis = "\n".join([item.source_id or "", item.source_location or "", item.exact_text])
    return f"sha256:{hashlib.sha256(basis.encode('utf-8')).hexdigest()}"


def _secret(record: dict[str, Any]) -> str | None:
    secret_env = record.get("secret_env")
    if not secret_env:
        return None
    value = os.getenv(str(secret_env))
    if not value:
        raise RuntimeError(f"Required integration secret environment variable is unset: {secret_env}")
    return value


def _signature(secret: str, payload: bytes) -> str:
    return "sha256=" + hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def _verify_signature(secret: str, payload: bytes, supplied: str | None) -> None:
    if not supplied:
        raise PermissionError("Missing X-Closure-Signature")
    expected = _signature(secret, payload)
    if not hmac.compare_digest(expected, supplied):
        raise PermissionError("Invalid X-Closure-Signature")


def _validate_url(url: str, allow_private_networks: bool) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Integration URL must be an absolute http(s) URL")
    if parsed.username or parsed.password:
        raise ValueError("Credentials must not be embedded in integration URLs")
    host = parsed.hostname.casefold()
    if not allow_private_networks and host in {"localhost", "localhost.localdomain"}:
        raise ValueError("Private integration URLs are disabled")
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = None
    if ip is not None and not allow_private_networks:
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_unspecified:
            raise ValueError("Private integration URLs are disabled")
    return url


class DigitalIntegrationManager:
    """Source-neutral bridges between Closure Supernet and digital systems.

    Pull connectors create immutable source occurrences. Push connectors export
    event batches and the current Black Mirror projection. Integrations never
    auto-upgrade an external assertion into translational truth.
    """

    def __init__(
        self,
        config: RuntimeConfig,
        event_store: EventStore,
        integration_store: IntegrationStore,
        ingest: Callable[[OccurrenceCreate], Awaitable[dict[str, Any]]],
        client_factory: Callable[[], httpx.AsyncClient] | None = None,
    ):
        self.config = config
        self.event_store = event_store
        self.store = integration_store
        self.ingest = ingest
        self._client_factory = client_factory or self._default_client

    def _default_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=self.config.integration_http_timeout_seconds,
            follow_redirects=False,
            headers={"User-Agent": self.config.integration_user_agent},
        )

    def capabilities(self) -> IntegrationCapabilities:
        return IntegrationCapabilities(kinds=list(IntegrationKind))

    def create(self, data: IntegrationCreate) -> IntegrationRecord:
        self._validate_config(data.kind, data.config)
        return IntegrationRecord.model_validate(self.store.create_integration(data))

    def _validate_config(self, kind: IntegrationKind, config: dict[str, Any]) -> None:
        if kind == IntegrationKind.GITHUB_REPOSITORY:
            repository = str(config.get("repository", ""))
            if repository.count("/") != 1 or repository.startswith("/") or repository.endswith("/"):
                raise ValueError("GITHUB_REPOSITORY requires config.repository='owner/name'")
            api_base = str(config.get("api_base", "https://api.github.com"))
            _validate_url(api_base, self.config.integration_allow_private_networks)
        elif kind in {IntegrationKind.HTTP_JSON_FEED, IntegrationKind.WEBHOOK_OUT}:
            _validate_url(str(config.get("url", "")), self.config.integration_allow_private_networks)
        elif kind == IntegrationKind.WEBHOOK_IN:
            return
        else:
            raise ValueError(f"Unsupported integration kind: {kind}")

    async def poll_enabled(self, integration_id: str | None = None) -> list[IntegrationRunResult]:
        records = [self.store.get_integration(integration_id)] if integration_id else self.store.list_integrations(enabled_only=True)
        results: list[IntegrationRunResult] = []
        for record in records:
            kind = IntegrationKind(record["kind"])
            if not record["enabled"] or kind not in {IntegrationKind.GITHUB_REPOSITORY, IntegrationKind.HTTP_JSON_FEED}:
                continue
            results.append(await self._poll_one(record))
        return results

    async def _poll_one(self, record: dict[str, Any]) -> IntegrationRunResult:
        started_at = utcnow()
        try:
            kind = IntegrationKind(record["kind"])
            if kind == IntegrationKind.GITHUB_REPOSITORY:
                pulled, skipped, cursor = await self._pull_github(record)
            elif kind == IntegrationKind.HTTP_JSON_FEED:
                pulled, skipped, cursor = await self._pull_json_feed(record)
            else:
                raise ValueError(f"Integration is not pull-capable: {kind}")
            self.store.update_cursor(record["id"], cursor, success=True)
            run = self.store.record_run(
                record["id"], "PULL", "SUCCESS", pulled=pulled, skipped=skipped, cursor=cursor,
                message="Source occurrences imported without changing their external source", started_at=started_at,
            )
            self.event_store.append_event(
                "INTEGRATION_PULL_COMPLETED", "integration", record["id"],
                {"kind": record["kind"], "pulled": pulled, "skipped": skipped, "cursor": cursor},
            )
            return IntegrationRunResult.model_validate(run)
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            self.store.update_cursor(record["id"], record.get("cursor") or {}, success=False, error=message)
            run = self.store.record_run(
                record["id"], "PULL", "ERROR", errors=1, cursor=record.get("cursor") or {},
                message=message, started_at=started_at,
            )
            self.event_store.append_event(
                "INTEGRATION_PULL_ERROR", "integration", record["id"], {"kind": record["kind"], "error": message}
            )
            return IntegrationRunResult.model_validate(run)

    async def push_enabled(self, projection: dict[str, Any]) -> list[IntegrationRunResult]:
        results: list[IntegrationRunResult] = []
        for record in self.store.list_integrations(enabled_only=True):
            if IntegrationKind(record["kind"]) == IntegrationKind.WEBHOOK_OUT:
                results.append(await self._push_webhook(record, projection))
        return results

    async def ingest_webhook(self, integration_id: str, raw_body: bytes, supplied_signature: str | None) -> dict[str, Any]:
        record = self.store.get_integration(integration_id)
        if IntegrationKind(record["kind"]) != IntegrationKind.WEBHOOK_IN:
            raise ValueError("Integration is not a WEBHOOK_IN connector")
        if not record["enabled"]:
            raise PermissionError("Integration is disabled")
        secret = _secret(record)
        if secret:
            _verify_signature(secret, raw_body, supplied_signature)
        payload = json.loads(raw_body.decode("utf-8"))
        if isinstance(payload, list):
            payload = {"version": "closure.supernet/v1", "items": payload}
        envelope = IntegrationEnvelope.model_validate(payload)
        pulled, skipped = await self._ingest_items(record, envelope.items, direction="INBOUND_WEBHOOK")
        cursor = {"last_received_at": utcnow(), "last_payload_hash": _sha256_bytes(raw_body)}
        self.store.update_cursor(record["id"], cursor, success=True)
        run = self.store.record_run(
            record["id"], "INBOUND_WEBHOOK", "SUCCESS", pulled=pulled, skipped=skipped, cursor=cursor,
            message="Inbound digital occurrences admitted as immutable sources, not as truth claims",
            started_at=cursor["last_received_at"],
        )
        self.event_store.append_event(
            "INTEGRATION_WEBHOOK_INGESTED", "integration", record["id"], {"pulled": pulled, "skipped": skipped}
        )
        return IntegrationRunResult.model_validate(run).model_dump(mode="json")

    async def _ingest_items(self, record: dict[str, Any], items: list[ExternalOccurrence], *, direction: str) -> tuple[int, int]:
        pulled = 0
        skipped = 0
        for item in items[: self.config.integration_max_items_per_cycle]:
            external_id = _stable_external_id(item)
            if self.store.receipt_exists(record["id"], direction, external_id):
                skipped += 1
                continue
            metadata = dict(item.metadata)
            metadata.update({
                "integration_id": record["id"],
                "integration_name": record["name"],
                "integration_kind": record["kind"],
                "external_id": external_id,
                "external_assertion_is_not_truth": True,
            })
            occurrence = await self.ingest(OccurrenceCreate(
                exact_text=item.exact_text,
                source_id=item.source_id or f"integration:{record['name']}",
                source_location=item.source_location,
                source_context=item.source_context,
                metadata=metadata,
            ))
            payload_hash = hashlib.sha256(item.model_dump_json().encode("utf-8")).hexdigest()
            self.store.record_receipt(
                record["id"], direction, external_id, payload_hash, occurrence_id=occurrence["id"],
                metadata={"source_location": item.source_location},
            )
            pulled += 1
        return pulled, skipped

    async def _pull_json_feed(self, record: dict[str, Any]) -> tuple[int, int, dict[str, Any]]:
        config = record["config"]
        url = _validate_url(str(config["url"]), self.config.integration_allow_private_networks)
        headers: dict[str, str] = {}
        cursor = dict(record.get("cursor") or {})
        if cursor.get("etag"):
            headers["If-None-Match"] = str(cursor["etag"])
        if cursor.get("last_modified"):
            headers["If-Modified-Since"] = str(cursor["last_modified"])
        secret = _secret(record)
        if secret:
            headers[str(config.get("auth_header", "Authorization"))] = str(config.get("auth_template", "Bearer {secret}")).format(secret=secret)
        async with self._client_factory() as client:
            response = await client.get(url, headers=headers)
        if response.status_code == 304:
            return 0, 0, cursor
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "jsonl" in content_type or "ndjson" in content_type:
            raw_items = [json.loads(line) for line in response.text.splitlines() if line.strip()]
        else:
            payload = response.json()
            raw_items = payload.get("items", []) if isinstance(payload, dict) else payload
        if not isinstance(raw_items, list):
            raise ValueError("HTTP_JSON_FEED must return a list or {'items': [...]} payload")
        items = [ExternalOccurrence.model_validate(item) for item in raw_items]
        pulled, skipped = await self._ingest_items(record, items, direction="PULL")
        new_cursor = {
            "etag": response.headers.get("etag"),
            "last_modified": response.headers.get("last-modified"),
            "last_polled_at": utcnow(),
        }
        return pulled, skipped, new_cursor

    async def _pull_github(self, record: dict[str, Any]) -> tuple[int, int, dict[str, Any]]:
        config = record["config"]
        repository = str(config["repository"])
        ref = str(config.get("ref", "main"))
        api_base = _validate_url(
            str(config.get("api_base", "https://api.github.com")).rstrip("/"),
            self.config.integration_allow_private_networks,
        )
        include = list(config.get("include", ["**/*.md", "**/*.txt", "**/*.lean", "*.md", "*.txt", "*.lean"]))
        exclude = list(config.get("exclude", [".git/**", "runtime_data/**"]))
        max_file_bytes = int(config.get("max_file_bytes", 1_000_000))
        headers = {"Accept": "application/vnd.github+json"}
        secret = _secret(record)
        if secret:
            headers["Authorization"] = f"Bearer {secret}"
        tree_url = f"{api_base}/repos/{repository}/git/trees/{quote(ref, safe='')}"
        async with self._client_factory() as client:
            response = await client.get(tree_url, params={"recursive": "1"}, headers=headers)
            response.raise_for_status()
            tree_payload = response.json()
            if tree_payload.get("truncated"):
                raise RuntimeError("GitHub recursive tree was truncated; narrow include paths or use a smaller source repository")
            tree_sha = str(tree_payload.get("sha") or ref)
            cursor = dict(record.get("cursor") or {})
            if cursor.get("tree_sha") == tree_sha:
                return 0, 0, cursor
            items: list[ExternalOccurrence] = []
            for entry in tree_payload.get("tree", []):
                if entry.get("type") != "blob":
                    continue
                path = str(entry.get("path", ""))
                if not path or any(fnmatch.fnmatch(path, pattern) for pattern in exclude):
                    continue
                if include and not any(fnmatch.fnmatch(path, pattern) for pattern in include):
                    continue
                if int(entry.get("size") or 0) > max_file_bytes:
                    continue
                blob_sha = str(entry["sha"])
                blob_url = f"{api_base}/repos/{repository}/git/blobs/{blob_sha}"
                blob_response = await client.get(blob_url, headers=headers)
                blob_response.raise_for_status()
                blob_payload = blob_response.json()
                if blob_payload.get("encoding") != "base64":
                    continue
                try:
                    text = base64.b64decode(str(blob_payload.get("content", ""))).decode("utf-8")
                except UnicodeDecodeError:
                    continue
                items.append(ExternalOccurrence(
                    external_id=f"github:{repository}:{path}:{blob_sha}",
                    exact_text=text,
                    source_id=f"github:{repository}",
                    source_location=f"github://{repository}@{tree_sha}/{path}",
                    source_context=f"Imported from GitHub {repository}:{path} at {tree_sha}",
                    metadata={"repository": repository, "ref": ref, "tree_sha": tree_sha, "blob_sha": blob_sha, "path": path},
                ))
        pulled, skipped = await self._ingest_items(record, items, direction="PULL")
        return pulled, skipped, {"tree_sha": tree_sha, "last_polled_at": utcnow()}

    async def _push_webhook(self, record: dict[str, Any], projection: dict[str, Any]) -> IntegrationRunResult:
        started_at = utcnow()
        cursor = dict(record.get("cursor") or {})
        after = int(cursor.get("event_seq", 0))
        config = record["config"]
        batch_size = min(int(config.get("batch_size", 250)), self.config.integration_max_items_per_cycle)
        raw_events = self.event_store.events_after(after, batch_size)
        last_seen_seq = max([after, *(int(event["seq"]) for event in raw_events)])
        excluded_event_types = {"INTEGRATION_PUSH_COMPLETED", "INTEGRATION_PUSH_ERROR"}
        events = [event for event in raw_events if event["event_type"] not in excluded_event_types]
        event_types = {str(value) for value in config.get("event_types", [])}
        if event_types:
            events = [event for event in events if event["event_type"] in event_types]
        if not events and not bool(config.get("send_empty_projection", False)):
            new_cursor = dict(cursor)
            if raw_events:
                new_cursor = {"event_seq": last_seen_seq, "last_pushed_at": utcnow()}
                self.store.update_cursor(record["id"], new_cursor, success=True)
            run = self.store.record_run(
                record["id"], "PUSH", "SUCCESS", skipped=1, cursor=new_cursor,
                message="No new exportable events; connector-local delivery events were not echoed",
                started_at=started_at,
            )
            return IntegrationRunResult.model_validate(run)
        payload = {
            "version": "closure.supernet/v1",
            "integration": {"id": record["id"], "name": record["name"]},
            "events": events,
            "projection": projection,
            "source_reverse_index": projection.get("source_reverse_index", {}),
            "generated_at": utcnow(),
            "nonterminal": True,
            "turing_complete_assumed": False,
        }
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "X-Closure-Protocol": "closure.supernet/v1",
            "X-Closure-Integration": record["id"],
        }
        secret = _secret(record)
        if secret:
            headers["X-Closure-Signature"] = _signature(secret, raw)
        url = _validate_url(str(config["url"]), self.config.integration_allow_private_networks)
        try:
            async with self._client_factory() as client:
                response = await client.post(url, content=raw, headers=headers)
            response.raise_for_status()
            last_seq = last_seen_seq
            new_cursor = {"event_seq": last_seq, "last_pushed_at": utcnow()}
            self.store.update_cursor(record["id"], new_cursor, success=True)
            self.store.record_receipt(
                record["id"], "PUSH", f"event-batch:{after + 1}:{last_seq}", _sha256_bytes(raw),
                metadata={"status_code": response.status_code, "event_count": len(events)},
            )
            run = self.store.record_run(
                record["id"], "PUSH", "SUCCESS", pushed=len(events), cursor=new_cursor,
                message="Events and source-reversible projection exported", started_at=started_at,
            )
            self.event_store.append_event(
                "INTEGRATION_PUSH_COMPLETED", "integration", record["id"], {"events": len(events), "cursor": new_cursor}
            )
            return IntegrationRunResult.model_validate(run)
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            self.store.update_cursor(record["id"], cursor, success=False, error=message)
            run = self.store.record_run(
                record["id"], "PUSH", "ERROR", errors=1, cursor=cursor, message=message, started_at=started_at,
            )
            self.event_store.append_event("INTEGRATION_PUSH_ERROR", "integration", record["id"], {"error": message})
            return IntegrationRunResult.model_validate(run)
