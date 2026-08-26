from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .reopening_models import (
    MoralConnectionCreate,
    OrderEffect,
    OrderedReadingCreate,
    ReopeningFamilyCreate,
    ReopeningProcessCreate,
    ReopeningProcessState,
    ResidueRoundState,
)


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _loads(value: str | None, default: Any) -> Any:
    return default if value is None else json.loads(value)


class ReopeningStore:
    """Persistent NRRF768 forms over canonical source occurrences."""

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
        CREATE TABLE IF NOT EXISTS reopening_families (
            id TEXT PRIMARY KEY,
            problem_id TEXT NOT NULL REFERENCES living_problems(id),
            name TEXT NOT NULL,
            created_by TEXT NOT NULL REFERENCES living_participants(id),
            assumption_occurrence_ids TEXT NOT NULL,
            mode TEXT NOT NULL,
            closure_rules TEXT NOT NULL,
            remaining_star_ids TEXT NOT NULL,
            closure_verified INTEGER NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS reopening_variants (
            id TEXT PRIMARY KEY,
            family_id TEXT NOT NULL REFERENCES reopening_families(id),
            label TEXT NOT NULL,
            held_occurrence_ids TEXT NOT NULL,
            closure_occurrence_ids TEXT NOT NULL,
            order_index INTEGER NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(family_id, order_index)
        );
        CREATE INDEX IF NOT EXISTS idx_reopening_variants_family
            ON reopening_variants(family_id, order_index);

        CREATE TABLE IF NOT EXISTS ordered_readings (
            id TEXT PRIMARY KEY,
            problem_id TEXT NOT NULL REFERENCES living_problems(id),
            participant_id TEXT NOT NULL REFERENCES living_participants(id),
            occurrence_id TEXT NOT NULL REFERENCES occurrences(id),
            held_occurrence_ids TEXT NOT NULL,
            dependency_edges TEXT NOT NULL,
            meaning_key TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_ordered_readings_problem
            ON ordered_readings(problem_id, created_at);
        CREATE TABLE IF NOT EXISTS order_assessments (
            id TEXT PRIMARY KEY,
            left_reading_id TEXT NOT NULL REFERENCES ordered_readings(id),
            right_reading_id TEXT NOT NULL REFERENCES ordered_readings(id),
            same_content INTEGER NOT NULL,
            order_changed INTEGER NOT NULL,
            effect TEXT NOT NULL,
            rationale TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(left_reading_id, right_reading_id)
        );

        CREATE TABLE IF NOT EXISTS reopening_processes (
            id TEXT PRIMARY KEY,
            problem_id TEXT NOT NULL REFERENCES living_problems(id),
            name TEXT NOT NULL,
            created_by TEXT NOT NULL REFERENCES living_participants(id),
            mode TEXT NOT NULL,
            initial_assumption_ids TEXT NOT NULL,
            joint_suspensions TEXT NOT NULL,
            closure_rules TEXT NOT NULL,
            max_rounds INTEGER NOT NULL,
            state TEXT NOT NULL,
            previous_process_id TEXT REFERENCES reopening_processes(id),
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_reopening_process_state
            ON reopening_processes(state, created_at);
        CREATE TABLE IF NOT EXISTS residue_rounds (
            id TEXT PRIMARY KEY,
            process_id TEXT NOT NULL REFERENCES reopening_processes(id),
            round_index INTEGER NOT NULL,
            input_assumption_ids TEXT NOT NULL,
            family_id TEXT NOT NULL REFERENCES reopening_families(id),
            remaining_star_ids TEXT NOT NULL,
            closed INTEGER NOT NULL,
            strictly_reopened INTEGER NOT NULL,
            state TEXT NOT NULL,
            previous_round_id TEXT REFERENCES residue_rounds(id),
            created_at TEXT NOT NULL,
            UNIQUE(process_id, round_index)
        );
        CREATE INDEX IF NOT EXISTS idx_residue_rounds_process
            ON residue_rounds(process_id, round_index);
        CREATE TABLE IF NOT EXISTS residue_moral_connections (
            id TEXT PRIMARY KEY,
            round_id TEXT NOT NULL REFERENCES residue_rounds(id),
            participant_a_id TEXT NOT NULL REFERENCES living_participants(id),
            participant_b_id TEXT NOT NULL REFERENCES living_participants(id),
            understanding_a_ids TEXT NOT NULL,
            understanding_b_ids TEXT NOT NULL,
            residue_ids TEXT NOT NULL,
            agrees_on_residue INTEGER NOT NULL,
            plurality_a_ids TEXT NOT NULL,
            plurality_b_ids TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_residue_moral_connections_round
            ON residue_moral_connections(round_id, created_at);
        CREATE TABLE IF NOT EXISTS reopening_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    def create_family(
        self,
        data: ReopeningFamilyCreate,
        *,
        variants: list[dict[str, Any]],
        remaining_star_ids: list[str],
        closure_verified: bool,
    ) -> dict[str, Any]:
        family_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                "INSERT INTO reopening_families VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    family_id,
                    data.problem_id,
                    data.name,
                    data.created_by,
                    _json(data.assumption_occurrence_ids),
                    str(data.mode),
                    _json([rule.model_dump(mode="json") for rule in data.closure_rules]),
                    _json(remaining_star_ids),
                    int(closure_verified),
                    _json(data.metadata),
                    created_at,
                ),
            )
            for index, variant in enumerate(variants):
                self._conn.execute(
                    "INSERT INTO reopening_variants VALUES(?,?,?,?,?,?,?,?,?)",
                    (
                        str(uuid.uuid4()), family_id, variant["label"],
                        _json(variant["held_occurrence_ids"]),
                        _json(variant["closure_occurrence_ids"]), index,
                        _json(variant.get("metadata") or {}), created_at,
                    ),
                )
            self._conn.commit()
        return self.get_family(family_id)

    def get_family(self, family_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM reopening_families WHERE id=?", (family_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Reopening family {family_id} not found")
        data = dict(row)
        for key, default in (
            ("assumption_occurrence_ids", []), ("closure_rules", []),
            ("remaining_star_ids", []), ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        data["closure_verified"] = bool(data["closure_verified"])
        data["variants"] = self.list_variants(family_id)
        return data

    def list_families(
        self, problem_id: str | None = None, limit: int = 5000
    ) -> list[dict[str, Any]]:
        if problem_id:
            rows = self._conn.execute(
                "SELECT id FROM reopening_families WHERE problem_id=? ORDER BY created_at,id LIMIT ?",
                (problem_id, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT id FROM reopening_families ORDER BY created_at,id LIMIT ?", (limit,)
            ).fetchall()
        return [self.get_family(str(row["id"])) for row in rows]

    def list_variants(self, family_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM reopening_variants WHERE family_id=? ORDER BY order_index,id",
            (family_id,),
        ).fetchall()
        result = []
        for row in rows:
            data = dict(row)
            for key, default in (
                ("held_occurrence_ids", []),
                ("closure_occurrence_ids", []),
                ("metadata", {}),
            ):
                data[key] = _loads(data[key], default)
            result.append(data)
        return result

    def create_ordered_reading(
        self, data: OrderedReadingCreate, occurrence_id: str
    ) -> dict[str, Any]:
        reading_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                "INSERT INTO ordered_readings VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    reading_id, data.problem_id, data.participant_id, occurrence_id,
                    _json(data.held_occurrence_ids), _json(data.dependency_edges),
                    data.meaning_key, _json(data.metadata), utcnow(),
                ),
            )
            self._conn.commit()
        return self.get_ordered_reading(reading_id)

    def get_ordered_reading(self, reading_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM ordered_readings WHERE id=?", (reading_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Ordered reading {reading_id} not found")
        data = dict(row)
        data["held_occurrence_ids"] = _loads(data["held_occurrence_ids"], [])
        data["dependency_edges"] = [
            tuple(edge) for edge in _loads(data["dependency_edges"], [])
        ]
        data["metadata"] = _loads(data["metadata"], {})
        return data

    def list_ordered_readings(
        self, problem_id: str | None = None, limit: int = 5000
    ) -> list[dict[str, Any]]:
        if problem_id:
            rows = self._conn.execute(
                "SELECT id FROM ordered_readings WHERE problem_id=? ORDER BY created_at,id LIMIT ?",
                (problem_id, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT id FROM ordered_readings ORDER BY created_at,id LIMIT ?", (limit,)
            ).fetchall()
        return [self.get_ordered_reading(str(row["id"])) for row in rows]

    def create_order_assessment(
        self,
        left_reading_id: str,
        right_reading_id: str,
        *,
        same_content: bool,
        order_changed: bool,
        effect: OrderEffect,
        rationale: str,
    ) -> tuple[dict[str, Any], bool]:
        left_reading_id, right_reading_id = sorted([left_reading_id, right_reading_id])
        existing = self._conn.execute(
            "SELECT * FROM order_assessments WHERE left_reading_id=? AND right_reading_id=?",
            (left_reading_id, right_reading_id),
        ).fetchone()
        if existing:
            return self._decode_order_assessment(existing), False
        assessment_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                "INSERT INTO order_assessments VALUES(?,?,?,?,?,?,?,?)",
                (
                    assessment_id, left_reading_id, right_reading_id,
                    int(same_content), int(order_changed), str(effect), rationale, utcnow(),
                ),
            )
            self._conn.commit()
        return self.get_order_assessment(assessment_id), True

    def get_order_assessment(self, assessment_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM order_assessments WHERE id=?", (assessment_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Order assessment {assessment_id} not found")
        return self._decode_order_assessment(row)

    @staticmethod
    def _decode_order_assessment(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["same_content"] = bool(data["same_content"])
        data["order_changed"] = bool(data["order_changed"])
        return data

    def list_order_assessments(self, limit: int = 10_000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM order_assessments ORDER BY created_at,id LIMIT ?", (limit,)
        ).fetchall()
        return [self._decode_order_assessment(row) for row in rows]

    def create_process(
        self, data: ReopeningProcessCreate, *, initial_closed_ids: list[str]
    ) -> dict[str, Any]:
        process_id = str(uuid.uuid4())
        metadata = dict(data.metadata)
        metadata["initial_closed_ids"] = initial_closed_ids
        with self._lock:
            self._conn.execute(
                "INSERT INTO reopening_processes VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    process_id, data.problem_id, data.name, data.created_by,
                    str(data.mode), _json(data.initial_assumption_ids),
                    _json(data.joint_suspensions),
                    _json([rule.model_dump(mode="json") for rule in data.closure_rules]),
                    data.max_rounds, str(ReopeningProcessState.ACTIVE),
                    data.previous_process_id, _json(metadata), utcnow(),
                ),
            )
            self._conn.commit()
        return self.get_process(process_id)

    def get_process(self, process_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM reopening_processes WHERE id=?", (process_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Reopening process {process_id} not found")
        data = dict(row)
        for key, default in (
            ("initial_assumption_ids", []), ("joint_suspensions", []),
            ("closure_rules", []), ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    def list_processes(
        self, *, active_only: bool = False, limit: int = 5000
    ) -> list[dict[str, Any]]:
        if active_only:
            rows = self._conn.execute(
                "SELECT id FROM reopening_processes WHERE state=? ORDER BY created_at,id LIMIT ?",
                (str(ReopeningProcessState.ACTIVE), limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT id FROM reopening_processes ORDER BY created_at,id LIMIT ?", (limit,)
            ).fetchall()
        return [self.get_process(str(row["id"])) for row in rows]

    def set_process_state(
        self, process_id: str, state: ReopeningProcessState
    ) -> dict[str, Any]:
        self.get_process(process_id)
        with self._lock:
            self._conn.execute(
                "UPDATE reopening_processes SET state=? WHERE id=?",
                (str(state), process_id),
            )
            self._conn.commit()
        return self.get_process(process_id)

    def create_round(
        self,
        *,
        process_id: str,
        round_index: int,
        input_assumption_ids: list[str],
        family_id: str,
        remaining_star_ids: list[str],
        closed: bool,
        strictly_reopened: bool,
        state: ResidueRoundState,
        previous_round_id: str | None,
    ) -> dict[str, Any]:
        round_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                "INSERT INTO residue_rounds VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    round_id, process_id, round_index, _json(input_assumption_ids),
                    family_id, _json(remaining_star_ids), int(closed),
                    int(strictly_reopened), str(state), previous_round_id, utcnow(),
                ),
            )
            self._conn.commit()
        return self.get_round(round_id)

    def get_round(self, round_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM residue_rounds WHERE id=?", (round_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Residue round {round_id} not found")
        return self._decode_round(row)

    @staticmethod
    def _decode_round(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["input_assumption_ids"] = _loads(data["input_assumption_ids"], [])
        data["remaining_star_ids"] = _loads(data["remaining_star_ids"], [])
        data["closed"] = bool(data["closed"])
        data["strictly_reopened"] = bool(data["strictly_reopened"])
        return data

    def list_rounds(
        self, process_id: str | None = None, limit: int = 10_000
    ) -> list[dict[str, Any]]:
        if process_id:
            rows = self._conn.execute(
                "SELECT * FROM residue_rounds WHERE process_id=? ORDER BY round_index,id LIMIT ?",
                (process_id, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM residue_rounds ORDER BY created_at,id LIMIT ?", (limit,)
            ).fetchall()
        return [self._decode_round(row) for row in rows]

    def latest_round(self, process_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT * FROM residue_rounds WHERE process_id=? ORDER BY round_index DESC,id DESC LIMIT 1",
            (process_id,),
        ).fetchone()
        return self._decode_round(row) if row else None

    def create_moral_connection(
        self,
        data: MoralConnectionCreate,
        *,
        residue_ids: list[str],
        agrees_on_residue: bool,
        plurality_a_ids: list[str],
        plurality_b_ids: list[str],
    ) -> dict[str, Any]:
        connection_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                "INSERT INTO residue_moral_connections VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    connection_id, data.round_id, data.participant_a_id,
                    data.participant_b_id, _json(data.understanding_a_ids),
                    _json(data.understanding_b_ids), _json(residue_ids),
                    int(agrees_on_residue), _json(plurality_a_ids),
                    _json(plurality_b_ids), _json(data.metadata), utcnow(),
                ),
            )
            self._conn.commit()
        return self.get_moral_connection(connection_id)

    def get_moral_connection(self, connection_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM residue_moral_connections WHERE id=?", (connection_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Moral connection {connection_id} not found")
        data = dict(row)
        for key, default in (
            ("understanding_a_ids", []), ("understanding_b_ids", []),
            ("residue_ids", []), ("plurality_a_ids", []),
            ("plurality_b_ids", []), ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        data["agrees_on_residue"] = bool(data["agrees_on_residue"])
        return data

    def list_moral_connections(self, limit: int = 10_000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT id FROM residue_moral_connections ORDER BY created_at,id LIMIT ?", (limit,)
        ).fetchall()
        return [self.get_moral_connection(str(row["id"])) for row in rows]

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute(
            "SELECT value FROM reopening_state WHERE key=?", (key,)
        ).fetchone()
        return _loads(row["value"], default) if row else default

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO reopening_state(key,value,updated_at) VALUES(?,?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def stats(self) -> dict[str, int]:
        tables = {
            "reopening_families": "families",
            "reopening_variants": "variants",
            "ordered_readings": "ordered_readings",
            "order_assessments": "order_assessments",
            "reopening_processes": "processes",
            "residue_rounds": "rounds",
            "residue_moral_connections": "moral_connections",
        }
        result: dict[str, int] = {}
        for table, key in tables.items():
            row = self._conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()
            result[key] = int(row["n"])
        result["active_processes"] = len(
            self.list_processes(active_only=True, limit=100_000)
        )
        return result
