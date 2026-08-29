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

        CREATE TABLE IF NOT EXISTS supernet_integrator_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        with self._lock:
            self._conn.executescript(schema)
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

    def events_after(self, seq: int, limit: int = 500) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """SELECT id FROM supernet_integration_events WHERE seq>?
            ORDER BY seq LIMIT ?""",
            (seq, limit),
        ).fetchall()
        return [self.get_event(str(row["id"])) for row in rows]

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
        current: dict[str, int] = {}
        verdicts: dict[str, int] = {}
        for event in self.list_events(limit=200_000):
            current[event["current_stage"]] = current.get(event["current_stage"], 0) + 1
            verdicts[event["current_verdict"]] = verdicts.get(event["current_verdict"], 0) + 1
        return {
            "events": events,
            "states": states,
            "stages": stages,
            "visual_closure_receipts": visual_closure_receipts,
            **{f"stage_{key.lower()}": value for key, value in current.items()},
            **{f"verdict_{key.lower()}": value for key, value in verdicts.items()},
        }

    def _event_row(self, event_id: str) -> sqlite3.Row:
        row = self._conn.execute(
            "SELECT * FROM supernet_integration_events WHERE id=?", (event_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"Supernet integration event {event_id} not found")
        return row

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
