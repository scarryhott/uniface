from __future__ import annotations

import json
import sqlite3
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _loads(value: str | None, default: Any) -> Any:
    return default if value is None else json.loads(value)


class SelectionStore:
    """Materialized NRRF790 lens over the canonical Supernet event log."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def _init_schema(self) -> None:
        schema = """
        CREATE TABLE IF NOT EXISTS selection_readings (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            field_symbols TEXT NOT NULL,
            admissible_symbols TEXT NOT NULL,
            selected_symbol TEXT,
            source_event_id TEXT,
            selection_scope TEXT NOT NULL,
            perspective_id TEXT,
            problem_id TEXT,
            evaluation TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_selection_readings_event
          ON selection_readings(integration_event_id);
        CREATE INDEX IF NOT EXISTS idx_selection_readings_source_event
          ON selection_readings(source_event_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_selection_readings_created
          ON selection_readings(created_at DESC, id DESC);

        CREATE TABLE IF NOT EXISTS selection_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    def create_reading(self, row: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._conn.execute(
                """INSERT INTO selection_readings(
                    id,occurrence_id,integration_event_id,name,authored_by,
                    field_symbols,admissible_symbols,selected_symbol,source_event_id,
                    selection_scope,perspective_id,problem_id,evaluation,source_ids,
                    metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    row["id"],
                    row["occurrence_id"],
                    row["integration_event_id"],
                    row["name"],
                    row["authored_by"],
                    _json(row["field_symbols"]),
                    _json(row["admissible_symbols"]),
                    row.get("selected_symbol"),
                    row.get("source_event_id"),
                    row["selection_scope"],
                    row.get("perspective_id"),
                    row.get("problem_id"),
                    _json(row["evaluation"]),
                    _json(row.get("source_ids", [])),
                    _json(row.get("metadata", {})),
                    row.get("created_at", utcnow()),
                ),
            )
            self._conn.commit()
        return self.get_reading(row["id"])

    @staticmethod
    def _decode(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in (
            ("field_symbols", []),
            ("admissible_symbols", []),
            ("evaluation", {}),
            ("source_ids", []),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    def get_reading(self, reading_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM selection_readings WHERE id=?", (reading_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Selection reading {reading_id} not found")
        return self._decode(row)

    def list_readings(self, limit: int = 10_000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT id FROM selection_readings ORDER BY created_at DESC,id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [self.get_reading(str(row["id"])) for row in rows]

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO selection_state(key,value,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute(
            "SELECT value FROM selection_state WHERE key=?", (key,)
        ).fetchone()
        return default if row is None else _loads(row["value"], default)

    def stats(self) -> dict[str, int]:
        readings = self.list_readings()
        return {
            "readings": len(readings),
            "empty": sum(
                int(item["evaluation"]["state"] == "EMPTY_TOTAL_ISOLATION")
                for item in readings
            ),
            "open_branching": sum(
                int(item["evaluation"]["state"] == "OPEN_BRANCHING")
                for item in readings
            ),
            "natural_selections": sum(
                int(item["evaluation"]["state"] == "NATURAL_SELECTION")
                for item in readings
            ),
            "forced_isolations": sum(
                int(item["evaluation"]["state"] == "FORCED_ISOLATION")
                for item in readings
            ),
        }
