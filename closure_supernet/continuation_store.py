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


class ContinuationStore:
    """Materialized NRRF807 lens over the canonical append-only Supernet field."""

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
        CREATE TABLE IF NOT EXISTS natural_continuation_systems (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            completion_system_id TEXT NOT NULL,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            presentations TEXT NOT NULL,
            step TEXT NOT NULL,
            origin TEXT NOT NULL,
            step_label TEXT NOT NULL,
            continuation_horizon INTEGER NOT NULL,
            turing_being_life_event_id TEXT,
            source_event_id TEXT,
            perspective_id TEXT,
            problem_id TEXT,
            source_ids TEXT NOT NULL,
            evaluation TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_continuation_system_created
          ON natural_continuation_systems(created_at DESC,id DESC);
        CREATE INDEX IF NOT EXISTS idx_continuation_system_turing
          ON natural_continuation_systems(turing_being_life_event_id);

        CREATE TABLE IF NOT EXISTS natural_continuation_maps (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            completion_map_id TEXT NOT NULL,
            source_system_id TEXT NOT NULL,
            target_system_id TEXT NOT NULL,
            mapping TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            source_event_id TEXT,
            evaluation TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_continuation_map_created
          ON natural_continuation_maps(created_at DESC,id DESC);

        CREATE TABLE IF NOT EXISTS natural_continuation_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    def create_system(self, row: dict[str, Any]) -> dict[str, Any]:
        columns = [
            "id",
            "occurrence_id",
            "integration_event_id",
            "completion_system_id",
            "name",
            "authored_by",
            "presentations",
            "step",
            "origin",
            "step_label",
            "continuation_horizon",
            "turing_being_life_event_id",
            "source_event_id",
            "perspective_id",
            "problem_id",
            "source_ids",
            "evaluation",
            "metadata",
            "created_at",
        ]
        values = [
            row["id"],
            row["occurrence_id"],
            row["integration_event_id"],
            row["completion_system_id"],
            row["name"],
            row["authored_by"],
            _json(row["presentations"]),
            _json(row["step"]),
            row["origin"],
            row["step_label"],
            int(row["continuation_horizon"]),
            row.get("turing_being_life_event_id"),
            row.get("source_event_id"),
            row.get("perspective_id"),
            row.get("problem_id"),
            _json(row.get("source_ids", [])),
            _json(row["evaluation"]),
            _json(row.get("metadata", {})),
            row.get("created_at", utcnow()),
        ]
        with self._lock:
            self._conn.execute(
                f"INSERT INTO natural_continuation_systems ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                values,
            )
            self._conn.commit()
        return self.get_system(row["id"])

    def create_map(self, row: dict[str, Any]) -> dict[str, Any]:
        columns = [
            "id",
            "occurrence_id",
            "integration_event_id",
            "completion_map_id",
            "source_system_id",
            "target_system_id",
            "mapping",
            "authored_by",
            "source_event_id",
            "evaluation",
            "metadata",
            "created_at",
        ]
        values = [
            row["id"],
            row["occurrence_id"],
            row["integration_event_id"],
            row["completion_map_id"],
            row["source_system_id"],
            row["target_system_id"],
            _json(row["mapping"]),
            row["authored_by"],
            row.get("source_event_id"),
            _json(row["evaluation"]),
            _json(row.get("metadata", {})),
            row.get("created_at", utcnow()),
        ]
        with self._lock:
            self._conn.execute(
                f"INSERT INTO natural_continuation_maps ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                values,
            )
            self._conn.commit()
        return self.get_map(row["id"])

    def _get(self, table: str, item_id: str, label: str) -> sqlite3.Row:
        row = self._conn.execute(
            f"SELECT * FROM {table} WHERE id=?", (item_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"{label} {item_id} not found")
        return row

    @staticmethod
    def _decode_system(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in (
            ("presentations", []),
            ("step", {}),
            ("source_ids", []),
            ("evaluation", {}),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        data["continuation_horizon"] = int(data["continuation_horizon"])
        return data

    @staticmethod
    def _decode_map(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in (
            ("mapping", {}),
            ("evaluation", {}),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    def get_system(self, system_id: str) -> dict[str, Any]:
        return self._decode_system(
            self._get("natural_continuation_systems", system_id, "continuation system")
        )

    def get_map(self, map_id: str) -> dict[str, Any]:
        return self._decode_map(
            self._get("natural_continuation_maps", map_id, "continuation map")
        )

    def _list_ids(self, table: str, limit: int) -> list[str]:
        rows = self._conn.execute(
            f"SELECT id FROM {table} ORDER BY created_at DESC,id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [str(row["id"]) for row in rows]

    def list_systems(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return [
            self.get_system(item_id)
            for item_id in self._list_ids("natural_continuation_systems", limit)
        ]

    def list_maps(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return [
            self.get_map(item_id)
            for item_id in self._list_ids("natural_continuation_maps", limit)
        ]

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO natural_continuation_state(key,value,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute(
            "SELECT value FROM natural_continuation_state WHERE key=?", (key,)
        ).fetchone()
        return default if row is None else _loads(row["value"], default)

    def stats(self) -> dict[str, int]:
        systems = self.list_systems()
        maps = self.list_maps()
        return {
            "systems": len(systems),
            "maps": len(maps),
            "rule_equals_geometry": sum(
                int(item["evaluation"].get("rule_eq_geometry") is True)
                for item in systems
            ),
            "rule_strictly_inside_geometry": sum(
                int(item["evaluation"].get("rule_eq_geometry") is False)
                for item in systems
            ),
            "linked_turing_being": sum(
                int(item.get("turing_being_life_event_id") is not None)
                for item in systems
            ),
        }
