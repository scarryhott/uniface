from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from closure_supernet.config import RuntimeConfig
from closure_supernet.production import Authenticator
from closure_supernet.sqlite_runtime import storage_contract


ROOT = Path(__file__).resolve().parents[1]


def test_production_sqlite_contract_uses_main_database_file(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("CLOSURE_ENVIRONMENT", "production")
    monkeypatch.delenv("CLOSURE_SQLITE_JOURNAL_MODE", raising=False)
    monkeypatch.delenv("CLOSURE_SQLITE_SYNCHRONOUS", raising=False)

    connection = sqlite3.connect(tmp_path / "contract.db")
    try:
        assert connection.execute("PRAGMA journal_mode").fetchone()[0].lower() == "delete"
        # SQLite reports FULL as integer 2.
        assert connection.execute("PRAGMA synchronous").fetchone()[0] == 2
        connection.execute("PRAGMA journal_mode=WAL")
        assert connection.execute("PRAGMA journal_mode").fetchone()[0].lower() == "delete"
        assert storage_contract()["production_main_file_commits"] is True
    finally:
        connection.close()


def test_turing_being_event_survives_abrupt_process_restart(
    tmp_path: Path, monkeypatch
) -> None:
    database = tmp_path / "persistent" / "closure_supernet.db"
    marker = tmp_path / "event-id.txt"
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": str(ROOT),
            "CLOSURE_ENVIRONMENT": "production",
            "CLOSURE_DB_PATH": str(database),
            "CLOSURE_INBOX_DIR": str(tmp_path / "inbox"),
            "CLOSURE_BACKUP_DIR": str(tmp_path / "backups"),
            "CLOSURE_AUTONOMY_ENABLED": "false",
            "CLOSURE_SQLITE_JOURNAL_MODE": "DELETE",
            "CLOSURE_SQLITE_SYNCHRONOUS": "FULL",
            "PERSISTENCE_MARKER": str(marker),
        }
    )
    script = r'''
import asyncio
import os
from pathlib import Path

from closure_supernet.config import RuntimeConfig
from closure_supernet.runtime import ClosureSupernetRuntime
from closure_supernet.turing_being_models import LifeActionWitness, TuringBeingLifeCreate

runtime = ClosureSupernetRuntime(
    RuntimeConfig(
        database_path=Path(os.environ["CLOSURE_DB_PATH"]),
        inbox_dir=Path(os.environ["CLOSURE_INBOX_DIR"]),
        backup_dir=Path(os.environ["CLOSURE_BACKUP_DIR"]),
        autonomy_enabled=False,
        environment="production",
    )
)

async def main() -> None:
    event = await runtime.turing_being.create_life_event(
        TuringBeingLifeCreate(
            name="abrupt production persistence test",
            authored_by="test",
            global_hair_executor="global-hair-0:test",
            local_ball_reactor="local-ball-infinity:test",
            action=LifeActionWitness(
                exact_occurrence="executor opens a restart boundary",
                source_preserved=True,
                admitted=True,
            ),
        )
    )
    Path(os.environ["PERSISTENCE_MARKER"]).write_text(event["id"], encoding="utf-8")

asyncio.run(main())
# Model a platform handoff that does not run application shutdown hooks.
os._exit(0)
'''
    subprocess.run([sys.executable, "-c", script], cwd=ROOT, env=env, check=True)

    event_id = marker.read_text(encoding="utf-8")
    monkeypatch.setenv("CLOSURE_ENVIRONMENT", "production")
    monkeypatch.setenv("CLOSURE_SQLITE_JOURNAL_MODE", "DELETE")
    connection = sqlite3.connect(database)
    try:
        row = connection.execute(
            "SELECT id FROM turing_being_life_events WHERE id=?", (event_id,)
        ).fetchone()
        assert row is not None
        assert row[0] == event_id
        assert connection.execute("PRAGMA journal_mode").fetchone()[0].lower() == "delete"
    finally:
        connection.close()

    # A full runtime reconstruction must read the same materialized life event.
    from closure_supernet.runtime import ClosureSupernetRuntime

    runtime = ClosureSupernetRuntime(
        RuntimeConfig(
            database_path=database,
            inbox_dir=tmp_path / "reopened-inbox",
            backup_dir=tmp_path / "reopened-backups",
            autonomy_enabled=False,
            environment="production",
        )
    )
    try:
        reopened = runtime.turing_being_store.get_life_event(event_id)
        assert reopened["id"] == event_id
        assert reopened["translational_truth_receipt"]["complete"] is False
    finally:
        runtime.close()


def test_owner_api_key_bootstraps_operator_without_duplicate_json(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("CLOSURE_OWNER_API_KEY", "owner-bootstrap-test-key")
    config = RuntimeConfig(
        database_path=tmp_path / "auth.db",
        inbox_dir=tmp_path / "inbox",
        backup_dir=tmp_path / "backups",
        autonomy_enabled=False,
        environment="test",
        auth_mode="api_key",
        auth_api_keys_json="{}",
        session_secret="test-session-secret-that-is-long-enough",
    )
    authenticator = Authenticator(config)
    ready, problems = authenticator.readiness()
    assert ready is True
    assert problems == []
    principal = authenticator.authenticate_api_key("owner-bootstrap-test-key")
    assert principal is not None
    assert principal.subject == "harry"
    assert principal.role == "operator"
    assert principal.participant_id == "harry"
    assert principal.scopes == ("supernet:operator",)
