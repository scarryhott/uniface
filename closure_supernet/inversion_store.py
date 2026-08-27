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


class InversionStore:
    """Materialized NRRF795/796 lens over the canonical Supernet event log."""

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
        CREATE TABLE IF NOT EXISTS self_limit_relations (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            source_event_id TEXT,
            perspective_id TEXT,
            problem_id TEXT,
            payload TEXT NOT NULL,
            evaluation TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_self_limit_relations_event
          ON self_limit_relations(integration_event_id);
        CREATE INDEX IF NOT EXISTS idx_self_limit_relations_created
          ON self_limit_relations(created_at DESC,id DESC);

        CREATE TABLE IF NOT EXISTS hair_constructions (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            kind TEXT NOT NULL,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            source_event_id TEXT,
            payload TEXT NOT NULL,
            evaluation TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_hair_constructions_event
          ON hair_constructions(integration_event_id);
        CREATE INDEX IF NOT EXISTS idx_hair_constructions_kind
          ON hair_constructions(kind,created_at DESC,id DESC);

        CREATE TABLE IF NOT EXISTS inversion_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    def create_relation(self, row: dict[str, Any]) -> dict[str, Any]:
        columns = [
            "id",
            "occurrence_id",
            "integration_event_id",
            "name",
            "authored_by",
            "source_event_id",
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
            row.get("perspective_id"),
            row.get("problem_id"),
            _json(row["payload"]),
            _json(row["evaluation"]),
            _json(row.get("source_ids", [])),
            _json(row.get("metadata", {})),
            row.get("created_at", utcnow()),
        ]
        with self._lock:
            self._conn.execute(
                f"INSERT INTO self_limit_relations ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                values,
            )
            self._conn.commit()
        return self.get_relation(row["id"])

    def create_construction(self, row: dict[str, Any]) -> dict[str, Any]:
        columns = [
            "id",
            "occurrence_id",
            "integration_event_id",
            "kind",
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
            row["name"],
            row["authored_by"],
            row.get("source_event_id"),
            _json(row["payload"]),
            _json(row["evaluation"]),
            _json(row.get("source_ids", [])),
            _json(row.get("metadata", {})),
            row.get("created_at", utcnow()),
        ]
        with self._lock:
            self._conn.execute(
                f"INSERT INTO hair_constructions ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                values,
            )
            self._conn.commit()
        return self.get_construction(row["id"])

    def _get(self, table: str, item_id: str, label: str) -> sqlite3.Row:
        row = self._conn.execute(
            f"SELECT * FROM {table} WHERE id=?", (item_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"{label} {item_id} not found")
        return row

    @staticmethod
    def _decode(row: sqlite3.Row, *, construction: bool = False) -> dict[str, Any]:
        data = dict(row)
        payload = _loads(data.pop("payload"), {})
        if construction:
            data["payload"] = payload
        else:
            data.update(payload)
        data["evaluation"] = _loads(data["evaluation"], {})
        data["source_ids"] = _loads(data["source_ids"], [])
        data["metadata"] = _loads(data["metadata"], {})
        return data

    def get_relation(self, relation_id: str) -> dict[str, Any]:
        return self._decode(
            self._get("self_limit_relations", relation_id, "Self-limit relation")
        )

    def get_construction(self, construction_id: str) -> dict[str, Any]:
        return self._decode(
            self._get("hair_constructions", construction_id, "Hair construction"),
            construction=True,
        )

    def _list_ids(self, table: str, limit: int) -> list[str]:
        rows = self._conn.execute(
            f"SELECT id FROM {table} ORDER BY created_at DESC,id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [str(row["id"]) for row in rows]

    def list_relations(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return [
            self.get_relation(item_id)
            for item_id in self._list_ids("self_limit_relations", limit)
        ]

    def list_constructions(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return [
            self.get_construction(item_id)
            for item_id in self._list_ids("hair_constructions", limit)
        ]

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO inversion_state(key,value,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute(
            "SELECT value FROM inversion_state WHERE key=?", (key,)
        ).fetchone()
        return default if row is None else _loads(row["value"], default)

    def stats(self) -> dict[str, int]:
        relations = self.list_relations()
        constructions = self.list_constructions()
        by_kind: dict[str, int] = {}
        for item in constructions:
            by_kind[item["kind"]] = by_kind.get(item["kind"], 0) + 1
        return {
            "relations": len(relations),
            "involutive": sum(
                int(item["evaluation"].get("return_inversion_involutive") is True)
                for item in relations
            ),
            "self_limit_exact": sum(
                int(item["evaluation"].get("self_limit_exact") is True)
                for item in relations
            ),
            "neutral_nonzero": sum(
                int(item["evaluation"].get("neutral_nonzero") is True)
                for item in relations
            ),
            "constructions": len(constructions),
            "entanglement": by_kind.get("ENTANGLEMENT_ORDER_DEFECT", 0),
            "superposition": by_kind.get("SUPERPOSITION_HAIR_SUM", 0),
            "singularity": by_kind.get("SINGULARITY_SEAM_HAIR", 0),
            "demon": by_kind.get("DEMON_NEUTRAL_NO_GAIN", 0),
        }
