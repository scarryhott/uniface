from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import Verdict
from .resource_models import (
    ProtocolReceiptCreate,
    ResourceCreate,
    ResourceEngagementCreate,
    ResourceTranslationCreate,
    ResourceTranslationDecisionCreate,
)


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _loads(value: str | None, default: Any) -> Any:
    return default if value is None else json.loads(value)


class ResourceStore:
    """Append-only resource forms and live translation stages.

    Resource forms and language labels are stored as authored strings.  There
    is intentionally no resource-kind or canonical-language registry.
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
        CREATE TABLE IF NOT EXISTS resource_forms (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL REFERENCES occurrences(id),
            created_by TEXT NOT NULL REFERENCES living_participants(id),
            form_label TEXT NOT NULL,
            language_label TEXT,
            perspective_id TEXT REFERENCES living_perspectives(id),
            problem_id TEXT REFERENCES living_problems(id),
            action_id TEXT REFERENCES living_actions(id),
            parent_resource_id TEXT REFERENCES resource_forms(id),
            visibility TEXT NOT NULL,
            affected_perspectives TEXT NOT NULL,
            capabilities TEXT NOT NULL,
            constraints TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_resource_forms_problem
            ON resource_forms(problem_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_resource_forms_author
            ON resource_forms(created_by, created_at);

        CREATE TABLE IF NOT EXISTS resource_engagements (
            id TEXT PRIMARY KEY,
            resource_id TEXT NOT NULL REFERENCES resource_forms(id),
            occurrence_id TEXT NOT NULL REFERENCES occurrences(id),
            actor_id TEXT NOT NULL REFERENCES living_participants(id),
            engagement_label TEXT NOT NULL,
            language_label TEXT,
            perspective_id TEXT REFERENCES living_perspectives(id),
            problem_id TEXT REFERENCES living_problems(id),
            interaction_id TEXT REFERENCES living_interactions(id),
            affected_perspectives TEXT NOT NULL,
            preserves TEXT NOT NULL,
            transforms TEXT NOT NULL,
            omits TEXT NOT NULL,
            visibility TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_resource_engagements_resource
            ON resource_engagements(resource_id, created_at);

        CREATE TABLE IF NOT EXISTS resource_translations (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL REFERENCES occurrences(id),
            source_resource_id TEXT NOT NULL REFERENCES resource_forms(id),
            target_resource_id TEXT NOT NULL REFERENCES resource_forms(id),
            authored_by TEXT NOT NULL REFERENCES living_participants(id),
            relation_label TEXT NOT NULL,
            source_frame TEXT NOT NULL,
            target_frame TEXT NOT NULL,
            source_language TEXT,
            target_language TEXT,
            preserved TEXT NOT NULL,
            transformed TEXT NOT NULL,
            omitted TEXT NOT NULL,
            faithfulness TEXT NOT NULL,
            affected_perspectives TEXT NOT NULL,
            protocol_verdict INTEGER,
            transport_label TEXT,
            visibility TEXT NOT NULL,
            metadata TEXT NOT NULL,
            candidate_relation_id TEXT,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_resource_translations_source
            ON resource_translations(source_resource_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_resource_translations_target
            ON resource_translations(target_resource_id, created_at);

        CREATE TABLE IF NOT EXISTS resource_translation_decisions (
            id TEXT PRIMARY KEY,
            translation_id TEXT NOT NULL REFERENCES resource_translations(id),
            verdict TEXT NOT NULL,
            reason TEXT NOT NULL,
            decided_by TEXT NOT NULL,
            scope TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_resource_translation_decisions
            ON resource_translation_decisions(translation_id, created_at);

        CREATE TABLE IF NOT EXISTS resource_returns (
            id TEXT PRIMARY KEY,
            engagement_id TEXT NOT NULL REFERENCES resource_engagements(id),
            source_resource_id TEXT NOT NULL REFERENCES resource_forms(id),
            returned_resource_id TEXT NOT NULL REFERENCES resource_forms(id),
            occurrence_id TEXT NOT NULL REFERENCES occurrences(id),
            authored_by TEXT NOT NULL REFERENCES living_participants(id),
            affected_perspectives TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            metadata TEXT NOT NULL,
            reintegration_status TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_resource_returns_engagement
            ON resource_returns(engagement_id, created_at);

        CREATE TABLE IF NOT EXISTS resource_reintegrations (
            id TEXT PRIMARY KEY,
            return_id TEXT NOT NULL UNIQUE REFERENCES resource_returns(id),
            source_resource_id TEXT NOT NULL REFERENCES resource_forms(id),
            returned_resource_id TEXT NOT NULL REFERENCES resource_forms(id),
            translation_id TEXT REFERENCES resource_translations(id),
            candidate_relation_id TEXT,
            status TEXT NOT NULL,
            open_questions TEXT NOT NULL,
            affected_perspectives TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_resource_reintegrations_status
            ON resource_reintegrations(status, updated_at);

        CREATE TABLE IF NOT EXISTS resource_protocol_receipts (
            id TEXT PRIMARY KEY,
            resource_id TEXT NOT NULL REFERENCES resource_forms(id),
            occurrence_id TEXT NOT NULL REFERENCES occurrences(id),
            recorded_by TEXT NOT NULL REFERENCES living_participants(id),
            transport_label TEXT NOT NULL,
            wire_reference TEXT,
            protocol_verdict INTEGER NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS resource_live_stages (
            id TEXT PRIMARY KEY,
            stage_index INTEGER NOT NULL UNIQUE,
            previous_stage_id TEXT REFERENCES resource_live_stages(id),
            trigger TEXT NOT NULL,
            delivery_order TEXT NOT NULL,
            resource_ids TEXT NOT NULL,
            engagement_ids TEXT NOT NULL,
            translation_ids TEXT NOT NULL,
            admitted_translation_ids TEXT NOT NULL,
            open_translation_ids TEXT NOT NULL,
            rejected_translation_ids TEXT NOT NULL,
            natural_components TEXT NOT NULL,
            stage_signature TEXT NOT NULL,
            limit_signature TEXT NOT NULL,
            complete_coverage INTEGER NOT NULL,
            canonical_language TEXT,
            source_reverse_index TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_resource_live_stages_index
            ON resource_live_stages(stage_index);

        CREATE TABLE IF NOT EXISTS resource_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    # ------------------------------------------------------------------
    # Resources
    # ------------------------------------------------------------------

    def create_resource(self, data: ResourceCreate, occurrence_id: str) -> dict[str, Any]:
        resource_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                """INSERT INTO resource_forms
                (id,occurrence_id,created_by,form_label,language_label,perspective_id,
                 problem_id,action_id,parent_resource_id,visibility,affected_perspectives,
                 capabilities,constraints,metadata,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    resource_id,
                    occurrence_id,
                    data.created_by,
                    data.form_label,
                    data.language_label,
                    data.perspective_id,
                    data.problem_id,
                    data.action_id,
                    data.parent_resource_id,
                    str(data.visibility),
                    _json(data.affected_perspectives),
                    _json(data.capabilities),
                    _json(data.constraints),
                    _json(data.metadata),
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_resource(resource_id)

    def get_resource(self, resource_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM resource_forms WHERE id=?", (resource_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Resource {resource_id} not found")
        data = dict(row)
        for key, default in (
            ("affected_perspectives", []),
            ("capabilities", []),
            ("constraints", []),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    def list_resources(
        self,
        *,
        problem_id: str | None = None,
        created_by: str | None = None,
        limit: int = 10_000,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        values: list[Any] = []
        if problem_id:
            clauses.append("problem_id=?")
            values.append(problem_id)
        if created_by:
            clauses.append("created_by=?")
            values.append(created_by)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        values.append(limit)
        rows = self._conn.execute(
            f"SELECT id FROM resource_forms{where} ORDER BY created_at,id LIMIT ?",
            tuple(values),
        ).fetchall()
        return [self.get_resource(str(row["id"])) for row in rows]

    # ------------------------------------------------------------------
    # Engagements
    # ------------------------------------------------------------------

    def create_engagement(
        self, data: ResourceEngagementCreate, occurrence_id: str
    ) -> dict[str, Any]:
        engagement_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                """INSERT INTO resource_engagements
                (id,resource_id,occurrence_id,actor_id,engagement_label,language_label,
                 perspective_id,problem_id,interaction_id,affected_perspectives,
                 preserves,transforms,omits,visibility,metadata,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    engagement_id,
                    data.resource_id,
                    occurrence_id,
                    data.actor_id,
                    data.engagement_label,
                    data.language_label,
                    data.perspective_id,
                    data.problem_id,
                    data.interaction_id,
                    _json(data.affected_perspectives),
                    _json(data.preserves),
                    _json(data.transforms),
                    _json(data.omits),
                    str(data.visibility),
                    _json(data.metadata),
                    utcnow(),
                ),
            )
            self._conn.commit()
        return self.get_engagement(engagement_id)

    def get_engagement(self, engagement_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM resource_engagements WHERE id=?", (engagement_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Resource engagement {engagement_id} not found")
        data = dict(row)
        for key, default in (
            ("affected_perspectives", []),
            ("preserves", []),
            ("transforms", []),
            ("omits", []),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    def list_engagements(
        self, resource_id: str | None = None, limit: int = 20_000
    ) -> list[dict[str, Any]]:
        if resource_id:
            rows = self._conn.execute(
                "SELECT id FROM resource_engagements WHERE resource_id=? ORDER BY created_at,id LIMIT ?",
                (resource_id, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT id FROM resource_engagements ORDER BY created_at,id LIMIT ?",
                (limit,),
            ).fetchall()
        return [self.get_engagement(str(row["id"])) for row in rows]

    # ------------------------------------------------------------------
    # Translations and decisions
    # ------------------------------------------------------------------

    def create_translation(
        self,
        data: ResourceTranslationCreate,
        occurrence_id: str,
        candidate_relation_id: str | None,
    ) -> dict[str, Any]:
        translation_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                """INSERT INTO resource_translations
                (id,occurrence_id,source_resource_id,target_resource_id,authored_by,
                 relation_label,source_frame,target_frame,source_language,target_language,
                 preserved,transformed,omitted,faithfulness,affected_perspectives,
                 protocol_verdict,transport_label,visibility,metadata,candidate_relation_id,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    translation_id,
                    occurrence_id,
                    data.source_resource_id,
                    data.target_resource_id,
                    data.authored_by,
                    data.relation_label,
                    data.source_frame,
                    data.target_frame,
                    data.source_language,
                    data.target_language,
                    _json(data.preserved),
                    _json(data.transformed),
                    _json(data.omitted),
                    _json(data.faithfulness),
                    _json(data.affected_perspectives),
                    None if data.protocol_verdict is None else int(data.protocol_verdict),
                    data.transport_label,
                    str(data.visibility),
                    _json(data.metadata),
                    candidate_relation_id,
                    created_at,
                ),
            )
            self._conn.execute(
                """INSERT INTO resource_translation_decisions
                (id,translation_id,verdict,reason,decided_by,scope,created_at)
                VALUES(?,?,?,?,?,?,?)""",
                (
                    str(uuid.uuid4()),
                    translation_id,
                    str(Verdict.OPEN),
                    "A proposed translation remains OPEN until relative admission; protocol success is not truth",
                    data.authored_by,
                    "proposal",
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_translation(translation_id)

    def decide_translation(
        self, translation_id: str, data: ResourceTranslationDecisionCreate
    ) -> dict[str, Any]:
        self.get_translation(translation_id)
        with self._lock:
            self._conn.execute(
                """INSERT INTO resource_translation_decisions
                (id,translation_id,verdict,reason,decided_by,scope,created_at)
                VALUES(?,?,?,?,?,?,?)""",
                (
                    str(uuid.uuid4()),
                    translation_id,
                    str(data.verdict),
                    data.reason,
                    data.decided_by,
                    data.scope,
                    utcnow(),
                ),
            )
            self._conn.commit()
        return self.get_translation(translation_id)

    def get_translation(self, translation_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM resource_translations WHERE id=?", (translation_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Resource translation {translation_id} not found")
        data = dict(row)
        for key, default in (
            ("preserved", []),
            ("transformed", []),
            ("omitted", []),
            ("faithfulness", {}),
            ("affected_perspectives", []),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        if data["protocol_verdict"] is not None:
            data["protocol_verdict"] = bool(data["protocol_verdict"])
        decision = self._conn.execute(
            """SELECT verdict,reason,decided_by,scope FROM resource_translation_decisions
            WHERE translation_id=? ORDER BY created_at DESC,rowid DESC LIMIT 1""",
            (translation_id,),
        ).fetchone()
        data["current_verdict"] = str(decision["verdict"])
        data["current_reason"] = str(decision["reason"])
        data["decided_by"] = str(decision["decided_by"])
        data["current_scope"] = str(decision["scope"])
        return data

    def list_translations(self, limit: int = 20_000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT id FROM resource_translations ORDER BY created_at,id LIMIT ?",
            (limit,),
        ).fetchall()
        return [self.get_translation(str(row["id"])) for row in rows]

    # ------------------------------------------------------------------
    # Returns and reintegration
    # ------------------------------------------------------------------

    def create_return(
        self,
        *,
        engagement_id: str,
        source_resource_id: str,
        returned_resource_id: str,
        occurrence_id: str,
        authored_by: str,
        affected_perspectives: list[str],
        evidence_status: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        return_id = str(uuid.uuid4())
        reintegration_id = str(uuid.uuid4())
        created_at = utcnow()
        open_questions = [
            "Which relation between the source resource and its return is admissible?",
            "What did active engagement preserve, transform or leave OPEN?",
            "Does the return create another resource form rather than terminate the continuum?",
        ]
        with self._lock:
            self._conn.execute(
                """INSERT INTO resource_returns
                (id,engagement_id,source_resource_id,returned_resource_id,occurrence_id,
                 authored_by,affected_perspectives,evidence_status,metadata,
                 reintegration_status,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    return_id,
                    engagement_id,
                    source_resource_id,
                    returned_resource_id,
                    occurrence_id,
                    authored_by,
                    _json(affected_perspectives),
                    evidence_status,
                    _json(metadata),
                    "PENDING",
                    created_at,
                ),
            )
            self._conn.execute(
                """INSERT INTO resource_reintegrations
                (id,return_id,source_resource_id,returned_resource_id,translation_id,
                 candidate_relation_id,status,open_questions,affected_perspectives,
                 created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    reintegration_id,
                    return_id,
                    source_resource_id,
                    returned_resource_id,
                    None,
                    None,
                    "PENDING",
                    _json(open_questions),
                    _json(affected_perspectives),
                    created_at,
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_return(return_id)

    def get_return(self, return_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM resource_returns WHERE id=?", (return_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Resource return {return_id} not found")
        data = dict(row)
        data["affected_perspectives"] = _loads(data["affected_perspectives"], [])
        data["metadata"] = _loads(data["metadata"], {})
        return data

    def list_returns(self, limit: int = 20_000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT id FROM resource_returns ORDER BY created_at,id LIMIT ?", (limit,)
        ).fetchall()
        return [self.get_return(str(row["id"])) for row in rows]

    def get_reintegration(self, reintegration_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM resource_reintegrations WHERE id=?", (reintegration_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Resource reintegration {reintegration_id} not found")
        data = dict(row)
        data["open_questions"] = _loads(data["open_questions"], [])
        data["affected_perspectives"] = _loads(data["affected_perspectives"], [])
        return data

    def list_reintegrations(
        self, status: str | None = None, limit: int = 20_000
    ) -> list[dict[str, Any]]:
        if status:
            rows = self._conn.execute(
                "SELECT id FROM resource_reintegrations WHERE status=? ORDER BY created_at,id LIMIT ?",
                (status, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT id FROM resource_reintegrations ORDER BY created_at,id LIMIT ?",
                (limit,),
            ).fetchall()
        return [self.get_reintegration(str(row["id"])) for row in rows]

    def complete_reintegration(
        self,
        reintegration_id: str,
        *,
        translation_id: str,
        candidate_relation_id: str | None,
    ) -> dict[str, Any]:
        current = self.get_reintegration(reintegration_id)
        now = utcnow()
        with self._lock:
            self._conn.execute(
                """UPDATE resource_reintegrations
                SET translation_id=?,candidate_relation_id=?,status=?,updated_at=? WHERE id=?""",
                (
                    translation_id,
                    candidate_relation_id,
                    "REINTEGRATED_OPEN",
                    now,
                    reintegration_id,
                ),
            )
            self._conn.execute(
                "UPDATE resource_returns SET reintegration_status=? WHERE id=?",
                ("REINTEGRATED_OPEN", current["return_id"]),
            )
            self._conn.commit()
        return self.get_reintegration(reintegration_id)

    # ------------------------------------------------------------------
    # Protocol receipts
    # ------------------------------------------------------------------

    def create_protocol_receipt(
        self, data: ProtocolReceiptCreate, occurrence_id: str
    ) -> dict[str, Any]:
        receipt_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                """INSERT INTO resource_protocol_receipts
                (id,resource_id,occurrence_id,recorded_by,transport_label,
                 wire_reference,protocol_verdict,metadata,created_at)
                VALUES(?,?,?,?,?,?,?,?,?)""",
                (
                    receipt_id,
                    data.resource_id,
                    occurrence_id,
                    data.recorded_by,
                    data.transport_label,
                    data.wire_reference,
                    int(data.protocol_verdict),
                    _json(data.metadata),
                    utcnow(),
                ),
            )
            self._conn.commit()
        return self.get_protocol_receipt(receipt_id)

    def get_protocol_receipt(self, receipt_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM resource_protocol_receipts WHERE id=?", (receipt_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Protocol receipt {receipt_id} not found")
        data = dict(row)
        data["protocol_verdict"] = bool(data["protocol_verdict"])
        data["metadata"] = _loads(data["metadata"], {})
        return data

    def list_protocol_receipts(self, limit: int = 20_000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT id FROM resource_protocol_receipts ORDER BY created_at,id LIMIT ?",
            (limit,),
        ).fetchall()
        return [self.get_protocol_receipt(str(row["id"])) for row in rows]

    # ------------------------------------------------------------------
    # Live stages
    # ------------------------------------------------------------------

    def create_stage(self, data: dict[str, Any]) -> dict[str, Any]:
        stage_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                """INSERT INTO resource_live_stages
                (id,stage_index,previous_stage_id,trigger,delivery_order,resource_ids,
                 engagement_ids,translation_ids,admitted_translation_ids,
                 open_translation_ids,rejected_translation_ids,natural_components,
                 stage_signature,limit_signature,complete_coverage,canonical_language,
                 source_reverse_index,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    stage_id,
                    data["stage_index"],
                    data.get("previous_stage_id"),
                    data["trigger"],
                    _json(data["delivery_order"]),
                    _json(data["resource_ids"]),
                    _json(data["engagement_ids"]),
                    _json(data["translation_ids"]),
                    _json(data["admitted_translation_ids"]),
                    _json(data["open_translation_ids"]),
                    _json(data["rejected_translation_ids"]),
                    _json(data["natural_components"]),
                    data["stage_signature"],
                    data["limit_signature"],
                    int(data["complete_coverage"]),
                    data.get("canonical_language"),
                    _json(data["source_reverse_index"]),
                    utcnow(),
                ),
            )
            self._conn.commit()
        return self.get_stage(stage_id)

    def get_stage(self, stage_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM resource_live_stages WHERE id=?", (stage_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Live resource stage {stage_id} not found")
        data = dict(row)
        for key, default in (
            ("delivery_order", []),
            ("resource_ids", []),
            ("engagement_ids", []),
            ("translation_ids", []),
            ("admitted_translation_ids", []),
            ("open_translation_ids", []),
            ("rejected_translation_ids", []),
            ("natural_components", []),
            ("source_reverse_index", {}),
        ):
            data[key] = _loads(data[key], default)
        data["complete_coverage"] = bool(data["complete_coverage"])
        return data

    def latest_stage(self) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT id FROM resource_live_stages ORDER BY stage_index DESC LIMIT 1"
        ).fetchone()
        return None if row is None else self.get_stage(str(row["id"]))

    def list_stages(self, limit: int = 1000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT id FROM resource_live_stages ORDER BY stage_index,id LIMIT ?",
            (limit,),
        ).fetchall()
        return [self.get_stage(str(row["id"])) for row in rows]

    def chronological_delivery_order(self) -> list[str]:
        rows = self._conn.execute(
            """SELECT created_at,'resource:' || id AS ref FROM resource_forms
            UNION ALL SELECT created_at,'engagement:' || id FROM resource_engagements
            UNION ALL SELECT created_at,'translation:' || id FROM resource_translations
            UNION ALL SELECT created_at,'return:' || id FROM resource_returns
            ORDER BY created_at,ref"""
        ).fetchall()
        return [str(row["ref"]) for row in rows]

    # ------------------------------------------------------------------
    # State and stats
    # ------------------------------------------------------------------

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO resource_state(key,value,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute(
            "SELECT value FROM resource_state WHERE key=?", (key,)
        ).fetchone()
        return default if row is None else _loads(row["value"], default)

    def stats(self) -> dict[str, int]:
        def count(table: str) -> int:
            return int(self._conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])

        return {
            "resources": count("resource_forms"),
            "engagements": count("resource_engagements"),
            "translations": count("resource_translations"),
            "returns": count("resource_returns"),
            "reintegrations": count("resource_reintegrations"),
            "pending_reintegrations": int(
                self._conn.execute(
                    "SELECT COUNT(*) FROM resource_reintegrations WHERE status='PENDING'"
                ).fetchone()[0]
            ),
            "protocol_receipts": count("resource_protocol_receipts"),
            "stages": count("resource_live_stages"),
        }
