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


class FrameworkStore:
    """Materialized NRRF784/785 lens over the canonical Supernet event log."""

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
        CREATE TABLE IF NOT EXISTS naturality_arenas (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            perspective_id TEXT,
            problem_id TEXT,
            payload TEXT NOT NULL,
            evaluation TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_naturality_arenas_event
          ON naturality_arenas(integration_event_id);
        CREATE INDEX IF NOT EXISTS idx_naturality_arenas_created
          ON naturality_arenas(created_at DESC,id DESC);

        CREATE TABLE IF NOT EXISTS truth_frameworks (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            perspective_id TEXT,
            problem_id TEXT,
            payload TEXT NOT NULL,
            evaluation TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_truth_frameworks_event
          ON truth_frameworks(integration_event_id);
        CREATE INDEX IF NOT EXISTS idx_truth_frameworks_created
          ON truth_frameworks(created_at DESC,id DESC);

        CREATE TABLE IF NOT EXISTS truth_selection_bridges (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            arena_id TEXT NOT NULL REFERENCES naturality_arenas(id),
            framework_id TEXT NOT NULL REFERENCES truth_frameworks(id),
            payload TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_truth_selection_bridges_event
          ON truth_selection_bridges(integration_event_id);
        CREATE INDEX IF NOT EXISTS idx_truth_selection_bridges_pair
          ON truth_selection_bridges(arena_id,framework_id,created_at DESC);

        CREATE TABLE IF NOT EXISTS framework_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    def _insert(self, table: str, row: dict[str, Any], *, bridge: bool = False) -> dict[str, Any]:
        columns = ["id", "occurrence_id", "integration_event_id", "name", "authored_by"]
        values: list[Any] = [row[column] for column in columns]
        if bridge:
            columns.extend(["arena_id", "framework_id"])
            values.extend([row["arena_id"], row["framework_id"]])
        else:
            columns.extend(["perspective_id", "problem_id"])
            values.extend([row.get("perspective_id"), row.get("problem_id")])
        columns.extend(["payload", "source_ids", "metadata", "created_at"])
        values.extend([
            _json(row["payload"]),
            _json(row.get("source_ids", [])),
            _json(row.get("metadata", {})),
            row.get("created_at", utcnow()),
        ])
        if not bridge:
            columns.insert(-3, "evaluation")
            values.insert(-3, _json(row["evaluation"]))
        placeholders = ",".join("?" for _ in columns)
        with self._lock:
            self._conn.execute(
                f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
                tuple(values),
            )
            self._conn.commit()
        if table == "naturality_arenas":
            return self.get_arena(row["id"])
        if table == "truth_frameworks":
            return self.get_framework(row["id"])
        return self.get_bridge(row["id"])

    def create_arena(self, row: dict[str, Any]) -> dict[str, Any]:
        return self._insert("naturality_arenas", row)

    def create_framework(self, row: dict[str, Any]) -> dict[str, Any]:
        return self._insert("truth_frameworks", row)

    def create_bridge(self, row: dict[str, Any]) -> dict[str, Any]:
        return self._insert("truth_selection_bridges", row, bridge=True)

    def _get(self, table: str, item_id: str, label: str) -> sqlite3.Row:
        row = self._conn.execute(f"SELECT * FROM {table} WHERE id=?", (item_id,)).fetchone()
        if row is None:
            raise KeyError(f"{label} {item_id} not found")
        return row

    @staticmethod
    def _decode_materialized(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        payload = _loads(data.pop("payload"), {})
        data.update(payload)
        if "evaluation" in data:
            data["evaluation"] = _loads(data["evaluation"], {})
        data["source_ids"] = _loads(data["source_ids"], [])
        data["metadata"] = _loads(data["metadata"], {})
        return data

    def get_arena(self, arena_id: str) -> dict[str, Any]:
        return self._decode_materialized(self._get("naturality_arenas", arena_id, "Naturality arena"))

    def get_framework(self, framework_id: str) -> dict[str, Any]:
        return self._decode_materialized(self._get("truth_frameworks", framework_id, "Truth framework"))

    def get_bridge(self, bridge_id: str) -> dict[str, Any]:
        return self._decode_materialized(self._get("truth_selection_bridges", bridge_id, "Truth-selection bridge"))

    def _list_ids(self, table: str, limit: int) -> list[str]:
        rows = self._conn.execute(
            f"SELECT id FROM {table} ORDER BY created_at DESC,id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [str(row["id"]) for row in rows]

    def list_arenas(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return [self.get_arena(item_id) for item_id in self._list_ids("naturality_arenas", limit)]

    def list_frameworks(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return [self.get_framework(item_id) for item_id in self._list_ids("truth_frameworks", limit)]

    def list_bridges(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return [self.get_bridge(item_id) for item_id in self._list_ids("truth_selection_bridges", limit)]

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO framework_state(key,value,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute("SELECT value FROM framework_state WHERE key=?", (key,)).fetchone()
        return default if row is None else _loads(row["value"], default)

    def stats(self) -> dict[str, int]:
        arenas = self.list_arenas()
        frameworks = self.list_frameworks()
        bridges = self.list_bridges()
        return {
            "arenas": len(arenas),
            "natural_arenas": sum(int(item["evaluation"]["natural"]) for item in arenas),
            "metric_biased_arenas": sum(
                int(item["evaluation"].get("resource_metric_selector_natural") is False)
                for item in arenas
            ),
            "frameworks": len(frameworks),
            "classical": sum(int(item["evaluation"]["classification"] == "CLASSICAL") for item in frameworks),
            "noncontextual_partial": sum(
                int(item["evaluation"]["classification"] == "NONCONTEXTUAL_PARTIAL")
                for item in frameworks
            ),
            "contextual": sum(int(item["evaluation"]["classification"] == "CONTEXTUAL") for item in frameworks),
            "open_translation_law": sum(
                int(item["evaluation"]["classification"] == "OPEN_TRANSLATIONAL_LAW")
                for item in frameworks
            ),
            "bridges": len(bridges),
            "unified_bridges": sum(int(item["unified"]) for item in bridges),
        }
