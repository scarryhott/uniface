from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .hardware_models import (
    HardwareConstraintCreate,
    HardwareConstraintState,
    HardwareDeviceCreate,
    HardwareDeviceState,
    HardwareReturnState,
)
from .models import Verdict


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _loads(value: str | None, default: Any) -> Any:
    return default if value is None else json.loads(value)


class HardwareClosureStore:
    """Append-only persistence for the bounded hardware closure loop."""

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
        CREATE TABLE IF NOT EXISTS hardware_devices (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            name TEXT NOT NULL,
            kind TEXT NOT NULL,
            created_by TEXT NOT NULL,
            capabilities TEXT NOT NULL,
            control_channels TEXT NOT NULL,
            safety_envelope TEXT NOT NULL,
            minimum_approvals INTEGER NOT NULL,
            max_duration_seconds REAL NOT NULL,
            driver TEXT NOT NULL,
            state TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_hardware_devices_created
            ON hardware_devices(created_at,id);

        CREATE TABLE IF NOT EXISTS hardware_constraints (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL,
            translation_id TEXT,
            device_id TEXT NOT NULL REFERENCES hardware_devices(id),
            created_by TEXT NOT NULL,
            source_occurrence_ids TEXT NOT NULL,
            source_translation_ids TEXT NOT NULL,
            source_interaction_ids TEXT NOT NULL,
            participant_ids TEXT NOT NULL,
            agent_ids TEXT NOT NULL,
            affected_perspectives TEXT NOT NULL,
            selected_metavector TEXT NOT NULL,
            control_values TEXT NOT NULL,
            duration_seconds REAL NOT NULL,
            expected_return TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_hardware_constraints_device
            ON hardware_constraints(device_id,created_at,id);

        CREATE TABLE IF NOT EXISTS hardware_constraint_states (
            id TEXT PRIMARY KEY,
            constraint_id TEXT NOT NULL REFERENCES hardware_constraints(id),
            state TEXT NOT NULL,
            verdict TEXT NOT NULL,
            reason TEXT NOT NULL,
            actor_id TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_hardware_constraint_states
            ON hardware_constraint_states(constraint_id,created_at,id);

        CREATE TABLE IF NOT EXISTS hardware_constraint_decisions (
            id TEXT PRIMARY KEY,
            constraint_id TEXT NOT NULL REFERENCES hardware_constraints(id),
            verdict TEXT NOT NULL,
            reason TEXT NOT NULL,
            decided_by TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_hardware_constraint_decisions
            ON hardware_constraint_decisions(constraint_id,created_at,id);

        CREATE TABLE IF NOT EXISTS hardware_twin_runs (
            id TEXT PRIMARY KEY,
            constraint_id TEXT NOT NULL REFERENCES hardware_constraints(id),
            requested_by TEXT NOT NULL,
            driver TEXT NOT NULL,
            input_controls TEXT NOT NULL,
            output_reading TEXT NOT NULL,
            metrics TEXT NOT NULL,
            safe INTEGER NOT NULL,
            reason TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_hardware_twin_runs
            ON hardware_twin_runs(constraint_id,created_at,id);

        CREATE TABLE IF NOT EXISTS hardware_actuations (
            id TEXT PRIMARY KEY,
            constraint_id TEXT NOT NULL UNIQUE REFERENCES hardware_constraints(id),
            twin_run_id TEXT NOT NULL REFERENCES hardware_twin_runs(id),
            requested_by TEXT NOT NULL,
            mode TEXT NOT NULL,
            control_values TEXT NOT NULL,
            output_reading TEXT NOT NULL,
            status TEXT NOT NULL,
            return_id TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS hardware_returns (
            id TEXT PRIMARY KEY,
            actuation_id TEXT NOT NULL UNIQUE REFERENCES hardware_actuations(id),
            constraint_id TEXT NOT NULL REFERENCES hardware_constraints(id),
            device_id TEXT NOT NULL REFERENCES hardware_devices(id),
            occurrence_id TEXT NOT NULL,
            authored_by TEXT NOT NULL,
            sensor_reading TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            reintegration_status TEXT NOT NULL,
            translation_id TEXT,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_hardware_returns_status
            ON hardware_returns(reintegration_status,created_at,id);

        CREATE TABLE IF NOT EXISTS hardware_runtime_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
            self._conn.commit()

    def create_device(
        self, data: HardwareDeviceCreate, occurrence_id: str, *, driver: str
    ) -> dict[str, Any]:
        device_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                """INSERT INTO hardware_devices(
                    id,occurrence_id,name,kind,created_by,capabilities,
                    control_channels,safety_envelope,minimum_approvals,
                    max_duration_seconds,driver,state,metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    device_id,
                    occurrence_id,
                    data.name,
                    str(data.kind),
                    data.created_by,
                    _json(data.capabilities),
                    _json(data.control_channels),
                    _json(
                        {
                            key: bound.model_dump(mode="json")
                            for key, bound in data.safety_envelope.items()
                        }
                    ),
                    data.minimum_approvals,
                    data.max_duration_seconds,
                    driver,
                    str(HardwareDeviceState.READY),
                    _json(data.metadata),
                    utcnow(),
                ),
            )
            self._conn.commit()
        return self.get_device(device_id)

    def get_device(self, device_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM hardware_devices WHERE id=?", (device_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Hardware device {device_id} not found")
        return self._decode_device(row)

    def list_devices(self, limit: int = 10_000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM hardware_devices ORDER BY created_at,id LIMIT ?", (limit,)
        ).fetchall()
        return [self._decode_device(row) for row in rows]

    def create_constraint(
        self,
        data: HardwareConstraintCreate,
        occurrence_id: str,
        expires_at: str,
    ) -> dict[str, Any]:
        constraint_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                """INSERT INTO hardware_constraints(
                    id,occurrence_id,translation_id,device_id,created_by,
                    source_occurrence_ids,source_translation_ids,
                    source_interaction_ids,participant_ids,agent_ids,
                    affected_perspectives,selected_metavector,control_values,
                    duration_seconds,expected_return,expires_at,metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    constraint_id,
                    occurrence_id,
                    None,
                    data.device_id,
                    data.created_by,
                    _json(data.source_occurrence_ids),
                    _json(data.source_translation_ids),
                    _json(data.source_interaction_ids),
                    _json(data.participant_ids),
                    _json(data.agent_ids),
                    _json(data.affected_perspectives),
                    _json(data.selected_metavector),
                    _json(data.control_values),
                    data.duration_seconds,
                    _json(data.expected_return),
                    expires_at,
                    _json(data.metadata),
                    utcnow(),
                ),
            )
            self._conn.commit()
        self.append_constraint_state(
            constraint_id,
            HardwareConstraintState.PROPOSED,
            Verdict.OPEN,
            "Temporary device constraint proposed; simulation and scoped admission remain required",
            data.created_by,
            {"temporary": True},
        )
        return self.get_constraint(constraint_id)

    def link_constraint_translation(
        self, constraint_id: str, translation_id: str
    ) -> dict[str, Any]:
        self.get_constraint(constraint_id)
        with self._lock:
            self._conn.execute(
                "UPDATE hardware_constraints SET translation_id=? WHERE id=?",
                (translation_id, constraint_id),
            )
            self._conn.commit()
        return self.get_constraint(constraint_id)

    def append_constraint_state(
        self,
        constraint_id: str,
        state: HardwareConstraintState,
        verdict: Verdict,
        reason: str,
        actor_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._get_constraint_row(constraint_id)
        state_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                """INSERT INTO hardware_constraint_states(
                    id,constraint_id,state,verdict,reason,actor_id,metadata,created_at
                ) VALUES(?,?,?,?,?,?,?,?)""",
                (
                    state_id,
                    constraint_id,
                    str(state),
                    str(verdict),
                    reason,
                    actor_id,
                    _json(metadata or {}),
                    utcnow(),
                ),
            )
            self._conn.commit()
        return self.get_constraint_state(state_id)

    def get_constraint_state(self, state_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM hardware_constraint_states WHERE id=?", (state_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Hardware constraint state {state_id} not found")
        return self._decode_constraint_state(row)

    def list_constraint_states(self, constraint_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """SELECT * FROM hardware_constraint_states WHERE constraint_id=?
            ORDER BY created_at,id""",
            (constraint_id,),
        ).fetchall()
        return [self._decode_constraint_state(row) for row in rows]

    def create_constraint_decision(
        self,
        constraint_id: str,
        verdict: Verdict,
        reason: str,
        decided_by: str,
    ) -> dict[str, Any]:
        self._get_constraint_row(constraint_id)
        decision_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                """INSERT INTO hardware_constraint_decisions(
                    id,constraint_id,verdict,reason,decided_by,created_at
                ) VALUES(?,?,?,?,?,?)""",
                (
                    decision_id,
                    constraint_id,
                    str(verdict),
                    reason,
                    decided_by,
                    utcnow(),
                ),
            )
            self._conn.commit()
        return self.get_constraint_decision(decision_id)

    def get_constraint_decision(self, decision_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM hardware_constraint_decisions WHERE id=?", (decision_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Hardware decision {decision_id} not found")
        return dict(row)

    def list_constraint_decisions(self, constraint_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """SELECT * FROM hardware_constraint_decisions WHERE constraint_id=?
            ORDER BY created_at,id""",
            (constraint_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def current_constraint_state(self, constraint_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            """SELECT * FROM hardware_constraint_states WHERE constraint_id=?
            ORDER BY created_at DESC,id DESC LIMIT 1""",
            (constraint_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Hardware constraint {constraint_id} has no state")
        return self._decode_constraint_state(row)

    def get_constraint(self, constraint_id: str) -> dict[str, Any]:
        data = self._decode_constraint(self._get_constraint_row(constraint_id))
        history = self.list_constraint_states(constraint_id)
        current = history[-1]
        data["current_state"] = current["state"]
        data["current_verdict"] = current["verdict"]
        data["state_history"] = history
        data["decisions"] = self.list_constraint_decisions(constraint_id)
        return data

    def list_constraints(self, limit: int = 100_000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT id FROM hardware_constraints ORDER BY created_at,id LIMIT ?",
            (limit,),
        ).fetchall()
        return [self.get_constraint(str(row["id"])) for row in rows]

    def _get_constraint_row(self, constraint_id: str) -> sqlite3.Row:
        row = self._conn.execute(
            "SELECT * FROM hardware_constraints WHERE id=?", (constraint_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Hardware constraint {constraint_id} not found")
        return row

    def create_twin_run(
        self,
        constraint_id: str,
        requested_by: str,
        driver: str,
        input_controls: dict[str, float],
        output_reading: dict[str, Any],
        metrics: dict[str, float],
        safe: bool,
        reason: str,
    ) -> dict[str, Any]:
        self._get_constraint_row(constraint_id)
        run_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                """INSERT INTO hardware_twin_runs(
                    id,constraint_id,requested_by,driver,input_controls,
                    output_reading,metrics,safe,reason,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (
                    run_id,
                    constraint_id,
                    requested_by,
                    driver,
                    _json(input_controls),
                    _json(output_reading),
                    _json(metrics),
                    1 if safe else 0,
                    reason,
                    utcnow(),
                ),
            )
            self._conn.commit()
        return self.get_twin_run(run_id)

    def get_twin_run(self, run_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM hardware_twin_runs WHERE id=?", (run_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Hardware twin run {run_id} not found")
        return self._decode_twin_run(row)

    def latest_twin_run(self, constraint_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            """SELECT * FROM hardware_twin_runs WHERE constraint_id=?
            ORDER BY created_at DESC,id DESC LIMIT 1""",
            (constraint_id,),
        ).fetchone()
        return None if row is None else self._decode_twin_run(row)

    def list_twin_runs(self, limit: int = 100_000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM hardware_twin_runs ORDER BY created_at,id LIMIT ?",
            (limit,),
        ).fetchall()
        return [self._decode_twin_run(row) for row in rows]

    def create_actuation(
        self,
        constraint_id: str,
        twin_run_id: str,
        requested_by: str,
        control_values: dict[str, float],
        output_reading: dict[str, Any],
    ) -> dict[str, Any]:
        existing = self._conn.execute(
            "SELECT id FROM hardware_actuations WHERE constraint_id=?",
            (constraint_id,),
        ).fetchone()
        if existing is not None:
            return self.get_actuation(str(existing["id"]))
        actuation_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                """INSERT INTO hardware_actuations(
                    id,constraint_id,twin_run_id,requested_by,mode,
                    control_values,output_reading,status,return_id,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (
                    actuation_id,
                    constraint_id,
                    twin_run_id,
                    requested_by,
                    "SIMULATED_TWIN",
                    _json(control_values),
                    _json(output_reading),
                    "EXECUTED",
                    None,
                    utcnow(),
                ),
            )
            self._conn.commit()
        return self.get_actuation(actuation_id)

    def link_actuation_return(self, actuation_id: str, return_id: str) -> dict[str, Any]:
        with self._lock:
            self._conn.execute(
                "UPDATE hardware_actuations SET return_id=? WHERE id=?",
                (return_id, actuation_id),
            )
            self._conn.commit()
        return self.get_actuation(actuation_id)

    def get_actuation(self, actuation_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM hardware_actuations WHERE id=?", (actuation_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Hardware actuation {actuation_id} not found")
        return self._decode_actuation(row)

    def list_actuations(self, limit: int = 100_000) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM hardware_actuations ORDER BY created_at,id LIMIT ?",
            (limit,),
        ).fetchall()
        return [self._decode_actuation(row) for row in rows]

    def create_return(
        self,
        actuation_id: str,
        constraint_id: str,
        device_id: str,
        occurrence_id: str,
        authored_by: str,
        sensor_reading: dict[str, Any],
        evidence_status: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        existing = self._conn.execute(
            "SELECT id FROM hardware_returns WHERE actuation_id=?", (actuation_id,)
        ).fetchone()
        if existing is not None:
            return self.get_return(str(existing["id"]))
        return_id = str(uuid.uuid4())
        now = utcnow()
        with self._lock:
            self._conn.execute(
                """INSERT INTO hardware_returns(
                    id,actuation_id,constraint_id,device_id,occurrence_id,
                    authored_by,sensor_reading,evidence_status,
                    reintegration_status,translation_id,metadata,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    return_id,
                    actuation_id,
                    constraint_id,
                    device_id,
                    occurrence_id,
                    authored_by,
                    _json(sensor_reading),
                    evidence_status,
                    str(HardwareReturnState.PENDING),
                    None,
                    _json(metadata or {}),
                    now,
                    now,
                ),
            )
            self._conn.commit()
        self.link_actuation_return(actuation_id, return_id)
        return self.get_return(return_id)

    def update_return_reintegration(
        self,
        return_id: str,
        status: HardwareReturnState,
        translation_id: str | None,
    ) -> dict[str, Any]:
        self.get_return(return_id)
        with self._lock:
            self._conn.execute(
                """UPDATE hardware_returns
                SET reintegration_status=?,translation_id=?,updated_at=? WHERE id=?""",
                (str(status), translation_id, utcnow(), return_id),
            )
            self._conn.commit()
        return self.get_return(return_id)

    def get_return(self, return_id: str) -> dict[str, Any]:
        row = self._conn.execute(
            "SELECT * FROM hardware_returns WHERE id=?", (return_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Hardware return {return_id} not found")
        return self._decode_return(row)

    def list_returns(
        self, status: str | None = None, limit: int = 100_000
    ) -> list[dict[str, Any]]:
        if status is None:
            rows = self._conn.execute(
                "SELECT * FROM hardware_returns ORDER BY created_at,id LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                """SELECT * FROM hardware_returns WHERE reintegration_status=?
                ORDER BY created_at,id LIMIT ?""",
                (status, limit),
            ).fetchall()
        return [self._decode_return(row) for row in rows]

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._conn.execute(
                """INSERT INTO hardware_runtime_state(key,value,updated_at)
                VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET
                value=excluded.value,updated_at=excluded.updated_at""",
                (key, _json(value), utcnow()),
            )
            self._conn.commit()

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self._conn.execute(
            "SELECT value FROM hardware_runtime_state WHERE key=?", (key,)
        ).fetchone()
        return default if row is None else _loads(row["value"], default)

    def stats(self) -> dict[str, int]:
        def count(table: str) -> int:
            return int(
                self._conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
            )

        pending = int(
            self._conn.execute(
                "SELECT COUNT(*) AS n FROM hardware_returns WHERE reintegration_status=?",
                (str(HardwareReturnState.PENDING),),
            ).fetchone()["n"]
        )
        admitted = 0
        open_constraints = 0
        for constraint in self.list_constraints(limit=100_000):
            if constraint["current_state"] == str(HardwareConstraintState.ADMITTED):
                admitted += 1
            if constraint["current_verdict"] == str(Verdict.OPEN):
                open_constraints += 1
        return {
            "devices": count("hardware_devices"),
            "constraints": count("hardware_constraints"),
            "twin_runs": count("hardware_twin_runs"),
            "actuations": count("hardware_actuations"),
            "returns": count("hardware_returns"),
            "pending_returns": pending,
            "admitted_constraints": admitted,
            "open_constraints": open_constraints,
        }

    @staticmethod
    def _decode_device(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in (
            ("capabilities", []),
            ("control_channels", []),
            ("safety_envelope", {}),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    @staticmethod
    def _decode_constraint(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        for key, default in (
            ("source_occurrence_ids", []),
            ("source_translation_ids", []),
            ("source_interaction_ids", []),
            ("participant_ids", []),
            ("agent_ids", []),
            ("affected_perspectives", []),
            ("selected_metavector", []),
            ("control_values", {}),
            ("expected_return", {}),
            ("metadata", {}),
        ):
            data[key] = _loads(data[key], default)
        return data

    @staticmethod
    def _decode_constraint_state(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["metadata"] = _loads(data["metadata"], {})
        return data

    @staticmethod
    def _decode_twin_run(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["input_controls"] = _loads(data["input_controls"], {})
        data["output_reading"] = _loads(data["output_reading"], {})
        data["metrics"] = _loads(data["metrics"], {})
        data["safe"] = bool(data["safe"])
        return data

    @staticmethod
    def _decode_actuation(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["control_values"] = _loads(data["control_values"], {})
        data["output_reading"] = _loads(data["output_reading"], {})
        return data

    @staticmethod
    def _decode_return(row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["sensor_reading"] = _loads(data["sensor_reading"], {})
        data["metadata"] = _loads(data["metadata"], {})
        return data
