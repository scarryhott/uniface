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


class ProofCompletionStore:
    """Materialized NRRF811 lens over the canonical append-only Supernet field."""

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
        CREATE TABLE IF NOT EXISTS proof_admission_systems (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            presentations TEXT NOT NULL,
            steps TEXT NOT NULL,
            readings TEXT NOT NULL,
            truths TEXT NOT NULL,
            continuation_system_id TEXT,
            turing_being_life_event_id TEXT,
            geometry_completion_system_id TEXT,
            source_event_id TEXT,
            perspective_id TEXT,
            problem_id TEXT,
            source_ids TEXT NOT NULL,
            evaluation TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_proof_system_created
          ON proof_admission_systems(created_at DESC,id DESC);
        CREATE INDEX IF NOT EXISTS idx_proof_system_continuation
          ON proof_admission_systems(continuation_system_id);
        CREATE INDEX IF NOT EXISTS idx_proof_system_turing
          ON proof_admission_systems(turing_being_life_event_id);

        CREATE TABLE IF NOT EXISTS proof_admission_receipts (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            system_id TEXT NOT NULL,
            kind TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            source_event_id TEXT,
            payload TEXT NOT NULL,
            evaluation TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_proof_receipt_created
          ON proof_admission_receipts(created_at DESC,id DESC);
        CREATE INDEX IF NOT EXISTS idx_proof_receipt_system
          ON proof_admission_receipts(system_id,created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_proof_receipt_kind
          ON proof_admission_receipts(kind,created_at DESC);

        CREATE TABLE IF NOT EXISTS proof_admission_state (
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
            "presentations",
            "steps",
            "readings",
            "truths",
            "continuation_system_id",
            "turing_being_life_event_id",
            "geometry_completion_system_id",
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
            _json(row["presentations"]),
            _json(row["steps"]),
            _json(row.get("readings", [])),
            _json(row.get("truths", [])),
            row.get("continuation_system_id"),
            row.get("turing_being_life_event_id"),
            row.get("geometry_completion_system_id"),
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
                f"INSERT INTO proof_admission_systems ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                values,
            )
            self._conn.commit()
        return self.get_system(row["id"])

    def create_receipt(self, row: dict[str, Any]) -> dict[str, Any]:
        columns = [
            "id",
            "occurrence_id",
            "integration_event_id",
            "system_id",
            "kind",
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
            row["system_id"],
            row["kind"],
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
                f"INSERT INTO proof_admission_receipts ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                values,
            )
            self._conn.commit()
        return self.get_receipt(row["id"])

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
            ("steps", []),
            ("readings", []),
            ("truths", []),
            ("source_ids", []),
            ("evaluation", {}),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    @staticmethod
    def _decode_receipt(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in (
            ("payload", {}),
            ("evaluation", {}),
            ("source_ids", []),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    def get_system(self, system_id: str) -> dict[str, Any]:
        return self._decode_system(
            self._get("proof_admission_systems", system_id, "proof system")
        )

    def get_receipt(self, receipt_id: str) -> dict[str, Any]:
        return self._decode_receipt(
            self._get("proof_admission_receipts", receipt_id, "proof receipt")
        )

    def _list_ids(
        self,
        table: str,
        limit: int,
        *,
        where: str = "",
        params: tuple[Any, ...] = (),
    ) -> list[str]:
        clause = f" WHERE {where}" if where else ""
        rows = self._conn.execute(
            f"SELECT id FROM {table}{clause} ORDER BY created_at DESC,id DESC LIMIT ?",
            (*params, limit),
        ).fetchall()
        return [str(row["id"]) for row in rows]

    def list_systems(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return [
            self.get_system(item_id)
            for item_id in self._list_ids("proof_admission_systems", limit)
        ]

    def list_receipts(
        self,
        limit: int = 10_000,
        *,
        system_id: str | None = None,
        kind: str | None = None,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: list[Any] = []
        if system_id is not None:
            conditions.append("system_id=?")
            params.append(system_id)
        if kind is not None:
            conditions.append("kind=?")
            params.append(kind)
        where = " AND ".join(conditions)
        return [
            self.get_receipt(item_id)
            for item_id in self._list_ids(
                "proof_admission_receipts",
                limit,
                where=where,
                params=tuple(params),
            )
        ]

    def find_by_continuation(self, continuation_system_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT id FROM proof_admission_systems WHERE continuation_system_id=? ORDER BY created_at DESC LIMIT 1",
            (continuation_system_id,),
        ).fetchone()
        return None if row is None else self.get_system(str(row["id"]))

    def find_by_turing_being(self, life_event_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT id FROM proof_admission_systems WHERE turing_being_life_event_id=? ORDER BY created_at DESC LIMIT 1",
            (life_event_id,),
        ).fetchone()
        return None if row is None else self.get_system(str(row["id"]))

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO proof_admission_state(key,value,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute(
            "SELECT value FROM proof_admission_state WHERE key=?", (key,)
        ).fetchone()
        return default if row is None else _loads(row["value"], default)

    def stats(self) -> dict[str, int]:
        systems = self.list_systems()
        receipts = self.list_receipts()
        return {
            "systems": len(systems),
            "receipts": len(receipts),
            "derivations": sum(int(item["kind"] == "DERIVATION") for item in receipts),
            "admissions": sum(int(item["kind"] == "ADMISSION") for item in receipts),
            "balances": sum(int(item["kind"] == "BALANCE") for item in receipts),
            "linked_continuations": sum(
                int(item.get("continuation_system_id") is not None) for item in systems
            ),
            "linked_turing_being": sum(
                int(item.get("turing_being_life_event_id") is not None) for item in systems
            ),
            "balance_equals_geometry": sum(
                int(item["evaluation"].get("balance_eq_geometry") is True)
                for item in systems
            ),
            "balance_strictly_inside_geometry": sum(
                int(item["evaluation"].get("balance_eq_geometry") is False)
                for item in systems
            ),
        }
