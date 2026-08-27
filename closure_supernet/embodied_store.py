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


class EmbodiedStore:
    """Materialized eight-sheaf lens over the canonical Supernet event log."""

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
        CREATE TABLE IF NOT EXISTS embodied_sections (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            sheaf TEXT NOT NULL,
            payload TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_embodied_sections_event
          ON embodied_sections(integration_event_id);
        CREATE INDEX IF NOT EXISTS idx_embodied_sections_sheaf
          ON embodied_sections(sheaf,created_at DESC);

        CREATE TABLE IF NOT EXISTS embodied_relations (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            left_section_id TEXT NOT NULL REFERENCES embodied_sections(id),
            right_section_id TEXT NOT NULL REFERENCES embodied_sections(id),
            payload TEXT NOT NULL,
            evaluation TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_embodied_relations_pair
          ON embodied_relations(left_section_id,right_section_id,created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_embodied_relations_event
          ON embodied_relations(integration_event_id);

        CREATE TABLE IF NOT EXISTS embodied_fields (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            payload TEXT NOT NULL,
            evaluation TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_embodied_fields_event
          ON embodied_fields(integration_event_id);
        CREATE INDEX IF NOT EXISTS idx_embodied_fields_created
          ON embodied_fields(created_at DESC,id DESC);

        CREATE TABLE IF NOT EXISTS embodied_sensor_reads (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            field_id TEXT NOT NULL REFERENCES embodied_fields(id),
            sensor_section_id TEXT NOT NULL REFERENCES embodied_sections(id),
            payload TEXT NOT NULL,
            evaluation TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_embodied_sensor_field
          ON embodied_sensor_reads(field_id,created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_embodied_sensor_event
          ON embodied_sensor_reads(integration_event_id);

        CREATE TABLE IF NOT EXISTS embodied_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    def _insert(self, table: str, row: dict[str, Any]) -> dict[str, Any]:
        columns = ["id", "occurrence_id", "integration_event_id", "name", "authored_by"]
        values: list[Any] = [row[column] for column in columns]
        if table == "embodied_sections":
            columns.append("sheaf")
            values.append(row["sheaf"])
        elif table == "embodied_relations":
            columns.extend(["left_section_id", "right_section_id"])
            values.extend([row["left_section_id"], row["right_section_id"]])
        elif table == "embodied_sensor_reads":
            columns.extend(["field_id", "sensor_section_id"])
            values.extend([row["field_id"], row["sensor_section_id"]])
        columns.append("payload")
        values.append(_json(row["payload"]))
        if table != "embodied_sections":
            columns.append("evaluation")
            values.append(_json(row["evaluation"]))
        columns.extend(["source_ids", "metadata", "created_at"])
        values.extend([
            _json(row.get("source_ids", [])),
            _json(row.get("metadata", {})),
            row.get("created_at", utcnow()),
        ])
        placeholders = ",".join("?" for _ in columns)
        with self._lock:
            self._conn.execute(
                f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
                tuple(values),
            )
            self._conn.commit()
        if table == "embodied_sections":
            return self.get_section(row["id"])
        if table == "embodied_relations":
            return self.get_relation(row["id"])
        if table == "embodied_fields":
            return self.get_field(row["id"])
        return self.get_sensor_read(row["id"])

    def create_section(self, row: dict[str, Any]) -> dict[str, Any]:
        return self._insert("embodied_sections", row)

    def create_relation(self, row: dict[str, Any]) -> dict[str, Any]:
        return self._insert("embodied_relations", row)

    def create_field(self, row: dict[str, Any]) -> dict[str, Any]:
        return self._insert("embodied_fields", row)

    def create_sensor_read(self, row: dict[str, Any]) -> dict[str, Any]:
        return self._insert("embodied_sensor_reads", row)

    def _get(self, table: str, item_id: str, label: str) -> sqlite3.Row:
        row = self._conn.execute(f"SELECT * FROM {table} WHERE id=?", (item_id,)).fetchone()
        if row is None:
            raise KeyError(f"{label} {item_id} not found")
        return row

    @staticmethod
    def _decode(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        payload = _loads(data.pop("payload"), {})
        data.update(payload)
        if "evaluation" in data:
            data["evaluation"] = _loads(data["evaluation"], {})
        data["source_ids"] = _loads(data["source_ids"], [])
        data["metadata"] = _loads(data["metadata"], {})
        return data

    def get_section(self, item_id: str) -> dict[str, Any]:
        return self._decode(self._get("embodied_sections", item_id, "Embodied section"))

    def get_relation(self, item_id: str) -> dict[str, Any]:
        return self._decode(self._get("embodied_relations", item_id, "Embodied relation"))

    def get_field(self, item_id: str) -> dict[str, Any]:
        return self._decode(self._get("embodied_fields", item_id, "Embodied field"))

    def get_sensor_read(self, item_id: str) -> dict[str, Any]:
        return self._decode(self._get("embodied_sensor_reads", item_id, "Embodied sensor read"))

    def _list_ids(self, table: str, limit: int) -> list[str]:
        rows = self._conn.execute(
            f"SELECT id FROM {table} ORDER BY created_at DESC,id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [str(row["id"]) for row in rows]

    def list_sections(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return [self.get_section(item_id) for item_id in self._list_ids("embodied_sections", limit)]

    def list_relations(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return [self.get_relation(item_id) for item_id in self._list_ids("embodied_relations", limit)]

    def list_fields(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return [self.get_field(item_id) for item_id in self._list_ids("embodied_fields", limit)]

    def list_sensor_reads(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return [self.get_sensor_read(item_id) for item_id in self._list_ids("embodied_sensor_reads", limit)]

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO embodied_state(key,value,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute("SELECT value FROM embodied_state WHERE key=?", (key,)).fetchone()
        return default if row is None else _loads(row["value"], default)

    def stats(self) -> dict[str, int]:
        sections = self.list_sections()
        relations = self.list_relations()
        fields = self.list_fields()
        reads = self.list_sensor_reads()
        return {
            "sections": len(sections),
            "sheaves_present": len({item["sheaf"] for item in sections}),
            "relations": len(relations),
            "love_admissible_relations": sum(
                int(item["evaluation"]["love_admissible"]) for item in relations
            ),
            "fields": len(fields),
            "all_eight_sheaf_fields": sum(
                int(item["evaluation"]["all_eight_sheaves_present"]) for item in fields
            ),
            "selected_fields": sum(
                int(item["evaluation"]["unique_natural_component"]) for item in fields
            ),
            "sensor_reads": len(reads),
        }
