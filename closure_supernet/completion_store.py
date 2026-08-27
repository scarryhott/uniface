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


class CompletionStore:
    """Materialized NRRF798/799 lens over the canonical Supernet event log."""

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
        CREATE TABLE IF NOT EXISTS translational_completion_systems (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            source_event_id TEXT,
            parent_system_id TEXT,
            perspective_id TEXT,
            problem_id TEXT,
            payload TEXT NOT NULL,
            evaluation TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_completion_systems_event
          ON translational_completion_systems(integration_event_id);
        CREATE INDEX IF NOT EXISTS idx_completion_systems_parent
          ON translational_completion_systems(parent_system_id,created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_completion_systems_created
          ON translational_completion_systems(created_at DESC,id DESC);

        CREATE TABLE IF NOT EXISTS translational_completion_maps (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            source_system_id TEXT NOT NULL,
            target_system_id TEXT NOT NULL,
            mapping TEXT NOT NULL,
            relation_preserving INTEGER NOT NULL,
            induced_class_map TEXT,
            map_mk_commutes INTEGER NOT NULL,
            identity_map INTEGER NOT NULL,
            parent_map_ids TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            source_event_id TEXT,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_completion_maps_source
          ON translational_completion_maps(source_system_id,created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_completion_maps_target
          ON translational_completion_maps(target_system_id,created_at DESC);

        CREATE TABLE IF NOT EXISTS translational_completion_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    def create_system(self, row: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "presentations": row["presentations"],
            "steps": row["steps"],
            "readings": row.get("readings", []),
            "truths": row.get("truths", []),
        }
        columns = [
            "id",
            "occurrence_id",
            "integration_event_id",
            "name",
            "authored_by",
            "source_event_id",
            "parent_system_id",
            "perspective_id",
            "problem_id",
            "payload",
            "evaluation",
            "source_ids",
            "metadata",
            "created_at",
        ]
        values = [
            row["id"],
            row["occurrence_id"],
            row["integration_event_id"],
            row["name"],
            row["authored_by"],
            row.get("source_event_id"),
            row.get("parent_system_id"),
            row.get("perspective_id"),
            row.get("problem_id"),
            _json(payload),
            _json(row["evaluation"]),
            _json(row.get("source_ids", [])),
            _json(row.get("metadata", {})),
            row.get("created_at", utcnow()),
        ]
        with self._lock:
            self._conn.execute(
                f"INSERT INTO translational_completion_systems ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                values,
            )
            self._conn.commit()
        return self.get_system(row["id"])

    def create_map(self, row: dict[str, Any]) -> dict[str, Any]:
        columns = [
            "id",
            "occurrence_id",
            "integration_event_id",
            "source_system_id",
            "target_system_id",
            "mapping",
            "relation_preserving",
            "induced_class_map",
            "map_mk_commutes",
            "identity_map",
            "parent_map_ids",
            "authored_by",
            "source_event_id",
            "metadata",
            "created_at",
        ]
        values = [
            row["id"],
            row["occurrence_id"],
            row["integration_event_id"],
            row["source_system_id"],
            row["target_system_id"],
            _json(row["mapping"]),
            int(bool(row["relation_preserving"])),
            None if row.get("induced_class_map") is None else _json(row["induced_class_map"]),
            int(bool(row["map_mk_commutes"])),
            int(bool(row["identity_map"])),
            _json(row.get("parent_map_ids", [])),
            row["authored_by"],
            row.get("source_event_id"),
            _json(row.get("metadata", {})),
            row.get("created_at", utcnow()),
        ]
        with self._lock:
            self._conn.execute(
                f"INSERT INTO translational_completion_maps ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
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
        payload = _loads(data.pop("payload"), {})
        data.update(payload)
        data["evaluation"] = _loads(data["evaluation"], {})
        data["source_ids"] = _loads(data["source_ids"], [])
        data["metadata"] = _loads(data["metadata"], {})
        return data

    @staticmethod
    def _decode_map(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["mapping"] = _loads(data["mapping"], {})
        data["relation_preserving"] = bool(data["relation_preserving"])
        data["induced_class_map"] = _loads(data["induced_class_map"], None)
        data["map_mk_commutes"] = bool(data["map_mk_commutes"])
        data["identity_map"] = bool(data["identity_map"])
        data["parent_map_ids"] = _loads(data["parent_map_ids"], [])
        data["metadata"] = _loads(data["metadata"], {})
        return data

    def get_system(self, system_id: str) -> dict[str, Any]:
        return self._decode_system(
            self._get("translational_completion_systems", system_id, "Completion system")
        )

    def get_map(self, map_id: str) -> dict[str, Any]:
        return self._decode_map(
            self._get("translational_completion_maps", map_id, "Completion map")
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
            for item_id in self._list_ids("translational_completion_systems", limit)
        ]

    def list_maps(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return [
            self.get_map(item_id)
            for item_id in self._list_ids("translational_completion_maps", limit)
        ]

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO translational_completion_state(key,value,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute(
            "SELECT value FROM translational_completion_state WHERE key=?", (key,)
        ).fetchone()
        return default if row is None else _loads(row["value"], default)

    def stats(self) -> dict[str, int]:
        systems = self.list_systems()
        maps = self.list_maps()
        return {
            "systems": len(systems),
            "presentations": sum(len(item["presentations"]) for item in systems),
            "local_steps": sum(len(item["steps"]) for item in systems),
            "admitted_steps": sum(
                sum(int(step.get("admitted_for_completion", True)) for step in item["steps"])
                for item in systems
            ),
            "completion_classes": sum(
                len(item["evaluation"].get("classes", [])) for item in systems
            ),
            "finite_path_complete": sum(
                int(item["evaluation"].get("every_identification_has_finite_local_path") is True)
                for item in systems
            ),
            "closed_completions": sum(
                int(item["evaluation"].get("completion_closed") is True)
                for item in systems
            ),
            "maps": len(maps),
            "relation_preserving_maps": sum(int(item["relation_preserving"]) for item in maps),
        }
