from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import OccurrenceCreate, RuleState, RuleVersionCreate, Verdict


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _loads(value: str | None, default: Any) -> Any:
    if value is None:
        return default
    return json.loads(value)


class EventStore:
    """SQLite event store with immutable source occurrences and versioned rules."""

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
        self._ensure_constitutional_rule()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def _init_schema(self) -> None:
        schema = """
        CREATE TABLE IF NOT EXISTS occurrences (
            id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            exact_text TEXT NOT NULL,
            exact_symbols TEXT NOT NULL,
            operator_path TEXT NOT NULL,
            source_location TEXT,
            source_context TEXT,
            status TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            checksum TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_occ_checksum ON occurrences(checksum);

        CREATE TABLE IF NOT EXISTS candidate_relations (
            id TEXT PRIMARY KEY,
            source_occurrence TEXT NOT NULL REFERENCES occurrences(id),
            target_occurrence TEXT NOT NULL REFERENCES occurrences(id),
            relation_type TEXT NOT NULL,
            score REAL NOT NULL,
            rationale TEXT NOT NULL,
            proposed_by TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(source_occurrence, target_occurrence, relation_type)
        );

        CREATE TABLE IF NOT EXISTS interpretations (
            id TEXT PRIMARY KEY,
            candidate_relation_id TEXT NOT NULL REFERENCES candidate_relations(id),
            source_operator_path TEXT NOT NULL,
            target_operator_path TEXT NOT NULL,
            preserved_structure TEXT NOT NULL,
            transformed_structure TEXT NOT NULL,
            omitted_or_hidden_structure TEXT NOT NULL,
            frame_and_scope TEXT NOT NULL,
            reverse_path TEXT NOT NULL,
            affected_perspectives TEXT NOT NULL,
            formal_scope TEXT NOT NULL,
            empirical_scope TEXT NOT NULL,
            reopening TEXT NOT NULL,
            generated_by TEXT NOT NULL,
            status TEXT NOT NULL,
            engine_version TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(candidate_relation_id, engine_version)
        );

        CREATE TABLE IF NOT EXISTS admissions (
            id TEXT PRIMARY KEY,
            interpretation_id TEXT NOT NULL REFERENCES interpretations(id),
            verdict TEXT NOT NULL,
            checks TEXT NOT NULL,
            reason TEXT NOT NULL,
            rule_version TEXT NOT NULL,
            decided_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(interpretation_id, rule_version)
        );

        CREATE TABLE IF NOT EXISTS open_seams (
            id TEXT PRIMARY KEY,
            source_occurrence TEXT,
            target_occurrence TEXT,
            reason TEXT NOT NULL,
            status TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(source_occurrence, target_occurrence, reason)
        );

        CREATE TABLE IF NOT EXISTS rules (
            id TEXT PRIMARY KEY,
            rule_id TEXT NOT NULL,
            version TEXT NOT NULL,
            parent_version TEXT,
            exact_rule_text TEXT NOT NULL,
            reason_for_change TEXT NOT NULL,
            state TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(rule_id, version)
        );

        CREATE TABLE IF NOT EXISTS events (
            seq INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS runtime_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    def _ensure_constitutional_rule(self) -> None:
        row = self._conn.execute(
            "SELECT id FROM rules WHERE rule_id=? AND state=? LIMIT 1",
            ("source-preserving-admission", RuleState.ACTIVE),
        ).fetchone()
        if row:
            return
        self.create_rule_version(
            RuleVersionCreate(
                rule_id="source-preserving-admission",
                exact_rule_text=(
                    "Never overwrite original notes; preserve literal symbols; make operator paths explicit; "
                    "do not silently normalize variants; separate formal, simulated, empirical and hypothetical status; "
                    "retain affected perspectives; expose projection loss; keep incomplete translations OPEN; "
                    "do not assume Turing completeness; every provisional return must reopen."
                ),
                reason_for_change="Constitutional runtime bootstrap",
                state=RuleState.ACTIVE,
                metadata={"constitutional": True},
            )
        )

    def append_event(self, event_type: str, entity_type: str, entity_id: str, payload: dict[str, Any]) -> int:
        with self._lock:
            cursor = self._conn.execute(
                "INSERT INTO events(event_type,entity_type,entity_id,payload,created_at) VALUES(?,?,?,?,?)",
                (event_type, entity_type, entity_id, _json(payload), utcnow()),
            )
            self._conn.commit()
            return int(cursor.lastrowid)

    def create_occurrence(
        self,
        data: OccurrenceCreate,
        exact_symbols: list[str],
        operator_path: list[dict[str, Any]],
    ) -> dict[str, Any]:
        checksum = hashlib.sha256(data.exact_text.encode("utf-8")).hexdigest()
        occurrence_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                """INSERT INTO occurrences
                (id,source_id,exact_text,exact_symbols,operator_path,source_location,source_context,status,evidence_status,checksum,metadata,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    occurrence_id,
                    data.source_id,
                    data.exact_text,
                    _json(exact_symbols),
                    _json(operator_path),
                    data.source_location,
                    data.source_context,
                    str(data.status),
                    str(data.evidence_status),
                    checksum,
                    _json(data.metadata),
                    created_at,
                ),
            )
            self._conn.commit()
        self.append_event("OCCURRENCE_CREATED", "occurrence", occurrence_id, {"checksum": checksum, "source_id": data.source_id})
        return self.get_occurrence(occurrence_id)

    def occurrence_exists_by_checksum(self, checksum: str, source_location: str | None = None) -> bool:
        query = "SELECT 1 FROM occurrences WHERE checksum=?"
        params: list[Any] = [checksum]
        if source_location is not None:
            query += " AND source_location=?"
            params.append(source_location)
        return self._conn.execute(query + " LIMIT 1", params).fetchone() is not None

    def get_occurrence(self, occurrence_id: str) -> dict[str, Any]:
        row = self._conn.execute("SELECT * FROM occurrences WHERE id=?", (occurrence_id,)).fetchone()
        if not row:
            raise KeyError(f"Occurrence {occurrence_id} not found")
        return self._decode_occurrence(row)

    def list_occurrences(self, limit: int = 500, offset: int = 0) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM occurrences ORDER BY created_at,id LIMIT ? OFFSET ?", (limit, offset)
        ).fetchall()
        return [self._decode_occurrence(row) for row in rows]

    def _decode_occurrence(self, row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in [("exact_symbols", []), ("operator_path", []), ("metadata", {})]:
            data[key] = _loads(data[key], default)
        return data

    def create_candidate_relation(
        self,
        source_occurrence: str,
        target_occurrence: str,
        relation_type: str,
        score: float,
        rationale: str,
        proposed_by: str,
        status: str = "PROPOSED",
    ) -> tuple[dict[str, Any], bool]:
        if source_occurrence == target_occurrence:
            raise ValueError("A candidate relation requires two distinct occurrences")
        source_occurrence, target_occurrence = sorted([source_occurrence, target_occurrence])
        existing = self._conn.execute(
            "SELECT * FROM candidate_relations WHERE source_occurrence=? AND target_occurrence=? AND relation_type=?",
            (source_occurrence, target_occurrence, relation_type),
        ).fetchone()
        if existing:
            return dict(existing), False
        relation_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                "INSERT INTO candidate_relations VALUES(?,?,?,?,?,?,?,?,?)",
                (relation_id, source_occurrence, target_occurrence, relation_type, score, rationale, proposed_by, status, utcnow()),
            )
            self._conn.commit()
        self.append_event("CANDIDATE_RELATION_CREATED", "candidate_relation", relation_id, {"type": relation_type, "score": score})
        return self.get_candidate_relation(relation_id), True

    def get_candidate_relation(self, relation_id: str) -> dict[str, Any]:
        row = self._conn.execute("SELECT * FROM candidate_relations WHERE id=?", (relation_id,)).fetchone()
        if not row:
            raise KeyError(relation_id)
        return dict(row)

    def list_candidate_relations(self, limit: int = 1000) -> list[dict[str, Any]]:
        return [dict(row) for row in self._conn.execute(
            "SELECT * FROM candidate_relations ORDER BY created_at,id LIMIT ?", (limit,)
        ).fetchall()]

    def uninterpreted_candidates(self, limit: int = 100) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """SELECT c.* FROM candidate_relations c
            LEFT JOIN interpretations i ON i.candidate_relation_id=c.id
            WHERE i.id IS NULL ORDER BY c.created_at,c.id LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

    def create_interpretation(self, payload: dict[str, Any], engine_version: str) -> tuple[dict[str, Any], bool]:
        existing = self._conn.execute(
            "SELECT * FROM interpretations WHERE candidate_relation_id=? AND engine_version=?",
            (payload["candidate_relation_id"], engine_version),
        ).fetchone()
        if existing:
            return self._decode_interpretation(existing), False
        interpretation_id = str(uuid.uuid4())
        values = (
            interpretation_id,
            payload["candidate_relation_id"],
            _json(payload["source_operator_path"]),
            _json(payload["target_operator_path"]),
            _json(payload["preserved_structure"]),
            _json(payload["transformed_structure"]),
            _json(payload["omitted_or_hidden_structure"]),
            payload["frame_and_scope"],
            _json(payload["reverse_path"]),
            _json(payload["affected_perspectives"]),
            payload["formal_scope"],
            payload["empirical_scope"],
            payload["reopening"],
            payload["generated_by"],
            payload.get("status", "INTERPRETED_RELATION"),
            engine_version,
            utcnow(),
        )
        with self._lock:
            self._conn.execute("INSERT INTO interpretations VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", values)
            self._conn.commit()
        self.append_event("INTERPRETATION_CREATED", "interpretation", interpretation_id, {"candidate_relation_id": payload["candidate_relation_id"]})
        return self.get_interpretation(interpretation_id), True

    def get_interpretation(self, interpretation_id: str) -> dict[str, Any]:
        row = self._conn.execute("SELECT * FROM interpretations WHERE id=?", (interpretation_id,)).fetchone()
        if not row:
            raise KeyError(interpretation_id)
        return self._decode_interpretation(row)

    def list_interpretations(self, limit: int = 1000) -> list[dict[str, Any]]:
        return [self._decode_interpretation(row) for row in self._conn.execute(
            "SELECT * FROM interpretations ORDER BY created_at,id LIMIT ?", (limit,)
        ).fetchall()]

    def _decode_interpretation(self, row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key in (
            "source_operator_path", "target_operator_path", "preserved_structure",
            "transformed_structure", "omitted_or_hidden_structure", "reverse_path",
            "affected_perspectives",
        ):
            data[key] = _loads(data[key], [])
        return data

    def unadmitted_interpretations(self, rule_version: str, limit: int = 100) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """SELECT i.* FROM interpretations i
            LEFT JOIN admissions a ON a.interpretation_id=i.id AND a.rule_version=?
            WHERE a.id IS NULL ORDER BY i.created_at,i.id LIMIT ?""",
            (rule_version, limit),
        ).fetchall()
        return [self._decode_interpretation(row) for row in rows]

    def create_admission(
        self,
        interpretation_id: str,
        verdict: Verdict,
        checks: dict[str, bool],
        reason: str,
        rule_version: str,
        decided_by: str,
    ) -> tuple[dict[str, Any], bool]:
        existing = self._conn.execute(
            "SELECT * FROM admissions WHERE interpretation_id=? AND rule_version=?",
            (interpretation_id, rule_version),
        ).fetchone()
        if existing:
            return self._decode_admission(existing), False
        admission_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                "INSERT INTO admissions VALUES(?,?,?,?,?,?,?,?)",
                (admission_id, interpretation_id, str(verdict), _json(checks), reason, rule_version, decided_by, utcnow()),
            )
            self._conn.commit()
        self.append_event("ADMISSION_DECIDED", "admission", admission_id, {"interpretation_id": interpretation_id, "verdict": str(verdict)})
        return self.get_admission(admission_id), True

    def get_admission(self, admission_id: str) -> dict[str, Any]:
        row = self._conn.execute("SELECT * FROM admissions WHERE id=?", (admission_id,)).fetchone()
        if not row:
            raise KeyError(admission_id)
        return self._decode_admission(row)

    def _decode_admission(self, row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["checks"] = _loads(data["checks"], {})
        return data

    def list_admissions(self, limit: int = 1000) -> list[dict[str, Any]]:
        return [self._decode_admission(row) for row in self._conn.execute(
            "SELECT * FROM admissions ORDER BY created_at,id LIMIT ?", (limit,)
        ).fetchall()]

    def latest_admissions(self, limit: int = 100_000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """SELECT a.* FROM admissions a
            JOIN (SELECT interpretation_id, MAX(created_at) AS max_created FROM admissions GROUP BY interpretation_id) latest
              ON latest.interpretation_id=a.interpretation_id AND latest.max_created=a.created_at
            ORDER BY a.created_at,a.id LIMIT ?""",
            (limit,),
        ).fetchall()
        return [self._decode_admission(row) for row in rows]

    def create_open_seam(
        self,
        source_occurrence: str | None,
        target_occurrence: str | None,
        reason: str,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], bool]:
        existing = self._conn.execute(
            "SELECT * FROM open_seams WHERE source_occurrence IS ? AND target_occurrence IS ? AND reason=?",
            (source_occurrence, target_occurrence, reason),
        ).fetchone()
        if existing:
            return self._decode_open_seam(existing), False
        seam_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                "INSERT INTO open_seams VALUES(?,?,?,?,?,?,?)",
                (seam_id, source_occurrence, target_occurrence, reason, str(Verdict.OPEN), _json(metadata or {}), utcnow()),
            )
            self._conn.commit()
        self.append_event("OPEN_SEAM_CREATED", "open_seam", seam_id, {"reason": reason})
        return self.get_open_seam(seam_id), True

    def get_open_seam(self, seam_id: str) -> dict[str, Any]:
        row = self._conn.execute("SELECT * FROM open_seams WHERE id=?", (seam_id,)).fetchone()
        if not row:
            raise KeyError(seam_id)
        return self._decode_open_seam(row)

    def _decode_open_seam(self, row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["metadata"] = _loads(data["metadata"], {})
        return data

    def list_open_seams(self, limit: int = 1000) -> list[dict[str, Any]]:
        return [self._decode_open_seam(row) for row in self._conn.execute(
            "SELECT * FROM open_seams ORDER BY created_at,id LIMIT ?", (limit,)
        ).fetchall()]

    def create_rule_version(self, data: RuleVersionCreate) -> dict[str, Any]:
        existing_versions = self._conn.execute(
            "SELECT version FROM rules WHERE rule_id=? ORDER BY created_at", (data.rule_id,)
        ).fetchall()
        version = str(len(existing_versions) + 1)
        rule_id = str(uuid.uuid4())
        with self._lock:
            if data.state == RuleState.ACTIVE:
                self._conn.execute("UPDATE rules SET state=? WHERE rule_id=? AND state=?", (RuleState.RETIRED, data.rule_id, RuleState.ACTIVE))
            self._conn.execute(
                "INSERT INTO rules VALUES(?,?,?,?,?,?,?,?,?)",
                (rule_id, data.rule_id, version, data.parent_version, data.exact_rule_text, data.reason_for_change, str(data.state), _json(data.metadata), utcnow()),
            )
            self._conn.commit()
        self.append_event("RULE_VERSION_CREATED", "rule", rule_id, {"rule_id": data.rule_id, "version": version, "state": str(data.state)})
        return self.get_rule(rule_id)

    def activate_rule(self, rule_db_id: str) -> dict[str, Any]:
        rule = self.get_rule(rule_db_id)
        with self._lock:
            self._conn.execute("UPDATE rules SET state=? WHERE rule_id=? AND state=?", (RuleState.RETIRED, rule["rule_id"], RuleState.ACTIVE))
            self._conn.execute("UPDATE rules SET state=? WHERE id=?", (RuleState.ACTIVE, rule_db_id))
            self._conn.commit()
        self.append_event("RULE_ACTIVATED", "rule", rule_db_id, {"rule_id": rule["rule_id"], "version": rule["version"]})
        return self.get_rule(rule_db_id)

    def get_rule(self, rule_db_id: str) -> dict[str, Any]:
        row = self._conn.execute("SELECT * FROM rules WHERE id=?", (rule_db_id,)).fetchone()
        if not row:
            raise KeyError(rule_db_id)
        data = dict(row)
        data["metadata"] = _loads(data["metadata"], {})
        return data

    def list_rules(self) -> list[dict[str, Any]]:
        rows = self._conn.execute("SELECT * FROM rules ORDER BY rule_id,created_at").fetchall()
        result = []
        for row in rows:
            data = dict(row)
            data["metadata"] = _loads(data["metadata"], {})
            result.append(data)
        return result

    def active_rule_version(self, rule_id: str = "source-preserving-admission") -> str:
        row = self._conn.execute(
            "SELECT version FROM rules WHERE rule_id=? AND state=? ORDER BY created_at DESC LIMIT 1",
            (rule_id, RuleState.ACTIVE),
        ).fetchone()
        return str(row["version"]) if row else "0"

    def events_after(self, seq: int = 0, limit: int = 500) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM events WHERE seq>? ORDER BY seq LIMIT ?", (seq, limit)
        ).fetchall()
        result = []
        for row in rows:
            data = dict(row)
            data["payload"] = _loads(data["payload"], {})
            result.append(data)
        return result

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute("SELECT value FROM runtime_state WHERE key=?", (key,)).fetchone()
        return _loads(row["value"], default) if row else default

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO runtime_state(key,value,updated_at) VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def stats(self) -> dict[str, int]:
        tables = ["occurrences", "candidate_relations", "interpretations", "admissions", "open_seams", "rules", "events"]
        return {table: int(self._conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]) for table in tables}
