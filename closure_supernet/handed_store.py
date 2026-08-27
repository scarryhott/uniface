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


class HandedLifeStore:
    """Materialized NRRF800 lens over the canonical Supernet event log."""

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
        CREATE TABLE IF NOT EXISTS handed_life_systems (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            initial_hand TEXT NOT NULL,
            initial_ball_phase INTEGER NOT NULL,
            source_event_id TEXT,
            perspective_id TEXT,
            problem_id TEXT,
            source_ids TEXT NOT NULL,
            evaluation TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_handed_life_systems_event
          ON handed_life_systems(integration_event_id);
        CREATE INDEX IF NOT EXISTS idx_handed_life_systems_created
          ON handed_life_systems(created_at DESC,id DESC);

        CREATE TABLE IF NOT EXISTS handed_life_records (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            kind TEXT NOT NULL,
            system_id TEXT,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            source_event_id TEXT,
            payload TEXT NOT NULL,
            evaluation TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_handed_life_records_event
          ON handed_life_records(integration_event_id);
        CREATE INDEX IF NOT EXISTS idx_handed_life_records_kind
          ON handed_life_records(kind,created_at DESC,id DESC);
        CREATE INDEX IF NOT EXISTS idx_handed_life_records_system
          ON handed_life_records(system_id,created_at DESC,id DESC);

        CREATE TABLE IF NOT EXISTS handed_life_state (
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
            "name",
            "authored_by",
            "initial_hand",
            "initial_ball_phase",
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
            row["name"],
            row["authored_by"],
            row["initial_hand"],
            int(row["initial_ball_phase"]),
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
                f"INSERT INTO handed_life_systems ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                values,
            )
            self._conn.commit()
        return self.get_system(row["id"])

    def create_record(self, row: dict[str, Any]) -> dict[str, Any]:
        columns = [
            "id",
            "occurrence_id",
            "integration_event_id",
            "kind",
            "system_id",
            "name",
            "authored_by",
            "source_event_id",
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
            row["kind"],
            row.get("system_id"),
            row["name"],
            row["authored_by"],
            row.get("source_event_id"),
            _json(row.get("payload", {})),
            _json(row.get("evaluation", {})),
            _json(row.get("source_ids", [])),
            _json(row.get("metadata", {})),
            row.get("created_at", utcnow()),
        ]
        with self._lock:
            self._conn.execute(
                f"INSERT INTO handed_life_records ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                values,
            )
            self._conn.commit()
        return self.get_record(row["id"])

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
        data["source_ids"] = _loads(data["source_ids"], [])
        data["evaluation"] = _loads(data["evaluation"], {})
        data["metadata"] = _loads(data["metadata"], {})
        return data

    @staticmethod
    def _decode_record(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["payload"] = _loads(data["payload"], {})
        data["evaluation"] = _loads(data["evaluation"], {})
        data["source_ids"] = _loads(data["source_ids"], [])
        data["metadata"] = _loads(data["metadata"], {})
        return data

    def get_system(self, system_id: str) -> dict[str, Any]:
        return self._decode_system(
            self._get("handed_life_systems", system_id, "Handed-life system")
        )

    def get_record(self, record_id: str) -> dict[str, Any]:
        return self._decode_record(
            self._get("handed_life_records", record_id, "Handed-life record")
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
            for item_id in self._list_ids("handed_life_systems", limit)
        ]

    def list_records(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return [
            self.get_record(item_id)
            for item_id in self._list_ids("handed_life_records", limit)
        ]

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO handed_life_state(key,value,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute(
            "SELECT value FROM handed_life_state WHERE key=?", (key,)
        ).fetchone()
        return default if row is None else _loads(row["value"], default)

    def stats(self) -> dict[str, int]:
        systems = self.list_systems()
        records = self.list_records()
        return {
            "systems": len(systems),
            "four_ball_one_hair": sum(
                int(item["evaluation"].get("four_ball_one_hair") is True)
                for item in systems
            ),
            "left_gate_traces": sum(
                int(item["evaluation"].get("left_handed_gate_complete") is True)
                for item in systems
            ),
            "records": len(records),
            "motion_traces": sum(int(item["kind"] == "MOTION_TRACE") for item in records),
            "human_relations": sum(int(item["kind"] == "HUMAN_RELATION") for item in records),
            "ball_returns": sum(
                int(item["evaluation"].get("transition_class") == "BALL_RETURN")
                for item in records
            ),
            "hair_returns": sum(
                int(item["evaluation"].get("transition_class") == "HAIR_RETURN")
                for item in records
            ),
        }
