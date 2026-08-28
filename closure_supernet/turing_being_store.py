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


class TuringBeingStore:
    """Materialized NRRF805 lens over the canonical append-only Supernet field."""

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
        CREATE TABLE IF NOT EXISTS turing_being_life_events (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            reaction_event_id TEXT,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            global_hair_zero TEXT NOT NULL,
            local_ball_infinity TEXT NOT NULL,
            action TEXT NOT NULL,
            reaction TEXT,
            translational_truth_receipt TEXT NOT NULL,
            derived_relations TEXT NOT NULL,
            affected_perspectives TEXT NOT NULL,
            untranslated_residue TEXT NOT NULL,
            reopening_potential TEXT NOT NULL,
            source_event_id TEXT,
            perspective_id TEXT,
            problem_id TEXT,
            source_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_turing_being_event_integration
          ON turing_being_life_events(integration_event_id);
        CREATE INDEX IF NOT EXISTS idx_turing_being_event_updated
          ON turing_being_life_events(updated_at DESC,id DESC);

        CREATE TABLE IF NOT EXISTS turing_being_charts (
            id TEXT PRIMARY KEY,
            life_event_id TEXT NOT NULL,
            handed_system_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            chart TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_turing_being_chart_life
          ON turing_being_charts(life_event_id,created_at DESC,id DESC);

        CREATE TABLE IF NOT EXISTS turing_being_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    def create_life_event(self, row: dict[str, Any]) -> dict[str, Any]:
        columns = [
            "id",
            "occurrence_id",
            "integration_event_id",
            "reaction_event_id",
            "name",
            "authored_by",
            "global_hair_zero",
            "local_ball_infinity",
            "action",
            "reaction",
            "translational_truth_receipt",
            "derived_relations",
            "affected_perspectives",
            "untranslated_residue",
            "reopening_potential",
            "source_event_id",
            "perspective_id",
            "problem_id",
            "source_ids",
            "metadata",
            "created_at",
            "updated_at",
        ]
        values = [
            row["id"],
            row["occurrence_id"],
            row["integration_event_id"],
            row.get("reaction_event_id"),
            row["name"],
            row["authored_by"],
            _json(row["global_hair_zero"]),
            _json(row["local_ball_infinity"]),
            _json(row["action"]),
            None if row.get("reaction") is None else _json(row["reaction"]),
            _json(row["translational_truth_receipt"]),
            _json(row["derived_relations"]),
            _json(row.get("affected_perspectives", [])),
            _json(row.get("untranslated_residue", [])),
            _json(row.get("reopening_potential", [])),
            row.get("source_event_id"),
            row.get("perspective_id"),
            row.get("problem_id"),
            _json(row.get("source_ids", [])),
            _json(row.get("metadata", {})),
            row.get("created_at", utcnow()),
            row.get("updated_at", utcnow()),
        ]
        with self._lock:
            self._conn.execute(
                f"INSERT INTO turing_being_life_events ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                values,
            )
            self._conn.commit()
        return self.get_life_event(row["id"])

    def complete_return(
        self,
        life_event_id: str,
        *,
        reaction_event_id: str,
        reaction: dict[str, Any],
        receipt: dict[str, Any],
        derived_relations: dict[str, Any],
        untranslated_residue: list[str],
        reopening_potential: list[dict[str, Any]],
        source_ids: list[str],
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        with self._lock:
            cursor = self._conn.execute(
                """UPDATE turing_being_life_events
                   SET reaction_event_id=?,reaction=?,translational_truth_receipt=?,
                       derived_relations=?,untranslated_residue=?,reopening_potential=?,
                       source_ids=?,metadata=?,updated_at=?
                   WHERE id=?""",
                (
                    reaction_event_id,
                    _json(reaction),
                    _json(receipt),
                    _json(derived_relations),
                    _json(untranslated_residue),
                    _json(reopening_potential),
                    _json(source_ids),
                    _json(metadata),
                    utcnow(),
                    life_event_id,
                ),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"Turing Being life event {life_event_id} not found")
            self._conn.commit()
        return self.get_life_event(life_event_id)

    def create_chart(self, row: dict[str, Any]) -> dict[str, Any]:
        columns = [
            "id",
            "life_event_id",
            "handed_system_id",
            "integration_event_id",
            "chart",
            "source_ids",
            "metadata",
            "created_at",
        ]
        values = [
            row["id"],
            row["life_event_id"],
            row["handed_system_id"],
            row["integration_event_id"],
            _json(row["chart"]),
            _json(row.get("source_ids", [])),
            _json(row.get("metadata", {})),
            row.get("created_at", utcnow()),
        ]
        with self._lock:
            self._conn.execute(
                f"INSERT INTO turing_being_charts ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                values,
            )
            self._conn.commit()
        return self.get_chart(row["id"])

    def _get(self, table: str, item_id: str, label: str) -> sqlite3.Row:
        row = self._conn.execute(
            f"SELECT * FROM {table} WHERE id=?", (item_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"{label} {item_id} not found")
        return row

    @staticmethod
    def _decode_life_event(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in (
            ("global_hair_zero", {}),
            ("local_ball_infinity", {}),
            ("action", {}),
            ("reaction", None),
            ("translational_truth_receipt", {}),
            ("derived_relations", {}),
            ("affected_perspectives", []),
            ("untranslated_residue", []),
            ("reopening_potential", []),
            ("source_ids", []),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    @staticmethod
    def _decode_chart(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["chart"] = _loads(data["chart"], {})
        data["source_ids"] = _loads(data["source_ids"], [])
        data["metadata"] = _loads(data["metadata"], {})
        return data

    def get_life_event(self, life_event_id: str) -> dict[str, Any]:
        return self._decode_life_event(
            self._get("turing_being_life_events", life_event_id, "Turing Being life event")
        )

    def get_chart(self, chart_id: str) -> dict[str, Any]:
        return self._decode_chart(
            self._get("turing_being_charts", chart_id, "Turing Being chart")
        )

    def _list_ids(self, table: str, order: str, limit: int) -> list[str]:
        rows = self._conn.execute(
            f"SELECT id FROM {table} ORDER BY {order} DESC,id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [str(row["id"]) for row in rows]

    def list_life_events(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return [
            self.get_life_event(item_id)
            for item_id in self._list_ids("turing_being_life_events", "updated_at", limit)
        ]

    def list_charts(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return [
            self.get_chart(item_id)
            for item_id in self._list_ids("turing_being_charts", "created_at", limit)
        ]

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO turing_being_state(key,value,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute(
            "SELECT value FROM turing_being_state WHERE key=?", (key,)
        ).fetchone()
        return default if row is None else _loads(row["value"], default)

    def stats(self) -> dict[str, int]:
        life_events = self.list_life_events()
        charts = self.list_charts()
        return {
            "life_events": len(life_events),
            "translational_truth_complete": sum(
                int(item["translational_truth_receipt"].get("complete") is True)
                for item in life_events
            ),
            "awaiting_reaction": sum(
                int(item["translational_truth_receipt"].get("complete") is not True)
                for item in life_events
            ),
            "internal_external_defined": sum(
                int(item["derived_relations"].get("internal_external_defined") is True)
                for item in life_events
            ),
            "derived_finite_charts": len(charts),
        }
