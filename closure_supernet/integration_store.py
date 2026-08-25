from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .integration_models import IntegrationCreate


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _loads(value: str | None, default: Any) -> Any:
    if value is None:
        return default
    return json.loads(value)


class IntegrationStore:
    """Persistent registry, cursors, receipts and run history for digital integrations.

    Integration secrets are never stored here. Only the name of the environment
    variable that contains a secret may be persisted.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL")
        self._init_schema()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def _init_schema(self) -> None:
        schema = """
        CREATE TABLE IF NOT EXISTS integrations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            kind TEXT NOT NULL,
            config TEXT NOT NULL,
            secret_env TEXT,
            enabled INTEGER NOT NULL,
            cursor TEXT NOT NULL,
            last_success_at TEXT,
            last_error TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS integration_receipts (
            id TEXT PRIMARY KEY,
            integration_id TEXT NOT NULL,
            direction TEXT NOT NULL,
            external_id TEXT NOT NULL,
            occurrence_id TEXT,
            payload_hash TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(integration_id, direction, external_id)
        );
        CREATE INDEX IF NOT EXISTS idx_integration_receipts_lookup
          ON integration_receipts(integration_id, direction, external_id);

        CREATE TABLE IF NOT EXISTS integration_runs (
            id TEXT PRIMARY KEY,
            integration_id TEXT NOT NULL,
            direction TEXT NOT NULL,
            status TEXT NOT NULL,
            pulled INTEGER NOT NULL,
            pushed INTEGER NOT NULL,
            skipped INTEGER NOT NULL,
            errors INTEGER NOT NULL,
            cursor TEXT NOT NULL,
            message TEXT NOT NULL,
            started_at TEXT NOT NULL,
            finished_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_integration_runs_created
          ON integration_runs(finished_at, integration_id);
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    def create_integration(self, data: IntegrationCreate) -> dict[str, Any]:
        integration_id = str(uuid.uuid4())
        now = utcnow()
        with self._lock:
            try:
                self._conn.execute(
                    """INSERT INTO integrations
                    (id,name,kind,config,secret_env,enabled,cursor,last_success_at,last_error,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        integration_id,
                        data.name,
                        str(data.kind),
                        _json(data.config),
                        data.secret_env,
                        int(data.enabled),
                        _json({}),
                        None,
                        None,
                        now,
                        now,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError(f"Integration name already exists: {data.name}") from exc
            self._conn.commit()
        return self.get_integration(integration_id)

    def get_integration(self, integration_id: str) -> dict[str, Any]:
        row = self._conn.execute("SELECT * FROM integrations WHERE id=?", (integration_id,)).fetchone()
        if not row:
            raise KeyError(f"Integration {integration_id} not found")
        return self._decode_integration(row)

    def list_integrations(self, enabled_only: bool = False) -> list[dict[str, Any]]:
        query = "SELECT * FROM integrations"
        if enabled_only:
            query += " WHERE enabled=1"
        query += " ORDER BY created_at,id"
        return [self._decode_integration(row) for row in self._conn.execute(query).fetchall()]

    def _decode_integration(self, row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["config"] = _loads(data["config"], {})
        data["cursor"] = _loads(data["cursor"], {})
        data["enabled"] = bool(data["enabled"])
        return data

    def set_enabled(self, integration_id: str, enabled: bool) -> dict[str, Any]:
        self.get_integration(integration_id)
        with self._lock:
            self._conn.execute(
                "UPDATE integrations SET enabled=?,updated_at=? WHERE id=?",
                (int(enabled), utcnow(), integration_id),
            )
            self._conn.commit()
        return self.get_integration(integration_id)

    def update_cursor(
        self,
        integration_id: str,
        cursor: dict[str, Any],
        *,
        success: bool,
        error: str | None = None,
    ) -> dict[str, Any]:
        now = utcnow()
        current = self.get_integration(integration_id)
        with self._lock:
            self._conn.execute(
                """UPDATE integrations
                SET cursor=?,last_success_at=?,last_error=?,updated_at=? WHERE id=?""",
                (
                    _json(cursor),
                    now if success else current["last_success_at"],
                    None if success else error,
                    now,
                    integration_id,
                ),
            )
            self._conn.commit()
        return self.get_integration(integration_id)

    def receipt_exists(self, integration_id: str, direction: str, external_id: str) -> bool:
        row = self._conn.execute(
            """SELECT 1 FROM integration_receipts
            WHERE integration_id=? AND direction=? AND external_id=? LIMIT 1""",
            (integration_id, direction, external_id),
        ).fetchone()
        return row is not None

    def record_receipt(
        self,
        integration_id: str,
        direction: str,
        external_id: str,
        payload_hash: str,
        *,
        occurrence_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        receipt_id = str(uuid.uuid4())
        with self._lock:
            try:
                self._conn.execute(
                    "INSERT INTO integration_receipts VALUES(?,?,?,?,?,?,?,?)",
                    (
                        receipt_id,
                        integration_id,
                        direction,
                        external_id,
                        occurrence_id,
                        payload_hash,
                        _json(metadata or {}),
                        utcnow(),
                    ),
                )
            except sqlite3.IntegrityError:
                row = self._conn.execute(
                    """SELECT * FROM integration_receipts
                    WHERE integration_id=? AND direction=? AND external_id=?""",
                    (integration_id, direction, external_id),
                ).fetchone()
                if not row:
                    raise
                return self._decode_receipt(row)
            self._conn.commit()
        row = self._conn.execute("SELECT * FROM integration_receipts WHERE id=?", (receipt_id,)).fetchone()
        assert row is not None
        return self._decode_receipt(row)

    def _decode_receipt(self, row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["metadata"] = _loads(data["metadata"], {})
        return data

    def record_run(
        self,
        integration_id: str,
        direction: str,
        status: str,
        *,
        pulled: int = 0,
        pushed: int = 0,
        skipped: int = 0,
        errors: int = 0,
        cursor: dict[str, Any] | None = None,
        message: str = "",
        started_at: str,
        finished_at: str | None = None,
    ) -> dict[str, Any]:
        run_id = str(uuid.uuid4())
        finished_at = finished_at or utcnow()
        with self._lock:
            self._conn.execute(
                "INSERT INTO integration_runs VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    run_id,
                    integration_id,
                    direction,
                    status,
                    pulled,
                    pushed,
                    skipped,
                    errors,
                    _json(cursor or {}),
                    message,
                    started_at,
                    finished_at,
                ),
            )
            self._conn.commit()
        row = self._conn.execute("SELECT * FROM integration_runs WHERE id=?", (run_id,)).fetchone()
        assert row is not None
        return self._decode_run(row)

    def list_runs(self, limit: int = 500) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM integration_runs ORDER BY finished_at DESC,id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [self._decode_run(row) for row in rows]

    def _decode_run(self, row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["cursor"] = _loads(data["cursor"], {})
        return data

    def stats(self) -> dict[str, int]:
        return {
            table: int(self._conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"])
            for table in ("integrations", "integration_receipts", "integration_runs")
        }
