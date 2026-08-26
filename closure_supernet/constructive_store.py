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


class ConstructiveStore:
    """Materialized NRRF783 views over the canonical Supernet event log."""

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
        CREATE TABLE IF NOT EXISTS constructive_forms (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            name TEXT NOT NULL,
            origin TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            perspective_id TEXT,
            problem_id TEXT,
            source_carrier TEXT NOT NULL,
            presentation_carrier TEXT NOT NULL,
            encode_map TEXT NOT NULL,
            evaluate_map TEXT NOT NULL,
            evaluation TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_constructive_forms_event
          ON constructive_forms(integration_event_id);
        CREATE INDEX IF NOT EXISTS idx_constructive_forms_created
          ON constructive_forms(created_at DESC,id DESC);

        CREATE TABLE IF NOT EXISTS constructive_translations (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            name TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            perspective_id TEXT,
            problem_id TEXT,
            group_data TEXT NOT NULL,
            sites TEXT NOT NULL,
            base_site TEXT NOT NULL,
            levels TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            evaluation TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_constructive_translations_event
          ON constructive_translations(integration_event_id);
        CREATE INDEX IF NOT EXISTS idx_constructive_translations_created
          ON constructive_translations(created_at DESC,id DESC);

        CREATE TABLE IF NOT EXISTS constructive_chart_comparisons (
            id TEXT PRIMARY KEY,
            closure_id TEXT NOT NULL REFERENCES constructive_translations(id),
            occurrence_id TEXT NOT NULL,
            integration_event_id TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            comparison_levels TEXT NOT NULL,
            derived_shift TEXT NOT NULL,
            charts_differ_by_common_shift INTEGER NOT NULL,
            relative_potentials_equal INTEGER NOT NULL,
            closure_equal INTEGER NOT NULL,
            unique_shift INTEGER NOT NULL,
            overlap_forces_equality INTEGER NOT NULL,
            absolute_levels_noncanonical INTEGER NOT NULL,
            source_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_constructive_comparisons_closure
          ON constructive_chart_comparisons(closure_id,created_at DESC);

        CREATE TABLE IF NOT EXISTS constructive_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    def create_form(self, row: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._conn.execute(
                """INSERT INTO constructive_forms(
                    id,occurrence_id,integration_event_id,name,origin,authored_by,
                    perspective_id,problem_id,source_carrier,presentation_carrier,
                    encode_map,evaluate_map,evaluation,source_ids,metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    row["id"],
                    row["occurrence_id"],
                    row["integration_event_id"],
                    row["name"],
                    row["origin"],
                    row["authored_by"],
                    row.get("perspective_id"),
                    row.get("problem_id"),
                    _json(row["source_carrier"]),
                    _json(row["presentation_carrier"]),
                    _json(row["encode"]),
                    _json(row["evaluate"]),
                    _json(row["evaluation"]),
                    _json(row.get("source_ids", [])),
                    _json(row.get("metadata", {})),
                    row.get("created_at", utcnow()),
                ),
            )
            self._conn.commit()
        return self.get_form(row["id"])

    def get_form(self, form_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM constructive_forms WHERE id=?", (form_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Constructive form {form_id} not found")
        return self._decode_form(row)

    def list_forms(self, limit: int = 10_000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT id FROM constructive_forms ORDER BY created_at DESC,id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [self.get_form(str(row["id"])) for row in rows]

    @staticmethod
    def _decode_form(row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        item["source_carrier"] = _loads(item.pop("source_carrier"), [])
        item["presentation_carrier"] = _loads(item.pop("presentation_carrier"), [])
        item["encode"] = _loads(item.pop("encode_map"), {})
        item["evaluate"] = _loads(item.pop("evaluate_map"), {})
        item["evaluation"] = _loads(item["evaluation"], {})
        item["source_ids"] = _loads(item["source_ids"], [])
        item["metadata"] = _loads(item["metadata"], {})
        return item

    def create_translation(self, row: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._conn.execute(
                """INSERT INTO constructive_translations(
                    id,occurrence_id,integration_event_id,name,authored_by,
                    perspective_id,problem_id,group_data,sites,base_site,levels,
                    source_ids,evaluation,metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    row["id"],
                    row["occurrence_id"],
                    row["integration_event_id"],
                    row["name"],
                    row["authored_by"],
                    row.get("perspective_id"),
                    row.get("problem_id"),
                    _json(row["group"]),
                    _json(row["sites"]),
                    row["base_site"],
                    _json(row["levels"]),
                    _json(row.get("source_ids", [])),
                    _json(row["evaluation"]),
                    _json(row.get("metadata", {})),
                    row.get("created_at", utcnow()),
                ),
            )
            self._conn.commit()
        return self.get_translation(row["id"])

    def get_translation(self, closure_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM constructive_translations WHERE id=?", (closure_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Constructive translational closure {closure_id} not found")
        return self._decode_translation(row)

    def list_translations(self, limit: int = 10_000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """SELECT id FROM constructive_translations
            ORDER BY created_at DESC,id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [self.get_translation(str(row["id"])) for row in rows]

    @staticmethod
    def _decode_translation(row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        item["group"] = _loads(item.pop("group_data"), {})
        item["sites"] = _loads(item["sites"], [])
        item["levels"] = _loads(item["levels"], {})
        item["source_ids"] = _loads(item["source_ids"], [])
        item["evaluation"] = _loads(item["evaluation"], {})
        item["metadata"] = _loads(item["metadata"], {})
        return item

    def create_comparison(self, row: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._conn.execute(
                """INSERT INTO constructive_chart_comparisons(
                    id,closure_id,occurrence_id,integration_event_id,authored_by,
                    comparison_levels,derived_shift,charts_differ_by_common_shift,
                    relative_potentials_equal,closure_equal,unique_shift,
                    overlap_forces_equality,absolute_levels_noncanonical,
                    source_ids,metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    row["id"],
                    row["closure_id"],
                    row["occurrence_id"],
                    row["integration_event_id"],
                    row["authored_by"],
                    _json(row["comparison_levels"]),
                    row["derived_shift"],
                    int(row["charts_differ_by_common_shift"]),
                    int(row["relative_potentials_equal"]),
                    int(row["closure_equal"]),
                    int(row["unique_shift"]),
                    int(row["overlap_forces_equality"]),
                    int(row["absolute_levels_noncanonical"]),
                    _json(row.get("source_ids", [])),
                    _json(row.get("metadata", {})),
                    row.get("created_at", utcnow()),
                ),
            )
            self._conn.commit()
        return self.get_comparison(row["id"])

    def get_comparison(self, comparison_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM constructive_chart_comparisons WHERE id=?",
            (comparison_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Constructive comparison {comparison_id} not found")
        return self._decode_comparison(row)

    def list_comparisons(
        self, limit: int = 10_000, closure_id: str | None = None
    ) -> list[dict[str, Any]]:
        if closure_id is None:
            rows = self._conn.execute(
                """SELECT id FROM constructive_chart_comparisons
                ORDER BY created_at DESC,id DESC LIMIT ?""",
                (limit,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                """SELECT id FROM constructive_chart_comparisons
                WHERE closure_id=? ORDER BY created_at DESC,id DESC LIMIT ?""",
                (closure_id, limit),
            ).fetchall()
        return [self.get_comparison(str(row["id"])) for row in rows]

    @staticmethod
    def _decode_comparison(row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        item["comparison_levels"] = _loads(item["comparison_levels"], {})
        item["source_ids"] = _loads(item["source_ids"], [])
        item["metadata"] = _loads(item["metadata"], {})
        for key in (
            "charts_differ_by_common_shift",
            "relative_potentials_equal",
            "closure_equal",
            "unique_shift",
            "overlap_forces_equality",
            "absolute_levels_noncanonical",
        ):
            item[key] = bool(item[key])
        item["classical_choice_required"] = False
        item["excluded_middle_required"] = False
        return item

    def stats(self) -> dict[str, int]:
        forms = int(
            self._conn.execute("SELECT COUNT(*) FROM constructive_forms").fetchone()[0]
        )
        translations = int(
            self._conn.execute(
                "SELECT COUNT(*) FROM constructive_translations"
            ).fetchone()[0]
        )
        comparisons = int(
            self._conn.execute(
                "SELECT COUNT(*) FROM constructive_chart_comparisons"
            ).fetchone()[0]
        )
        closing_forms = 0
        admissible_forms = 0
        for item in self.list_forms(limit=200_000):
            admissible_forms += int(bool(item["evaluation"].get("admissible_form")))
            closing_forms += int(bool(item["evaluation"].get("u3_closes")))
        return {
            "forms": forms,
            "admissible_forms": admissible_forms,
            "closing_forms": closing_forms,
            "translations": translations,
            "comparisons": comparisons,
        }

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO constructive_state(key,value,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET
                value=excluded.value,updated_at=excluded.updated_at""",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute(
            "SELECT value FROM constructive_state WHERE key=?", (key,)
        ).fetchone()
        return default if row is None else _loads(row["value"], default)
