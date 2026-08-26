from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .equality_models import (
    EqualityChartCreate,
    EqualityContextCreate,
    EqualityDecisionCreate,
    RelativeEqualityCreate,
    ReturnCoherenceCreate,
)


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _loads(value: str | None, default: Any) -> Any:
    return default if value is None else json.loads(value)


class RelativeEqualityStore:
    """Append-only store for context-indexed relative equality.

    TranslationEvents remain the directed live primitive. This store records the
    additional reversible witness, return-coherence, context, chart and decision
    data required before two relative forms can be admitted as equal at a scope.
    """

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
        CREATE TABLE IF NOT EXISTS equality_contexts (
            id TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            exact_source_ids TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            participant_ids TEXT NOT NULL,
            perspective_ids TEXT NOT NULL,
            frame_and_scope TEXT NOT NULL,
            predecessor_context_id TEXT REFERENCES equality_contexts(id),
            reopening_translation_id TEXT,
            external_key TEXT UNIQUE,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_equality_contexts_created
            ON equality_contexts(created_at,id);

        CREATE TABLE IF NOT EXISTS relative_equality_witnesses (
            id TEXT PRIMARY KEY,
            context_id TEXT NOT NULL REFERENCES equality_contexts(id),
            left_form TEXT NOT NULL,
            right_form TEXT NOT NULL,
            forward_translation_id TEXT NOT NULL,
            reverse_translation_id TEXT,
            exact_source_ids TEXT NOT NULL,
            invariant TEXT NOT NULL,
            residue TEXT NOT NULL,
            return_form TEXT,
            reopening_conditions TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            external_key TEXT UNIQUE,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_equality_witness_context
            ON relative_equality_witnesses(context_id,created_at,id);

        CREATE TABLE IF NOT EXISTS relative_equality_decisions (
            id TEXT PRIMARY KEY,
            witness_id TEXT NOT NULL REFERENCES relative_equality_witnesses(id),
            verdict TEXT NOT NULL,
            reason TEXT NOT NULL,
            decided_by TEXT NOT NULL,
            scope TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_equality_decisions_witness
            ON relative_equality_decisions(witness_id,created_at,id);

        CREATE TABLE IF NOT EXISTS return_coherences (
            id TEXT PRIMARY KEY,
            witness_id TEXT NOT NULL REFERENCES relative_equality_witnesses(id),
            side TEXT NOT NULL,
            path_translation_ids TEXT NOT NULL,
            return_form TEXT NOT NULL,
            exact_source_ids TEXT NOT NULL,
            preserved TEXT NOT NULL,
            residue TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            external_key TEXT UNIQUE,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(witness_id,side)
        );

        CREATE TABLE IF NOT EXISTS return_coherence_decisions (
            id TEXT PRIMARY KEY,
            coherence_id TEXT NOT NULL REFERENCES return_coherences(id),
            verdict TEXT NOT NULL,
            reason TEXT NOT NULL,
            decided_by TEXT NOT NULL,
            scope TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_coherence_decisions
            ON return_coherence_decisions(coherence_id,created_at,id);

        CREATE TABLE IF NOT EXISTS equality_charts (
            id TEXT PRIMARY KEY,
            context_id TEXT REFERENCES equality_contexts(id),
            name TEXT NOT NULL,
            exact_source_ids TEXT NOT NULL,
            carrier_context TEXT NOT NULL,
            generator TEXT NOT NULL,
            inverse_reading TEXT NOT NULL,
            invariant TEXT NOT NULL,
            residue TEXT NOT NULL,
            return_form TEXT NOT NULL,
            reopening TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_equality_charts_context
            ON equality_charts(context_id,created_at,id);

        CREATE TABLE IF NOT EXISTS equality_runtime_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    def create_context(self, data: EqualityContextCreate) -> tuple[dict[str, Any], bool]:
        if data.external_key:
            existing = self.get_context_by_external_key(data.external_key)
            if existing is not None:
                return existing, False
        context_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                """INSERT INTO equality_contexts(
                    id,label,exact_source_ids,authored_by,participant_ids,
                    perspective_ids,frame_and_scope,predecessor_context_id,
                    reopening_translation_id,external_key,metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    context_id,
                    data.label,
                    _json(data.exact_source_ids),
                    data.authored_by,
                    _json(data.participant_ids),
                    _json(data.perspective_ids),
                    data.frame_and_scope,
                    data.predecessor_context_id,
                    data.reopening_translation_id,
                    data.external_key,
                    _json(data.metadata),
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_context(context_id), True

    def get_context_by_external_key(self, external_key: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT id FROM equality_contexts WHERE external_key=?", (external_key,)
        ).fetchone()
        return None if row is None else self.get_context(str(row["id"]))

    def get_context(self, context_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM equality_contexts WHERE id=?", (context_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Equality context {context_id} not found")
        return self._decode_context(row)

    def list_contexts(self, limit: int = 10_000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM equality_contexts ORDER BY created_at,id LIMIT ?",
            (limit,),
        ).fetchall()
        return [self._decode_context(row) for row in rows]

    def create_witness(self, data: RelativeEqualityCreate) -> tuple[dict[str, Any], bool]:
        if data.external_key:
            existing = self.get_witness_by_external_key(data.external_key)
            if existing is not None:
                return existing, False
        witness_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                """INSERT INTO relative_equality_witnesses(
                    id,context_id,left_form,right_form,forward_translation_id,
                    reverse_translation_id,exact_source_ids,invariant,residue,
                    return_form,reopening_conditions,authored_by,external_key,
                    metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    witness_id,
                    data.context_id,
                    _json(data.left_form.model_dump(mode="json")),
                    _json(data.right_form.model_dump(mode="json")),
                    data.forward_translation_id,
                    data.reverse_translation_id,
                    _json(data.exact_source_ids),
                    _json(data.invariant),
                    _json(data.residue),
                    None if data.return_form is None else _json(data.return_form.model_dump(mode="json")),
                    _json(data.reopening_conditions),
                    data.authored_by,
                    data.external_key,
                    _json(data.metadata),
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_witness(witness_id), True

    def get_witness_by_external_key(self, external_key: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT id FROM relative_equality_witnesses WHERE external_key=?",
            (external_key,),
        ).fetchone()
        return None if row is None else self.get_witness(str(row["id"]))

    def get_witness(self, witness_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM relative_equality_witnesses WHERE id=?", (witness_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Relative equality witness {witness_id} not found")
        return self._decode_witness(row)

    def list_witnesses(
        self, context_id: str | None = None, limit: int = 100_000
    ) -> list[dict[str, Any]]:
        if context_id is None:
            rows = self._conn.execute(
                "SELECT * FROM relative_equality_witnesses ORDER BY created_at,id LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                """SELECT * FROM relative_equality_witnesses
                WHERE context_id=? ORDER BY created_at,id LIMIT ?""",
                (context_id, limit),
            ).fetchall()
        return [self._decode_witness(row) for row in rows]

    def append_witness_decision(
        self, witness_id: str, data: EqualityDecisionCreate
    ) -> dict[str, Any]:
        self.get_witness(witness_id)
        decision_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                """INSERT INTO relative_equality_decisions(
                    id,witness_id,verdict,reason,decided_by,scope,metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?)""",
                (
                    decision_id,
                    witness_id,
                    str(data.verdict),
                    data.reason,
                    data.decided_by,
                    data.scope,
                    _json(data.metadata),
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_witness_decision(decision_id)

    def get_witness_decision(self, decision_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM relative_equality_decisions WHERE id=?", (decision_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Equality decision {decision_id} not found")
        return self._decode_witness_decision(row)

    def list_witness_decisions(self, witness_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """SELECT * FROM relative_equality_decisions WHERE witness_id=?
            ORDER BY created_at,id""",
            (witness_id,),
        ).fetchall()
        return [self._decode_witness_decision(row) for row in rows]

    def create_coherence(self, data: ReturnCoherenceCreate) -> tuple[dict[str, Any], bool]:
        if data.external_key:
            existing = self.get_coherence_by_external_key(data.external_key)
            if existing is not None:
                return existing, False
        existing = self._conn.execute(
            "SELECT id FROM return_coherences WHERE witness_id=? AND side=?",
            (data.witness_id, str(data.side)),
        ).fetchone()
        if existing is not None:
            return self.get_coherence(str(existing["id"])), False
        coherence_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                """INSERT INTO return_coherences(
                    id,witness_id,side,path_translation_ids,return_form,
                    exact_source_ids,preserved,residue,authored_by,external_key,
                    metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    coherence_id,
                    data.witness_id,
                    str(data.side),
                    _json(data.path_translation_ids),
                    _json(data.return_form.model_dump(mode="json")),
                    _json(data.exact_source_ids),
                    _json(data.preserved),
                    _json(data.residue),
                    data.authored_by,
                    data.external_key,
                    _json(data.metadata),
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_coherence(coherence_id), True

    def get_coherence_by_external_key(self, external_key: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT id FROM return_coherences WHERE external_key=?", (external_key,)
        ).fetchone()
        return None if row is None else self.get_coherence(str(row["id"]))

    def get_coherence(self, coherence_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM return_coherences WHERE id=?", (coherence_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Return coherence {coherence_id} not found")
        return self._decode_coherence(row)

    def list_coherences(
        self, witness_id: str | None = None, limit: int = 100_000
    ) -> list[dict[str, Any]]:
        if witness_id is None:
            rows = self._conn.execute(
                "SELECT * FROM return_coherences ORDER BY created_at,id LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                """SELECT * FROM return_coherences WHERE witness_id=?
                ORDER BY created_at,id LIMIT ?""",
                (witness_id, limit),
            ).fetchall()
        return [self._decode_coherence(row) for row in rows]

    def append_coherence_decision(
        self, coherence_id: str, data: EqualityDecisionCreate
    ) -> dict[str, Any]:
        self.get_coherence(coherence_id)
        decision_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                """INSERT INTO return_coherence_decisions(
                    id,coherence_id,verdict,reason,decided_by,scope,metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?)""",
                (
                    decision_id,
                    coherence_id,
                    str(data.verdict),
                    data.reason,
                    data.decided_by,
                    data.scope,
                    _json(data.metadata),
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_coherence_decision(decision_id)

    def get_coherence_decision(self, decision_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM return_coherence_decisions WHERE id=?", (decision_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Coherence decision {decision_id} not found")
        return self._decode_coherence_decision(row)

    def list_coherence_decisions(self, coherence_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """SELECT * FROM return_coherence_decisions WHERE coherence_id=?
            ORDER BY created_at,id""",
            (coherence_id,),
        ).fetchall()
        return [self._decode_coherence_decision(row) for row in rows]

    def create_chart(self, data: EqualityChartCreate) -> dict[str, Any]:
        chart_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                """INSERT INTO equality_charts(
                    id,context_id,name,exact_source_ids,carrier_context,generator,
                    inverse_reading,invariant,residue,return_form,reopening,
                    authored_by,metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    chart_id,
                    data.context_id,
                    data.name,
                    _json(data.exact_source_ids),
                    data.carrier_context,
                    data.generator,
                    data.inverse_reading,
                    _json(data.invariant),
                    _json(data.residue),
                    data.return_form,
                    data.reopening,
                    data.authored_by,
                    _json(data.metadata),
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_chart(chart_id)

    def get_chart(self, chart_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM equality_charts WHERE id=?", (chart_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Equality chart {chart_id} not found")
        return self._decode_chart(row)

    def list_charts(
        self, context_id: str | None = None, limit: int = 100_000
    ) -> list[dict[str, Any]]:
        if context_id is None:
            rows = self._conn.execute(
                "SELECT * FROM equality_charts ORDER BY created_at,id LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                """SELECT * FROM equality_charts WHERE context_id=?
                ORDER BY created_at,id LIMIT ?""",
                (context_id, limit),
            ).fetchall()
        return [self._decode_chart(row) for row in rows]

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO equality_runtime_state(key,value,updated_at)
                VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET
                value=excluded.value,updated_at=excluded.updated_at""",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute(
            "SELECT value FROM equality_runtime_state WHERE key=?", (key,)
        ).fetchone()
        return default if row is None else _loads(row["value"], default)

    def stats(self) -> dict[str, int]:
        def count(table: str) -> int:
            return int(self._conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"])

        return {
            "contexts": count("equality_contexts"),
            "witnesses": count("relative_equality_witnesses"),
            "witness_decisions": count("relative_equality_decisions"),
            "coherences": count("return_coherences"),
            "coherence_decisions": count("return_coherence_decisions"),
            "charts": count("equality_charts"),
        }

    @staticmethod
    def _decode_context(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in (
            ("exact_source_ids", []),
            ("participant_ids", []),
            ("perspective_ids", []),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    @staticmethod
    def _decode_witness(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in (
            ("left_form", {}),
            ("right_form", {}),
            ("exact_source_ids", []),
            ("invariant", []),
            ("residue", []),
            ("return_form", None),
            ("reopening_conditions", []),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    @staticmethod
    def _decode_witness_decision(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["metadata"] = _loads(data["metadata"], {})
        return data

    @staticmethod
    def _decode_coherence(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in (
            ("path_translation_ids", []),
            ("return_form", {}),
            ("exact_source_ids", []),
            ("preserved", []),
            ("residue", []),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    @staticmethod
    def _decode_coherence_decision(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["metadata"] = _loads(data["metadata"], {})
        return data

    @staticmethod
    def _decode_chart(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in (
            ("exact_source_ids", []),
            ("invariant", []),
            ("residue", []),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data
