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


class RenormalizationStore:
    """Materialized NRRF781 lens over the canonical Supernet event log."""

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
        CREATE TABLE IF NOT EXISTS renormalization_families (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            parent_family_id TEXT REFERENCES renormalization_families(id),
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            perspective_id TEXT,
            problem_id TEXT,
            cutoff_labels TEXT NOT NULL,
            members TEXT NOT NULL,
            tolerance TEXT NOT NULL,
            universality_source_ids TEXT NOT NULL,
            universality TEXT NOT NULL,
            status TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_renorm_family_event
          ON renormalization_families(integration_event_id);
        CREATE INDEX IF NOT EXISTS idx_renorm_family_parent
          ON renormalization_families(parent_family_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_renorm_family_status
          ON renormalization_families(status, created_at DESC);

        CREATE TABLE IF NOT EXISTS renormalization_schemes (
            id TEXT PRIMARY KEY,
            family_id TEXT NOT NULL REFERENCES renormalization_families(id),
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            scheme_source_ids TEXT NOT NULL,
            evaluation TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_renorm_scheme_family
          ON renormalization_schemes(family_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_renorm_scheme_event
          ON renormalization_schemes(integration_event_id);

        CREATE TABLE IF NOT EXISTS renormalization_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    def create_family(self, row: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._conn.execute(
                """INSERT INTO renormalization_families
                (id,occurrence_id,integration_event_id,parent_family_id,name,authored_by,
                 perspective_id,problem_id,cutoff_labels,members,tolerance,
                 universality_source_ids,universality,status,metadata,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    row["id"],
                    row["occurrence_id"],
                    row["integration_event_id"],
                    row.get("parent_family_id"),
                    row["name"],
                    row["authored_by"],
                    row.get("perspective_id"),
                    row.get("problem_id"),
                    _json(row["cutoff_labels"]),
                    _json(row["members"]),
                    row["tolerance"],
                    _json(row.get("universality_source_ids", [])),
                    _json(row["universality"]),
                    row["status"],
                    _json(row.get("metadata", {})),
                    row.get("created_at", utcnow()),
                ),
            )
            self._conn.commit()
        return self.get_family(row["id"])

    def get_family(self, family_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM renormalization_families WHERE id=?", (family_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Regularized family {family_id} not found")
        return self._decode_family(row)

    def list_families(self, limit: int = 10_000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM renormalization_families ORDER BY created_at DESC,id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [self._decode_family(row) for row in rows]

    @staticmethod
    def _decode_family(row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        for key, default in (
            ("cutoff_labels", []),
            ("members", {}),
            ("universality_source_ids", []),
            ("universality", {}),
            ("metadata", {}),
        ):
            item[key] = _loads(item[key], default)
        return item

    def create_scheme(self, row: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._conn.execute(
                """INSERT INTO renormalization_schemes
                (id,family_id,occurrence_id,integration_event_id,name,authored_by,
                 scheme_source_ids,evaluation,metadata,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (
                    row["id"],
                    row["family_id"],
                    row["occurrence_id"],
                    row["integration_event_id"],
                    row["name"],
                    row["authored_by"],
                    _json(row.get("scheme_source_ids", [])),
                    _json(row["evaluation"]),
                    _json(row.get("metadata", {})),
                    row.get("created_at", utcnow()),
                ),
            )
            self._conn.commit()
        return self.get_scheme(row["id"])

    def get_scheme(self, scheme_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM renormalization_schemes WHERE id=?", (scheme_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Renormalization scheme {scheme_id} not found")
        return self._decode_scheme(row)

    def list_schemes(
        self, limit: int = 10_000, family_id: str | None = None
    ) -> list[dict[str, Any]]:
        if family_id is None:
            rows = self._conn.execute(
                "SELECT * FROM renormalization_schemes ORDER BY created_at DESC,id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                """SELECT * FROM renormalization_schemes
                WHERE family_id=? ORDER BY created_at DESC,id DESC LIMIT ?""",
                (family_id, limit),
            ).fetchall()
        return [self._decode_scheme(row) for row in rows]

    @staticmethod
    def _decode_scheme(row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        item["scheme_source_ids"] = _loads(item["scheme_source_ids"], [])
        item["evaluation"] = _loads(item["evaluation"], {})
        item["metadata"] = _loads(item["metadata"], {})
        return item

    def stats(self) -> dict[str, int]:
        families = int(
            self._conn.execute("SELECT COUNT(*) FROM renormalization_families").fetchone()[0]
        )
        schemes = int(
            self._conn.execute("SELECT COUNT(*) FROM renormalization_schemes").fetchone()[0]
        )
        determined = int(
            self._conn.execute(
                "SELECT COUNT(*) FROM renormalization_families WHERE status='RELATIVE_CLOSURE_DETERMINED'"
            ).fetchone()[0]
        )
        open_families = families - determined
        admissible_schemes = 0
        for row in self._conn.execute(
            "SELECT evaluation FROM renormalization_schemes"
        ).fetchall():
            if bool(_loads(row["evaluation"], {}).get("admissible_scheme")):
                admissible_schemes += 1
        return {
            "families": families,
            "determined_closures": determined,
            "open_universality": open_families,
            "schemes": schemes,
            "admissible_schemes": admissible_schemes,
        }

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO renormalization_state(key,value,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at""",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute(
            "SELECT value FROM renormalization_state WHERE key=?", (key,)
        ).fetchone()
        return default if row is None else _loads(row["value"], default)
