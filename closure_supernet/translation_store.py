from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import Verdict
from .translation_models import (
    TranslationEventCreate,
    TranslationState,
    TranslationStateCreate,
)


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _loads(value: str | None, default: Any) -> Any:
    return default if value is None else json.loads(value)


class TranslationStore:
    """Append-only store for the live translational-truth field.

    Protocol messages and domain objects may point into this store, but they do
    not replace it. Translation events and their state history are immutable;
    later interpretation, admission, return and reopening append state records.
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
        CREATE TABLE IF NOT EXISTS translation_events (
            id TEXT PRIMARY KEY,
            kind TEXT NOT NULL,
            exact_source_ids TEXT NOT NULL,
            source_forms TEXT NOT NULL,
            target_forms TEXT NOT NULL,
            participant_ids TEXT NOT NULL,
            participating_perspective_ids TEXT NOT NULL,
            interaction_trace_ids TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            preserves TEXT NOT NULL,
            transforms TEXT NOT NULL,
            untranslated TEXT NOT NULL,
            affected_perspectives TEXT NOT NULL,
            frame_and_scope TEXT NOT NULL,
            admission_scope TEXT NOT NULL,
            reopening_conditions TEXT NOT NULL,
            predecessor_translation_ids TEXT NOT NULL,
            successor_potential TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            generated_by TEXT NOT NULL,
            external_key TEXT UNIQUE,
            transport TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_translation_events_created
            ON translation_events(created_at, id);
        CREATE INDEX IF NOT EXISTS idx_translation_events_kind
            ON translation_events(kind, created_at);

        CREATE TABLE IF NOT EXISTS translation_states (
            id TEXT PRIMARY KEY,
            translation_id TEXT NOT NULL REFERENCES translation_events(id),
            state TEXT NOT NULL,
            verdict TEXT NOT NULL,
            reason TEXT NOT NULL,
            actor_id TEXT NOT NULL,
            interpretation_id TEXT,
            admission_id TEXT,
            returned_form TEXT,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_translation_states_translation
            ON translation_states(translation_id, created_at, id);

        CREATE TABLE IF NOT EXISTS translation_runtime_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    def create_translation(
        self, data: TranslationEventCreate
    ) -> tuple[dict[str, Any], bool]:
        if data.external_key:
            existing = self.get_by_external_key(data.external_key)
            if existing is not None:
                return existing, False
        translation_id = str(uuid.uuid4())
        created_at = utcnow()
        values = (
            translation_id,
            str(data.kind),
            _json(data.exact_source_ids),
            _json([item.model_dump(mode="json") for item in data.source_forms]),
            _json([item.model_dump(mode="json") for item in data.target_forms]),
            _json(data.participant_ids),
            _json(data.participating_perspective_ids),
            _json(data.interaction_trace_ids),
            data.relation_type,
            _json(data.preserves),
            _json(data.transforms),
            _json(data.untranslated),
            _json(data.affected_perspectives),
            data.frame_and_scope,
            data.admission_scope,
            _json(data.reopening_conditions),
            _json(data.predecessor_translation_ids),
            _json([item.model_dump(mode="json") for item in data.successor_potential]),
            str(data.evidence_status),
            data.generated_by,
            data.external_key,
            _json(data.transport),
            _json(data.metadata),
            created_at,
        )
        with self._lock:
            self._conn.execute(
                """INSERT INTO translation_events(
                    id,kind,exact_source_ids,source_forms,target_forms,
                    participant_ids,participating_perspective_ids,
                    interaction_trace_ids,relation_type,preserves,transforms,
                    untranslated,affected_perspectives,frame_and_scope,
                    admission_scope,reopening_conditions,
                    predecessor_translation_ids,successor_potential,
                    evidence_status,generated_by,external_key,transport,metadata,
                    created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                values,
            )
            self._conn.commit()
        self.append_state(
            translation_id,
            TranslationStateCreate(
                state=TranslationState.PROPOSED,
                verdict=Verdict.OPEN,
                reason="Translation entered the live field without terminal admission",
                actor_id=data.generated_by,
                metadata={"initial": True},
            ),
        )
        return self.get_translation(translation_id), True

    def get_by_external_key(self, external_key: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT id FROM translation_events WHERE external_key=?", (external_key,)
        ).fetchone()
        return None if row is None else self.get_translation(str(row["id"]))

    def append_state(
        self, translation_id: str, data: TranslationStateCreate
    ) -> tuple[dict[str, Any], bool]:
        self._get_event_row(translation_id)
        returned_form = (
            None
            if data.returned_form is None
            else _json(data.returned_form.model_dump(mode="json"))
        )
        duplicate = self._conn.execute(
            """SELECT * FROM translation_states
            WHERE translation_id=? AND state=? AND verdict=? AND reason=?
              AND actor_id=? AND interpretation_id IS ? AND admission_id IS ?
            ORDER BY created_at DESC LIMIT 1""",
            (
                translation_id,
                str(data.state),
                str(data.verdict),
                data.reason,
                data.actor_id,
                data.interpretation_id,
                data.admission_id,
            ),
        ).fetchone()
        if duplicate:
            return self._decode_state(duplicate), False
        state_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                """INSERT INTO translation_states(
                    id,translation_id,state,verdict,reason,actor_id,
                    interpretation_id,admission_id,returned_form,metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    state_id,
                    translation_id,
                    str(data.state),
                    str(data.verdict),
                    data.reason,
                    data.actor_id,
                    data.interpretation_id,
                    data.admission_id,
                    returned_form,
                    _json(data.metadata),
                    utcnow(),
                ),
            )
            self._conn.commit()
        return self.get_state(state_id), True

    def get_state(self, state_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM translation_states WHERE id=?", (state_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Translation state {state_id} not found")
        return self._decode_state(row)

    def list_states(self, translation_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """SELECT * FROM translation_states WHERE translation_id=?
            ORDER BY created_at,id""",
            (translation_id,),
        ).fetchall()
        return [self._decode_state(row) for row in rows]

    def current_state(self, translation_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            """SELECT * FROM translation_states WHERE translation_id=?
            ORDER BY created_at DESC,id DESC LIMIT 1""",
            (translation_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Translation {translation_id} has no state")
        return self._decode_state(row)

    def get_translation(self, translation_id: str) -> dict[str, Any]:
        data = self._decode_event(self._get_event_row(translation_id))
        history = self.list_states(translation_id)
        current = history[-1]
        data["current_state"] = current["state"]
        data["current_verdict"] = current["verdict"]
        data["state_history"] = history
        return data

    def list_translations(
        self,
        *,
        state: str | None = None,
        kind: str | None = None,
        limit: int = 10_000,
    ) -> list[dict[str, Any]]:
        query = "SELECT id FROM translation_events"
        clauses: list[str] = []
        params: list[Any] = []
        if kind is not None:
            clauses.append("kind=?")
            params.append(kind)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY created_at,id LIMIT ?"
        params.append(limit)
        result = [
            self.get_translation(str(row["id"]))
            for row in self._conn.execute(query, params).fetchall()
        ]
        if state is not None:
            result = [item for item in result if item["current_state"] == state]
        return result

    def _get_event_row(self, translation_id: str) -> sqlite3.Row:
        row = self._conn.execute(
            "SELECT * FROM translation_events WHERE id=?", (translation_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Translation {translation_id} not found")
        return row

    @staticmethod
    def _decode_event(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in (
            ("exact_source_ids", []),
            ("source_forms", []),
            ("target_forms", []),
            ("participant_ids", []),
            ("participating_perspective_ids", []),
            ("interaction_trace_ids", []),
            ("preserves", []),
            ("transforms", []),
            ("untranslated", []),
            ("affected_perspectives", []),
            ("reopening_conditions", []),
            ("predecessor_translation_ids", []),
            ("successor_potential", []),
            ("transport", {}),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    @staticmethod
    def _decode_state(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["returned_form"] = _loads(data["returned_form"], None)
        data["metadata"] = _loads(data["metadata"], {})
        return data

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO translation_runtime_state(key,value,updated_at)
                VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET
                value=excluded.value,updated_at=excluded.updated_at""",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state_value(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute(
            "SELECT value FROM translation_runtime_state WHERE key=?", (key,)
        ).fetchone()
        return default if row is None else _loads(row["value"], default)

    def stats(self) -> dict[str, int]:
        translations = int(
            self._conn.execute("SELECT COUNT(*) AS n FROM translation_events").fetchone()["n"]
        )
        states = int(
            self._conn.execute("SELECT COUNT(*) AS n FROM translation_states").fetchone()["n"]
        )
        current: dict[str, int] = {}
        for item in self.list_translations(limit=100_000):
            current[item["current_state"]] = current.get(item["current_state"], 0) + 1
        return {"translations": translations, "states": states, **current}
