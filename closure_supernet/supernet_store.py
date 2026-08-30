from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import Verdict
from .supernet_models import IntegrationStage, IntegrationStateCreate


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _loads(value: str | None, default: Any) -> Any:
    return default if value is None else json.loads(value)


class SupernetIntegrationStore:
    """Append-only state for the one continuous Supernet integration operation."""

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
        CREATE TABLE IF NOT EXISTS supernet_integration_events (
            seq INTEGER PRIMARY KEY AUTOINCREMENT,
            id TEXT NOT NULL UNIQUE,
            external_key TEXT UNIQUE,
            exact_source_ids TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            perspective_id TEXT,
            problem_id TEXT,
            action_id TEXT,
            form_label TEXT NOT NULL,
            language_label TEXT,
            visibility TEXT NOT NULL,
            capabilities TEXT NOT NULL,
            constraints TEXT NOT NULL,
            relation_hints TEXT NOT NULL,
            causal_predecessor_ids TEXT NOT NULL,
            parent_event_ids TEXT NOT NULL,
            affected_perspectives TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            adapter_label TEXT,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_supernet_integration_created
          ON supernet_integration_events(created_at,id);
        CREATE INDEX IF NOT EXISTS idx_supernet_integration_form
          ON supernet_integration_events(form_label,created_at);

        CREATE TABLE IF NOT EXISTS supernet_integration_states (
            id TEXT PRIMARY KEY,
            event_id TEXT NOT NULL REFERENCES supernet_integration_events(id),
            stage TEXT NOT NULL,
            verdict TEXT NOT NULL,
            reason TEXT NOT NULL,
            actor_id TEXT NOT NULL,
            rigidity_scope TEXT NOT NULL,
            rigidity_receipt TEXT,
            determined_form TEXT,
            unitary_path_partition TEXT,
            returned_resource_ids TEXT NOT NULL,
            successor_potential TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_supernet_states_event
          ON supernet_integration_states(event_id,created_at,id);

        CREATE TABLE IF NOT EXISTS supernet_field_stages (
            stage_index INTEGER PRIMARY KEY AUTOINCREMENT,
            id TEXT NOT NULL UNIQUE,
            previous_stage_id TEXT,
            trigger TEXT NOT NULL,
            trigger_event_id TEXT,
            event_ids TEXT NOT NULL,
            history_signature TEXT NOT NULL,
            limit_signature TEXT NOT NULL,
            event_count INTEGER NOT NULL,
            open_count INTEGER NOT NULL,
            admitted_count INTEGER NOT NULL,
            determined_count INTEGER NOT NULL,
            returned_count INTEGER NOT NULL,
            reopened_count INTEGER NOT NULL,
            summary TEXT NOT NULL,
            source_reverse_index TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_supernet_stages_created
          ON supernet_field_stages(stage_index,created_at);

        CREATE TABLE IF NOT EXISTS supernet_visual_closure_receipts (
            seq INTEGER PRIMARY KEY AUTOINCREMENT,
            id TEXT NOT NULL UNIQUE,
            source_event_id TEXT NOT NULL REFERENCES supernet_integration_events(id),
            input_signature TEXT NOT NULL UNIQUE,
            parent_receipt_ids TEXT NOT NULL,
            receipt TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_supernet_visual_closure_event
          ON supernet_visual_closure_receipts(source_event_id,seq);

        CREATE TABLE IF NOT EXISTS supernet_closure_ui_executions (
            fingerprint TEXT PRIMARY KEY,
            contract_id TEXT NOT NULL,
            action_id TEXT NOT NULL,
            perspective_id TEXT NOT NULL,
            focus_event_id TEXT,
            request_values TEXT NOT NULL,
            status TEXT NOT NULL,
            response TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_supernet_closure_ui_contract
          ON supernet_closure_ui_executions(contract_id,action_id,created_at);

        CREATE TABLE IF NOT EXISTS supernet_commitment_proposals (
            id TEXT PRIMARY KEY,
            proposal_event_id TEXT NOT NULL UNIQUE
              REFERENCES supernet_integration_events(id),
            intent_event_id TEXT NOT NULL
              REFERENCES supernet_integration_events(id),
            action_id TEXT,
            title TEXT NOT NULL DEFAULT 'Coordination proposal',
            proposed_by TEXT NOT NULL DEFAULT 'participant',
            exact_terms TEXT NOT NULL DEFAULT '',
            open_assumptions TEXT NOT NULL DEFAULT '[]',
            unity_selector_version TEXT NOT NULL DEFAULT 'nrrf837-unity-selector/v1',
            target_event_ids TEXT NOT NULL,
            required_participant_ids TEXT NOT NULL,
            resource_conditions TEXT NOT NULL,
            external_key TEXT UNIQUE,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_supernet_commitment_proposals_intent
          ON supernet_commitment_proposals(intent_event_id,created_at,id);
        CREATE INDEX IF NOT EXISTS idx_supernet_commitment_proposals_action
          ON supernet_commitment_proposals(action_id,created_at,id);

        CREATE TABLE IF NOT EXISTS supernet_commitment_decisions (
            seq INTEGER PRIMARY KEY AUTOINCREMENT,
            id TEXT NOT NULL UNIQUE,
            proposal_id TEXT NOT NULL
              REFERENCES supernet_commitment_proposals(id),
            decision_event_id TEXT NOT NULL UNIQUE
              REFERENCES supernet_integration_events(id),
            participant_id TEXT NOT NULL,
            decision TEXT NOT NULL
              CHECK(decision IN ('ACCEPT','REJECT','WITHDRAW')),
            resource_offers TEXT NOT NULL,
            constraints TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_supernet_commitment_decisions_proposal
          ON supernet_commitment_decisions(proposal_id,seq);
        CREATE INDEX IF NOT EXISTS idx_supernet_commitment_decisions_participant
          ON supernet_commitment_decisions(proposal_id,participant_id,seq);

        CREATE TABLE IF NOT EXISTS supernet_integrator_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            proposal_columns = {
                str(row["name"])
                for row in self._conn.execute(
                    "PRAGMA table_info(supernet_commitment_proposals)"
                ).fetchall()
            }
            proposal_migrations = {
                "title": (
                    "ALTER TABLE supernet_commitment_proposals ADD COLUMN "
                    "title TEXT NOT NULL DEFAULT 'Coordination proposal'"
                ),
                "proposed_by": (
                    "ALTER TABLE supernet_commitment_proposals ADD COLUMN "
                    "proposed_by TEXT NOT NULL DEFAULT 'participant'"
                ),
                "exact_terms": (
                    "ALTER TABLE supernet_commitment_proposals ADD COLUMN "
                    "exact_terms TEXT NOT NULL DEFAULT ''"
                ),
                "open_assumptions": (
                    "ALTER TABLE supernet_commitment_proposals ADD COLUMN "
                    "open_assumptions TEXT NOT NULL DEFAULT '[]'"
                ),
                "unity_selector_version": (
                    "ALTER TABLE supernet_commitment_proposals ADD COLUMN "
                    "unity_selector_version TEXT NOT NULL DEFAULT "
                    "'nrrf837-unity-selector/v1'"
                ),
            }
            for column, statement in proposal_migrations.items():
                if column not in proposal_columns:
                    self._conn.execute(statement)
            tables = {
                str(row["name"])
                for row in self._conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            if "occurrences" in tables:
                historical = self._conn.execute(
                    """SELECT id,proposal_event_id,title,proposed_by,exact_terms,
                    open_assumptions,resource_conditions,metadata
                    FROM supernet_commitment_proposals
                    WHERE exact_terms='' OR open_assumptions='[]'"""
                ).fetchall()
                for proposal in historical:
                    event = self._conn.execute(
                        """SELECT exact_source_ids,metadata
                        FROM supernet_integration_events WHERE id=?""",
                        (proposal["proposal_event_id"],),
                    ).fetchone()
                    if event is None:
                        continue
                    source_ids = _loads(event["exact_source_ids"], [])
                    occurrence = None
                    for source_id in source_ids:
                        occurrence = self._conn.execute(
                            "SELECT exact_text,metadata FROM occurrences WHERE id=?",
                            (str(source_id),),
                        ).fetchone()
                        if occurrence is not None:
                            break
                    event_metadata = _loads(event["metadata"], {})
                    occurrence_metadata = (
                        _loads(occurrence["metadata"], {})
                        if occurrence is not None
                        else {}
                    )
                    proposal_metadata = _loads(proposal["metadata"], {})
                    resource_conditions = set(
                        _loads(proposal["resource_conditions"], [])
                    )
                    recovered_assumptions = [
                        item
                        for item in (
                            event_metadata.get("open_assumptions")
                            or occurrence_metadata.get("open_assumptions")
                            or []
                        )
                        if item not in resource_conditions
                    ]
                    self._conn.execute(
                        """UPDATE supernet_commitment_proposals
                        SET title=?,proposed_by=?,exact_terms=?,open_assumptions=?
                        WHERE id=?""",
                        (
                            str(
                                proposal_metadata.get("title")
                                or proposal["title"]
                            ),
                            str(
                                proposal_metadata.get("proposed_by")
                                or proposal["proposed_by"]
                            ),
                            str(
                                proposal["exact_terms"]
                                or (
                                    occurrence["exact_text"]
                                    if occurrence is not None
                                    else ""
                                )
                            ),
                            (
                                proposal["open_assumptions"]
                                if proposal["open_assumptions"] != "[]"
                                else _json(recovered_assumptions)
                            ),
                            proposal["id"],
                        ),
                    )
            self._conn.commit()

    def create_event(self, data: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        external_key = data.get("external_key")
        if external_key:
            existing = self.get_by_external_key(str(external_key))
            if existing is not None:
                return existing, False
        event_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            cursor = self._conn.execute(
                """INSERT INTO supernet_integration_events(
                    id,external_key,exact_source_ids,authored_by,perspective_id,
                    problem_id,action_id,form_label,language_label,visibility,
                    capabilities,constraints,relation_hints,causal_predecessor_ids,
                    parent_event_ids,affected_perspectives,evidence_status,
                    adapter_label,metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    event_id,
                    external_key,
                    _json(data.get("exact_source_ids", [])),
                    data.get("authored_by", "participant"),
                    data.get("perspective_id"),
                    data.get("problem_id"),
                    data.get("action_id"),
                    data.get("form_label", "resource"),
                    data.get("language_label"),
                    data.get("visibility", "PUBLIC"),
                    _json(data.get("capabilities", [])),
                    _json(data.get("constraints", [])),
                    _json(data.get("relation_hints", [])),
                    _json(data.get("causal_predecessor_ids", [])),
                    _json(data.get("parent_event_ids", [])),
                    _json(data.get("affected_perspectives", [])),
                    data.get("evidence_status", "ORIGINAL_NOTE"),
                    data.get("adapter_label"),
                    _json(data.get("metadata", {})),
                    created_at,
                ),
            )
            self._conn.commit()
            seq = int(cursor.lastrowid)
        self.append_state(
            event_id,
            IntegrationStateCreate(
                stage=IntegrationStage.SOURCE_PRESERVED,
                verdict=Verdict.OPEN,
                reason="Exact source entered the one continuous Supernet field",
                actor_id=str(data.get("authored_by", "participant")),
                metadata={"initial": True, "event_seq": seq},
            ),
        )
        return self.get_event(event_id), True

    def get_by_external_key(self, external_key: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT id FROM supernet_integration_events WHERE external_key=?",
            (external_key,),
        ).fetchone()
        return None if row is None else self.get_event(str(row["id"]))

    def append_state(
        self, event_id: str, data: IntegrationStateCreate
    ) -> tuple[dict[str, Any], bool]:
        self._event_row(event_id)
        duplicate = self._conn.execute(
            """SELECT id FROM supernet_integration_states
            WHERE event_id=? AND stage=? AND verdict=? AND reason=? AND actor_id=?
            ORDER BY created_at DESC,id DESC LIMIT 1""",
            (
                event_id,
                str(data.stage),
                str(data.verdict),
                data.reason,
                data.actor_id,
            ),
        ).fetchone()
        if duplicate is not None:
            return self.get_state(str(duplicate["id"])), False
        state_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                """INSERT INTO supernet_integration_states(
                    id,event_id,stage,verdict,reason,actor_id,rigidity_scope,
                    rigidity_receipt,determined_form,unitary_path_partition,
                    returned_resource_ids,successor_potential,metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    state_id,
                    event_id,
                    str(data.stage),
                    str(data.verdict),
                    data.reason,
                    data.actor_id,
                    _json(data.rigidity_scope),
                    None if data.rigidity_receipt is None else _json(data.rigidity_receipt),
                    None if data.determined_form is None else _json(data.determined_form),
                    None
                    if data.unitary_path_partition is None
                    else _json(data.unitary_path_partition),
                    _json(data.returned_resource_ids),
                    _json(data.successor_potential),
                    _json(data.metadata),
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_state(state_id), True

    def get_state(self, state_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM supernet_integration_states WHERE id=?", (state_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Supernet integration state {state_id} not found")
        return self._decode_state(row)

    def list_states(self, event_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """SELECT * FROM supernet_integration_states WHERE event_id=?
            ORDER BY created_at,id""",
            (event_id,),
        ).fetchall()
        return [self._decode_state(row) for row in rows]

    def current_state(self, event_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            """SELECT * FROM supernet_integration_states WHERE event_id=?
            ORDER BY created_at DESC,id DESC LIMIT 1""",
            (event_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Supernet integration event {event_id} has no state")
        return self._decode_state(row)

    def get_event(self, event_id: str) -> dict[str, Any]:
        data = self._decode_event(self._event_row(event_id))
        history = self.list_states(event_id)
        current = history[-1]
        data["current_stage"] = current["stage"]
        data["current_verdict"] = current["verdict"]
        data["state_history"] = history
        return data

    def list_events(
        self, *, limit: int = 100_000, offset: int = 0
    ) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """SELECT id FROM supernet_integration_events
            ORDER BY seq LIMIT ? OFFSET ?""",
            (limit, offset),
        ).fetchall()
        return [self.get_event(str(row["id"])) for row in rows]

    def latest_event_sequence(self) -> int:
        row = self._conn.execute(
            "SELECT COALESCE(MAX(seq),0) AS seq FROM supernet_integration_events"
        ).fetchone()
        return 0 if row is None else int(row["seq"])

    def events_after(self, seq: int, limit: int = 500) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """SELECT id FROM supernet_integration_events WHERE seq>?
            ORDER BY seq LIMIT ?""",
            (seq, limit),
        ).fetchall()
        return [self.get_event(str(row["id"])) for row in rows]

    def create_commitment_proposal(
        self, data: dict[str, Any]
    ) -> tuple[dict[str, Any], bool]:
        """Index one source-preserved event as a non-transferable proposal."""

        proposal_event_id = str(data["proposal_event_id"])
        intent_event_id = str(data["intent_event_id"])
        self._event_row(proposal_event_id)
        self._event_row(intent_event_id)

        target_event_ids = [str(item) for item in data.get("target_event_ids", [])]
        for event_id in target_event_ids:
            self._event_row(event_id)
        required_participant_ids = [
            str(item).strip() for item in data.get("required_participant_ids", [])
        ]
        if any(not participant_id for participant_id in required_participant_ids):
            raise ValueError("required_participant_ids cannot contain an empty id")
        if len(set(required_participant_ids)) != len(required_participant_ids):
            raise ValueError("required_participant_ids must be unique")

        external_key_value = data.get("external_key")
        external_key = (
            None if not external_key_value else str(external_key_value)
        )
        proposal_id = str(data.get("id") or uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            if external_key is not None:
                existing = self._conn.execute(
                    """SELECT * FROM supernet_commitment_proposals
                    WHERE external_key=?""",
                    (external_key,),
                ).fetchone()
                if existing is not None:
                    return self.get_commitment_proposal(str(existing["id"])), False
            existing = self._conn.execute(
                """SELECT * FROM supernet_commitment_proposals
                WHERE proposal_event_id=?""",
                (proposal_event_id,),
            ).fetchone()
            if existing is not None:
                return self.get_commitment_proposal(str(existing["id"])), False
            self._conn.execute(
                """INSERT INTO supernet_commitment_proposals(
                    id,proposal_event_id,intent_event_id,action_id,title,proposed_by,
                    exact_terms,open_assumptions,unity_selector_version,target_event_ids,
                    required_participant_ids,resource_conditions,external_key,
                    metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    proposal_id,
                    proposal_event_id,
                    intent_event_id,
                    None if data.get("action_id") is None else str(data["action_id"]),
                    str(data.get("title") or "Coordination proposal"),
                    str(data.get("proposed_by") or "participant"),
                    str(data.get("exact_terms") or ""),
                    _json(data.get("open_assumptions", [])),
                    str(
                        data.get("unity_selector_version")
                        or "nrrf837-unity-selector/v1"
                    ),
                    _json(target_event_ids),
                    _json(required_participant_ids),
                    _json(data.get("resource_conditions", [])),
                    external_key,
                    _json(data.get("metadata", {})),
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_commitment_proposal(proposal_id), True

    def get_commitment_proposal(self, proposal_id: str) -> dict[str, Any]:
        proposal = self._decode_commitment_proposal(
            self._commitment_proposal_row(proposal_id)
        )
        return self._decorate_commitment_proposal(
            proposal, self.list_commitment_decisions(proposal_id)
        )

    def get_commitment_proposal_by_external_key(
        self, external_key: str
    ) -> dict[str, Any] | None:
        row = self._conn.execute(
            """SELECT * FROM supernet_commitment_proposals
            WHERE external_key=?""",
            (external_key,),
        ).fetchone()
        return (
            None
            if row is None
            else self.get_commitment_proposal(str(row["id"]))
        )

    def get_commitment_proposal_by_event(
        self, proposal_event_id: str
    ) -> dict[str, Any] | None:
        row = self._conn.execute(
            """SELECT * FROM supernet_commitment_proposals
            WHERE proposal_event_id=?""",
            (proposal_event_id,),
        ).fetchone()
        return (
            None
            if row is None
            else self.get_commitment_proposal(str(row["id"]))
        )

    def list_commitment_proposals(
        self,
        *,
        limit: int = 100_000,
        offset: int = 0,
        intent_event_id: str | None = None,
        action_id: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        parameters: list[Any] = []
        if intent_event_id is not None:
            clauses.append("intent_event_id=?")
            parameters.append(intent_event_id)
        if action_id is not None:
            clauses.append("action_id=?")
            parameters.append(action_id)
        where = "" if not clauses else " WHERE " + " AND ".join(clauses)
        rows = self._conn.execute(
            """SELECT id FROM supernet_commitment_proposals"""
            + where
            + " ORDER BY created_at,id LIMIT ? OFFSET ?",
            (*parameters, limit, offset),
        ).fetchall()
        return [self.get_commitment_proposal(str(row["id"])) for row in rows]

    def append_commitment_decision(
        self, proposal_id: str, data: dict[str, Any]
    ) -> tuple[dict[str, Any], bool]:
        """Append one required participant's source-preserved proposal decision."""

        proposal = self.get_commitment_proposal(proposal_id)
        participant_id = str(data.get("participant_id", "")).strip()
        if not participant_id:
            raise ValueError("participant_id is required")
        if participant_id not in proposal["required_participant_ids"]:
            raise ValueError(
                f"Participant {participant_id} is not required by proposal {proposal_id}"
            )
        decision = str(data.get("decision", "")).strip().upper()
        allowed = {"ACCEPT", "REJECT", "WITHDRAW"}
        if decision not in allowed:
            raise ValueError(
                "decision must be one of ACCEPT, REJECT, or WITHDRAW"
            )
        decision_event_id = str(data["decision_event_id"])
        self._event_row(decision_event_id)

        decision_id = str(data.get("id") or uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            existing = self._conn.execute(
                """SELECT * FROM supernet_commitment_decisions
                WHERE decision_event_id=?""",
                (decision_event_id,),
            ).fetchone()
            if existing is not None:
                current = self._decode_commitment_decision(existing)
                if (
                    current["proposal_id"] != proposal_id
                    or current["participant_id"] != participant_id
                    or current["decision"] != decision
                ):
                    raise ValueError(
                        "decision_event_id already indexes a different decision"
                    )
                return current, False
            self._conn.execute(
                """INSERT INTO supernet_commitment_decisions(
                    id,proposal_id,decision_event_id,participant_id,decision,
                    resource_offers,constraints,metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?)""",
                (
                    decision_id,
                    proposal_id,
                    decision_event_id,
                    participant_id,
                    decision,
                    _json(data.get("resource_offers", [])),
                    _json(data.get("constraints", [])),
                    _json(data.get("metadata", {})),
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_commitment_decision(decision_id), True

    def get_commitment_decision(self, decision_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            """SELECT * FROM supernet_commitment_decisions WHERE id=?""",
            (decision_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Supernet commitment decision {decision_id} not found")
        return self._decode_commitment_decision(row)

    def list_commitment_decisions(
        self, proposal_id: str
    ) -> list[dict[str, Any]]:
        self._commitment_proposal_row(proposal_id)
        rows = self._conn.execute(
            """SELECT * FROM supernet_commitment_decisions
            WHERE proposal_id=? ORDER BY seq""",
            (proposal_id,),
        ).fetchall()
        return [self._decode_commitment_decision(row) for row in rows]

    def commitment_proposal_receipt(self, proposal_id: str) -> dict[str, Any]:
        proposal = self.get_commitment_proposal(proposal_id)
        return {
            "proposal_id": proposal_id,
            "proposal": proposal,
            **{
                key: proposal[key]
                for key in (
                    "status",
                    "latest_decisions",
                    "decisions",
                    "decision_history",
                    "required_participant_ids",
                    "accepted_participant_ids",
                    "rejected_participant_ids",
                    "withdrawn_participant_ids",
                    "pending_participant_ids",
                    "binding",
                    "transferable",
                    "currency_issued",
                    "interactions_gated",
                    "security_enforcement",
                    "truth_issued",
                )
            },
        }

    def get_commitment_proposal_receipt(
        self, proposal_id: str
    ) -> dict[str, Any]:
        return self.commitment_proposal_receipt(proposal_id)

    def create_field_stage(self, data: dict[str, Any]) -> dict[str, Any]:
        stage_id = str(uuid.uuid4())
        previous = self.current_stage()
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                """INSERT INTO supernet_field_stages(
                    id,previous_stage_id,trigger,trigger_event_id,event_ids,
                    history_signature,limit_signature,event_count,open_count,
                    admitted_count,determined_count,returned_count,reopened_count,
                    summary,source_reverse_index,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    stage_id,
                    None if previous is None else previous["id"],
                    data["trigger"],
                    data.get("trigger_event_id"),
                    _json(data["event_ids"]),
                    data["history_signature"],
                    data["limit_signature"],
                    data["event_count"],
                    data["open_count"],
                    data["admitted_count"],
                    data["determined_count"],
                    data["returned_count"],
                    data["reopened_count"],
                    _json(data["summary"]),
                    _json(data["source_reverse_index"]),
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_stage(stage_id)

    def get_stage(self, stage_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM supernet_field_stages WHERE id=?", (stage_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Supernet field stage {stage_id} not found")
        return self._decode_stage(row)

    def current_stage(self) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT * FROM supernet_field_stages ORDER BY stage_index DESC LIMIT 1"
        ).fetchone()
        return None if row is None else self._decode_stage(row)

    def list_stages(self, limit: int = 1000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """SELECT * FROM supernet_field_stages
            ORDER BY stage_index DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [self._decode_stage(row) for row in reversed(rows)]

    def append_visual_closure_receipt(
        self,
        *,
        source_event_id: str,
        input_signature: str,
        parent_receipt_ids: list[str],
        receipt: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        """Append one SLEARN–mirror–AI–tokenomic closure receipt.

        The input signature makes repeated Sense of an unchanged event
        idempotent while a return or reopening produces a new receipt.
        """

        self._event_row(source_event_id)
        with self._lock:
            existing = self._conn.execute(
                """SELECT * FROM supernet_visual_closure_receipts
                WHERE input_signature=?""",
                (input_signature,),
            ).fetchone()
            if existing is not None:
                return self._decode_visual_closure_receipt(existing), False

            receipt_id = str(uuid.uuid4())
            created_at = utcnow()
            cursor = self._conn.execute(
                """INSERT INTO supernet_visual_closure_receipts(
                    id,source_event_id,input_signature,parent_receipt_ids,
                    receipt,created_at
                ) VALUES(?,?,?,?,?,?)""",
                (
                    receipt_id,
                    source_event_id,
                    input_signature,
                    _json(parent_receipt_ids),
                    _json(receipt),
                    created_at,
                ),
            )
            seq = int(cursor.lastrowid)
            completed = dict(receipt)
            completed["id"] = receipt_id
            completed["seq"] = seq
            completed["created_at"] = created_at
            completed["input_signature"] = input_signature
            completed["parent_receipt_ids"] = list(parent_receipt_ids)
            operational = dict(completed.get("operational_closure", {}))
            operational["receipt_persisted"] = True
            operational["all_desired_functions_in_this_occurrence"] = all(
                operational.get(key) is True
                for key in (
                    "black_mirror_sensed",
                    "slearn_memory_committed",
                    "ai_translation_executed",
                    "tokenomic_resources_derived",
                    "visual_network_derived",
                    "network_return_open",
                    "receipt_persisted",
                )
            )
            completed["operational_closure"] = operational
            self._conn.execute(
                """UPDATE supernet_visual_closure_receipts
                SET receipt=? WHERE id=?""",
                (_json(completed), receipt_id),
            )
            self._conn.commit()
        return self.get_visual_closure_receipt(receipt_id), True

    def get_visual_closure_receipt(self, receipt_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM supernet_visual_closure_receipts WHERE id=?",
            (receipt_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Visual closure receipt {receipt_id} not found")
        return self._decode_visual_closure_receipt(row)

    def claim_closure_ui_execution(
        self,
        *,
        fingerprint: str,
        contract_id: str,
        action_id: str,
        perspective_id: str,
        focus_event_id: str | None,
        request_values: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        """Persist a one-shot claim before a closure UI mutation begins."""

        with self._lock, self._conn:
            existing = self._conn.execute(
                """SELECT * FROM supernet_closure_ui_executions
                   WHERE fingerprint=?""",
                (fingerprint,),
            ).fetchone()
            if existing is not None:
                return self._decode_closure_ui_execution(existing), False
            now = utcnow()
            self._conn.execute(
                """INSERT INTO supernet_closure_ui_executions(
                       fingerprint,contract_id,action_id,perspective_id,
                       focus_event_id,request_values,status,response,
                       created_at,completed_at
                   ) VALUES(?,?,?,?,?,?,?,NULL,?,NULL)""",
                (
                    fingerprint,
                    contract_id,
                    action_id,
                    perspective_id,
                    focus_event_id,
                    _json(request_values),
                    "EXECUTING",
                    now,
                ),
            )
            row = self._conn.execute(
                """SELECT * FROM supernet_closure_ui_executions
                   WHERE fingerprint=?""",
                (fingerprint,),
            ).fetchone()
        assert row is not None
        return self._decode_closure_ui_execution(row), True

    def get_closure_ui_execution(
        self, fingerprint: str
    ) -> dict[str, Any] | None:
        """Read a durable execution result without creating a new claim."""

        row = self._conn.execute(
            """SELECT * FROM supernet_closure_ui_executions
               WHERE fingerprint=?""",
            (fingerprint,),
        ).fetchone()
        return (
            None
            if row is None
            else self._decode_closure_ui_execution(row)
        )

    def complete_closure_ui_execution(
        self,
        fingerprint: str,
        response: dict[str, Any],
    ) -> dict[str, Any]:
        with self._lock, self._conn:
            self._conn.execute(
                """UPDATE supernet_closure_ui_executions
                   SET status='COMPLETED',response=?,completed_at=?
                   WHERE fingerprint=? AND status='EXECUTING'""",
                (_json(response), utcnow(), fingerprint),
            )
            row = self._conn.execute(
                """SELECT * FROM supernet_closure_ui_executions
                   WHERE fingerprint=?""",
                (fingerprint,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Closure UI execution {fingerprint} not found")
        return self._decode_closure_ui_execution(row)

    def fail_closure_ui_execution(
        self,
        fingerprint: str,
        detail: str,
    ) -> None:
        """Seal a failed claim so a partial mutation cannot be replayed."""

        with self._lock, self._conn:
            self._conn.execute(
                """UPDATE supernet_closure_ui_executions
                   SET status='FAILED',response=?,completed_at=?
                   WHERE fingerprint=? AND status='EXECUTING'""",
                (_json({"detail": detail}), utcnow(), fingerprint),
            )

    def latest_visual_closure_receipt(
        self, source_event_id: str
    ) -> dict[str, Any] | None:
        row = self._conn.execute(
            """SELECT * FROM supernet_visual_closure_receipts
            WHERE source_event_id=? ORDER BY seq DESC LIMIT 1""",
            (source_event_id,),
        ).fetchone()
        return None if row is None else self._decode_visual_closure_receipt(row)

    def list_visual_closure_receipts(
        self, limit: int = 100_000
    ) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """SELECT * FROM supernet_visual_closure_receipts
            ORDER BY seq LIMIT ?""",
            (limit,),
        ).fetchall()
        return [self._decode_visual_closure_receipt(row) for row in rows]

    def visual_closure_event_ids(self) -> set[str]:
        rows = self._conn.execute(
            "SELECT DISTINCT source_event_id FROM supernet_visual_closure_receipts"
        ).fetchall()
        return {str(row["source_event_id"]) for row in rows}

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO supernet_integrator_state(key,value,updated_at)
                VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET
                value=excluded.value,updated_at=excluded.updated_at""",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state_value(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute(
            "SELECT value FROM supernet_integrator_state WHERE key=?", (key,)
        ).fetchone()
        return default if row is None else _loads(row["value"], default)

    def stats(self) -> dict[str, int]:
        events = int(
            self._conn.execute(
                "SELECT COUNT(*) AS n FROM supernet_integration_events"
            ).fetchone()["n"]
        )
        states = int(
            self._conn.execute(
                "SELECT COUNT(*) AS n FROM supernet_integration_states"
            ).fetchone()["n"]
        )
        stages = int(
            self._conn.execute(
                "SELECT COUNT(*) AS n FROM supernet_field_stages"
            ).fetchone()["n"]
        )
        visual_closure_receipts = int(
            self._conn.execute(
                "SELECT COUNT(*) AS n FROM supernet_visual_closure_receipts"
            ).fetchone()["n"]
        )
        commitment_proposals = int(
            self._conn.execute(
                "SELECT COUNT(*) AS n FROM supernet_commitment_proposals"
            ).fetchone()["n"]
        )
        commitment_decisions = int(
            self._conn.execute(
                "SELECT COUNT(*) AS n FROM supernet_commitment_decisions"
            ).fetchone()["n"]
        )
        current: dict[str, int] = {}
        verdicts: dict[str, int] = {}
        for event in self.list_events(limit=200_000):
            current[event["current_stage"]] = current.get(event["current_stage"], 0) + 1
            verdicts[event["current_verdict"]] = verdicts.get(event["current_verdict"], 0) + 1
        commitment_statuses = {
            status: 0
            for status in (
                "PROPOSED",
                "PARTIAL",
                "ACCEPTED",
                "REJECTED",
                "WITHDRAWN",
            )
        }
        for proposal in self.list_commitment_proposals(limit=200_000):
            status = proposal["status"]
            commitment_statuses[status] += 1
        return {
            "events": events,
            "states": states,
            "stages": stages,
            "visual_closure_receipts": visual_closure_receipts,
            "commitment_proposals": commitment_proposals,
            "commitment_decisions": commitment_decisions,
            **{f"stage_{key.lower()}": value for key, value in current.items()},
            **{f"verdict_{key.lower()}": value for key, value in verdicts.items()},
            **{
                f"commitment_status_{key.lower()}": value
                for key, value in commitment_statuses.items()
            },
        }

    def _event_row(self, event_id: str) -> sqlite3.Row:
        row = self._conn.execute(
            "SELECT * FROM supernet_integration_events WHERE id=?", (event_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Supernet integration event {event_id} not found")
        return row

    def _commitment_proposal_row(self, proposal_id: str) -> sqlite3.Row:
        row = self._conn.execute(
            "SELECT * FROM supernet_commitment_proposals WHERE id=?", (proposal_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Supernet commitment proposal {proposal_id} not found")
        return row

    @staticmethod
    def _decorate_commitment_proposal(
        proposal: dict[str, Any], history: list[dict[str, Any]]
    ) -> dict[str, Any]:
        latest: dict[str, dict[str, Any]] = {}
        for item in history:
            latest[item["participant_id"]] = item

        required = proposal["required_participant_ids"]
        latest_required = {
            participant_id: latest[participant_id]
            for participant_id in required
            if participant_id in latest
        }
        accepted = [
            participant_id
            for participant_id in required
            if latest.get(participant_id, {}).get("decision") == "ACCEPT"
        ]
        rejected = [
            participant_id
            for participant_id in required
            if latest.get(participant_id, {}).get("decision") == "REJECT"
        ]
        withdrawn = [
            participant_id
            for participant_id in required
            if latest.get(participant_id, {}).get("decision") == "WITHDRAW"
        ]
        pending = [
            participant_id
            for participant_id in required
            if participant_id not in latest
        ]
        if rejected:
            status = "REJECTED"
        elif withdrawn:
            status = "WITHDRAWN"
        elif required and len(accepted) == len(required):
            status = "ACCEPTED"
        elif latest_required:
            status = "PARTIAL"
        else:
            status = "PROPOSED"
        consent_updated_at = max(
            (str(item.get("created_at") or "") for item in latest_required.values()),
            default=None,
        )
        unanimous_acceptance_at = (
            consent_updated_at
            if status == "ACCEPTED" and len(accepted) == len(required)
            else None
        )

        return {
            **proposal,
            "status": status,
            "latest_decisions": latest_required,
            "decisions": list(latest_required.values()),
            "decision_history": list(history),
            "accepted_participant_ids": accepted,
            "rejected_participant_ids": rejected,
            "withdrawn_participant_ids": withdrawn,
            "pending_participant_ids": pending,
            "consent_updated_at": consent_updated_at,
            "unanimous_acceptance_at": unanimous_acceptance_at,
            "binding": False,
            "transferable": False,
            "currency_issued": False,
            "interactions_gated": False,
            "security_enforcement": "OPEN",
            "truth_issued": False,
        }

    @staticmethod
    def _decode_event(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in (
            ("exact_source_ids", []),
            ("capabilities", []),
            ("constraints", []),
            ("relation_hints", []),
            ("causal_predecessor_ids", []),
            ("parent_event_ids", []),
            ("affected_perspectives", []),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    @staticmethod
    def _decode_state(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in (
            ("rigidity_scope", []),
            ("returned_resource_ids", []),
            ("successor_potential", []),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        for key in ("rigidity_receipt", "determined_form", "unitary_path_partition"):
            data[key] = _loads(data[key], None)
        return data

    @staticmethod
    def _decode_commitment_proposal(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in (
            ("target_event_ids", []),
            ("required_participant_ids", []),
            ("resource_conditions", []),
            ("open_assumptions", []),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    @staticmethod
    def _decode_commitment_decision(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in (
            ("resource_offers", []),
            ("constraints", []),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    @staticmethod
    def _decode_stage(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in (
            ("event_ids", []),
            ("summary", {}),
            ("source_reverse_index", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    @staticmethod
    def _decode_visual_closure_receipt(row: sqlite3.Row) -> dict[str, Any]:
        receipt = _loads(row["receipt"], {})
        receipt.setdefault("id", str(row["id"]))
        receipt.setdefault("seq", int(row["seq"]))
        receipt.setdefault("source_event_id", str(row["source_event_id"]))
        receipt.setdefault("input_signature", str(row["input_signature"]))
        receipt.setdefault("parent_receipt_ids", _loads(row["parent_receipt_ids"], []))
        receipt.setdefault("created_at", str(row["created_at"]))
        return receipt

    @staticmethod
    def _decode_closure_ui_execution(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "fingerprint": str(row["fingerprint"]),
            "contract_id": str(row["contract_id"]),
            "action_id": str(row["action_id"]),
            "perspective_id": str(row["perspective_id"]),
            "focus_event_id": (
                None
                if row["focus_event_id"] is None
                else str(row["focus_event_id"])
            ),
            "request_values": _loads(row["request_values"], {}),
            "status": str(row["status"]),
            "response": _loads(row["response"], None),
            "created_at": str(row["created_at"]),
            "completed_at": (
                None
                if row["completed_at"] is None
                else str(row["completed_at"])
            ),
        }
