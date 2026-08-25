from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .living_models import (
    ActionState,
    CollectiveActionCreate,
    InteractionCreate,
    ParticipantCreate,
    PerspectiveCreate,
    ProblemCreate,
    ProblemState,
    ReintegrationStatus,
)
from .models import Verdict


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _loads(value: str | None, default: Any) -> Any:
    if value is None:
        return default
    return json.loads(value)


class LivingNetworkStore:
    """Persistent relative forms for the public living network.

    Exact authored text remains in the canonical occurrences table. This store
    keeps append-only state transitions and relations among participants,
    perspectives, real problems, interactions-as-solutions, collective actions,
    returned consequences, and reintegration proposals.
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
        CREATE TABLE IF NOT EXISTS living_participants (
            id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            public_key TEXT,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS living_perspectives (
            id TEXT PRIMARY KEY,
            participant_id TEXT NOT NULL REFERENCES living_participants(id),
            label TEXT NOT NULL,
            description TEXT NOT NULL,
            visibility TEXT NOT NULL,
            parent_perspective_id TEXT REFERENCES living_perspectives(id),
            source_occurrence_id TEXT REFERENCES occurrences(id),
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS living_problems (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL REFERENCES occurrences(id),
            title TEXT NOT NULL,
            situations TEXT NOT NULL,
            created_by TEXT NOT NULL REFERENCES living_participants(id),
            perspective_id TEXT REFERENCES living_perspectives(id),
            visibility TEXT NOT NULL,
            affected_perspectives TEXT NOT NULL,
            language_label TEXT,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS living_problem_states (
            id TEXT PRIMARY KEY,
            problem_id TEXT NOT NULL REFERENCES living_problems(id),
            state TEXT NOT NULL,
            reason TEXT NOT NULL,
            actor_id TEXT NOT NULL REFERENCES living_participants(id),
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_living_problem_states
            ON living_problem_states(problem_id, created_at);

        CREATE TABLE IF NOT EXISTS living_interactions (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL REFERENCES occurrences(id),
            from_problem_id TEXT NOT NULL REFERENCES living_problems(id),
            to_problem_id TEXT NOT NULL REFERENCES living_problems(id),
            author_id TEXT NOT NULL REFERENCES living_participants(id),
            kind TEXT NOT NULL,
            source_perspective_id TEXT REFERENCES living_perspectives(id),
            target_perspective_id TEXT REFERENCES living_perspectives(id),
            affected_perspectives TEXT NOT NULL,
            preserves TEXT NOT NULL,
            transforms TEXT NOT NULL,
            omits TEXT NOT NULL,
            parent_interaction_id TEXT REFERENCES living_interactions(id),
            visibility TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_living_interactions_from
            ON living_interactions(from_problem_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_living_interactions_to
            ON living_interactions(to_problem_id, created_at);

        CREATE TABLE IF NOT EXISTS living_solution_receipts (
            id TEXT PRIMARY KEY,
            interaction_id TEXT NOT NULL UNIQUE REFERENCES living_interactions(id),
            problem_id TEXT NOT NULL REFERENCES living_problems(id),
            target_problem_id TEXT NOT NULL REFERENCES living_problems(id),
            verdict TEXT NOT NULL,
            reason TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS living_problem_notes (
            id TEXT PRIMARY KEY,
            problem_id TEXT NOT NULL REFERENCES living_problems(id),
            interaction_id TEXT NOT NULL UNIQUE REFERENCES living_interactions(id),
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS living_actions (
            id TEXT PRIMARY KEY,
            problem_id TEXT NOT NULL REFERENCES living_problems(id),
            occurrence_id TEXT NOT NULL REFERENCES occurrences(id),
            title TEXT NOT NULL,
            created_by TEXT NOT NULL REFERENCES living_participants(id),
            participant_ids TEXT NOT NULL,
            affected_perspectives TEXT NOT NULL,
            open_assumptions TEXT NOT NULL,
            visibility TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS living_action_states (
            id TEXT PRIMARY KEY,
            action_id TEXT NOT NULL REFERENCES living_actions(id),
            state TEXT NOT NULL,
            reason TEXT NOT NULL,
            actor_id TEXT NOT NULL REFERENCES living_participants(id),
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_living_action_states
            ON living_action_states(action_id, created_at);

        CREATE TABLE IF NOT EXISTS living_action_returns (
            id TEXT PRIMARY KEY,
            action_id TEXT NOT NULL REFERENCES living_actions(id),
            occurrence_id TEXT NOT NULL REFERENCES occurrences(id),
            authored_by TEXT NOT NULL REFERENCES living_participants(id),
            evidence_status TEXT NOT NULL,
            affected_perspectives TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_living_action_returns
            ON living_action_returns(action_id, created_at);

        CREATE TABLE IF NOT EXISTS living_reintegration_proposals (
            id TEXT PRIMARY KEY,
            problem_id TEXT NOT NULL REFERENCES living_problems(id),
            action_id TEXT NOT NULL REFERENCES living_actions(id),
            return_id TEXT NOT NULL UNIQUE REFERENCES living_action_returns(id),
            source_occurrence_id TEXT NOT NULL REFERENCES occurrences(id),
            target_occurrence_id TEXT NOT NULL REFERENCES occurrences(id),
            candidate_relation_id TEXT NOT NULL REFERENCES candidate_relations(id),
            proposal_text TEXT NOT NULL,
            preserved TEXT NOT NULL,
            changed TEXT NOT NULL,
            open_questions TEXT NOT NULL,
            affected_perspectives TEXT NOT NULL,
            generated_by TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS living_reintegration_decisions (
            id TEXT PRIMARY KEY,
            proposal_id TEXT NOT NULL REFERENCES living_reintegration_proposals(id),
            status TEXT NOT NULL,
            reason TEXT NOT NULL,
            author_id TEXT NOT NULL REFERENCES living_participants(id),
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_living_reintegration_decisions
            ON living_reintegration_decisions(proposal_id, created_at);

        CREATE TABLE IF NOT EXISTS living_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    def create_participant(self, data: ParticipantCreate) -> dict[str, Any]:
        participant_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                "INSERT INTO living_participants VALUES(?,?,?,?,?)",
                (participant_id, data.display_name, data.public_key, _json(data.metadata), created_at),
            )
            self._conn.commit()
        return self.get_participant(participant_id)

    def get_participant(self, participant_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM living_participants WHERE id=?", (participant_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Participant {participant_id} not found")
        data = dict(row)
        data["metadata"] = _loads(data["metadata"], {})
        return data

    def list_participants(self, limit: int = 1000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM living_participants ORDER BY created_at,id LIMIT ?", (limit,)
        ).fetchall()
        result = []
        for row in rows:
            data = dict(row)
            data["metadata"] = _loads(data["metadata"], {})
            result.append(data)
        return result

    def create_perspective(self, data: PerspectiveCreate) -> dict[str, Any]:
        self.get_participant(data.participant_id)
        if data.parent_perspective_id:
            self.get_perspective(data.parent_perspective_id)
        perspective_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                "INSERT INTO living_perspectives VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    perspective_id,
                    data.participant_id,
                    data.label,
                    data.description,
                    str(data.visibility),
                    data.parent_perspective_id,
                    data.source_occurrence_id,
                    _json(data.metadata),
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_perspective(perspective_id)

    def get_perspective(self, perspective_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM living_perspectives WHERE id=?", (perspective_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Perspective {perspective_id} not found")
        data = dict(row)
        data["metadata"] = _loads(data["metadata"], {})
        return data

    def list_perspectives(self, limit: int = 5000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM living_perspectives ORDER BY created_at,id LIMIT ?", (limit,)
        ).fetchall()
        result = []
        for row in rows:
            data = dict(row)
            data["metadata"] = _loads(data["metadata"], {})
            result.append(data)
        return result

    def create_problem(self, data: ProblemCreate, occurrence_id: str) -> dict[str, Any]:
        self.get_participant(data.created_by)
        if data.perspective_id:
            self.get_perspective(data.perspective_id)
        problem_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                "INSERT INTO living_problems VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    problem_id,
                    occurrence_id,
                    data.title,
                    _json(data.situations),
                    data.created_by,
                    data.perspective_id,
                    str(data.visibility),
                    _json(data.affected_perspectives),
                    data.language_label,
                    _json(data.metadata),
                    created_at,
                ),
            )
            self._conn.execute(
                "INSERT INTO living_problem_states VALUES(?,?,?,?,?,?)",
                (
                    str(uuid.uuid4()),
                    problem_id,
                    str(ProblemState.OPEN),
                    "A real problem has been admitted with discretion remaining",
                    data.created_by,
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_problem(problem_id)

    def transition_problem(
        self, problem_id: str, state: ProblemState, reason: str, actor_id: str
    ) -> dict[str, Any]:
        self.get_problem(problem_id)
        self.get_participant(actor_id)
        with self._lock:
            self._conn.execute(
                "INSERT INTO living_problem_states VALUES(?,?,?,?,?,?)",
                (str(uuid.uuid4()), problem_id, str(state), reason, actor_id, utcnow()),
            )
            self._conn.commit()
        return self.get_problem(problem_id)

    def _current_problem_state(self, problem_id: str) -> str:
        row = self._conn.execute(
            "SELECT state FROM living_problem_states WHERE problem_id=? ORDER BY created_at DESC,id DESC LIMIT 1",
            (problem_id,),
        ).fetchone()
        return str(row["state"]) if row else str(ProblemState.OPEN)

    def get_problem(self, problem_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM living_problems WHERE id=?", (problem_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Problem {problem_id} not found")
        data = dict(row)
        for key, default in (
            ("situations", []),
            ("affected_perspectives", []),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        data["current_state"] = self._current_problem_state(problem_id)
        return data

    def list_problems(self, limit: int = 5000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT id FROM living_problems ORDER BY created_at,id LIMIT ?", (limit,)
        ).fetchall()
        return [self.get_problem(str(row["id"])) for row in rows]

    def create_interaction(
        self,
        data: InteractionCreate,
        occurrence_id: str,
        *,
        verdict: Verdict = Verdict.OPEN,
        reason: str = "A solution is constituted by this interaction; settlement remains provisional",
    ) -> dict[str, Any]:
        self.get_participant(data.author_id)
        self.get_problem(data.from_problem_id)
        target_problem_id = data.to_problem_id or data.from_problem_id
        self.get_problem(target_problem_id)
        if data.source_perspective_id:
            self.get_perspective(data.source_perspective_id)
        if data.target_perspective_id:
            self.get_perspective(data.target_perspective_id)
        interaction_id = str(uuid.uuid4())
        receipt_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                "INSERT INTO living_interactions VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    interaction_id,
                    occurrence_id,
                    data.from_problem_id,
                    target_problem_id,
                    data.author_id,
                    str(data.kind),
                    data.source_perspective_id,
                    data.target_perspective_id,
                    _json(data.affected_perspectives),
                    _json(data.preserves),
                    _json(data.transforms),
                    _json(data.omits),
                    data.parent_interaction_id,
                    str(data.visibility),
                    _json(data.metadata),
                    created_at,
                ),
            )
            self._conn.execute(
                "INSERT INTO living_solution_receipts VALUES(?,?,?,?,?,?,?)",
                (
                    receipt_id,
                    interaction_id,
                    data.from_problem_id,
                    target_problem_id,
                    str(verdict),
                    reason,
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_interaction(interaction_id)

    def create_problem_note(self, problem_id: str, interaction_id: str) -> dict[str, Any]:
        self.get_problem(problem_id)
        self.get_interaction(interaction_id)
        note_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                "INSERT INTO living_problem_notes VALUES(?,?,?,?)",
                (note_id, problem_id, interaction_id, created_at),
            )
            self._conn.commit()
        return {
            "id": note_id,
            "problem_id": problem_id,
            "interaction_id": interaction_id,
            "created_at": created_at,
        }

    def get_solution_receipt_by_interaction(self, interaction_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM living_solution_receipts WHERE interaction_id=?", (interaction_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Solution receipt for interaction {interaction_id} not found")
        return dict(row)

    def get_interaction(self, interaction_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM living_interactions WHERE id=?", (interaction_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Interaction {interaction_id} not found")
        data = dict(row)
        for key, default in (
            ("affected_perspectives", []),
            ("preserves", []),
            ("transforms", []),
            ("omits", []),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        data["solution_receipt_id"] = self.get_solution_receipt_by_interaction(interaction_id)["id"]
        return data

    def list_interactions(
        self, *, problem_id: str | None = None, limit: int = 10_000
    ) -> list[dict[str, Any]]:
        if problem_id:
            rows = self._conn.execute(
                "SELECT id FROM living_interactions WHERE from_problem_id=? OR to_problem_id=? ORDER BY created_at,id LIMIT ?",
                (problem_id, problem_id, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT id FROM living_interactions ORDER BY created_at,id LIMIT ?", (limit,)
            ).fetchall()
        return [self.get_interaction(str(row["id"])) for row in rows]

    def list_solution_receipts(self, limit: int = 10_000) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self._conn.execute(
                "SELECT * FROM living_solution_receipts ORDER BY created_at,id LIMIT ?",
                (limit,),
            ).fetchall()
        ]

    def create_action(
        self, data: CollectiveActionCreate, occurrence_id: str
    ) -> dict[str, Any]:
        self.get_problem(data.problem_id)
        self.get_participant(data.created_by)
        for participant_id in data.participant_ids:
            self.get_participant(participant_id)
        action_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                "INSERT INTO living_actions VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    action_id,
                    data.problem_id,
                    occurrence_id,
                    data.title,
                    data.created_by,
                    _json(data.participant_ids),
                    _json(data.affected_perspectives),
                    _json(data.open_assumptions),
                    str(data.visibility),
                    _json(data.metadata),
                    created_at,
                ),
            )
            self._conn.execute(
                "INSERT INTO living_action_states VALUES(?,?,?,?,?,?)",
                (
                    str(uuid.uuid4()),
                    action_id,
                    str(ActionState.PROPOSED),
                    "Collective action proposed from a real problem and its interactions",
                    data.created_by,
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_action(action_id)

    def transition_action(
        self, action_id: str, state: ActionState, reason: str, actor_id: str
    ) -> dict[str, Any]:
        self.get_action(action_id)
        self.get_participant(actor_id)
        with self._lock:
            self._conn.execute(
                "INSERT INTO living_action_states VALUES(?,?,?,?,?,?)",
                (str(uuid.uuid4()), action_id, str(state), reason, actor_id, utcnow()),
            )
            self._conn.commit()
        return self.get_action(action_id)

    def _current_action_state(self, action_id: str) -> str:
        row = self._conn.execute(
            "SELECT state FROM living_action_states WHERE action_id=? ORDER BY created_at DESC,id DESC LIMIT 1",
            (action_id,),
        ).fetchone()
        return str(row["state"]) if row else str(ActionState.PROPOSED)

    def get_action(self, action_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM living_actions WHERE id=?", (action_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Collective action {action_id} not found")
        data = dict(row)
        for key, default in (
            ("participant_ids", []),
            ("affected_perspectives", []),
            ("open_assumptions", []),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        data["current_state"] = self._current_action_state(action_id)
        return data

    def list_actions(self, limit: int = 5000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT id FROM living_actions ORDER BY created_at,id LIMIT ?", (limit,)
        ).fetchall()
        return [self.get_action(str(row["id"])) for row in rows]

    def create_action_return(
        self,
        action_id: str,
        occurrence_id: str,
        authored_by: str,
        evidence_status: str,
        affected_perspectives: list[str],
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        self.get_action(action_id)
        self.get_participant(authored_by)
        return_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                "INSERT INTO living_action_returns VALUES(?,?,?,?,?,?,?,?)",
                (
                    return_id,
                    action_id,
                    occurrence_id,
                    authored_by,
                    evidence_status,
                    _json(affected_perspectives),
                    _json(metadata),
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_action_return(return_id)

    def get_action_return(self, return_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM living_action_returns WHERE id=?", (return_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Action return {return_id} not found")
        data = dict(row)
        data["affected_perspectives"] = _loads(data["affected_perspectives"], [])
        data["metadata"] = _loads(data["metadata"], {})
        return data

    def list_action_returns(
        self, *, action_id: str | None = None, limit: int = 10_000
    ) -> list[dict[str, Any]]:
        if action_id:
            rows = self._conn.execute(
                "SELECT id FROM living_action_returns WHERE action_id=? ORDER BY created_at,id LIMIT ?",
                (action_id, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT id FROM living_action_returns ORDER BY created_at,id LIMIT ?", (limit,)
            ).fetchall()
        return [self.get_action_return(str(row["id"])) for row in rows]

    def reintegration_exists_for_return(self, return_id: str) -> bool:
        return (
            self._conn.execute(
                "SELECT 1 FROM living_reintegration_proposals WHERE return_id=? LIMIT 1",
                (return_id,),
            ).fetchone()
            is not None
        )

    def create_reintegration_proposal(
        self,
        *,
        problem_id: str,
        action_id: str,
        return_id: str,
        source_occurrence_id: str,
        target_occurrence_id: str,
        candidate_relation_id: str,
        proposal_text: str,
        preserved: list[str],
        changed: list[str],
        open_questions: list[str],
        affected_perspectives: list[str],
        generated_by: str,
    ) -> dict[str, Any]:
        if self.reintegration_exists_for_return(return_id):
            row = self._conn.execute(
                "SELECT id FROM living_reintegration_proposals WHERE return_id=?",
                (return_id,),
            ).fetchone()
            return self.get_reintegration_proposal(str(row["id"]))
        proposal_id = str(uuid.uuid4())
        created_at = utcnow()
        with self._lock:
            self._conn.execute(
                "INSERT INTO living_reintegration_proposals VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    proposal_id,
                    problem_id,
                    action_id,
                    return_id,
                    source_occurrence_id,
                    target_occurrence_id,
                    candidate_relation_id,
                    proposal_text,
                    _json(preserved),
                    _json(changed),
                    _json(open_questions),
                    _json(affected_perspectives),
                    generated_by,
                    created_at,
                ),
            )
            self._conn.commit()
        return self.get_reintegration_proposal(proposal_id)

    def decide_reintegration(
        self,
        proposal_id: str,
        status: ReintegrationStatus,
        reason: str,
        author_id: str,
    ) -> dict[str, Any]:
        self.get_reintegration_proposal(proposal_id)
        self.get_participant(author_id)
        with self._lock:
            self._conn.execute(
                "INSERT INTO living_reintegration_decisions VALUES(?,?,?,?,?,?)",
                (str(uuid.uuid4()), proposal_id, str(status), reason, author_id, utcnow()),
            )
            self._conn.commit()
        return self.get_reintegration_proposal(proposal_id)

    def _current_reintegration_decision(self, proposal_id: str) -> tuple[str, str | None]:
        row = self._conn.execute(
            "SELECT status,reason FROM living_reintegration_decisions WHERE proposal_id=? ORDER BY created_at DESC,id DESC LIMIT 1",
            (proposal_id,),
        ).fetchone()
        if not row:
            return str(ReintegrationStatus.OPEN), None
        return str(row["status"]), str(row["reason"])

    def get_reintegration_proposal(self, proposal_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM living_reintegration_proposals WHERE id=?", (proposal_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Reintegration proposal {proposal_id} not found")
        data = dict(row)
        for key in ("preserved", "changed", "open_questions", "affected_perspectives"):
            data[key] = _loads(data[key], [])
        status, reason = self._current_reintegration_decision(proposal_id)
        data["current_status"] = status
        data["current_reason"] = reason
        return data

    def list_reintegration_proposals(self, limit: int = 10_000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT id FROM living_reintegration_proposals ORDER BY created_at,id LIMIT ?", (limit,)
        ).fetchall()
        return [self.get_reintegration_proposal(str(row["id"])) for row in rows]

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO living_state(key,value,updated_at) VALUES(?,?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute(
            "SELECT value FROM living_state WHERE key=?", (key,)
        ).fetchone()
        return _loads(row["value"], default) if row else default

    def stats(self) -> dict[str, int]:
        tables = {
            "participants": "living_participants",
            "perspectives": "living_perspectives",
            "problems": "living_problems",
            "interactions": "living_interactions",
            "solutions": "living_solution_receipts",
            "actions": "living_actions",
            "returns": "living_action_returns",
            "reintegration": "living_reintegration_proposals",
        }
        return {
            name: int(self._conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"])
            for name, table in tables.items()
        }
