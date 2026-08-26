from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from closure_supernet.api_production import create_app
from closure_supernet.config import RuntimeConfig


def production_config(tmp_path: Path, **overrides) -> RuntimeConfig:
    values = {
        "database_path": tmp_path / "closure.db",
        "inbox_dir": tmp_path / "inbox",
        "backup_dir": tmp_path / "backups",
        "autonomy_enabled": False,
        "environment": "test",
        "public_development_mode": False,
        "auth_mode": "api_key",
        "auth_api_keys_json": json.dumps(
            {
                "member-key": {
                    "subject": "member-user",
                    "role": "member",
                    "participant_id": "participant-member",
                },
                "operator-key": {
                    "subject": "operator-user",
                    "role": "operator",
                    "scopes": ["*"],
                },
            }
        ),
        "session_secret": "test-session-secret-that-is-long-enough",
        "trusted_hosts": ("testserver",),
        "cors_origins": ("https://client.example",),
        "rate_limit_read_per_minute": 1000,
        "rate_limit_write_per_minute": 1000,
    }
    values.update(overrides)
    return RuntimeConfig(**values)


def test_anonymous_read_and_authenticated_write(tmp_path: Path) -> None:
    app = create_app(production_config(tmp_path))
    with TestClient(app, base_url="https://testserver") as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.headers["x-content-type-options"] == "nosniff"
        denied = client.post(
            "/occurrences",
            json={"exact_text": "A source that should require a member."},
        )
        assert denied.status_code == 401
        created = client.post(
            "/occurrences",
            headers={"X-Closure-API-Key": "member-key"},
            json={"exact_text": "An authenticated production source."},
        )
        assert created.status_code == 200


def test_member_cannot_operate_runtime_but_operator_can(tmp_path: Path) -> None:
    app = create_app(production_config(tmp_path))
    with TestClient(app, base_url="https://testserver") as client:
        member = client.post(
            "/runtime/cycle", headers={"X-Closure-API-Key": "member-key"}
        )
        assert member.status_code == 403
        operator = client.post(
            "/runtime/cycle", headers={"X-Closure-API-Key": "operator-key"}
        )
        assert operator.status_code == 200
        events = client.get("/events").json()
        assert any(event["event_type"] == "PRODUCTION_REQUEST" for event in events)


def test_browser_session_cookie_reuses_api_key_identity(tmp_path: Path) -> None:
    app = create_app(production_config(tmp_path))
    with TestClient(app, base_url="https://testserver") as client:
        login = client.post("/auth/login", json={"api_key": "member-key"})
        assert login.status_code == 200
        session = client.get("/auth/session").json()
        assert session["principal"]["subject"] == "member-user"
        created = client.post(
            "/occurrences", json={"exact_text": "Cookie-authenticated source."}
        )
        assert created.status_code == 200
        assert client.post("/auth/logout").status_code == 200
        assert client.post(
            "/occurrences", json={"exact_text": "No longer authenticated."}
        ).status_code == 401


def test_member_cannot_claim_another_author(tmp_path: Path) -> None:
    app = create_app(production_config(tmp_path))
    with TestClient(app, base_url="https://testserver") as client:
        response = client.post(
            "/network/problems",
            headers={"X-Closure-API-Key": "member-key"},
            json={
                "title": "Authorship boundary",
                "exact_text": "The request attempts to claim another source.",
                "situations": ["A production author field is present."],
                "created_by": "someone-else",
            },
        )
        assert response.status_code == 403
        assert "authenticated participant" in response.json()["detail"]


def test_consistent_database_backup(tmp_path: Path) -> None:
    app = create_app(production_config(tmp_path))
    with TestClient(app, base_url="https://testserver") as client:
        client.post(
            "/occurrences",
            headers={"X-Closure-API-Key": "member-key"},
            json={"exact_text": "Source preserved before snapshot."},
        )
        backup = client.post(
            "/admin/backups",
            headers={"X-Closure-API-Key": "operator-key"},
            json={"label": "test"},
        )
        assert backup.status_code == 200
        assert Path(backup.json()["backup"]).exists()
        listed = client.get(
            "/admin/backups", headers={"X-Closure-API-Key": "operator-key"}
        )
        assert listed.status_code == 200
        assert listed.json()


def test_readiness_requires_production_auth_material(tmp_path: Path) -> None:
    configured = create_app(production_config(tmp_path / "configured"))
    with TestClient(configured, base_url="https://testserver") as client:
        assert client.get("/readyz").status_code == 200

    missing = production_config(
        tmp_path / "missing",
        auth_api_keys_json="{}",
        session_secret=None,
    )
    app = create_app(missing)
    with TestClient(app, base_url="https://testserver") as client:
        response = client.get("/readyz")
        assert response.status_code == 503
        assert response.json()["problems"]


def test_websocket_requires_member_identity(tmp_path: Path) -> None:
    app = create_app(production_config(tmp_path))
    with TestClient(app, base_url="https://testserver") as client:
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/ws/events"):
                pass
        client.post(
            "/occurrences",
            headers={"X-Closure-API-Key": "member-key"},
            json={"exact_text": "Event available to authenticated websocket."},
        )
        with client.websocket_connect(
            "/ws/events", headers={"X-Closure-API-Key": "member-key"}
        ) as websocket:
            event = websocket.receive_json()
            assert "event_type" in event


def test_open_development_mode_remains_nonbreaking(tmp_path: Path) -> None:
    config = production_config(
        tmp_path,
        environment="development",
        auth_mode="open",
        auth_api_keys_json="{}",
        session_secret=None,
    )
    app = create_app(config)
    with TestClient(app) as client:
        response = client.post(
            "/occurrences", json={"exact_text": "Open local development source."}
        )
        assert response.status_code == 200


def test_write_rate_limit_is_enforced(tmp_path: Path) -> None:
    app = create_app(
        production_config(tmp_path, rate_limit_write_per_minute=1)
    )
    with TestClient(app, base_url="https://testserver") as client:
        headers = {"X-Closure-API-Key": "member-key"}
        assert client.post(
            "/occurrences", headers=headers, json={"exact_text": "First write."}
        ).status_code == 200
        limited = client.post(
            "/occurrences", headers=headers, json={"exact_text": "Second write."}
        )
        assert limited.status_code == 429
